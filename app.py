import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. Page Configuration
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. Force Professional Light Mode
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    [data-testid="stMetric"] {
        background-color: #f1f3f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff7e00;
    }
    .stButton>button {
        background-color: #ff7e00;
        color: white !important;
        font-weight: bold;
    }
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Strict Column Definition
FINAL_COLS = ["Tracking_ID", "Date", "Type", "Particulars", "Emp_ID", "Recipient", "Approved_By", "Medium", "Amount"]

# Initialize and Safety Check: This part fixes 'KeyError' automatically
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=FINAL_COLS)
else:
    # If old data exists with missing columns, add them automatically
    for col in FINAL_COLS:
        if col not in st.session_state.ledger_data.columns:
            st.session_state.ledger_data[col] = "N/A"

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
        styles={"nav-link-selected": {"background-color": "#ff7e00", "color": "white"}}
    )

# --- DASHBOARD ---
if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    
    if not df.empty:
        # Safety: Ensure Amount is numeric before calculation
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        t_in = df[df['Type'] == 'Receipt']['Amount'].sum()
        t_out = df[df['Type'] == 'Payment']['Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance", f"₹ {t_in - t_out:,.2f}")
        
        st.subheader("Transaction History")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records found. Please start by adding a transaction.")

# --- ADD RECEIPT ---
elif selected == "Add Receipt":
    st.title("📥 Add Receipt")
    with st.form("receipt_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        p = col1.text_input("Particulars")
        e = col2.text_input("Employee ID", value="ADMIN")
        a = col2.number_input("Amount (₹)", min_value=0.0)
        m = st.selectbox("Medium", ["Cash", "Bank", "UPI"])
        
        if st.form_submit_button("Save Receipt"):
            tid = get_new_tid()
            new_data = [tid, str(d), "Receipt", p, e, "Company", "Self", m, a]
            new_row = pd.DataFrame([new_data], columns=FINAL_COLS)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"Receipt Saved! ID: {tid}")

# --- ADD PAYMENT ---
elif selected == "Add Payment":
    st.title("📤 Add Payment")
    with st.form("pay_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        e = col1.text_input("Employee ID")
        r = col1.text_input("Paid To")
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
                st.success(f"Payment Recorded! ID: {tid}")
            else:
                st.error("Missing required fields.")

# --- MANAGE REPORTS ---
elif selected == "Manage Reports":
    st.title("📝 Edit & Delete Records")
    
    # Editable Table
    st.subheader("1. View/Edit Database")
    edited_df = st.data_editor(st.session_state.ledger_data, use_container_width=True, num_rows="dynamic")
    if st.button("Save All Changes"):
        st.session_state.ledger_data = edited_df
        st.success("Database successfully updated!")
    
    st.divider()
    
    # Specific Delete Section
    st.subheader("2. Delete Specific Entry")
    if not st.session_state.ledger_data.empty:
        # Check if column exists before listing to avoid KeyError
        if 'Tracking_ID' in st.session_state.ledger_data.columns:
            id_list = st.session_state.ledger_data['Tracking_ID'].tolist()
            to_del = st.selectbox("Select ID to delete:", ["None"] + id_list)
            if st.button("Confirm Delete"):
                if to_del != "None":
                    st.session_state.ledger_data = st.session_state.ledger_data[st.session_state.ledger_data.Tracking_ID != to_del]
                    st.warning(f"Record {to_del} deleted.")
                    st.rerun()
    else:
        st.write("No data available to delete.")

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
        cnt = col.number_input(f"₹ {n} Notes", min_value=0, key=f"note_{n}")
        total += (n * cnt)
    st.markdown(f"<div style='background-color:#ff7e00; padding:20px; border-radius:10px; color:white; text-align:center;'><h2>Total: ₹ {total:,.2f}</h2></div>", unsafe_allow_html=True)
