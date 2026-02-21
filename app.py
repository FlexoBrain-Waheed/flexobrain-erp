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

# --- PAGE: Machine Management (Settings) ---
if page == "Machine Management":
    st.title("⚙️ Machine Management")
    st.info("Define your factory machines here. This data will populate your Job Orders.")
    
    with st.form("add_machine_form"):
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Machine Name (e.g., Gallus 01)")
            m_drive = st.selectbox("Drive System", ["Gear Type", "Gearless"])
        with col2:
            m_width = st.number_input("Max Web Width (mm)", value=330)
            m_pitch = st.number_input("Gear Pitch (Default 3.175 for 1/8)", value=3.175, format="%.3f")
        
        if st.form_submit_button("Save Machine"):
            try:
                supabase.table("machines").insert({
                    "machine_name": m_name, 
                    "drive_system": m_drive, 
                    "max_web_width": m_width,
                    "pitch_value": m_pitch
                }).execute()
                st.success(f"Machine '{m_name}' saved successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Current Machines
    st.subheader("Existing Machines")
    m_data = supabase.table("machines").select("*").execute()
    if m_data.data:
        st.table(pd.DataFrame(m_data.data)[["machine_name", "drive_system", "max_web_width"]])

# --- PAGE: Job Order (Production) ---
elif page == "Job Order":
    st.title("📝 New Job Order")
    
    # Fetch Machines from DB for the dropdown
    m_res = supabase.table("machines").select("machine_name", "drive_system", "pitch_value").execute()
    if not m_res.data:
        st.warning("⚠️ Please add a machine in 'Machine Management' first!")
    else:
        machine_options = {m['machine_name']: m for m in m_res.data}
        
        with st.form("job_order_form"):
            selected_m = st.selectbox("Select Machine", list(machine_options.keys()))
            m_info = machine_options[selected_m]
            
            st.divider()
            col_a, col_b = st.columns(2)
            
            with col_a:
                client = st.text_input("Client Name")
                if m_info['drive_system'] == "Gear Type":
                    z_teeth = st.number_input("Cylinder Teeth (Z)", min_value=1, value=96)
                    repeat = z_teeth * m_info['pitch_value']
                    st.success(f"Calculated Repeat: {repeat:.2f} mm")
                else:
                    repeat = st.number_input("Sleeve Repeat (mm)", min_value=1.0)
            
            with col_b:
                order_qty = st.number_input("Order Quantity", min_value=1)
                speed = st.number_input("Target Speed (m/min)", value=100)

            if st.form_submit_button("Process Order"):
                st.write("Order details processed for machine:", selected_m)

# --- PAGE: Cylinder Inventory ---
elif page == "Cylinder Inventory":
    st.title("📂 Cylinder & Sleeve Library")
    st.write("In this section, you can list all cylinders/sleeves available in your warehouse.")
    # (Future logic for cylinder inventory can go here)
