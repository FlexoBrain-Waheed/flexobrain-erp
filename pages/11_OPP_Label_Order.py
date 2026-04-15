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
import qrcode

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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 24 - Complete Smart ERP</div>", unsafe_allow_html=True)

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
# --- Helper Functions ---
# ==========================================
def safe_idx(opt_list, val):
    try: return opt_list.index(val)
    except (ValueError, KeyError): return 0

def generate_order_number(supabase_client):
    today_str = datetime.date.today().strftime("%Y%m%d")
    prefix = f"BOPP-{today_str}-"
    try:
        response = supabase_client.table("job_orders").select("order_number").execute()
        seqs = []
        for row in response.data:
            if row.get('order_number', '').startswith(prefix):
                try:
                    base_num = row['order_number'].split('-R')[0]
                    seq = int(base_num.split('-')[-1])
                    seqs.append(seq)
                except: pass
        next_seq = max(seqs) + 1 if seqs else 1
        return f"{prefix}{next_seq:03d}"
    except Exception as e:
        return f"{prefix}999"

def generate_revision_number(base_order_no):
    if "-R" in base_order_no:
        parts = base_order_no.rsplit("-R", 1)
        try: return f"{parts[0]}-R{int(parts[1]) + 1}"
        except ValueError: return f"{base_order_no}-R1"
    return f"{base_order_no}-R1"

def compress_image(image_file, quality=65):
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    return buffer

# ==========================================
# --- Fetch Customers for Autocomplete ---
# ==========================================
try:
    cust_res = supabase.table("job_orders").select("customer_name, customer_id, head_office_address, head_office_city").execute()
    if cust_res.data:
        cust_df = pd.DataFrame(cust_res.data).drop_duplicates(subset=['customer_name']).dropna(subset=['customer_name'])
    else: cust_df = pd.DataFrame()
except Exception:
    cust_df = pd.DataFrame()

# ==========================================
# --- Mode Detection (Edit vs Repeat vs New) ---
# ==========================================
edit_order = st.session_state.get('edit_data', {})
old_order = st.session_state.get('repeat_data', {})
is_edit_mode = bool(edit_order)
is_repeat_mode = bool(old_order)
active_data = edit_order if is_edit_mode else old_order

if is_edit_mode: target_job_order_no = generate_revision_number(active_data.get("order_number", ""))
else: target_job_order_no = generate_order_number(supabase)

# ==========================================
# --- Smart Web Calculator Callbacks ---
# ==========================================
if 'in_lines' not in st.session_state: st.session_state['in_lines'] = int(active_data.get("no_of_lines", 1))
if 'in_qty' not in st.session_state: st.session_state['in_qty'] = int(active_data.get("required_quantity", 0))

def calc_smart_lines():
    mw, w, trim = st.session_state.get('in_mr_width', 0.0), st.session_state.get('in_width', 0.0), st.session_state.get('in_edge', 24.0)
    if mw > 0 and w > 0:
        suggested = int((mw - trim) / w)
        st.session_state['in_lines'] = suggested if suggested > 0 else 1
    calc_smart_qty()

def calc_smart_qty():
    mr_len, rep, lines, rolls = st.session_state.get('in_mr_len', 0.0), st.session_state.get('in_repeat', 0.0), st.session_state.get('in_lines', 1), st.session_state.get('in_rolls', 1)
    if mr_len > 0 and rep > 0:
        st.session_state['in_qty'] = int(((mr_len * 1000) / rep) * lines * rolls)

