import streamlit as st
import datetime
import pandas as pd
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
st.set_page_config(page_title="BOPP Label Order", page_icon="📝", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth
auth.require_role(["sales", "admin"])
auth.logout_button()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 21 - ISO Revision Control</div>", unsafe_allow_html=True)

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
# --- Helper Functions ---
# ==========================================
def safe_idx(opt_list, val):
    try:
        return opt_list.index(val)
    except (ValueError, KeyError):
        return 0

def generate_order_number(supabase_client):
    today_str = datetime.date.today().strftime("%Y%m%d")
    prefix = f"BOPP-{today_str}-"
    try:
        response = supabase_client.table("job_orders").select("order_number").execute()
        seqs = []
        for row in response.data:
            if row.get('order_number', '').startswith(prefix):
                try:
                    # Ignore revisions for the base sequence generator
                    base_num = row['order_number'].split('-R')[0]
                    seq = int(base_num.split('-')[-1])
                    seqs.append(seq)
                except:
                    pass
        next_seq = max(seqs) + 1 if seqs else 1
        return f"{prefix}{next_seq:03d}"
    except Exception as e:
        return f"{prefix}999"

def generate_revision_number(base_order_no):
    """Generates an ISO standard revision number (-R1, -R2, etc.)"""
    if "-R" in base_order_no:
        parts = base_order_no.rsplit("-R", 1)
        try:
            rev_num = int(parts[1]) + 1
            return f"{parts[0]}-R{rev_num}"
        except ValueError:
            return f"{base_order_no}-R1"
    return f"{base_order_no}-R1"

# ==========================================
# --- Mode Detection (Edit vs Repeat vs New) ---
# ==========================================
edit_order = st.session_state.get('edit_data', {})
old_order = st.session_state.get('repeat_data', {})

is_edit_mode = bool(edit_order)
is_repeat_mode = bool(old_order)

# active_data dictates what fills the default values
active_data = edit_order if is_edit_mode else old_order

# Generate appropriate Job Order Number for display
if is_edit_mode:
    target_job_order_no = generate_revision_number(active_data.get("order_number", ""))
else:
    target_job_order_no = generate_order_number(supabase)

# ==========================================
# --- Smart Calculator Callbacks & State ---
# ==========================================
if 'in_lines' not in st.session_state:
    st.session_state['in_lines'] = int(active_data.get("no_of_lines", 1))
if 'in_qty' not in st.session_state:
    st.session_state['in_qty'] = int(active_data.get("required_quantity", 0))

def calc_smart_lines():
    mw = st.session_state.get('in_mr_width', 0.0)
    w = st.session_state.get('in_width', 0.0)
    trim = st.session_state.get('in_edge', 24.0)
    if mw > 0 and w > 0:
        suggested = int((mw - trim) / w)
        st.session_state['in_lines'] = suggested if suggested > 0 else 1
    calc_smart_qty()

def calc_smart_qty():
    mr_len = st.session_state.get('in_mr_len', 0.0)
    rep = st.session_state.get('in_repeat', 0.0)
    lines = st.session_state.get('in_lines', 1)
    rolls = st.session_state.get('in_rolls', 1)
    if mr_len > 0 and rep > 0:
        st.session_state['in_qty'] = int(((mr_len * 1000) / rep) * lines * rolls)

# ==========================================
# --- PDF Engine ---
# ==========================================
def create_pdf(data_dict, image_file=None, artwork_url=None, stamp_name="Sales Department"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header distinction based on mode
    doc_title = "Sales Job Order - BOPP Wrap Around Label"
    if "-R" in data_dict.get("Job Order No", ""):
        doc_title += " [ REVISED ]"
        
    pdf.cell(0, 10, doc_title, ln=True, align='C')
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

    section_header("1. Order Information")
    row_2_cols("Job Order No", data_dict.get("Job Order No"), "Date", data_dict.get("Date"))
    row_2_cols("Customer Name", data_dict.get("Customer Name"), "Customer PO#", data_dict.get("Customer PO#"))
    row_2_cols("Sales PO#", data_dict.get("Sales PO#"), "Customer ID", data_dict.get("Customer ID"))
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
    row_2_cols("Artwork Status", data_dict.get("Artwork Status"), "Artwork No.", data_dict.get("Artwork No."))
    pdf.ln(2)

    section_header("4. Print, Winding & Core")
    row_2_cols("Print Surface", data_dict.get("Print Surface"), "Final Format", data_dict.get("Final Format"))
    row_2_cols("Inner Core", data_dict.get("Inner Core"), "Core Type", data_dict.get("Core Type"))
    row_2_cols("Wall Thickness", data_dict.get("Wall Thickness (mm)"), "Winding Dir", data_dict.get("Winding Direction"))
    pdf.ln(2)

    section_header("5. Quantity & Delivery")
    row_2_cols("Required QTY", data_dict.get("Required Quantity"), "Due Date", data_dict.get("Due Date"))
    row_2_cols("Delivery City", data_dict.get("Delivery City"), "Packaging", data_dict.get("Packaging"))
    row_full("Delivery Address", data_dict.get("Delivery Address"))
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    
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

    if image_file is not None or (artwork_url and str(artwork_url).startswith("http")):
        try:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C')
            pdf.ln(5)
            
            if image_file is not None:
                img = Image.open(image_file).convert('RGB')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_path = tmp_file.name
                    img.save(tmp_path, format="JPEG")
                pdf.image(tmp_path, x=10, y=30, w=190)
                os.remove(tmp_path)
            elif artwork_url:
                response = requests.get(artwork_url, stream=True, timeout=10)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        for chunk in response.iter_content(1024):
                            tmp_file.write(chunk)
                        tmp_path = tmp_file.name
                    pdf.image(tmp_path, x=10, y=30, w=190)
                    os.remove(tmp_path)
        except Exception as e:
            pass

    return pdf.output(dest='S').encode('latin-1')


# ==========================================
# --- Main UI Starts Here ---
# ==========================================
st.title("📝 Create / Edit Job Order - Wrap Around Label")

if is_edit_mode:
    st.warning(f"✏️ **EDIT MODE ACTIVE:** You are modifying Order **{active_data.get('order_number')}**. A new revision number **{target_job_order_no}** will be generated upon saving.")
elif is_repeat_mode:
    st.info(f"🔄 **REPEAT MODE ACTIVE:** Auto-filling data based on previous Job Order **{active_data.get('order_number')}**")

st.markdown("---")

st.subheader("👤 1. Customer Information")
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", datetime.date.today(), key="in_date")
    company_name = st.text_input("Company Name", value=active_data.get("customer_name", ""), key="in_company")
with col2:
    job_order_no = st.text_input("Job Order No.", value=target_job_order_no, disabled=True) 
    customer_id = st.text_input("Customer ID", value=active_data.get("customer_id", ""), key="in_cust_id")
with col3:
    po_number = st.text_input("Customer's PO#", value=active_data.get("customer_po", ""), key="in_po")
    sales_po = st.text_input("Sales PO#", value=active_data.get("sales_po", ""), key="in_sales_po")

col_addr1, col_addr2 = st.columns(2)
with col_addr1:
    head_office_address = st.text_input("Company Head Office Address", value=active_data.get("head_office_address", ""), key="in_addr1")
with col_addr2:
    head_office_city = st.text_input("Company Head Office City", value=active_data.get("head_office_city", ""), key="in_addr2")
st.markdown("---")

st.subheader("⚙️ 2. Product Specs")
st.text_input("Product Type", value="BOPP Wrap Around Label", disabled=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)", value=active_data.get("product_code", ""), key="in_prod_code")
with col_s2:
    mat_ops = ["BOPP", "PETG", "PE", "Other"]
    material_type = st.selectbox("Material Type", mat_ops, index=safe_idx(mat_ops, active_data.get("material_type", "BOPP")), key="in_mat_type")
with col_s3:
    den_ops = [0.91, 0.92, 1.40]
    density = st.selectbox("Density (g/cm3)", den_ops, index=safe_idx(den_ops, float(active_data.get("density", 0.91)) if active_data.get("density") else 0.91), key="in_density") 
with col_s4:
    thk_ops = [30, 35, 38, 40]
    thickness = st.selectbox("Thickness (u)", thk_ops, index=safe_idx(thk_ops, int(active_data.get("thickness_micron", 30)) if active_data.get("thickness_micron") else 30), key="in_thick")

col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Label Width (mm)", min_value=0.0, value=float(active_data.get("label_width_mm", 0.0)), key="in_width", on_change=calc_smart_lines) 
with col_s6:
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0, value=float(active_data.get("repeat_length_mm", 0.0)), key="in_repeat", on_change=calc_smart_qty)
with col_s7:
    color_choice = st.selectbox("Color of Film", ["Transparent", "White", "Other"], key="in_color_choice")
    color_of_film = st.text_input("Specify Color:", value=active_data.get("color_of_film", "Transparent"), key="in_spec_color") if color_choice == "Other" else color_choice
with col_s8:
    colors_no = st.number_input("No. of Colors", min_value=1, max_value=10, value=int(active_data.get("colors_count", 1)) if active_data else 1, key="in_color_no")

col_s9, col_s10 = st.columns(2)
with col_s9:
    art_ops = ["NEW", "REPEAT"]
    artwork = st.selectbox("Artwork Status", art_ops, index=safe_idx(art_ops, active_data.get("artwork_status", "NEW")), key="in_art_stat")
with col_s10:
    artwork_no = st.text_input("Artwork No.", value=active_data.get("artwork_number", ""), key="in_art_no") 

st.markdown("#### 🧻 Print, Core & Winding Specifications")
col_w1, col_w2 = st.columns(2)
with col_w1:
    print_ops = ["Reverse Print", "Surface Print"]
    print_position = st.selectbox("Print Surface", print_ops, index=safe_idx(print_ops, active_data.get("print_surface", "Reverse Print")), key="in_print_surf")
with col_w2:
    fmt_ops = ["Roll", "Cut (Pieces)"]
    final_format = st.selectbox("Final Product Format", fmt_ops, index=safe_idx(fmt_ops, active_data.get("final_format", "Roll")), key="in_final_form")

col_d1, col_d2, col_d3, col_d4 = st.columns(4)
with col_d1:
    core_ops = ["3 inch", "6 inch"]
    inner_core = st.selectbox("Inner Core", core_ops, index=safe_idx(core_ops, active_data.get("inner_core", "6 inch")) if active_data else 1, key="in_inner_core")
with col_d2:
    ctype_ops = ["Paper", "Plastic"]
    core_type = st.selectbox("Core Type", ctype_ops, index=safe_idx(ctype_ops, active_data.get("core_type", "Paper")), key="in_core_type")
with col_d3:
    core_thickness = st.number_input("Wall Thickness (mm)", min_value=0.0, value=float(active_data.get("core_wall_thickness_mm", 0.0)), key="in_core_thick")
with col_d4:
    wind_ops = ["Clockwise #4", "Anti-clockwise #3"]
    winding_direction = st.selectbox("Winding Direction", wind_ops, index=safe_idx(wind_ops, active_data.get("winding_direction", "Clockwise #4")), key="in_wind_dir")

st.markdown("#### 🧮 Smart Web & Production Calculator")
col_edge, _, _, _ = st.columns(4)
with col_edge:
    edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0.0, value=float(active_data.get("edge_trim_mm", 24.0)), key="in_edge", on_change=calc_smart_lines)

