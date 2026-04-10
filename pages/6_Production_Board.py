import streamlit as st
import sys
from pathlib import Path
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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 06 - cm³/m² Primary Input</div>", unsafe_allow_html=True)

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

def display_advanced_order_card(order, current_tab):
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']}", expanded=(current_tab == "in_prod")):
        
        # 1. Basic Info
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Product:** {order.get('product_type')}")
        col2.write(f"**Material:** {order.get('material_type')} ({order.get('thickness_micron')}µ)")
        col3.write(f"**Size:** {order.get('label_width_mm')} x {order.get('repeat_length_mm')} mm")
        col4.write(f"**QTY:** {order.get('required_quantity'):,} PCS")
            
        st.markdown("---")
        
        # 2. Advanced Technical Setup (Print Units)
        st.markdown("#### ⚙️ Technical Job Ticket (Unit Configuration)")
        st.info("Set up each printing unit. Calculations for LPI and BCM are handled automatically.")
        
        # Example: Unit 1 Configuration
        with st.container(border=True):
            st.markdown("##### Unit 1")
            u1_c1, u1_c2, u1_c3 = st.columns(3)
            
            with u1_c1:
                st.markdown("**🎨 Ink & Color**")
                color_name = st.text_input("Color Name / Code", value="White", key=f"u1_color_{order['id']}")
                coverage = st.number_input("Ink Coverage (%)", value=80.01, key=f"u1_cov_{order['id']}")
                viscosity = st.selectbox("Viscosity Cup", ["Ford #4", "DIN 4", "Zahn 2"], key=f"u1_visc_{order['id']}")
                lab_values = st.text_input("LAB Values (L,a,b) From Ref", key=f"u1_lab_{order['id']}")
                
            with u1_c2:
                st.markdown("**🧻 Anilox Selection**")
                anilox_selected = st.selectbox("Anilox Brand & No.", ["Select Anilox...", "Apex 1200", "Zecher 800"], key=f"u1_anilox_{order['id']}")
                
                lpc = st.number_input("Anilox LPC", value=100, step=10, key=f"u1_lpc_{order['id']}")
                st.caption(f"🔄 Equivalent: **{lpc * 2.54:.0f} LPI**")
                
                # --- CORRECTED SECTION HERE ---
                cm3_vol = st.number_input("Volume (cm³/m²)", value=4.65, step=0.1, key=f"u1_cm3_{order['id']}")
                st.caption(f"💧 Equivalent: **{cm3_vol / 1.55:.2f} BCM**")
                # ------------------------------
                
            with u1_c3:
                st.markdown("**🛠️ Mounting & Wash**")
                tape_brand = st.selectbox("Tape Brand", ["tesa", "3M", "Lohmann", "Olinxo"], key=f"u1_tape_{order['id']}")
                tape_hard = st.selectbox("Tape Hardness", ["Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"], key=f"u1_hard_{order['id']}")
                
                wash_mode = st.selectbox(
                    "🧼 Cleaning Mode", 
                    ["Evacuation (1L)", "Light Wash (3L)", "Normal Wash (6L)", "Intensive/Deep (12L)"], 
                    index=2, 
                    key=f"u1_wash_{order['id']}"
                )
        
        # Requisition Generation Section
        st.markdown("<br>", unsafe_allow_html=True)
        req_col1, req_col2 = st.columns([1, 1])
        req_col1.success("💡 **Calculations Estimate:** Required Ink: **14.5 Kg** | Solvent: **6 Liters**")
        req_col2.button("📤 Generate Material Requisitions", key=f"req_{order['id']}", use_container_width=True, type="secondary")
            
        st.markdown("---")
        
        # 3. Actions
        action1, action2 = st.columns(2)
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Confirm Setup & Start Production", key=f"start_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                    st.rerun()
            elif current_tab == "in_prod":
                if st.button("✅ Mark as Completed", key=f"comp_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "completed"}).eq("id", order['id']).execute()
                    st.rerun()
        with action2:
            st.button("🖨️ Print Technical Job Ticket", key=f"print_{order['id']}", use_container_width=True)

# --- Populate Tabs ---
with tab1:
    if not pending_orders: st.info("No pending orders.")
    for order in pending_orders: display_advanced_order_card(order, "pending")
with tab2:
    if not in_production_orders: st.info("No orders in production.")
    for order in in_production_orders: display_advanced_order_card(order, "in_prod")
with tab3:
    if not completed_orders: st.info("No completed orders.")
    for order in completed_orders: display_advanced_order_card(order, "completed")
