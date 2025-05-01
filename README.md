# 📊 ThriveFund Investment & ROI Manager

A powerful interactive web dashboard built with **Streamlit** for managing investment transactions, tracking ROI, and calculating profit margins based on benchmark rates and spread margins — all on a **daily compound interest basis**.

---

## 🚀 Features

- Add and manage multiple client profiles.
- Record deposit and withdrawal transactions with tenors.
- Dynamically adjust benchmark interest rates.
- Automatically compute customer rates and profits using spread margins.
- Daily compound interest calculation with maturity logic.
- Real-time ROI projection tables and downloadable reports (CSV & Excel).

---

## 📈 Interest & Profit Logic

- **Benchmark Rate:** Annual interest rate set by the market or institution.
- **Spread:** Margin deducted from the benchmark rate to arrive at the customer rate.
- **Customer Rate:** `Benchmark Rate - Spread`.
- **Profit:** Earnings from the spread difference, applied to the balance on a daily rest, compounding basis.

---

## 📦 Installation

1. **Clone this repository**  
   ```bash
   git clone https://github.com/your-username/thrivefund-dashboard.git
   cd thrivefund-dashboard