col_calc1, col_calc_rolls, col_calc2, col_calc3 = st.columns(4)
with col_calc1:
    mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0.0, value=float(active_data.get("mother_roll_length_m", 0.0)), key="in_mr_len", on_change=calc_smart_qty)
with col_calc_rolls:
    no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=int(active_data.get("no_of_rolls", 1)), key="in_rolls", on_change=calc_smart_qty)
with col_calc2:
    mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0.0, value=float(active_data.get("mother_roll_width_mm", 0.0)), key="in_mr_width", on_change=calc_smart_lines)
with col_calc3:
    no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, key="in_lines", on_change=calc_smart_qty)

pcs_per_roll = int((mother_roll_length * 1000) / repeat_length) if mother_roll_length > 0 and repeat_length > 0 else 0
waste_by_mm = float(mother_roll_width - (width * no_of_lines)) if mother_roll_width > 0 and width > 0 and no_of_lines > 0 else 0.0
unused_waste = float(waste_by_mm - edge_trim) if waste_by_mm > 0 else 0.0

col_calc5, col_calc6, col_calc7, _ = st.columns(4)
with col_calc5:
    st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
with col_calc6:
    st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
with col_calc7:
    st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

width_error = False
required_roll_width = (width * no_of_lines) + edge_trim
if mother_roll_width > 0 and required_roll_width > mother_roll_width:
    st.error(f"❌ Engineering Alert: Required production width ({required_roll_width} mm) exceeds Mother Roll Width ({mother_roll_width} mm). Please check measurements.")
    width_error = True

