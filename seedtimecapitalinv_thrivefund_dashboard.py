import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="ThriveFund Dashboard", layout="centered")

# Initialize session state
if 'clients' not in st.session_state:
    st.session_state.clients = []

st.title("🌱 ThriveFund Investment Dashboard")

st.sidebar.header("📋 Navigation")
page = st.sidebar.radio("Go to", ["Add Client Record", "View & Export Records"])

# Helper: Convert client records to Excel
def export_clients_to_excel(clients):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    for client in clients:
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

    # Dynamic rate changes input
    st.subheader("📈 Money Market Rate Changes")
    rate_change_count = st.number_input("Number of Rate Changes", min_value=1, step=1, value=1)
    rate_changes = []
    for i in range(int(rate_change_count)):
        st.markdown(f"**Rate Change {i+1}**")
        rate_date = st.date_input(f"Effective Date for Rate {i+1}", format="DD-MM-YYYY", key=f"rate_date_{i}")
        rate_value = st.number_input(f"Rate (% p.a) for Rate {i+1}", min_value=0.0, format="%.2f", key=f"rate_value_{i}")
        rate_changes.append((rate_date.strftime("%d-%m-%Y"), rate_value))

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
        if name == "" or principal <= 0 or tenor <= 0 or len(rate_changes) == 0:
            st.error("Please complete all required fields and at least one rate change.")
        else:
            # Collect all transactions
            transactions = []
            transactions.append({
                "Date": principal_date.strftime("%d-%m-%Y"),
                "Type": "Initial Deposit",
                "Amount": principal
            })
            for dep in deposits:
                transactions.append({"Date": dep[0], "Type": "Additional Deposit", "Amount": dep[1]})
            for wd in withdrawals:
                transactions.append({"Date": wd[0], "Type": "Withdrawal", "Amount": wd[1]})

            # Create combined events (transactions + rate changes)
            events = []
            for t in transactions:
                events.append({"Date": t["Date"], "Event": t["Type"], "Amount": t["Amount"], "Rate": None})
            for r in rate_changes:
                events.append({"Date": r[0], "Event": "Rate Change", "Amount": None, "Rate": r[1]})

            # Sort events by date
            events_df = pd.DataFrame(events)
            events_df["Date"] = pd.to_datetime(events_df["Date"], format="%d-%m-%Y")
            events_df.sort_values("Date", inplace=True)
            events_df.reset_index(drop=True, inplace=True)

            # ROI calculation with dynamic rates
            balance = 0.0
            roi = 0.0
            last_date = events_df.loc[0, "Date"]
            current_rate = rate_changes[0][1]  # Set first rate

            details = []
            for _, row in events_df.iterrows():
                current_date = row["Date"]
                days = (current_date - last_date).days
                if days > 0:
                    interest = (balance * (current_rate / 100) * days) / 365
                    roi += interest
                else:
                    interest = 0

                if row["Event"] == "Rate Change":
                    current_rate = row["Rate"]
                elif pd.notnull(row["Amount"]):
                    balance += row["Amount"]

                details.append({
                    "Date": current_date.strftime("%d-%m-%Y"),
                    "Event": row["Event"],
                    "Transaction (₦)": row["Amount"] if pd.notnull(row["Amount"]) else 0.0,
                    "Balance After (₦)": balance,
                    "Interest Accrued (₦)": interest,
                    "Active Rate (%)": current_rate
                })

                last_date = current_date

            # Final interest from last event to maturity
            final_days = tenor - (last_date - pd.to_datetime(principal_date.strftime("%d-%m-%Y"), format="%d-%m-%Y")).days
            final_interest = (balance * (current_rate / 100) * final_days) / 365
            roi += final_interest
            maturity_date = last_date + pd.Timedelta(days=final_days)
            details.append({
                "Date": f"Maturity ({maturity_date.strftime('%d-%m-%Y')})",
                "Event": "Maturity",
                "Transaction (₦)": 0.0,
                "Balance After (₦)": balance,
                "Interest Accrued (₦)": final_interest,
                "Active Rate (%)": current_rate
            })

            st.session_state.clients.append({
                "name": name,
                "principal": principal,
                "tenor": tenor,
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
            st.write(f"**Final Balance (Before Final Interest):** ₦{client['final_balance']:,.2f}")

            df = pd.DataFrame(client["transactions"])
            st.dataframe(df.style.format({
                "Transaction (₦)": "₦{:.2f}",
                "Balance After (₦)": "₦{:.2f}",
                "Interest Accrued (₦)": "₦{:.2f}",
                "Active Rate (%)": "{:.2f}"
            }))

        excel_data = export_clients_to_excel(st.session_state.clients)
        st.download_button(
            label="📥 Download All Records as Excel",
            data=excel_data,
            file_name="ThriveFund_Client_Records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No records available yet.")
