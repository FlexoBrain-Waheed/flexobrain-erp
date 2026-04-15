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
import qrcode

# --- Page configuration ---
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path: sys.path.append(root_dir)

import auth
auth.require_role(["sales", "admin"])
auth.logout_button()

st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 08 - Fixed Spacing & Fields</div>", unsafe_allow_html=True)

USERS_DB = {"p11": "Eng. Amr Al mahmoudi", "p22": "Production Manager", "p33": "System Administrator"}
current_user_name = USERS_DB.get(st.session_state.get("user_id", ""), "Sales Department")

# ==========================================
# --- Supabase Database Connection (Bulletproof) ---
# ==========================================
@st.cache_resource
def init_connection():
    try:
        # Smart detection
        if "SUPABASE_URL" in st.secrets:
            raw_url = str(st.secrets["SUPABASE_URL"])
            raw_key = str(st.secrets["SUPABASE_KEY"])
        elif "supabase" in st.secrets:
            raw_url = str(st.secrets["supabase"]["url"])
            raw_key = str(st.secrets["supabase"]["key"])
        else:
            st.error("⚠️ Credentials missing in Secrets.")
            st.stop()
            
        # 🛑 Aggressive Cleanup: Remove accidental quotes and spaces
        clean_url = raw_url.strip().replace('"', '').replace("'", "")
        clean_key = raw_key.strip().replace('"', '').replace("'", "")
        
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"⚠️ Secrets parsing error: {e}")
        st.stop()

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# ==========================================
# --- PDF Generator ---
# ==========================================
def create_pdf(data_dict, artwork_url=None, stamp_name="Sales Department"):
    pdf = FPDF()
    pdf.add_page()
    
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(data_dict.get("Job Order No", ""))
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_qr:
        img_qr.save(tmp_qr.name)
        pdf.image(tmp_qr.name, x=175, y=10, w=25)
        os.remove(tmp_qr.name)

    pdf.set_font("Arial", 'B', 16)
    doc_title = "Sales Job Order - BOPP Wrap Around Label"
    if "-R" in data_dict.get("Job Order No", ""): doc_title += " [ REVISED ]"
    pdf.cell(0, 10, doc_title, ln=True, align='C')
    
    # FIX: Generous vertical space to avoid overlap
    pdf.ln(20)
    
    def safe_txt(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
    def section_header(title):
        pdf.set_font("Arial", 'B', 11); pdf.set_fill_color(220, 220, 220)
        pdf.cell(190, 8, safe_txt(title), border=1, ln=True, fill=True)
    def row_2_cols(k1, v1, k2, v2):
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 8, safe_txt(f"{k1}:"), border=1)
        pdf.set_font("Arial", '', 10); pdf.cell(50, 8, safe_txt(v1)[:40], border=1)
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 8, safe_txt(f"{k2}:"), border=1)
        pdf.set_font("Arial", '', 10); pdf.cell(50, 8, safe_txt(v2)[:40], border=1, ln=True)
    def row_full(k, v):
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 8, safe_txt(f"{k}:"), border=1)
        pdf.set_font("Arial", '', 10); pdf.multi_cell(145, 8, safe_txt(v), border=1)

    section_header("1. Order Information")
    row_2_cols("Job Order No", data_dict.get("Job Order No"), "Date", data_dict.get("Date"))
    row_2_cols("Customer Name", data_dict.get("Customer Name"), "Customer PO#", data_dict.get("Customer PO#"))
    row_2_cols("Product Code", data_dict.get("Product Code"), "Sales PO / Quotation", data_dict.get("Sales PO / Quotation")) # Restored
    row_2_cols("Customer ID", data_dict.get("Customer ID"), "", "")
    row_full("Head Office Address", data_dict.get("Head Office Address"))
    row_full("Head Office City", data_dict.get("Head Office City"))
    pdf.ln(2)

    section_header("2. Material Specifications")
    row_2_cols("Product Type", data_dict.get("Product Type"), "Material Type", data_dict.get("Material Type"))
    row_2_cols("Thickness (u)", data_dict.get("Thickness (u)"), "Density", data_dict.get("Density (g/cm3)"))
    row_2_cols("Mother Roll Width", data_dict.get("Mother Roll Width (mm)"), "Edge Trim", data_dict.get("Edge Trim (mm)"))
    pdf.ln(2)

    section_header("3. Print & Dimensions")
    row_2_cols("Label Width (mm)", data_dict.get("Label/Film Width (mm)"), "Repeat Length", data_dict.get("Repeat Length (mm)"))
    row_2_cols("No. of Colors", data_dict.get("Colors"), "Film Color", data_dict.get("Color of Film"))
    row_2_cols("Artwork Status", data_dict.get("Artwork Status"), "Artwork No.", data_dict.get("Artwork No.")) # Restored
    pdf.ln(2)

    section_header("4. Print, Winding & Core")
    row_2_cols("Print Surface", data_dict.get("Print Surface"), "Final Format", data_dict.get("Final Format"))
    row_2_cols("Inner Core", data_dict.get("Inner Core"), "Core Type", data_dict.get("Core Type"))
    row_2_cols("Wall Thickness", data_dict.get("Wall Thickness (mm)"), "Winding Dir", data_dict.get("Winding Direction")) # Restored
    pdf.ln(2)

    section_header("5. Quantity & Delivery")
    row_2_cols("Required QTY", data_dict.get("Required Quantity"), "Due Date", data_dict.get("Due Date"))
    row_2_cols("Delivery City", data_dict.get("Delivery City"), "Packaging", data_dict.get("Packaging")) # Restored
    row_full("Delivery Address", data_dict.get("Delivery Address")) # Restored
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    
    pdf.ln(6); current_y = pdf.get_y(); pdf.set_fill_color(245, 245, 245); pdf.rect(10, current_y, 190, 32, 'F')
    pdf.set_xy(15, current_y + 5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, "[ APPROVED ] Digitally Approved & Sealed", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 10)
    current_time = datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")
    pdf.set_x(15); pdf.cell(0, 6, f"By: {stamp_name}", ln=True)
    pdf.set_x(15); pdf.cell(0, 6, f"Timestamp: {current_time}", ln=True)
    pdf.set_x(15); pdf.cell(0, 6, f"System ID: {data_dict.get('Job Order No')}", ln=True)

    if artwork_url and str(artwork_url).startswith("http"):
        try:
            pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork", ln=True, align='C'); pdf.ln(5)
            response = requests.get(artwork_url, stream=True, timeout=10)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    for chunk in response.iter_content(1024): tmp_file.write(chunk)
                pdf.image(tmp_file.name, x=10, y=30, w=190); os.remove(tmp_file.name)
        except: pass
    return pdf.output(dest='S').encode('latin-1')

