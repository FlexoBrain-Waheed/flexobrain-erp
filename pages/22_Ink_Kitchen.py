import streamlit as st
import math
import datetime
import io
import pandas as pd
from fpdf import FPDF

# ==========================================
# 1. Page Configuration & Kiosk Mode
# ==========================================
st.set_page_config(
    page_title="Ink Kitchen & Color QC", 
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
    
    .golden-box { background-color: #F8FAFC; border-left: 8px solid #3B82F6; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .golden-text { font-size: 1.4rem; color: #1E293B; font-weight: bold; margin: 5px 0;}
    .ink-id-badge { background-color: #3B82F6; color: white; padding: 5px 15px; border-radius: 20px; font-size: 1.2rem; display: inline-block; margin-bottom: 10px;}
    
    .stNumberInput input { font-size: 1.8rem !important; text-align: center; height: 70px !important; border: 2px solid #4F46E5 !important; border-radius: 10px !important;}
    .stNumberInput label { font-size: 1.4rem !important; font-weight: bold; color: #374151;}
    .stTextInput input { font-size: 1.5rem !important; height: 60px !important;}
    
    .btn-approve { height: 90px; font-size: 2rem; font-weight: bold; border-radius: 12px; background-color: #10B981; color: white; border: none; width: 100%; transition: 0.3s;}
    
    .alert-green { background-color: #D1FAE5; color: #065F46; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #10B981;}
    .alert-red { background-color: #FEE2E2; color: #991B1B; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #EF4444;}
    .alert-yellow { background-color: #FEF3C7; color: #92400E; padding: 20px; border-radius: 15px; font-size: 1.5rem; font-weight: bold; text-align: center; border: 3px solid #F59E0B;}
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 1.5rem; font-weight: bold; padding: 15px 25px; background-color: #f0f2f6; border-radius: 10px 10px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #4F46E5 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='kitchen-title'>🎨 FlexoBrain - Central Ink Library & QC</div>", unsafe_allow_html=True)

# ==========================================
# 3. Master Data Management (Pantone Standards)
# ==========================================
PANTONE_BASES = [
    "Pantone Yellow", "Pantone Warm Red", "Pantone Rubine Red", "Pantone Rhodamine Red", 
    "Pantone Purple", "Pantone Violet", "Pantone Blue 072", "Pantone Reflex Blue", 
    "Pantone Process Blue", "Pantone Green", "Pantone Black", 
    "Pantone Transparent White (Extender)", "Pantone Opaque White"
]
SOLVENTS = ["Ethyl Acetate", "N-Propanol", "Retarder", "Accelerator", "Ethanol"]

if 'ink_library' not in st.session_state:
    st.session_state['ink_library'] = {
        "INK-GR-101": {"name": "Pantone 347 Green", "material": "BOPP Trans", "bar": "Mayer #3", "L": 50.0, "a": -40.0, "b": 20.0, "visc": 22, "recipe": "Pantone Green: 70% | Pantone Trans White: 20% | Ethyl Acetate: 10%"},
        "INK-GR-102": {"name": "Opaque White (Backing)", "material": "BOPP Trans", "bar": "Mayer #4", "L": 95.0, "a": 0.0, "b": -2.0, "visc": 24, "recipe": "Pantone Opaque White: 90% | N-Propanol: 10%"},
        "INK-GR-103": {"name": "Strawberry Red 185", "material": "BOPP White", "bar": "Mayer #3", "L": 45.0, "a": 60.0, "b": 15.0, "visc": 20, "recipe": "Pantone Rubine Red: 80% | Ethyl Acetate: 20%"}
    }

if 'job_assignments' not in st.session_state:
    st.session_state['job_assignments'] = {
        "BOPP-20260413-001": ["INK-GR-101", "INK-GR-102"], 
        "BOPP-20260413-002": ["INK-GR-103"]               
    }

lib = st.session_state['ink_library']
jobs = st.session_state['job_assignments']

# ==========================================
# 4. PDF Generator Engine
# ==========================================
def create_qc_pdf(job_no, ink_id, ink_data, actual, delta_e, status, user="Ink QC Manager"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Color QC & Approval Certificate", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Job Order No: {job_no}", ln=True)
    pdf.cell(0, 8, f"Ink ID & Name: {ink_id} | {ink_data['name']}", ln=True)
    pdf.cell(0, 8, f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Approved By: {user}", ln=True)
    pdf.ln(5)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(95, 10, "Target (Golden Reference)", border=1, fill=True)
    pdf.cell(95, 10, "Actual (New Batch)", border=1, ln=True, fill=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 8, f"L*: {ink_data['L']} | a*: {ink_data['a']} | b*: {ink_data['b']}", border=1)
    pdf.cell(95, 8, f"L*: {actual['L']} | a*: {actual['a']} | b*: {actual['b']}", border=1, ln=True)
    pdf.cell(95, 8, f"Viscosity: {ink_data['visc']} sec", border=1)
    pdf.cell(95, 8, f"Viscosity: {actual['visc']} sec", border=1, ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Delta E (Color Diff): {delta_e:.2f}", ln=True)
    pdf.cell(0, 10, f"QC Decision: {status.upper()}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. Top Navigation Menu
# ==========================================
menu = st.radio("🛠️ Navigation Menu:", ["🔬 1. QC Production Mode (Daily Use)", "🔗 2. Job Setup (Link Inks)", "📚 3. Master Ink Library (Create New)"], horizontal=True)
st.markdown("---")

# ==========================================
# MODE 1: QC PRODUCTION MODE (Daily Use)
# ==========================================
if menu == "🔬 1. QC Production Mode (Daily Use)":
    st.info("💡 Scan or enter Job Order to pull assigned Golden Inks.")
    scanned_job = st.text_input("📦 Scan Job Order No:", placeholder="e.g., BOPP-20260413-001")
    
    if scanned_job:
        if scanned_job in jobs:
            assigned_inks = jobs[scanned_job]
            st.success(f"✅ Found {len(assigned_inks)} ink(s) assigned to this job.")
            tabs = st.tabs([f"🎨 {lib[ink_id]['name']}" for ink_id in assigned_inks])
            
            for i, tab in enumerate(tabs):
                ink_id = assigned_inks[i]
                ref = lib[ink_id]
                with tab:
                    col_ref, col_new = st.columns(2)
                    with col_ref:
                        st.markdown("<div class='section-header'>🏆 Golden Reference</div>", unsafe_allow_html=True)
                        st.markdown(f"""
                            <div class='golden-box'>
                                <div class='ink-id-badge'>🔖 ID: {ink_id}</div>
                                <div class='golden-text'>🎨 Name: {ref['name']}</div>
                                <div class='golden-text'>🎞️ Substrate: {ref['material']} | 🖌️ Tool: {ref['bar']}</div>
                                <hr style='border-color: #CBD5E1;'>
                                <div class='golden-text'>🎯 Target L: {ref['L']} | a: {ref['a']} | b: {ref['b']}</div>
                                <div class='golden-text'>💧 Target Viscosity: {ref['visc']} Sec</div>
                                <hr style='border-color: #CBD5E1;'>
                                <div class='golden-text'>📝 Recipe: <span style='font-weight:normal;'>{ref['recipe']}</span></div>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_new:
                        st.markdown("<div class='section-header'>🔬 New Batch Input (X-Rite)</div>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns(3)
                        with c1: L_act = st.number_input("L*", value=ref['L'], step=0.1, key=f"L_{ink_id}")
                        with c2: a_act = st.number_input("a*", value=ref['a'], step=0.1, key=f"a_{ink_id}")
                        with c3: b_act = st.number_input("b*", value=ref['b'], step=0.1, key=f"b_{ink_id}")
                        v_act = st.number_input("💧 Current Viscosity", value=ref['visc'], step=1, key=f"v_{ink_id}")
                        
                        delta_e = math.sqrt((L_act - ref['L'])**2 + (a_act - ref['a'])**2 + (b_act - ref['b'])**2)
                        v_diff = abs(v_act - ref['visc'])
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.metric("ΔE (Color Difference)", f"{delta_e:.2f}", f"{delta_e - 2.0:.2f}", delta_color="inverse")
                        
                        pdf_data = create_qc_pdf(scanned_job, ink_id, ref, {'L':L_act, 'a':a_act, 'b':b_act, 'visc':v_act}, delta_e, "Approved" if delta_e<=2 else "Rejected")
                        
                        if delta_e <= 2.0 and v_diff <= 2:
                            st.markdown("<div class='alert-green'>🟢 APPROVED!</div>", unsafe_allow_html=True)
                            b1, b2 = st.columns(2)
                            with b1: 
                                if st.button(f"✅ APPROVE {ink_id}", use_container_width=True, key=f"btn_{ink_id}"): st.balloons()
                            with b2: 
                                st.download_button("📄 Print QC Certificate", pdf_data, f"QC_{scanned_job}_{ink_id}.pdf", "application/pdf", use_container_width=True, key=f"pdf_{ink_id}")
                        elif delta_e <= 2.0 and v_diff > 2:
                            st.markdown("<div class='alert-yellow'>🟡 VISCOSITY WARNING! Adjust solvent.</div>", unsafe_allow_html=True)
                        elif 2.0 < delta_e <= 3.0:
                            st.markdown("<div class='alert-yellow'>🟡 BORDERLINE MATCH! QA Override Needed.</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='alert-red'>🔴 REJECTED! Adjust ink and re-scan.</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Job Order not found. Go to 'Job Setup' to link inks.")

# ==========================================
# MODE 2: JOB SETUP (Link Inks to Job)
# ==========================================
elif menu == "🔗 2. Job Setup (Link Inks)":
    st.markdown("<div class='section-header'>🔗 Assign Golden Inks to Job Order</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1: job_no_input = st.text_input("1. Enter Job Order No:", placeholder="BOPP-...")
    with col2:
        available_inks = [f"{k} - {v['name']}" for k, v in lib.items()]
        selected_inks_disp = st.multiselect("2. Select Required Inks from Master Library:", available_inks)
    if st.button("💾 SAVE JOB-INK ASSIGNMENT", type="primary"):
        if job_no_input and selected_inks_disp:
            selected_ids = [item.split(" - ")[0] for item in selected_inks_disp]
            st.session_state['job_assignments'][job_no_input] = selected_ids
            st.success(f"✅ Successfully linked {len(selected_ids)} ink(s) to Job {job_no_input}!")
        else:
            st.error("Please enter a Job No and select at least one ink.")

# ==========================================
# MODE 3: MASTER INK LIBRARY (Create New)
# ==========================================
elif menu == "📚 3. Master Ink Library (Create New)":
    st.markdown("<div class='section-header'>➕ Add New Golden Reference to Library</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        i_name = st.text_input("Color Name / Description (e.g., Mango Orange)")
        i_mat = st.selectbox("Substrate", ["BOPP Trans", "BOPP White", "PETG", "PE Clear", "Paper"])
        i_bar = st.selectbox("Drawdown Tool", ["Mayer #2", "Mayer #3", "Mayer #4", "IGT"])
    with col2:
        c_L, c_a, c_b, c_v = st.columns(4)
        with c_L: i_L = st.number_input("Target L*", step=0.1, value=50.0)
        with c_a: i_a = st.number_input("Target a*", step=0.1, value=0.0)
        with c_b: i_b = st.number_input("Target b*", step=0.1, value=0.0)
        with c_v: i_v = st.number_input("Visc (Sec)", step=1, value=22)

    st.markdown("### 🧪 Dynamic Recipe Formulation (Must equal 100%)")
    
    # Initialize an empty dataframe for the recipe if not exists
    if 'recipe_df' not in st.session_state:
        st.session_state.recipe_df = pd.DataFrame([
            {"Type": "Base Ink", "Component": "Pantone Rubine Red", "Percentage (%)": 80.0},
            {"Type": "Solvent", "Component": "Ethyl Acetate", "Percentage (%)": 20.0}
        ])

    # Dynamic Data Editor (The Grid)
    edited_recipe = st.data_editor(
        st.session_state.recipe_df,
        column_config={
            "Type": st.column_config.SelectboxColumn("Component Type", options=["Base Ink", "Solvent"], required=True, width="medium"),
            "Component": st.column_config.SelectboxColumn("Pantone Base / Solvent Name", options=PANTONE_BASES + SOLVENTS, required=True, width="large"),
            "Percentage (%)": st.column_config.NumberColumn("Percentage (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f%%", required=True, width="small")
        },
        num_rows="dynamic",
        use_container_width=True,
        key="recipe_editor"
    )

    # 100% Validation Logic
    total_percentage = edited_recipe["Percentage (%)"].sum()
    
    if total_percentage == 100.0:
        st.markdown(f"<div class='alert-green'>⚖️ Total Percentage: {total_percentage}% (Perfect Match!)</div>", unsafe_allow_html=True)
        can_save = True
    else:
        st.markdown(f"<div class='alert-red'>⚠️ Total Percentage: {total_percentage}% (Must be exactly 100% to save)</div>", unsafe_allow_html=True)
        can_save = False

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Save Button (Locked if not 100%)
    if st.button("💾 GENERATE ID & ADD TO LIBRARY", type="primary", use_container_width=True, disabled=not can_save):
        if i_name:
            # Format recipe to string for saving
            recipe_str = " | ".join([f"{row['Component']}: {row['Percentage (%)']}%" for _, row in edited_recipe.iterrows() if row['Percentage (%)'] > 0])
            
            next_num = len(st.session_state['ink_library']) + 101
            new_id = f"INK-GR-{next_num}"
            st.session_state['ink_library'][new_id] = {
                "name": i_name, "material": i_mat, "bar": i_bar,
                "L": i_L, "a": i_a, "b": i_b, "visc": i_v, "recipe": recipe_str
            }
            st.success(f"✅ Success! New Ink added to library with ID: {new_id}")
            st.balloons()
        else:
            st.error("Please enter an Ink Name.")
