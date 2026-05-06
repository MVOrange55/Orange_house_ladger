import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. Professional Light Mode CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #262730; }
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ff7e00;
        border: 1px solid #dee2e6;
    }
    [data-testid="stMetricLabel"] p { color: #6c757d !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] div { color: #ff7e00 !important; }
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
            "nav-link-selected": {"background-color": "#ff7e00", "color": "white"},
        }
    )

# --- DASHBOARD ---
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
        
        st.subheader("Transaction History")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No records found.")

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
                new_row = pd.DataFrame([[tid, str(dt), "Receipt", pt, eid, "Company", "Self", md, am]], 
                                       columns=st.session_state.ledger_data.columns)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Saved! ID: {tid}")

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
                new_row = pd.DataFrame([[tid, str(dt), "Payment", pt, eid, rc, ap, md, am]], 
                                       columns=st.session_state.ledger_data.columns)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"Recorded! ID: {tid}")

# --- MANAGE REPORTS (With Delete Feature) ---
elif selected == "Manage Reports":
    st.title("📝 Manage & Delete Records")
    
    # 1. The Edit Section
    st.subheader("1. Edit Data")
    updated_df = st.data_editor(st.session_state.ledger_data, num_rows="dynamic", use_container_width=True)
    if st.button("Save Edits"):
        st.session_state.ledger_data = updated_df
        st.success("Changes saved!")

    st.divider()

    # 2. The Delete Section
    st.subheader("2. Delete Specific Entry")
    col_del1, col_del2 = st.columns([3, 1])
    
    # Create a list of Tracking IDs for the dropdown
    ids = st.session_state.ledger_data['Tracking_ID'].tolist()
    to_delete = col_del1.selectbox("Select Tracking ID to delete:", ["None"] + ids)
    
    if col_del2.button("🗑️ Delete Now"):
        if to_delete != "None":
            st.session_state.ledger_data = st.session_state.ledger_data[st.session_state.ledger_data.Tracking_ID != to_delete]
            st.warning(f"Record {to_delete} has been deleted.")
            st.rerun() # Refresh page to update list
        else:
            st.error("Please select a valid ID.")

    st.divider()
    # Excel Download
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
        count = col.number_input(f"₹ {n}", min_value=0, key=f"n_{n}")
        total += (n * count)
    st.markdown(f"<div style='background-color:#ff7e00; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>Total: ₹ {total:,.2f}</h2></div>", unsafe_allow_html=True)
