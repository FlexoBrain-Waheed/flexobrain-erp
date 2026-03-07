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

# Variables for global scope (so they don't cause errors if not selected)
repeat_length = 0
width = 0

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
        width = st.number_input("Width (mm)", min_value=0)
    with col_s6:
        repeat_length = st.number_input("Repeat Length (mm)", min_value=0)
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
    
    # Variables for dynamic fields initialization
    inner_core = pcs_per_roll = winding_direction = roll_weight = length = bottom_gusset = ""
    mother_roll_length = mother_roll_width = no_of_lines = 0

    if product_type == "OPP Label (Wrap Around)":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"])
        with col_d2:
            winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])

        # --- SMART CALCULATOR SECTION ---
        st.markdown("#### 🧮 Calculator & Mother Roll Data")
        col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)
        
        with col_calc1:
            mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
        with col_calc2:
            mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
        with col_calc3:
            no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        with col_calc4:
            pcs_per_roll = st.number_input("Target Pcs / Roll", min_value=0)

        # The logic behind the smart calculation
        if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0:
            # Calculate total pieces: (Length in m * 1000 / repeat length in mm) * number of lines
            total_labels_calculated = int((mother_roll_length * 1000 / repeat_length) * no_of_lines)
            
            # Calculate finished rolls if pcs_per_roll is defined
            total_finished_rolls = 0
            if pcs_per_roll > 0:
                total_finished_rolls = total_labels_calculated / pcs_per_roll
                
            # Displaying the results in a beautiful success box
            st.success(f"""
            **💡 Production Estimate for 1 Mother Roll:**
            * Total Exact Quantity: **{total_labels_calculated:,}** PCS
            * Expected Finished Rolls: **{total_finished_rolls:,.1f}** Rolls
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
            length = st.number_input("Length (mm)", min_value=0)
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
        "Width (mm)": width,
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
    if mother_roll_length: job_data["Mother Roll Length (m)"] = mother_roll_length
    if mother_roll_width: job_data["Mother Roll Width (mm)"] = mother_roll_width
    if no_of_lines: job_data["No. of Lines"] = no_of_lines
    if inner_core: job_data["Inner Core"] = inner_core
    if pcs_per_roll: job_data["Pcs/Roll"] = pcs_per_roll
    if winding_direction: job_data["Winding Direction"] = winding_direction
    if roll_weight: job_data["Roll Weight (kg)"] = roll_weight
    if length: job_data["Bag Length (mm)"] = length
    if bottom_gusset: job_data["Bottom Gusset (mm)"] = bottom_gusset

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
