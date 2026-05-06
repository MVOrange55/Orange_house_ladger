import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. Clean Light Mode CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #262730; }
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        border-left: 5px solid #ff7e00;
    }
    .stButton>button {
        background-color: #ff7e00;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] { background-color: #f1f3f5; }
    </style>
    """, unsafe_allow_html=True)

# 3. Standardized Data Storage (Column Names Fixed)
# We use these exact names everywhere to prevent KeyError
COLUMNS = ["Tracking_ID", "Date", "Type", "Particulars", "Emp_ID", "Recipient", "Approved_By", "Medium", "Amount"]

if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=COLUMNS)

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
        styles={"nav-link-selected": {"background-color": "#ff7e00", "color": "white"}}
    )

# --- DASHBOARD ---
if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    
    if not df.empty:
        # Converting Amount to numeric safely to avoid errors
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        t_in = df[df['Type'] == 'Receipt']['Amount'].sum()
        t_out = df[df['Type'] == 'Payment']['Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance", f"₹ {t_in - t_out:,.2f}")
        
        st.subheader("Transaction History")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No records found yet.")

# --- ADD RECEIPT ---
elif selected == "Add Receipt":
    st.title("📥 Add Receipt")
    with st.form("r_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        pt = col1.text_input("Particulars")
        eid = col2.text_input("Employee ID", value="ADMIN")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        md = st.selectbox("Medium", ["Bank Transfer", "Cash", "UPI", "Cheque"])
        
        if st.form_submit_button("Save Receipt"):
            if pt and am > 0:
                tid = generate_tracking_id()
                new_row = pd.DataFrame([[tid, str(dt), "Receipt", pt, eid, "Company", "Self", md, am]], columns=COLUMNS)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Saved! ID: {tid}")
            else:
                st.error("Please enter Particulars and Amount.")

# --- ADD PAYMENT ---
elif selected == "Add Payment":
    st.title("📤 Add Payment")
    with st.form("p_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        eid = col1.text_input("Employee ID")
        rc = col1.text_input("Recipient")
        pt = col2.text_input("Purpose")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        ap = col2.text_input("Approved By")
        md = st.selectbox("Medium", ["Cash", "Bank Transfer", "UPI"])
        
        if st.form_submit_button("Save Payment"):
            if eid and rc and am > 0:
                tid = generate_tracking_id()
                new_row = pd.DataFrame([[tid, str(dt), "Payment", pt, eid, rc, ap, md, am]], columns=COLUMNS)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Payment Recorded! ID: {tid}")
            else:
                st.error("Fields cannot be empty.")

# --- MANAGE REPORTS ---
elif selected == "Manage Reports":
    st.title("📝 Manage Records")
    
    # Editable Table
    st.subheader("Edit/View Data")
    updated_df = st.data_editor(st.session_state.ledger_data, num_rows="dynamic", use_container_width=True)
    if st.button("Save Changes"):
        st.session_state.ledger_data = updated_df
        st.success("Database Updated!")

    st.divider()

    # Delete Functionality
    st.subheader("Delete Record")
    if not st.session_state.ledger_data.empty:
        ids = st.session_state.ledger_data['Tracking_ID'].tolist()
        to_del = st.selectbox("Select ID to delete:", ["None"] + ids)
        if st.button("Delete Now"):
            if to_del != "None":
                st.session_state.ledger_data = st.session_state.ledger_data[st.session_state.ledger_data.Tracking_ID != to_del]
                st.warning(f"Record {to_del} deleted.")
                st.rerun()
    else:
        st.write("No records to delete.")

    # Excel Download
    if not st.session_state.ledger_data.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            st.session_state.ledger_data.to_excel(writer, index=False)
        st.download_button("📥 Download Excel Report", buf.getvalue(), "OrangeHouse_Report.xlsx")

# --- CASH COUNTER ---
elif selected == "Cash Counter":
    st.title("💰 Cash Counter")
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    total = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        col = c1 if i % 2 == 0 else c2
        count = col.number_input(f"₹ {n} Notes", min_value=0, key=f"n_{n}")
        total += (n * count)
    st.markdown(f"<div style='background-color:#ff7e00; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>Total: ₹ {total:,.2f}</h2></div>", unsafe_allow_html=True)
