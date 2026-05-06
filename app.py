import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. Improved CSS - For clear visibility on black backgrounds
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #ffffff; }
    
    /* Side Menu Visibility Fix */
    .nav-link { color: white !important; }
    .nav-link:hover { color: #ff7e00 !important; }
    
    /* Metrics box design */
    [data-testid="stMetric"] {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        border-bottom: 4px solid #ff7e00;
    }
    [data-testid="stMetricLabel"] p {
        color: #8b949e !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-size: 30px !important;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #ff7e00, #ff9e00);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Storage
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=[
        "Tracking_ID", "Date", "Type", "Particulars", "Emp_ID", "Recipient", "Approved_By", "Medium", "Amount"
    ])

def generate_tracking_id():
    return f"OHL-{random.randint(1000, 9999)}"

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ff7e00;'>ORANGE HOUSE</h2>", unsafe_allow_html=True)
    st.divider()
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Dashboard", "Add Receipt", "Add Payment", "Manage Reports", "Cash Counter"],
        icons=["speedometer2", "plus-circle", "dash-circle", "journal-text", "coin"], 
        default_index=0,
        styles={
            "container": {"background-color": "#161b22"},
            "nav-link": {"color": "white", "font-size": "16px"},
            "nav-link-selected": {"background-color": "#ff7e00", "color": "black", "font-weight": "bold"},
        }
    )

# --- Logic ---

if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        t_in = df[df['Type'] == 'Receipt']['Amount'].sum()
        t_out = df[df['Type'] == 'Payment']['Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance", f"₹ {t_in - t_out:,.2f}")
        
        st.subheader("Recent Transactions")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No records found. Please add a transaction.")

elif selected == "Add Receipt":
    st.title("📥 Add Receipt")
    with st.form("r_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        pt = col1.text_input("Particulars")
        eid = col2.text_input("Employee ID", value="ADMIN")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        md = st.selectbox("Medium", ["Bank", "Cash", "UPI", "Cheque"])
        
        if st.form_submit_button("Save Receipt"):
            tid = generate_tracking_id()
            new_row = pd.DataFrame([[tid, str(dt), "Receipt", pt, eid, "Company", "Self", md, am]], 
                                   columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"Entry Saved! ID: {tid}")

elif selected == "Add Payment":
    st.title("📤 Add Payment")
    with st.form("p_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        eid = col1.text_input("Employee ID", placeholder="EMP-101")
        rc = col1.text_input("Recipient")
        pt = col2.text_input("Purpose")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        ap = col2.text_input("Approved By")
        md = st.selectbox("Medium", ["Cash", "Bank", "UPI"])
        
        if st.form_submit_button("Save Payment"):
            if eid and rc:
                tid = generate_tracking_id()
                new_row = pd.DataFrame([[tid, str(dt), "Payment", pt, eid, rc, ap, md, am]], 
                                       columns=st.session_state.ledger_data.columns)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Payment Saved! ID: {tid}")
            else:
                st.error("Employee ID and Recipient are required!")

elif selected == "Manage Reports":
    st.title("📝 Manage Reports & Editing")
    st.write("Double-click any cell to edit, then click 'Save Changes'.")
    updated_df = st.data_editor(st.session_state.ledger_data, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes"):
        st.session_state.ledger_data = updated_df
        st.success("Database Updated!")
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state.ledger_data.to_excel(writer, index=False)
    st.download_button("📥 Download Excel Report", buf.getvalue(), "OrangeHouse_Report.xlsx")

elif selected == "Cash Counter":
    st.title("💰 Cash Counter")
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    total = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        col = c1 if i % 2 == 0 else c2
        count = col.number_input(f"₹ {n} Notes", min_value=0, key=f"n_{n}")
        total += (n * count)
    st.markdown(f"<h1 style='color:#ff7e00;'>Total Cash: ₹ {total:,.2f}</h1>", unsafe_allow_html=True)
