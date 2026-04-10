import streamlit as st
import datetime
import pandas as pd
import io
import tempfile
import os
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
auth.require_role(["sales"])
auth.logout_button()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 14 - FlexoBrain Logic Fix & UI Cleanup</div>", unsafe_allow_html=True)

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
# --- Auto-generate Job Order Number Logic ---
# ==========================================
def generate_order_number(supabase_client):
    today_str = datetime.date.today().strftime("%Y%m%d")
    prefix = f"BOPP-{today_str}-"
    try:
        response = supabase_client.table("job_orders").select("order_number").execute()
        seqs = []
        for row in response.data:
            if row.get('order_number', '').startswith(prefix):
                try:
                    seq = int(row['order_number'].split('-')[-1])
                    seqs.append(seq)
                except:
                    pass
        next_seq = max(seqs) + 1 if seqs else 1
        return f"{prefix}{next_seq:03d}"
    except Exception as e:
        return f"{prefix}999"

auto_job_order_no = generate_order_number(supabase)

# ==========================================
# --- Functions for PDF Generation ---
# ==========================================
def create_pdf(data_dict, image_file=None, artwork_url=None):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"FlexoBrain Job Order: {data_dict.get('Job Order No')}", ln=True, align='C')
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
    row_full("Delivery Address / City", data_dict.get("Delivery Address"))
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
    row_full("Packaging Notes", data_dict.get("Packaging"))
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    
    # --- Stamp ---
    pdf.ln(8)
    current_y = pdf.get_y()
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, current_y, 190, 35, 'F')
    pdf.set_xy(15, current_y + 5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 6, "[ APPROVED ] Digitally Approved & Sealed", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    current_time = datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")
    user_name = "Eng. Amro"
    pdf.set_x(15)
    pdf.cell(0, 6, f"By: {user_name}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"Timestamp: {current_time}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"System ID: {data_dict.get('Job Order No')}", ln=True)

    # --- Page 2 Artwork ---
    if image_file is not None or (artwork_url and str(artwork_url).startswith("http")):
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C')
        pdf.ln(5)
        if image_file:
            img = Image.open(image_file).convert('RGB')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_path = tmp_file.name
                img.save(tmp_path, format="JPEG")
            pdf.image(tmp_path, x=10, y=30, w=190)
            os.remove(tmp_path)
        else:
            pdf.image(artwork_url, x=10, y=30, w=190)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI ---
# ==========================================
st.title("📝 Create New Job Order")

old_order = st.session_state.get('repeat_data', {})
if old_order:
    st.info(f"🔄 Repeat Mode Active: Auto-filling based on {old_order.get('order_number')}")

st.markdown("---")
st.subheader("👤 1. Customer Information")
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", datetime.date.today())
    company_name = st.text_input("Company Name", value=old_order.get("customer_name", ""))
with col2:
    job_order_no = st.text_input("Job Order No.", value=auto_job_order_no, disabled=True) 
    customer_id = st.text_input("Customer ID", value=old_order.get("customer_id", ""))
with col3:
    po_number = st.text_input("Customer's PO#") 
    sales_po = st.text_input("Sales PO#") 

col_addr1, col_addr2, col_city = st.columns([2, 2, 1])
with col_addr1:
    head_office_address = st.text_input("Head Office Address")
with col_addr2:
    delivery_address = st.text_input("Delivery Address")
with col_city:
    delivery_city = st.text_input("Delivery City", value=old_order.get("delivery_city", ""))

st.markdown("---")
st.subheader("⚙️ 2. Product Specs")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)", value=old_order.get("product_code", ""))
with col_s2:
    mat_ops = ["BOPP", "PETG", "PE", "Other"]
    material_type = st.selectbox("Material Type", mat_ops, index=safe_idx(mat_ops, old_order.get("material_type", "BOPP")))
with col_s3:
    density = st.selectbox("Density", [0.91, 0.92, 1.40], index=safe_idx([0.91, 0.92, 1.40], float(old_order.get("density", 0.91))))
with col_s4:
    thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40], index=safe_idx([30, 35, 38, 40], int(old_order.get("thickness_micron", 30))))

col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Label Width (mm)", min_value=0.0, value=float(old_order.get("label_width_mm", 0.0))) 
with col_s6:
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0, value=float(old_order.get("repeat_length_mm", 0.0)))
with col_s7:
    color_of_film = st.text_input("Film Color", value=old_order.get("color_of_film", "Transparent"))
with col_s8:
    colors_no = st.number_input("No. of Colors", min_value=1, value=int(old_order.get("colors_count", 1)))

st.markdown("#### 🧮 Smart Web & Production Calculator")
col_calc1, col_calc_rolls, col_calc2, col_calc3 = st.columns(4)
with col_calc1:
    mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0.0, value=float(old_order.get("mother_roll_length_m", 0.0)))
