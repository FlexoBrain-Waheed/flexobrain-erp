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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 05 - FlexoBrain Dynamic Units</div>", unsafe_allow_html=True)

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
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']} | Due: {order.get('due_date','')}", expanded=(current_tab == "in_prod")):
        
        # 1. Overview Columns
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
        
        # 2. TECHNICAL SECTION (Unit Configuration)
        st.markdown("#### 🎨 Technical Job Ticket (Unit Configuration)")
        st.info("Setup each printing unit. Calculations for LPI and BCM are handled automatically.")
        
        # Dynamically generate units based on colors_count
        colors_count = int(order.get('colors_count', 1))
        width_mm = order.get('label_width_mm', 0)
        repeat_mm = order.get('repeat_length_mm', 0)
        
        for i in range(1, colors_count + 1):
            with st.container(border=True):
                st.markdown(f"**⚙️ Unit {i}**")
                
                col_ink, col_anilox, col_mount = st.columns(3)
                
                # --- Ink Section ---
                with col_ink:
                    st.caption("🎨 Ink & Color")
                    st.text_input("Color Name / Code", key=f"color_name_{order['id']}_{i}")
                    
                    # Dynamic coverage label based on width and repeat length
                    coverage_label = f"Ink coverage % (W: {width_mm}mm x L: {repeat_mm}mm)"
                    st.number_input(coverage_label, min_value=0.0, max_value=100.0, value=20.0, key=f"cov_{order['id']}_{i}")
                    
                    st.selectbox("Viscosity Cup", ["Ford #4", "DIN 4", "Zahn 2", "Other"], key=f"visc_{order['id']}_{i}")
                    st.text_input("LAB Values (L,a,b) From Ref", key=f"lab_{order['id']}_{i}")
                
                # --- Anilox Section ---
                with col_anilox:
                    st.caption("🧻 Anilox Selection")
                    st.selectbox("Anilox Brand & No.", ["Select Anilox...", "Apex", "Sandon", "Cheshire", "Zecher"], key=f"anx_brand_{order['id']}_{i}")
                    
                    lpc = st.number_input("Anilox LPC", min_value=0, value=100, step=10, key=f"lpc_{order['id']}_{i}")
                    st.caption(f"💧 Equivalent: {int(lpc * 2.54)} LPI")
                    
                    vol_cm3 = st.number_input("Volume (cm³/m²)", min_value=0.0, value=4.65, step=0.1, key=f"vol_{order['id']}_{i}")
                    bcm_val = vol_cm3 / 1.55 if vol_cm3 > 0 else 0
                    st.caption(f"💧 Equivalent: {bcm_val:.2f} BCM")
                
                # --- Mounting Section ---
                with col_mount:
                    st.caption("🛠️ Mounting")
                    st.selectbox("Tape Brand", ["tesa", "3M", "Lohmann", "Biessse"], key=f"tape_brand_{order['id']}_{i}")
                    st.selectbox("Tape Hardness", ["Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"], key=f"tape_hard_{order['id']}_{i}")
                    # Note: Cleaning mode removed as requested for the future smart scheduler.

        # Plates & Cliché Actions
        st.markdown("<br>", unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        if order.get("artwork_status") == "NEW":
            col_p1.button("📑 Generate New Cliché Request (PDF)", key=f"cliche_{order['id']}", type="secondary")
        else:
            col_p1.button("📂 Request Cliché from Archive", key=f"archive_{order['id']}", type="secondary")

        st.markdown("---")
        
        # 3. Actions
        action1, action2, action3 = st.columns(3)
        
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Confirm Setup & Start Production", key=f"start_{order['id']}", type="primary", use_container_width=True):
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
