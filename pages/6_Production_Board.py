import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from fpdf import FPDF
from supabase import create_client, Client

# --- Page configuration ---
st.set_page_config(page_title="Production Board", page_icon="🏭", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth
auth.require_role(["production", "admin"])
auth.logout_button()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 05 - Print Units Architecture</div>", unsafe_allow_html=True)

# ==========================================
# --- Supabase Database Connection ---
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("⚠️ Database connection failed.")
    st.stop()

# ==========================================
# --- Main UI: Production Kanban Board ---
# ==========================================
st.title("🏭 Production Kanban Board")
st.markdown("---")

def fetch_all_orders():
    try:
        response = supabase.table("job_orders").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        return []

all_orders = fetch_all_orders()

pending_orders = [o for o in all_orders if o.get('status') == 'pending']
in_production_orders = [o for o in all_orders if o.get('status') == 'in_production']
completed_orders = [o for o in all_orders if o.get('status') == 'completed']

tab1, tab2, tab3 = st.tabs(["📥 Pending (New)", "⚙️ In Production", "✅ Completed"])

# --- NEW: Print Units Architecture ---
def display_order_card(order, current_tab):
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']}", expanded=(current_tab == "in_prod")):
        
        # 1. Basic Info
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Product:** {order.get('product_type')}")
        col2.write(f"**Material:** {order.get('material_type')} ({order.get('thickness_micron')}µ)")
        col3.write(f"**Size:** {order.get('label_width_mm')} x {order.get('repeat_length_mm')} mm")
        colors_count = int(order.get('colors_count', 6) or 6) # Default to 6 if empty
        col4.write(f"**Colors:** {colors_count}")
            
        st.markdown("---")
        
        # 2. TECHNICAL JOB TICKET (Print Units Dashboard)
        st.markdown(f"#### ⚙️ Technical Job Ticket ({colors_count} Print Units)")
        st.info("💡 **Draft Mode:** UI/UX Test. Data saving to cloud will be activated next.")
        
        # Create Tabs for each Print Unit
        unit_tabs = st.tabs([f"🎨 Unit {i+1}" for i in range(colors_count)])
        
        for i, tab in enumerate(unit_tabs):
            with tab:
                st.markdown(f"**⚙️ Settings for Print Unit {i+1}**")
                col_ink, col_anilox, col_plate = st.columns(3)
                
                with col_ink:
                    st.markdown("**🎨 1. Ink Setup**")
                    st.text_input("Color Name (e.g., Pantone 485 C)", key=f"color_{order['id']}_{i}")
                    st.text_input("Ink Code & Mfg", key=f"ink_mfg_{order['id']}_{i}")
                    st.selectbox("Viscosity Cup", ["Ford #4", "DIN 4", "Zahn 2", "Other"], key=f"visc_cup_{order['id']}_{i}")
                    st.number_input("Viscosity (sec)", min_value=0, key=f"visc_sec_{order['id']}_{i}")
                    st.text_input("LAB Values (L,a,b)", key=f"lab_{order['id']}_{i}")
                    
                with col_anilox:
                    st.markdown("**🧻 2. Anilox Setup**")
                    st.text_input("Anilox No. & Brand", key=f"anx_no_{order['id']}_{i}")
                    st.number_input("LPI", min_value=0, step=50, key=f"anx_lpi_{order['id']}_{i}")
                    
                    # Smart cm3 -> BCM Calculator
                    cm3_val = st.number_input("Volume (cm³/m²)", min_value=0.0, step=0.1, key=f"anx_cm3_{order['id']}_{i}")
                    bcm_val = round(cm3_val / 1.55, 2) if cm3_val > 0 else 0.0
                    if cm3_val > 0:
                        st.success(f"🔄 Equivalent: **{bcm_val} BCM**")
                        
                with col_plate:
                    st.markdown("**🛠️ 3. Plate & Tape**")
                    st.selectbox("Plate Thickness", ["1.14 mm", "1.70 mm", "2.54 mm", "2.84 mm", "Other"], key=f"plate_thk_{order['id']}_{i}")
                    st.number_input("Distortion Factor (%)", min_value=0.0, max_value=100.0, value=100.0, step=0.01, key=f"dist_{order['id']}_{i}")
                    st.text_input("Tape Brand", key=f"tape_br_{order['id']}_{i}")
                    st.selectbox("Tape Hardness", ["Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"], key=f"tape_hrd_{order['id']}_{i}")

        # Cliché & Plate Actions
        st.markdown("<br>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
        if order.get("artwork_status") == "NEW":
            col_p1.button("📑 Issue New Cliché Request (PDF)", key=f"cliche_{order['id']}", type="secondary", use_container_width=True)
        else:
            col_p1.button("📂 Pull Cliché from Archive", key=f"archive_{order['id']}", type="secondary", use_container_width=True)
            col_p2.button("🔄 Copy Specs from Last Run", key=f"copy_{order['id']}", use_container_width=True)
            
        st.markdown("---")
        
        # 3. Final Actions
        action1, action2 = st.columns(2)
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Confirm Specs & Move to Production", key=f"start_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                    st.rerun()
            elif current_tab == "in_prod":
                if st.button("✅ Job Completed", key=f"comp_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "completed"}).eq("id", order['id']).execute()
                    st.rerun()
        with action2:
            st.button("🖨️ Print Technical Job Ticket", key=f"print_{order['id']}", use_container_width=True)

# --- Populate Tabs ---
with tab1:
    for order in pending_orders: display_order_card(order, "pending")
with tab2:
    for order in in_production_orders: display_order_card(order, "in_prod")
with tab3:
    for order in completed_orders: display_order_card(order, "completed")
