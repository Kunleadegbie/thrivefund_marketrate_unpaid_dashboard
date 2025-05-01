# Profit Spread Manager for SEEDTIME CAPITAL MGT LIMITED (ThriveFund)

import streamlit as st
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="Seedtime ThriveFund Profit Manager", page_icon="💰", layout="wide")

# Custom colors
primary_color = "#86cfd3"
accent_color = "#fbb37f"

# Custom CSS for branding
st.markdown(f"""
    <style>
    .reportview-container .main {{
        background-color: #f8f9fa;
        color: #333;
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: {accent_color};
        color: #333;
    }}
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown(f"<h2 style='color:{primary_color};'>💼 SEEDTIME CAPITAL MGT LIMITED | ThriveFund Profit Manager</h2>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color:{accent_color};'>Smart, Dynamic, Profitable 💸</h5>", unsafe_allow_html=True)

# Session State for Benchmark Rate and Deposits
if 'benchmark_rate' not in st.session_state:
    st.session_state.benchmark_rate = 21.0

if 'deposits' not in st.session_state:
    st.session_state.deposits = pd.DataFrame(columns=["Client Name", "Deposit Amount (NGN)", "Spread (%)", "Depositor Rate (%)", "Date"])

if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Client Name", "Transaction Type", "Amount", "Date"])

# Tier Definitions
tiers = [
    (5000, 49999, 9.0),
    (50000, 499999, 7.5),
    (500000, float('inf'), 6.0)
]

# Function to determine spread
def get_spread(amount):
    for lower, upper, spread in tiers:
        if lower <= amount <= upper:
            return spread
    return None

# Add New Deposit
with st.form("deposit_form"):
    st.subheader("➕ Add New Deposit")
    col1, col2, col3 = st.columns(3)
    client_name = col1.text_input("Client Name")
    deposit_amount = col2.number_input("Deposit Amount (NGN)", min_value=0.0, step=1000.0)
    deposit_date = col3.date_input("Deposit Date")
    submitted = st.form_submit_button("Add Deposit")

    if submitted:
        if deposit_amount < 5000:
            st.error("Minimum deposit is NGN 5,000.")
        elif not client_name:
            st.error("Client name is required.")
        else:
            spread = get_spread(deposit_amount)
            depositor_rate = st.session_state.benchmark_rate - spread
            new_entry = pd.DataFrame([[client_name, deposit_amount, spread, depositor_rate, deposit_date.strftime('%d-%m-%Y')]],
                                     columns=st.session_state.deposits.columns)
            st.session_state.deposits = pd.concat([st.session_state.deposits, new_entry], ignore_index=True)
            st.success(f"Deposit for {client_name} added.")

# Add Deposit/Withdrawal Transaction
with st.form("transaction_form"):
    st.subheader("➕ Record Additional Deposit / Withdrawal")
    col1, col2, col3, col4 = st.columns(4)
    client_name_tx = col1.text_input("Client Name (as recorded)")
    tx_type = col2.selectbox("Transaction Type", ["Additional Deposit", "Withdrawal"])
    amount_tx = col3.number_input("Amount (NGN)", min_value=0.0, step=1000.0)
    date_tx = col4.date_input("Transaction Date")
    tx_submit = st.form_submit_button("Record Transaction")

    if tx_submit:
        if not client_name_tx or amount_tx == 0:
            st.error("Client name and amount are required.")
        else:
            new_tx = pd.DataFrame([[client_name_tx, tx_type, amount_tx, date_tx.strftime('%d-%m-%Y')]],
                                  columns=st.session_state.transactions.columns)
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_tx], ignore_index=True)
            st.success(f"Transaction for {client_name_tx} recorded.")

# Benchmark Rate Update
st.subheader("⚙️ Update Benchmark Rate")
new_rate = st.number_input("Benchmark Rate (% p.a.)", value=st.session_state.benchmark_rate, step=0.5)

if st.button("Update Benchmark Rate"):
    st.session_state.benchmark_rate = new_rate
    for index, row in st.session_state.deposits.iterrows():
        new_rate_per_client = st.session_state.benchmark_rate - row["Spread (%)"]
        st.session_state.deposits.at[index, "Depositor Rate (%)"] = new_rate_per_client
    st.success(f"Benchmark rate updated to {new_rate}% p.a. and depositor rates adjusted.")

# Display Deposits and Transactions
st.subheader("📄 Current Deposits")
st.dataframe(st.session_state.deposits.style.format({
    "Deposit Amount (NGN)": "₦{:,.2f}",
    "Spread (%)": "{:.2f}",
    "Depositor Rate (%)": "{:.2f}"
}))

st.subheader("📊 Transactions (Additional Deposits / Withdrawals)")
st.dataframe(st.session_state.transactions.style.format({
    "Amount": "₦{:,.2f}"
}))

# Export to CSV
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_deposits = convert_df(st.session_state.deposits)
csv_transactions = convert_df(st.session_state.transactions)

st.download_button("📥 Download Deposits as CSV", csv_deposits, file_name='seedtime_deposits.csv', mime='text/csv')
st.download_button("📥 Download Transactions as CSV", csv_transactions, file_name='seedtime_transactions.csv', mime='text/csv')
