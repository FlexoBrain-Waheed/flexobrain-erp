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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 04 - Technical UI Draft</div>", unsafe_allow_html=True)

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

# --- Technical DataFrame Template ---
def get_empty_tech_df():
    return pd.DataFrame({
        "Color Name": ["Pantone 485 C", "", "", "", "", ""], # Example row
        "Ink Code": ["", "", "", "", "", ""],
        "Ink Mfg": ["", "", "", "", "", ""],
        "Viscosity (sec)": ["", "", "", "", "", ""],
        "LAB Values": ["", "", "", "", "", ""],
        "Std Drawdown": ["", "", "", "", "", ""],
        "Anilox LPI": ["", "", "", "", "", ""],
        "Anilox BCM": ["", "", "", "", "", ""],
        "Anilox cm³/m²": ["", "", "", "", "", ""], # 1 BCM = 1.55 cm3
        "Anilox No.": ["", "", "", "", "", ""],
        "Anilox Brand": ["", "", "", "", "", ""],
        "Tape Brand": ["", "", "", "", "", ""],
        "Tape Color": ["", "", "", "", "", ""],
        "Tape Hardness": ["Medium", "Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"]
    })

def display_order_card(order, current_tab):
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']}", expanded=(current_tab == "in_prod")):
        
        # 1. Basic Info
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Product:** {order.get('product_type')}")
        col2.write(f"**Material:** {order.get('material_type')} ({order.get('thickness_micron')}µ)")
        col3.write(f"**Size:** {order.get('label_width_mm')} x {order.get('repeat_length_mm')} mm")
        col4.write(f"**QTY:** {order.get('required_quantity'):,} PCS")
            
        st.markdown("---")
        
        # 2. THE NEW TECHNICAL SECTION (UI ONLY)
        st.markdown("#### 🎨 Technical Job Ticket (Engineering & Setup)")
        st.info("💡 **Draft Mode:** Fill the table below. (1 BCM/in² = 1.55 cm³/m²). *Data saving to Supabase will be added in the next step.*")
        
        # Interactive Data Editor
        edited_df = st.data_editor(
            get_empty_tech_df(),
            num_rows="dynamic",
            use_container_width=True,
            key=f"tech_editor_{order['id']}",
            column_config={
                "Tape Hardness": st.column_config.SelectboxColumn(
                    "Tape Hardness",
                    help="Select the mounting tape hardness",
                    options=["Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"],
                    required=True
                ),
                "Anilox BCM": st.column_config.NumberColumn("Anilox BCM", format="%.2f"),
                "Viscosity (sec)": st.column_config.NumberColumn("Viscosity (sec)"),
            }
        )
        
        # Plates & Cliché Actions
        st.markdown("<br>", unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        if order.get("artwork_status") == "NEW":
            col_p1.button("📑 Generate New Cliché Request (PDF)", key=f"cliche_{order['id']}", type="secondary")
        else:
            col_p1.button("📂 Request Cliché from Archive", key=f"archive_{order['id']}", type="secondary")
            
        st.markdown("---")
        
        # 3. Actions
        action1, action2 = st.columns(2)
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Confirm Setup & Start Production", key=f"start_{order['id']}", type="primary"):
                    supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                    st.rerun()
            elif current_tab == "in_prod":
                if st.button("✅ Mark as Completed", key=f"comp_{order['id']}", type="primary"):
                    supabase.table("job_orders").update({"status": "completed"}).eq("id", order['id']).execute()
                    st.rerun()
        with action2:
            st.button("🖨️ Print Full Technical Job Ticket", key=f"print_{order['id']}")

# --- Populate Tabs ---
with tab1:
    for order in pending_orders: display_order_card(order, "pending")
with tab2:
    for order in in_production_orders: display_order_card(order, "in_prod")
with tab3:
    for order in completed_orders: display_order_card(order, "completed")
