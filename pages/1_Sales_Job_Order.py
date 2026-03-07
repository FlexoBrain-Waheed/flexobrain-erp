import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- SVG Drawing Function (Reverted to the EXCELLENT version, but without Text) ---
def draw_winding_svg(direction):
    if "Clockwise" in direction and "Anti" not in direction:
        # Drawing for Clockwise (Unwinding from Bottom)
        svg = """
        <svg width="250" height="120" viewBox="0 0 250 120" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="40" fill="#e0e7ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="60" cy="60" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="35" y1="60" x2="85" y2="60" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <line x1="60" y1="35" x2="60" y2="85" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <rect x="60" y="80" width="160" height="20" fill="#f3f4f6" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="110" y1="80" x2="110" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="160" y1="80" x2="160" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="210" y1="80" x2="210" y2="100" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <path d="M 25 60 A 35 35 0 0 1 60 25" fill="none" stroke="#ef4444" stroke-width="3"/>
            <polygon points="60,20 70,25 60,30" fill="#ef4444"/>
        </svg>
        """
    else:
        # Drawing for Anti-Clockwise (Unwinding from Top)
        svg = """
        <svg width="250" height="120" viewBox="0 0 250 120" xmlns="http://www.w3.org/2000/svg">
            <circle cx="60" cy="60" r="40" fill="#e0e7ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="60" cy="60" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="35" y1="60" x2="85" y2="60" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <line x1="60" y1="35" x2="60" y2="85" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <rect x="60" y="20" width="160" height="20" fill="#f3f4f6" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="110" y1="20" x2="110" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="160" y1="20" x2="160" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <line x1="210" y1="20" x2="210" y2="40" stroke="#1e3a8a" stroke-dasharray="3" stroke-width="2"/>
            <path d="M 95 60 A 35 35 0 0 1 60 95" fill="none" stroke="#ef4444" stroke-width="3"/>
            <polygon points="60,90 50,95 60,100" fill="#ef4444"/>
        </svg>
        """
    return f'<div style="background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db; text-align: center;">{svg}</div>'

# --- Custom A4 PDF Generator (ERP Data based, Paper Layout) ---
def create_pdf(data_dict):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. Main Header
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(190, 10, "FLEXO ERP - JOB ORDER", 0, 1, 'C')
    pdf.ln(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 9)
    
    # 2. Date & Job Order No
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(45, 8, "DATE:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Date", ""), 1, 0, 'C')
    pdf.cell(45, 8, "JOB ORDER NO:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Job Order No", "Auto-Generated"), 1, 1, 'C')
    pdf.ln(2)

    # 3. Customer Info Section
    pdf.set_fill_color(180, 180, 180)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "CUSTOMER INFORMATION", 1, 1, 'C', True)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(45, 8, "COMPANY NAME:", 1, 0, 'L', True)
    pdf.cell(145, 8, data_dict.get("Company Name", ""), 1, 1, 'L')
    pdf.cell(45, 8, "CUSTOMER ID:", 1, 0, 'L', True)
    pdf.cell(145, 8, data_dict.get("Customer ID", ""), 1, 1, 'L')
    pdf.cell(45, 8, "HEAD OFFICE:", 1, 0, 'L', True)
    pdf.cell(145, 8, data_dict.get("Head Office Address", ""), 1, 1, 'L')
    pdf.cell(45, 8, "DELIVERY ADDRESS:", 1, 0, 'L', True)
    pdf.cell(145, 8, data_dict.get("Delivery Address", ""), 1, 1, 'L')
    pdf.cell(45, 8, "CUSTOMER PO#:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Customer PO#", ""), 1, 0, 'C')
    pdf.cell(45, 8, "SALES PO#:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Sales PO#", ""), 1, 1, 'C')
    pdf.ln(2)

    # 4. Product Specs Section (Pure ERP Data)
    pdf.set_fill_color(180, 180, 180)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "PRODUCT SPECIFICATIONS", 1, 1, 'C', True)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    
    pdf.cell(45, 8, "PRODUCT TYPE:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Product Type", ""), 1, 0, 'C')
    pdf.cell(45, 8, "PRODUCT CODE:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Product Code", ""), 1, 1, 'C')

    pdf.cell(45, 8, "MATERIAL TYPE:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Material Type", ""), 1, 0, 'C')
    pdf.cell(45, 8, "DENSITY (g/cm3):", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Density (g/cm3)", "")), 1, 1, 'C')

    pdf.cell(45, 8, "WIDTH (mm):", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Label/Film Width (mm)", "")), 1, 0, 'C')
    pdf.cell(45, 8, "REPEAT LENGTH (mm):", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Repeat Length (mm)", "")), 1, 1, 'C')

    pdf.cell(45, 8, "THICKNESS (u):", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Thickness (u)", "")), 1, 0, 'C')
    pdf.cell(45, 8, "COLORS:", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Colors", "")), 1, 1, 'C')

    pdf.cell(45, 8, "COLOR OF FILM:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Color of Film", ""), 1, 0, 'C')
    pdf.cell(45, 8, "ARTWORK STATUS:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Artwork Status", ""), 1, 1, 'C')

    pdf.cell(45, 8, "ARTWORK NO:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Artwork No.", ""), 1, 0, 'C')
    pdf.cell(45, 8, "INNER CORE:", 1, 0, 'L', True)
    pdf.cell(50, 8, str(data_dict.get("Inner Core", "")), 1, 1, 'C')

    pdf.cell(45, 8, "WINDING DIRECTION:", 1, 0, 'L', True)
    pdf.cell(145, 8, str(data_dict.get("Winding Direction", "")), 1, 1, 'C')
    pdf.ln(2)

    # 5. Quantity & Delivery Section
    pdf.set_fill_color(180, 180, 180)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "QUANTITY & DELIVERY", 1, 1, 'C', True)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(45, 8, "REQUIRED QUANTITY:", 1, 0, 'L', True)
    pdf.cell(145, 8, str(data_dict.get("Required Quantity", "")), 1, 1, 'C')
    pdf.cell(45, 8, "PACKAGING:", 1, 0, 'L', True)
    pdf.cell(145, 8, data_dict.get("Packaging", ""), 1, 1, 'C')
    pdf.cell(45, 8, "DELIVERY CITY:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Delivery City", ""), 1, 0, 'C')
    pdf.cell(45, 8, "DUE DATE:", 1, 0, 'L', True)
    pdf.cell(50, 8, data_dict.get("Due Date", ""), 1, 1, 'C')
    pdf.ln(2)

    # 6. Approvals (Paper style formatting)
    pdf.set_fill_color(180, 180, 180)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    
    col_w = 190 / 5
    pdf.cell(col_w, 8, "SALES DEPT.", 1, 0, 'C', True)
    pdf.cell(col_w, 8, "PLANT MANAGER", 1, 0, 'C', True)
    pdf.cell(col_w, 8, "PRODUCTION DEPT.", 1, 0, 'C', True)
    pdf.cell(col_w, 8, "PRINTING DEPT.", 1, 0, 'C', True)
    pdf.cell(col_w, 8, "QC DEPT.", 1, 1, 'C', True)
    
    # Signature boxes (Empty space for physical signing)
    pdf.cell(col_w, 20, "", 1, 0, 'C')
    pdf.cell(col_w, 20, "", 1, 0, 'C')
    pdf.cell(col_w, 20, "", 1, 0, 'C')
    pdf.cell(col_w, 20, "", 1, 0, 'C')
    pdf.cell(col_w, 20, "", 1, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

def create_excel(data_dict):
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Job Order')
    return output.getvalue()

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
    job_order_no = st.text_input("Job Order No.", placeholder="Auto-generated", disabled=True) 
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
    ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film", "Printed LDPE Bag"]
)

