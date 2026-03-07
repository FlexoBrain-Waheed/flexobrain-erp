import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: 3D Perspective Engineering Drawing ---
def draw_3d_winding_svg(direction_text):
    # A more aesthetic 3D-like isometric view of the roll
    svg = f"""
    <svg width="300" height="180" viewBox="0 0 300 180" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="90" cy="130" rx="55" ry="15" fill="#e5e7eb" />
        
        <path d="M 40 60 A 50 25 0 0 0 140 60 L 140 110 A 50 25 0 0 1 40 110 Z" fill="#f8fafc" stroke="#1e3a8a" stroke-width="2"/>
        <ellipse cx="90" cy="60" rx="50" ry="25" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="2"/>
        
        <ellipse cx="90" cy="60" rx="40" ry="20" fill="none" stroke="#94a3b8" stroke-width="1" />
        <ellipse cx="90" cy="60" rx="30" ry="15" fill="none" stroke="#94a3b8" stroke-width="1" />
        
        <ellipse cx="90" cy="60" rx="15" ry="7.5" fill="white" stroke="#1e3a8a" stroke-width="2"/>
        
        <path d="M 90 110 L 240 110 L 260 135 L 110 135 Z" fill="#f1f5f9" stroke="#1e3a8a" stroke-width="2"/>
        <line x1="160" y1="110" x2="180" y2="135" stroke="#1e3a8a" stroke-dasharray="4"/>
        <line x1="210" y1="110" x2="230" y2="135" stroke="#1e3a8a" stroke-dasharray="4"/>
        
        <rect x="160" y="10" width="130" height="25" rx="5" fill="#1e3a8a" />
        <text x="225" y="27" font-family="Arial" font-size="12" font-weight="bold" fill="white" text-anchor="middle">
            {direction_text}
        </text>
    </svg>
    """
    return svg

# --- Section 2: PDF Generator (Formal A4 Layout) ---
def create_pdf(data_dict):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "JOB ORDER - 3P PRIME PLASTIC PRODUCTS", 0, 1, 'C')
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

    draw_section("CUSTOMER & LOGISTICS", {
        "Date": data_dict.get("Date"),
        "Company Name": data_dict.get("Company Name"),
        "Sales PO#": data_dict.get("Sales PO#"),
        "Winding Direction": data_dict.get("Winding Direction")
    })

    draw_section("TECHNICAL SPECS", {
        "Width (mm)": data_dict.get("Width"),
        "Repeat (mm)": data_dict.get("Repeat Length"),
        "Thickness (u)": data_dict.get("Thickness"),
        "Colors": data_dict.get("Colors")
    })

    # Approvals
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(63.3, 15, "Sales", 1, 0, 'C')
    pdf.cell(63.3, 15, "Production", 1, 0, 'C')
    pdf.cell(63.4, 15, "QC", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- Section 3: Streamlit UI ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

# 1. Item Selection (Updated Label)
st.subheader("📦 1. Item Selection")
col_i1, col_i2 = st.columns(2)
with col_i1:
    item_name = st.text_input("Item Name", placeholder="e.g. Naqi Water 330ml Label")
with col_i2:
    item_format = st.text_area("Item Format", placeholder="Specify dimensions and type...", height=68)

# 2. Basic Info
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
    artwork_no = st.text_input("Artwork/Stereo No.")

# 4. Visual Preview Section
st.markdown("---")
st.subheader("🔄 3. Visual Preview")

col_v1, col_v2 = st.columns([1, 1])
with col_v2:
    # Selection moved here to feed the SVG
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
    inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
    quantity = st.text_input("Quantity Required")

with col_v1:
    # Drawing includes the direction text inside the blue box
    st.markdown(f'<div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">{draw_3d_winding_svg(winding_direction)}</div>', unsafe_allow_html=True)
    
    # Text labels under the image
    st.markdown(f"""
        <div style="text-align: center; margin-top: 15px; font-family: Arial;">
            <div style="color: #1e3a8a; font-weight: bold; font-size: 18px;">{item_name if item_name else "ITEM NAME"}</div>
            <div style="color: #64748b; font-size: 14px; margin-top: 5px;">{item_format if item_format else "ITEM FORMAT"}</div>
        </div>
    """, unsafe_allow_html=True)

# 5. Actions
st.markdown("---")
if st.button("📄 Generate Formal PDF", use_container_width=True, type="primary"):
    data = {
        "Item Name": item_name, "Item Format": item_format,
        "Date": str(date), "Company Name": company_name, "Customer ID": customer_id,
        "Sales PO#": sales_po, "Material Type": material_type, "Width": width,
        "Repeat Length": repeat_length, "Thickness": thickness, "Colors": colors_no,
        "Artwork No": artwork_no, "Inner Core": inner_core, "Winding Direction": winding_direction,
        "Quantity": quantity
    }
    pdf_out = create_pdf(data)
    st.download_button("📥 Click to Download PDF", data=pdf_out, file_name=f"Job_Order_{item_name}.pdf", use_container_width=True)
