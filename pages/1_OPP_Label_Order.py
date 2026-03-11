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
    pdf.cell(0, 10, "Sales Job Order For Printed Item", ln=True, align='C')
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
st.set_page_config(page_title="OPP Label Order", page_icon="📝", layout="wide")

# --- تقسيم المنطقة العلوية لإضافة الأيقونة على اليمين ---
col_title, col_icon = st.columns([5, 1]) 

with col_title:
    st.title("📝 Create New Job Order - OPP Label (Wrap Around)")

with col_icon:
    # --- MODIFIED: رسم SVG يجمع بين (العلبة) و (الرول) والأسهم بناءً على الصورة المرجعية ---
    st.markdown(
        """
        <div style="border: 2px solid #ddd; padding: 10px; border-radius: 10px; text-align: center; background-color: white; display: flex; justify-content: center;">
            <svg width="120" height="70" viewBox="0 0 120 70" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#555" />
                    </marker>
                </defs>
                
                <rect x="14" y="10" width="12" height="4" rx="1" fill="#ddd" stroke="#555" stroke-width="1.5"/>
                <rect x="10" y="15" width="20" height="40" rx="4" fill="#f9f9f9" stroke="#555" stroke-width="1.5"/>
                <rect x="10" y="30" width="20" height="15" fill="#ddd" stroke="#555" stroke-width="1.5"/>
                
                <path d="M 90 20 C 100 20, 105 27, 105 35 C 105 43, 100 50, 90 50" fill="#f0f0f0" stroke="#555" stroke-width="1.5"/>
                <path d="M 90 20 L 50 20 L 50 50 L 90 50 Z" fill="#fff" stroke="#555" stroke-width="1.5"/>
                <ellipse cx="90" cy="35" rx="6" ry="15" fill="#f9f9f9" stroke="#555" stroke-width="1.5"/>
                <ellipse cx="90" cy="35" rx="2" ry="5" fill="#fff" stroke="#555" stroke-width="1.5"/>
                
                <rect x="55" y="25" width="25" height="20" rx="2" fill="#313131"/>
                <text x="67.5" y="38" font-family="Arial" font-size="7" fill="#fff" text-anchor="middle">LABEL</text>
                
                <line x1="50" y1="60" x2="100" y2="60" stroke="#555" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
            </svg>
        </div>
        """, 
        unsafe_allow_html=True
    )

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
st.text_input("Product Type", value="OPP Label (Wrap Around)", disabled=True)

# Row 1: Basic Material Specs
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    product_code = st.text_input("Product Code (SAP)")
with col_s2:
    material_type = st.selectbox("Material Type", ["BOPP", "PETG", "PE", "Other"])
with col_s3:
    density = st.selectbox("Density (g/cm3)", [0.91, 0.92, 1.40]) 
with col_s4:
    thickness = st.selectbox("Thickness (u)", [30, 35, 38, 40])

# Row 2: Dimensions and Colors
col_s5, col_s6, col_s7, col_s8 = st.columns(4)
with col_s5:
    width = st.number_input("Label Width (mm)", min_value=0.0) 
with col_s6:
    repeat_length = st.number_input("Repeat Length (mm)", min_value=0.0)
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

# 3. Dynamic Section based on OPP
st.markdown("### 🔄 Specific Specs for: OPP Label")

st.markdown("#### 🧻 Print, Core & Winding Specifications")

col_w1, col_w2 = st.columns(2)
with col_w1:
    print_position = st.selectbox("Print Surface", ["Reverse Print", "Surface Print"])

col_d1, col_d2, col_d3, col_d4 = st.columns(4)
with col_d1:
    inner_core = st.selectbox("Inner Core Diameter", ["3 inch", "6 inch"], index=1)
with col_d2:
    core_type = st.selectbox("Core Type", ["Paper", "Plastic"])
with col_d3:
    core_thickness = st.number_input("Wall Thickness (mm)", min_value=0.0)
with col_d4:
    winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])

# --- SMART CALCULATOR & VALIDATION SECTION ---
st.markdown("#### 🧮 Smart Web & Production Calculator")

col_calc1, col_calc_rolls, col_calc2, col_calc3 = st.columns(4)
with col_calc1:
    mother_roll_length = st.number_input("Mother Roll Length (m)", min_value=0)
with col_calc_rolls:
    no_of_rolls = st.number_input("No. of Rolls", min_value=1, value=1)
with col_calc2:
    mother_roll_width = st.number_input("Mother Roll Width (mm)", min_value=0)
with col_calc3:
    no_of_lines = st.number_input("No. of Lines (Lanes)", min_value=1, value=1)
    
col_calc4, col_calc5, col_calc6, col_calc7 = st.columns(4)
with col_calc4:
    edge_trim = st.number_input("Target Edge Trim (mm)", min_value=0, value=24)

# Variable Initialization for calculations
pcs_per_roll = 0
waste_by_mm = 0.0
unused_waste = 0.0
total_labels_calculated = 0
    
# Calculation Logic
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

if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0 and no_of_rolls > 0:
    total_labels_calculated = pcs_per_roll * no_of_lines * no_of_rolls
    st.success(f"**💡 Production Estimate for {no_of_rolls} Mother Roll(s):** Total Exact Quantity: **{total_labels_calculated:,}** PCS")

st.markdown("---")

# 4. Quantity & Delivery
st.subheader("📦 3. Quantity & Delivery")
col_q1, col_q2, col_q3, col_q4 = st.columns(4) 

with col_q1:
    quantity = st.number_input("Required Quantity by Customer", min_value=0) 
    
    # --- RED WARNING LOGIC ---
    if quantity > 0 and total_labels_calculated > 0:
        if quantity != total_labels_calculated:
            st.markdown(
                f"<p style='color:red; font-size:14px; font-weight:bold;'>🚨 WARNING: Requested Quantity ({quantity:,}) does NOT match Calculated Production ({total_labels_calculated:,})!</p>", 
                unsafe_allow_html=True
            )

with col_q2:
    packaging = st.text_input("Packaging", value="Suitable / As Usual")
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
    "Product Type": "OPP Label (Wrap Around)",
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
    "Print Surface": print_position,
    "Inner Core": inner_core,
    "Core Type": core_type,                 
    "Wall Thickness (mm)": core_thickness,  
    "Winding Direction": winding_direction,
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
        st.success("OPP Job Order saved successfully! Ready for production review.")
        
with btn_col2:
    pdf_file = create_pdf(job_data)
    st.download_button(
        label="📄 Export to PDF",
        data=pdf_file,
        file_name="OPP_Job_Order.pdf",
        mime="application/pdf",
        use_container_width=True
    )
