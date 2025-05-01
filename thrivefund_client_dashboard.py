
import streamlit as st
import pandas as pd
import datetime
import io

# Page config
st.set_page_config(page_title="ThriveFund Investor Dashboard", layout="centered")

# Banner and logo
st.title("🌱 ThriveFund Investors Management")
st.markdown("Manage investor records, compute ROI, track maturity dates, and export data.")

# Initialize session state
if 'clients' not in st.session_state:
    st.session_state.clients = []

# Function to compute ROI with compound interest
def compute_compound_interest(principal, rate, tenor):
    years = tenor / 365
    amount = principal * ((1 + (rate / (100 * 1))) ** (1 * years))
    roi = amount - principal
    return round(roi, 2)

# Function to export to Excel with exact headers
def export_clients_to_excel(clients):
    output = io.BytesIO()
    df = pd.DataFrame(clients)
    df.columns = [
        "S/N", "Account Number", "Depositor Name", "Amount Invested (₦)",
        "Tenor", "Interest rate", "Effective Date", "Maturity Date",
        "ROI on maturity", "Phone Number", "Email Address", "Contact Address"
    ]
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Sheet1')
        writer.sheets['Sheet1'] = worksheet
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value)
        for row_num, row_data in enumerate(df.values, start=2):
            for col_num, cell_value in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_value)
    output.seek(0)
    return output

# Input form
with st.form("new_client_form"):
    st.subheader("➕ Add New Investor")
    account_number = st.text_input("Account Number")
    depositor_name = st.text_input("Depositor Name")
    amount_invested = st.number_input("Amount Invested (₦)", min_value=0.0, format="%.2f")
    tenor = st.number_input("Tenor (days)", min_value=1, step=1)
    interest_rate = st.number_input("Interest rate (% per annum)", min_value=0.0, format="%.2f")
    effective_date = st.date_input("Effective Date (DD-MM-YYYY)", format="DD-MM-YYYY")
    phone_number = st.text_input("Phone Number")
    email_address = st.text_input("Email Address")
    contact_address = st.text_area("Contact Address")
    submitted = st.form_submit_button("Add Investor")
    if submitted:
        if not (account_number and depositor_name and amount_invested and tenor and interest_rate and effective_date):
            st.error("Please fill in all required fields.")
        else:
            sn = len(st.session_state.clients) + 1
            maturity_date = effective_date + datetime.timedelta(days=tenor)
            roi = compute_compound_interest(amount_invested, interest_rate, tenor)
            client_data = [
                sn, account_number, depositor_name, amount_invested, tenor,
                interest_rate, effective_date.strftime("%d-%m-%Y"),
                maturity_date.strftime("%d-%m-%Y"), roi, phone_number,
                email_address, contact_address
            ]
            st.session_state.clients.append(client_data)
            st.success(f"Investor {depositor_name} added successfully!")

# View records
st.subheader("📊 Current Investors Portfolio")
if st.session_state.clients:
    df_clients = pd.DataFrame(st.session_state.clients, columns=[
        "S/N", "Account Number", "Depositor Name", "Amount Invested (₦)",
        "Tenor", "Interest rate", "Effective Date", "Maturity Date",
        "ROI on maturity", "Phone Number", "Email Address", "Contact Address"
    ])
    st.dataframe(df_clients)
    excel_data = export_clients_to_excel(st.session_state.clients)
    st.download_button(
        label="📥 Download Excel File",
        data=excel_data,
        file_name="ThriveFund_Investors.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No investors added yet.")
