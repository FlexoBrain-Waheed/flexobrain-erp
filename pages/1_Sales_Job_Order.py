import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

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
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Sales Job Order", ln=True, align='C')
    pdf.ln(10)
    
    # Data Rows
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

# Variables for global scope initialization
repeat_length = width = 0
inner_core = winding_direction = roll_weight = length = bottom_gusset = ""
mother_roll_length = mother_roll_width = no_of_lines = edge_trim = 0
pcs_per_roll = waste_by_mm = unused_waste = 0

if product_type != "Select Product Type...":
    
    # Row 1: Basic Material Specs
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        product_code = st.text_input("Product Code (SAP)")
    with col_s2:
        material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"])
    with col_s3:
        density = st.selectbox("Density (g/cm³)", [0.91, 0.92, 1.40]) 
    with col_s4:
        thickness = st.selectbox("Thickness (µ)", [30, 35, 38, 40])

    # Row 2: Dimensions and Colors
    col_s5, col_s6, col_s7, col_s8 = st.columns(4)
    with col_s5:
        width = st.number_input("Label Width (mm)", min_value=0.0) 
    with col_s6:
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
    with col_s7:
        color_of_film = st.text_input("Color of Film", value="Transparent")
    with col_s8:
        colors_no = st.number_input("No. of Colors in Printing", min_value=1, max_value=10)

    # Row 3: Design Data
    col_s9, col_s10 = st.columns(2)
    with col_s9:
        artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"])
    with col_s10:
        artwork_no = st.text_input("Artwork No.") 

    # 3. Dynamic Section based on Product Type
    st.markdown(f"### 🔄 Specific Specs for: {product_type}")

    if product_type == "OPP Label (Wrap Around)":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
        with col_d2:
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])

        # --- SMART CALCULATOR & VALIDATION SECTION ---
        st.markdown("#### 🧮 Smart Web & Production Calculator")
        
        # Row 1 of Calculator
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        with col_calc1:
            mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
        with col_calc2:
            mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
        with col_calc3:
            no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)
            
        # Row 2 of Calculator (Auto-Calculated Fields)
        # جعلنا الأعمدة 4 لاستيعاب الخانة الجديدة
        col_calc4, col_calc5, col_calc6, col_calc7 = st.columns(4)
        with col_calc4:
            edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0, value=24)
            
        # --- Auto Calculation Logic ---
        # 1. Calculate Pcs / Roll
        if mother_roll_length > 0 and repeat_length > 0:
            pcs_per_roll = int((mother_roll_length * 1000) / repeat_length)
            
        with col_calc5:
            st.number_input("Pcs / Roll", value=pcs_per_roll, disabled=True)
            
        # 2. Calculate Total Waste & Unused Waste
        if mother_roll_width > 0 and width > 0 and no_of_lines > 0:
            waste_by_mm = float(mother_roll_width - (width * no_of_lines))
            unused_waste = float(waste_by_mm - edge_trim)
            
        with col_calc6:
            st.number_input("Total Waste (mm)", value=waste_by_mm, disabled=True)
            
        with col_calc7:
            # الخانة الجديدة
            st.number_input("Unused Waste (mm)", value=unused_waste, disabled=True)

        # --- Validation Messages ---
        if mother_roll_width > 0 and width > 0 and no_of_lines > 0:
            required_width = (width * no_of_lines) + edge_trim
            
            if required_width > mother_roll_width:
                st.error(f"🚨 **GEOMETRY ERROR:** Required width is **{required_width} mm**, but your Mother Roll is only **{mother_roll_width} mm**! This is physically impossible.")
            elif required_width < mother_roll_width:
                st.warning(f"⚠️ **WIDTH WARNING:** You have **{unused_waste} mm** of UNUSED waste beyond the target edge trim. Total waste will be {waste_by_mm} mm.")
            else:
                st.info(f"✅ **PERFECT FIT:** Required width exactly matches the Mother Roll. Total waste is strictly the edge trim ({waste_by_mm} mm).")

        # --- Quantity Estimate ---
        if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0:
            total_labels_calculated = pcs_per_roll * no_of_lines
            st.success(f"""
            **💡 Production Estimate for 1 Mother Roll:**
            * Pcs per Final Roll: **{pcs_per_roll:,}** PCS
            * Final Output Rolls: **{no_of_lines}** Rolls
            * Total Exact Quantity: **{total_labels_calculated:,}** PCS
            """)

    elif product_type == "Printed PE Shrink Film":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
        with col_d2:
            roll_weight = st.number_input("Roll Weight (kg)", min_value=0.0)
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])

    elif product_type == "Printed LDPE Bag":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            length = st.number_input("Bag Length (mm)", min_value=0)
        with col_d2:
            bottom_gusset = st.number_input("Bottom Gusset (mm)", min_value=0)

    st.markdown("---")

    # 4. Quantity & Delivery
    st.subheader("📦 3. Quantity & Delivery")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
    
    with col_q1:
        quantity = st.text_input("Required Quantity by Customer") 
    with col_q2:
        packaging = st.text_input("Packaging", value="Suitable / As Usual")
    with col_q3:
        due_date = st.text_input("Due Date of Order", value="ASAP")
    with col_q4:
        delivery_city = st.text_input("Delivery City") 

    # --- Data Collection for Export ---
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
        "Due Date": due_date
    }
    
    # Add dynamic fields for printing only if they exist
    if product_type == "OPP Label (Wrap Around)":
        job_data["Mother Roll Length (m)"] = mother_roll_length
        job_data["Mother Roll Width (mm)"] = mother_roll_width
        job_data["No. of Lines"] = no_of_lines
        job_data["Target Edge Trim (mm)"] = edge_trim
        job_data["Total Waste (mm)"] = waste_by_mm
        job_data["Unused Waste (mm)"] = unused_waste
        job_data["Pcs/Roll"] = pcs_per_roll
        job_data["Inner Core"] = inner_core
        job_data["Winding Direction"] = winding_direction
        
    elif product_type == "Printed PE Shrink Film":
        job_data["Inner Core"] = inner_core
        job_data["Roll Weight (kg)"] = roll_weight
        job_data["Winding Direction"] = winding_direction
        
    elif product_type == "Printed LDPE Bag":
        job_data["Bag Length (mm)"] = length
        job_data["Bottom Gusset (mm)"] = bottom_gusset

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Action Buttons Row ---
    st.subheader("🎯 Actions")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    with btn_col1:
        if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
            st.success("Job Order saved successfully! Ready for production review.")
            
    with btn_col2:
        excel_file = create_excel(job_data)
        st.download_button(
            label="📊 Export to Excel",
            data=excel_file,
            file_name="Job_Order_Export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with btn_col3:
        pdf_file = create_pdf(job_data)
        st.download_button(
            label="📄 Export to PDF",
            data=pdf_file,
            file_name="Job_Order_Export.pdf",
            mime="application/pdf",
            use_container_width=True
        )
