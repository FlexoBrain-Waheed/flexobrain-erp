import streamlit as st
import math
import datetime

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
    
    /* Golden Reference Styling */
    .golden-box { background-color: #FEF3C7; border-left: 8px solid #F59E0B; padding: 20px; border-radius: 10px; margin-bottom: 15px;}
    .golden-text { font-size: 1.4rem; color: #92400E; font-weight: bold; margin: 5px 0;}
    
    /* Input Styling for Tablets */
    .stNumberInput input { font-size: 1.8rem !important; text-align: center; height: 70px !important; border: 2px solid #4F46E5 !important;}
    .stNumberInput label { font-size: 1.4rem !important; font-weight: bold; color: #374151;}
    
    /* Action Buttons */
    .btn-approve { height: 90px; font-size: 2rem; font-weight: bold; border-radius: 12px; background-color: #10B981; color: white; border: none; width: 100%; transition: 0.3s;}
    .btn-approve:hover { background-color: #059669; }
    .btn-warning { height: 90px; font-size: 2rem; font-weight: bold; border-radius: 12px; background-color: #F59E0B; color: white; border: none; width: 100%; transition: 0.3s;}
    .btn-warning:hover { background-color: #D97706; }
    
    /* Alert Boxes */
    .alert-green { background-color: #D1FAE5; color: #065F46; padding: 20px; border-radius: 15px; font-size: 1.8rem; font-weight: bold; text-align: center; border: 3px solid #10B981;}
    .alert-red { background-color: #FEE2E2; color: #991B1B; padding: 20px; border-radius: 15px; font-size: 1.8rem; font-weight: bold; text-align: center; border: 3px solid #EF4444;}
    .alert-yellow { background-color: #FEF3C7; color: #92400E; padding: 20px; border-radius: 15px; font-size: 1.8rem; font-weight: bold; text-align: center; border: 3px solid #F59E0B;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='kitchen-title'>🎨 FlexoBrain - Ink Kitchen & Color QC</div>", unsafe_allow_html=True)

# ==========================================
# 3. Mock Database (Golden References)
# ==========================================
# In production, this data comes from Supabase based on the scanned Job Order
golden_db = {
    "BOPP-20260413-001 (Al-Marai Green)": {
        "job_no": "BOPP-20260413-001",
        "client": "Al-Marai",
        "material": "BOPP Transparent",
        "target_L": 50.0,
        "target_a": -40.0,
        "target_b": 20.0,
        "viscosity": 22,
        "recipe": "70% Green, 20% White, 10% Solvent",
        "anilox": "400 LPI / 4.5 BCM"
    },
    "BOPP-20260413-002 (Al-Safi Blue)": {
        "job_no": "BOPP-20260413-002",
        "client": "Al-Safi Dairy",
        "material": "PETG White",
        "target_L": 35.0,
        "target_a": 10.0,
        "target_b": -45.0,
        "viscosity": 20,
        "recipe": "80% Blue, 15% Cyan, 5% Solvent",
        "anilox": "300 LPI / 5.0 BCM"
    }
}

# ==========================================
# 4. Job Selection (The Trigger)
# ==========================================
selected_job = st.selectbox("🔍 Select or Scan Job Order to load Golden Reference:", ["-- Select Job --"] + list(golden_db.keys()))

if selected_job != "-- Select Job --":
    ref = golden_db[selected_job]
    
    st.markdown("---")
    
    # ==========================================
    # 5. UI Layout: Left (Golden) vs Right (New)
    # ==========================================
    col_ref, col_new = st.columns(2)
    
    # ------------------------------------------
    # LEFT COLUMN: GOLDEN REFERENCE (Read-Only)
    # ------------------------------------------
    with col_ref:
        st.markdown("<div class='section-header'>🏆 The Golden Reference (Target)</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='golden-box'>
                <div class='golden-text'>📦 Job: {ref['job_no']} | {ref['client']}</div>
                <div class='golden-text'>🎞️ Material: {ref['material']}</div>
                <div class='golden-text'>🛢️ Anilox: {ref['anilox']}</div>
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

    # ------------------------------------------
    # RIGHT COLUMN: NEW BATCH INPUT (Data Entry)
    # ------------------------------------------
    with col_new:
        st.markdown("<div class='section-header'>🔬 New Batch Input (X-Rite Data)</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: L_actual = st.number_input("L* (Lightness)", value=ref['target_L'], step=0.1, format="%.1f")
        with c2: a_actual = st.number_input("a* (Red/Green)", value=ref['target_a'], step=0.1, format="%.1f")
        with c3: b_actual = st.number_input("b* (Yellow/Blue)", value=ref['target_b'], step=0.1, format="%.1f")
        
        viscosity_actual = st.number_input("💧 Current Viscosity (Seconds)", value=ref['viscosity'], step=1)
        new_recipe_notes = st.text_area("📝 Recipe Adjustments (Optional)", placeholder="e.g., Added 50g of Solvent to match viscosity...")

    st.markdown("---")

    # ==========================================
    # 6. Delta E Calculation Engine
    # ==========================================
    # Delta E Formula (CIE76)
    delta_L = L_actual - ref['target_L']
    delta_a = a_actual - ref['target_a']
    delta_b = b_actual - ref['target_b']
    delta_e = math.sqrt((delta_L ** 2) + (delta_a ** 2) + (delta_b ** 2))
    
    viscosity_diff = abs(viscosity_actual - ref['viscosity'])

    # ==========================================
    # 7. Smart Decision Engine (The Interlock)
    # ==========================================
    st.markdown("<div class='section-header'>🧠 Quality Control Decision</div>", unsafe_allow_html=True)
    
    col_result, col_action = st.columns([1, 1])
    
    with col_result:
        st.metric(label="ΔE (Color Difference)", value=f"{delta_e:.2f}", delta=f"{delta_e - 2.0:.2f} from acceptable limit", delta_color="inverse")
        st.metric(label="Viscosity Variance", value=f"{viscosity_diff} Sec", delta=f"{viscosity_diff} sec diff", delta_color="inverse")

    with col_action:
        # LOGIC 1: Excellent Match
        if delta_e <= 2.0 and viscosity_diff <= 2:
            st.markdown("<div class='alert-green'>🟢 MATCH APPROVED!<br>Color and Viscosity are within limits.</div><br>", unsafe_allow_html=True)
            if st.button("✅ APPROVE INK & UNLOCK MACHINE", use_container_width=True, type="primary"):
                st.balloons()
                st.success(f"🔒 INTERLOCK RELEASED: Machine is now authorized to print Job {ref['job_no']}!")
                # In production: supabase.table("job_orders").update({"ink_approved": True}).eq("order_number", ref['job_no']).execute()
        
        # LOGIC 2: Color OK, but Viscosity Bad
        elif delta_e <= 2.0 and viscosity_diff > 2:
            st.markdown("<div class='alert-yellow'>🟡 VISCOSITY WARNING!<br>Color is OK, but Viscosity is out of limits. Adjust solvent!</div><br>", unsafe_allow_html=True)
            st.button("⚠️ REQUEST QA OVERRIDE", use_container_width=True)

        # LOGIC 3: Color Warning (Acceptable but borderline)
        elif 2.0 < delta_e <= 3.0:
            st.markdown("<div class='alert-yellow'>🟡 BORDERLINE MATCH!<br>ΔE is between 2.0 and 3.0. Commercial match only.</div><br>", unsafe_allow_html=True)
            st.button("⚠️ REQUEST QA OVERRIDE", use_container_width=True)
            
        # LOGIC 4: Rejected (Bad Match)
        else:
            st.markdown("<div class='alert-red'>🔴 REJECTED!<br>ΔE is too high. Do not send this ink to the machine. Adjust and re-scan.</div><br>", unsafe_allow_html=True)
            st.error("❌ Machine remains LOCKED.")

else:
    st.info("👈 Please scan or select a Job Order from the dropdown to begin Quality Control.")
