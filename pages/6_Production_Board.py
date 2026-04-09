import streamlit as st
import pandas as pd
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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 02 - Live Cloud Sync</div>", unsafe_allow_html=True)

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
    st.error("⚠️ Database connection failed. Please check Streamlit Secrets.")
    st.stop()

# ==========================================
# --- Main UI: Production Kanban Board ---
# ==========================================
st.title("🏭 Production Kanban Board")
st.markdown("---")

# --- Fetch Live Data from Supabase ---
def fetch_pending_orders():
    try:
        # Fetch only orders with status 'pending'
        response = supabase.table("job_orders").select("*").eq("status", "pending").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

pending_orders = fetch_pending_orders()

# --- Display Orders ---
st.subheader("📥 Pending Job Orders (From Sales)")

if not pending_orders:
    st.info("🎉 No pending orders at the moment! Great job.")
else:
    for order in pending_orders:
        with st.expander(f"📦 Job Order: {order['order_number']} | Customer: {order['customer_name']} | Due: {order['due_date']}", expanded=True):
            
            # Overview Columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption("Product Type")
                st.write(f"**{order['product_type']}**")
            with col2:
                st.caption("Material Spec")
                st.write(f"**{order['material_type']} ({order['thickness_micron']}µ)**")
            with col3:
                st.caption("Dimensions")
                st.write(f"**W: {order['label_width_mm']}mm x L: {order['repeat_length_mm']}mm**")
            with col4:
                st.caption("Required QTY")
                st.write(f"**{order['required_quantity']:,} PCS**")
                
            st.markdown("---")
            
            # Action Buttons
            action1, action2 = st.columns([1, 4])
            with action1:
                if st.button("⚙️ Start Production", key=f"start_{order['id']}", type="primary", use_container_width=True):
                    try:
                        # Update status in cloud
                        supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                        st.success(f"Order {order['order_number']} moved to Production!")
                        st.rerun()
                    except Exception as e:
                        st.error("Failed to update status.")
            with action2:
                st.button("🔍 Request Material", key=f"mat_{order['id']}", use_container_width=False)