repeat_length = width = 0
inner_core = winding_direction = roll_weight = length = bottom_gusset = ""
mother_roll_length = mother_roll_width = no_of_lines = edge_trim = 0
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

    if product_type == "Printed OPP Label":
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        with col_d2:
            st.markdown("**🔍 Live Unwind Direction Preview:**")
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

        if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0:
            total_labels_calculated = pcs_per_roll * no_of_lines

    st.markdown("---")

    st.subheader("📦 3. Quantity & Delivery")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
    
    with col_q1:
        quantity = st.number_input("Required Quantity", min_value=0) 
        if product_type == "Printed OPP Label" and quantity > 0 and total_labels_calculated > 0:
            if quantity != total_labels_calculated:
                st.markdown(f"<p style='color:red; font-size:14px; font-weight:bold;'>🚨 WARNING: Requested ({quantity:,}) != Calculated ({total_labels_calculated:,})!</p>", unsafe_allow_html=True)

    with col_q2:
        packaging = st.text_input("Packaging", value="In pallets")
    with col_q3:
        delivery_city = st.text_input("Delivery City")
    with col_q4:
        due_date = st.date_input("Due Date of Order", datetime.date.today())

    # --- PURE ERP EXPORT DATA (NO SMART CALCULATOR FIELDS INCLUDED) ---
    export_data = {
        "Date": str(date),
        "Job Order No": job_order_no,
        "Company Name": company_name,
        "Customer ID": customer_id,
        "Head Office Address": head_office_address,
        "Delivery Address": delivery_address,
        "Sales PO#": sales_po,          
        "Customer PO#": po_number,
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
        "Inner Core": inner_core,
        "Winding Direction": winding_direction,
        "Required Quantity": quantity,
        "Packaging": packaging,
        "Delivery City": delivery_city,
        "Due Date": str(due_date)
    }

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎯 Actions")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
            st.success("Job Order saved successfully! Ready for production review.")
            
    with btn_col2:
        excel_file = create_excel(export_data)
        st.download_button("📊 Export to Excel", data=excel_file, file_name="Job_Order_ERP.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        
    with btn_col3:
        pdf_file = create_pdf(export_data)
        st.download_button("📄 Export to PDF", data=pdf_file, file_name="Job_Order_ERP.pdf", mime="application/pdf", use_container_width=True)
