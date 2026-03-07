import streamlit as st
import datetime
import pandas as pd
import io

# --- Section 1: Simple & Clean SVG (Fixed for No Errors) ---
def draw_simple_svg(item_n, item_f, art_no, direction_t):
    svg_code = f"""
    <div style="text-align: center; background: white; padding: 20px; border-radius: 12px; border: 2px solid #1e3a8a;">
        <svg width="360" height="210" viewBox="0 0 360 210" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="350" height="200" rx="10" fill="none" stroke="#d1d5db" stroke-width="1"/>
            
            <rect x="190" y="20" width="150" height="55" rx="5" fill="#1e3a8a" />
            <text x="265" y="42" font-family="Arial" font-size="11" font-weight="bold" fill="white" text-anchor="middle">{direction_t}</text>
            <text x="265" y="62" font-family="Arial" font-size="10" fill="#93c5fd" text-anchor="middle">Art No: {art_no if art_no else "N/A"}</text>

            <circle cx="75" cy="85" r="45" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="2"/>
            <circle cx="75" cy="85" r="15" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            
            <path d="M 75 130 L 300 130 L 300 160 L 75 160" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="150" y1="130" x2="150" y2="160" stroke="#1e3a8a" stroke-dasharray="4"/>
            <line x1="225" y1="130" x2="225" y2="160" stroke="#1e3a8a" stroke-dasharray="4"/>

            <text x="180" y="185" font-family="Arial" font-size="13" font-weight="bold" fill="#1e3a8a" text-anchor="middle">{item_n if item_n else "ITEM NAME"}</text>
            <text x="180" y="202" font-family="Arial" font-size="10" fill="#64748b" text-anchor="middle">{item_f if item_f else "ITEM FORMAT"}</text>
        </svg>
    </div>
    """
    return svg_code

# --- Main App ---
st.set_page_config(page_title="Flexo ERP", layout="wide")
st.title("📝 Sales Job Order Creation")

product_type = st.selectbox("Product Type", ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film"])

if product_type != "Select Product Type...":
    st.markdown("---")
    
    # 📦 Identification
    col_i1, col_i2 = st.columns(2)
    item_name = col_i1.text_input("Item Name")
    item_format = col_i2.text_input("Item Format")

    # 👤 Info & Specs
    col_c1, col_c2, col_c3 = st.columns(3)
    company_name = col_c1.text_input("Company Name")
    sales_po = col_c2.text_input("Sales PO#")
    artwork_no = col_c3.text_input("Artwork No.")

    col_s1, col_s2, col_s3 = st.columns(3)
    material = col_s1.selectbox("Material", ["BOPP", "PE", "PETG"])
    width = col_s2.number_input("Width (mm)", min_value=0.0)
    repeat = col_s3.number_input("Repeat Length (mm)", min_value=0.0)

    # 🔄 Visuals & Smart Calculator
    st.markdown("---")
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        st.subheader("🔄 Production View")
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        st.markdown(draw_simple_svg(item_name, item_format, artwork_no, winding_direction), unsafe_allow_html=True)

    with col_v2:
        st.subheader("🧮 Smart Web & Production Calculator")
        c1, c2, c3, c_edge = st.columns(4)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        # Added Edge Trim 12+12
        edge_trim_val = c_edge.number_input("Edge Trim 12+12", value=24, disabled=True)
        
        # Corrected Calculation Variables
        pcs_per_roll = int((m_length * 1000) / repeat) if repeat > 0 else 0
        total_waste = float(m_width - (width * lanes)) if m_width > 0 else 0.0
        unused_material = float(total_waste - edge_trim_val) if total_waste > 0 else 0.0
        total_production = pcs_per_roll * lanes

        # Display Metrics
        res1, res2, res3 = st.columns(3)
        res1.metric("Pcs / Roll", f"{pcs_per_roll:,}")
        res2.metric("Total Waste (mm)", f"{total_waste} mm")
        res3.metric("Unused Material (mm)", f"{unused_material} mm")

        # --- CORRECTED WARNING SYSTEM ---
        if m_width > 0 and width > 0:
            required_width = (width * lanes) + edge_trim_val
            if required_width > m_width:
                st.error(f"🚨 **WIDTH ERROR:** Required is {required_width}mm, but Mother Roll is {m_width}mm!")
            elif unused_material > 10: # Fixed variable name here
                st.warning(f"⚠️ **UNUSED MATERIAL WARNING:** You have {unused_material}mm extra waste!")

    # 📦 Quantity Validation
    st.markdown("---")
    st.subheader("📦 Order Quantity & Validation")
    q_col1, q_col2 = st.columns(2)
    order_qty = q_col1.number_input("Requested Quantity (Pcs)", min_value=0)
    
    if order_qty > 0 and total_production > 0:
        if order_qty != total_production:
            st.error(f"🚨 **QUANTITY MISMATCH:** Order asks for {order_qty:,} pcs, but production yields {total_production:,} pcs!")
        else:
            st.success("✅ Quantity perfectly matches production yield.")

    due_date = q_col2.date_input("Due Date")

    if st.button("💾 Finalize Job Order", type="primary", use_container_width=True):
        st.success(f"Job Order for {item_name} has been generated successfully!")
