import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. Database Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="FlexoBrain ERP", layout="wide", page_icon="🏭")

# --- 2. Navigation Sidebar ---
st.sidebar.title("FlexoBrain Menu")
page = st.sidebar.radio("Navigate to:", ["Machine Setup", "Anilox Library"])

# --- PAGE 1: Machine Setup ---
if page == "Machine Setup":
    st.title("⚙️ Comprehensive Machine Configuration")
    st.markdown("Define your CI/Inline Flexo press specifications with high precision.")

    with st.form("machine_setup_form"):
        # Creating Tabs for better UX
        tab1, tab2, tab3 = st.tabs(["1. Core Specs", "2. Dimensions & Web Handling", "3. Quality & Finishing"])
        
        # TAB 1: Core Specifications
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                m_name = st.text_input("Machine Name & Model")
                m_drive = st.radio("Drive System Architecture", ["Gearless (Servo-Driven)", "Gear Type (Cylinder)"], horizontal=True)
            with col2:
                m_speed = st.number_input("Max Mechanical Speed (m/min)", value=150)
                m_colors = st.number_input("Number of Printing Stations", min_value=1, max_value=20, value=8)

        # TAB 2: Dimensions & Web Handling
        with tab2:
            col3, col4 = st.columns(2)
            with col3:
                m_web_width = st.number_input("Max Web Width (mm)", value=330)
                m_print_width = st.number_input("Actual Print Width (mm)", value=320)
                m_pitch = st.number_input("Gear Pitch (mm) - Skip if Gearless", value=3.175, format="%.3f")
            with col4:
                m_unwind = st.number_input("Unwind Max Diameter (mm)", value=1000)
                m_rewind = st.number_input("Rewind Max Diameter (mm)", value=1000)

        # TAB 3: Quality & Finishing
        with tab3:
            col5, col6 = st.columns(2)
            with col5:
                m_dryer = st.selectbox("Primary Drying Capability", ["UV", "Hot Air", "IR", "UV + Hot Air"])
                m_camera = st.selectbox("Inspection Camera System", ["None", "BST", "AVT", "Erhardt+Leimer", "Other"])
                m_die_cut = st.number_input("Die-Cutting Stations", min_value=0, max_value=5, value=0)
            with col6:
                st.markdown("**Inline Processing Units:**")
                m_corona = st.checkbox("Corona Treater System")
                m_turnbar = st.checkbox("Turn-bar (Front/Back Printing)")
                m_coldfoil = st.checkbox("Cold Foil Unit")

        st.markdown("---")
        submit = st.form_submit_button("🚀 Save Full Press Configuration")

        if submit:
            try:
                supabase.table("printing_machines").insert({
                    "machine_name": m_name,
                    "drive_system": m_drive,
                    "max_web_width": m_web_width,
                    "max_speed": m_speed,
                    "number_of_colors": m_colors,
                    "primary_dryer": m_dryer,
                    "print_width": m_print_width,
                    "gear_pitch": m_pitch,
                    "unwind_max_dia": m_unwind,
                    "rewind_max_dia": m_rewind,
                    "corona_treater": m_corona,
                    "die_cutting_stations": m_die_cut,
                    "turn_bar": m_turnbar,
                    "cold_foil": m_coldfoil,
                    "inspection_camera": m_camera
                }).execute()
                st.success(f"Machine '{m_name}' has been saved successfully!")
            except Exception as e:
                st.error(f"Error saving data: {e}")

    st.markdown("---")
    st.subheader("🏭 Factory Fleet Overview")
    try:
        m_data = supabase.table("printing_machines").select("*").execute()
        if m_data.data:
            df = pd.DataFrame(m_data.data)
            display_cols = ["machine_name", "drive_system", "number_of_colors", "max_web_width", "max_speed"]
            existing_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[existing_cols])
    except Exception as e:
        st.warning("No machines found or database still updating.")

# --- PAGE 2: Anilox Library ---
elif page == "Anilox Library":
    st.title("🛼 Anilox Roll Inventory")
    st.write("Manage your Anilox rolls linked to specific machines.")
