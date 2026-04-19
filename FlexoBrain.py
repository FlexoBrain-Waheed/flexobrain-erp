import streamlit as st
import auth

# --- Page Configuration ---
st.set_page_config(page_title="FlexoBrain ERP Portal", page_icon="🏭", layout="centered")

# --- Authentication Check ---
# This line is the magic: it relies on the unified security system to prevent conflicts
if not auth.check_password():
    st.stop()

# --- Main Portal UI ---
st.title("🏭 FlexoBrain Executive Hub")
st.markdown("---")

st.info("👋 Welcome to the system. You can navigate via the sidebar, or use the quick links below.")
st.write("") # Breathing space for layout

# --- Quick Links (Updated) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Sales & Orders")
    st.page_link("pages/10_Sales_Dashboard.py", label="Sales Dashboard", icon="📊")
    st.page_link("pages/11_OPP_Label_Order.py", label="OPP Label Form", icon="🏷️")

with col2:
    st.subheader("⚙️ Production & Planning")
    # ✅ Added the newly renamed Printing Press Monitoring page here!
    try:
        st.page_link("pages/20_Smart_Scheduler.py", label="Smart Scheduler", icon="📅")
        st.page_link("pages/24_Printing_Press_Monitoring.py", label="Printing Press Monitoring", icon="🖨️")
        st.page_link("pages/25_Production_Board.py", label="Production Board", icon="🏭")
    except Exception:
        st.caption("⏳ Production modules loading...")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>FlexoBrain ERP System © 2026</div>", unsafe_allow_html=True)
