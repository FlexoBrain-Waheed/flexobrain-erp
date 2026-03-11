import streamlit as st

def check_password():
    """Returns True if the user had entered the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Delete password from session state for security
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First time opening the app
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔒 3P Packaging Factory ERP</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: gray;'>Please enter the password to access the system</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("🔑 Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # If the password is wrong
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔒 3P Packaging Factory ERP</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("🔑 Password:", type="password", on_change=password_entered, key="password")
            st.error("🚨 Incorrect password, please try again.")
        return False
    else:
        # Password is correct
        return True