# ==========================================
# --- PDF Engine (with QR Code & Spacing Fix) ---
# ==========================================
def create_pdf(data_dict, image_file=None, artwork_url=None, stamp_name="Sales Department"):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(data_dict.get("Job Order No", ""))
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_qr:
        img_qr.save(tmp_qr.name)
        pdf.image(tmp_qr.name, x=175, y=10, w=25)
        os.remove(tmp_qr.name)

    # 2. Main PDF Content
    pdf.set_font("Arial", 'B', 16)
    doc_title = "Sales Job Order - BOPP Wrap Around Label"
    if "-R" in data_dict.get("Job Order No", ""): doc_title += " [ REVISED ]"
        
    pdf.cell(0, 10, doc_title, ln=True, align='C')
    
    # FIX: Added generous vertical space so tables do not overlap the QR code
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

    if image_file is not None or (artwork_url and str(artwork_url).startswith("http")):
        try:
            pdf.add_page(); pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C'); pdf.ln(5)
            if image_file is not None:
                img = Image.open(image_file).convert('RGB')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file: img.save(tmp_file.name, format="JPEG"); tmp_path = tmp_file.name
                pdf.image(tmp_path, x=10, y=30, w=190); os.remove(tmp_path)
            elif artwork_url:
                response = requests.get(artwork_url, stream=True, timeout=10)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        for chunk in response.iter_content(1024): tmp_file.write(chunk)
                    pdf.image(tmp_file.name, x=10, y=30, w=190); os.remove(tmp_file.name)
        except Exception: pass
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI Starts Here ---
# ==========================================
st.title("📝 Create / Edit Job Order - Wrap Around Label")

if is_edit_mode: st.warning(f"✏️ **EDIT MODE ACTIVE:** Modifying Order **{active_data.get('order_number')}**. Revision **{target_job_order_no}** will be generated.")
elif is_repeat_mode: st.info(f"🔄 **REPEAT/FETCH MODE ACTIVE:** Auto-filled data based on previous records.")

st.markdown("---")
st.subheader("👤 1. Customer Information")
col_c1, col_c2, col_c3 = st.columns([2, 1, 1])

with col_c1:
    cust_list = ["[ + Add New Customer ]"] + cust_df['customer_name'].tolist() if not cust_df.empty else ["[ + Add New Customer ]"]
    default_cust_name = active_data.get("customer_name", "")
    cust_index = cust_list.index(default_cust_name) if default_cust_name in cust_list else 0
    selected_cust = st.selectbox("Company Name", cust_list, index=cust_index)
    
    if selected_cust == "[ + Add New Customer ]":
        company_name = st.text_input("Enter New Company Name", value=default_cust_name if default_cust_name and default_cust_name not in cust_list else "")
        c_id_val, h_addr_val, h_city_val = active_data.get("customer_id", ""), active_data.get("head_office_address", ""), active_data.get("head_office_city", "")
    else:
        company_name = selected_cust
        row = cust_df[cust_df['customer_name'] == selected_cust].iloc[0]
        c_id_val = str(row['customer_id']) if pd.notna(row['customer_id']) else ""
        h_addr_val = str(row['head_office_address']) if pd.notna(row['head_office_address']) else ""
        h_city_val = str(row['head_office_city']) if pd.notna(row['head_office_city']) else ""

with col_c2: date = st.date_input("Date", datetime.date.today())
with col_c3: job_order_no = st.text_input("Job Order No.", value=target_job_order_no, disabled=True) 

col_addr1, col_addr2, col_addr3 = st.columns(3)
with col_addr1: customer_id = st.text_input("Customer ID", value=c_id_val)
with col_addr2: head_office_address = st.text_input("Head Office Address", value=h_addr_val)
with col_addr3: head_office_city = st.text_input("Head Office City", value=h_city_val)

st.markdown("---")
st.subheader("⚙️ 2. Product Specs")
col_sap1, col_sap2, col_sap3, col_sap4 = st.columns([1.5, 0.8, 1, 1])