total_labels_calculated = 0
if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0 and no_of_rolls > 0:
    total_labels_calculated = pcs_per_roll * no_of_lines * no_of_rolls
    st.info(f"💡 Calculated Total Quantity: **{total_labels_calculated:,}** PCS")

st.markdown("---")
st.subheader("📦 3. Quantity, Delivery & Artwork")

uploaded_design = st.file_uploader("🖼️ Upload Approved Design", type=["jpg", "jpeg", "png"], key="in_upload")
existing_artwork_url = active_data.get('artwork_url', "")

if uploaded_design is not None:
    st.image(uploaded_design, caption="New Artwork Uploaded", width=200)
elif existing_artwork_url and str(existing_artwork_url).startswith("http"):
    st.success("🔄 USING EXISTING DESIGN PREVIOUSLY ATTACHED")
    try:
        st.image(existing_artwork_url, caption="Existing design", width=200)
    except Exception:
        st.info("Existing design link attached to order.")

col_q1, col_q2, col_q3 = st.columns(3) 
with col_q1:
    quantity = st.number_input("Required Quantity", min_value=0, step=1000, key="in_qty") 
with col_q2:
    delivery_city = st.text_input("Delivery City", value=active_data.get("delivery_city", ""), key="in_city") 
with col_q3:
    delivery_address = st.text_input("Delivery Address", value=active_data.get("delivery_address", ""), key="in_addr_deliv")

