import streamlit as st
import time

# --- 1. Kiosk Mode Configuration ---
# Setting layout to wide and hiding sidebar for a full-screen app feel
st.set_page_config(page_title="Shop Floor Control", page_icon="🏭", layout="wide", initial_sidebar_state="collapsed")

# --- 2. Custom CSS for Factory UI ---
# Making everything MASSIVE so workers can tap easily with gloves or dirty hands
st.markdown("""
    <style>
    .kiosk-title { font-size: 3rem; font-weight: bold; text-align: center; color: #1E3A8A; margin-bottom: 20px;}
    .big-info { font-size: 1.8rem; font-weight: bold; color: #333; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 10px;}
    .stTextInput input { font-size: 2.5rem !important; text-align: center; height: 80px;}
    .stButton button { height: 120px; font-size: 2.5rem; font-weight: bold; border-radius: 15px; border: 3px solid #000; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='kiosk-title'>🏭 FlexoBrain - Shop Floor Control</div>", unsafe_allow_html=True)

# --- 3. The Universal Scanner Input ---
st.info("💡 Instructions: Use the Bluetooth Scanner Gun to scan the QR on the Job Order, or type it manually.")
scanned_code = st.text_input("", placeholder="[ SCAN QR CODE HERE ]")

# --- 4. The State Machine & UI Logic ---
if scanned_code:
    # --- Mockup Job Details (Later this will fetch from Supabase) ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='big-info'>📦 Job No: {scanned_code}</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-info'>👤 Client: Mockup Customer Ltd.</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='big-info'>🎨 Spec: BOPP White | 38u | 6 Colors</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-info'>📏 Target QTY: 50,000 PCS</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Manage the machine state using Session State
    if 'machine_status' not in st.session_state:
        st.session_state['machine_status'] = 'idle'
    
    status = st.session_state['machine_status']

    # State 1: IDLE (Ready to start)
    if status == 'idle':
        if st.button("▶️ START MACHINE", type="primary", use_container_width=True):
            st.session_state['machine_status'] = 'running'
            st.rerun()

    # State 2: RUNNING (Currently Printing)
    elif status == 'running':
        st.success("🟢 MACHINE IS RUNNING... TIMER STARTED", icon="⏳")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⏸️ PAUSE (ISSUE)", use_container_width=True):
                st.session_state['machine_status'] = 'paused'
                st.rerun()
        with col_btn2:
            if st.button("⏹️ FINISH JOB", use_container_width=True):
                st.session_state['machine_status'] = 'finished'
                st.rerun()

    # State 3: PAUSED (Problem on the floor)
    elif status == 'paused':
        st.error("🔴 MACHINE PAUSED! TIMER STOPPED", icon="🛑")
        reason = st.selectbox("Select Reason for Downtime:", ["Technical / Mechanic Issue", "Waiting for Plates/Ink", "Web Break / Cleaning", "Lunch Break"])
        if st.button("▶️ RESUME JOB", type="primary", use_container_width=True):
            # Later: Save the 'reason' and 'duration' to DB
            st.session_state['machine_status'] = 'running'
            st.rerun()

    # State 4: FINISHED (Data Entry before closing)
    elif status == 'finished':
        st.warning("⚠️ JOB FINISHED. PLEASE ENTER FINAL DATA.", icon="📝")
        waste_kg = st.number_input("Enter Total Waste (KG):", min_value=0.0, step=1.0)
        
        if st.button("💾 SAVE & CLOSE JOB", type="primary", use_container_width=True):
            # Later: Update Supabase with finish time and waste
            st.session_state['machine_status'] = 'idle'
            st.balloons()
            st.toast("Job Saved to Cloud Successfully!", icon="☁️")
            # Clear input by re-running
            st.rerun()
