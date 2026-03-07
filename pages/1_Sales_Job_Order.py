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
# السطر الأول للبيانات الأساسية
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

# السطر الثاني مخصص للعناوين فقط لكي تكون واسعة
col_addr1, col_addr2 = st.columns(2)
with col_addr1:
    head_office_address = st.text_input("Company Head Office Address") # الخانة الأولى
with col_addr2:
    delivery_address = st.text_input("Delivery Address") # الخانة الثانية

st.markdown("---")

# 2. Product Specs
st.subheader("⚙️ 2. Product Specs")

product_type = st.selectbox(
    "Product Type", 
    ["Select Product Type...", "OPP Label (Wrap Around)", "Printed PE Shrink Film", "Printed LDPE Bag"]
)

if product_type != "Select Product Type...":
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        product_code = st.text_input("Product Code (SAP)")
        width = st.number_input("Width (mm)", min_value=0)
        thickness = st.number_input("Thickness (µ)", min_value=0)
    with col_s2:
        colors_no = st.number_input("No. of Colors in Printing", min_value=1, max_value=10)
        color_of_film = st.text_input("Color of Film", value="Transparent")
    with col_s3:
        artwork = st.selectbox("Art Work", ["NEW", "REPEAT"])
        negative = st.text_input("Negative / Design No.")

    # 3. Dynamic Section based on Product Type
    st.markdown(f"### 🔄 Specific Specs for: {product_type}")
    col_d1, col_d2 = st.columns(2)

    # Variables for dynamic fields
    repeat_length = inner_core = pcs_per_roll = winding_direction = roll_weight = length = bottom_gusset = ""

    if product_type == "OPP Label (Wrap Around)":
        with col_d1:
            repeat_length = st.number_input("Repeat Length (mm)", min_value=0)
            inner_core = st.number_input("Inner Core Diameter (mm)", min_value=0)
        with col_d2:
            pcs_per_roll = st.number_input("No. of Pcs / Roll", min_value=0)
            winding_direction = st.text_input("Winding Direction#")

    elif product_type == "Printed PE Shrink Film":
        with col_d1:
            repeat_length = st.number_input("Repeat Length (mm)", min_value=0)
            inner_core = st.number_input("Inner Core Diameter (mm)", min_value=0)
        with col_d2:
            roll_weight = st.number_input("Roll Weight (kg)", min_value=0.0)
            winding_direction = st.text_input("Winding Direction")

    elif product_type == "Printed LDPE Bag":
        with col_d1:
            length = st.number_input("Length (mm)", min_value=0)
        with col_d2:
            bottom_gusset = st.number_input("Bottom Gusset (mm)", min_value=0)

    st.markdown("---")

    # 4. Quantity & Delivery
    st.subheader("📦 3. Quantity & Delivery")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4) 
    
    with col_q1:
        quantity = st.text_input("Quantity (e.g., 2,000,000 PCS or 3,000 Kg)") 
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
        "Head Office Address": head_office_address, # العنوان الأول في التقرير
        "Delivery Address": delivery_address,       # العنوان الثاني في التقرير
        "Delivery City": delivery_city, 
        "Product Type": product_type,
        "Product Code": product_code,
        "Width (mm)": width,
        "Thickness (u)": thickness,
        "Colors": colors_no,
        "Quantity": quantity,
        "Packaging": packaging,
        "Due Date": due_date
    }
    
    # إضافة الخانات التفاعلية للطباعة فقط إذا كانت موجودة
    if repeat_length: job_data["Repeat Length (mm)"] = repeat_length
    if inner_core: job_data["Inner Core (mm)"] = inner_core
    if pcs_per_roll: job_data["Pcs/Roll"] = pcs_per_roll
    if winding_direction: job_data["Winding Direction"] = winding_direction
    if roll_weight: job_data["Roll Weight (kg)"] = roll_weight
    if length: job_data["Length (mm)"] = length
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
