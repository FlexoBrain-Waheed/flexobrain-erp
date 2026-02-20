import streamlit as st
from supabase import create_client, Client

# Database connection setup
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Page configuration
st.set_page_config(page_title="FlexoBrain ERP", layout="wide")

st.title("📂 FlexoBrain - Job Order System")
st.markdown("---")

with st.form("job_order_form"):
    st.subheader("Order Details")
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input("Client Name")
        po_number = st.text_input("PO Number")
        product_type = st.selectbox("Product Type", ["Labels", "Flexible Packaging", "Shrink Film", "Other"])
        quantity = st.number_input("Order Quantity", min_value=0)

    with col2:
        target_speed = st.number_input("Target Speed (m/min)", min_value=0)
        web_width = st.number_input("Web Width (mm)", min_value=0.0)
        material_color = st.text_input("Material Color")
        roll_change = st.radio("Roll Changeover", ["Auto Splicer", "Manual Stop"])

    submit_button = st.form_submit_button("Save Job Order")

    if submit_button:
        # Prepare data for insertion
        data = {
            "client_name": client_name,
            "po_number": po_number,
            "product_type": product_type,
            "quantity": quantity,
            "target_speed": target_speed,
            "web_width": web_width,
            "material_color": material_color,
            "roll_changeover": roll_change
        }
        
        try:
            # Insert data into Supabase
            response = supabase.table("job_orders").insert(data).execute()
            st.success(f"✔️ Success! Job Order for '{client_name}' has been saved.")
        except Exception as e:
            st.error(f"❌ Error: Could not save data. {e}")
