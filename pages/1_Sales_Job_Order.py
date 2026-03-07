import streamlit as st
import datetime
import pandas as pd
import io
from fpdf import FPDF

# --- Section 1: Fixed SVG Drawing (Extra Wide to prevent clipping) ---
def draw_final_svg(item_n, item_f, art_no, direction_t):
    svg_code = f"""
    <div style="text-align: center; background: white; padding: 25px; border-radius: 15px; border: 2px solid #1e3a8a;">
        <svg width="380" height="260" viewBox="0 0 380 260" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="370" height="250" rx="15" fill="none" stroke="#1e3a8a" stroke-width="1"/>
            
            <rect x="180" y="20" width="180" height="70" rx="8" fill="#1e3a8a" />
            <text x="270" y="45" font-family="Arial" font-size="13" font-weight="bold" fill="white" text-anchor="middle">{direction_t}</text>
            <text x="270" y="75" font-family="Arial" font-size="12" fill="#93c5fd" text-anchor="middle">Art No: {art_no if art_no else "N/A"}</text>

            <circle cx="90" cy="110" r="55" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="110" r="20" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="55" y1="110" x2="125" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            <line x1="90" y1="75" x2="90" y2="145" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="4"/>
            
            <path d="M 90 165 L 280 165 L 280 195 L 90 195" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="150" y1="165" x2="150" y2="195" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="210" y1="165" x2="210" y2="195" stroke="#1e3a8a" stroke-dasharray="3"/>

            <text x="190" y="225" font-family="Arial" font-size="16" font-weight="bold" fill="#1e3a8a" text-anchor="middle">{item_n if item_n else "ITEM NAME"}</text>
            <text x="190" y="248" font-family="Arial" font-size="12" fill="#64748b" text-anchor="middle">{item_f if item_f else "ITEM FORMAT"}</text>
        </svg>
    </div>
    """
    return svg_code

# --- App Logic ---
st.set_page_config(page_title="Flexo ERP - Job Order", layout="wide")
st.title("📝 Sales Job Order Creation")

# 🟢 STEP 1: Select Work Type
product_type = st.selectbox("Product Type", ["Select Product Type...", "Printed OPP Label", "Printed PE Shrink Film", "Printed LDPE Bag"])

if product_type != "Select Product Type...":
    st.markdown("---")
    
    # 📦 2. Identification
    col_i1, col_i2 = st.columns(2)
    item_name = col_i1.text_input("Item Name")
    item_format = col_i2.text_input("Item Format")

    # 👤 3. Customer & Tech Specs
    col_c1, col_c2, col_c3 = st.columns(3)
    company_name = col_c1.text_input("Company Name")
    sales_po = col_c2.text_input("Sales PO#")
    artwork_no = col_c3.text_input("Artwork No.")

    col_s1, col_s2, col_s3 = st.columns(3)
    material = col_s1.selectbox("Material", ["BOPP", "PE", "PETG"])
    width = col_s2.number_input("Width (mm)", min_value=0.0)
    repeat = col_s3.number_input("Repeat Length (mm)", min_value=0.0)

    # 🔄 4. Visual & CALCULATOR (RE-INSTATED WITH ALL WARNINGS)
    st.markdown("---")
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        st.subheader("🔄 Production View")
        winding_direction = st.selectbox("Winding Direction#", ["Clockwise #4", "Anti-clockwise #3"])
        st.markdown(draw_final_svg(item_name, item_format, artwork_no, winding_direction), unsafe_allow_html=True)

    with col_v2:
        st.subheader("🧮 Smart Web & Production Calculator")
        c1, c2, c3 = st.columns(3)
        m_length = c1.number_input("Mother Roll Length (m)", min_value=0)
        m_width = c2.number_input("Mother Roll Width (mm)", min_value=0)
        lanes = c3.number_input("No. of Lines (Lanes)", min_value=1, value=1)
        
        # Calculations Logic
        pcs_per_roll = int((m_length * 1000) / repeat) if repeat > 0 else 0
        total_waste = float(m_width - (width * lanes)) if m_width > 0 else 0
        unused_waste = float(total_waste - 24) if total_waste > 0 else 0
        total_production = pcs_per_roll * lanes

        # Warnings & Display
        res1, res2, res3 = st.columns(3)
        res1.metric("Pcs / Roll", f"{pcs_per_roll:,}")
        res2.metric("Total Waste (mm)", f"{total_waste} mm")
        res3.metric("Unused Waste (mm)", f"{unused_waste} mm")

        # --- THE WARNING SYSTEM ---
        if m_width > 0 and width > 0:
            required_w = (width * lanes) + 24
            if required_w > m_width:
                st.error(f"🚨 **WIDTH ERROR:** Required is {required_w}mm, but Mother Roll is {m_width}mm!")
            elif unused_waste > 10:
                st.warning(f"⚠️ **UNUSED MATERIAL WARNING:** You have {unused_waste}mm of extra waste!")

    # 📦 5. Quantity & Warnings
    st.markdown("---")
    st.subheader("📦 Quantity & Delivery")
    q_col1, q_col2 = st.columns(2)
    order_qty = q_col1.number_input("Order Quantity (Pcs)", min_value=0)
    
    if order_qty > 0 and total_production > 0:
        if order_qty != total_production:
            st.error(f"🚨 **QUANTITY MISMATCH:** Order asks for {order_qty:,} pcs, but production yields {total_production:,} pcs!")
        else:
            st.success("✅ Quantity matches production yield.")

    due_date = q_col2.date_input("Due Date")

    # 🎯 6. Actions
    st.markdown("---")
    if st.button("💾 Generate Final Job Order", type="primary", use_container_width=True):
        st.balloons()
        st.success("Job Order Ready for Production!")
