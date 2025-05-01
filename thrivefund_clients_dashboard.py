import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Set up Streamlit page config
st.set_page_config(page_title="ThriveFund Investor Dashboard", layout="centered")

# Load logo/banner image
st.title("💼 ThriveFund Investor Dashboard")

# Initialize session state for clients if it doesn't exist
if 'clients' not in st.session_state:
    st.session_state.clients = []

# Function to export client data to Excel
def export_clients_to_excel(clients):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(clients)
        df.to_excel(writer, index=False, sheet_name='Clients')
    processed_data = output.getvalue()
    return processed_data

# Investment form
st.header("📥 Add New Client Investment Record")

with st.form("investment_form"):
    client_name = st.text_input("Client Name")
    contact = st.text_input("Contact Number / Email")
    principal = st.number_input("Initial Deposit Amount (₦)", min_value=0.0, format="%.2f")
    principal_date = st.date_input("Initial Deposit Date (DD-MM-YYYY)").strftime("%d-%m-%Y")
    tenor = st.number_input("Investment Tenor (Days)", min_value=1, format="%d")
    rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, format="%.2f")

    st.markdown("### ➕ Additional Deposits (Optional)")
    add_deposit_count = st.number_input("Number of Additional Deposits", min_value=0, step=1)
    add_deposits = []
    for i in range(int(add_deposit_count)):
        amount = st.number_input(f"Amount (₦) for Deposit {i+1}", min_value=0.0, format="%.2f", key=f"dep_amt_{i}")
        date = st.date_input(f"Date for Deposit {i+1} (DD-MM-YYYY)", key=f"dep_date_{i}").strftime("%d-%m-%Y")
        add_deposits.append({"Amount": amount, "Date": date})

    st.markdown("### ➖ Withdrawals (Optional)")
    withdrawal_count = st.number_input("Number of Withdrawals", min_value=0, step=1)
    withdrawals = []
    for i in range(int(withdrawal_count)):
        amount = st.number_input(f"Amount (₦) for Withdrawal {i+1}", min_value=0.0, format="%.2f", key=f"with_amt_{i}")
        date = st.date_input(f"Date for Withdrawal {i+1} (DD-MM-YYYY)", key=f"with_date_{i}").strftime("%d-%m-%Y")
        withdrawals.append({"Amount": amount, "Date": date})

    submitted = st.form_submit_button("Add Client Record")

if submitted:
    new_client = {
        "Client Name": client_name,
        "Contact": contact,
        "Initial Deposit (₦)": principal,
        "Initial Deposit Date": principal_date,
        "Tenor (Days)": tenor,
        "Rate (% p.a.)": rate,
        "Additional Deposits": add_deposits,
        "Withdrawals": withdrawals
    }
    st.session_state.clients.append(new_client)
    st.success("Client investment record added successfully!")

# View existing clients
st.header("📊 View Client Investment Records")

if st.session_state.clients:
    for idx, client in enumerate(st.session_state.clients):
        with st.expander(f"📁 {client['Client Name']}"):
            st.write(f"**Contact:** {client['Contact']}")
            st.write(f"**Initial Deposit:** ₦{client['Initial Deposit (₦)']:,.2f} on {client['Initial Deposit Date']}")
            st.write(f"**Tenor:** {client['Tenor (Days)']} days")
            st.write(f"**Rate:** {client['Rate (% p.a.)']}% per annum")

            if client["Additional Deposits"]:
                st.write("**Additional Deposits:**")
                for dep in client["Additional Deposits"]:
                    st.write(f" - ₦{dep['Amount']:,.2f} on {dep['Date']}")
            else:
                st.write("**Additional Deposits:** None")

            if client["Withdrawals"]:
                st.write("**Withdrawals:**")
                for wd in client["Withdrawals"]:
                    st.write(f" - ₦{wd['Amount']:,.2f} on {wd['Date']}")
            else:
                st.write("**Withdrawals:** None")

else:
    st.info("No client records added yet.")

# Download button for Excel export
if st.session_state.clients:
    excel_data = export_clients_to_excel(st.session_state.clients)
    st.download_button(
        label="📥 Download Client Records (Excel)",
        data=excel_data,
        file_name="ThriveFund_Client_Records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
