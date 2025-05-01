import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="ThriveFund Dashboard", layout="centered")

# Initialize session state to store client records
if 'clients' not in st.session_state:
    st.session_state.clients = []

st.title("🌱 ThriveFund Investment Dashboard")

st.sidebar.header("📋 Navigation")
page = st.sidebar.radio("Go to", ["Add Client Record", "View & Export Records"])

# Helper: Convert client records to Excel
def export_clients_to_excel(clients):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    for idx, client in enumerate(clients):
        df = pd.DataFrame(client["transactions"])
        df.to_excel(writer, sheet_name=f"{client['name']}", index=False)

    writer.close()
    output.seek(0)
    return output

# Add Client Record Page
if page == "Add Client Record":
    st.header("➕ Add New Client Investment Record")

    name = st.text_input("Client Full Name")
    principal = st.number_input("Initial Investment Amount (₦)", min_value=0.0, format="%.2f")
    principal_date = st.date_input("Date of Initial Investment", format="DD-MM-YYYY")
    tenor = st.number_input("Tenor (Days)", min_value=1, format="%d")
    rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, format="%.2f")

    st.subheader("➕ Additional Deposits (Optional)")
    deposit_count = st.number_input("Number of Additional Deposits", min_value=0, step=1)
    deposits = []
    for i in range(int(deposit_count)):
        st.markdown(f"**Deposit {i+1}**")
        amount = st.number_input(f"Amount (₦) for Deposit {i+1}", min_value=0.0, format="%.2f", key=f"dep_amt_{i}")
        date = st.date_input(f"Date of Deposit {i+1}", format="DD-MM-YYYY", key=f"dep_date_{i}")
        deposits.append((date.strftime("%d-%m-%Y"), amount))

    st.subheader("➖ Withdrawals (Optional)")
    withdrawal_count = st.number_input("Number of Withdrawals", min_value=0, step=1)
    withdrawals = []
    for i in range(int(withdrawal_count)):
        st.markdown(f"**Withdrawal {i+1}**")
        amount = st.number_input(f"Amount (₦) for Withdrawal {i+1}", min_value=0.0, format="%.2f", key=f"with_amt_{i}")
        date = st.date_input(f"Date of Withdrawal {i+1}", format="DD-MM-YYYY", key=f"with_date_{i}")
        withdrawals.append((date.strftime("%d-%m-%Y"), -amount))

    if st.button("➕ Save Client Record"):
        if name == "" or principal <= 0 or tenor <= 0 or rate <= 0:
            st.error("Please complete all required fields.")
        else:
            transactions = []
            transactions.append({
                "Date": principal_date.strftime("%d-%m-%Y"),
                "Transaction Type": "Initial Deposit",
                "Amount (₦)": principal
            })
            for dep in deposits:
                transactions.append({
                    "Date": dep[0],
                    "Transaction Type": "Additional Deposit",
                    "Amount (₦)": dep[1]
                })
            for withdr in withdrawals:
                transactions.append({
                    "Date": withdr[0],
                    "Transaction Type": "Withdrawal",
                    "Amount (₦)": withdr[1]
                })

            transactions_df = pd.DataFrame(transactions)
            transactions_df["Date"] = pd.to_datetime(transactions_df["Date"], format="%d-%m-%Y")
            transactions_df.sort_values("Date", inplace=True)
            transactions_df["Date"] = transactions_df["Date"].dt.strftime("%d-%m-%Y")

            # ROI calculation with compound interest
            roi = 0
            balance = 0
            last_date = datetime.strptime(principal_date.strftime("%d-%m-%Y"), "%d-%m-%Y")

            details = []
            for _, row in transactions_df.iterrows():
                current_date = datetime.strptime(row["Date"], "%d-%m-%Y")
                days_invested = (current_date - last_date).days
                interest = (balance * (rate / 100) * days_invested) / 365
                roi += interest
                balance += row["Amount (₦)"]
                details.append({
                    "Date": row["Date"],
                    "Transaction Type": row["Transaction Type"],
                    "Transaction (₦)": row["Amount (₦)"],
                    "Balance After (₦)": balance,
                    "Interest Accrued (₦)": interest
                })
                last_date = current_date

            # Final interest from last transaction to maturity
            final_days = tenor - (last_date - datetime.strptime(principal_date.strftime("%d-%m-%Y"), "%d-%m-%Y")).days
            final_interest = (balance * (rate / 100) * final_days) / 365
            roi += final_interest
            details.append({
                "Date": f"Maturity ({(last_date + pd.Timedelta(days=final_days)).strftime('%d-%m-%Y')})",
                "Transaction Type": "Maturity",
                "Transaction (₦)": 0,
                "Balance After (₦)": balance,
                "Interest Accrued (₦)": final_interest
            })

            st.session_state.clients.append({
                "name": name,
                "principal": principal,
                "tenor": tenor,
                "rate": rate,
                "transactions": details,
                "total_roi": roi,
                "final_balance": balance
            })

            st.success(f"✅ Investment record for {name} saved successfully!")

# View & Export Records Page
if page == "View & Export Records":
    st.header("📊 All Client Investment Records")

    if st.session_state.clients:
        for client in st.session_state.clients:
            st.subheader(f"📌 {client['name']}")
            st.write(f"**Total ROI:** ₦{client['total_roi']:,.2f}")
            st.write(f"**Final Balance (Before Interest):** ₦{client['final_balance']:,.2f}")

            df = pd.DataFrame(client["transactions"])
            st.dataframe(df.style.format({"Transaction (₦)": "₦{:.2f}", "Balance After (₦)": "₦{:.2f}", "Interest Accrued (₦)": "₦{:.2f}"}))

        excel_data = export_clients_to_excel(st.session_state.clients)
        st.download_button(
            label="📥 Download All Records as Excel",
            data=excel_data,
            file_name="ThriveFund_Client_Records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No records available yet.")
