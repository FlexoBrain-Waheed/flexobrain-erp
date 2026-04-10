import streamlit as st
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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 03 - Full Kanban & Print</div>", unsafe_allow_html=True)

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
# --- PDF Generator for Production Ticket ---
# ==========================================
def create_production_pdf(order):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Production Job Ticket: {order.get('order_number', '')}", ln=True, align='C')
    pdf.ln(5)
    
    def safe_txt(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')
        
    pdf.set_font("Arial", 'B', 10)
    
    # Loop through important dictionary items
    exclude_keys = ['id', 'created_at', 'status']
    for key, value in order.items():
        if key not in exclude_keys and value is not None and value != "":
            clean_key = str(key).replace('_', ' ').title()
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(50, 8, safe_txt(f"{clean_key}:"), border=1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(140, 8, safe_txt(str(value))[:80], border=1, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Signatures:", ln=True)
    pdf.cell(63, 15, "Operator: _____________", border=0)
    pdf.cell(63, 15, "QC: _____________", border=0)
    pdf.cell(63, 15, "Manager: _____________", border=0, ln=True)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI: Production Kanban Board ---
# ==========================================
st.title("🏭 Production Kanban Board")
st.markdown("---")

# --- Fetch ALL Orders from Supabase ---
def fetch_all_orders():
    try:
        response = supabase.table("job_orders").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

all_orders = fetch_all_orders()

# Filter orders by status
pending_orders = [o for o in all_orders if o.get('status') == 'pending']
in_production_orders = [o for o in all_orders if o.get('status') == 'in_production']
completed_orders = [o for o in all_orders if o.get('status') == 'completed']

# --- UI Tabs ---
tab1, tab2, tab3 = st.tabs(["📥 Pending (New)", "⚙️ In Production", "✅ Completed"])

def display_order_card(order, current_tab):
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']} | Due: {order.get('due_date','')}"):
        
        # Overview Columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.caption("Product Type")
            st.write(f"**{order.get('product_type')}**")
        with col2:
            st.caption("Material Spec")
            st.write(f"**{order.get('material_type')} ({order.get('thickness_micron')}µ)**")
        with col3:
            st.caption("Dimensions")
            st.write(f"**W: {order.get('label_width_mm')}mm x L: {order.get('repeat_length_mm')}mm**")
        with col4:
            st.caption("Required QTY")
            st.write(f"**{order.get('required_quantity'):,} PCS**")
            
        st.markdown("---")
        
        # Action Buttons
        action1, action2, action3 = st.columns(3)
        
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Start Production", key=f"start_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                    st.rerun()
            elif current_tab == "in_prod":
                if st.button("✅ Mark as Completed", key=f"comp_{order['id']}", type="primary", use_container_width=True):
                    supabase.table("job_orders").update({"status": "completed"}).eq("id", order['id']).execute()
                    st.rerun()
            elif current_tab == "completed":
                if st.button("↩️ Revert to Production", key=f"rev_{order['id']}", use_container_width=True):
                    supabase.table("job_orders").update({"status": "in_production"}).eq("id", order['id']).execute()
                    st.rerun()
                    
        with action2:
            pdf_bytes = create_production_pdf(order)
            st.download_button(
                label="🖨️ Print Job Ticket",
                data=pdf_bytes,
                file_name=f"Production_Ticket_{order['order_number']}.pdf",
                mime="application/pdf",
                key=f"print_{order['id']}",
                use_container_width=True
            )
            
        with action3:
            st.button("🔍 View Full Details", key=f"view_{order['id']}", use_container_width=True, help="Full edit feature coming soon")

# --- Populate Tabs ---
with tab1:
    if not pending_orders:
        st.info("No pending orders at the moment.")
    else:
        for order in pending_orders:
            display_order_card(order, "pending")

with tab2:
    if not in_production_orders:
        st.info("No orders currently in production.")
    else:
        for order in in_production_orders:
            display_order_card(order, "in_prod")

with tab3:
    if not completed_orders:
        st.info("No completed orders yet.")
    else:
        for order in completed_orders:
            display_order_card(order, "completed")
