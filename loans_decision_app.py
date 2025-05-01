import streamlit as st

# Function to calculate a credit score internally
def calculate_credit_score(repayment_history, dti_ratio, num_defaults, num_open_loans):
    score = 500  # base score

    # Repayment history
    if repayment_history == 'Good':
        score += 100
    elif repayment_history == 'Average':
        score += 50
    else:
        score -= 50

    # Debt-to-Income Ratio
    if dti_ratio < 0.3:
        score += 80
    elif dti_ratio < 0.5:
        score += 50
    else:
        score -= 30

    # Number of Defaults
    score -= num_defaults * 40

    # Open Loans
    if num_open_loans < 3:
        score += 30
    else:
        score -= 10

    # Clamp score between 300–850
    score = max(300, min(score, 850))

    return score

# Loan decision logic using dynamic credit score
def loan_decision(customer_data, credit_score):
    score = 0

    # Age criteria
    if 25 <= customer_data['age'] <= 60:
        score += 10
    else:
        score -= 10

    # Income check
    if customer_data['monthly_income'] >= 50000:
        score += 20
    elif customer_data['monthly_income'] >= 30000:
        score += 10
    else:
        score -= 10

    # Debt-to-Income Ratio
    dti_ratio = customer_data['existing_debt'] / customer_data['monthly_income']
    if dti_ratio < 0.3:
        score += 20
    elif dti_ratio < 0.5:
        score += 10
    else:
        score -= 10

    # Use the dynamically calculated credit score
    if credit_score >= 700:
        score += 30
    elif credit_score >= 600:
        score += 15
    else:
        score -= 20

    # Loan amount vs income
    loan_to_income = customer_data['loan_amount'] / customer_data['monthly_income']
    if loan_to_income <= 1:
        score += 10
    else:
        score -= 10

    # Past default history
    if customer_data['num_defaults'] > 0:
        score -= 20

    # Final Decision
    if score >= 50:
        decision = '✅ Approved'
    elif score >= 30:
        decision = '⚠️ Review'
    else:
        decision = '❌ Rejected'

    return decision, score


# Streamlit UI Setup
st.set_page_config(page_title="CHUMCRED LIMITED Loan Decision App", page_icon="💳")

# Company Title and Styling
st.markdown("""
    <h1 style='text-align: center; color: navy;'>CHUMCRED LIMITED</h1>
    <h3 style='text-align: center; color: darkgreen;'>Digital Loan Decision Management App</h3>
    <hr style='border:1px solid gray'>
""", unsafe_allow_html=True)

st.subheader("📋 Enter Customer Loan Application Details")

# Input fields
age = st.number_input("Age", min_value=18, max_value=100, value=30)
monthly_income = st.number_input("Monthly Income (NGN)", min_value=10000, step=5000, value=50000)
existing_debt = st.number_input("Existing Debt (NGN)", min_value=0, step=1000, value=10000)
loan_amount = st.number_input("Loan Amount Requested (NGN)", min_value=5000, step=5000, value=40000)
num_defaults = st.number_input("Number of Past Loan Defaults", min_value=0, max_value=10, value=0)
num_open_loans = st.number_input("Number of Open Loans", min_value=0, max_value=10, value=1)
repayment_history = st.selectbox("Repayment History", ['Good', 'Average', 'Poor'])

# Submit button
if st.button("📝 Check Loan Decision"):
    customer_data = {
        'age': age,
        'monthly_income': monthly_income,
        'existing_debt': existing_debt,
        'loan_amount': loan_amount,
        'num_defaults': num_defaults
    }

    # Debt-to-Income ratio for credit score calculation
    dti_ratio = existing_debt / monthly_income

    # Dynamically calculate the credit score
    credit_score = calculate_credit_score(
        repayment_history,
        dti_ratio,
        num_defaults,
        num_open_loans
    )

    decision, decision_score = loan_decision(customer_data, credit_score)

    st.success(f"**Loan Decision:** {decision}")
    st.info(f"**Calculated Credit Score:** {credit_score} points")
    st.info(f"**Loan Decision Score:** {decision_score} points")

    if decision == '✅ Approved':
        st.balloons()

# Footer
st.markdown("""
    <hr style='border:0.5px solid lightgray'>
    <div style='text-align: center; font-size: 14px;'>© 2025 CHUMCRED LIMITED | Powered by Digital Analytics</div>
""", unsafe_allow_html=True)