def map_db_to_pdf_dict(row):
    return {
        "Date": str(row.get('created_at', '')).split('T')[0] if row.get('created_at') else "",
        "Job Order No": row.get('order_number', ''), "Customer Name": row.get('customer_name', ''),
        "Customer ID": row.get('customer_id', ''), "Customer PO#": row.get('customer_po', ''),
        "Sales PO / Quotation": row.get('sales_po', ''), "Product Code": row.get('product_code', ''), # Restored
        "Head Office Address": row.get('head_office_address', ''), "Head Office City": row.get('head_office_city', ''),
        "Delivery Address": row.get('delivery_address', ''), "Delivery City": row.get('delivery_city', ''), # Restored
        "Product Type": row.get('product_type', ''), "Material Type": row.get('material_type', ''),
        "Density (g/cm3)": str(row.get('density', '')), "Label/Film Width (mm)": str(row.get('label_width_mm', '')),
        "Repeat Length (mm)": str(row.get('repeat_length_mm', '')), "Thickness (u)": str(row.get('thickness_micron', '')),
        "Colors": str(row.get('colors_count', '')), "Color of Film": row.get('color_of_film', ''),
        "Artwork Status": row.get('artwork_status', ''), "Artwork No.": row.get('artwork_number', ''), # Restored
        "Print Surface": row.get('print_surface', ''), "Final Format": row.get('final_format', ''),
        "Inner Core": row.get('inner_core', ''), "Core Type": row.get('core_type', ''),
        "Wall Thickness (mm)": str(row.get('core_wall_thickness_mm', '')), "Winding Direction": row.get('winding_direction', ''), # Restored
        "Mother Roll Width (mm)": str(row.get('mother_roll_width_mm', '')), "Edge Trim (mm)": str(row.get('edge_trim_mm', '')),
        "Required Quantity": str(row.get('required_quantity', '')), "Packaging": row.get('packaging_notes', ''), # Restored
        "Due Date": str(row.get('due_date', '')), "Remarks / Notes": row.get('remarks', '')
    }

