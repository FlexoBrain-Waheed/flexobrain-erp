import streamlit as st
import pandas as pd
import datetime
import io
import tempfile
import os
import requests
from fpdf import FPDF
import sys
from pathlib import Path
from PIL import Image
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

st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 05 - Smart Control Center</div>", unsafe_allow_html=True)

# ==========================================
# --- Users & Digital Signature Dictionary ---
# ==========================================
USERS_DB = {
    "p11": "Eng. Amr Al mahmoudi",
    "p22": "Production Manager",
    "p33": "System Administrator"
}
current_user_id = st.session_state.get("user_id", "")
current_user_name = USERS_DB.get(current_user_id, "Sales Department")

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
# --- PDF Generation Engine (Imported) ---
# ==========================================
def create_pdf(data_dict, artwork_url=None, stamp_name="Sales Department"):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Sales Job Order - BOPP Wrap Around Label", ln=True, align='C')
    pdf.ln(2)
    
    def safe_txt(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')
        
    def section_header(title):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(190, 8, safe_txt(title), border=1, ln=True, fill=True)
        
    def row_2_cols(k1, v1, k2, v2):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, safe_txt(f"{k1}:"), border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 8, safe_txt(v1)[:40], border=1)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, safe_txt(f"{k2}:"), border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 8, safe_txt(v2)[:40], border=1, ln=True)

    def row_full(k, v):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, safe_txt(f"{k}:"), border=1)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(145, 8, safe_txt(v), border=1)

    # Section 1
    section_header("1. Order Information")
    row_2_cols("Job Order No", data_dict.get("Job Order No"), "Date", data_dict.get("Date"))
    row_2_cols("Customer Name", data_dict.get("Customer Name"), "Customer PO#", data_dict.get("Customer PO#"))
    row_2_cols("Sales PO#", data_dict.get("Sales PO#"), "Customer ID", data_dict.get("Customer ID"))
    row_full("Head Office Address", data_dict.get("Head Office Address"))
    row_full("Head Office City", data_dict.get("Head Office City"))
    pdf.ln(2)

    # Section 2
    section_header("2. Material Specifications")
    row_2_cols("Product Type", data_dict.get("Product Type"), "Material Type", data_dict.get("Material Type"))
    row_2_cols("Thickness (u)", data_dict.get("Thickness (u)"), "Density", data_dict.get("Density (g/cm3)"))
    row_2_cols("Mother Roll Width", data_dict.get("Mother Roll Width (mm)"), "Edge Trim", data_dict.get("Edge Trim (mm)"))
    pdf.ln(2)

    # Section 3
    section_header("3. Print & Dimensions")
    row_2_cols("Label Width (mm)", data_dict.get("Label/Film Width (mm)"), "Repeat Length", data_dict.get("Repeat Length (mm)"))
    row_2_cols("No. of Colors", data_dict.get("Colors"), "Film Color", data_dict.get("Color of Film"))
    row_2_cols("Artwork Status", data_dict.get("Artwork Status"), "Artwork No.", data_dict.get("Artwork No."))
    pdf.ln(2)

    # Section 4
    section_header("4. Print, Winding & Core")
    row_2_cols("Print Surface", data_dict.get("Print Surface"), "Final Format", data_dict.get("Final Format"))
    row_2_cols("Inner Core", data_dict.get("Inner Core"), "Core Type", data_dict.get("Core Type"))
    row_2_cols("Wall Thickness", data_dict.get("Wall Thickness (mm)"), "Winding Dir", data_dict.get("Winding Direction"))
    pdf.ln(2)

    # Section 5
    section_header("5. Quantity & Delivery")
    row_2_cols("Required QTY", data_dict.get("Required Quantity"), "Due Date", data_dict.get("Due Date"))
    row_2_cols("Delivery City", data_dict.get("Delivery City"), "Packaging", data_dict.get("Packaging"))
    row_full("Delivery Address", data_dict.get("Delivery Address"))
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    
    # --- DIGITAL STAMP ---
    pdf.ln(6)
    current_y = pdf.get_y()
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, current_y, 190, 32, 'F')
    pdf.set_xy(15, current_y + 5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, "[ APPROVED ] Digitally Approved & Sealed", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    
    current_time = datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")
    pdf.set_x(15)
    pdf.cell(0, 6, f"By: {stamp_name}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"Timestamp: {current_time}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"System ID: {data_dict.get('Job Order No')}", ln=True)

    # --- PAGE 2: ARTWORK (Fetched from URL) ---
    if artwork_url and str(artwork_url).startswith("http"):
        try:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C')
            pdf.ln(5)
            
            response = requests.get(artwork_url, stream=True, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    for chunk in response.iter_content(1024):
                        tmp_file.write(chunk)
                    tmp_path = tmp_file.name
                pdf.image(tmp_path, x=10, y=30, w=190)
                os.remove(tmp_path)
        except Exception as e:
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, "⚠️ Note: Artwork image could not be embedded.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Helper: Map DB Row to PDF Dict ---
# ==========================================
def map_db_to_pdf_dict(row):
    # Created At comes like "2026-04-12T10:30:00+00:00", we split to get the date part
    date_created = str(row.get('created_at', '')).split('T')[0] if row.get('created_at') else ""
    
    return {
        "Date": date_created,
        "Job Order No": row.get('order_number', ''),
        "Customer Name": row.get('customer_name', ''),
        "Customer ID": row.get('customer_id', ''),
        "Customer PO#": row.get('customer_po', ''),
        "Sales PO#": row.get('sales_po', ''),
        "Head Office Address": row.get('head_office_address', ''),
        "Head Office City": row.get('head_office_city', ''),
        "Delivery Address": row.get('delivery_address', ''),
        "Delivery City": row.get('delivery_city', ''),
        "Product Type": row.get('product_type', ''),
        "Material Type": row.get('material_type', ''),
        "Density (g/cm3)": str(row.get('density', '')),
        "Label/Film Width (mm)": str(row.get('label_width_mm', '')),
        "Repeat Length (mm)": str(row.get('repeat_length_mm', '')),
        "Thickness (u)": str(row.get('thickness_micron', '')),
        "Colors": str(row.get('colors_count', '')),
        "Color of Film": row.get('color_of_film', ''),
        "Artwork Status": row.get('artwork_status', ''),
        "Artwork No.": row.get('artwork_number', ''),
        "Print Surface": row.get('print_surface', ''),
        "Final Format": row.get('final_format', ''),
        "Inner Core": row.get('inner_core', ''),
        "Core Type": row.get('core_type', ''),
        "Wall Thickness (mm)": str(row.get('core_wall_thickness_mm', '')),
        "Winding Direction": row.get('winding_direction', ''),
        "Mother Roll Width (mm)": str(row.get('mother_roll_width_mm', '')),
        "Edge Trim (mm)": str(row.get('edge_trim_mm', '')),
        "Required Quantity": str(row.get('required_quantity', '')),
        "Packaging": row.get('packaging_notes', ''),
        "Due Date": str(row.get('due_date', '')),
        "Remarks / Notes": row.get('remarks', '')
    }

# ==========================================
# --- Action Functions ---
# ==========================================
def update_order_status(order_id, new_status):
    try:
        supabase.table("job_orders").update({"status": new_status}).eq("id", order_id).execute()
        st.toast(f"✅ Order status updated to {new_status.upper()}", icon="🔄")
    except Exception as e:
        st.error(f"Error updating status: {e}")

# ==========================================
# --- Main UI Starts Here ---
# ==========================================
st.title("📊 Sales Dashboard & Control Center")
st.markdown("---")

st.subheader("📋 Order Live Tracking")

# Fetch Data
try:
    response = supabase.table("job_orders").select("*").order("id", desc=True).execute()
    data = response.data
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if not data:
    st.info("No orders found in the database.")
else:
    # Colors and Emojis for statuses
    status_config = {
        'pending': '🟡 Pending',
        'in progress': '🔵 In Progress',
        'on hold': '⏸️ On Hold',
        'cancelled': '❌ Cancelled',
        'completed': '🟢 Completed'
    }

    for row in data:
        current_status = str(row.get('status', 'pending')).lower()
        status_disp = status_config.get(current_status, f"⚪ {current_status.upper()}")
        
        # Display title of the Expander
        expander_title = f"📦 Order: {row.get('order_number')} | Client: {row.get('customer_name')} | Status: {status_disp}"
        
        with st.expander(expander_title):
            # --- Mini-Card Data Enrichment ---
            st.markdown(f"**👤 Customer:** {row.get('customer_name')} | **📑 PO Number:** {row.get('customer_po', 'N/A')}")
            st.markdown(f"**🚚 Delivery:** {row.get('delivery_city', 'N/A')} (Due: {row.get('due_date', 'N/A')})")
            
            w = row.get('label_width_mm', 0)
            r = row.get('repeat_length_mm', 0)
            st.markdown(f"**⚙️ Specs:** {row.get('material_type')} ({row.get('thickness_micron')}µ) | **Size:** {w} x {r} mm | **QTY:** {int(row.get('required_quantity', 0)):,} PCS")
            
            art_url = row.get('artwork_url', '')
            art_disp = f"[🔗 View Artwork]({art_url})" if art_url and art_url.startswith("http") else "No URL"
            st.markdown(f"**🎨 Colors:** {row.get('colors_count')} | **Status:** {row.get('artwork_status')} | **Artwork:** {art_disp}")
            
            st.markdown("---")
            
            # --- Action Center (Buttons) ---
            col1, col2, col3, col4 = st.columns(4)
            
            # Action 1: Download PDF (Dynamic)
            with col1:
                pdf_dict = map_db_to_pdf_dict(row)
                pdf_file = create_pdf(pdf_dict, artwork_url=art_url, stamp_name=current_user_name)
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_file,
                    file_name=f"{row.get('order_number')}_Copy.pdf",
                    mime="application/pdf",
                    key=f"pdf_{row['id']}",
                    use_container_width=True
                )
            
            # Action 2: Repeat Order
            with col2:
                if st.button("🔄 Repeat Order", key=f"repeat_{row['id']}", use_container_width=True):
                    st.session_state['repeat_data'] = row
                    st.success("Data loaded! Please navigate to the 'OPP Label Order' page from the sidebar to submit the repeat order.")
            
            # Action 3 & 4: Status Controls (Hold / Cancel / Resume)
            with col3:
                if current_status == 'pending':
                    if st.button("⏸️ Put on Hold", key=f"hold_{row['id']}", use_container_width=True):
                        update_order_status(row['id'], 'on hold')
                        st.rerun()
                elif current_status == 'on hold':
                    if st.button("▶️ Resume Order", type="primary", key=f"resume_{row['id']}", use_container_width=True):
                        update_order_status(row['id'], 'pending')
                        st.rerun()
                else:
                    st.button("🔒 Locked", disabled=True, key=f"lock1_{row['id']}", use_container_width=True)
            
            with col4:
                if current_status in ['pending', 'on hold']:
                    if st.button("❌ Cancel Order", key=f"cancel_{row['id']}", use_container_width=True):
                        update_order_status(row['id'], 'cancelled')
                        st.rerun()
                else:
                    st.button("🔒 Locked", disabled=True, key=f"lock2_{row['id']}", use_container_width=True)
