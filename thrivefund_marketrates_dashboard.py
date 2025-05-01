import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Chumcred Profit Spread Manager", page_icon="💰", layout="wide")

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
    .css-18e3th9 {{
        padding: 2rem;
    }}
    .css-1d391kg {{
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
st.markdown(f"<h2 style='color:{primary_color};'>💼 Chumcred LIMITED | Profit Spread Manager</h2>", unsafe_allow_html=True)
st.markdown(f"<h5 style='color:{accent_color};'>Smart, Dynamic, Profitable 💸</h5>", unsafe_allow_html=True)

# Session State for Benchmark Rate and Deposits
if 'benchmark_rate' not in st.session_state:
    st.session_state.benchmark_rate = 21.0

if 'deposits' not in st.session_state:
    st.session_state.deposits = pd.DataFrame(columns=["Client Name", "Deposit Amount (NGN)", "Spread (%)", "Depositor Rate (%)"])

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

# Deposit Form
with st.form("deposit_form"):
    st.subheader("➕ Add New Deposit Record")
    col1, col2 = st.columns(2)
    client_name = col1.text_input("Client Name")
    deposit_amount = col2.number_input("Deposit Amount (NGN)", min_value=0.0, step=1000.0)
    submitted = st.form_submit_button("Add Deposit")

    if submitted:
        if deposit_amount < 5000:
            st.error("Minimum deposit is NGN 5,000.")
        elif not client_name:
            st.error("Client name is required.")
        else:
            spread = get_spread(deposit_amount)
            depositor_rate = st.session_state.benchmark_rate - spread
            new_entry = pd.DataFrame([[client_name, deposit_amount, spread, depositor_rate]],
                                     columns=st.session_state.deposits.columns)
            st.session_state.deposits = pd.concat([st.session_state.deposits, new_entry], ignore_index=True)
            st.success(f"Deposit for {client_name} added successfully.")

# Benchmark Rate Adjustment
st.subheader("⚙️ Update Benchmark Rate")
new_rate = st.number_input("Benchmark Rate (% p.a.)", value=st.session_state.benchmark_rate, step=0.5)

if st.button("Update Benchmark Rate"):
    st.session_state.benchmark_rate = new_rate
    # Update all depositor rates
    for index, row in st.session_state.deposits.iterrows():
        new_rate_per_client = st.session_state.benchmark_rate - row["Spread (%)"]
        st.session_state.deposits.at[index, "Depositor Rate (%)"] = new_rate_per_client
    st.success(f"Benchmark rate updated to {new_rate}% p.a. and all depositor rates recalculated.")

# Display Deposits
st.subheader("📄 Current Deposits & Rates")
st.dataframe(st.session_state.deposits.style.format({
    "Deposit Amount (NGN)": "₦{:,.2f}",
    "Spread (%)": "{:.2f}",
    "Depositor Rate (%)": "{:.2f}"
}), height=400)

# Export to Excel
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(st.session_state.deposits)

st.download_button(
    label="📥 Download as CSV",
    data=csv,
    file_name='chumcred_deposits.csv',
    mime='text/csv'
)
