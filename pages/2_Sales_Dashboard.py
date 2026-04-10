import streamlit as st
import sys
from pathlib import Path
from supabase import create_client, Client

# --- Page configuration ---
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth
auth.require_role(["sales", "admin"])
auth.logout_button()

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
# --- Main UI: Sales Dashboard ---
# ==========================================
st.title("📊 FlexoBrain Sales Dashboard")
st.markdown("Track your clients' orders and process repeat jobs instantly.")
st.markdown("---")

def fetch_orders():
    try:
        response = supabase.table("job_orders").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

orders = fetch_orders()

if not orders:
    st.info("No orders found in the system yet.")
    st.stop()

# --- KPIs ---
total_orders = len(orders)
pending_count = len([o for o in orders if o.get('status') == 'pending'])
in_prod_count = len([o for o in orders if o.get('status') == 'in_production'])
completed_count = len([o for o in orders if o.get('status') == 'completed'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", total_orders)
col2.metric("🟡 Pending (New)", pending_count)
col3.metric("🔵 In Production", in_prod_count)
col4.metric("🟢 Ready / Completed", completed_count)

st.markdown("---")
st.subheader("📋 Order Live Tracking")

for order in orders:
    status = order.get('status', 'pending')
    if status == 'pending':
        status_ui = "🟡 Pending"
    elif status == 'in_production':
        status_ui = "🔵 In Production"
    elif status == 'completed':
        status_ui = "🟢 Completed"
    else:
        status_ui = f"⚪ {status}"

    with st.expander(f"📦 Order: {order.get('order_number', 'N/A')} | Client: {order.get('customer_name', 'Unknown')} | Status: {status_ui}"):
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Product:** {order.get('product_type')}")
        c2.write(f"**Material:** {order.get('material_type')} ({order.get('thickness_micron')}µ)")
        c3.write(f"**Size:** {order.get('label_width_mm')} x {order.get('repeat_length_mm')} mm")
        c4.write(f"**QTY:** {order.get('required_quantity'):,} PCS")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        action_col, _ = st.columns([1, 4])
        with action_col:
            if st.button("🔁 Repeat Order", key=f"repeat_{order['id']}", type="primary", use_container_width=True):
                st.session_state['repeat_data'] = order
                st.success("✅ Order data copied! Please navigate to the 'Create Order' page to submit this Repeat Job.")
