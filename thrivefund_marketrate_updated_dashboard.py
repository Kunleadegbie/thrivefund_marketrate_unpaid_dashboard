import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import timedelta

st.set_page_config(page_title="ThriveFund Investment Dashboard", layout="wide")

# App title
st.title("📊 ThriveFund Investment & ROI Manager")
st.subheader("SeedTime Capital Management Limited")
st.markdown("---")

# Initialize session state to hold client data
if 'clients' not in st.session_state:
    st.session_state.clients = {}

# Function to calculate ROI and profit with tenors and compound interest
def compute_roi(transactions, benchmark_changes):
    transactions = transactions.sort_values('Date').reset_index(drop=True)
    transactions['Balance'] = transactions['Amount'].cumsum()

    benchmark_df = pd.DataFrame(benchmark_changes, columns=['Date', 'Benchmark Rate'])
    benchmark_df['Date'] = pd.to_datetime(benchmark_df['Date'], format='%d-%m-%Y')
    benchmark_df = benchmark_df.sort_values('Date')
    transactions['Benchmark Rate'] = np.nan

    for i, row in benchmark_df.iterrows():
        transactions.loc[transactions['Date'] >= row['Date'], 'Benchmark Rate'] = row['Benchmark Rate']
    transactions['Benchmark Rate'] = transactions['Benchmark Rate'].ffill()

    def get_spread(balance):
        if balance < 50000:
            return 9
        elif balance < 500000:
            return 7.5
        else:
            return 6

    transactions['Spread'] = transactions['Balance'].apply(get_spread)
    transactions['Customer Rate'] = transactions['Benchmark Rate'] - transactions['Spread']

    balance = 0
    total_profit = 0
    transactions['Interest'] = 0.0
    transactions['Profit'] = 0.0

    maturity_date = transactions['Maturity Date'].iloc[0]  # maturity date from first transaction

    for i in range(len(transactions)):
        if i == 0:
            balance = transactions.loc[i, 'Amount']
        else:
            days = (transactions.loc[i, 'Date'] - transactions.loc[i-1, 'Date']).days
            if days > 0:
                cust_rate = transactions.loc[i-1, 'Customer Rate'] / 100
                bench_rate = transactions.loc[i-1, 'Benchmark Rate'] / 100
                spread_rate = bench_rate - cust_rate

                # Customer Interest — on balance at customer rate
                interest_earned = balance * ((1 + cust_rate / 365) ** days - 1)

                # Profit — on balance at spread rate
                profit_earned = balance * ((1 + spread_rate / 365) ** days - 1)

                balance += interest_earned
                total_profit += profit_earned

            balance += transactions.loc[i, 'Amount']

        transactions.loc[i, 'Interest'] = balance - transactions['Amount'][:i+1].sum()
        transactions.loc[i, 'Profit'] = total_profit

    transactions['Final Balance'] = transactions['Amount'].cumsum() + transactions['Interest']

    return transactions, total_profit

# Add new client section
st.sidebar.subheader("➕ Add New Client")
client_name = st.sidebar.text_input("Client Name")
if st.sidebar.button("Create Client Profile"):
    if client_name not in st.session_state.clients:
        st.session_state.clients[client_name] = {
            'transactions': [],
            'benchmark_changes': [['01-01-2024', 21]]
        }
        st.sidebar.success(f"{client_name}'s profile created.")
    else:
        st.sidebar.warning("Client already exists.")

# Select client
client_list = list(st.session_state.clients.keys())
if client_list:
    selected_client = st.selectbox("Select a Client to Manage", client_list)

    # Add Transaction
    st.subheader(f"Add Transaction for {selected_client}")
    trans_date = st.date_input("Transaction Date")
    trans_type = st.radio("Type", ["Deposit", "Withdrawal"])
    amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0)

    if st.session_state.clients[selected_client]['transactions']:
        maturity_date = pd.to_datetime(
            st.session_state.clients[selected_client]['transactions'][0]['Maturity Date'],
            format='%d-%m-%Y'
        )
    else:
        tenor = st.number_input("Tenor (Days)", min_value=0, step=1)
        maturity_date = pd.Timestamp(trans_date) + timedelta(days=int(tenor))  # Converted here

    if st.button("Add Transaction"):
        amount_signed = amount if trans_type == "Deposit" else -amount

        tenor_days = (maturity_date - pd.Timestamp(trans_date)).days  # Fixed type mismatch

        st.session_state.clients[selected_client]['transactions'].append(
            {
                'Date': trans_date.strftime('%d-%m-%Y'),
                'Type': trans_type,
                'Amount': amount_signed,
                'Tenor': tenor_days,
                'Maturity Date': maturity_date.strftime('%d-%m-%Y')
            }
        )
        st.success("Transaction recorded.")

    # Update Benchmark Rate
    st.subheader("Adjust Benchmark Interest Rate")
    rate_date = st.date_input("Effective Date for New Rate")
    new_rate = st.number_input("New Benchmark Rate (% p.a.)", value=21.0, step=0.5)
    if st.button("Add Rate Change"):
        st.session_state.clients[selected_client]['benchmark_changes'].append(
            [rate_date.strftime('%d-%m-%Y'), new_rate]
        )
        st.success("Rate change added.")

    # Transaction Log
    st.subheader("📑 Transaction Log")
    if st.session_state.clients[selected_client]['transactions']:
        transactions_df = pd.DataFrame(st.session_state.clients[selected_client]['transactions'])
        transactions_df = transactions_df.sort_values('Date')
        transactions_df['Balance'] = transactions_df['Amount'].cumsum()
        st.dataframe(transactions_df)

    # Benchmark History
    st.subheader("📊 Benchmark Rate History")
    benchmark_df = pd.DataFrame(
        st.session_state.clients[selected_client]['benchmark_changes'],
        columns=['Date', 'Benchmark Rate']
    ).sort_values('Date')
    st.dataframe(benchmark_df)

    # Compute ROI
    if st.button("📈 Compute ROI"):
        transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], format='%d-%m-%Y')
        transactions_df['Maturity Date'] = pd.to_datetime(transactions_df['Maturity Date'], format='%d-%m-%Y')
        benchmark_df['Date'] = pd.to_datetime(benchmark_df['Date'], format='%d-%m-%Y')

        result_df, total_profit = compute_roi(
            transactions_df,
            st.session_state.clients[selected_client]['benchmark_changes']
        )

        st.subheader("📊 ROI Projection (Daily Compound Interest)")
        st.dataframe(result_df)

        st.subheader(f"📊 Total Profit: ₦{total_profit:,.2f}")

        # Download as CSV
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, f"{selected_client}_transactions.csv", "text/csv")

        # Download as Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False, sheet_name=selected_client)

        st.download_button("📥 Download Excel", data=excel_buffer.getvalue(),
                           file_name=f"{selected_client}_transactions.xlsx")

else:
    st.info("👉 Add a client profile from the sidebar to begin.")
