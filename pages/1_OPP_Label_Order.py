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
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 10 - FlexoBrain Digital Stamp & Validation</div>", unsafe_allow_html=True)

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
def create_pdf(data_dict, image_file=None):
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
    row_full("Delivery Address", data_dict.get("Delivery Address"))
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
    row_2_cols("Packaging", data_dict.get("Packaging"), "Delivery City", data_dict.get("Delivery City"))
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    
    # ==========================================
    # --- THE DIGITAL STAMP ---
    # ==========================================
    pdf.ln(8)
    current_y = pdf.get_y()
    
    # Draw stamp background (light gray rectangle)
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, current_y, 190, 35, 'F')
    
    # Approval mark
    pdf.set_xy(15, current_y + 5)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 128, 0) # Green for approval
    pdf.cell(0, 6, "[ APPROVED ] Digitally Approved & Sealed", ln=True)
    
    # Retrieve automated data
    pdf.set_text_color(0, 0, 0) # Return to black
    pdf.set_font("Arial", '', 10)
    
    current_time = datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")
    user_name = "Eng. Amro" # Hardcoded as requested
    order_number = data_dict.get("Job Order No")
    
    pdf.set_x(15)
    pdf.cell(0, 6, f"By: {user_name}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"Timestamp: {current_time}", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 6, f"System ID: {order_number}", ln=True)

    # ==========================================
    # --- PAGE 2: ARTWORK (If uploaded) ---
    # ==========================================
    if image_file is not None:
        try:
            img = Image.open(image_file).convert('RGB')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_path = tmp_file.name
                img.save(tmp_path, format="JPEG")

            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C')
            pdf.ln(5)
            pdf.image(tmp_path, x=10, y=30, w=190)
            os.remove(tmp_path)
        except Exception:
            pass

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI Starts Here ---
# ==========================================
st.title("📝 Create New Job Order")
st.markdown("---")

st.subheader("👤 1. Customer Information")
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", datetime.date.today(), key="in_date")
    company_name = st.text_input("Company Name", key="in_company")
with col2:
    job_order_no = st.text_input("Job Order No.", value=auto_job_order_no, disabled=True) 
    customer_id = st.text_input("Customer ID", key="in_cust_id")
with col3:
    po_number = st.text_input("Customer's PO#", key="in_po")
    sales_po = st.text_input("Sales PO#", key="in_sales_po")

col_addr1, col_addr2 = st.columns(2)
with col_addr1:
    head_office_address = st.text_input("Company Head Office Address", key="in_addr1")
with col_addr2:
    delivery_address = st.text_input("Delivery Address", key="in_addr2")
st.markdown("---")

st.subheader("⚙️ 2. Product Specs")
st.text_input("Product Type", value="BOPP Wrap Around Label", disabled=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)", key="in_prod_code")
with col_s2:
    material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"], key="in_mat_type")
with col_s3:
    density = st.selectbox("Density (g/cm3)", [0.91, 0.92, 1.40], key="in_density") 
with col_s4:
    thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40], key="in_thick")

col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Label Width (mm)", min_value=0.0, key="in_width") 
with col_s6:
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0, key="in_repeat")
with col_s7:
    color_choice = st.selectbox("Color of Film", ["Transparent", "White", "Other"], key="in_color_choice")
    color_of_film = st.text_input("Specify Color:", key="in_spec_color") if color_choice == "Other" else color_choice
with col_s8:
    colors_no = st.number_input("No. of Colors", min_value=1, max_value=10, key="in_color_no")

col_s9, col_s10 = st.columns(2)
with col_s9:
    artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"], key="in_art_stat")
with col_s10:
    artwork_no = st.text_input("Artwork No.", key="in_art_no") 

st.markdown("#### 🧻 Print, Core & Winding Specifications")
col_w1, col_w2 = st.columns(2)
with col_w1:
    print_position = st.selectbox("Print Surface", ["Reverse Print", "Surface Print"], key="in_print_surf")
with col_w2:
    final_format = st.selectbox("Final Product Format", ["Roll", "Cut (Pieces)"], key="in_final_form")

col_d1, col_d2, col_d3, col_d4 = st.columns(4)
with col_d1:
    inner_core = st.selectbox("Inner Core", ["3 inch", "6 inch"], index=1, key="in_inner_core")
with col_d2:
    core_type = st.selectbox("Core Type", ["Paper", "Plastic"], key="in_core_type")
with col_d3:
    core_thickness = st.number_input("Wall Thickness (mm)", min_value=0.0, key="in_core_thick")
with col_d4:
    winding_direction = st.selectbox("Winding Direction", ["Clockwise #4", "Anti-clockwise #3"], key="in_wind_dir")

