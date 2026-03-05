import streamlit as st
from supabase import create_client, Client

# --- Page Configuration ---
st.set_page_config(page_title="Machine Setup", page_icon="⚙️", layout="wide")

# --- Database Connection ---
# We initialize the connection here because each page in Streamlit runs independently
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.warning("Database connection not configured or missing secrets.")

# --- Custom CSS for Elegance ---
st.markdown("""
<style>
.main-header {font-size: 28px !important; font-weight: bold; color: #1E3A8A; margin-bottom: 0px;}
.sub-header {font-size: 18px !important; color: #4B5563; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Comprehensive Machine Configuration</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Define your CI/Inline Flexo press specifications with high precision.</p>', unsafe_allow_html=True)

# --- Machine Setup Form ---
with st.form("machine_setup_form"):
    
    # Organizing the UI into Tabs based on your original design
    tab1, tab2, tab3 = st.tabs(["Core Specs", "Dimensions & Web Handling", "Quality & Finishing"])
    
    # TAB 1: Core Specifications
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Machine Name (e.g., SOMA Optima)")
            m_model = st.text_input("Machine Model")
            m_type = st.selectbox("Press Type", ["CI (Central Impression)", "Inline Flexo", "Stack Press"])
        with col2:
            m_colors = st.number_input("Number of Colors (Decks)", min_value=1, max_value=12, value=8)
            m_year = st.number_input("Installation Year", min_value=1990, max_value=2030, value=2024)
            m_status = st.selectbox("Current Status", ["Active", "Maintenance", "Inactive"])

    # TAB 2: Dimensions & Web Handling
    with tab2:
        col3, col4 = st.columns(2)
        with col3:
            max_web_width = st.number_input("Max Web Width (mm)", min_value=0)
            min_web_width = st.number_input("Min Web Width (mm)", min_value=0)
            max_speed = st.number_input("Max Speed (m/min)", min_value=0)
        with col4:
            max_repeat = st.number_input("Max Repeat Length (mm)", min_value=0)
            min_repeat = st.number_input("Min Repeat Length (mm)", min_value=0)

    # TAB 3: Quality & Finishing
    with tab3:
        col5, col6 = st.columns(2)
        with col5:
            drying_sys = st.selectbox("Drying System", ["Hot Air", "UV", "LED-UV", "Mixed System"])
            auto_reg = st.checkbox("Has Auto-Registration System?")
        with col6:
            inline_slit = st.checkbox("Inline Slitting Capability?")
            corona_treat = st.checkbox("Inline Corona Treater?")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit Button
    submitted = st.form_submit_button("💾 Save Machine Configuration", type="primary", use_container_width=True)

    # --- Form Submission Logic ---
    if submitted:
        if m_name == "":
            st.error("Machine Name is required to save the configuration!")
        else:
            # Collect all data into a dictionary
            machine_data = {
                "machine_name": m_name,
                "model": m_model,
                "press_type": m_type,
                "colors": m_colors,
                "year": m_year,
                "status": m_status,
                "max_web_width": max_web_width,
                "min_web_width": min_web_width,
                "max_speed": max_speed,
                "max_repeat": max_repeat,
                "min_repeat": min_repeat,
                "drying_system": drying_sys,
                "auto_registration": auto_reg,
                "inline_slitting": inline_slit,
                "corona_treater": corona_treat
            }
            
            # TODO: Uncomment the code below once your Supabase 'machines' table is ready
            # try:
            #     response = supabase.table("machines").insert(machine_data).execute()
            #     st.success(f"Machine '{m_name}' successfully configured and saved to database!")
            # except Exception as e:
            #     st.error(f"Error saving to database: {e}")
            
            # Display success message and the collected data for testing
            st.success(f"Machine '{m_name}' successfully configured!")
            st.json(machine_data)
