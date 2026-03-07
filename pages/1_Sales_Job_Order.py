import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: SVG Engineering Drawing (Simple & Clean) ---
def draw_fixed_svg(item_n, item_f, art_no, direction_t):
    svg_code = f"""
    <div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">
        <svg width="350" height="240" viewBox="0 0 350 240" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="340" height="230" rx="10" fill="white" stroke="#1e3a8a" stroke-width="1"/>
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

# --- Section 2: PDF and Excel Generation ---
def create_excel(data_dict):
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Job Order')
    return output.getvalue()

def create_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Sales Job Order - ERP System", ln=True, align='C')
    pdf.ln(10)
    for key, value in data_dict.items():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 8, f"{key}:", border=1, fill=False)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, str(value), border=1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- Main Page Config ---
st.set_page_config(page_title="Sales Job Order", page_icon="📝", layout="wide")
st.title("📝 Create New Sales Job Order")
st.markdown("---")

# Step 1: Work Type Selection
product_type = st.selectbox("Product Type", ["Select Product Type...", "OPP Label (Wrap Around)", "Printed PE Shrink Film", "Printed LDPE Bag"])

if product_type != "Select Product Type...":
    
    # Identification
    st.subheader("📦 1. Item Identification")
    col_i1, col_i2 = st.columns(2)
    item_name = col_i1.text_input("Item Name")
    item_format = col_i2.text_input("Item Format")

    # Customer Information
    st.subheader("👤 2. Customer Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("Date", datetime.date.today())
        company_name = st.text_input("Company Name")
    with col2:
        job_order_no = st.text_input("Job Order No.", placeholder="Auto-generated", disabled=True)
        customer_id = st.text_input("Customer ID")
    with col3:
        po_number = st.text_input("Customer's PO#")
        sales_po = st.text_input("Sales PO#")

    # Technical Specs
    st.subheader("⚙️ 3. Technical Specifications")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        product_code = st.text_input("Product Code (SAP)")
        material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"])
    with col_s2:
        density = st.selectbox("Density (g/cm³)", [0.91, 0.92, 1.40])
        width = st.number_input("Width (mm)", min_value=0.0)
    with col_s3:
        thickness = st.selectbox("Thickness (µ)", [30, 35, 38, 40])
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
    with col_s4:
        artwork_no = st.text_input("Artwork No.")
        colors_no = st.number_input("No. of Colors", min_value=1, max_value=10)

    # Visuals & Smart Calculator
    st.markdown("---")
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        st.subheader("🔄 Production View")
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        st.markdown(draw_fixed_svg(item_name, item_format, artwork_no, winding_direction), unsafe_allow_html=True)

    with col_v2:
        st.subheader("🧮 Smart Web & Production Calculator")
        c1, c2, c3, c_edge = st.columns(4)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        edge_trim_val = c_edge.number_input("Edge Trim Total", value=24)

        pcs_per_roll = int((m_length * 1000) / repeat_length) if repeat_length > 0 else 0
        total_waste = float(m_width - (width * lanes)) if m_width > 0 else 0.0
        unused_material = float(total_waste - edge_trim_val) if total_waste > 0 else 0.0
        total_production = pcs_per_roll * lanes

        res1, res2, res3 = st.columns(3)
        res1.metric("Pcs / Roll", f"{pcs_per_roll:,}")
        res2.metric("Total Waste (mm)", f"{total_waste} mm")
        res3.metric("Unused Material (mm)", f"{unused_material} mm")

        if m_width > 0 and width > 0:
            required_w = (width * lanes) + edge_trim_val
            if required_w > m_width:
                st.error(f"🚨 **WIDTH ERROR:** Required is {required_w}mm, but Mother Roll is {m_width}mm!")
            elif unused_material > 10:
                st.warning(f"⚠️ **UNUSED MATERIAL WARNING:** You have {unused_material}mm extra waste!")

    # Quantity Validation
    st.markdown("---")
    st.subheader("📦 4. Quantity & Delivery")
    q_col1, q_col2, q_col3 = st.columns(3)
    order_qty = q_col1.number_input("Required Quantity (Pcs)", min_value=0)
    
    if order_qty > 0 and total_production > 0:
        if order_qty != total_production:
            st.error(f"🚨 **QUANTITY MISMATCH:** Order asks for {order_qty:,} pcs, but production yields {total_production:,} pcs!")
        else:
            st.success("✅ Quantity matches production yield.")

    due_date = q_col2.date_input("Due Date", datetime.date.today())
    delivery_city = q_col3.text_input("Delivery City")

    # Actions
    st.subheader("🎯 Actions")
    job_data = {"Item": item_name, "Format": item_format, "Customer": company_name, "Quantity": order_qty, "Due Date": str(due_date)}
    
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("💾 Save Job Order", type="primary", use_container_width=True):
            st.success("Saved!")
    with b2:
        st.download_button("📊 Export Excel", data=create_excel(job_data), file_name="Job_Order.xlsx", use_container_width=True)
    with b3:
        st.download_button("📄 Export PDF", data=create_pdf(job_data), file_name="Job_Order.pdf", use_container_width=True)
