import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Functions for PDF Generation ---
def create_pdf(data_dict):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Sales Job Order - Printed LDPE Bag", ln=True, align='C')
    pdf.ln(5)
    
    # Helper function to prevent UnicodeEncodeError in FPDF
    def safe_txt(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')
    
    # Fields that require a full line
    full_width_fields = ["Head Office Address", "Delivery Address", "Remarks / Notes"]
    
    items = list(data_dict.items())
    i = 0
    
    # Loop to print 2 items per row with borders
    while i < len(items):
        key1, val1 = items[i]
        
        # If the field is a long text, give it a full row
        if key1 in full_width_fields:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, safe_txt(f"{key1}:"), border=1, ln=True, fill=False)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(190, 8, safe_txt(val1), border=1)
            pdf.ln(1)
            i += 1
            continue
        
        # Column 1
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, safe_txt(f"{key1}:"), border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(50, 8, safe_txt(val1)[:40], border=1)
        
        # Column 2
        if i + 1 < len(items) and items[i+1][0] not in full_width_fields:
            key2, val2 = items[i+1]
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(45, 8, safe_txt(f"{key2}:"), border=1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(50, 8, safe_txt(val2)[:40], border=1, ln=True)
            i += 2
        else:
            # End the line with an empty bordered cell to keep the grid perfectly aligned
            pdf.cell(95, 8, "", border=1, ln=True)
            i += 1
            
    # --- Approvals / Signature Boxes ---
    pdf.ln(8)
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(47.5, 8, "Sales", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "Production", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "QC", border=1, align='C', fill=True)
    pdf.cell(47.5, 8, "Manager", border=1, align='C', fill=True, ln=True)
    
    # Empty boxes for signing
    pdf.cell(47.5, 20, "", border=1)
    pdf.cell(47.5, 20, "", border=1)
    pdf.cell(47.5, 20, "", border=1)
    pdf.cell(47.5, 20, "", border=1, ln=True)
            
    return pdf.output(dest='S').encode('latin-1')

# --- Page configuration ---
st.set_page_config(page_title="LDPE Bag Order", page_icon="🛍️", layout="wide")

st.title("🛍️ Create New Job Order - Printed LDPE Bag")
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

# Product type is fixed for this page
st.text_input("Product Type", value="Printed LDPE Bag", disabled=True)

# Row 1: Basic Material Specs
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)")
with col_s2:
    material_type = st.selectbox("Material Type", ["LDPE", "HDPE", "MDPE", "Other"])
with col_s3:
    density = st.selectbox("Density (g/cm3)", [0.92, 0.91, 0.93, 0.94, 0.95, 0.96]) 
with col_s4:
    thickness = st.text_input("Thickness (u)")

# Row 2: Dimensions and Colors
col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Bag Width (mm)", min_value=0.0) 
with col_s6:
    repeat_length = st.number_input("Repeat Length / Pitch (mm)", min_value=0.0)
with col_s7:
    color_choice = st.selectbox("Color of Film", ["Transparent", "White", "Other"])
    if color_choice == "Other":
        color_of_film = st.text_input("Specify Color:")
    else:
        color_of_film = color_choice
with col_s8:
    colors_no = st.number_input("No. of Colors in Printing", min_value=1, max_value=10)

# Row 3: Design Data
col_s9, col_s10 = st.columns(2)
with col_s9:
    artwork = st.selectbox("Artwork Status", ["NEW", "REPEAT"])
with col_s10:
    artwork_no = st.text_input("Artwork No.") 

# Specific Specs for LDPE Bags
st.markdown("### 🔄 LDPE Bag Specifics")
col_d1, col_d2 = st.columns(2)
with col_d1:
    length = st.number_input("Bag Length (mm)", min_value=0.0)
with col_d2:
    bottom_gusset = st.number_input("Bottom Gusset (mm)", min_value=0.0)

st.markdown("---")

# 3. Quantity & Delivery
st.subheader("📦 3. Quantity & Delivery")
col_q1, col_q2, col_q3, col_q4 = st.columns(4) 

with col_q1:
    quantity = st.number_input("Required Quantity (pcs/kg)", min_value=0) 
with col_q2:
    packaging = st.text_input("Packaging", value="Cartons / As Usual")
with col_q3:
    due_date = st.date_input("Due Date of Order", datetime.date.today())
with col_q4:
    delivery_city = st.text_input("Delivery City") 

# Remarks / Notes Section
st.markdown("---")
st.subheader("📝 4. Additional Notes")
notes = st.text_area("Remarks / Notes", placeholder="Enter any specific notes or instructions here...")

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
    "Product Type": "Printed LDPE Bag",
    "Product Code": product_code,
    "Material Type": material_type, 
    "Density (g/cm3)": density,     
    "Bag Width (mm)": width,
    "Repeat Length (mm)": repeat_length, 
    "Bag Length (mm)": length,
    "Bottom Gusset (mm)": bottom_gusset,
    "Thickness (u)": thickness,
    "Colors": colors_no,
    "Color of Film": color_of_film,
    "Artwork Status": artwork,
    "Artwork No.": artwork_no, 
    "Required Quantity": quantity,
    "Packaging": packaging,
    "Due Date": str(due_date),
    "Remarks / Notes": notes
}

st.markdown("<br>", unsafe_allow_html=True)

# --- Action Buttons Row ---
st.subheader("🎯 Actions")
btn_col1, btn_col2 = st.columns(2) 

with btn_col1:
    if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
        st.success("LDPE Bag Job Order saved successfully!")
        
with btn_col2:
    pdf_file = create_pdf(job_data)
    st.download_button(
        label="📄 Export to PDF",
        data=pdf_file,
        file_name="LDPE_Bag_Job_Order.pdf",
        mime="application/pdf",
        use_container_width=True
    )
