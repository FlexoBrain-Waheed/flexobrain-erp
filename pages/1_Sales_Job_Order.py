import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: SVG Engineering Drawings (STRICTLY CORRECTED) ---
def draw_winding_svg(direction):
    if "Clockwise" in direction and "Anti" not in direction:
        # Clockwise #4: Arrow moves WITH clock (Right), web opens from TOP
        svg = """
        <svg width="300" height="160" viewBox="0 0 300 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                </marker>
            </defs>
            <circle cx="90" cy="80" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="80" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="60" y1="80" x2="120" y2="80" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="90" y1="50" x2="90" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 90 30 L 250 30 L 250 55 L 90 55" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="150" y1="30" x2="150" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="200" y1="30" x2="200" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 40 70 A 50 50 0 0 1 125 50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead)"/>
        </svg>
        """
    else:
        # Anti-clockwise #3: Arrow moves AGAINST clock (Left), web opens from BOTTOM
        svg = """
        <svg width="300" height="160" viewBox="0 0 300 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead_inv" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="10 0, 0 3.5, 10 7" fill="#ef4444" />
                </marker>
            </defs>
            <circle cx="90" cy="80" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="80" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="60" y1="80" x2="120" y2="80" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="90" y1="50" x2="90" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 90 130 L 250 130 L 250 155 L 90 155" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="150" y1="130" x2="150" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="200" y1="130" x2="200" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 130 100 A 50 50 0 0 1 50 100" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead_inv)"/>
        </svg>
        """
    return f'<div style="text-align: center; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; overflow: visible;">{svg}</div>'

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

    draw_section("CUSTOMER INFORMATION", {
        "Date": data_dict.get("Date"),
        "Job Order No": data_dict.get("Job Order No"),
        "Company Name": data_dict.get("Company Name"),
        "Customer ID": data_dict.get("Customer ID"),
        "Sales PO#": data_dict.get("Sales PO#"),
        "Delivery Address": data_dict.get("Delivery Address")
    })

    draw_section("PRODUCT SPECIFICATIONS", {
        "Product Type": data_dict.get("Product Type"),
        "Material": data_dict.get("Material Type"),
        "Width (mm)": data_dict.get("Width"),
        "Repeat Length (mm)": data_dict.get("Repeat Length"),
        "Thickness (u)": data_dict.get("Thickness"),
        "Colors": data_dict.get("Colors"),
        "Artwork No": data_dict.get("Artwork No"),
        "Inner Core": data_dict.get("Inner Core"),
        "Winding Direction": data_dict.get("Winding Direction"),
        "Pcs/Roll": data_dict.get("Pcs/Roll")
    })

    draw_section("DELIVERY & QUANTITY", {
        "Quantity": data_dict.get("Quantity"),
        "Packaging": data_dict.get("Packaging"),
        "Due Date": data_dict.get("Due Date"),
        "Delivery City": data_dict.get("Delivery City")
    })

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(47.5, 20, "Sales", 1, 0, 'C')
    pdf.cell(47.5, 20, "Production", 1, 0, 'C')
    pdf.cell(47.5, 20, "Printing", 1, 0, 'C')
    pdf.cell(47.5, 20, "QC", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- Section 3: Main UI ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.date.today())
        company_name = st.text_input("Company Name")
    with col2:
        job_order_no = st.text_input("Job Order No.", placeholder="Auto-generated", disabled=True)
        customer_id = st.text_input("Customer ID")
    with col3:
        sales_po = st.text_input("Sales PO#")
        delivery_address = st.text_input("Delivery Address")

st.markdown("---")

product_type = st.selectbox("Product Type", ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film"])

if product_type != "Select Product Type...":
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        material_type = st.selectbox("Material Type", ["BOPP", "PE", "PETG"])
        width = st.number_input("Width (mm)", min_value=0.0)
    with col_s2:
        density = st.selectbox("Density (g/cm³)", [0.91, 0.92, 1.40])
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
    with col_s3:
        thickness = st.selectbox("Thickness (µ)", [30, 35, 38, 40])
        colors_no = st.number_input("No. of Colors", min_value=0)
    with col_s4:
        artwork_no = st.text_input("Artwork No.")

    st.subheader("🔄 Winding Direction & Visuals")
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
    with col_v2:
        st.markdown(draw_winding_svg(winding_direction), unsafe_allow_html=True)

    with st.expander("🧮 Smart Production Calculator"):
        c1, c2, c3, c4 = st.columns(4)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        edge_trim = c4.number_input("Target Edge Trim (mm)", min_value=0, value=24)
        
        pcs_per_roll = int((m_length * 1000) / repeat_length) if repeat_length > 0 else 0
        waste = float(m_width - (width * lanes)) if m_width > 0 else 0
        st.info(f"Production Estimate: {pcs_per_roll * lanes:,} Total PCS | Waste: {waste} mm")

    st.subheader("📦 Quantity & Delivery")
    cq1, cq2, cq3, cq4 = st.columns(4)
    quantity = cq1.number_input("Required Quantity", min_value=0)
    packaging = cq2.text_input("Packaging", value="In Pallets")
    delivery_city = cq3.text_input("Delivery City")
    due_date = cq4.date_input("Due Date")

    final_data = {
        "Date": str(date), "Job Order No": job_order_no, "Company Name": company_name,
        "Customer ID": customer_id, "Sales PO#": sales_po, "Delivery Address": delivery_address,
        "Product Type": product_type, "Material Type": material_type, "Width": width,
        "Repeat Length": repeat_length, "Thickness": thickness, "Colors": colors_no,
        "Artwork No": artwork_no, "Inner Core": inner_core, "Winding Direction": winding_direction,
        "Quantity": quantity, "Pcs/Roll": pcs_per_roll, "Packaging": packaging,
        "Delivery City": delivery_city, "Due Date": str(due_date)
    }

    st.markdown("---")
    if st.button("📄 Export to PDF", use_container_width=True):
        pdf_out = create_pdf(final_data)
        st.download_button("Click here to download PDF", data=pdf_out, file_name="Job_Order.pdf")
