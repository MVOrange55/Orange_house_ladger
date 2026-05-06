import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_option_menu import option_menu

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. CSS 'Magic'
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #ff7e00 !important; font-size: 32px; font-weight: bold; }
    [data-testid="stMetric"] {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #ff7e00;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #ff7e00, #ff9e00);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        width: 100%;
    }
    input { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. डेटा स्टोरेज
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=[
        "ID", "Date", "Type", "Particulars", "Recipient", "Approved_By", "Medium", "Amount_INR"
    ])

# Side Navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ff7e00;'>ORANGE HOUSE</h2>", unsafe_allow_html=True)
    st.divider()
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Dashboard", "Add Receipt", "Add Payment", "Manage Reports", "Cash Counter"],
        icons=["speedometer2", "plus-circle", "dash-circle", "journal-text", "coin"], 
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#ff7e00", "color": "black"},
        }
    )

# --- Logic ---
if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    if not df.empty:
        df_dash = df.copy()
        df_dash['Amount_INR'] = pd.to_numeric(df_dash['Amount_INR'], errors='coerce').fillna(0)
        t_in = df_dash[df_dash['Type'] == 'Receipt']['Amount_INR'].sum()
        t_out = df_dash[df_dash['Type'] == 'Payment']['Amount_INR'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance", f"₹ {t_in - t_out:,.2f}")
        st.dataframe(df_dash.sort_values("ID", ascending=False), use_container_width=True)
    else:
        st.info("कोई डेटा उपलब्ध नहीं है।")

elif selected == "Add Receipt":
    st.title("📥 Receipt Entry")
    with st.form("r_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        pt = col1.text_input("Particulars")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        md = col2.selectbox("Medium", ["Cash", "UPI", "Bank"])
        
        if st.form_submit_button("Save Receipt"):
            new_id = len(st.session_state.ledger_data) + 1
            # यहाँ एरर फिक्स किया गया है (ब्रैकेट बंद किया गया है)
            data_list = [[new_id, str(dt), "Receipt", pt, "N/A", "Self", md, am]]
            new_row = pd.DataFrame(data_list, columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success("जमा दर्ज हो गया!")

elif selected == "Add Payment":
    st.title("📤 Payment Entry")
    with st.form("p_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("Date", datetime.now())
        pt = col1.text_input("Description")
        rc = col1.text_input("Recipient")
        am = col2.number_input("Amount (₹)", min_value=0.0)
        ap = col2.text_input("Approved By")
        md = col2.selectbox("Medium", ["Cash", "UPI", "Bank"])
        
        if st.form_submit_button("Save Payment"):
            new_id = len(st.session_state.ledger_data) + 1
            data_list = [[new_id, str(dt), "Payment", pt, rc, ap, md, am]]
            new_row = pd.DataFrame(data_list, columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success("भुगतान दर्ज हो गया!")

elif selected == "Manage Reports":
    st.title("📝 Reports")
    updated_df = st.data_editor(st.session_state.ledger_data, num_rows="dynamic", use_container_width=True)
    if st.button("Update Database"):
        st.session_state.ledger_data = updated_df
        st.success("डेटा अपडेट हो गया!")
    
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state.ledger_data.to_excel(writer, index=False)
    st.download_button("📥 Download Excel", buf.getvalue(), "OrangeHouse_Report.xlsx")

elif selected == "Cash Counter":
    st.title("💰 Cash Counter")
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    total = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        col = c1 if i % 2 == 0 else c2
        count = col.number_input(f"₹ {n}", min_value=0, key=f"n_{n}")
        total += (n * count)
    st.subheader(f"Total Cash: ₹ {total:,.2f}")