with col_sap1: product_code = st.text_input("Product Code", value=active_data.get("product_code", ""))
with col_sap2:
    st.write(" ")
    if st.button("🔍 Fetch Specs", use_container_width=True):
        if product_code:
            res = supabase.table("job_orders").select("*").eq("product_code", product_code).order("id", desc=True).limit(1).execute()
            if res.data:
                freq = supabase.table("job_orders").select("id", count="exact").eq("product_code", product_code).execute()
                count = freq.count if hasattr(freq, 'count') else "multiple"
                last_date = str(res.data[0].get('created_at', '')).split('T')[0]
                st.session_state['repeat_data'] = res.data[0]
                st.success(f"✅ Loaded Specs! (Ordered {count} times. Last on {last_date})")
                st.rerun()
            else: st.info("New code detected.")
with col_sap3: po_number = st.text_input("Customer's PO#", value=active_data.get("customer_po", ""))
with col_sap4: sales_po = st.text_input("Sales PO / Quotation", value=active_data.get("sales_po", "")) # RESTORED: Field 2

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1: material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"], index=safe_idx(["BOPP", "PETG", "PE", "Other"], active_data.get("material_type", "BOPP")))
with col_s2: density = st.selectbox("Density (g/cm3)", [0.91, 0.92, 1.40], index=safe_idx([0.91, 0.92, 1.40], float(active_data.get("density", 0.91)))) 
with col_s3: thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40], index=safe_idx([30, 35, 38, 40], int(active_data.get("thickness_micron", 30))))
with col_s4: colors_no = st.number_input("No. of Colors", min_value=1, max_value=10, value=int(active_data.get("colors_count", 1)))

col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5: width = st.number_input("Label Width (mm)", min_value=0.0, value=float(active_data.get("label_width_mm", 0.0)), key="in_width", on_change=calc_smart_lines) 
with col_s6: repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0, value=float(active_data.get("repeat_length_mm", 0.0)), key="in_repeat", on_change=calc_smart_qty)
with col_s7:
    color_choice = st.selectbox("Color of Film", ["Transparent", "White", "Other"])
    color_of_film = st.text_input("Specify Color:", value=active_data.get("color_of_film", "Transparent")) if color_choice == "Other" else color_choice
with col_s8:
    artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"], index=safe_idx(["NEW", "REPEAT"], active_data.get("artwork_status", "NEW")))
    artwork_no = st.text_input("Artwork No.", value=active_data.get("artwork_number", "")) # RESTORED: Field 1

st.markdown("#### 🧻 Print, Core & Winding")
col_w1, col_w2, col_d1, col_d2, col_d4 = st.columns(5)
with col_w1: print_position = st.selectbox("Print Surface", ["Reverse Print", "Surface Print"], index=safe_idx(["Reverse Print", "Surface Print"], active_data.get("print_surface", "Reverse Print")))
with col_w2: final_format = st.selectbox("Final Format", ["Roll", "Cut (Pieces)"], index=safe_idx(["Roll", "Cut (Pieces)"], active_data.get("final_format", "Roll")))
with col_d1: inner_core = st.selectbox("Inner Core", ["3 inch", "6 inch"], index=safe_idx(["3 inch", "6 inch"], active_data.get("inner_core", "6 inch")))
with col_d2: core_wall_thickness = st.number_input("Wall Thickness (mm)", min_value=0.0, value=float(active_data.get("core_wall_thickness_mm", 0.0))) # RESTORED: Field 3
with col_d4: winding_direction = st.selectbox("Winding Direction", ["Clockwise #4", "Anti-clockwise #3"], index=safe_idx(["Clockwise #4", "Anti-clockwise #3"], active_data.get("winding_direction", "Clockwise #4")))

st.markdown("#### 🧮 Smart Web Calculator")
col_edge, col_calc1, col_calc_rolls = st.columns(3)
with col_edge: edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0.0, value=float(active_data.get("edge_trim_mm", 24.0)), key="in_edge", on_change=calc_smart_lines)
with col_calc1: mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0.0, value=float(active_data.get("mother_roll_length_m", 0.0)), key="in_mr_len", on_change=calc_smart_qty)
with col_calc_rolls: no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=int(active_data.get("no_of_rolls", 1)), key="in_rolls", on_change=calc_smart_qty)

