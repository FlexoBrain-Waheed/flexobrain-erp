import streamlit as st
from supabase import create_client, Client
from fpdf import FPDF
import base64

# --- 1. Database Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. Page Configurations ---
st.set_page_config(page_title="FlexoBrain ERP", layout="wide", page_icon="🏭")

# --- 3. Professional Lists ---
MATERIALS = ["BOPP Clear", "BOPP White", "PET 12mic", "PE White", "PVC Shrink", "Paper"]
THICKNESS = ["12 mic", "15 mic", "20 mic", "30 mic", "38 mic", "40 mic", "50 mic"]
# Generate Sleeves list from Z-80 to Z-140
SLEEVES = [f"Z-{i} ({round(i*3.175, 2)}mm)" for i in range(80, 141, 4)]
ANILOX_OPTIONS = ["360/4.5 BCM", "800/2.0 BCM", "1000/1.5 BCM", "1200/1.0 BCM"]

# Product Images
PRODUCT_IMAGES = {
    "Labels": "https://img.freepik.com/premium-vector/blank-white-paper-sticker-labels-isolated-white-background-mockup-packaging_120819-270.jpg",
    "Flexible Packaging": "https://5.imimg.com/data5/SELLER/Default/2021/3/EO/RY/MB/13309653/flexible-packaging-pouch-500x500.jpg"
}

# --- 4. PDF Generation Function (A4) ---
def generate_job_order_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(190, 20, "FLEXOBRAIN ERP - JOB ORDER", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    for key, value in data.items():
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 10, f" {key.upper()}", border=1, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(130, 10, f" {value}", border=1, ln=True)
    
    pdf.ln(20)
    pdf.cell(95, 10, "Production Manager Signature: __________")
    pdf.cell(95, 10, "Quality Control Approval: __________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. User Interface (UI) ---
st.title("📂 Master Job Order System")
st.markdown("---")

# Sidebar - Visual Guide
with st.sidebar:
    st.header("🎨 Product Reference")
    category = st.selectbox("Select Category", list(PRODUCT_IMAGES.keys()))
    st.image(PRODUCT_IMAGES[category], caption=f"Typical {category} Structure", use_container_width=True)
    

# Main Entry Form
with st.form("master_order_form"):
    st.subheader("🛠️ Technical Specifications")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        client_name = st.text_input("Client Name")
        po_number = st.text_input("PO Number")
        job_id = st.text_input("Internal Job ID")
    
    with c2:
        material = st.selectbox("Material Type", MATERIALS)
        micron = st.selectbox("Thickness (Micron)", THICKNESS)
        width = st.number_input("Web Width (mm)", value=800.0)
        
    with c3:
        sleeve_z = st.selectbox("Sleeve Size (Z)", SLEEVES)
        anilox_v = st.selectbox("Anilox Selection", ANILOX_OPTIONS)
        target_speed = st.number_input("Target Speed (m/min)", value=300)

    st.markdown("---")
    notes = st.text_area("Special Instructions")

    if st.form_submit_button("🚀 Finalize, Save & Print PDF"):
        final_data = {
            "Client": client_name, "PO": po_number, "Internal ID": job_id,
            "Material": material, "Micron": micron, "Width (mm)": str(width),
            "Sleeve": sleeve_z, "Anilox": anilox_v, "Speed": str(target_speed),
            "Instructions": notes
        }
        
        try:
            # Save basic info to Supabase (ensure table structure matches)
            supabase.table("job_orders").insert({
                "client_name": client_name, 
                "po_number": po_number
            }).execute()
            
            st.success("✔️ Order Successfully Saved to Cloud!")
            
            # Generate and View PDF
            pdf_bytes = generate_job_order_pdf(final_data)
            
            # PDF Preview (Iframe)
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
            st.markdown("### 📄 Job Order Preview (A4)")
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Download Button
            st.download_button(label="📥 Download Official PDF", data=pdf_bytes, file_name=f"Job_Order_{client_name}.pdf", mime='application/pdf')
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Error Saving Data: {e}")
