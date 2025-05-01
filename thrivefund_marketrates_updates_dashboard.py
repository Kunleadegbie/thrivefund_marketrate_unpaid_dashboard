import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

# Function to calculate daily ROI with compound interest
def calculate_roi(transactions, benchmark_changes):
    transactions['Date'] = pd.to_datetime(transactions['Date'], format='%d-%m-%Y')
    benchmark_changes['Date'] = pd.to_datetime(benchmark_changes['Date'], format='%d-%m-%Y')
    transactions = transactions.sort_values('Date').reset_index(drop=True)
    benchmark_changes = benchmark_changes.sort_values('Date')

    balance = 0
    roi = 0
    current_rate = benchmark_changes.iloc[0]['Benchmark Rate (%)']

    transactions['Benchmark Rate (%)'] = 0.0
    transactions['ROI (₦)'] = 0.0
    transactions['Balance (₦)'] = 0.0

    last_date = transactions.iloc[0]['Date']

    for i in range(len(transactions)):
        today = transactions.iloc[i]['Date']

        # Check for rate changes before today's date
        rate_changes = benchmark_changes[(benchmark_changes['Date'] > last_date) & (benchmark_changes['Date'] <= today)]
        for _, row in rate_changes.iterrows():
            days_diff = (row['Date'] - last_date).days
            daily_rate = (current_rate / 100) / 365
            roi += balance * ((1 + daily_rate) ** days_diff - 1)
            last_date = row['Date']
            current_rate = row['Benchmark Rate (%)']

        # Now process days_diff from last_date to today
        days_diff = (today - last_date).days
        daily_rate = (current_rate / 100) / 365
        roi += balance * ((1 + daily_rate) ** days_diff - 1)
        last_date = today

        # Apply transaction
        if transactions.iloc[i]['Transaction Type'] == 'Deposit' or transactions.iloc[i]['Transaction Type'] == 'Additional Deposit':
            balance += transactions.iloc[i]['Amount (₦)']
        elif transactions.iloc[i]['Transaction Type'] == 'Withdrawal':
            balance -= transactions.iloc[i]['Amount (₦)']

        transactions.loc[i, 'Benchmark Rate (%)'] = current_rate
        transactions.loc[i, 'ROI (₦)'] = round(roi, 2)
        transactions.loc[i, 'Balance (₦)'] = round(balance, 2)

    return transactions

# Streamlit App Layout
st.set_page_config(page_title="SeedTime ThriveFund App", layout="wide")

# Logo
st.image("Seedtime capital logo.png", width=280)
st.title("📊 ThriveFund Deposit & ROI Manager")
st.write("**SeedTime Capital Management Limited** — Manage deposits, withdrawals, rate changes & ROI for multiple clients.")

# Upload transaction log CSV
transaction_file = st.file_uploader("📄 Upload Transaction CSV (per client)", type=["csv"])
benchmark_file = st.file_uploader("📄 Upload Benchmark Rate Changes CSV", type=["csv"])

if transaction_file and benchmark_file:
    transactions = pd.read_csv(transaction_file)
    benchmark_changes = pd.read_csv(benchmark_file)

    result = calculate_roi(transactions, benchmark_changes)

    st.subheader("🔍 Updated Transaction Log with ROI")
    st.dataframe(result)

    # ROI Summary
    client_name = transactions['Client Name'].iloc[0]
    opening_balance = transactions[transactions['Transaction Type'] == 'Deposit']['Amount (₦)'].sum()
    total_deposits = transactions[transactions['Transaction Type'] == 'Additional Deposit']['Amount (₦)'].sum()
    total_withdrawals = transactions[transactions['Transaction Type'] == 'Withdrawal']['Amount (₦)'].sum()
    final_balance = result['Balance (₦)'].iloc[-1]
    total_roi = result['ROI (₦)'].iloc[-1]
    effective_rate = round((total_roi / opening_balance) * 100, 2) if opening_balance > 0 else 0

    summary_df = pd.DataFrame({
        'Client Name': [client_name],
        'Opening Balance (₦)': [opening_balance],
        'Total Deposits (₦)': [total_deposits],
        'Total Withdrawals (₦)': [total_withdrawals],
        'Final Balance (₦)': [final_balance],
        'Total ROI (₦)': [total_roi],
        'Effective ROI (%)': [effective_rate]
    })

    st.subheader("📈 ROI Summary")
    st.dataframe(summary_df)

    # Export to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        result.to_excel(writer, sheet_name='Transaction Log', index=False)
        summary_df.to_excel(writer, sheet_name='ROI Summary', index=False)
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel Report",
        data=processed_data,
        file_name=f"{client_name}_ThriveFund_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Also export Transaction Log CSV
    csv = result.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Transaction Log CSV",
        data=csv,
        file_name=f"{client_name}_Transaction_Log.csv",
        mime="text/csv"
    )

