# seedtimecapital_thrivefund_dashboard.py

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ThriveFund Dashboard", layout="wide")

# Initialize session state
if 'clients' not in st.session_state:
    st.session_state.clients = []

# Function to calculate compound interest ROI
def calculate_roi(principal, tenor, rate, deposits, withdrawals):
    transactions = [(0, principal)] + deposits + withdrawals
    transactions.sort()

    balance = 0
    roi = 0
    last_day = 0
    details = []

    for day, amount in transactions:
        days_invested = day - last_day
        if days_invested > 0:
            interest = balance * ((1 + (rate / 100 / 365))**days_invested - 1)
            roi += interest
            balance += interest
        balance += amount
        last_day = day
        details.append({
            "Day": day,
            "Transaction": amount,
            "Balance": balance,
            "Interest Accrued": roi
        })

    # Final interest from last transaction to tenor
    days_invested = tenor - last_day
    if days_invested > 0:
        final_interest = balance * ((1 + (rate / 100 / 365))**days_invested - 1)
        roi += final_interest
        balance += final_interest
        details.append({
            "Day": tenor,
            "Transaction": 0,
            "Balance": balance,
            "Interest Accrued": roi
        })

    return roi, balance, pd.DataFrame(details)

# Function to export client data to Excel
def export_clients_to_excel(clients):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for client in clients:
        df = pd.DataFrame(client["Details"])
        df.to_excel(writer, sheet_name=client["Name"][:30], index=False)
    writer.close()
    output.seek(0)
    return output

# Sidebar navigation
st.sidebar.title("ThriveFund Dashboard")
menu = st.sidebar.radio("Go to:", ("Add New Client", "Client Summary"))

# Add New Client Page
if menu == "Add New Client":
    st.title("💼 Add New Client ROI Record")

    name = st.text_input("Client Name")
    principal = st.number_input("Principal Amount (₦)", min_value=0.0, format="%.2f")
    tenor = st.number_input("Tenor (Days)", min_value=1, format="%d")
    rate = st.number_input("Interest Rate (% p.a)", min_value=0.0, format="%.2f")

    st.subheader("➕ Additional Deposits (Optional)")
    deposit_count = st.number_input("Number of Additional Deposits", min_value=0, step=1)
    deposits = []
    for i in range(int(deposit_count)):
        st.markdown(f"**Deposit {i+1}**")
        amount = st.number_input(f"Amount (₦) for Deposit {i+1}", min_value=0.0, format="%.2f", key=f"dep_amt_{i}")
        day = st.number_input(f"Day of Deposit {i+1}", min_value=0, max_value=tenor, format="%d", key=f"dep_day_{i}")
        deposits.append((day, amount))

    st.subheader("➖ Withdrawals (Optional)")
    withdrawal_count = st.number_input("Number of Withdrawals", min_value=0, step=1)
    withdrawals = []
    for i in range(int(withdrawal_count)):
        st.markdown(f"**Withdrawal {i+1}**")
        amount = st.number_input(f"Amount (₦) for Withdrawal {i+1}", min_value=0.0, format="%.2f", key=f"with_amt_{i}")
        day = st.number_input(f"Day of Withdrawal {i+1}", min_value=0, max_value=tenor, format="%d", key=f"with_day_{i}")
        withdrawals.append((day, -amount))

    if st.button("Save Client Record"):
        if name and principal > 0 and tenor > 0 and rate > 0:
            roi, final_balance, details_df = calculate_roi(principal, tenor, rate, deposits, withdrawals)
            client_record = {
                "Name": name,
                "Principal": principal,
                "Tenor": tenor,
                "Rate": rate,
                "ROI": roi,
                "Final Balance": final_balance,
                "Details": details_df.to_dict(orient="records")
            }
            st.session_state.clients.append(client_record)
            st.success(f"Client {name}'s ROI record saved successfully!")
        else:
            st.error("Please fill in all required fields.")

# Client Summary Page
if menu == "Client Summary":
    st.title("📊 Client Portfolio Summary")

    if st.session_state.clients:
        clients_df = pd.DataFrame([{
            "Name": c["Name"],
            "Principal (₦)": c["Principal"],
            "Tenor (Days)": c["Tenor"],
            "Rate (%)": c["Rate"],
            "ROI (₦)": round(c["ROI"], 2),
            "Final Balance (₦)": round(c["Final Balance"], 2)
        } for c in st.session_state.clients])

        st.dataframe(clients_df.style.format({"Principal (₦)": "₦{:.2f}", "ROI (₦)": "₦{:.2f}", "Final Balance (₦)": "₦{:.2f}"}))

        excel_data = export_clients_to_excel(st.session_state.clients)
        st.download_button(
            label="📥 Download All Clients Portfolio as Excel",
            data=excel_data,
            file_name="thrivefund_clients.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No client records available yet. Please add records first.")

