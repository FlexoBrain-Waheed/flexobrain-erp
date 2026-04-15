import streamlit as st
import sys
import json
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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 07 - FlexoBrain Live DB & Requisitions</div>", unsafe_allow_html=True)

# ==========================================
# --- Universal Database Connection ---
# ==========================================
@st.cache_resource
def init_connection():
    try:
        # Fetching the secrets
        raw_url = st.secrets.get("SUPABASE_URL", "")
        raw_key = st.secrets.get("SUPABASE_KEY", "")
        
        # Radical Cleanup: Remove ALL invisible spaces, newlines, and literal quotes
        clean_url = str(raw_url).strip().replace('"', '').replace("'", "").replace("\n", "")
        clean_key = str(raw_key).strip().replace('"', '').replace("'", "").replace("\n", "")
        
        if not clean_url or not clean_key:
            st.error("⚠️ Credentials missing. Check Streamlit Secrets.")
            st.stop()
            
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.stop()

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"⚠️ DB Error: {e}")
    st.stop()
# ==========================================
# --- PDF Generators ---
# ==========================================
def create_production_pdf(order):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"FlexoBrain Production Ticket: {order.get('order_number', '')}", ln=True, align='C')
    pdf.ln(5)
    
    def safe_txt(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')
        
    exclude_keys = ['id', 'created_at', 'status', 'technical_details']
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

def create_requisition_pdf(order, req_type):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"FlexoBrain Material Requisition: {req_type}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Job Order: {order.get('order_number')}", ln=True)
    pdf.cell(0, 8, f"Customer: {order.get('customer_name')}", ln=True)
    pdf.cell(0, 8, f"Material Required: {req_type}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, "Please issue the requested materials for the aforementioned job order immediately to avoid production delays. All items must be checked by QC upon delivery to the shop floor.")
    
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Warehouse / Pre-press Signature: _______________________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI: Production Kanban Board ---
# ==========================================
st.title("🧠 FlexoBrain Production Board")
st.markdown("---")

def fetch_all_orders():
    try:
        response = supabase.table("job_orders").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

all_orders = fetch_all_orders()

pending_orders = [o for o in all_orders if o.get('status') == 'pending']
in_production_orders = [o for o in all_orders if o.get('status') == 'in_production']
completed_orders = [o for o in all_orders if o.get('status') == 'completed']

tab1, tab2, tab3 = st.tabs(["📥 Pending (New)", "⚙️ In Production", "✅ Completed"])

def display_order_card(order, current_tab):
    with st.expander(f"📦 Order: {order['order_number']} | Client: {order['customer_name']}", expanded=(current_tab == "in_prod")):
        
        # 1. Basic Info
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Product:** {order.get('product_type')}")
        col2.write(f"**Material:** {order.get('material_type')} ({order.get('thickness_micron')}µ)")
        col3.write(f"**Size:** {order.get('label_width_mm')} x {order.get('repeat_length_mm')} mm")
        col4.write(f"**QTY:** {order.get('required_quantity'):,} PCS")
        st.markdown("---")
        
        # 2. Technical Job Ticket (Unit Configuration)
        st.markdown("#### 🎨 Technical Job Ticket (Unit Configuration)")
        st.info("Setup each printing unit. Calculations for LPI and BCM are handled automatically.")
        
        colors_count = int(order.get('colors_count', 1))
        width_mm = order.get('label_width_mm', 0)
        repeat_mm = order.get('repeat_length_mm', 0)
        
        unit_tabs = st.tabs([f"⚙️ Unit {i}" for i in range(1, colors_count + 1)])
        
        for i, tab in enumerate(unit_tabs, start=1):
            with tab:
                col_ink, col_anilox, col_mount = st.columns(3)
                
                with col_ink:
                    st.caption("🎨 Ink & Color")
                    st.text_input("Color Name / Code", key=f"color_name_{order['id']}_{i}")
                    coverage_label = f"Ink coverage % (from W: {width_mm}mm x L: {repeat_mm}mm)"
                    st.number_input(coverage_label, min_value=0.0, max_value=100.0, value=20.0, key=f"cov_{order['id']}_{i}")
                    st.selectbox("Viscosity Cup", ["Ford #4", "DIN 4", "Zahn 2", "Other"], key=f"visc_{order['id']}_{i}")
                    st.text_input("LAB Values (L,a,b) From Ref", key=f"lab_{order['id']}_{i}")
                
                with col_anilox:
                    st.caption("🧻 Anilox Selection")
                    st.selectbox("Anilox Brand & No.", ["Select Anilox...", "Apex", "Sandon", "Cheshire", "Zecher"], key=f"anx_brand_{order['id']}_{i}")
                    lpc = st.number_input("Anilox LPC", min_value=0, value=100, step=10, key=f"lpc_{order['id']}_{i}")
                    st.caption(f"💧 Equivalent: {int(lpc * 2.54)} LPI")
                    vol_cm3 = st.number_input("Volume (cm³/m²)", min_value=0.0, value=4.65, step=0.1, key=f"vol_{order['id']}_{i}")
                    bcm_val = vol_cm3 / 1.55 if vol_cm3 > 0 else 0
                    st.caption(f"💧 Equivalent: {bcm_val:.2f} BCM")
                
                with col_mount:
                    st.caption("🛠️ Mounting")
                    st.selectbox("Tape Brand", ["tesa", "3M", "Lohmann", "Biessse", "Other"], key=f"tape_brand_{order['id']}_{i}")
                    st.selectbox("Tape Hardness", ["Soft", "Medium Soft", "Medium", "Medium Hard", "Hard"], key=f"tape_hard_{order['id']}_{i}")
        
        # 3. Material Requisitions (PDF Generators)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📥 Material Requisitions")
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            req_type = "New Cliche" if order.get("artwork_status") == "NEW" else "Archive Cliche"
            st.download_button(label=f"📑 Request {req_type}", data=create_requisition_pdf(order, "Cliché / Plates"), file_name=f"Cliche_Req_{order['order_number']}.pdf", mime="application/pdf", key=f"cliche_{order['id']}", use_container_width=True)
                
        with btn_col2:
            st.download_button(label="💧 Generate Ink Requisition", data=create_requisition_pdf(order, "Ink & Solvents"), file_name=f"Ink_Req_{order['order_number']}.pdf", mime="application/pdf", key=f"ink_req_{order['id']}", use_container_width=True)
            
        with btn_col3:
            st.download_button(label="🧻 Generate Tape Requisition", data=create_requisition_pdf(order, "Mounting Tape"), file_name=f"Tape_Req_{order['order_number']}.pdf", mime="application/pdf", key=f"tape_req_{order['id']}", use_container_width=True)
            
        with btn_col4:
            st.download_button(label="📦 Generate Roll Requisition", data=create_requisition_pdf(order, "Raw Material Rolls"), file_name=f"Roll_Req_{order['order_number']}.pdf", mime="application/pdf", key=f"roll_req_{order['id']}", use_container_width=True)
            
        st.markdown("---")
        
        # 4. Actions & Database Save Logic
        action1, action2 = st.columns(2)
        with action1:
            if current_tab == "pending":
                if st.button("🚀 Confirm Setup & Start Production", key=f"start_{order['id']}", type="primary"):
                    # Collect all technical data from the tabs dynamically
                    tech_data = {}
                    for i in range(1, colors_count + 1):
                        tech_data[f"Unit_{i}"] = {
                            "Color": st.session_state.get(f"color_name_{order['id']}_{i}", ""),
                            "Viscosity": st.session_state.get(f"visc_{order['id']}_{i}", ""),
                            "Anilox_Brand": st.session_state.get(f"anx_brand_{order['id']}_{i}", ""),
                            "Anilox_Vol": st.session_state.get(f"vol_{order['id']}_{i}", 0),
                            "Tape_Hardness": st.session_state.get(f"tape_hard_{order['id']}_{i}", "")
                        }
                    # Save to Supabase
                    supabase.table("job_orders").update({
                        "status": "in_production",
                        "technical_details": tech_data
                    }).eq("id", order['id']).execute()
                    st.rerun()
                    
            elif current_tab == "in_prod":
                if st.button("✅ Mark as Completed", key=f"comp_{order['id']}", type="primary"):
                    supabase.table("job_orders").update({"status": "completed"}).eq("id", order['id']).execute()
                    st.rerun()
        with action2:
            st.download_button(
                label="🖨️ Print Full Job Ticket",
                data=create_production_pdf(order),
                file_name=f"Production_Ticket_{order['order_number']}.pdf",
                mime="application/pdf",
                key=f"print_main_{order['id']}"
            )

# --- Populate Tabs ---
with tab1:
    if not pending_orders:
        st.info("No pending orders at the moment.")
    else:
        for order in pending_orders: display_order_card(order, "pending")

with tab2:
    if not in_production_orders:
        st.info("No orders currently in production.")
    else:
        for order in in_production_orders: display_order_card(order, "in_prod")

with tab3:
    if not completed_orders:
        st.info("No completed orders yet.")
    else:
        for order in completed_orders: display_order_card(order, "completed")