col_calc2, col_calc3, col_calc4 = st.columns(3)
with col_calc2: mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0.0, value=float(active_data.get("mother_roll_width_mm", 0.0)), key="in_mr_width", on_change=calc_smart_lines)
with col_calc3: no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, key="in_lines", on_change=calc_smart_qty)
with col_calc4: core_type = st.selectbox("Core Type", ["Paper", "Plastic"], index=safe_idx(["Paper", "Plastic"], active_data.get("core_type", "Paper")))

width_error = False
required_roll_width = (width * no_of_lines) + edge_trim
if mother_roll_width > 0 and required_roll_width > mother_roll_width:
    st.error(f"❌ Engineering Alert: Required width ({required_roll_width} mm) exceeds Mother Roll Width ({mother_roll_width} mm).")
    width_error = True

st.markdown("---")
st.subheader("📦 3. Quantity, Delivery & Artwork")

col_q1, col_q2, col_q3 = st.columns(3) 
with col_q1: quantity = st.number_input("Required Quantity (PCS)", min_value=0, step=1000, key="in_qty") 
with col_q2:
    delivery_city = st.text_input("Delivery City", value=active_data.get("delivery_city", "")) 
    delivery_address = st.text_input("Delivery Address", value=active_data.get("delivery_address", "")) # RESTORED: Field 4
with col_q3:
    due_date = st.date_input("Due Date", datetime.datetime.strptime(active_data["due_date"], "%Y-%m-%d").date() if active_data.get("due_date") else datetime.date.today())
    packaging_notes = st.text_input("Packaging Notes", value=active_data.get("packaging_notes", "As Usual")) # RESTORED: Field 5

if width > 0 and repeat_length > 0 and thickness > 0 and quantity > 0:
    net_weight_kg = (width / 1000) * (repeat_length / 1000) * thickness * density * quantity / 1000
    st.info(f"⚖️ **Estimated Net Weight:** {net_weight_kg:,.2f} KG")
else: st.info("⚖️ **Estimated Net Weight:** 0.00 KG")

MAX_FILE_SIZE_MB = 2
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
uploaded_design = st.file_uploader(f"🖼️ Upload Approved Design (Max {MAX_FILE_SIZE_MB}MB, will be compressed)", type=["jpg", "jpeg", "png"])
existing_artwork_url = active_data.get('artwork_url', "")

if uploaded_design is not None:
    if uploaded_design.size > MAX_FILE_SIZE_BYTES: st.error(f"❌ File is too large! Max allowed size is {MAX_FILE_SIZE_MB} MB.")
    else: st.image(uploaded_design, caption="New Artwork (Size OK)", width=200)
elif existing_artwork_url and str(existing_artwork_url).startswith("http"):
    st.success("🔄 USING EXISTING DESIGN")
    try: st.image(existing_artwork_url, caption="Existing design", width=200)
    except: pass

notes = st.text_area("Remarks / Notes", value=active_data.get("remarks", ""))

pdf_data = {
    "Date": str(date), "Job Order No": target_job_order_no, "Customer Name": company_name, "Customer ID": customer_id,
    "Customer PO#": po_number, "Sales PO / Quotation": sales_po, "Product Code": product_code,          
    "Head Office Address": head_office_address, "Head Office City": head_office_city,
    "Delivery Address": delivery_address, "Delivery City": delivery_city, 
    "Product Type": "BOPP Wrap Around Label", "Material Type": material_type, "Density (g/cm3)": str(density),     
    "Label/Film Width (mm)": str(width), "Repeat Length (mm)": str(repeat_length), "Thickness (u)": str(thickness),
    "Colors": str(colors_no), "Color of Film": color_of_film, "Artwork Status": artwork, "Artwork No.": artwork_no,
    "Print Surface": print_position, "Final Format": final_format, "Inner Core": inner_core, "Core Type": core_type,                 
    "Wall Thickness (mm)": str(core_wall_thickness), "Winding Direction": winding_direction,
    "Mother Roll Width (mm)": str(mother_roll_width), "Edge Trim (mm)": str(edge_trim),
    "Required Quantity": str(quantity), "Packaging": packaging_notes, "Due Date": str(due_date), "Remarks / Notes": notes
}

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🎯 Actions")
btn_col1, btn_col2, btn_col3 = st.columns(3) 

