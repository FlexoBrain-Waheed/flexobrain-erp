import streamlit as st
import pandas as pd

# ==========================================
# --- Page Configuration ---
# ==========================================
st.set_page_config(page_title="Cliché Vault", page_icon="📦", layout="wide")

st.title("📦 Cliché Vault & Lifecycle Intelligence")
st.markdown("Monitor cliché health, impressions, and lifecycle status automatically.")
st.markdown("---")

# ==========================================
# --- 1. Mock Database (Temporary for Testing) ---
# ==========================================
# We use session_state to remember updates during the session
if 'cliche_db' not in st.session_state:
    st.session_state['cliche_db'] = [
        {"id": "CL-101", "design_no": "ART-2026-A", "client": "Al-Safi", "status": "Active", "location": "Rack A-1", "repeat_mm": 400, "good_meters": 150000, "max_meters": 1000000},
        {"id": "CL-102", "design_no": "ART-2025-B", "client": "Nadec", "status": "Active", "location": "Rack A-2", "repeat_mm": 320, "good_meters": 880000, "max_meters": 1000000}, # Close to worn out
        {"id": "CL-103", "design_no": "ART-2024-C", "client": "Halwani", "status": "Pending Pull", "location": "Rack B-1", "repeat_mm": 450, "good_meters": 995000, "max_meters": 1000000},
    ]

# ==========================================
# --- 2. Data Processing & Smart Calculations ---
# ==========================================
df = pd.DataFrame(st.session_state['cliche_db'])

# Smart Math: Calculate Impressions based on Repeat Length
# Formula: Impressions = Good Meters / (Repeat in meters)
df['impressions'] = (df['good_meters'] / (df['repeat_mm'] / 1000)).astype(int)

# Health Percentage = (Consumed Meters / Max Meters) * 100
df['consumption_percent'] = (df['good_meters'] / df['max_meters']) * 100
df['consumption_percent'] = df['consumption_percent'].clip(upper=100) # Cap at 100%

# Auto-Flag Worn out cliches (Over 85% consumed)
worn_out_count = len(df[(df['consumption_percent'] >= 85) & (df['status'] == 'Active')])
active_count = len(df[df['status'] == 'Active'])
pull_count = len(df[df['status'] == 'Pending Pull'])

# ==========================================
# --- 3. Dashboard Metrics ---
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("🟢 Active Clichés", active_count)
col2.metric("🟡 Worn Out Warning (>85%)", worn_out_count, delta="Check Inventory", delta_color="inverse")
col3.metric("🔴 Pending Pull (Scrap)", pull_count)
st.write("")

# ==========================================
# --- 4. Interactive Inventory Table ---
# ==========================================
st.subheader("📋 Main Inventory List")

# Configure columns for a beautiful UI, especially the Progress Bar
column_config = {
    "id": "Cliché ID",
    "design_no": "Design No.",
    "client": "Client Name",
    "status": st.column_config.SelectboxColumn("Status", options=["Active", "Pending Pull", "Scrapped"]),
    "location": "Warehouse Location",
    "repeat_mm": "Repeat (mm)",
    "good_meters": st.column_config.NumberColumn("Good Meters Printed", format="%d M"),
    "impressions": st.column_config.NumberColumn("Total Impressions", format="%d Hits"),
    "consumption_percent": st.column_config.ProgressColumn(
        "Health / Consumption %",
        help="Green < 70% | Yellow < 85% | Red > 85%",
        format="%.1f %%",
        min_value=0,
        max_value=100,
    ),
    "max_meters": None # Hide this column to keep table clean
}

st.dataframe(df, column_config=column_config, use_container_width=True, hide_index=True)

st.markdown("---")

# ==========================================
# --- 5. Background Automation Simulator ---
# ==========================================
# This section simulates what happens when the Production Floor finishes a job
st.subheader("⚙️ Simulator: Auto-Update from Production")
st.info("In the final version, this happens invisibly when 'Complete Order' is clicked on the Shop Floor.")

with st.form("simulate_production"):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        # Filter only active cliches for the simulator
        active_options = df[df['status'] == 'Active']['id'].tolist()
        selected_cliche = st.selectbox("1. Select Cliché on Machine", active_options)
    with c2:
        added_meters = st.number_input("2. Enter 'Good Meters' Produced", min_value=0, value=10000, step=1000)
    with c3:
        st.write("") # Spacing
        st.write("")
        submit = st.form_submit_button("Run Simulation 🚀", type="primary", use_container_width=True)

    if submit:
        # Find the cliché in our session state and update its meters
        for cliche in st.session_state['cliche_db']:
            if cliche['id'] == selected_cliche:
                cliche['good_meters'] += added_meters
                st.success(f"✅ Auto-Updated {selected_cliche}: Added {added_meters:,} meters successfully!")
                st.rerun() # Refresh the page to update the table and progress bar