col_q4, col_q5 = st.columns(2)
with col_q4:
    # Handle potentially missing or differently formatted dates gracefully
    default_date = datetime.date.today()
    try:
        if active_data.get("due_date"):
            default_date = datetime.datetime.strptime(active_data["due_date"], "%Y-%m-%d").date()
    except:
        pass
    due_date = st.date_input("Due Date", default_date, key="in_due")
    
with col_q5:
    packaging = st.text_input("Packaging", value=active_data.get("packaging_notes", "Suitable / As Usual"), key="in_pack")

notes = st.text_area("Remarks / Notes", value=active_data.get("remarks", ""), key="in_notes")

# PDF Data Dictionary
pdf_data = {
    "Date": str(date),
    "Job Order No": target_job_order_no,
    "Customer Name": company_name,
    "Customer ID": customer_id,
    "Customer PO#": po_number,
    "Sales PO#": sales_po,          
    "Head Office Address": head_office_address,
    "Head Office City": head_office_city,
    "Delivery Address": delivery_address,
    "Delivery City": delivery_city, 
    "Product Type": "BOPP Wrap Around Label", 
    "Material Type": material_type, 
    "Density (g/cm3)": str(density),     
    "Label/Film Width (mm)": str(width),
    "Repeat Length (mm)": str(repeat_length), 
    "Thickness (u)": str(thickness),
    "Colors": str(colors_no),
    "Color of Film": color_of_film, 
    "Artwork Status": artwork,
    "Artwork No.": artwork_no,
    "Print Surface": print_position,
    "Final Format": final_format, 
    "Inner Core": inner_core,
    "Core Type": core_type,                 
    "Wall Thickness (mm)": str(core_thickness),  
    "Winding Direction": winding_direction,
    "Mother Roll Width (mm)": str(mother_roll_width),
    "Edge Trim (mm)": str(edge_trim),
    "Required Quantity": str(quantity),
    "Packaging": packaging,
    "Due Date": str(due_date),
    "Remarks / Notes": notes
}

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🎯 Actions")
btn_col1, btn_col2, btn_col3 = st.columns(3) 

