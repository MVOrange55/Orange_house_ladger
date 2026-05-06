import streamlit as st
import pandas as pd
from datetime import datetime
import io
import random
from streamlit_option_menu import option_menu

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="Orange House Pvt Ltd", layout="wide", page_icon="🟠")

# 2. CSS 'Magic' - Visibility और Premium Look के लिए
st.markdown("""
    <style>
    /* मुख्य बैकग्राउंड */
    .main { background-color: #0d1117; color: #ffffff; }
    
    /* Metrics डिजाइन - ब्लैक बैकग्राउंड पर वाइट टेक्स्ट फिक्स */
    [data-testid="stMetric"] {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
        border-bottom: 4px solid #ff7e00;
    }
    /* Metric Label (ऊपर का छोटा टेक्स्ट) */
    [data-testid="stMetricLabel"] p {
        color: #8b949e !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    /* Metric Value (बड़ा नंबर/रुपये) */
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-size: 30px !important;
    }

    /* बटन डिजाइन */
    .stButton>button {
        background: linear-gradient(90deg, #ff7e00, #ff9e00);
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(255,126,0,0.4); }

    /* डेटा एडिटर (Table) के अंदर का टेक्स्ट साफ़ दिखने के लिए */
    .stDataEditor div { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. डेटा स्टोरेज
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=[
        "Tracking_ID", "Date", "Type", "Particulars", "Emp_ID", "Recipient", "Approved_By", "Medium", "Amount"
    ])

# यूनिक ट्रैकिंग नंबर जेनरेटर
def generate_tracking_id():
    return f"OHL-{random.randint(1000, 9999)}"

# साइडबार नेविगेशन
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
            "nav-link-selected": {"background-color": "#ff7e00", "color": "black", "font-weight": "bold"},
        }
    )

# --- पेज लॉजिक ---

if selected == "Dashboard":
    st.title("📊 Financial Summary")
    df = st.session_state.ledger_data
    
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        t_in = df[df['Type'] == 'Receipt']['Amount'].sum()
        t_out = df[df['Type'] == 'Payment']['Amount'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Inflow (जमा)", f"₹ {t_in:,.2f}")
        c2.metric("Total Outflow (खर्च)", f"₹ {t_out:,.2f}")
        c3.metric("Net Balance (बचत)", f"₹ {t_in - t_out:,.2f}")
        
        st.subheader("Recent Transactions")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("स्वागत है! कृपया हिसाब शुरू करने के लिए एंट्री करें।")

elif selected == "Add Receipt":
    st.title("📥 पैसा आया (Receipt)")
    with st.form("r_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("तारीख (Date)", datetime.now())
        pt = col1.text_input("विवरण (Particulars)")
        eid = col2.text_input("Employee ID", value="ADMIN")
        am = col2.number_input("राशि (Amount ₹)", min_value=0.0)
        md = st.selectbox("Medium", ["Bank Transfer", "Cash", "UPI", "Cheque"])
        
        if st.form_submit_button("Save Receipt ✅"):
            tid = generate_tracking_id()
            new_row = pd.DataFrame([[tid, str(dt), "Receipt", pt, eid, "Company", "Self", md, am]], 
                                   columns=st.session_state.ledger_data.columns)
            st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
            st.success(f"एंट्री सेव हो गई! Tracking ID: {tid}")

elif selected == "Add Payment":
    st.title("📤 पैसा गया (Payment)")
    with st.form("p_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        dt = col1.date_input("तारीख (Date)", datetime.now())
        eid = col1.text_input("Employee ID (देने वाला)", placeholder="EMP-101")
        rc = col1.text_input("Recipient (पाने वाला)")
        pt = col2.text_input("खर्च का कारण (Purpose)")
        am = col2.number_input("राशि (Amount ₹)", min_value=0.0)
        ap = col2.text_input("Approved By")
        md = st.selectbox("Medium", ["Cash", "Bank Transfer", "UPI"])
        
        if st.form_submit_button("Save Payment 📤"):
            if eid and rc:
                tid = generate_tracking_id()
                new_row = pd.DataFrame([[tid, str(dt), "Payment", pt, eid, rc, ap, md, am]], 
                                       columns=st.session_state.ledger_data.columns)
                st.session_state.ledger_data = pd.concat([st.session_state.ledger_data, new_row], ignore_index=True)
                st.success(f"भुगतान दर्ज! Tracking ID: {tid}")
            else:
                st.error("कृपया Employee ID और Recipient का नाम भरें!")

elif selected == "Manage Reports":
    st.title("📝 Edit & Manage Reports")
    st.markdown("किसी भी एंट्री को बदलने के लिए उस पर **Double Click** करें और फिर नीचे बटन दबाएँ।")
    
    # एडिटेबल टेबल
    updated_df = st.data_editor(st.session_state.ledger_data, num_rows="dynamic", use_container_width=True)
    
    if st.button("Save Changes (डेटा अपडेट करें)"):
        st.session_state.ledger_data = updated_df
        st.success("डेटाबेस सफलतापूर्वक अपडेट हो गया!")
    
    st.divider()
    # Excel एक्सपोर्ट
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        st.session_state.ledger_data.to_excel(writer, index=False)
    st.download_button("📥 Download Master Report (Excel)", buf.getvalue(), "OrangeHouse_Report.xlsx")

elif selected == "Cash Counter":
    st.title("💰 नोटों की गिनती")
    notes = [500, 200, 100, 50, 20, 10, 5, 2, 1]
    total = 0
    c1, c2 = st.columns(2)
    for i, n in enumerate(notes):
        col = c1 if i % 2 == 0 else c2
        count = col.number_input(f"₹ {n} के नोट", min_value=0, key=f"note_{n}")
        total += (n * count)
    
    st.markdown(f"""
        <div style="background-color: #ff7e00; color: black; padding: 20px; border-radius: 15px; text-align: center; margin-top: 10px;">
            <h2 style="margin:0;">कुल नकद (Total Cash)</h2>
            <h1 style="margin:0;">₹ {total:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
