if page == "Machine Management":
    st.title("⚙️ Machine Profile Configuration")
    st.markdown("Use this form to define the technical limits and capabilities of your machinery.")
    
    with st.form("detailed_machine_form"):
        # Section 1: Machine Identity
        st.subheader("General Identity")
        c1, c2, c3, c4 = st.columns(4)
        with c1: brand = st.text_input("Brand")
        with c2: model = st.text_input("Model")
        with c3: year = st.number_input("Manufacturing Year", value=2024)
        with c4: serial = st.text_input("Serial Number")

        # Section 2: Production Capabilities
        st.subheader("Performance & Configuration")
        c5, c6, c7 = st.columns(3)
        with c5: colors = st.number_input("Number of Colors", min_value=1, max_value=20, value=8)
        with c6: max_speed = st.number_input("Design Max Speed (m/min)", value=300)
        with c7: splice = st.selectbox("Splicing System", ["Auto Fly Splice", "Manual Roll Change"])

        # Section 3: Technical Dimensions
        st.subheader("Size & Repeat Limits")
        c8, c9, c10 = st.columns(3)
        with c8: min_rep = st.number_input("Min Repeat Length (mm)", value=300.0)
        with c9: max_rep = st.number_input("Max Repeat Length (mm)", value=800.0)
        with c10: max_mat_w = st.number_input("Max Material Width (mm)", value=1000.0)

        c11, c12, c13 = st.columns(3)
        with c11: max_print_w = st.number_input("Max Printing Width (mm)", value=980.0)
        with c12: unwind_d = st.number_input("Unwind Max Diameter (mm)", value=1000.0)
        with c13: rewind_d = st.number_input("Rewind Max Diameter (mm)", value=1000.0)

        # Section 4: Efficiency Parameters
        st.subheader("Waste & Downtime Analysis")
        c14, c15 = st.columns(2)
        with c14: splice_time = st.number_input("Estimated Time Waste per Splice (min)", value=5.0 if splice == "Manual Roll Change" else 0.5)
        with c15: splice_waste = st.number_input("Estimated Material Waste per Splice (m)", value=20.0 if splice == "Manual Roll Change" else 2.0)

        if st.form_submit_button("Save Full Machine Profile"):
            machine_data = {
                "machine_name": f"{brand} {model}",
                "brand": brand,
                "model": model,
                "manufacturing_year": year,
                "serial_no": serial,
                "num_colors": colors,
                "max_speed": max_speed,
                "splice_type": splice,
                "min_repeat_length": min_rep,
                "max_repeat_length": max_rep,
                "max_material_width": max_mat_w,
                "max_printing_width": max_print_w,
                "unwind_max_diameter": unwind_d,
                "rewind_max_diameter": rewind_d,
                "splice_time_waste": splice_time,
                "splice_material_waste": splice_waste
            }
            try:
                supabase.table("machines").insert(machine_data).execute()
                st.success(f"Profile for {brand} {model} has been successfully registered.")
            except Exception as e:
                st.error(f"Failed to save profile: {e}")
