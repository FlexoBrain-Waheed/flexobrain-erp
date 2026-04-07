import streamlit as st

def show_smart_sidebar():
    """Hides the default sidebar and builds a role-based custom sidebar"""
    
    # 1. Hide the default Streamlit sidebar menu using CSS
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # 2. Build the custom, professional sidebar
    with st.sidebar:
        st.markdown("### 🏭 FlexoBrain")
        st.page_link("app.py", label="Main Hub", icon="🏠")
        
        role = st.session_state.get("role")
        
        st.markdown("---")
        st.markdown("#### 📋 Job Orders")
        st.page_link("pages/1_OPP_Label_Order.py", label="OPP Labels", icon="🏷️")
        st.page_link("pages/2_Shrink_Film_Order.py", label="Shrink Films", icon="📦")
        st.page_link("pages/3_LDPE_Bag_Order.py", label="LDPE Bags", icon="🛍️")
        
        # Show Admin menu ONLY if role is admin
        if role == "admin":
            st.markdown("---")
            st.markdown("#### ⚙️ Admin Settings")
            st.page_link("pages/4_Anilox_Library.py", label="Anilox Library", icon="🖨️")
            st.page_link("pages/5_Machine_Setup.py", label="Machine Setup", icon="🎛️")
            
        st.markdown("---")
        
        # Log out button
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets["passwords"]["admin"]:
            st.session_state["password_correct"] = True
            st.session_state["role"] = "admin"
            del st.session_state["password"]
            
        elif st.session_state["password"] == st.secrets["passwords"]["orders"]:
            st.session_state["password_correct"] = True
            st.session_state["role"] = "orders"
            del st.session_state["password"]
            
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔒 Please enter your password:", type="password", on_change=password_entered, key="password"
        )
        return False
        
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Please enter your password:", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Incorrect password")
        return False
        
    else:
        # Password is correct! Show the smart sidebar before loading the page content
        show_smart_sidebar()
        return True
