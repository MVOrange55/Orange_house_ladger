import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. Light Mode CSS - Force High Visibility
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff7e00;
    }
    .stButton>button {
        background-color: #ff7e00;
        color: white !important;
        font-weight: bold;
    }
    /* Fix for sidebar text visibility */
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Permanent Column Names - This prevents the KeyError
# NEVER CHANGE THESE NAMES
FINAL_COLS = ["Tracking_ID", "Date", "Type", "Particulars", "Emp_ID", "Recipient", "Approved_By", "Medium", "Amount"]

# Initialize Ledger
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=FINAL_COLS)

def get_new_tid():
    return f"OHL-{random.randint(1000, 9999)}"

# Side Navigation
with st.sidebar:
    st.markdown("<h1 style='color: #ff7e00; text-align: center;'>ORANGE HOUSE</h1>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None, 
        options=["Dashboard", "Add Receipt", "Add Payment", "Manage Reports", "Cash Counter"],
        icons=["house", "plus-circle", "dash-circle", "table", "calculator"], 
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#ff7e00"}}
    )

# --- PAGES ---

if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    
    if not df.empty:
        # Force Amount to be a number to fix calculation errors
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        t_in = df[df['Type'] == 'Receipt']['Amount'].sum()
        t_out = df[df['Type'] == 'Payment']['Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance", f"₹ {t_in - t_out:,.2f}")
        
        st.subheader("Transaction Records")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("The ledger is currently empty.")

elif selected == "Add Receipt":
    st.title("📥 Add Receipt")
    with st.form("receipt_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        p = col1.text_input("Particulars")
        e = col2.text_input("Employee ID", value="ADMIN")
        a = col2.number_input("Amount (₹)", min_value=0.0)
        m = st.selectbox("Medium", ["Cash", "Bank", "UPI"])
        
        if st.form_submit_button("Save Entry"):
            tid = get_new_tid()
            # Adding row using the strict column list
            new_data = [tid, str(d), "Receipt", p, e, "Company", "Self", m, a]
            new_row = pd.DataFrame([new_data], columns=FINAL_COLS)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"Receipt Saved! ID: {tid}")

elif selected == "Add Payment":
    st.title("📤 Add Payment")
    with st.form("pay_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        e = col1.text_input("Employee ID")
        r = col1.text_input("Paid To (Recipient)")
        p = col2.text_input("Purpose")
        a = col2.number_input("Amount (₹)", min_value=0.0)
        app = col2.text_input("Approved By")
        m = st.selectbox("Medium", ["Cash", "UPI", "Bank"])
        
        if st.form_submit_button("Save Payment"):
            if e and r and a > 0:
                tid = get_new_tid()
                new_data = [tid, str(d), "Payment", p, e, r, app, m, a]
                new_row = pd.DataFrame([new_data], columns=FINAL_COLS)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Payment Saved! ID: {tid}")
            else:
                st.error("Please fill all required fields.")

elif selected == "Manage Reports":
    st.title("📝 Edit & Delete")
    
    # 1. Edit Section
    st.subheader("Edit Data Table")
    edited_df = st.data_editor(st.session_state.ledger_data, use_container_width=True, num_rows="dynamic")
    if st.button("Commit All Changes"):
        st.session_state.ledger_data = edited_df
        st.success("Database Updated!")
    
    st.divider()
    
    # 2. Specific Delete
    st.subheader("Remove Entry")
    if not st.session_state.ledger_data.empty:
        id_list = st.session_state.ledger_data['Tracking_ID'].tolist()
        to_del = st.selectbox("Select Tracking ID to delete:", ["None"] + id_list)
        if st.button("Confirm Delete"):
            if to_del != "None":
                st.session_state.ledger_data = st.session_state.ledger_data[st.session_state.ledger_data.Tracking_ID != to_del]
                st.warning(f"Record {to_del} removed.")
                st.rerun()

    # 3. Download
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state.ledger_data.to_excel(writer, index=False)
    st.download_button("📥 Download Excel Report", buf.getvalue(), "OrangeHouse_Final.xlsx")

elif selected == "Cash Counter":
    st.title("💰 Cash Counter")
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    total = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        col = c1 if i % 2 == 0 else c2
        cnt = col.number_input(f"₹ {n} Notes", min_value=0, key=f"note_{n}")
        total += (n * cnt)
    st.subheader(f"Total Cash: ₹ {total:,.2f}")
