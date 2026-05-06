import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_option_menu import option_menu

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. CSS 'Magic' - डिज़ाइन और कलर्स
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
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(255,126,0,0.4); }

    input { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. डेटा स्टोरेज (Session State)
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=[
        "ID", "Date", "Type", "Particulars", "Recipient", "Approved_By", "Medium", "Amount_INR"
    ])

# --- साइडबार नेविगेशन ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #ff7e00;'>ORANGE HOUSE</h2>", unsafe_allow_html=True)
    st.divider()
    
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Dashboard", "Add Receipt", "Add Payment", "Manage Reports", "Cash Counter"],
        icons=["speedometer2", "plus-circle", "dash-circle", "journal-text", "coin"], 
        menu_icon="menu-button-wide", 
        default_index=0,
        styles={
            "container": {"background-color": "#161b22", "padding": "5px"},
            "icon": {"color": "#ff7e00", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px", "color": "white"},
            "nav-link-selected": {"background-color": "#ff7e00", "color": "black", "font-weight": "bold"},
        }
    )

# --- पेज लॉजिक ---

if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    
    if not df.empty:
        df_dash = df.copy()
        df_dash['Amount_INR'] = pd.to_numeric(df_dash['Amount_INR'], errors='coerce').fillna(0)
        
        t_in = df_dash[df_dash['Type'] == 'Receipt']['Amount_INR'].sum()
        t_out = df_dash[df_dash['Type'] == 'Payment']['Amount_INR'].sum()
        net_bal = t_in - t_out
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow (जमा)", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow (खर्च)", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance (बचत)", f"₹ {net_bal:,.2f}")
        
        st.subheader("Recent Activity")
        st.dataframe(df_dash.sort_values("ID", ascending=False), use_container_width=True)
    else:
        st.info("स्वागत है! कृपया अपना हिसाब-किताब शुरू करने के लिए एंट्री करें।")

elif selected == "Add Receipt":
    st.title("📥 पैसा आया (Receipt Entry)")
    with st.form("r_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dt = st.date_input("Transaction Date", datetime.now())
            pt = st.text_input("विवरण (Description)")
        with col2:
            am = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            md = st.selectbox("Medium", ["Cash", "UPI", "Online Bank", "Check"])
        
        submit = st.form_submit_button("Save Receipt ✅")
        if submit:
            if pt:
                new_id = len(st.session_state.ledger_data) + 1
                new_row = pd.DataFrame([[new_id, str(dt), "Receipt", pt, "N/A", "Self", md, am]],
