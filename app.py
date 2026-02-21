import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. Database Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="FlexoBrain ERP", layout="wide", page_icon="🏭")

# --- Custom CSS for Elegance ---
st.markdown("""
<style>
.main-header {font-size: 28px !important; font-weight: bold; color: #1E3A8A; margin-bottom: -10px;}
.sub-header {font-size: 18px !important; color: #4B5563; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 2. Navigation Sidebar ---
st.sidebar.title("🏭 FlexoBrain Menu")
page = st.sidebar.radio("Navigate to:", ["⚙️ Machine Setup", "🔞 Anilox Library"])

# --- PAGE 1: INTERACTIVE MACHINE SETUP ---
if page == "⚙️ Machine Setup":
    st.markdown('<p class="main-header">Interactive Machine Configuration</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Define your CI Flexo press specifications with high precision.</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. Core Specifications")
            # Default placeholder matching high-end CI machines
            m_name = st.text_input("Machine Name & Model", placeholder="e.g., SOMA Optima 820")
            
            # Interactive UI for Drive System
            st.write("**Drive System Architecture**")
            drive_type = st.radio("Drive Type", ["Gearless (Servo-Driven)", "Gear Type (Cylinder)"], horizontal=True, label_visibility="collapsed")
            
            m_width = st.number_input("Max Web Width (mm)", min_value=100, max_value=2500, value=820, step=10)
            m_speed = st.number_input("Max Mechanical Speed (m/min)", min_value=50, max_value=1000, value=300, step=50)

        with col2:
            st.subheader("2. Printing Units Setup")
            # INTERACTIVE SLIDER FOR COLORS
            num_colors = st.slider("Number of Printing Stations", min_value=1, max_value=12, value=8)
            
            st.write(f"**Configure Drying System for {num_colors} units:**")
            primary_dryer = st.selectbox("Primary Drying Capability", ["Hot Air Only", "UV Only", "UV + Hot Air", "LED UV"])
            
            st.info(f"💡 The system will register this press with {num_colors} color stations and {primary_dryer} drying.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Save Press Configuration", use_container_width=True, type="primary"):
        if m_name:
            try:
                # Insert data into the new relational table
                supabase.table("printing_machines").insert({
                    "machine_name": m_name,
                    "drive_system": drive_type,
                    "max_web_width": m_width,
                    "max_speed": m_speed,
                    "number_of_colors": num_colors,
                    "primary_dryer": primary_dryer
                }).execute()
                st.success(f"✅ Master configuration for '{m_name}' has been successfully saved to the cloud!")
            except Exception as e:
                st.error(f"⚠️ Sync Error: {e}")
        else:
            st.warning("⚠️ Please provide a valid Machine Name.")

    # Display existing infrastructure elegantly
    st.markdown("---")
    st.subheader("🏭 Factory Fleet Overview")
    fleet = supabase.table("printing_machines").select("*").execute()
    if fleet.data:
        df = pd.DataFrame(fleet.data)
        st.dataframe(df[["machine_name", "drive_system", "number_of_colors", "max_web_width", "max_speed"]], use_container_width=True)

# --- PAGE 2: ANILOX LIBRARY ---
elif page == "🔞 Anilox Library":
    st.markdown('<p class="main-header">Anilox Inventory Management</p>', unsafe_allow_html=True)
    st.info("Here we will dynamically link specific Anilox rolls to the machines you just created. (Coming Next!)")
