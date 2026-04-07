import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        # Check for admin password
        if st.session_state["password"] == st.secrets["passwords"]["admin"]:
            st.session_state["password_correct"] = True
            st.session_state["role"] = "admin"
            del st.session_state["password"]  # Don't store password
            
        # Check for orders password
        elif st.session_state["password"] == st.secrets["passwords"]["orders"]:
            st.session_state["password_correct"] = True
            st.session_state["role"] = "orders"
            del st.session_state["password"]  # Don't store password
            
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔒 Please enter your password:", type="password", on_change=password_entered, key="password"
        )
        return False
        
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "🔒 Please enter your password:", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Incorrect password")
        return False
        
    else:
        # Password correct
        return True
