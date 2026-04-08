import streamlit as st
import datetime
import pandas as pd
import io
import tempfile
import os
from fpdf import FPDF
import sys
from pathlib import Path
from PIL import Image  # 🆕 استدعاء مكتبة معالجة الصور

# --- Page configuration ---
st.set_page_config(page_title="OPP Label Order", page_icon="📝", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth

if not auth.check_password():
    st.stop()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 05 - 2026-04-08</div>", unsafe_allow_html=True)

# ==========================================
# --- Main System Code Starts Here ---
# ==========================================

# --- Functions for PDF Generation (Structured & 2 Pages) ---
def create_pdf(data_dict, image_file=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Sales Job Order - OPP Label", ln=True, align='C')
    pdf.ln(2)
    
    # Helper functions for structured layout
    def safe_txt(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')
        
    def section_header(title):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220) # Light Gray background
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

    # --- Section 1: Order Info ---
    section_header("1. Order Information")
    row_2_cols("Job Order No", data_dict.get("Job Order No"), "Date", data_dict.get("Date"))
    row_2_cols("Customer Name", data_dict.get("Customer Name"), "Customer PO#", data_dict.get("Customer PO#"))
    row_2_cols("Sales PO#", data_dict.get("Sales PO#"), "Customer ID", data_dict.get("Customer ID"))
    row_full("Delivery Address", data_dict.get("Delivery Address"))
    pdf.ln(2)

    # --- Section 2: Material Specs ---
    section_header("2. Material Specifications")
    row_2_cols("Product Type", data_dict.get("Product Type"), "Material Type", data_dict.get("Material Type"))
    row_2_cols("Thickness (u)", data_dict.get("Thickness (u)"), "Density", data_dict.get("Density (g/cm3)"))
    row_2_cols("Mother Roll Width", data_dict.get("Mother Roll Width (mm)"), "Target Edge Trim", data_dict.get("Edge Trim (mm)"))
    pdf.ln(2)

    # --- Section 3: Print & Dimensions ---
    section_header("3. Print & Dimensions")
    row_2_cols("Label Width (mm)", data_dict.get("Label/Film Width (mm)"), "Repeat Length (mm)", data_dict.get("Repeat Length (mm)"))
    row_2_cols("No. of Colors", data_dict.get("Colors"), "Film Color", data_dict.get("Color of Film"))
    row_2_cols("Artwork Status", data_dict.get("Artwork Status"), "Artwork No.", data_dict.get("Artwork No."))
    pdf.ln(2)

    # --- Section 4: Winding & Core (تم إضافة سُمك القلب هنا) ---
    section_header("4. Print, Winding & Core")
    row_2_cols("Print Surface", data_dict.get("Print Surface"), "Final Format", data_dict.get("Final Format"))
    row_2_cols("Inner Core", data_dict.get("Inner Core"), "Core Type", data_dict.get("Core Type"))
    row_2_cols("Wall Thickness (mm)", data_dict.get("Wall Thickness (mm)"), "Winding Direction", data_dict.get("Winding Direction"))
    pdf.ln(2)

    # --- Section 5: Quantity & Delivery ---
    section_header("5. Quantity & Delivery")
    row_2_cols("Required QTY", data_dict.get("Required Quantity"), "Due Date", data_dict.get("Due Date"))
    row_2_cols("Packaging", data_dict.get("Packaging"), "Delivery City", data_dict.get("Delivery City"))
    row_full("Remarks / Notes", data_dict.get("Remarks / Notes"))
    pdf.ln(4)

    # --- Section 6: Signatures ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(47.5, 8, "Sales", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "Production", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "QC", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "Manager", border=1, align='C', fill=True, ln=True)
    
    pdf.cell(47.5, 15, "", border=1)
    pdf.cell(47.5, 15, "", border=1)
    pdf.cell(47.5, 15, "", border=1)
    pdf.cell(47.5, 15, "", border=1, ln=True)

    # --- PAGE 2: Attached Design (معالجة الصور القوية) ---
    if image_file is not None:
        try:
            # 🆕 فتح الصورة باستخدام Pillow وتحويلها إلى RGB لضمان التوافق التام وإزالة أي شفافية (PNG)
            img = Image.open(image_file).convert('RGB')
            
            # إنشاء ملف مؤقت بصيغة JPG لتستطيع FPDF قراءته
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_path = tmp_file.name
                img.save(tmp_path, format="JPEG")

            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Page 2: Approved Artwork / Design", ln=True, align='C')
            pdf.ln(5)
            
            # وضع الصورة (w=190 يجعلها تملأ عرض الصفحة بشكل ممتاز)
            pdf.image(tmp_path, x=10, y=30, w=190)
            
            # تنظيف السيرفر من الملف المؤقت
            os.remove(tmp_path)
        except Exception as e:
            pdf.add_page()
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Notice: Could not load the image. System Error: {str(e)}", ln=True)

    return pdf.output(dest='S').encode('latin-1')


st.title("📝 Create New Job Order - OPP Label")
st.markdown("---")

# 1. Customer Information
st.subheader("👤 1. Customer Information")
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", datetime.date.today())
    company_name = st.text_input("Company Name")
with col2:
    job_order_no = st.text_input("Job Order No.", placeholder="Auto-generated on save", disabled=True) 
    customer_id = st.text_input("Customer ID")
with col3:
    po_number = st.text_input("Customer's PO#")
    sales_po = st.text_input("Sales PO#")

col_addr1, col_addr2 = st.columns(2)
with col_addr1:
    head_office_address = st.text_input("Company Head Office Address")
with col_addr2:
    delivery_address = st.text_input("Delivery Address")
st.markdown("---")

# 2. Product Specs 
st.subheader("⚙️ 2. Product Specs")
st.text_input("Product Type", value="OPP Label (Wrap Around)", disabled=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)")
with col_s2:
    material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"])
with col_s3:
    density = st.selectbox("Density (g/cm3)", [0.91, 0.92, 1.40]) 
with col_s4:
    thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40])

