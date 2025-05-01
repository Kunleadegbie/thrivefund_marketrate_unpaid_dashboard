import streamlit as st
import pandas as pd

st.set_page_config(page_title="ROI Calculator", layout="centered")

st.title("💰 ThriveFund ROI Calculator (Compound Interest)")

st.header("📥 Investment Details")
principal = st.number_input("Principal Amount (₦)", min_value=0.0, format="%.2f")
tenor = st.number_input("Tenor (Days)", min_value=1, format="%d")
rate = st.number_input("Interest Rate (% per annum)", min_value=0.0, format="%.2f")

st.markdown("---")
st.subheader("➕ Additional Deposits (Optional)")
deposit_count = st.number_input("Number of Additional Deposits", min_value=0, step=1)
deposits = []
for i in range(int(deposit_count)):
    st.markdown(f"**Deposit {i+1}**")
    amount = st.number_input(f"Amount (₦) for Deposit {i+1}", min_value=0.0, format="%.2f", key=f"dep_amt_{i}")
    day = st.number_input(f"Day of Deposit {i+1}", min_value=0, max_value=tenor, format="%d", key=f"dep_day_{i}")
    deposits.append((day, amount))

st.markdown("---")
st.subheader("➖ Withdrawals (Optional)")
withdrawal_count = st.number_input("Number of Withdrawals", min_value=0, step=1)
withdrawals = []
for i in range(int(withdrawal_count)):
    st.markdown(f"**Withdrawal {i+1}**")
    amount = st.number_input(f"Amount (₦) for Withdrawal {i+1}", min_value=0.0, format="%.2f", key=f"with_amt_{i}")
    day = st.number_input(f"Day of Withdrawal {i+1}", min_value=0, max_value=tenor, format="%d", key=f"with_day_{i}")
    withdrawals.append((day, -amount))

if st.button("Calculate ROI"):
    if principal <= 0 or tenor <= 0 or rate <= 0:
        st.error("Please enter positive values for Principal, Tenor, and Interest Rate.")
    else:
        transactions = [(0, principal)] + deposits + withdrawals
        transactions.sort()

        balance = 0
        roi = 0
        last_day = 0
        details = []

        daily_rate = (rate / 100) / 365

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

        df = pd.DataFrame(details)
        st.subheader("📊 Transaction Details")
        st.dataframe(df.style.format({"Transaction": "₦{:.2f}", "Balance": "₦{:.2f}", "Interest Accrued": "₦{:.2f}"}))

        st.subheader("📈 ROI Summary")
        st.success(f"**Total ROI (Compound Interest):** ₦{roi:,.2f}")
        st.info(f"**Final Balance (including ROI):** ₦{balance:,.2f}")