with btn_col1:
    save_btn_text = "🔄 Update Order (Revision)" if is_edit_mode else "💾 Save to Cloud & Send"
    if st.button(save_btn_text, type="primary", use_container_width=True):
        if uploaded_design is not None and uploaded_design.size > MAX_FILE_SIZE_BYTES: st.error("❌ Artwork too large.")
        elif width_error: st.error("❌ Fix width calculations.")
        elif not company_name or company_name == "[ + Add New Customer ]": st.error("❌ Valid Customer Name required.")
        else:
            with st.spinner("Processing & Compressing Image..."):
                try:
                    final_url_to_save = existing_artwork_url
                    if uploaded_design is not None:
                        compressed_buffer = compress_image(uploaded_design)
                        file_name = f"{target_job_order_no}.jpg"
                        try:
                            supabase.storage.from_('artworks').upload(path=file_name, file=compressed_buffer.getvalue(), file_options={"content-type": "image/jpeg"})
                            final_url_to_save = supabase.storage.from_('artworks').get_public_url(file_name)
                        except Exception as e: st.warning(f"Upload warning: {e}")

                    db_data = {
                        "order_number": target_job_order_no, "customer_name": company_name, "customer_po": po_number, "sales_po": sales_po,
                        "customer_id": customer_id, "head_office_address": head_office_address, "head_office_city": head_office_city,
                        "delivery_address": delivery_address, "delivery_city": delivery_city, "product_type": "BOPP Wrap Around Label",
                        "product_code": product_code, "material_type": material_type, "density": float(density), "thickness_micron": float(thickness),
                        "label_width_mm": float(width), "repeat_length_mm": float(repeat_length), "color_of_film": color_of_film,
                        "colors_count": int(colors_no), "artwork_status": artwork, "artwork_number": artwork_no, "artwork_url": final_url_to_save,
                        "print_surface": print_position, "final_format": final_format, "inner_core": inner_core, "core_type": core_type,
                        "core_wall_thickness_mm": float(core_wall_thickness), "winding_direction": winding_direction,
                        "mother_roll_length_m": float(mother_roll_length), "no_of_rolls": int(no_of_rolls), "no_of_lines": int(no_of_lines),
                        "mother_roll_width_mm": float(mother_roll_width), "edge_trim_mm": float(edge_trim), "required_quantity": int(quantity),
                        "packaging_notes": packaging_notes, "due_date": str(due_date), "remarks": notes, "status": "pending"
                    }
                    if is_edit_mode:
                        supabase.table("job_orders").update(db_data).eq("id", active_data["id"]).execute()
                        st.success(f"✅ UPDATED: {target_job_order_no}")
                    else:
                        supabase.table("job_orders").insert(db_data).execute()
                        st.success(f"✅ SAVED: {target_job_order_no}"); st.balloons()
                    
                    for k in ['repeat_data', 'edit_data']:
                        if k in st.session_state: del st.session_state[k]
                except Exception as e: st.error(f"❌ DB Error: {e}")

with btn_col2:
    pdf_url = existing_artwork_url if uploaded_design is None else None
    pdf_file = create_pdf(pdf_data, image_file=uploaded_design, artwork_url=pdf_url, stamp_name=current_user_name)
    st.download_button(label="📄 Export PDF (w/ QR)", data=pdf_file, file_name=f"{target_job_order_no}.pdf", mime="application/pdf", use_container_width=True)

with btn_col3:
    if st.button("🗑️ Reset Form / Exit", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["authenticated", "role", "user_id"]: del st.session_state[key]
        st.rerun()
