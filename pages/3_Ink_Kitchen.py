import streamlit as st
import math
import datetime
import io
from fpdf import FPDF

# ==========================================
# 1. Page Configuration & Kiosk Mode
# ==========================================
st.set_page_config(
    page_title="Ink Kitchen & QC", 
    page_icon="🎨", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. Custom CSS for Ink Kitchen UI
# ==========================================
st.markdown("""
    <style>
    .kitchen-title { font-size: 3rem; font-weight: bold; text-align: center; color: #4F46E5; margin-bottom: 20px;}
    .section-header { font-size: 1.8rem; font-weight: bold; color: #111827; margin-bottom: 15px; border-bottom: 3px solid #E5E7EB; padding-bottom: 10px;}
    
    .golden-box { background-color: #FEF3C7; border-left: 8px solid #F59E0B; padding: 20px; border-radius: 10px; margin-bottom: 15px;}
    .golden-text { font-size: 1.4rem; color: #92400E; font-weight: bold; margin: 5px 0;}
    
    .stNumberInput input { font-size: 1.8rem !important; text-align: center; height: 70px !important; border: 2px solid #4F46E5 !important;}
    .stNumberInput label { font-size: 1.4rem !important; font-weight: bold; color: #374151;}
    .stTextInput input, .stSelectbox select { font-size: 1.2rem !important; }
    
    .btn-approve { height: 90px; font-size: 2rem; font-weight: bold; border-radius: 12px; background-color: #10B981; color: white; border: none; width: 100%; transition: 0.3s;}
    .btn-warning { height: 90px; font-size: 2rem; font-weight: bold; border-radius: 12px; background-color: #F59E0B; color: white; border: none; width: 100%; transition: 0.3s;}
    
    .alert-green { background-color: #D1FAE5; color: #065F46; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #10B981;}
    .alert-red { background-color: #FEE2E2; color: #991B1B; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #EF4444;}
    .alert-yellow { background-color: #FEF3C7; color: #92400E; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #F59E0B;}
    
    /* Styling for the Tabs (10 colors handling) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 1.5rem; font-weight: bold; padding: 15px 25px; background-color: #f0f2f6; border-radius: 10px 10px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #4F46E5 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='kitchen-title'>🎨 FlexoBrain - Ink Kitchen & Color QC</div>", unsafe_allow_html=True)

# ==========================================
# 3. Mock Database (Golden References)
# Handling multiple colors per job
# ==========================================
if 'golden_db' not in st.session_state:
    st.session_state['golden_db'] = {
        "BOPP-20260413-001 (Al-Marai)": {
            "job_no": "BOPP-20260413-001",
            "client": "Al-Marai",
            "colors": [
                {
                    "color_name": "Green (Pantone 347)",
                    "material": "BOPP Transparent",
                    "drawdown_bar": "Mayer Bar #3",
                    "target_L": 50.0, "target_a": -40.0, "target_b": 20.0,
                    "viscosity": 22,
                    "recipe": "70% Green, 20% White, 10% Solvent"
                },
                {
                    "color_name": "White (Backing)",
                    "material": "BOPP Transparent",
                    "drawdown_bar": "Mayer Bar #4",
                    "target_L": 95.0, "target_a": 0.0, "target_b": -2.0,
                    "viscosity": 24,
                    "recipe": "90% Titanium White, 10% Solvent"
                }
            ]
        }
    }

golden_db = st.session_state['golden_db']

# ==========================================
# 4. PDF Generation Engine
# ==========================================
def create_qc_pdf(job_no, color_name, target, actual, delta_e, status, user="Ink Technician"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Color Quality Control (QC) Certificate", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Job Number: {job_no}", ln=True)
    pdf.cell(0, 8, f"Color Name: {color_name}", ln=True)
    pdf.cell(0, 8, f"Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Operator: {user}", ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(95, 10, "Target (Golden Reference)", border=1, fill=True)
    pdf.cell(95, 10, "Actual (New Batch)", border=1, ln=True, fill=True)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 8, f"L*: {target['target_L']} | a*: {target['target_a']} | b*: {target['target_b']}", border=1)
    pdf.cell(95, 8, f"L*: {actual['L']} | a*: {actual['a']} | b*: {actual['b']}", border=1, ln=True)
    
    pdf.cell(95, 8, f"Viscosity: {target['viscosity']} sec", border=1)
    pdf.cell(95, 8, f"Viscosity: {actual['visc']} sec", border=1, ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Delta E (Color Difference): {delta_e:.2f}", ln=True)
    pdf.cell(0, 10, f"QC Decision: {status.upper()}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. Operating Mode Selection
# ==========================================
mode = st.radio("🛠️ Operating Mode:", ["🔬 QC Mode (Match Existing Job)", "✍️ Master Mode (Create New Golden Ref)"], horizontal=True)
st.markdown("---")

if mode == "✍️ Master Mode (Create New Golden Ref)":
    st.markdown("<div class='section-header'>🌟 Create New Golden Reference</div>", unsafe_allow_html=True)
    st.info("Use this mode after successfully printing a NEW job. Record the approved values here to serve as the Golden Reference for future repeats.")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        new_job_no = st.text_input("Job Order No (e.g., BOPP-20260415-001)")
        new_client = st.text_input("Client Name")
        new_color_name = st.text_input("Color Name / Code (e.g., Pantone 185 C)")
        new_material = st.selectbox("Proofing Substrate", ["BOPP Transparent", "BOPP White", "PETG", "PE Clear", "Paper"])
        new_bar = st.selectbox("Drawdown Bar Method", ["Mayer Bar #2", "Mayer Bar #3", "Mayer Bar #4", "IGT Tester"])
    with m_col2:
        n_L = st.number_input("Target L*", step=0.1, value=50.0)
        n_a = st.number_input("Target a*", step=0.1, value=0.0)
        n_b = st.number_input("Target b*", step=0.1, value=0.0)
        n_visc = st.number_input("Target Viscosity (Sec)", step=1, value=22)
        new_recipe = st.text_area("Approved Recipe Formulation")
        
    if st.button("💾 SAVE AS GOLDEN REFERENCE", type="primary"):
        if new_job_no and new_color_name:
            job_key = f"{new_job_no} ({new_client})"
            color_data = {
                "color_name": new_color_name, "material": new_material, "drawdown_bar": new_bar,
                "target_L": n_L, "target_a": n_a, "target_b": n_b, "viscosity": n_visc, "recipe": new_recipe
            }
            if job_key not in st.session_state['golden_db']:
                st.session_state['golden_db'][job_key] = {"job_no": new_job_no, "client": new_client, "colors": []}
            st.session_state['golden_db'][job_key]["colors"].append(color_data)
            st.success(f"✅ Saved {new_color_name} to Golden DB!")
        else:
            st.error("Please fill Job No and Color Name.")

# ==========================================
# 6. QC Mode (The 10 Colors Handler)
# ==========================================
elif mode == "🔬 QC Mode (Match Existing Job)":
    selected_job = st.selectbox("🔍 Select Job Order to load Golden References:", ["-- Select Job --"] + list(golden_db.keys()))

    if selected_job != "-- Select Job --":
        job_data = golden_db[selected_job]
        colors = job_data["colors"]
        
        # Create TABS dynamically based on number of colors
        color_names = [c["color_name"] for c in colors]
        tabs = st.tabs(color_names)
        
        # Loop through each tab and color data
        for i, tab in enumerate(tabs):
            with tab:
                ref = colors[i]
                
                col_ref, col_new = st.columns(2)
                
                # LEFT: Golden Reference
                with col_ref:
                    st.markdown("<div class='section-header'>🏆 The Golden Reference</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class='golden-box'>
                            <div class='golden-text'>🎨 Color: {ref['color_name']}</div>
                            <div class='golden-text'>🎞️ Substrate: {ref['material']}</div>
                            <div class='golden-text'>🖌️ Drawdown Tool: {ref['drawdown_bar']}</div>
                            <hr style='border-color: #F59E0B;'>
                            <div class='golden-text'>🎯 Target L: {ref['target_L']}</div>
                            <div class='golden-text'>🎯 Target a: {ref['target_a']}</div>
                            <div class='golden-text'>🎯 Target b: {ref['target_b']}</div>
                            <div class='golden-text'>💧 Target Viscosity: {ref['viscosity']} Sec</div>
                            <hr style='border-color: #F59E0B;'>
                            <div class='golden-text'>📝 Approved Recipe:</div>
                            <div style='font-size: 1.2rem; color: #333;'>{ref['recipe']}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # RIGHT: New Batch Input
                with col_new:
                    st.markdown("<div class='section-header'>🔬 New Batch Input (X-Rite)</div>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: L_actual = st.number_input(f"L* (Lightness)", value=ref['target_L'], step=0.1, format="%.1f", key=f"L_{i}")
                    with c2: a_actual = st.number_input(f"a* (Red/Green)", value=ref['target_a'], step=0.1, format="%.1f", key=f"a_{i}")
                    with c3: b_actual = st.number_input(f"b* (Yellow/Blue)", value=ref['target_b'], step=0.1, format="%.1f", key=f"b_{i}")
                    
                    viscosity_actual = st.number_input("💧 Current Viscosity (Sec)", value=ref['viscosity'], step=1, key=f"v_{i}")
                    
                    # Delta E Math
                    delta_L = L_actual - ref['target_L']
                    delta_a = a_actual - ref['target_a']
                    delta_b = b_actual - ref['target_b']
                    delta_e = math.sqrt((delta_L ** 2) + (delta_a ** 2) + (delta_b ** 2))
                    viscosity_diff = abs(viscosity_actual - ref['viscosity'])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.metric(label="ΔE (Color Difference)", value=f"{delta_e:.2f}", delta=f"{delta_e - 2.0:.2f} from limit", delta_color="inverse")

                    # Decision Engine & PDF
                    pdf_data = create_qc_pdf(
                        job_no=job_data['job_no'], color_name=ref['color_name'],
                        target=ref, actual={'L': L_actual, 'a': a_actual, 'b': b_actual, 'visc': viscosity_actual},
                        delta_e=delta_e, status="Approved" if delta_e <= 2 else ("Warning" if delta_e <= 3 else "Rejected")
                    )

                    if delta_e <= 2.0 and viscosity_diff <= 2:
                        st.markdown("<div class='alert-green'>🟢 APPROVED!</div>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button(f"✅ APPROVE {ref['color_name']}", use_container_width=True, key=f"app_{i}"): st.success("Approved!")
                        with b2:
                            st.download_button("📄 Print QC Certificate", data=pdf_data, file_name=f"QC_{ref['color_name']}.pdf", mime="application/pdf", use_container_width=True, key=f"pdf_g_{i}")
                    
                    elif delta_e <= 2.0 and viscosity_diff > 2:
                        st.markdown("<div class='alert-yellow'>🟡 VISCOSITY WARNING! Adjust solvent.</div>", unsafe_allow_html=True)
                        st.download_button("📄 Print QC Certificate", data=pdf_data, file_name=f"QC_{ref['color_name']}.pdf", mime="application/pdf", use_container_width=True, key=f"pdf_y1_{i}")

                    elif 2.0 < delta_e <= 3.0:
                        st.markdown("<div class='alert-yellow'>🟡 BORDERLINE MATCH!</div>", unsafe_allow_html=True)
                        st.download_button("📄 Print QC Certificate", data=pdf_data, file_name=f"QC_{ref['color_name']}.pdf", mime="application/pdf", use_container_width=True, key=f"pdf_y2_{i}")
                        
                    else:
                        st.markdown("<div class='alert-red'>🔴 REJECTED! Adjust ink and re-scan.</div>", unsafe_allow_html=True)