def update_order_status(order_id, new_status):
    try:
        supabase.table("job_orders").update({"status": new_status}).eq("id", order_id).execute()
        st.toast(f"✅ Order status updated to {new_status.upper()}", icon="🔄")
    except Exception as e: st.error(f"Error: {e}")

st.title("📊 Sales Dashboard & Control Center")
st.markdown("---")

try: data = supabase.table("job_orders").select("*").order("id", desc=True).execute().data
except Exception as e: st.error(f"Error fetching data: {e}"); st.stop()

if not data: st.info("No orders found.")
else:
    df = pd.DataFrame(data)
    df['order_date'] = pd.to_datetime(df['created_at']).dt.date
    unique_dates = df['order_date'].unique()
    status_config = {'pending':'🟡 Pending', 'in progress':'🔵 In Progress', 'on hold':'⏸️ On Hold', 'cancelled':'❌ Cancelled', 'completed':'🟢 Completed'}

    for d in unique_dates:
        daily_orders = df[df['order_date'] == d]
        total_qty = daily_orders['required_quantity'].sum()
        with st.expander(f"📁 Orders for: {d.strftime('%Y-%m-%d')}  |  Orders: {len(daily_orders)}  |  Total QTY: {int(total_qty):,} PCS", expanded=(d == unique_dates[0])):
            for _, row_series in daily_orders.iterrows():
                row = row_series.to_dict()
                status_disp = status_config.get(str(row.get('status', 'pending')).lower(), f"⚪ {row.get('status', 'pending').upper()}")
                st.markdown(f"**📦 {row.get('order_number')}** | 👤 {row.get('customer_name')} | Status: {status_disp}")
                w, r = row.get('label_width_mm', 0), row.get('repeat_length_mm', 0)
                st.caption(f"⚙️ Specs: {row.get('material_type')} ({row.get('thickness_micron')}µ) | Size: {w}x{r} mm | QTY: {int(row.get('required_quantity', 0)):,} PCS")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    pdf_file = create_pdf(map_db_to_pdf_dict(row), artwork_url=row.get('artwork_url', ''), stamp_name=current_user_name)
                    st.download_button("📄 PDF w/ QR", data=pdf_file, file_name=f"{row.get('order_number')}.pdf", key=f"pdf_{row['id']}", use_container_width=True)
                with col2:
                    if st.button("🔄 Repeat", key=f"rep_{row['id']}", use_container_width=True):
                        st.session_state['repeat_data'] = row
                        if 'edit_data' in st.session_state: del st.session_state['edit_data']
                        st.success("Loaded as REPEAT.")
                with col3:
                    if row.get('status', 'pending') in ['pending', 'on hold']:
                        if st.button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True):
                            st.session_state['edit_data'] = row
                            if 'repeat_data' in st.session_state: del st.session_state['repeat_data']
                            st.warning("EDIT Mode Active.")
                    else: st.button("✏️ Edit", disabled=True, key=f"ed_d_{row['id']}", use_container_width=True)
                with col4:
                    curr_st = str(row.get('status', 'pending')).lower()
                    if curr_st == 'pending':
                        if st.button("⏸️ Hold", key=f"hold_{row['id']}", use_container_width=True): update_order_status(row['id'], 'on hold'); st.rerun()
                    elif curr_st == 'on hold':
                        if st.button("▶️ Resume", type="primary", key=f"res_{row['id']}", use_container_width=True): update_order_status(row['id'], 'pending'); st.rerun()
                    else: st.button("🔒 Locked", disabled=True, key=f"l1_{row['id']}", use_container_width=True)
                with col5:
                    if curr_st in ['pending', 'on hold']:
                        if st.button("❌ Cancel", key=f"can_{row['id']}", use_container_width=True): update_order_status(row['id'], 'cancelled'); st.rerun()
                    else: st.button("🔒 Locked", disabled=True, key=f"l2_{row['id']}", use_container_width=True)
                st.markdown("---")