with btn_col1:
    # Button text adapts to mode
    save_btn_text = "🔄 Update Order (Revision)" if is_edit_mode else "💾 Save to Cloud & Send"
    
    if st.button(save_btn_text, type="primary", use_container_width=True):
        if width_error:
            st.error("❌ Cannot save. Please fix the width calculation errors first.")
        elif not company_name:
            st.error("❌ Please enter Customer Name before saving.")
        else:
            with st.spinner("Processing data to cloud..."):
                try:
                    final_url_to_save = existing_artwork_url
                    
                    # --- Storage Upload Logic ---
                    if uploaded_design is not None:
                        file_ext = uploaded_design.name.split('.')[-1]
                        file_name = f"{target_job_order_no}.{file_ext}"
                        file_bytes = uploaded_design.getvalue()
                        mime_type = uploaded_design.type
                        
                        try:
                            supabase.storage.from_('artworks').upload(
                                path=file_name,
                                file=file_bytes,
                                file_options={"content-type": mime_type}
                            )
                            final_url_to_save = supabase.storage.from_('artworks').get_public_url(file_name)
                        except Exception as upload_err:
                            st.warning(f"⚠️ Image upload warning: {upload_err}")

                    db_data = {
                        "order_number": target_job_order_no,
                        "customer_name": company_name,
                        "customer_po": po_number,
                        "sales_po": sales_po,
                        "customer_id": customer_id,
                        "head_office_address": head_office_address,
                        "head_office_city": head_office_city,
                        "delivery_address": delivery_address,
                        "delivery_city": delivery_city,
                        "product_type": "BOPP Wrap Around Label",
                        "product_code": product_code,
                        "material_type": material_type,
                        "density": float(density) if density else 0.0,
                        "thickness_micron": float(thickness) if thickness else 0.0,
                        "label_width_mm": float(width) if width else 0.0,
                        "repeat_length_mm": float(repeat_length) if repeat_length else 0.0,
                        "color_of_film": color_of_film,
                        "colors_count": int(colors_no) if colors_no else 0,
                        "artwork_status": artwork,
                        "artwork_number": artwork_no,
                        "artwork_url": final_url_to_save,
                        "print_surface": print_position,
                        "final_format": final_format,
                        "inner_core": inner_core,
                        "core_type": core_type,
                        "core_wall_thickness_mm": float(core_thickness) if core_thickness else 0.0,
                        "winding_direction": winding_direction,
                        "mother_roll_length_m": float(mother_roll_length) if mother_roll_length else 0.0,
                        "no_of_rolls": int(no_of_rolls) if no_of_rolls else 0,
                        "no_of_lines": int(no_of_lines) if no_of_lines else 0,
                        "mother_roll_width_mm": float(mother_roll_width) if mother_roll_width else 0.0,
                        "edge_trim_mm": float(edge_trim) if edge_trim else 0.0,
                        "required_quantity": int(quantity) if quantity else 0,
                        "packaging_notes": packaging,
                        "due_date": str(due_date),
                        "remarks": notes,
                        "status": "pending"
                    }
                    
                    if is_edit_mode:
                        # UPDATE existing record using its unique database ID
                        response = supabase.table("job_orders").update(db_data).eq("id", active_data["id"]).execute()
                        st.success(f"✅ Order successfully UPDATED as {target_job_order_no}!")
                    else:
                        # INSERT new record
                        response = supabase.table("job_orders").insert(db_data).execute()
                        st.success(f"✅ Order successfully saved to Cloud as {target_job_order_no}!")
                        st.balloons()
                    
                    # Clear states after successful save
                    if 'repeat_data' in st.session_state:
                        del st.session_state['repeat_data']
                    if 'edit_data' in st.session_state:
                        del st.session_state['edit_data']
                        
                except Exception as e:
                    st.error(f"❌ Database Error: {str(e)}")

with btn_col2:
    pdf_url = existing_artwork_url if uploaded_design is None else None
    pdf_file = create_pdf(pdf_data, image_file=uploaded_design, artwork_url=pdf_url, stamp_name=current_user_name)
    
    st.download_button(
        label="📄 Export PDF",
        data=pdf_file,
        file_name=f"{target_job_order_no}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with btn_col3:
    if st.button("🗑️ Reset Form / Exit Edit Mode", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["authenticated", "role", "user_id"]:
                del st.session_state[key]
        st.rerun()
