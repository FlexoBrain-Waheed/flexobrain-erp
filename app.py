import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="FlexoBrain ERP", layout="wide", page_icon="🧠")

st.title("🧠 FlexoBrain - Production ERP")
st.markdown("### Internal Job Order Entry & Estimator")
st.divider()

# --- Section 1: Order & Client Information ---
st.subheader("1️⃣ Order & Client Information")
c1, c2, c3 = st.columns(3)
with c1:
    client_name = st.selectbox("Client Name", ["3P - Delta Water", "Naqi Water", "Nova Water", "Other"])
with c2:
    po_number = st.text_input("Sales PO#", placeholder="e.g. 4000035640")
with c3:
    job_type = st.selectbox("Product Type", ["Shrink PE Printed Roll", "Printed OPP Label", "BOPP Wrap", "Other"])

# --- Section 2: Material & Machine Setup ---
st.subheader("2️⃣ Material & Machine Setup")
m1, m2, m3, m4 = st.columns(4)
with m1:
    material_color = st.selectbox("Material Color", ["Transparent", "White", "Pearlized", "Metallized"])
with m2:
    splicing_type = st.radio("Roll Changeover", ["Auto Splicer (Non-stop)", "Manual (Machine Stop)"])
with m3:
    running_speed = st.number_input("Target Speed (m/min)", min_value=50, max_value=600, value=200, step=10)
with m4:
    trim_waste = st.number_input("Trim Waste (mm)", min_value=0, value=10, step=1)

# --- Section 3: Technical & Cylinder Specs ---
st.subheader("3️⃣ Technical & Cylinder Specs")
t1, t2, t3, t4, t5 = st.columns(5)
with t1:
    width = st.number_input("Web Width (mm)", value=430.0, step=1.0)
with t2:
    cylinder_repeat = st.number_input("Cylinder Repeat (mm)", value=860.0, step=0.1)
with t3:
    lines_across = st.number_input("Lines (Across Web)", min_value=1, value=2, step=1)
with t4:
    ups_around = st.number_input("Ups (Around Cyl.)", min_value=1, value=4, step=1)
with t5:
    quantity_meters = st.number_input("Quantity (Linear Meters)", min_value=1000, value=10000, step=1000)

# --- Section 4: Colors, Anilox & Ink Consumption ---
st.divider()
st.subheader("4️⃣ Colors, Anilox & Ink Consumption")
num_colors = st.slider("Number of Printing Colors", min_value=1, max_value=10, value=6)

data = {
    "Unit #": [i+1 for i in range(num_colors)],
    "Color (Pantone)": ["White", "Cyan", "Magenta", "Yellow", "Black", "Spot Color"][:num_colors] + [""]*(num_colors-6) if num_colors > 6 else ["White", "Cyan", "Magenta", "Yellow", "Black", "Spot Color"][:num_colors],
    "LPI": [800 if i==0 else 1000 for i in range(num_colors)], 
    "BCM": [3.5 if i==0 else 2.5 for i in range(num_colors)],
    "Est. Ink (Kg)": [15.0 if i==0 else 5.0 for i in range(num_colors)] 
}
df_colors = pd.DataFrame(data)
edited_df = st.data_editor(df_colors, use_container_width=True, hide_index=True)

# --- Section 5: FlexoBrain Estimations ---
st.divider()
st.subheader("🧠 FlexoBrain Estimations")

# Automated Calculations
sq_meters = (width / 1000) * quantity_meters
estimated_hours = (quantity_meters / running_speed) / 60 
setup_time = 1.5 
total_time = estimated_hours + setup_time

calc1, calc2, calc3 = st.columns(3)
calc1.metric(label="📐 Total Area (Square Meters)", value=f"{sq_meters:,.0f} m²")
calc2.metric(label="⏱️ Run Time (Hours)", value=f"{estimated_hours:.1f} hrs")
calc3.metric(label="🛑 Total Estimated Time (with Setup)", value=f"{total_time:.1f} hrs")

# --- Footer & Submission ---
st.divider()
submit_btn = st.button("🚀 Save Job Order & Lock Estimations", use_container_width=True, type="primary")

if submit_btn:
    st.success("✅ Job Order Saved Successfully! (Database linking coming soon)")
    st.balloons()
