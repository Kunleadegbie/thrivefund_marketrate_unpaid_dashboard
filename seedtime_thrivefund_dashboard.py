import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

# Set page configuration
st.set_page_config(page_title="ThriveFund Portfolio Dashboard", layout="wide")

st.title("💼 ThriveFund Client Portfolio Dashboard")

# Initialize session state for clients
if 'clients' not in st.session_state:
    st.session_state.clients = {}

# Sidebar for adding a new client
st.sidebar.header("Add New Client")
with st.sidebar.form("client_form"):
    client_name = st.text_input("Client Name")
    principal = st.number_input("Principal Amount (₦)", min_value=0.0, format="%.2f")
    tenor = st.number_input("Tenor (Days)", min_value=1, format="%d")
    rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, format="%.2f")

    st.markdown("### Additional Deposits")
    deposit_count = st.number_input("Number of Additional Deposits", min_value=0, step=1)
    deposits = []
    for i in range(int(deposit_count)):
        amount = st.number_input(f"Deposit {i+1} Amount (₦)", min_value=0.0, format="%.2f", key=f"dep_amt_{i}")
        day = st.number_input(f"Deposit {i+1} Day", min_value=0, max_value=tenor, format="%d", key=f"dep_day_{i}")
        deposits.append((day, amount))

    st.markdown("### Withdrawals")
    withdrawal_count = st.number_input("Number of Withdrawals", min_value=0, step=1)
    withdrawals = []
    for i in range(int(withdrawal_count)):
        amount = st.number_input(f"Withdrawal {i+1} Amount (₦)", min_value=0.0, format="%.2f", key=f"with_amt_{i}")
        day = st.number_input(f"Withdrawal {i+1} Day", min_value=0, max_value=tenor, format="%d", key=f"with_day_{i}")
        withdrawals.append((day, -amount))

    submitted = st.form_submit_button("Add Client")
    if submitted:
        if client_name in st.session_state.clients:
            st.warning("Client already exists.")
        else:
            st.session_state.clients[client_name] = {
                "principal": principal,
                "tenor": tenor,
                "rate": rate,
                "deposits": deposits,
                "withdrawals": withdrawals
            }
            st.success(f"Client '{client_name}' added successfully!")

# Function to calculate compound interest-based ROI
def calculate_roi(principal, tenor, rate, deposits, withdrawals):
    transactions = [(0, principal)] + deposits + withdrawals
    transactions.sort()

    balance = 0
    roi = 0
    last_day = 0
    daily_rate = (rate / 100) / 365
    details = []

    for day, amount in transactions:
        days_invested = day - last_day
        if days_invested > 0:
            interest = balance * ((1 + daily_rate) ** days_invested - 1)
            roi += interest
            balance += interest
        balance += amount
        last_day = day
        details.append({
            "Day": day,
            "Transaction": amount,
            "Balance": balance,
            "Interest Accrued": interest if days_invested > 0 else 0
        })

    # Final interest from last transaction day to tenor
    days_invested = tenor - last_day
    if days_invested > 0:
        final_interest = balance * ((1 + daily_rate) ** days_invested - 1)
        roi += final_interest
        balance += final_interest
    else:
        final_interest = 0

    details.append({
        "Day": tenor,
        "Transaction": 0,
        "Balance": balance,
        "Interest Accrued": final_interest
    })

    return roi, balance, details

# Function to export client data to Excel
def export_clients_to_excel(clients_data):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for client_name, data in clients_data.items():
            roi, final_balance, details = calculate_roi(
                data["principal"],
                data["tenor"],
                data["rate"],
                data["deposits"],
                data["withdrawals"]
            )
            df = pd.DataFrame(details)
            df.to_excel(writer, sheet_name=client_name[:31], index=False)
    output.seek(0)
    return output

# Display client portfolios
st.header("📊 Client Portfolios")
if st.session_state.clients:
    for client_name, data in st.session_state.clients.items():
        with st.expander(f"Client: {client_name}", expanded=False):
            roi, final_balance, details = calculate_roi(
                data["principal"],
                data["tenor"],
                data["rate"],
                data["deposits"],
                data["withdrawals"]
            )

            st.subheader("Summary")
            st.write(f"**Total ROI (Compound Interest):** ₦{roi:,.2f}")
            st.write(f"**Final Balance (including ROI):** ₦{final_balance:,.2f}")

            df = pd.DataFrame(details)
            st.subheader("Transaction Details")
            st.dataframe(df.style.format({"Transaction": "₦{:.2f}", "Balance": "₦{:.2f}", "Interest Accrued": "₦{:.2f}"}))

            # Plot investment growth
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["Day"], y=df["Balance"], mode='lines+markers', name='Balance'))
            fig.update_layout(title='Investment Growth Over Time',
                              xaxis_title='Day',
                              yaxis_title='Balance (₦)',
                              template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)

    # Download button for Excel file
    st.subheader("📥 Download All Client Data")
    excel_data = export_clients_to_excel(st.session_state.clients)
    st.download_button(label='Download Excel File',
                       data=excel_data,
                       file_name='clients_data.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
else:
    st.info("No clients added yet. Use the sidebar to add a new client.")
