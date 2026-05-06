import streamlit as st
import pandas as pd
from datetime import datetime
import io
from streamlit_option_menu import option_menu

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. CSS 'Magic' - डिज़ाइन सुधार
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
        # डेटा को कैलकुलेशन के लिए तैयार करना
        df_dash = df.copy()
        df_dash['Amount_INR'] = pd.to_numeric(df_dash['Amount_INR'], errors='coerce').fillna(0)
        
        t_in = df_dash[df_dash['Type'] == 'Receipt']['Amount_INR'].sum()
        t_out = df_dash[df_dash['Type'] == 'Payment']['Amount_INR'].sum()
        net_bal = t_in - t_out
        
        # यहाँ वह फिक्स्ड लाइनें हैं जिनमें एरर था
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
            am = st.number_input("Amount (₹)", min_value=0.0)
            md = st.selectbox("Medium", ["Cash", "UPI", "Online Bank", "Check"])
        
        if st.form_submit_button("Save Receipt ✅"):
            new_id = len(st.session_state.ledger_data) + 1
            new_row = pd.DataFrame([[new_id, str(dt), "Receipt", pt, "N/A", "Self", md, am]], 
                                   columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"₹ {am} जमा कर लिए गए!")

elif selected == "Add Payment":
    st.title("📤 पैसा गया (Payment Entry)")
    with st.form("p_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dt = st.date_input("Transaction Date", datetime.now())
            pt = st.text_input("खर्च का विवरण")
            rc = st.text_input("किसको दिया (Recipient)")
        with col2:
            am = st.number_input("Amount (₹)", min_value=0.0)
            ap = st.text_input("Approved By (किसने पास किया)")
            md = st.selectbox("Medium", ["Cash", "UPI", "Bank"])
        
        if st.form_submit_button("Save Payment 📤"):
            new_id = len(st.session_state.ledger_data) + 1
            new_row = pd.DataFrame([[new_id, str(dt), "Payment", pt, rc, ap, md, am]], 
                                   columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"₹ {am} का भुगतान दर्ज हो गया!")

elif selected == "Manage Reports":
    st.title("📝 मास्टर रिपोर्ट और सुधार केंद्र")
    df = st.session_state.ledger_data
    
    search_q = st.text_input("🔍 यहाँ नाम या विवरण लिखकर गलती ढूँढें...")
    if search_q:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
    
    st.write("सुधारने के लिए किसी भी बॉक्स पर डबल-क्लिक करें:")
    updated_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Permanently Update Data"):
        st.session_state.ledger_data = updated_df
        st.success("डेटाबेस अपडेट हो गया!")
    
    st.divider()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state.ledger_data.to_excel(writer, index=False)
    st.download_button("📥 Download Master Excel Report", buf.getvalue(), "OrangeHouse_Final_Report.xlsx")

elif selected == "Cash Counter":
    st.title("💰 नोटों की गिनती (Cash Denomination)")
    notes = [500, 200, 100, 50, 20, 10, 5]
    total_val = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        with c1 if i < 4 else c2:
            count = st.number_input(f"₹ {n} के कितने नोट हैं?", min_value=0, key=f"note_{n}")
            total_val += (n * count)
    
    st.markdown(f"""
        <div style="background-color: #ff7e00; color: black; padding: 25px; border-radius: 15px; text-align: center; margin-top: 20px;">
            <h2 style="margin:0;">कुल कैश राशि</h2>
            <h1 style="margin:0;">₹ {total_val:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
