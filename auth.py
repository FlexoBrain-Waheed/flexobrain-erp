import streamlit as st

# ==========================================
# 1. Define Roles and Passwords
# ==========================================
ROLE_PASSWORDS = {
    "p11": "sales",       # Sales Department
    "p22": "production",  # Production Department
    "p33": "admin"        # Top Management (Full Access)
}

# ==========================================
# 2. Elegant Login Interface
# ==========================================
def login_form():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🧠 FlexoBrain ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Please enter your department password</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("🚪 Login", type="primary", use_container_width=True):
                if password in ROLE_PASSWORDS:
                    # Save login state and set user role
                    st.session_state["authenticated"] = True
                    st.session_state["role"] = ROLE_PASSWORDS[password]
                    st.session_state["user_id"] = password  # <--- Added to track specific user ID
                    st.rerun()
                else:
                    st.error("❌ Invalid Password!")

# ==========================================
# 3. Core Authentication Function
# ==========================================
def check_password():
    """Checks if the user is already logged in."""
    if not st.session_state.get("authenticated"):
        login_form()
        st.stop() # Stops the rest of the page from running until logged in
    return True

# ==========================================
# 4. Department Guard (Role Access Control)
# ==========================================
def require_role(allowed_roles):
    """
    Allows access only to specified roles (and always allows admin).
    allowed_roles: list, e.g., ["sales"]
    """
    check_password() # Ensure user is logged in first
    
    current_role = st.session_state.get("role")
    
    # Admin has a master key, can enter anywhere
    if current_role == "admin":
        return True
        
    # If user role is in the allowed roles for this page
    if current_role in allowed_roles:
        return True
    
    # If an employee tries to access an unauthorized page:
    st.error("⛔ Sorry, you do not have permission to access this section.")
    st.info("💡 This section is reserved for other departments. Please select your department's page from the sidebar.")
    st.stop()

# ==========================================
# 5. Logout Button
# ==========================================
def logout_button():
    """Places a logout button in the sidebar."""
    if st.session_state.get("authenticated"):
        st.sidebar.markdown("---")
        # Display department role for clarity
        role_display = st.session_state.get("role").upper()
        st.sidebar.caption(f"👤 Logged in as: **{role_display}**")
        
        if st.sidebar.button("Logout 🚪", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
