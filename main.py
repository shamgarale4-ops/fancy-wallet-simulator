"""
Digital Wallet Simulator (SkyWallet Pro )
-------------------------------------------------------
Project:     Digital Wallet Simulator
Prepared By: Samadhan Appasaheb Garale
Guided By:   Sanket Dodya Sir

Features:
- 🔢 Strict Numeric Check for Bill Payments
- 💡 Bill Payments, Notifications, Credit Score
- 🔒 SHA-256 Security & Auto-Clear
- 🎨 Premium Dark UI
"""

import streamlit as st
import json
import time
import random
from datetime import datetime
import os
import pandas as pd
import qrcode
import hashlib
import plotly.express as px
from io import BytesIO

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="SkyWallet Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. ENTERPRISE CSS STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Global Theme */
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; }
    
    /* Sidebar Menu */
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display: none; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 12px 20px; margin-bottom: 8px; border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05); background-color: #0f172a;
        color: #94a3b8; cursor: pointer; transition: all 0.3s ease; font-weight: 500;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background-color: #1e293b; transform: translateX(5px); color: #e2e8f0; border-color: #3b82f6;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #172554 0%, #2563eb 100%);
        color: white; border: 1px solid #3b82f6; font-weight: 600;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transform: translateX(5px);
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important; color: #f8fafc !important;
        border: 1px solid #334155 !important; border-radius: 10px; padding: 10px;
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8); color: white;
        border: none; border-radius: 10px; font-weight: 600; padding: 0.7rem 1.5rem;
        transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.6); transform: translateY(-2px);
    }

    /* Cards */
    .stat-card {
        background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px);
        padding: 1.5rem; border-radius: 16px; border: 1px solid #334155;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;
    }
    .stat-value { font-size: 2rem; font-weight: 700; color: #60a5fa; }
    .stat-label { font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; }
    
    /* Credit Score Circle */
    .score-circle {
        width: 100px; height: 100px; border-radius: 50%;
        border: 8px solid #10b981; display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; font-weight: bold; color: #10b981; margin: 0 auto;
    }

    div[data-testid="stDataFrame"] { background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "wallet_data.json"
CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Education", "Health", "Other"]

# ---------------------------------------------------------
# 3. DATA & SECURITY LOGIC
# ---------------------------------------------------------
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def default_accounts():
    h1 = hash_pin("1111")
    h2 = hash_pin("2222")
    admin = hash_pin("0000")
    return {
        "alice": {"pin": h1, "balance": 5000.0, "locked": False, "is_verified": True, "enable_2fa": True, "transactions": [], "notifications": []},
        "bob": {"pin": h2, "balance": 1500.0, "locked": False, "is_verified": False, "enable_2fa": False, "transactions": [], "notifications": []},
        "admin": {"pin": admin, "balance": 0.0, "locked": False, "is_verified": True, "enable_2fa": False, "transactions": [], "notifications": []} 
    }

def load_accounts():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                accs = data.get("accounts", default_accounts())
                for u in accs:
                    if "notifications" not in accs[u]: accs[u]["notifications"] = []
                    if "is_verified" not in accs[u]: accs[u]["is_verified"] = False
                return accs
        except: pass
    return default_accounts()

def save_accounts():
    try:
        with open(DB_FILE, "w") as f:
            json.dump({"accounts": st.session_state.accounts}, f, indent=2)
    except Exception as e: st.error(f"DB Error: {e}")

def init_state():
    if "accounts" not in st.session_state: st.session_state.accounts = load_accounts()
    if "current_user" not in st.session_state: st.session_state.current_user = None
    if "login_attempts" not in st.session_state: st.session_state.login_attempts = {}
    if "signup_step" not in st.session_state: st.session_state.signup_step = 1
    if "generated_otp" not in st.session_state: st.session_state.generated_otp = None
    if "last_active" not in st.session_state: st.session_state.last_active = time.time()

init_state()

def check_timeout():
    if st.session_state.current_user:
        if time.time() - st.session_state.last_active > 300: # 5 mins
            st.session_state.current_user = None
            st.warning("Session Timed Out.")
            time.sleep(1)
            st.rerun()
        else: st.session_state.last_active = time.time()

def make_txn(txn_type, amount, note, category, counterparty):
    return {
        "id": f"TXN-{int(time.time())}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": txn_type,
        "amount": float(round(amount, 2)),
        "note": note,
        "category": category,
        "counterparty": counterparty,
    }

def add_notification(username, message):
    if username in st.session_state.accounts:
        notif = {"time": datetime.now().strftime("%H:%M"), "msg": message}
        st.session_state.accounts[username]["notifications"].insert(0, notif)

def compute_credit_score(acc):
    score = 600 + int(acc['balance'] / 100)
    return min(score, 850)

def get_recent_contacts(acc):
    contacts = set()
    for tx in acc.get("transactions", []):
        if tx["type"] in ["transfer_out", "qr_out"]: contacts.add(tx["counterparty"])
    return sorted(list(contacts))

# ---------------------------------------------------------
# 4. AUTHENTICATION UI
# ---------------------------------------------------------
def ui_create_account():
    st.subheader("📝 Create New Account")
    st.markdown('<div class="stat-card" style="padding:10px; border-left:4px solid #3b82f6; margin-bottom:20px;">💡 <b>Tip:</b> Use <b>TAB</b> to switch boxes. <b>ENTER</b> to submit.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        if st.session_state.signup_step == 1:
            with st.form("signup_1", clear_on_submit=False):
                u = st.text_input("Username (No spaces)")
                mob = st.text_input("Mobile Number (10 digits)")
                c1, c2 = st.columns(2)
                with c1: p = st.text_input("Set PIN (4 digits)", type="password", max_chars=4)
                with c2: cp = st.text_input("Confirm PIN", type="password", max_chars=4)
                bal = st.number_input("Initial Deposit", min_value=0.0, step=100.0)
                
                if st.form_submit_button("Get Verification Code"):
                    u = u.strip().lower()
                    if not u or " " in u: st.error("Invalid Username.")
                    elif u in st.session_state.accounts: st.warning(f"Username '{u}' taken.")
                    elif len(mob)!=10 or not mob.isdigit(): st.error("Invalid Mobile Number (Digits Only).")
                    elif len(p)!=4 or not p.isdigit(): st.error("PIN must be 4 digits.")
                    elif p!=cp: st.error("PINs do not match.")
                    else:
                        st.session_state.signup_data = {"u":u, "p":hash_pin(p), "bal":bal}
                        st.session_state.generated_otp = str(random.randint(1000, 9999))
                        st.session_state.signup_step = 2
                        st.rerun()
        
        elif st.session_state.signup_step == 2:
            otp = st.session_state.generated_otp
            st.success(f"🔔 SIMULATION SMS: Your OTP is **{otp}**")
            with st.form("signup_2", clear_on_submit=False):
                user_otp = st.text_input("Enter 4-digit OTP", max_chars=4)
                if st.form_submit_button("Verify & Finish"):
                    if user_otp == otp:
                        d = st.session_state.signup_data
                        txns = []
                        if d["bal"]>0: txns.append(make_txn("deposit", d["bal"], "Opening Balance", "Other", "Self"))
                        st.session_state.accounts[d["u"]] = {
                            "pin": d["p"], "balance": d["bal"], "locked": False, 
                            "is_verified": True, "enable_2fa": False, "transactions": txns, "notifications": []
                        }
                        save_accounts()
                        st.session_state.current_user = d["u"]
                        st.session_state.login_attempts[d["u"]] = 0
                        st.session_state.signup_step = 1
                        st.success("Created! Logging in...")
                        time.sleep(0.5); st.rerun()
                    else: st.error("Invalid OTP")

def ui_login():
    st.subheader("🔐 Secure Login")
    with st.container(border=True):
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("PIN", type="password", max_chars=4)
            if st.form_submit_button("👉 Login"):
                u = u.strip().lower()
                acc = st.session_state.accounts.get(u)
                if not acc: st.error("User not found.")
                elif acc.get("locked"): st.error("Account Locked.")
                elif acc["pin"] == hash_pin(p):
                    st.session_state.current_user = u
                    st.session_state.login_attempts[u] = 0
                    st.success("Welcome back!"); time.sleep(0.5); st.rerun()
                else:
                    fails = st.session_state.login_attempts.get(u, 0) + 1
                    st.session_state.login_attempts[u] = fails
                    if fails >= 3:
                        acc["locked"] = True; save_accounts(); st.error("Locked.")
                    else: st.warning(f"Wrong PIN. Tries left: {3-fails}")

# ---------------------------------------------------------
# 5. CORE FEATURES
# ---------------------------------------------------------
def ui_dashboard():
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    score = compute_credit_score(acc)
    
    c1, c2 = st.columns([3, 1])
    with c1: st.title(f"👋 Hello, {user.capitalize()}")
    with c2: st.markdown("### ✅ Verified")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Balance</div>
            <div class="stat-value">₹{acc['balance']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card" style="text-align:center;">
            <div class="score-circle">{score}</div>
            <div style="margin-top:10px; color:#94a3b8;">Credit Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📉 Recent Transactions")
    df = pd.DataFrame(acc["transactions"])
    if not df.empty:
        st.dataframe(df[['timestamp', 'type', 'amount', 'note']].tail(5).sort_values('timestamp', ascending=False), use_container_width=True, hide_index=True)
    else: st.info("No recent activity.")

def ui_notifications():
    st.header("🔔 Notifications")
    user = st.session_state.current_user
    notifs = st.session_state.accounts[user].get("notifications", [])
    
    if notifs:
        if st.button("Clear All"):
            st.session_state.accounts[user]["notifications"] = []
            save_accounts(); st.rerun()
        for n in notifs:
            st.info(f"**{n['time']}** - {n['msg']}")
    else:
        st.success("No new notifications.")

def ui_bill_pay():
    st.header("💡 Bill Payments")
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    
    bill_type = st.selectbox("Select Biller", ["📱 Mobile Recharge", "⚡ Electricity Bill", "📺 DTH / Cable", "🌐 Broadband"])
    
    with st.container(border=True):
        with st.form("bill_pay", clear_on_submit=True):
            # --- FIX: Added help text about numbers only ---
            consumer_no = st.text_input("Consumer Number / Mobile No", help="Enter numbers only")
            amt = st.number_input("Bill Amount (₹)", min_value=0.0)
            pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            
            if st.form_submit_button(f"Pay {bill_type}"):
                # --- FIX: Strict Validation Check ---
                if not consumer_no: st.error("Enter Consumer Number")
                elif not consumer_no.isdigit(): st.error("❌ Invalid Format: Consumer Number must contain only digits (0-9).")
                elif amt <= 0: st.error("Invalid Amount")
                elif hash_pin(pin) != acc["pin"]: st.error("Wrong PIN")
                elif acc["balance"] < amt: st.error("Insufficient Balance")
                else:
                    acc["balance"] -= amt
                    acc["transactions"].append(make_txn("bill_pay", amt, bill_type, "Bills", "Utility"))
                    add_notification(user, f"Paid {bill_type} of ₹{amt}")
                    save_accounts()
                    st.balloons()
                    st.success(f"✅ {bill_type} Successful!")

def ui_transfer():
    st.header("💸 Transfer (UPI)")
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    
    contacts = get_recent_contacts(acc)
    selected = ""
    if contacts:
        opt = ["-- Select Contact --"] + contacts
        ch = st.selectbox("🔍 Quick Pay", opt)
        if ch != "-- Select Contact --": selected = ch

    with st.container(border=True):
        with st.form("transfer", clear_on_submit=True):
            to = st.text_input("Receiver Username", value=selected)
            amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            note = st.text_input("Note", value="Payment")
            pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            
            if st.form_submit_button("Send Money"):
                rec = to.strip().lower()
                if not rec or rec not in st.session_state.accounts: st.error("User not found")
                elif rec == user: st.error("Self transfer not allowed")
                elif amt <= 0: st.error("Invalid Amount")
                elif acc["balance"] < amt: st.error("Low Balance")
                elif hash_pin(pin) != acc["pin"]: st.error("Wrong PIN")
                else:
                    acc["balance"] -= amt
                    acc["transactions"].append(make_txn("transfer_out", amt, note, "Transfer", rec))
                    st.session_state.accounts[rec]["balance"] += amt
                    st.session_state.accounts[rec]["transactions"].append(make_txn("transfer_in", amt, note, "Uncategorized", user))
                    add_notification(rec, f"Received ₹{amt} from {user}")
                    save_accounts()
                    st.success(f"✅ Sent ₹{amt} to {rec}")

def ui_deposit():
    st.header("📥 Add Money")
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    with st.container(border=True):
        with st.form("deposit", clear_on_submit=True):
            amt = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            if st.form_submit_button("Deposit"):
                if amt <= 0: st.error("Invalid Amount")
                elif hash_pin(pin) != acc["pin"]: st.error("Wrong PIN")
                else:
                    acc["balance"] += amt
                    acc["transactions"].append(make_txn("deposit", amt, "Wallet Load", "Other", "Bank"))
                    save_accounts(); st.success(f"✅ Added ₹{amt}")

def ui_withdraw():
    st.header("🏧 Withdraw")
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    with st.container(border=True):
        with st.form("withdraw", clear_on_submit=True):
            amt = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            cat = st.selectbox("Category", CATEGORIES)
            note = st.text_input("Note", value="Cash")
            pin = st.text_input("Confirm PIN", type="password", max_chars=4)
            if st.form_submit_button("Withdraw"):
                if amt <= 0: st.error("Invalid Amount")
                elif amt > acc["balance"]: st.error("Low Balance")
                elif hash_pin(pin) != acc["pin"]: st.error("Wrong PIN")
                else:
                    acc["balance"] -= amt
                    acc["transactions"].append(make_txn("withdraw", amt, note, cat, "ATM"))
                    save_accounts(); st.success(f"✅ Withdrawn ₹{amt}")

def ui_qr_tools():
    st.header("🟦 QR Code")
    user = st.session_state.current_user
    t1, t2 = st.tabs(["Generate QR", "Scan QR"])
    
    with t1:
        with st.form("qr_make"):
            amt = st.number_input("Amount", min_value=0.0)
            if st.form_submit_button("Create QR"):
                data = json.dumps({"to": user, "amount": amt, "ts": str(time.time())})
                qr = qrcode.QRCode(box_size=10, border=2); qr.add_data(data); qr.make(fit=True)
                img = qr.make_image(fill_color="#0284c7", back_color="white")
                buf = BytesIO(); img.save(buf)
                st.image(buf.getvalue(), width=250)
                st.code(data, language="json")
    
    with t2:
        user_acc = st.session_state.accounts[user]
        with st.form("qr_scan", clear_on_submit=True):
            payload = st.text_area("Paste QR JSON")
            cat = st.selectbox("Category", CATEGORIES)
            pin = st.text_input("PIN", type="password", max_chars=4)
            if st.form_submit_button("Pay"):
                try:
                    d = json.loads(payload); to_u = d["to"]; amt = d["amount"]
                    if not to_u in st.session_state.accounts: st.error("Invalid QR")
                    elif hash_pin(pin) != user_acc["pin"]: st.error("Wrong PIN")
                    elif user_acc["balance"] < amt: st.error("Low Balance")
                    else:
                        user_acc["balance"] -= amt
                        st.session_state.accounts[to_u]["balance"] += amt
                        user_acc["transactions"].append(make_txn("qr_out", amt, "QR Pay", cat, to_u))
                        st.session_state.accounts[to_u]["transactions"].append(make_txn("qr_in", amt, "QR Pay", "Sales", user))
                        add_notification(to_u, f"QR Payment: Received ₹{amt} from {user}")
                        save_accounts(); st.success("Paid!")
                except: st.error("Invalid Data")

def ui_history():
    st.header("📜 Analysis")
    user = st.session_state.current_user
    df = pd.DataFrame(st.session_state.accounts[user]["transactions"])
    if not df.empty:
        st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)
        st.markdown("### 📊 Spending Breakdown")
        out = df[df['type'].isin(['withdraw', 'transfer_out', 'qr_out', 'bill_pay'])]
        if not out.empty:
            fig = px.pie(out, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    else: st.info("Empty.")

def ui_admin():
    st.header("👑 Admin")
    accs = st.session_state.accounts
    total = sum(a['balance'] for a in accs.values())
    st.metric("System Funds", f"₹{total:,.2f}")
    data = [{"User": u, "Balance": d['balance'], "Txns": len(d['transactions'])} for u, d in accs.items()]
    st.dataframe(pd.DataFrame(data), use_container_width=True)

def ui_settings():
    st.header("⚙️ Settings")
    user = st.session_state.current_user
    acc = st.session_state.accounts[user]
    
    with st.form("pin_chg", clear_on_submit=True):
        st.subheader("Change PIN")
        old = st.text_input("Old PIN", type="password", max_chars=4)
        new = st.text_input("New PIN", type="password", max_chars=4)
        if st.form_submit_button("Update"):
            if hash_pin(old) == acc["pin"] and len(new)==4 and new.isdigit():
                acc["pin"] = hash_pin(new); save_accounts(); st.success("Updated!")
            else: st.error("Invalid Details")

# ---------------------------------------------------------
# 6. MAIN ROUTER
# ---------------------------------------------------------
def main():
    check_timeout()
    if not st.session_state.current_user:
        auth = st.sidebar.radio("Auth", ["Login", "Sign Up"])
        if auth=="Login": ui_login()
        else: ui_create_account()
    else:
        with st.sidebar:
            st.title("🔷 SkyWallet Pro")
            st.caption(f"User: {st.session_state.current_user.upper()}")
            
            # Notification Badge
            user = st.session_state.current_user
            notif_count = len(st.session_state.accounts[user].get("notifications", []))
            notif_label = f"Notifications ({notif_count})" if notif_count > 0 else "Notifications"
            
            menu = st.radio("Menu", [
                "Dashboard", "Add Money", "Withdraw", "Transfer", "Bill Payment",
                "My QR & Scan", notif_label, "History & Reports", "Settings"
            ])
            if st.session_state.current_user == "admin": 
                if st.button("Admin Panel"): menu = "Admin Panel"
            
            st.markdown("---")
            if st.button("Logout"): st.session_state.current_user = None; st.rerun()

        if menu == "Dashboard": ui_dashboard()
        elif menu == "Add Money": ui_deposit()
        elif menu == "Withdraw": ui_withdraw()
        elif menu == "Transfer": ui_transfer()
        elif menu == "Bill Payment": ui_bill_pay()
        elif menu == "My QR & Scan": ui_qr_tools()
        elif menu == notif_label: ui_notifications()
        elif menu == "History & Reports": ui_history()
        elif menu == "Settings": ui_settings()
        elif menu == "Admin Panel": ui_admin()

if __name__ == "__main__":
    main()
