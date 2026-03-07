import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: Fixed SVG Drawing (Corrected Framing & Details) ---
def draw_fixed_svg(item_n, item_f, art_no, direction_t):
    # Expanded ViewBox (350x250) to ensure zero clipping
    svg_code = f"""
    <div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">
        <svg width="350" height="250" viewBox="0 0 350 250" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="340" height="240" rx="10" fill="white" stroke="#1e3a8a" stroke-width="1"/>
            
            <rect x="160" y="15" width="175" height="60" rx="5" fill="#1e3a8a" />
            <text x="247.5" y="38" font-family="Arial" font-size="12" font-weight="bold" fill="white" text-anchor="middle">{direction_t}</text>
            <text x="247.5" y="60" font-family="Arial" font-size="11" fill="#93c5fd" text-anchor="middle">Art No: {art_no if art_no else "N/A"}</text>

            <circle cx="85" cy="100" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="85" cy="100" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="55" y1="100" x2="115" y2="100" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="85" y1="70" x2="85" y2="130" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            
            <path d="M 85 145 L 260 145 L 260 175 L 85 175" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="145" y1="145" x2="145" y2="175" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="205" y1="145" x2="205" y2="175" stroke="#1e3a8a" stroke-dasharray="3"/>

            <text x="175" y="210" font-family="Arial" font-size="15" font-weight="bold" fill="#1e3a8a" text-anchor="middle">{item_n if item_n else "ITEM NAME"}</text>
            <text x="175" y="230" font-family="Arial" font-size="11" fill="#64748b" text-anchor="middle">{item_f if item_f else "ITEM FORMAT"}</text>
        </svg>
    </div>
    """
    return svg_code

# --- Section 2: PDF Generator ---
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

    draw_section("ITEM DETAILS", {"NAME": data_dict.get("Item Name"), "FORMAT": data_dict.get("Item Format"), "ARTWORK NO": data_dict.get("Artwork No")})
    draw_section("PRODUCT SPECS", {"Type": data_dict.get("Product Type"), "Material": data_dict.get("Material Type"), "Width": data_dict.get("Width"), "Repeat": data_dict.get("Repeat Length")})
    
    return pdf.output(dest='S').encode('latin-1')

# --- Main Application ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

# 🟢 STEP 1: Select Work Type (Re-instated)
st.subheader("🛠️ Step 1: Select Work Type")
product_type = st.selectbox("Product Type", ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film", "Printed LDPE Bag"])

if product_type != "Select Product Type...":
    st.markdown("---")
    
    # 📦 2. Item Identification
    st.subheader("📦 2. Item Identification")
    col_i1, col_i2 = st.columns(2)
    item_name = col_i1.text_input("Item Name", placeholder="e.g. Naqi Water 330ml Label")
    item_format = col_i2.text_input("Item Format", placeholder="e.g. 37 x 190 mm")

    # 👤 3. Customer Info
    st.markdown("---")
    st.subheader("👤 3. Customer Information")
    col_b1, col_b2, col_b3 = st.columns(3)
    date = col_b1.date_input("Date", datetime.date.today())
    company_name = col_b1.text_input("Company Name")
    customer_id = col_b2.text_input("Customer ID")
    sales_po = col_b3.text_input("Sales PO#")

    # ⚙️ 4. Technical Specs
    st.markdown("---")
    st.subheader("⚙️ 4. Technical Specifications")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    material_type = col_s1.selectbox("Material Type", ["BOPP", "PE", "PETG"])
    width = col_s1.number_input("Width (mm)", min_value=0.0)
    density = col_s2.selectbox("Density", [0.91, 0.92, 1.40])
    repeat_length = col_s2.number_input("Repeat Length (mm)", min_value=0.0)
    thickness = col_s3.selectbox("Thickness (µ)", [30, 35, 38, 40])
    colors_no = col_s3.number_input("No. of Colors", min_value=0)
    artwork_no = col_s4.text_input("Artwork No.")

    # 🔄 5. Visual Preview & Calculator
    st.markdown("---")
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        st.subheader("🔄 Production View")
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        st.markdown(draw_fixed_svg(item_name, item_format, artwork_no, winding_direction), unsafe_allow_html=True)

    with col_v2:
        st.subheader("🧮 Smart Production Calculator")
        c_c1, c_c2, c_c3 = st.columns(3)
        m_length = c_c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c_c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c_c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        
        # Calculations
        pcs_per_roll = int((m_length * 1000) / repeat_length) if repeat_length > 0 else 0
        waste = float(m_width - (width * lanes)) if m_width > 0 else 0
        
        c_c4, c_c5, c_c6 = st.columns(3)
        c_c4.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
        c_c5.number_input("Total Waste (mm)", value=waste, disabled=True)
        c_c6.number_input("Unused Waste (mm)", value=float(waste - 24) if waste > 24 else 0.0, disabled=True)

    # 📦 6. Quantity & Delivery
    st.markdown("---")
    st.subheader("📦 5. Quantity & Delivery")
    cq1, cq2, cq3 = st.columns(3)
    quantity = cq1.text_input("Quantity Required")
    packaging = cq2.text_input("Packaging", value="In Pallets")
    due_date = cq3.date_input("Due Date")

    # 🎯 7. Export
    if st.button("📄 Generate Job Order PDF", type="primary", use_container_width=True):
        data = {"Item Name": item_name, "Item Format": item_format, "Artwork No": artwork_no, "Product Type": product_type, "Material Type": material_type, "Width": width, "Repeat Length": repeat_length, "Winding Direction": winding_direction}
        st.download_button("📥 Click to Download", data=create_pdf(data), file_name=f"Job_Order_{item_name}.pdf", use_container_width=True)