col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Label Width (mm)", min_value=0.0) 
with col_s6:
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
with col_s7:
    color_choice = st.selectbox("Color of Film", ["Transparent", "White", "Other"])
    color_of_film = st.text_input("Specify Color:") if color_choice == "Other" else color_choice
with col_s8:
    colors_no = st.number_input("No. of Colors in Printing", min_value=1, max_value=10)

col_s9, col_s10 = st.columns(2)
with col_s9:
    artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"])
with col_s10:
    artwork_no = st.text_input("Artwork No.") 

# 3. Dynamic Section
st.markdown("### 🔄 Specific Specs for: OPP Label")
st.markdown("#### 🧻 Print, Core & Winding Specifications")

col_w1, col_w2 = st.columns(2)
with col_w1:
    print_position = st.selectbox("Print Surface", ["Reverse Print", "Surface Print"])
with col_w2:
    final_format = st.selectbox("Final Product Format", ["Roll", "Cut (Pieces)"])

col_d1, col_d2, col_d3, col_d4 = st.columns(4)
with col_d1:
    inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"], index=1)
with col_d2:
    core_type = st.selectbox("Core Type", ["Paper", "Plastic"])
with col_d3:
    core_thickness = st.number_input("Wall Thickness (mm)", min_value=0.0)
with col_d4:
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])

# Smart Calculator
st.markdown("#### 🧮 Smart Web & Production Calculator")
col_calc1, col_calc_rolls, col_calc2, col_calc3 = st.columns(4)
with col_calc1:
    mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
with col_calc_rolls:
    no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=1)
with col_calc2:
    mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
with col_calc3:
    no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)
    
col_calc4, col_calc5, col_calc6, col_calc7 = st.columns(4)
with col_calc4:
    edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0, value=24)

pcs_per_roll = int((mother_roll_length * 1000) / repeat_length) if mother_roll_length > 0 and repeat_length > 0 else 0
with col_calc5:
    st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
    
waste_by_mm = float(mother_roll_width - (width * no_of_lines)) if mother_roll_width > 0 and width > 0 and no_of_lines > 0 else 0.0
unused_waste = float(waste_by_mm - edge_trim) if waste_by_mm > 0 else 0.0

with col_calc6:
    st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
with col_calc7:
    st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

total_labels_calculated = 0
if mother_roll_width > 0 and width > 0 and no_of_lines > 0:
    required_width = (width * no_of_lines) + edge_trim
    if required_width > mother_roll_width:
        st.error(f"🚨 **GEOMETRY ERROR:** Required width is **{required_width} mm**, but Mother Roll is only **{mother_roll_width} mm**!")
    elif required_width < mother_roll_width:
        st.warning(f"⚠️ **WIDTH WARNING:** You have **{unused_waste} mm** of UNUSED waste.")
    else:
        st.info(f"✅ **PERFECT FIT:** Required width exactly matches the Mother Roll.")

if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0 and no_of_rolls > 0:
    total_labels_calculated = pcs_per_roll * no_of_lines * no_of_rolls
    st.success(f"**💡 Production Estimate for {no_of_rolls} Mother Roll(s):** Total Exact Quantity: **{total_labels_calculated:,}** PCS")

st.markdown("---")

# 4. Quantity, Delivery & Artwork Upload
st.subheader("📦 3. Quantity, Delivery & Artwork")

# NEW: Artwork Upload feature
uploaded_design = st.file_uploader("🖼️ Upload Approved Design / Artwork (JPG or PNG)", type=["jpg", "jpeg", "png"])
if uploaded_design:
    st.success("Design attached successfully! It will appear on Page 2 of the PDF.")

col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
with col_q1:
    quantity = st.number_input("Required Quantity by Customer", min_value=0) 
    if quantity > 0 and total_labels_calculated > 0 and quantity != total_labels_calculated:
        st.markdown(f"<p style='color:red; font-size:14px; font-weight:bold;'>🚨 WARNING: Requested Quantity ({quantity:,}) does NOT match Calculated Production ({total_labels_calculated:,})!</p>", unsafe_allow_html=True)
with col_q2:
    packaging = st.text_input("Packaging", value="Suitable / As Usual")
with col_q3:
    due_date = st.date_input("Due Date of Order", datetime.date.today())
with col_q4:
    delivery_city = st.text_input("Delivery City") 

notes = st.text_area("Remarks / Notes", placeholder="Enter any specific notes or instructions here...")

# Data Collection
job_data = {
    "Date": str(date),
    "Job Order No": job_order_no,
    "Customer Name": company_name,
    "Customer ID": customer_id,
    "Customer PO#": po_number,
    "Sales PO#": sales_po,          
    "Head Office Address": head_office_address,
    "Delivery Address": delivery_address,
    "Delivery City": delivery_city, 
    "Product Type": "OPP Label (Wrap Around)",
    "Product Code": product_code,
    "Material Type": material_type, 
    "Density (g/cm3)": density,     
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

# Actions
st.subheader("🎯 Actions")
btn_col1, btn_col2 = st.columns(2) 

with btn_col1:
    if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
        st.success("OPP Job Order saved successfully! Ready for production review.")
        
with btn_col2:
    pdf_file = create_pdf(job_data, image_file=uploaded_design)
    st.download_button(
        label="📄 Export to PDF",
        data=pdf_file,
        file_name="OPP_Job_Order.pdf",
        mime="application/pdf",
        use_container_width=True
    )