st.markdown("#### 🧮 Smart Web & Production Calculator")
col_calc1, col_calc_rolls, col_calc2, col_calc3 = st.columns(4)
with col_calc1:
    mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0, key="in_mr_len")
with col_calc_rolls:
    no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=1, key="in_rolls")
with col_calc2:
    mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0.0, key="in_mr_width")
with col_calc3:
    no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1, key="in_lines")
    
col_calc4, col_calc5, col_calc6, col_calc7 = st.columns(4)
with col_calc4:
    edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0.0, value=24.0, key="in_edge")

pcs_per_roll = int((mother_roll_length * 1000) / repeat_length) if mother_roll_length > 0 and repeat_length > 0 else 0
with col_calc5:
    st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
    
waste_by_mm = float(mother_roll_width - (width * no_of_lines)) if mother_roll_width > 0 and width > 0 and no_of_lines > 0 else 0.0
unused_waste = float(waste_by_mm - edge_trim) if waste_by_mm > 0 else 0.0

with col_calc6:
    st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
with col_calc7:
    st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

# Validation Error for Width
width_error = False
required_roll_width = (width * no_of_lines) + edge_trim
if mother_roll_width > 0 and required_roll_width > mother_roll_width:
    st.error(f"❌ Engineering Alert: Required production width ({required_roll_width} mm) exceeds Mother Roll Width ({mother_roll_width} mm). Please reduce No. of Lines or adjust widths.")
    width_error = True

total_labels_calculated = 0
if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0 and no_of_rolls > 0:
    total_labels_calculated = pcs_per_roll * no_of_lines * no_of_rolls
    st.info(f"💡 Calculated Total Quantity: **{total_labels_calculated:,}** PCS")

st.markdown("---")
st.subheader("📦 3. Quantity, Delivery & Artwork")

uploaded_design = st.file_uploader("🖼️ Upload Approved Design", type=["jpg", "jpeg", "png"], key="in_upload")

col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
with col_q1:
    quantity = st.number_input("Required Quantity", min_value=0, key="in_qty") 
with col_q2:
    packaging = st.text_input("Packaging", value="Suitable / As Usual", key="in_pack")
with col_q3:
    due_date = st.date_input("Due Date", datetime.date.today(), key="in_due")
with col_q4:
    delivery_city = st.text_input("Delivery City", key="in_city") 

notes = st.text_area("Remarks / Notes", key="in_notes")

# PDF Data Dictionary
pdf_data = {
    "Date": str(date),
    "Job Order No": job_order_no,
    "Customer Name": company_name,
    "Customer ID": customer_id,
    "Customer PO#": po_number,
    "Sales PO#": sales_po,          
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
    if st.button("💾 Save to Cloud & Send", type="primary", use_container_width=True):
        if width_error:
            st.error("❌ Cannot save. Please fix the width calculation errors first.")
        elif not company_name:
            st.error("❌ Please enter Customer Name before saving.")
        else:
            try:
                # 1. Generate Fresh Number on Save
                fresh_order_no = generate_order_number(supabase)
                
                # Prepare data exactly matching Supabase columns
                db_data = {
                    "order_number": fresh_order_no,
                    "customer_name": company_name,
                    "customer_po": po_number,
                    "sales_po": sales_po,
                    "customer_id": customer_id,
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
                    "print_surface": print_position,
                    "final_format": final_format,
                    "inner_core": inner_core,
                    "core_type": core_type,
                    "core_wall_thickness_mm": float(core_thickness) if core_thickness else 0.0,
                    "winding_direction": winding_direction,
                    "mother_roll_width_mm": float(mother_roll_width) if mother_roll_width else 0.0,
                    "edge_trim_mm": float(edge_trim) if edge_trim else 0.0,
                    "required_quantity": int(quantity) if quantity else 0,
                    "packaging_notes": packaging,
                    "due_date": str(due_date),
                    "remarks": notes,
                    "status": "pending"
                }
                
                # Insert command
                response = supabase.table("job_orders").insert(db_data).execute()
                
                st.success(f"✅ Order successfully saved to Cloud Database as {fresh_order_no}!")
                st.toast("✅ Sent to Production Board!", icon="☁️")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Database Error: {str(e)}")

with btn_col2:
    pdf_file = create_pdf(pdf_data, image_file=uploaded_design)
    st.download_button(
        label="📄 Export PDF",
        data=pdf_file,
        file_name=f"{job_order_no}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with btn_col3:
    if st.button("🗑️ Reset Form", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["authenticated", "role"]:
                del st.session_state[key]
        st.rerun()
