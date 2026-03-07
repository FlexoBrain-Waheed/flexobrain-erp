import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: SVG Engineering Drawing Function ---
def draw_final_svg(item_n, item_f, direction_t):
    # Logic for arrow rotation based on direction
    if "Clockwise" in direction_t:
        # Clockwise #4: Arrow moves WITH clock, web opens from TOP
        arrow_path = '<path d="M 40 70 A 50 50 0 0 1 125 50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead)"/>'
        web_path = '<path d="M 90 30 L 250 30 L 250 55 L 90 55" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>'
        sep_lines = '<line x1="150" y1="30" x2="150" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/><line x1="200" y1="30" x2="200" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>'
    else:
        # Anti-clockwise #3: Arrow moves AGAINST clock, web opens from BOTTOM
        arrow_path = '<path d="M 130 100 A 50 50 0 0 1 50 100" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead_inv)"/>'
        web_path = '<path d="M 90 130 L 250 130 L 250 155 L 90 155" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>'
        sep_lines = '<line x1="150" y1="130" x2="150" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/><line x1="200" y1="130" x2="200" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/>'

    svg_code = f"""
    <div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">
        <svg width="320" height="220" viewBox="0 0 320 220" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" /></marker>
                <marker id="arrowhead_inv" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="10 0, 0 3.5, 10 7" fill="#ef4444" /></marker>
            </defs>
            <rect x="5" y="5" width="310" height="210" rx="10" fill="white" stroke="#1e3a8a" stroke-width="1"/>
            <rect x="160" y="15" width="145" height="30" rx="5" fill="#1e3a8a" />
            <text x="232" y="35" font-family="Arial" font-size="12" font-weight="bold" fill="white" text-anchor="middle">{direction_t}</text>
            <circle cx="90" cy="95" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="95" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            {web_path}
            {sep_lines}
            {arrow_path}
            <text x="160" y="190" font-family="Arial" font-size="14" font-weight="bold" fill="#1e3a8a" text-anchor="middle">{item_n if item_n else "ITEM NAME"}</text>
            <text x="160" y="208" font-family="Arial" font-size="11" fill="#64748b" text-anchor="middle">{item_f if item_f else "ITEM FORMAT"}</text>
        </svg>
    </div>
    """
    return svg_code

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

    draw_section("ITEM IDENTIFICATION", {"NAME": data_dict.get("Item Name"), "FORMAT": data_dict.get("Item Format")})
    draw_section("PRODUCT SPECS", {"Material": data_dict.get("Material Type"), "Width": data_dict.get("Width"), "Repeat": data_dict.get("Repeat Length"), "Direction": data_dict.get("Winding Direction")})
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(63.3, 15, "Sales", 1, 0, 'C'); pdf.cell(63.3, 15, "Production", 1, 0, 'C'); pdf.cell(63.4, 15, "QC", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Main App ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Create New Sales Job Order")

# 1. Item Selection
st.subheader("📦 1. Item Selection")
col_i1, col_i2 = st.columns(2)
item_name = col_i1.text_input("Item Name", placeholder="e.g. Naqi Water 330ml Label")
item_format = col_i2.text_input("Item Format", placeholder="e.g. 37 x 190 mm")

# 2. Tech Specs
st.markdown("---")
st.subheader("⚙️ 2. Technical Specifications")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
material_type = col_s1.selectbox("Material Type", ["BOPP", "PE", "PETG"])
width = col_s1.number_input("Width (mm)", min_value=0.0)
density = col_s2.selectbox("Density", [0.91, 0.92, 1.40])
repeat_length = col_s2.number_input("Repeat Length (mm)", min_value=0.0)
thickness = col_s3.selectbox("Thickness (µ)", [30, 35, 38, 40])
colors_no = col_s3.number_input("No. of Colors", min_value=0)
artwork_no = col_s4.text_input("Artwork No.")

# 3. Visuals & Calculator
st.markdown("---")
col_v1, col_v2 = st.columns([1, 1])
with col_v1:
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
    st.markdown(draw_final_svg(item_name, item_format, winding_direction), unsafe_allow_html=True)

with col_v2:
    st.subheader("🧮 Smart Web & Production Calculator")
    c_c1, c_c2, c_c3 = st.columns(3)
    m_length = c_c1.number_input("Mother Roll Length (m)", min_value=0)
    m_width = c_c2.number_input("Mother Roll Width (mm)", min_value=0)
    lanes = c_c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
    
    pcs_per_roll = int((m_length * 1000) / repeat_length) if repeat_length > 0 else 0
    waste = float(m_width - (width * lanes)) if m_width > 0 else 0
    
    c_c4, c_c5, c_c6 = st.columns(3)
    c_c4.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
    c_c5.number_input("Total Waste (mm)", value=waste, disabled=True)
    c_c6.number_input("Unused Waste (mm)", value=float(waste - 24) if waste > 24 else 0.0, disabled=True)

# 4. Quantity & Delivery
st.markdown("---")
st.subheader("📦 3. Quantity & Delivery")
cq1, cq2, cq3 = st.columns(3)
quantity = cq1.text_input("Quantity")
packaging = cq2.text_input("Packaging", value="Pallets")
due_date = cq3.date_input("Due Date")

# 5. Export
st.markdown("---")
if st.button("📄 Generate PDF", type="primary", use_container_width=True):
    export_data = {"Item Name": item_name, "Item Format": item_format, "Date": str(datetime.date.today()), "Material Type": material_type, "Width": width, "Repeat Length": repeat_length, "Winding Direction": winding_direction, "Quantity": quantity}
    st.download_button("📥 Click to Download", data=create_pdf(export_data), file_name=f"Job_Order_{item_name}.pdf", use_container_width=True)
