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
page = st.sidebar.radio("Navigate to:", ["Job Order", "Machine Management", "Cylinder Inventory"])

# --- PAGE: Machine Management (The Full Version) ---
if page == "Machine Management":
    st.title("⚙️ Comprehensive Machine Setup")
    st.info("Define your factory infrastructure below.")
    
    with st.form("advanced_machine_form"):
        c1, c2 = st.columns(2)
        with c1:
            m_name = st.text_input("Machine Name (Brand/Model)")
            m_drive = st.selectbox("Drive System", ["Gear Type", "Gearless"])
            m_colors = st.number_input("Number of Color Units", min_value=1, max_value=20, value=8)
        with c2:
            m_width = st.number_input("Max Web Width (mm)", value=330)
            m_speed = st.number_input("Design Max Speed (m/min)", value=150)
            m_dryer = st.selectbox("Drying System", ["UV", "Hot Air", "IR", "UV + Hot Air"])

        if st.form_submit_button("Save & Configure Machine"):
            try:
                supabase.table("machines").insert({
                    "machine_name": m_name, 
                    "drive_system": m_drive,
                    "max_web_width": m_width,
                    "num_colors": m_colors,
                    "max_speed_design": m_speed,
                    "drying_type": m_dryer
                }).execute()
                st.success(f"Machine '{m_name}' is now fully configured!")
            except Exception as e:
                st.error(f"Error: {e}. (Make sure you updated Supabase columns)")

    # Show Existing Machines
    st.subheader("Current Factory Infrastructure")
    m_data = supabase.table("machines").select("*").execute()
    if m_data.data:
        st.dataframe(pd.DataFrame(m_data.data))

# --- PAGE: Job Order ---
elif page == "Job Order":
    st.title("📝 New Production Order")
    # Pulling dynamic machine list from DB
    res = supabase.table("machines").select("machine_name", "drive_system").execute()
    if res.data:
        m_list = [m['machine_name'] for m in res.data]
        selected_m = st.selectbox("Select Target Machine", m_list)
        st.write(f"Preparing order for a **{selected_m}** unit.")
    else:
        st.warning("Please add a machine in settings first.")

# --- PAGE: Cylinder Inventory ---
elif page == "Cylinder Inventory":
    st.title("📂 Cylinder & Sleeve Library")
    st.write("Manage your inventory here.")
