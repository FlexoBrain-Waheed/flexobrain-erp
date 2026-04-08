import streamlit as st
import pandas as pd
import datetime
import sys
from pathlib import Path

# --- Page configuration ---
st.set_page_config(page_title="Production Board", page_icon="🏭", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth

if not auth.check_password():
    st.stop()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 01 - 2026-04-08</div>", unsafe_allow_html=True)

# ==========================================
# --- Mock Database Initialization ---
# ==========================================
# This acts as a temporary database until we connect to Supabase
if 'pending_orders' not in st.session_state:
    st.session_state.pending_orders = [
        {"id": "BOPP-20260408-001", "customer": "Al-Wataniya", "material": "BOPP 30u", "width": 450, "qty": 150000, "colors": 4},
        {"id": "BOPP-20260408-002", "customer": "Delta Food", "material": "PETG 40u", "width": 320, "qty": 85000, "colors": 6}
    ]

if 'anilox_library' not in st.session_state:
    st.session_state.anilox_library = ["Available", "3.0 BCM", "4.5 BCM", "6.0 BCM", "8.0 BCM", "10.0 BCM (White)"]

# ==========================================
# --- Dialog Functions (Pop-ups) ---
# ==========================================
@st.dialog("📦 Material Requisition")
def open_material_dialog(order):
    st.write(f"**Issue Raw Material for:** {order['id']}")
    st.info(f"Target Material: {order['material']} | Width: {order['width']} mm")
    
    req_weight = st.number_input("Requested Weight (Kg)", min_value=1.0, value=500.0)
    notes = st.text_area("Notes for Warehouse")
    
    if st.button("Submit Material Request", type="primary"):
        st.toast(f"Material Request sent to Warehouse for {req_weight} Kg!", icon="✅")
        st.rerun()

@st.dialog("🎨 Ink Preparation Request")
def open_ink_dialog(order):
    st.write(f"**Prepare Inks for:** {order['id']}")
    st.info(f"Total Colors Required: {order['colors']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Color 1 (e.g., White)", value="White")
        st.text_input("Color 2 (e.g., Cyan)", value="Cyan")
    with col2:
        st.number_input("Qty (Kg)", key="k1", value=20)
        st.number_input("Qty (Kg)", key="k2", value=15)
        
    if st.button("Send to Ink Kitchen", type="primary"):
        st.toast("Ink Request sent to Kitchen!", icon="✅")
        st.rerun()

@st.dialog("🖨️ Cliche / Plate Request (Al-Basit Lab)")
def open_cliche_dialog(order):
    st.write(f"**Order Plates from Al-Basit Lab for:** {order['id']}")
    
    col1, col2 = st.columns(2)
    with col1:
        thickness = st.selectbox("Plate Thickness", ["1.14 mm", "1.70 mm"])
        lpi = st.selectbox("Line Screen (LPI)", ["120 LPI", "133 LPI", "150 LPI", "175 LPI"])
    with col2:
        st.number_input("Cylinder Circumference (mm)", value=400)
        st.selectbox("Sticky Back Tape", ["0.38 mm (Hard)", "0.38 mm (Medium)", "0.38 mm (Soft)"])
        
    if st.button("Generate & Send Cliche Request", type="primary"):
        st.toast("Cliche Order sent to Al-Basit Laboratory!", icon="✅")
        st.rerun()

@st.dialog("🧻 Core Request")
def open_core_dialog(order):
    st.write(f"**Request Cores for:** {order['id']}")
    st.info(f"Slitting Width: {order['width']} mm")
    
    col1, col2 = st.columns(2)
    with col1:
        core_type = st.selectbox("Core Material", ["Paper Core", "Plastic Core"])
    with col2:
        qty = st.number_input("Required Quantity (Pieces)", min_value=1, value=50)
        
    if st.button("Send to Slitting Dept", type="primary"):
        st.toast("Core Request sent!", icon="✅")
        st.rerun()


# ==========================================
# --- Main UI Starts Here ---
# ==========================================
st.title("🏭 Production Board - Work Order Execution")
st.markdown("---")

if len(st.session_state.pending_orders) == 0:
    st.success("🎉 No pending orders. Production queue is clear!")
    st.stop()

# --- Section 1: Pending Orders ---
st.subheader("📥 1. Pending Job Orders")
st.write("Select a pending order from sales to prepare for production:")

order_options = {order["id"]: order for order in st.session_state.pending_orders}
selected_id = st.selectbox("Select Order", list(order_options.keys()))
active_order = order_options[selected_id]

# Display Order Summary
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Customer", active_order["customer"])
    c2.metric("Material", active_order["material"])
    c3.metric("Width (mm)", active_order["width"])
    c4.metric("Required QTY", f'{active_order["qty"]:,}')

st.markdown("---")

# --- Section 2: Technical Setup ---
st.subheader("⚙️ 2. Technical Setup & Color Sequence")
st.write("Assign colors and Anilox rollers to the printing stations:")

# Default data for 8-color machine
default_sequence = pd.DataFrame([
    {"Station": "Unit 1", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 2", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 3", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 4", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 5", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 6", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 7", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"},
    {"Station": "Unit 8", "Color Name": "", "Anilox (BCM)": "Available", "Sticky Back": "0.38 Medium", "Status": "Skip"}
])

# Interactive Data Editor
edited_sequence = st.data_editor(
    default_sequence,
    column_config={
        "Status": st.column_config.SelectboxColumn("Status", options=["Active", "Skip"], required=True),
        "Anilox (BCM)": st.column_config.SelectboxColumn("Anilox (BCM)", options=st.session_state.anilox_library, required=True),
        "Color Name": st.column_config.TextColumn("Color Name", help="Enter Pantone or standard color")
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# --- Section 3: Requisitions ---
st.subheader("🎫 3. Requisitions & Tooling")
st.write("Issue requests to different departments before starting production:")

req_col1, req_col2, req_col3, req_col4 = st.columns(4)

with req_col1:
    if st.button("📦 Material Requisition", use_container_width=True):
        open_material_dialog(active_order)

with req_col2:
    if st.button("🎨 Ink Prep Request", use_container_width=True):
        open_ink_dialog(active_order)

with req_col3:
    if st.button("🖨️ Cliche Order (Al-Basit)", use_container_width=True):
        open_cliche_dialog(active_order)

with req_col4:
    if st.button("🧻 Core Request", use_container_width=True):
        open_core_dialog(active_order)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Section 4: Issue Work Order ---
st.subheader("🚀 4. Issue Work Order")
st.info("Issuing the work order will move this job from 'Pending' to 'In Production' and generate the Machine Job Ticket.")

if st.button("✅ Issue Work Order & Generate Ticket", type="primary", use_container_width=True):
    # Remove the order from pending list
    st.session_state.pending_orders = [o for o in st.session_state.pending_orders if o["id"] != active_order["id"]]
    
    st.balloons()
    st.success(f"Work Order for {active_order['id']} has been successfully issued to the shop floor!")
    st.rerun()
