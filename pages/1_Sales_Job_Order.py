import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: Final Refined SVG Drawing (Includes Item Data Inside) ---
def draw_final_svg(item_n, item_f, direction_t):
    # Centered and clean SVG to prevent cropping
    svg = f"""
    <svg width="320" height="200" viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="5" width="310" height="190" rx="10" fill="white" stroke="#1e3a8a" stroke-width="2"/>
        
        <rect x="180" y="15" width="125" height="30" rx="5" fill="#1e3a8a" />
        <text x="242.5" y="35" font-family="Arial" font-size="12" font-weight="bold" fill="white" text-anchor="middle">
            {direction_t}
        </text>

        <circle cx="80" cy="90" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
        <circle cx="80" cy="90" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
        <line x1="50" y1="90" x2="110" y2="90" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
        <line x1="80" y1="60" x2="80" y2="120" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
        
        <path d="M 80 140 L 220 140 L 220 165 L 80 165" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
        <line x1="130" y1="140" x2="130" y2="165" stroke="#1e3a8a" stroke-dasharray="3"/>
        <line x1="180" y1="140" x2="180" y2="165" stroke="#1e3a8a" stroke-dasharray="3"/>

        <text x="160" y="185" font-family="Arial" font-size="14" font-weight="bold" fill="#1e3a8a" text-anchor="middle">
            {item_n if item_n else "ITEM NAME"}
        </text>
    </svg>
    """
    return svg

# --- Section 2: PDF Generator ---
def create_pdf(data_dict):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "JOB ORDER - ERP SYSTEM", 0, 1, 'C')
    pdf.ln(5)

    def draw_section(title, fields):
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 8, title, 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        for label, val in fields.items():
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(50, 7, f"{label}:", 1, 0, 'L', True)
            pdf.cell(140, 7, str(val), 1, 1, 'L')
        pdf.ln(3)

    draw_section("ITEM IDENTIFICATION", {
        "ITEM NAME": data_dict.get("Item Name"),
        "ITEM FORMAT": data_dict.get("Item Format")
    })
    
    draw_section("PRODUCT SPECIFICATIONS", {
        "Material": data_dict.get("Material Type"),
        "Width (mm)": data_dict.get("Width"),
        "Repeat (mm)": data_dict.get("Repeat Length"),
        "Winding Direction": data_dict.get("Winding Direction")
    })

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(63.3, 20, "Sales", 1, 0, 'C')
    pdf.cell(63.3, 20, "Production", 1, 0, 'C')
    pdf.cell(63.4, 20, "QC", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- Section 3: Streamlit UI ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

# 1. Item Selection
st.subheader("📦 1. Item Selection")
col_i1, col_i2 = st.columns(2)
with col_i1:
    item_name = st.text_input("Item Name", placeholder="e.g. Naqi Water 330ml Label")
with col_i2:
    item_format = st.text_input("Item Format", placeholder="e.g. 37 x 190 mm")

# 2. Customer Info
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    date = st.date_input("Date", datetime.date.today())
    company_name = st.text_input("Company Name")
with col_b2:
    customer_id = st.text_input("Customer ID")
with col_b3:
    sales_po = st.text_input("Sales PO#")

# 3. Product Specs
st.markdown("---")
st.subheader("⚙️ 2. Technical Specifications")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    material_type = st.selectbox("Material Type", ["BOPP", "PE", "PETG"])
    width = st.number_input("Width (mm)", min_value=0.0)
with col_s2:
    density = st.selectbox("Density", [0.91, 0.92, 1.40])
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
with col_s3:
    thickness = st.selectbox("Thickness (µ)", [30, 35, 38, 40])
    colors_no = st.number_input("No. of Colors", min_value=0)
with col_s4:
    artwork_no = st.text_input("Artwork No.")

# 4. Winding Direction & Static Preview
st.markdown("---")
col_v1, col_v2 = st.columns([1, 1])
with col_v1:
    # Drawing with item data inside
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
    st.markdown(f'<div style="text-align: center;">{draw_final_svg(item_name, item_format, winding_direction)}</div>', unsafe_allow_html=True)

with col_v2:
    st.subheader("🔄 Production Details")
    inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
    
    # SMART PRODUCTION CALCULATOR (REINSTATED)
    st.markdown("#### 🧮 Smart Web & Production Calculator")
    c_calc1, c_calc2, c_calc3 = st.columns(3)
    with c_calc1:
        mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
    with c_calc2:
        mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
    with c_calc3:
        no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)

    c_calc4, c_calc5, c_calc6 = st.columns(3)
    edge_trim = 24 # Fixed standard
    
    # Auto Calculations
    pcs_per_roll = int((mother_roll_length * 1000) / repeat_length) if repeat_length > 0 else 0
    waste_by_mm = float(mother_roll_width - (width * no_of_lines)) if mother_roll_width > 0 else 0
    unused_waste = float(waste_by_mm - edge_trim) if waste_by_mm > 0 else 0

    with c_calc4:
        st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
    with c_calc5:
        st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
    with c_calc6:
        st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

# 5. Quantity & Delivery
st.markdown("---")
st.subheader("📦 3. Quantity & Delivery")
cq1, cq2, cq3 = st.columns(3)
quantity = cq1.text_input("Required Quantity")
packaging = cq2.text_input("Packaging", value="In Pallets")
due_date = cq3.date_input("Due Date")

# 6. Actions
st.markdown("---")
if st.button("📄 Generate Formal PDF", type="primary", use_container_width=True):
    data = {
        "Item Name": item_name, "Item Format": item_format, "Date": str(date),
        "Company Name": company_name, "Customer ID": customer_id, "Sales PO#": sales_po,
        "Material Type": material_type, "Width": width, "Repeat Length": repeat_length,
        "Winding Direction": winding_direction, "Quantity": quantity, "Pcs/Roll": pcs_per_roll
    }
    pdf_out = create_pdf(data)
    st.download_button("📥 Click to Download PDF", data=pdf_out, file_name=f"Job_Order_{item_name}.pdf", use_container_width=True)
