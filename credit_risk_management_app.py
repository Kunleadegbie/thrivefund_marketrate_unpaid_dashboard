import streamlit as st

# Function to calculate risk rating
def assess_risk(missed_payments, repayment_timeliness, dti_ratio, outstanding_balance_ratio, months_remaining):
    risk_score = 0

    # Missed Payments
    if missed_payments >= 2:
        risk_score += 30
    elif missed_payments == 1:
        risk_score += 15

    # Repayment Timeliness
    if repayment_timeliness < 80:
        risk_score += 25
    elif repayment_timeliness < 90:
        risk_score += 10

    # DTI Ratio
    if dti_ratio > 0.5:
        risk_score += 20
    elif dti_ratio > 0.3:
        risk_score += 10

    # Outstanding Balance vs Loan Tenure Progress
    if outstanding_balance_ratio >= 0.8 and months_remaining < 0.5:
        risk_score += 20

    # Final Risk Rating
    if risk_score >= 50:
        risk_rating = "🚨 High Risk"
    elif risk_score >= 30:
        risk_rating = "⚠️ Medium Risk"
    else:
        risk_rating = "✅ Low Risk"

    return risk_rating, risk_score


# Streamlit UI Setup
st.set_page_config(page_title="CHUMCRED LIMITED Credit & Risk Management", page_icon="📊")

# Title and Styling
st.markdown("""
    <h1 style='text-align: center; color: navy;'>CHUMCRED LIMITED</h1>
    <h3 style='text-align: center; color: darkred;'>Credit & Risk Management Dashboard</h3>
    <hr style='border:1px solid gray'>
""", unsafe_allow_html=True)

st.subheader("📋 Enter Loan Monitoring Details")

# Input fields
loan_amount = st.number_input("Original Loan Amount (NGN)", min_value=5000, step=5000, value=50000)
outstanding_balance = st.number_input("Outstanding Loan Balance (NGN)", min_value=0, step=1000, value=20000)
monthly_income = st.number_input("Current Monthly Income (NGN)", min_value=10000, step=5000, value=50000)
missed_payments = st.number_input("Number of Missed Payments", min_value=0, max_value=10, value=0)
repayment_timeliness = st.slider("Repayment Timeliness (%)", min_value=0, max_value=100, value=95)
months_remaining = st.number_input("Loan Tenure Remaining (months)", min_value=0, max_value=36, value=6)

# Risk Calculation button
if st.button("📊 Assess Credit Risk"):
    dti_ratio = outstanding_balance / monthly_income
    outstanding_balance_ratio = outstanding_balance / loan_amount
    tenure_progress = months_remaining / 12  # Assuming a 12-month loan initially

    risk_rating, risk_score = assess_risk(
        missed_payments,
        repayment_timeliness,
        dti_ratio,
        outstanding_balance_ratio,
        tenure_progress
    )

    st.success(f"**Risk Assessment Result:** {risk_rating}")
    st.info(f"**Risk Score:** {risk_score} points")
    st.info(f"**Debt-to-Income Ratio:** {dti_ratio:.2f}")
    st.info(f"**Outstanding Balance Ratio:** {outstanding_balance_ratio:.2f}")

    if risk_rating == '🚨 High Risk':
        st.error("⚠️ Action Needed: Consider recovery measures or restructure.")
    elif risk_rating == '⚠️ Medium Risk':
        st.warning("📌 Monitor closely: Possible early warning signals.")
    else:
        st.balloons()

# Footer
st.markdown("""
    <hr style='border:0.5px solid lightgray'>
    <div style='text-align: center; font-size: 14px;'>© 2025 CHUMCRED LIMITED | Powered by Digital Analytics</div>
""", unsafe_allow_html=True)
