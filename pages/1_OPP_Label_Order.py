import streamlit as st
import datetime
import pandas as pd
import io
import tempfile
import os
from fpdf import FPDF
import sys
from pathlib import Path
from PIL import Image
from supabase import create_client, Client

# --- Page configuration ---
st.set_page_config(page_title="BOPP Label Order", page_icon="📝", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth
auth.require_role(["sales"])
auth.logout_button()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 16 - FlexoBrain FULL RESTORE</div>", unsafe_allow_html=True)

# ==========================================
# --- Supabase Database Connection ---
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("⚠️ Database connection failed.")
    st.stop()

# ==========================================
# --- Helper Functions ---
# ==========================================
def safe_idx(opt_list, val):
    try:
        return opt_list.index(val)
    except:
        return 0

def generate_order_number(supabase_client):
    today_str = datetime.date.today().strftime("%Y%m%d")
    prefix = f"BOPP-{today_str}-"
    try:
        response = supabase_client.table("job_orders").select("order_number").execute()
        seqs = [int(row['order_number'].split('-')[-1]) for row in response.data if row.get('order_number', '').startswith(prefix)]
        next_seq = max(seqs) + 1 if seqs else 1
        return f"{prefix}{next_seq:03d}"
    except:
        return f"{prefix}999"

auto_job_order_no = generate_order_number(supabase)

# ==========================================
# --- PDF Generation (With Stamp & Artwork) ---
# ==========================================
def create_pdf(data_dict, image_file=None, artwork_url=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"FlexoBrain Job Order: {data_dict.get('Job Order No')}", ln=True, align='C')
    
    def safe_txt(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
    def section_h(t):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(190, 8, safe_txt(t), border=1, ln=True, fill=True)
    def r2(k1, v1, k2, v2):
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 8, safe_txt(k1)+":", border=1)
        pdf.set_font("Arial", '', 10); pdf.cell(50, 8, safe_txt(v1), border=1)
        pdf.set_font("Arial", 'B', 10); pdf.cell(45, 8, safe_txt(k2)+":", border=1)
        pdf.set_font("Arial", '', 10); pdf.cell(50, 8, safe_txt(v2), border=1, ln=True)

    section_h("1. Order Information")
    r2("Job Order No", data_dict.get("Job Order No"), "Date", data_dict.get("Date"))
    r2("Customer Name", data_dict.get("Customer Name"), "Customer ID", data_dict.get("Customer ID"))
    pdf.ln(2)

    # Stamp
    pdf.ln(10)
    pdf.set_fill_color(245, 245, 245); pdf.rect(10, pdf.get_y(), 190, 30, 'F')
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 8, "  ✅ Digitally Approved & Sealed", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"  By: Eng. Amro | Timestamp: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)

    if image_file or artwork_url:
        pdf.add_page()
        pdf.cell(0, 10, "Approved Design Artwork", ln=True, align='C')
        if image_file:
            img = Image.open(image_file).convert('RGB')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img.save(tmp.name, format="JPEG")
                pdf.image(tmp.name, x=10, y=30, w=190)
        elif artwork_url: pdf.image(artwork_url, x=10, y=30, w=190)

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# --- Main UI ---
# ==========================================
st.title("📝 Create New Job Order")
old_order = st.session_state.get('repeat_data', {})

# --- 1. Customer Info ---
st.subheader("👤 1. Customer Information")
c1, c2, c3 = st.columns(3)
with c1:
    date = st.date_input("Date", datetime.date.today())
    company_name = st.text_input("Company Name", value=old_order.get("customer_name", ""))
with c2:
    job_order_no = st.text_input("Job Order No.", value=auto_job_order_no, disabled=True)
    customer_id = st.text_input("Customer ID", value=old_order.get("customer_id", ""))
with c3:
    po_number = st.text_input("Customer's PO#")
    sales_po = st.text_input("Sales PO#")

ca1, ca2, ca3 = st.columns([2, 2, 1])
with ca1: head_office = st.text_input("Head Office Address")
with ca2: delivery_addr = st.text_input("Delivery Address")
with ca3: delivery_city = st.text_input("Delivery City", value=old_order.get("delivery_city", ""))

st.markdown("---")
# --- 2. Product Specs ---
st.subheader("⚙️ 2. Product Specs")
st.text_input("Product Type", value="BOPP Wrap Around Label", disabled=True)

cs1, cs2, cs3, cs4 = st.columns(4)
with cs1: product_code = st.text_input("Product Code (SAP)", value=old_order.get("product_code", ""))
with cs2:
    mat_ops = ["BOPP", "PETG", "PE", "Other"]
    material_type = st.selectbox("Material Type", mat_ops, index=safe_idx(mat_ops, old_order.get("material_type", "BOPP")))
with cs3:
    den_ops = [0.91, 0.92, 1.40]
    density = st.selectbox("Density (g/cm3)", den_ops, index=safe_idx(den_ops, float(old_order.get("density", 0.91))))
with cs4:
    thk_ops = [30, 35, 38, 40]
    thickness = st.selectbox("Thickness (u)", thk_ops, index=safe_idx(thk_ops, int(old_order.get("thickness_micron", 30))))

cs5, cs6, cs7, cs8 = st.columns(4)
with cs5: width = st.number_input("Label Width (mm)", value=float(old_order.get("label_width_mm", 0.0)))
with cs6: repeat = st.number_input("Repeat Length (mm)", value=float(old_order.get("repeat_length_mm", 0.0)))
with cs7: film_color = st.text_input("Film Color", value=old_order.get("color_of_film", "Transparent"))
with cs8: colors = st.number_input("No. of Colors", min_value=1, value=int(old_order.get("colors_count", 1)))

cs9, cs10 = st.columns(2)
with cs9:
    art_ops = ["NEW", "REPEAT"]
    art_status = st.selectbox("Artwork Status", art_ops, index=safe_idx(art_ops, "REPEAT" if old_order else "NEW"))
with cs10: art_no = st.text_input("Artwork No.", value=old_order.get("artwork_number", ""))

# --- Calculator ---
st.markdown("#### 🧮 Smart Web & Production Calculator")
cc1, cc2, cc3, cc4 = st.columns(4)
with cc1: mr_len = st.number_input("Mother Roll Length (m)", value=float(old_order.get("mother_roll_length_m", 0.0)))
with cc2: rolls_no = st.number_input("No. of Rolls", min_value=1, value=int(old_order.get("no_of_rolls", 1)))
with cc3: mr_width = st.number_input("Mother Roll Width (mm)", value=float(old_order.get("mother_roll_width_mm", 0.0)))
with cc4: lines_no = st.number_input("No. of Lines", min_value=1, value=int(old_order.get("no_of_lines", 1)))

edge_trim = st.number_input("Target Edge Trim (mm)", value=float(old_order.get("edge_trim_mm", 24.0)))

# Results
pcs_per_roll = int((mr_len * 1000) / repeat) if mr_len > 0 and repeat > 0 else 0
total_qty_calc = pcs_per_roll * lines_no * rolls_no
waste_mm = float(mr_width - (width * lines_no)) if mr_width > 0 else 0.0
unused_waste = float(waste_mm - edge_trim)

col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric("Pcs / Roll", f"{pcs_per_roll:,}")
col_res2.metric("Total Waste (mm)", f"{waste_mm:.2f}")
col_res3.metric("Unused Waste (mm)", f"{unused_waste:.2f}")

st.info(f"💡 Calculated Total Quantity: **{total_qty_calc:,}** PCS")

st.markdown("---")
# --- 3. Final Section ---
st.subheader("📦 3. Quantity, Delivery & Artwork")
uploaded_design = st.file_uploader("🖼️ Upload NEW Design", type=["jpg", "png", "jpeg"])
final_art_url = ""
if uploaded_design: 
    st.image(uploaded_design, width=200); final_art_url = "new_upload"
elif old_order.get('artwork_url'):
    st.success("🔄 USING EXISTING DESIGN"); st.image(old_order.get('artwork_url'), width=200); final_art_url = old_order.get('artwork_url')

# Sync Quantity
qty = st.number_input("Required Quantity", min_value=0, value=total_qty_calc, step=1000)

cq1, cq2, cq3 = st.columns(3)
with cq1: packaging = st.text_input("Packaging Notes", value=old_order.get("packaging_notes", "Suitable / As Usual"))
with cq2: due_date = st.date_input("Due Date", datetime.date.today())
with cq3: delivery_city_final = st.text_input("Delivery City (Final Check)", value=delivery_city)

notes = st.text_area("Remarks / Notes")

# Save
if st.button("💾 Save to Cloud & Send", type="primary"):
    if not company_name: st.error("❌ Customer Name Required")
    else:
        try:
            f_no = generate_order_number(supabase)
            data = {
                "order_number": f_no, "customer_name": company_name, "customer_id": customer_id,
                "delivery_city": delivery_city_final, "product_code": product_code, "material_type": material_type,
                "density": float(density), "thickness_micron": float(thickness), "label_width_mm": float(width),
                "repeat_length_mm": float(repeat), "color_of_film": film_color, "colors_count": int(colors),
                "artwork_url": final_art_url, "artwork_status": art_status, "artwork_number": art_no,
                "mother_roll_length_m": float(mr_len), "no_of_rolls": int(rolls_no), "no_of_lines": int(lines_no),
                "mother_roll_width_mm": float(mr_width), "edge_trim_mm": float(edge_trim),
                "required_quantity": int(qty), "packaging_notes": packaging, "due_date": str(due_date),
                "remarks": notes, "status": "pending"
            }
            supabase.table("job_orders").insert(data).execute()
            st.success(f"✅ Saved as {f_no}"); st.balloons()
            if 'repeat_data' in st.session_state: del st.session_state['repeat_data']
            st.rerun()
        except Exception as e: st.error(f"❌ Error: {e}")

# PDF
pdf_data = {"Job Order No": job_order_no, "Date": str(date), "Customer Name": company_name, "Customer ID": customer_id, "Delivery Address": f"{delivery_addr}, {delivery_city_final}", "Material Type": material_type, "Thickness (u)": str(thickness), "Density (g/cm3)": str(density), "Required Quantity": str(qty), "Due Date": str(due_date), "Packaging": packaging, "Remarks / Notes": notes}
st.download_button("📄 Export PDF", data=create_pdf(pdf_data, uploaded_design, final_art_url if final_art_url.startswith("http") else None), file_name=f"{job_order_no}.pdf")
