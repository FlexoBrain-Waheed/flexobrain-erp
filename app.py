import streamlit as st

# Main page configuration
st.set_page_config(page_title="FlexoBrain ERP", page_icon="🧠", layout="wide")

# System welcome and title
st.title("🧠 FlexoBrain ERP System")
st.markdown("---")

st.markdown("""
### Welcome to the Future of Flexo Printing Management!
This system is designed using Clean Architecture to manage:
* 📝 **Sales & Production Orders**
* ⚙️ **Machine Configurations**
* 🎨 **Anilox Library & Inventory**
* 📊 **Live Production Tracking (IoT)**

👈 **Please use the sidebar menu to navigate through the modules.**
""")

# You can later add quick statistics here (e.g., pending orders, machine status, etc.)
st.info("System is Online and Ready. 🚀")
