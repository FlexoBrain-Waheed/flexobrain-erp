import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Corrected SVG Drawing Function (Winding Logic Re-Engineered) ---
def draw_winding_svg(direction):
    if "Clockwise" in direction:
        # Clockwise #4: Web opens from TOP to the right, following the arrow
        svg = """
        <svg width="250" height="150" viewBox="0 0 250 150" xmlns="http://www.w3.org/2000/svg">
            <circle cx="80" cy="80" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="80" cy="80" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="50" y1="80" x2="110" y2="80" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="80" y1="50" x2="80" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 80 30 L 220 30 L 220 55 L 80 55" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="130" y1="30" x2="130" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="180" y1="30" x2="180" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 40 50 A 55 55 0 0 1 120 50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead)"/>
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                </marker>
            </defs>
        </svg>
        """
    else:
        # Anti-clockwise #3: Web opens from BOTTOM to the right
        svg = """
        <svg width="250" height="150" viewBox="0 0 250 150" xmlns="http://www.w3.org/2000/svg">
            <circle cx="80" cy="70" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="80" cy="70" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="50" y1="70" x2="110" y2="70" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="80" y1="40" x2="80" y2="100" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 80 120 L 220 120 L 220 145 L 80 145" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="130" y1="120" x2="130" y2="145" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="180" y1="120" x2="180" y2="145" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 120 100 A 55 55 0 0 1 40 100" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead_inv)"/>
            <defs>
                <marker id="arrowhead_inv" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                </marker>
            </defs>
        </svg>
        """
    return f'<div style="text-align: center; background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">{svg}</div>'

# --- PDF Generator (A4 ERP Structured) ---
def create_pdf(data_dict):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "JOB ORDER - ERP SYSTEM", 0, 1, 'C')
    pdf.ln(5)

    # Tables Style
    def draw_section(title, fields):
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 8, title, 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        for label, val in fields.items():
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(45, 7, f"{label}:", 1, 0, 'L', True)
            pdf.cell(145, 7, str(val), 1, 1, 'L')
        pdf.ln(3)

    # Data Sections
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
        "Width (mm)": data_dict.get("Label/Film Width (mm)"),
        "Repeat Length (mm)": data_dict.get("Repeat Length (mm)"),
        "Thickness (u)": data_dict.get("Thickness (u)"),
        "Colors": data_dict.get("Colors"),
        "Artwork No": data_dict.get("Artwork No."),
        "Winding Direction": data_dict.get("Winding Direction"),
        "Pcs/Roll": data_dict.get("Pcs/Roll")
    })

    draw_section("DELIVERY & QUANTITY", {
        "Total Quantity": data_dict.get("Required Quantity"),
        "Packaging": data_dict.get("Packaging"),
        "Due Date": data_dict.get("Due Date"),
        "Delivery City": data_dict.get("Delivery City")
    })

    # Approvals Box
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVAL SIGNATURES", 1, 1, 'C', True)
    pdf.cell(47.5, 20, "Sales", 1, 0, 'C')
    pdf.cell(47.5, 20, "Production", 1, 0, 'C')
    pdf.cell(47.5, 20, "Printing", 1, 0, 'C')
    pdf.cell(47.5, 20, "QC", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

def create_excel(data_dict):
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Streamlit Page UI ---
st.set_page_config(page_title="Sales Job Order", layout="wide")
st.title("📝 Create New Sales Job Order")

# 1. Customer Info
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

# 2. Specs
st.markdown("---")
product_type = st.selectbox("Product Type", ["Select...", "Printed OPP Label", "PE Shrink Film"])

if product_type != "Select...":
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        material_type = st.selectbox("Material", ["BOPP", "PE", "PETG"])
        width = st.number_input("Width (mm)", min_value=0.0)
    with col_s2:
        density = st.selectbox("Density", [0.91, 0.92, 1.40])
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
    with col_s3:
        thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40])
        colors_no = st.number_input("Colors", min_value=0)
    with col_s4:
        artwork_no = st.text_input("Artwork No.")

    # 3. Winding Visuals
    st.subheader("🔄 Winding Direction & Calculations")
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        inner_core = st.selectbox("Inner Core", ["3 inch", "6 inch"])
    with col_v2:
        st.markdown(draw_winding_svg(winding_direction), unsafe_allow_html=True)

    # 4. Smart Calculator (Hidden from Print)
    with st.expander("🧮 Smart Production Calculator (Internal Only)"):
        c1, c2, c3 = st.columns(3)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lanes", min_value=1, value=1)
        
        pcs_per_roll = int((m_length * 1000) / repeat_length) if repeat_length > 0 else 0
        total_qty = pcs_per_roll * lanes
        st.info(f"Production Output: {total_qty:,} pcs total ({pcs_per_roll:,} per roll)")

    # 5. Quantity
    st.subheader("📦 Delivery Details")
    cq1, cq2, cq3 = st.columns(3)
    quantity = cq1.number_input("Order Quantity", min_value=0)
    packaging = cq2.text_input("Packaging", "Pallets")
    due_date = cq3.date_input("Due Date")
    delivery_city = st.text_input("Delivery City")

    # Data Prep
    export_data = {
        "Date": str(date), "Job Order No": job_order_no, "Company Name": company_name,
        "Customer ID": customer_id, "Sales PO#": sales_po, "Delivery Address": delivery_address,
        "Product Type": product_type, "Material Type": material_type, "Label/Film Width (mm)": width,
        "Repeat Length (mm)": repeat_length, "Thickness (u)": thickness, "Colors": colors_no,
        "Artwork No.": artwork_no, "Inner Core": inner_core, "Winding Direction": winding_direction,
        "Required Quantity": quantity, "Pcs/Roll": pcs_per_roll, "Packaging": packaging,
        "Delivery City": delivery_city, "Due Date": str(due_date)
    }

    # Actions
    st.markdown("---")
    ac1, ac2 = st.columns(2)
    with ac1:
        pdf_file = create_pdf(export_data)
        st.download_button("📄 Download PDF Job Order", data=pdf_file, file_name="Job_Order.pdf", mime="application/pdf", use_container_width=True)
    with ac2:
        excel_file = create_excel(export_data)
        st.download_button("📊 Export to Excel", data=excel_file, file_name="Job_Order.xlsx", use_container_width=True)
