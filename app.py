import streamlit as st
import auth

# --- Page Configuration ---
st.set_page_config(page_title="FlexoBrain Portal", page_icon="🏭", layout="centered")

# --- Authentication Check ---
# This will trigger the login screen if the user hasn't entered a valid password
if not auth.check_password():
    st.stop()

# --- Main Portal UI ---
st.title("🏭 Job Orders Hub")
st.markdown("---")

st.markdown("### 📋 Please select the type of job order:")
st.write("") # Empty space for layout breathing room

# Create 3 columns for the navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🏷️ **OPP Labels**")
    # Button linking directly to the OPP page
    st.page_link("pages/1_OPP_Label_Order.py", label="Open OPP Form", icon="➡️")

with col2:
    st.success("📦 **Shrink Films**")
    # Button linking directly to the Shrink Film page
    st.page_link("pages/2_Shrink_Film_Order.py", label="Open Shrink Form", icon="➡️")

with col3:
    st.warning("🛍️ **LDPE Bags**")
    # Button linking directly to the LDPE Bag page
    st.page_link("pages/3_LDPE_Bag_Order.py", label="Open LDPE Form", icon="➡️")
