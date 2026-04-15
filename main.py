import streamlit as st

# ==========================================
# 1. Page Configuration (Gateway)
# ==========================================
st.set_page_config(page_title="FlexoBrain - Login", page_icon="🏭", layout="centered")

# ==========================================
# 2. Mock Database for Users (Created by Admin only)
# ==========================================
# In production, this comes from Supabase "users" table
USERS_DB = {
    "admin": {"password": "123", "role": "admin", "name": "System Admin (Waheed)"},
    "sales_ali": {"password": "123", "role": "sales", "name": "Ali (Sales Dept)"},
    "ink_sami": {"password": "123", "role": "ink_tech", "name": "Sami (Ink Kitchen)"},
    "press_omar": {"password": "123", "role": "press_op", "name": "Omar (Machine Operator)"}
}

# ==========================================
# 3. Session State Initialization
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""
if "name" not in st.session_state:
    st.session_state["name"] = ""

# ==========================================
# 4. Login Function
# ==========================================
def login():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏭 FlexoBrain ERP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6B7280;'>Authorized Personnel Only</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Simple, clean login form (No Registration, No Email)
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        submit_button = st.form_submit_button("LOGIN", type="primary", use_container_width=True)
        
        if submit_button:
            if username in USERS_DB and USERS_DB[username]["password"] == password:
                # Success! Save user data to session memory
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = USERS_DB[username]["role"]
                st.session_state["name"] = USERS_DB[username]["name"]
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password. Please contact your Administrator.")

# ==========================================
# 5. Smart Routing (Role-Based Access Control)
# ==========================================
def main_dashboard():
    # Sidebar Profile Info & Logout
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state['name']}")
        st.caption(f"Role: {st.session_state['role'].upper()}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown("---")
        st.markdown("### 🧭 Navigation Menu")

    role = st.session_state["role"]

    # ---------------------------------------------------------
    # ROUTE 1: ADMIN (Sees Everything)
    # ---------------------------------------------------------
    if role == "admin":
        st.sidebar.success("All Systems Accessible")
        page = st.sidebar.radio("Go to:", [
            "📊 Executive Dashboard", 
            "📝 1. Job Creation (Sales)", 
            "🏭 2. Press Monitoring", 
            "🎨 3. Ink Kitchen QC",
            "👥 User Management"
        ])
        
        st.title("📊 Admin Executive Dashboard")
        st.info("As an Admin, you have access to all factory modules from the left menu.")
        # Here we will later import the other python files based on selection

    # ---------------------------------------------------------
    # ROUTE 2: INK TECHNICIAN (Sees only Ink Kitchen)
    # ---------------------------------------------------------
    elif role == "ink_tech":
        st.sidebar.warning("Restricted Access")
        page = st.sidebar.radio("Go to:", ["🎨 3. Ink Kitchen QC"])
        
        st.title("🎨 Ink Kitchen Terminal")
        st.info("This is where the code from '3_Ink_Kitchen.py' will be loaded.")
        # import 3_Ink_Kitchen as ink; ink.run()

    # ---------------------------------------------------------
    # ROUTE 3: PRESS OPERATOR (Sees only Shop Floor)
    # ---------------------------------------------------------
    elif role == "press_op":
        st.sidebar.error("Machine Operator Access")
        page = st.sidebar.radio("Go to:", ["🏭 2. Press Monitoring"])
        
        st.title("🏭 Press Monitoring Terminal")
        st.info("This is where the code from '2_Shop_Floor.py' will be loaded.")

    # ---------------------------------------------------------
    # ROUTE 4: SALES (Sees only Job Creation)
    # ---------------------------------------------------------
    elif role == "sales":
        st.sidebar.info("Sales Access")
        page = st.sidebar.radio("Go to:", ["📝 1. Job Creation (Sales)"])
        
        st.title("📝 Sales & Job Order Creation")
        st.info("This is where the code for Sales will be loaded.")

# ==========================================
# 6. Execution Engine
# ==========================================
if not st.session_state["logged_in"]:
    # Hide sidebar during login
    st.markdown("""<style>[data-testid="collapsedControl"] {display: none;}</style>""", unsafe_allow_html=True)
    login()
else:
    # Show sidebar and load dashboard
    main_dashboard()
