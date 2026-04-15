import streamlit as st
import json
import os

DB_FILE = "users_db.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {"admin": {"password": "123", "name": "System Administrator", "role": "admin"}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def login_form():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🏭 FlexoBrain ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Employee Login Portal</p>", unsafe_allow_html=True)
    
    users_db = load_users()
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            username = st.text_input("👤 Employee ID (Username)", key="login_user")
            password = st.text_input("🔒 Password", type="password", key="login_pass")
            
            if st.button("🚪 Login", type="primary", use_container_width=True):
                if username in users_db and users_db[username]["password"] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = users_db[username]["role"]
                    st.session_state["name"] = users_db[username]["name"]
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password!")

def check_password():
    """Checks if the user is logged in. If not, shows the login form."""
    if not st.session_state.get("authenticated"):
        login_form()
        st.stop()
    return True

def require_role(allowed_roles):
    """Guards pages based on user roles."""
    check_password()
    current_role = st.session_state.get("role")
    
    # Admin has master access
    if current_role == "admin":
        return True
    
    if current_role in allowed_roles:
        return True
        
    st.error("⛔ Access Denied. You do not have permission to view this section.")
    st.stop()

def logout_button():
    """Displays user info and a logout button in the sidebar."""
    if st.session_state.get("authenticated"):
        st.sidebar.markdown("---")
        name = st.session_state.get("name")
        role = st.session_state.get("role").upper()
        st.sidebar.caption(f"👤 {name} ({role})")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
