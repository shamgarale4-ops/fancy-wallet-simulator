# Fancy Wallet Simulator (SkyWallet Pro)

Project: Digital Wallet Simulator  
Prepared By: **Samadhan Appasaheb Garale**  
Guided By: **Sanket Dodya Sir**

## 🚀 Features

- Secure Login & Signup with PIN (SHA-256 hashed)
- Add Money, Withdraw Cash
- UPI-style Transfer between users
- Bill Payments with **numeric-only consumer number validation**
- QR Code generation & scan for payments
- Dashboard with balance, recent transactions, and credit score
- Notifications for received payments and bill payments
- Admin panel to view all users and balances
- Data stored in `wallet_data.json` locally (ignored in GitHub using `.gitignore`)

## 🛠 Tech Stack

- Python 3
- Streamlit
- Pandas
- Plotly
- qrcode
- Pillow

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run main.py
