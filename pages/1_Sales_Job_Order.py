import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Functions for PDF Generation ---
def create_pdf(data_dict):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "SALES JOB ORDER", 0, 1, 'C')
    pdf.ln(5)
    
    def draw_section(title, fields_dict):
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 8, title, 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        for label, val in fields_dict.items():
            if val is not None and str(val).strip() != "":
                pdf.set_fill_color(245, 245, 245)
                if label == "Remarks / Notes" or label == "Delivery Address" or label == "Head Office Address":
                    pdf.cell(190, 7, f"{label}:", 1, 1, 'L', True)
                    pdf.multi_cell(190, 7, str(val), 1, 'L')
                else:
                    pdf.cell(60, 7, f"{label}:", 1, 0, 'L', True)
                    pdf.cell(130, 7, str(val), 1, 1, 'L')
        pdf.ln(3)

    # Grouping Data for PDF
    cust_info = {
        "Date": data_dict.get("Date"),
        "Job Order No": data_dict.get("Job Order No"),
        "Customer Name": data_dict.get("Customer Name"),
        "Customer ID": data_dict.get("Customer ID"),
        "Customer PO#": data_dict.get("Customer PO#"),
        "Sales PO#": data_dict.get("Sales PO#"),
        "Head Office Address": data_dict.get("Head Office Address")
    }
    
    prod_specs = {
        "Product Type": data_dict.get("Product Type"),
        "Product Code": data_dict.get("Product Code"),
        "Material Type": data_dict.get("Material Type"),
        "Density (g/cm3)": data_dict.get("Density (g/cm3)"),
        "Label/Film Width (mm)": data_dict.get("Label/Film Width (mm)"),
        "Repeat Length (mm)": data_dict.get("Repeat Length (mm)"),
        "Thickness (u)": data_dict.get("Thickness (u)"),
        "Colors": data_dict.get("Colors"),
        "Color of Film": data_dict.get("Color of Film"),
        "Artwork Status": data_dict.get("Artwork Status"),
        "Artwork No.": data_dict.get("Artwork No.")
    }
    
    dynamic_specs = {}
    if data_dict.get("Product Type") == "OPP Label (Wrap Around)":
        dynamic_specs = {
            "Mother Roll Length (m)": data_dict.get("Mother Roll Length (m)"),
            "Mother Roll Width (mm)": data_dict.get("Mother Roll Width (mm)"),
            "No. of Lines": data_dict.get("No. of Lines"),
            "Target Edge Trim (mm)": data_dict.get("Target Edge Trim (mm)"),
            "Total Waste (mm)": data_dict.get("Total Waste (mm)"),
            "Unused Waste (mm)": data_dict.get("Unused Waste (mm)"),
            "Pcs/Roll": data_dict.get("Pcs/Roll"),
            "Inner Core": data_dict.get("Inner Core"),
            "Winding Direction": data_dict.get("Winding Direction")
        }
    elif data_dict.get("Product Type") == "Printed PE Shrink Film":
        dynamic_specs = {
            "Inner Core": data_dict.get("Inner Core"),
            "Roll Weight (kg)": data_dict.get("Roll Weight (kg)"),
            "Winding Direction": data_dict.get("Winding Direction")
        }
    elif data_dict.get("Product Type") == "Printed LDPE Bag":
        dynamic_specs = {
            "Bag Length (mm)": data_dict.get("Bag Length (mm)"),
            "Bottom Gusset (mm)": data_dict.get("Bottom Gusset (mm)")
        }

    del_info = {
        "Required Quantity": data_dict.get("Required Quantity"),
        "Packaging": data_dict.get("Packaging"),
        "Due Date": data_dict.get("Due Date"),
        "Delivery City": data_dict.get("Delivery City"),
        "Delivery Address": data_dict.get("Delivery Address"),
        "Remarks / Notes": data_dict.get("Remarks / Notes")
    }

    # Draw Sections
    draw_section("CUSTOMER INFORMATION", cust_info)
    draw_section("PRODUCT SPECIFICATIONS", prod_specs)
    if dynamic_specs:
        draw_section("PRODUCTION DETAILS", dynamic_specs)
    draw_section("QUANTITY, DELIVERY & NOTES", del_info)

    # Approvals
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 8, "APPROVALS", 1, 1, 'C', True)
    pdf.cell(47.5, 15, "Sales", 1, 0, 'C')
    pdf.cell(47.5, 15, "Production", 1, 0, 'C')
    pdf.cell(47.5, 15, "QC", 1, 0, 'C')
    pdf.cell(47.5, 15, "Manager", 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1')

# --- Page configuration ---
st.set_page_config(page_title="Sales Job Order", page_icon="📝", layout="wide")

st.title("📝 Create New Sales Job Order For Printed Item")
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

head_office_address = st.text_input("Company Head Office Address")

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
pcs_per_roll = waste_by_mm = unused_waste = total_labels_calculated = 0

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

        if mother_roll_length > 0 and repeat_length > 0 and no_of_lines > 0:
            total_labels_calculated = pcs_per_roll * no_of_lines
            st.success(f"**💡 Production Estimate for 1 Mother Roll:** Total Exact Quantity: **{total_labels_calculated:,}** PCS")

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
        quantity = st.number_input("Required Quantity by Customer", min_value=0) 
        
        # --- RED WARNING LOGIC ---
        if product_type == "OPP Label (Wrap Around)" and quantity > 0 and total_labels_calculated > 0:
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
        
    delivery_address = st.text_input("Delivery Address")
    notes = st.text_area("Remarks / Notes")

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
        "Due Date": str(due_date),
        "Remarks / Notes": notes
    }
    
    # Add dynamic fields for printing
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
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("💾 Save & Send to Production", type="primary", use_container_width=True):
            st.success("Job Order saved successfully! Ready for production review.")
            
    with btn_col2:
        pdf_file = create_pdf(job_data)
        st.download_button(
            label="📄 Export to PDF",
            data=pdf_file,
            file_name="Job_Order_Export.pdf",
            mime="application/pdf",
            use_container_width=True
        )
