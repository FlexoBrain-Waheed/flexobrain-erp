import streamlit as st
import datetime

# ==========================================
# 1. Kiosk Mode Configuration
# ==========================================
st.set_page_config(
    page_title="Shop Floor Control", 
    page_icon="🏭", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. Custom CSS for Factory UI (Massive Elements)
# ==========================================
st.markdown("""
    <style>
    .kiosk-title { font-size: 3rem; font-weight: bold; text-align: center; color: #1E3A8A; margin-bottom: 20px;}
    .big-info { font-size: 1.5rem; font-weight: bold; color: #333; padding: 15px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 10px;}
    
    div[data-baseweb="input"] {
        height: 90px !important;
        border-radius: 10px !important;
    }
    .stTextInput input { 
        font-size: 2.2rem !important; 
        text-align: center !important; 
        height: 90px !important; 
        border: 3px solid #1E3A8A !important;
        border-radius: 10px !important;
    }
    
    .stButton button { height: 100px; font-size: 2.2rem; font-weight: bold; border-radius: 15px; border: 3px solid #000; transition: 0.2s;}
    .stButton button:active { transform: scale(0.95); }
    .stSelectbox label { font-size: 1.5rem !important; font-weight: bold; }
    .stNumberInput label { font-size: 1.5rem !important; font-weight: bold; }
    .stTextArea label { font-size: 1.5rem !important; font-weight: bold; }
    .stTextArea textarea { font-size: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='kiosk-title'>🏭 FlexoBrain - Shop Floor Terminal</div>", unsafe_allow_html=True)

# ==========================================
# 3. State Management Initialization
# ==========================================
if 'machine_status' not in st.session_state:
    st.session_state['machine_status'] = 'idle'
if 'downtime_start' not in st.session_state:
    st.session_state['downtime_start'] = None

# ==========================================
# 4. Universal Scanner Input
# ==========================================
st.info("💡 Instructions: Use the Bluetooth Scanner Gun to scan the Job Order QR, or type it manually and press Enter.")
scanned_code = st.text_input("", placeholder="[ 📷 SCAN BARCODE / QR HERE ]", key="barcode_input")

# ==========================================
# 5. Machine Logic & Workflow
# ==========================================
if scanned_code:
    # --- Mockup Data ---
    st.markdown("---")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(f"<div class='big-info'>📦 Job No: <span style='color:green;'>{scanned_code}</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='big-info'>👤 Client: Al-Safi Dairy</div>", unsafe_allow_html=True)
    with col_info2:
        st.markdown("<div class='big-info'>⚙️ Spec: BOPP Transparent | 30µ | 8 Colors</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-info'>📏 Target QTY: 150,000 PCS</div>", unsafe_allow_html=True)
    st.markdown("---")

    status = st.session_state['machine_status']

    if status == 'idle':
        if st.button("▶️ START MACHINE", type="primary", use_container_width=True):
            st.session_state['machine_status'] = 'running'
            st.rerun()

    elif status == 'running':
        st.success("🟢 MACHINE IS RUNNING... (Production Timer Active)", icon="⚙️")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⏸️ PAUSE (ISSUE)", use_container_width=True):
                st.session_state['machine_status'] = 'paused'
                st.session_state['downtime_start'] = datetime.datetime.now()
                st.rerun()
        with col_btn2:
            if st.button("⏹️ FINISH JOB", use_container_width=True):
                st.session_state['machine_status'] = 'finished'
                st.rerun()

    elif status == 'paused':
        st.error("🔴 MACHINE PAUSED! (Downtime Timer Active)", icon="🛑")
        
        # Cascading Menu Dictionary - SPLIT FOR ACCURATE REPORTING
        downtime_reasons = {
            "🛢️ Ink & Print Unit": [
                "Anilox Change",
                "Anilox Deep Cleaning",
                "Doctor Blade Replacement",
                "Ink Viscosity Adjustment",
                "Color Correction"
            ],
            "🎞️ Substrate & Web": [
                "Waiting for Mother Roll",
                "Roll Splicing",
                "Web Break",
                "Tension Issue",
                "Low Corona Treatment"
            ],
            "🔬 Quality & Setup": [
                "Waiting for QC Approval",
                "Registration Setup",
                "Color Alignment Issue",
                "Mounting Cylinder Issue"
            ],
            "⏱️ Admin & Operations": [
                "Shift Handover",
                "Preventive Maintenance",
                "Machine Cleaning",
                "Lunch Break",
                "Rest Break"
            ]
        }
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            category = st.selectbox("1. Select Issue Category:", list(downtime_reasons.keys()))
        with col_r2:
            specific_reason = st.selectbox("2. Select Specific Reason:", downtime_reasons[category])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶️ RESUME PRODUCTION", type="primary", use_container_width=True):
            st.session_state['machine_status'] = 'running'
            st.session_state['downtime_start'] = None
            st.rerun()

    elif status == 'finished':
        st.warning("⚠️ JOB FINISHED. Please enter Final Production Data.", icon="📝")
        
        # Row 1: Rolls Tracking
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            rolls_in = st.number_input("📥 Number of Rolls Fed to Machine:", min_value=0, step=1)
        with col_w2:
            rolls_out = st.number_input("✅ Number of Good Rolls Printed (Out):", min_value=0, step=1)
        
        # Row 2: Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            total_meters = st.number_input("📏 Total Linear Meters Printed (m):", min_value=0.0, step=100.0)
        with col_m2:
            print_speed = st.number_input("⚡ Average Print Speed (m/min):", min_value=0, step=10)
        with col_m3:
            waste_kg = st.number_input("🗑️ Total Waste (KG):", min_value=0.0, step=1.0)
            
        # Row 3: Operator Notes
        operator_notes = st.text_area("📝 Operator Notes (Optional):", placeholder="Any issues with inks, material, or machine?")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SAVE & CLOSE JOB", type="primary", use_container_width=True):
            st.session_state['machine_status'] = 'idle'
            st.balloons()
            st.toast("Job Data Saved to Cloud Successfully!", icon="☁️")
            st.rerun()
