import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- SVG Drawing Function for Winding Direction ---
def draw_winding_svg(direction):
    if "Clockwise" in direction and "Anti" not in direction:
        # Drawing for Clockwise (Unwinding from TOP)
        svg = """<svg width="250" height="120" viewBox="0 0 250 120" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="40" fill="#e0e7ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="60" cy="60" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="35" y1="60" x2="85" y2="60" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <line x1="60" y1="35" x2="60" y2="85" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <rect x="60" y="20" width="160" height="20" fill="#f3f4f6" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="110" y1="20" x2="110" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="160" y1="20" x2="160" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="210" y1="20" x2="210" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <path d="M 25 60 A 35 35 0 0 1 60 25" fill="none" stroke="#ef4444" stroke-width="3"/>
            <polygon points="55,20 65,25 55,30" fill="#ef4444"/>
        </svg>"""
    else:
        # Drawing for Anti-Clockwise (Unwinding from BOTTOM)
        svg = """<svg width="250" height="120" viewBox="0 0 250 120" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="40" fill="#e0e7ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="60" cy="60" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="35" y1="60" x2="85" y2="60" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <line x1="60" y1="35" x2="60" y2="85" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <rect x="60" y="80" width="160" height="20" fill="#f3f4f6" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="110" y1="80" x2="110" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="160" y1="80" x2="160" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="210" y1="80" x2="210" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <path d="M 25 60 A 35 35 0 0 0 60 95" fill="none" stroke="#ef4444" stroke-width="3"/>
            <polygon points="55,90 65,95 55,100" fill="#ef4444"/>
        </svg>"""
    return f'<div style="background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db; text-align: center;">{svg}</div>'

