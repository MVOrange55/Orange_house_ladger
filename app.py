import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_option_menu import option_menu

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. CSS 'Magic' 
# यहाँ 'unsafe_allow_html=True' सही पैरामीटर है
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
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(255,126,0,0.4); }
    input { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. डेटा स्टोरेज
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=[
        "ID", "Date", "Type", "Particulars", "Recipient", "Approved_By", "Medium", "Amount_INR"
    ])

# --- साइडबार नेविगेशन ---
with st.sidebar:
    # यहाँ लोगो एरर को हैंडल किया गया है
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
        df_dash['Amount_INR'] = pd.to_numeric(df_dash['Amount_INR'])
        t_in = df_dash[df_dash['Type'] == 'Receipt']['Amount_INR'].sum()
        t_out = df_dash[df_dash['Type'] == 'Payment']['Amount_INR'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow (जमा)", f"₹ {t
