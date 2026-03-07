import streamlit as st
import datetime
import pandas as pd
import io

# --- Section 1: Simple & Clean SVG Drawing (No Cropping) ---
def draw_clean_svg(item_n, item_f, art_no, direction_t):
    # Expanded canvas to 400x220 for maximum safety against clipping
    svg_code = f"""
    <div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">
        <svg width="380" height="220" viewBox="0 0 380 220" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="370" height="210" rx="10" fill="none" stroke="#d1d5db" stroke-width="1"/>
            
            <rect x="200" y="20" width="160" height="60" rx="5" fill="#1e3a8a" />
            <text x="280" y="45" font-family="Arial" font-size="12" font-weight="bold" fill="white" text-anchor="middle">{direction_t}</text>
            <text x="280" y="68" font-family="Arial" font-size="11" fill="#93c5fd" text-anchor="middle">Art No: {art_no if art_no else "N/A"}</text>

            <circle cx="80" cy="90" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="2"/>
            <circle cx="80" cy="90" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            
            <path d="M 80 140 L 320 140 L 320 170 L 80 170" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="160" y1="140" x2="160" y2="170" stroke="#1e3a8a" stroke-dasharray="4"/>
            <line x1="240" y1="140" x2="240" y2="170" stroke="#1e3a8a" stroke-dasharray="4"/>

            <text x="190" y="195" font-family="Arial" font-size="15" font-weight="bold" fill="#1e3a8a" text-anchor="middle">{item_n if item_n else "ITEM NAME"}</text>
            <text x="190" y="212" font-family="Arial" font-size="11" fill="#64748b" text-anchor="middle">{item_f if item_f else "ITEM FORMAT"}</text>
        </svg>
    </div>
    """
    return svg_code

# --- Main App ---
st.set_page_config(page_title="NexFlexo ERP", layout="wide")
st.title("📝 Sales Job Order Creation")

product_type = st.selectbox("Product Type", ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film"])

if product_type != "Select Product Type...":
    st.markdown("---")
    
    # Identification
    col_i1, col_i2 = st.columns(2)
    item_name = col_i1.text_input("Item Name")
    item_format = col_i2.text_input("Item Format")

    # Info & Specs
    col_c1, col_c2, col_c3 = st.columns(3)
    company_name = col_c1.text_input("Company Name")
    sales_po = col_c2.text_input("Sales PO#")
    artwork_no = col_c3.text_input("Artwork No.")

    col_s1, col_s2, col_s3 = st.columns(3)
    material = col_s1.selectbox("Material", ["BOPP", "PE", "PETG"])
    width = col_s2.number_input("Width (mm)", min_value=0.0)
    repeat = col_s3.number_input("Repeat Length (mm)", min_value=0.0)

    # Visuals & Smart Calculator
    st.markdown("---")
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        st.subheader("🔄 Production View")
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        st.markdown(draw_clean_svg(item_name, item_format, artwork_no, winding_direction), unsafe_allow_html=True)

    with col_v2:
        st.subheader("🧮 Smart Web & Production Calculator")
        c1, c2, c3, c_edge = st.columns(4)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        # UPDATED: Edge Trim is now INTERACTIVE
        edge_trim_val = c_edge.number_input("Edge Trim Total", value=24, help="Default is 12+12=24mm")

        # Core Calculations
        pcs_per_roll = int((m_length * 1000) / repeat) if repeat > 0 else 0
        total_waste = float(m_width - (width * lanes)) if m_width > 0 else 0.0
        unused_material = float(total_waste - edge_trim_val) if total_waste > 0 else 0.0
        total_production = pcs_per_roll * lanes

        # Metrics Display
        res1, res2, res3 = st.columns(3)
        res1.metric("Pcs / Roll", f"{pcs_per_roll:,}")
        res2.metric("Total Waste (mm)", f"{total_waste} mm")
        res3.metric("Unused Material (mm)", f"{unused_material} mm")

        # --- FULL WARNING SYSTEM ---
        if m_width > 0 and width > 0:
            required_width = (width * lanes) + edge_trim_val
            if required_width > m_width:
                st.error(f"🚨 **WIDTH ERROR:** Required width is {required_width}mm, but Mother Roll is only {m_width}mm!")
            elif unused_material > 10:
                st.warning(f"⚠️ **WASTE WARNING:** You have {unused_material}mm of unused material beyond edge trim!")

    # Quantity Validation
    st.markdown("---")
    st.subheader("📦 Order Quantity & Validation")
    q_col1, q_col2 = st.columns(2)
    order_qty = q_col1.number_input("Requested Quantity (Pcs)", min_value=0)
    
    if order_qty > 0 and total_production > 0:
        if order_qty != total_production:
            st.error(f"🚨 **QUANTITY MISMATCH:** Order asks for {order_qty:,} pcs, but production yields {total_production:,} pcs!")
        else:
            st.success("✅ Order quantity perfectly matches production yield.")

    due_date = q_col2.date_input("Due Date")

    if st.button("💾 Finalize Job Order", type="primary", use_container_width=True):
        st.success(f"Job Order for {item_name} has been processed successfully!")
