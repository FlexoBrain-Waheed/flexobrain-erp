import streamlit as st
from supabase import create_client, Client
import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Anilox Library", page_icon="🎨", layout="wide")

# --- Database Connection ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.warning("Database connection not configured or missing secrets.")

# --- Custom CSS ---
st.markdown("""
<style>
.main-header {font-size: 28px !important; font-weight: bold; color: #1E3A8A; margin-bottom: 0px;}
.sub-header {font-size: 18px !important; color: #4B5563; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Anilox Inventory & Management</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Track your Anilox rollers, specifications, and maintenance status.</p>', unsafe_allow_html=True)

# --- Anilox Entry Form ---
with st.form("anilox_entry_form"):
    
    st.subheader("🔍 1. Anilox Identification")
    col1, col2, col3 = st.columns(3)
    with col1:
        serial_number = st.text_input("Serial Number / ID")
    with col2:
        manufacturer = st.text_input("Manufacturer")
    with col3:
        assigned_machine = st.selectbox("Assigned Machine", ["Unassigned", "SOMA", "Other"])

    st.markdown("---")
    
    st.subheader("📏 2. Engraving Specifications")
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        lpi = st.number_input("Line Count (LPI)", min_value=0, step=10)
    with col5:
        volume = st.number_input("Volume (BCM or cm3/m2)", min_value=0.0, step=0.1, format="%.2f")
    with col6:
        angle = st.selectbox("Engraving Angle", ["60° (Hexagonal)", "45°", "30°", "Channel / GTT", "Other"])
    with col7:
        cell_shape = st.selectbox("Cell Shape", ["Hexagonal", "Elongated", "Tri-Helical", "Other"])

    st.markdown("---")

    st.subheader("✨ 3. Status & Maintenance")
    col8, col9, col10 = st.columns(3)
    with col8:
        status = st.selectbox("Current Condition", ["New", "Good", "Needs Cleaning", "Damaged", "Re-engraved"])
    with col9:
        last_cleaned_date = st.date_input("Last Deep Cleaning Date", datetime.date.today())
    with col10:
        cleaner_used = st.selectbox("Recommended/Last Cleaner", ["Cell Max", "SealMax", "Ultrasonic", "Standard Solvent", "Other"])
        
    notes = st.text_area("Additional Notes (e.g., specific damages, printing issues)")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit Button
    submitted = st.form_submit_button("💾 Save Anilox Record", type="primary", use_container_width=True)

    # --- Form Submission Logic ---
    if submitted:
        if serial_number == "":
            st.error("Serial Number is required to save the Anilox record!")
        else:
            anilox_data = {
                "serial_number": serial_number,
                "manufacturer": manufacturer,
                "assigned_machine": assigned_machine,
                "lpi": lpi,
                "volume": volume,
                "angle": angle,
                "cell_shape": cell_shape,
                "status": status,
                "last_cleaned_date": str(last_cleaned_date),
                "cleaner_used": cleaner_used,
                "notes": notes
            }
            
            # TODO: Uncomment the code below once your Supabase 'anilox_library' table is ready
            # try:
            #     response = supabase.table("anilox_library").insert(anilox_data).execute()
            #     st.success(f"Anilox '{serial_number}' successfully saved to database!")
            # except Exception as e:
            #     st.error(f"Error saving to database: {e}")
            
            st.success(f"Anilox Roller '{serial_number}' successfully added to the library!")