with col_calc_rolls:
    no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=int(old_order.get("no_of_rolls", 1)))
with col_calc2:
    mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0.0, value=float(old_order.get("mother_roll_width_mm", 0.0)))
with col_calc3:
    no_of_lines = st.number_input("No. of Lines", min_value=1, value=int(old_order.get("no_of_lines", 1)))

edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0.0, value=float(old_order.get("edge_trim_mm", 24.0)))

# Calculations
pcs_per_roll = int((mother_roll_length * 1000) / repeat_length) if mother_roll_length > 0 and repeat_length > 0 else 0
total_labels_calculated = pcs_per_roll * no_of_lines * no_of_rolls
st.info(f"💡 Calculated Total Quantity: **{total_labels_calculated:,}** PCS")

st.markdown("---")
st.subheader("📦 3. Quantity, Delivery & Artwork")

# --- Design ---
uploaded_design = st.file_uploader("🖼️ Upload NEW Design", type=["jpg", "jpeg", "png"])
final_artwork_path_for_db = ""
if uploaded_design:
    st.image(uploaded_design, width=200)
    final_artwork_path_for_db = "new_upload"
elif old_order.get('artwork_url'):
    st.success("🔄 USING EXISTING DESIGN")
    st.image(old_order.get('artwork_url'), width=200)
    final_artwork_path_for_db = old_order.get('artwork_url')

# --- REQUIRED QUANTITY (Sync Logic) ---
# We use the calculator result as a 'value' to sync it live
quantity = st.number_input("Required Quantity", min_value=0, value=total_labels_calculated, step=1000) 

col_q1, col_q2 = st.columns(2)
with col_q1:
    packaging = st.text_input("Packaging Notes", value=old_order.get("packaging_notes", "Suitable / As Usual"))
with col_q2:
    due_date = st.date_input("Due Date", datetime.date.today())

notes = st.text_area("Remarks / Notes")

# Actions
if st.button("💾 Save to Cloud & Send", type="primary"):
    if not company_name:
        st.error("❌ Customer Name is required.")
    else:
        try:
            fresh_no = generate_order_number(supabase)
            db_data = {
                "order_number": fresh_no, "customer_name": company_name, "customer_po": po_number,
                "sales_po": sales_po, "customer_id": customer_id, "delivery_city": delivery_city,
                "product_type": "BOPP Wrap Around Label", "product_code": product_code,
                "material_type": material_type, "density": float(density), "thickness_micron": float(thickness),
                "label_width_mm": float(width), "repeat_length_mm": float(repeat_length),
                "color_of_film": color_of_film, "colors_count": int(colors_no), "artwork_url": final_artwork_path_for_db,
                "mother_roll_length_m": float(mother_roll_length), "no_of_rolls": int(no_of_rolls),
                "no_of_lines": int(no_of_lines), "mother_roll_width_mm": float(mother_roll_width),
                "edge_trim_mm": float(edge_trim), "required_quantity": int(quantity),
                "packaging_notes": packaging, "due_date": str(due_date), "remarks": notes, "status": "pending"
            }
            supabase.table("job_orders").insert(db_data).execute()
            st.success(f"✅ Order {fresh_no} Saved!")
            if 'repeat_data' in st.session_state: del st.session_state['repeat_data']
        except Exception as e:
            st.error(f"❌ Error: {e}")

# PDF Export
pdf_data = {
    "Job Order No": job_order_no, "Date": str(date), "Customer Name": company_name,
    "Customer ID": customer_id, "Customer PO#": po_number, "Sales PO#": sales_po,
    "Delivery Address": f"{delivery_address}, {delivery_city}", "Product Type": "BOPP Label",
    "Material Type": material_type, "Thickness (u)": str(thickness), "Density (g/cm3)": str(density),
    "Mother Roll Width (mm)": str(mother_roll_width), "Edge Trim (mm)": str(edge_trim),
    "Label/Film Width (mm)": str(width), "Repeat Length (mm)": str(repeat_length),
    "Colors": str(colors_no), "Color of Film": color_of_film, "Artwork Status": "REPEAT" if old_order else "NEW",
    "Artwork No.": old_order.get("artwork_number", "N/A"), "Print Surface": "Reverse", "Final Format": "Roll",
    "Inner Core": "6 inch", "Core Type": "Paper", "Wall Thickness (mm)": "12", "Winding Direction": "#4",
    "Required Quantity": str(quantity), "Due Date": str(due_date), "Packaging": packaging, "Remarks / Notes": notes
}

st.download_button("📄 Export PDF", data=create_pdf(pdf_data, uploaded_design, final_artwork_path_for_db), file_name=f"{job_order_no}.pdf")
