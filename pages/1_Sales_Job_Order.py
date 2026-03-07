import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: Static Engineering Drawing ---
def draw_static_winding_svg():
    svg = """
    <svg width="250" height="150" viewBox="0 0 250 150" xmlns="http://www.w3.org/2000/svg">
        <circle cx="80" cy="70" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
        <circle cx="80" cy="70" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
        <line x1="50" y1="70" x2="110" y2="70" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
        <line x1="80" y1="40" x2="80" y2="100" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
        <path d="M 80 120 L 220 120 L 220 145 L 80 145" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
        <line x1="130" y1="120" x2="130" y2="145" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
        <line x1="180" y1="120" x2="180" y2="145" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
    </svg>
    """
    return svg

# --- Section 2: PDF Generator (Updated with Item Details) ---
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

    draw_section("ITEM DETAILS", {
        "ITEM NAME": data_dict.get("Item Name"),
        "DESCRIPTION": data_dict.get("Item Description")
    })

    draw_section("CUSTOMER INFORMATION", {
        "Date": data_dict.get("Date"),
        "Company Name": data_dict.get("Company Name"),
        "Customer ID": data_dict.get("Customer ID"),
        "Sales PO#": data_dict.get("Sales PO#")
    })

    draw_section("PRODUCT SPECIFICATIONS", {
        "Material": data_dict.get("Material Type"),
        "Width (mm)": data_dict.get("Width"),
        "Repeat (mm)": data_dict.get("Repeat Length"),
        "Colors": data_dict.get("Colors"),
        "Direction": data_dict.get("Winding Direction")
    })

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(47.5, 20, "Sales", 1, 0, 'C')
    pdf.cell(47.5, 20, "Production", 1, 0, 'C')
    pdf.cell(47.5, 20, "QC", 1, 0, 'C')
    pdf.cell(47.5, 20, "Manager", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- Section 3: Streamlit UI ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

# 1. Item Selection & Basics
st.subheader("📦 1. Item Selection")
col_i1, col_i2 = st.columns(2)
with col_i1:
    item_name = st.text_input("Item Name", placeholder="e.g. Naqi Water 330ml Label")
with col_i2:
    item_description = st.text_area("Item Description", placeholder="Detailed product description...", height=68)

# 2. Customer Info
st.markdown("---")
st.subheader("👤 2. Customer Information")
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("Date", datetime.date.today())
    company_name = st.text_input("Company Name")
with col2:
    customer_id = st.text_input("Customer ID")
with col3:
    sales_po = st.text_input("Sales PO#")

# 3. Product Specs
st.markdown("---")
st.subheader("⚙️ 3. Product Specifications")
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

# 4. Visuals & Direction
st.markdown("---")
col_v1, col_v2 = st.columns([1, 1])
with col_v1:
    st.markdown("**🔍 Technical Drawing:**")
    st.markdown(f'<div style="text-align: center; background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">{draw_static_winding_svg()}</div>', unsafe_allow_html=True)
    # New Data Labels under Image
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10px; color: #1e3a8a; font-family: Arial;">
            <div style="font-weight: bold; font-size: 16px;">{item_name if item_name else "ITEM NAME"}</div>
            <div style="font-size: 13px;">{item_description if item_description else "DESCRIPTION"}</div>
        </div>
    """, unsafe_allow_html=True)

with col_v2:
    st.subheader("🔄 Production Details")
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
    # Show direction under the image too
    st.markdown(f'<div style="text-align: center; font-weight: bold; color: #ef4444;">Direction: {winding_direction}</div>', unsafe_allow_html=True)
    inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
    quantity = st.text_input("Quantity Required")

# Export Logic
st.markdown("---")
if st.button("📄 Generate Formal PDF", use_container_width=True, type="primary"):
    data = {
        "Item Name": item_name, "Item Description": item_description,
        "Date": str(date), "Company Name": company_name, "Customer ID": customer_id,
        "Sales PO#": sales_po, "Material Type": material_type, "Width": width,
        "Repeat Length": repeat_length, "Thickness": thickness, "Colors": colors_no,
        "Artwork No": artwork_no, "Inner Core": inner_core, "Winding Direction": winding_direction,
        "Quantity": quantity
    }
    pdf_out = create_pdf(data)
    st.download_button("📥 Download PDF", data=pdf_out, file_name=f"Job_Order_{item_name}.pdf", use_container_width=True)
