import streamlit as st
import datetime
from fpdf import FPDF
import pandas as pd
import auth 

# ==========================================
# 1. Security & Page Configuration
# ==========================================
# Only Production staff or Admins can access this page
auth.require_role(["production", "admin"])

st.set_page_config(
    page_title="Plate Management", 
    page_icon="🖨️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. Custom CSS
# ==========================================
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .job-badge { background-color: #EFF6FF; border-left: 6px solid #3B82F6; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .job-text { font-size: 1.3rem; color: #1E293B; font-weight: bold; margin: 5px 0;}
    .color-badge { background-color: #475569; color: white; padding: 5px 12px; border-radius: 15px; font-size: 1rem; margin-right: 5px; display: inline-block;}
    
    .alert-green { background-color: #D1FAE5; color: #065F46; padding: 15px; border-radius: 10px; font-weight: bold; border: 2px solid #10B981; }
    .alert-red { background-color: #FEE2E2; color: #991B1B; padding: 15px; border-radius: 10px; font-weight: bold; border: 2px solid #EF4444; }
    .alert-yellow { background-color: #FEF3C7; color: #92400E; padding: 15px; border-radius: 10px; font-weight: bold; border: 2px solid #F59E0B; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🖨️ Plate Management & Storage Hub</div>", unsafe_allow_html=True)

# ==========================================
# 3. Mock Database (ERP Integration)
# ==========================================
# In a real ERP, this fetches data based on the scanned Job Order
if 'plate_jobs_db' not in st.session_state:
    st.session_state['plate_jobs_db'] = {
        "ORD-9055": {
            "client": "Al-Marai",
            "design_name": "Al-Marai Orange Juice 1L",  # Single Source of Truth
            "job_type": "New Job",
            "colors": ["Cyan", "Magenta", "Yellow", "Black", "Pantone 021 Orange"],
            "status": "Pending", # Pending -> Ordered -> Received -> Approved/Rejected
            "rack_no": ""
        },
        "ORD-9056": {
            "client": "Nada Dairy",
            "design_name": "Nada Greek Yogurt 150g",
            "job_type": "Repeat Job",
            "colors": ["Cyan", "Magenta", "Yellow", "Black", "Pantone 286 Blue"],
            "status": "Ordered",
            "rack_no": "Rack A-05" # Already has a rack because it's a repeat
        }
    }

db = st.session_state['plate_jobs_db']

# ==========================================
# 4. PDF Generator Function
# ==========================================
def generate_plate_order_pdf(job_id, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    title = "NEW PLATE PRODUCTION ORDER" if data['job_type'] == "New Job" else "PLATE RETRIEVAL SLIP"
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Job Order No: {job_id}", ln=True)
    pdf.cell(0, 8, f"Client: {data['client']}", ln=True)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, f"Design / Plate Name: {data['design_name']}", ln=True)
    
    if data['job_type'] == "Repeat Job":
        pdf.set_text_color(220, 20, 20) # Red color for Rack location
        pdf.cell(0, 12, f"STORAGE LOCATION: {data['rack_no']}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Required Colors ({len(data['colors'])}):", ln=True)
    pdf.set_font("Arial", '', 12)
    for color in data['colors']:
        pdf.cell(0, 8, f"- {color}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. UI: Scanning & Loading Job
# ==========================================
st.markdown("### 🔍 Scan Job Order Ticket")
scanned_job = st.text_input("Enter Job Order No:", placeholder="e.g., ORD-9055")
st.markdown("---")

if scanned_job:
    if scanned_job in db:
        job = db[scanned_job]
        
        # --- HEADER SECTION (Read-Only) ---
        col_info, col_status = st.columns([2, 1])
        with col_info:
            st.markdown(f"""
                <div class='job-badge'>
                    <div class='job-text'>📦 Job Order: {scanned_job} | {job['client']}</div>
                    <div class='job-text' style='color: #DC2626;'>🖼️ Plate / Design Name: {job['design_name']}</div>
                    <div class='job-text'>🔄 Job Type: {job['job_type']}</div>
                    <hr style='border-color: #94A3B8; margin: 10px 0;'>
                    <div style='margin-bottom: 5px;'><b>🎨 Required Colors:</b></div>
                    {''.join([f"<span class='color-badge'>{c}</span>" for c in job['colors']])}
                </div>
            """, unsafe_allow_html=True)
            
        with col_status:
            # Dynamic Status Alert
            if job['status'] == "Pending":
                st.markdown("<div class='alert-yellow'>⚠️ Status: Pending Procurement</div>", unsafe_allow_html=True)
            elif job['status'] == "Ordered":
                st.markdown("<div class='alert-yellow'>⏳ Status: Ordered / Pending Delivery</div>", unsafe_allow_html=True)
            elif job['status'] == "Received":
                st.markdown("<div class='alert-green'>🟢 Status: Received (Awaiting QC)</div>", unsafe_allow_html=True)
            elif job['status'] == "Approved":
                st.markdown("<div class='alert-green'>✅ Status: APPROVED & Ready for Mounting</div>", unsafe_allow_html=True)
            elif job['status'] == "Rejected":
                st.markdown("<div class='alert-red'>❌ Status: REJECTED & Returned</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # --- WORKFLOW LOGIC ---
        
        # STEP 1: PROCUREMENT (Print PDF)
        if job['status'] in ["Pending", "Ordered"]:
            st.markdown("### 🖨️ Step 1: Plate Procurement / Retrieval")
            
            pdf_data = generate_plate_order_pdf(scanned_job, job)
            btn_text = "📄 Generate NEW Plate Order PDF" if job['job_type'] == "New Job" else "📄 Print Warehouse RETRIEVAL Slip"
            
            if st.download_button(label=btn_text, data=pdf_data, file_name=f"Plate_Order_{scanned_job}.pdf", mime="application/pdf", use_container_width=True):
                st.session_state['plate_jobs_db'][scanned_job]['status'] = "Ordered"
                st.rerun()

        # STEP 2: RECEIVING & STORAGE
        if job['status'] == "Ordered":
            st.markdown("### 📥 Step 2: Receiving & Storage Allocation")
            st.info("When plates physically arrive or are retrieved, assign them a storage rack and mark as received.")
            
            c1, c2 = st.columns(2)
            with c1:
                # If it's a repeat job, pre-fill the rack number
                default_rack = job['rack_no'] if job['rack_no'] else ""
                rack_input = st.text_input("📍 Assign Storage Rack Number (Required):", value=default_rack, placeholder="e.g., Rack B-12")
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📦 Mark Plates as RECEIVED", type="primary", use_container_width=True):
                    if rack_input.strip() == "":
                        st.error("You must enter a Storage Rack Number to proceed!")
                    else:
                        st.session_state['plate_jobs_db'][scanned_job]['rack_no'] = rack_input
                        st.session_state['plate_jobs_db'][scanned_job]['status'] = "Received"
                        st.rerun()

        # STEP 3: QUALITY CONTROL & INTERLOCK
        if job['status'] == "Received":
            st.markdown("### 🔬 Step 3: Quality Control Check")
            st.write(f"Plates are currently stored at: **{job['rack_no']}**")
            
            col_app, col_rej = st.columns(2)
            
            with col_app:
                if st.button("✅ APPROVE All Plates (Send to Mounting)", use_container_width=True):
                    st.session_state['plate_jobs_db'][scanned_job]['status'] = "Approved"
                    st.balloons()
                    st.rerun()
                    
            with col_rej:
                # Toggle Rejection Matrix
                if 'show_rejection' not in st.session_state:
                    st.session_state['show_rejection'] = False
                    
                if st.button("❌ REJECT & Return to Supplier", use_container_width=True):
                    st.session_state['show_rejection'] = not st.session_state['show_rejection']

            # THE REJECTION MATRIX
            if st.session_state.get('show_rejection', False):
                st.markdown("<br><div class='alert-red'>📋 Rejection Report Matrix</div>", unsafe_allow_html=True)
                st.write("Please specify exactly which colors are rejected and why:")
                
                with st.form("rejection_form"):
                    rejected_colors = []
                    for i, color in enumerate(job['colors']):
                        rc1, rc2 = st.columns([1, 2])
                        with rc1:
                            is_rejected = st.checkbox(f"Reject: {color}", key=f"chk_{i}")
                        with rc2:
                            reason = st.selectbox(
                                "Reason for rejection:", 
                                ["-- Select Reason --", "Damaged Dot / Surface", "Registration Error", "Wrong Plate Thickness", "Artwork/Design Error", "Missing Color"], 
                                key=f"rsn_{i}",
                                disabled=not is_rejected
                            )
                        if is_rejected and reason != "-- Select Reason --":
                            rejected_colors.append({"color": color, "reason": reason})
                            
                    notes = st.text_area("Additional Notes (Optional)")
                    
                    if st.form_submit_button("🚨 Submit Official Rejection", type="primary", use_container_width=True):
                        if not rejected_colors:
                            st.warning("Please select at least one color and reason for rejection.")
                        else:
                            st.session_state['plate_jobs_db'][scanned_job]['status'] = "Rejected"
                            st.session_state['show_rejection'] = False
                            st.error(f"Rejection logged for {len(rejected_colors)} plate(s). Order locked.")
                            # In production, this data (rejected_colors) would be saved to a database for end-of-month cost analysis
                            st.rerun()

    else:
        st.warning("⚠️ Job Order not found. Please check the number.")