# --- Functions for PDF and Excel Generation ---
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
    pdf.cell(0, 10, "Sales Job Order", ln=True, align='C')
    pdf.ln(10)
    for key, value in data_dict.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(60, 10, f"{key}:", border=0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, str(value), border=0, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- Page configuration ---
st.set_page_config(page_title="Sales Job Order", page_icon="📝", layout="wide")

st.title("📝 Create New Sales Job Order")
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

product_type = st.selectbox(
    "Product Type", 
    ["Select Product Type...", "OPP Label (Wrap Around)", "Printed PE Shrink Film", "Printed LDPE Bag"]
)

repeat_length = width = 0
inner_core = core_type = winding_direction = roll_weight = length = bottom_gusset = ""
core_thickness = mother_roll_length = mother_roll_width = no_of_lines = edge_trim = 0
pcs_per_roll = waste_by_mm = unused_waste = total_labels_calculated = 0

if product_type != "Select Product Type...":
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        product_code = st.text_input("Product Code (SAP)")
    with col_s2:
        material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"])
    with col_s3:
        density = st.selectbox("Density (g/cm³)", [0.91, 0.92, 1.40]) 
    with col_s4:
        thickness = st.selectbox("Thickness (µ)", [30, 35, 38, 40])

    col_s5, col_s6, col_s7, col_s8 = st.columns(4)
    with col_s5:
        width = st.number_input("Label Width (mm)", min_value=0.0) 
    with col_s6:
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
    with col_s7:
        color_of_film = st.text_input("Color of Film", value="Transparent")
    with col_s8:
        colors_no = st.number_input("No. of Colors in Printing", min_value=1, max_value=10)

    col_s9, col_s10 = st.columns(2)
    with col_s9:
        artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"])
    with col_s10:
        artwork_no = st.text_input("Artwork No.") 

    st.markdown(f"### 🔄 Specific Specs for: {product_type}")

    if product_type == "OPP Label (Wrap Around)":
        
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
            core_type = st.selectbox("Core Material", ["Paper", "Plastic"])
            core_thickness = st.number_input("Core Wall Thickness (mm)", min_value=0.0)
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        with col_d2:
            st.markdown("**📦 Product Look Like:**")
            st.markdown(draw_winding_svg(winding_direction), unsafe_allow_html=True)

        st.markdown("#### 🧮 Smart Web & Production Calculator")
        
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        with col_calc1:
            mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
        with col_calc2:
            mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
        with col_calc3:
            no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)
            
        col_calc4, col_calc5, col_calc6, col_calc7 = st.columns(4)
        with col_calc4:
            edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0, value=24)
            
        if mother_roll_length > 0 and repeat_length > 0:
            pcs_per_roll = int((mother_roll_length * 1000) / repeat_length)
        with col_calc5:
            st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
            
        if mother_roll_width > 0 and width > 0 and no_of_lines > 0:
            waste_by_mm = float(mother_roll_width - (width * no_of_lines))
            unused_waste = float(waste_by_mm - edge_trim)
        with col_calc6:
            st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
        with col_calc7:
            st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

        if mother_roll_width > 0 and width > 0 and no_of_lines > 0:
            required_width = (width * no_of_lines) + edge_trim
            if required_width > mother_roll_width:
                st.error(f"🚨 **GEOMETRY ERROR:** Required width is **{required_width} mm**, but your Mother Roll is only **{mother_roll_width} mm**!")
            elif required_width < mother_roll_width:
                st.warning(f"⚠️ **WIDTH WARNING:** You have **{unused_waste} mm** of UNUSED waste.")
            else:
                st.info(f"✅ **PERFECT FIT:** Required width exactly matches the Mother Roll.")

        if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0:
            total_labels_calculated = pcs_per_roll * no_of_lines
            st.success(f"**💡 Production Estimate for 1 Mother Roll:** Total Exact Quantity: **{total_labels_calculated:,}** PCS")

    elif product_type == "Printed PE Shrink Film":
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
            core_type = st.selectbox("Core Material", ["Paper", "Plastic"])
            core_thickness = st.number_input("Core Wall Thickness (mm)", min_value=0.0)
            roll_weight = st.number_input("Roll Weight (kg)", min_value=0.0)
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        with col_d2:
            st.markdown("**📦 Product Look Like:**")
            st.markdown(draw_winding_svg(winding_direction), unsafe_allow_html=True)

    elif product_type == "Printed LDPE Bag":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            length = st.number_input("Bag Length (mm)", min_value=0)
        with col_d2:
            bottom_gusset = st.number_input("Bottom Gusset (mm)", min_value=0)

    st.markdown("---")

    st.subheader("📦 3. Quantity & Delivery")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
    
    with col_q1:
        quantity = st.number_input("Required Quantity by Customer", min_value=0) 
        if product_type == "OPP Label (Wrap Around)" and quantity > 0 and total_labels_calculated > 0:
            if quantity != total_labels_calculated:
                st.markdown(f"<p style='color:red; font-size:14px; font-weight:bold;'>🚨 WARNING: Requested Quantity ({quantity:,}) does NOT match Calculated Production ({total_labels_calculated:,})!</p>", unsafe_allow_html=True)

    with col_q2:
        packaging = st.text_input("Packaging", value="Suitable / As Usual")
    with col_q3:
        due_date = st.date_input("Due Date of Order", datetime.date.today())
    with col_q4:
        delivery_city = st.text_input("Delivery City") 

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
        "Product Type": product_type,
        "Product Code": product_code,
        "Material Type": material_type, 
        "Density (g/cm3)": density,     
        "Label/Film Width (mm)": width,
        "Repeat Length (mm)": repeat_length, 
        "Thickness (u)": thickness,
        "Colors": colors_no,
        "Color of Film": color_of_film,
        "Artwork Status": artwork,
        "Artwork No.": artwork_no,      
        "Required Quantity": quantity,
        "Packaging": packaging,
        "Due Date": str(due_date)
    }
    
    if product_type == "OPP Label (Wrap Around)":
        job_data["Mother Roll Length (m)"] = mother_roll_length
        job_data["Mother Roll Width (mm)"] = mother_roll_width
        job_data["No. of Lines"] = no_of_lines
        job_data["Target Edge Trim (mm)"] = edge_trim
        job_data["Total Waste (mm)"] = waste_by_mm
        job_data["Unused Waste (mm)"] = unused_waste
        job_data["Pcs/Roll"] = pcs_per_roll
        job_data["Inner Core"] = inner_core
        job_data["Core Type"] = core_type
        job_data["Core Thickness (mm)"] = core_thickness
        job_data["Winding Direction"] = winding_direction
        
    elif product_type == "Printed PE Shrink Film":
        job_data["Inner Core"] = inner_core
        job_data["Core Type"] = core_type
        job_data["Core Thickness (mm)"] = core_thickness
        job_data["Roll Weight (kg)"] = roll_weight
        job_data["Winding Direction"] = winding_direction
        
    elif product_type == "Printed LDPE Bag":
        job_data["Bag Length (mm)"] = length
        job_data["Bottom Gusset (mm)"] = bottom_gusset

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎯 Actions")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
            st.success("Job Order saved successfully! Ready for production review.")
            
    with btn_col2:
        excel_file = create_excel(job_data)
        st.download_button("📊 Export to Excel", data=excel_file, file_name="Job_Order_Export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        
    with btn_col3:
        pdf_file = create_pdf(job_data)
        st.download_button("📄 Export to PDF", data=pdf_file, file_name="Job_Order_Export.pdf", mime="application/pdf", use_container_width=True)
