import streamlit as st
import json
import os
import pandas as pd
import auth 

# Security: Admin only can access this page
auth.require_role(["admin"])

st.set_page_config(page_title="User Management", page_icon="👥", layout="wide")

st.title("👥 User Management & Permissions (Admin Only)")
st.markdown("---")

DB_FILE = "users_db.json"

# 1. Load users database
def load_users():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"password": "123", "name": "System Administrator", "role": "admin"}}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=4)
        return default_db
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. Save users database
def save_users(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

users_db = load_users()

# ==========================================
# Add New Employee Form
# ==========================================
with st.expander("➕ Add New Factory Employee", expanded=True):
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            emp_id = st.text_input("Employee ID (Username) *e.g., E105*")
            emp_name = st.text_input("Full Employee Name")
        with col2:
            emp_pass = st.text_input("Password", type="password")
            emp_role = st.selectbox("Assign Role", [
                "sales", 
                "production", 
                "ink_tech", 
                "press_op",
                "admin"
            ])
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            submit = st.form_submit_button("💾 Create User Account", type="primary", use_container_width=True)
            
        if submit:
            if emp_id and emp_name and emp_pass:
                if emp_id in users_db:
                    st.error(f"❌ Employee ID {emp_id} already exists!")
                else:
                    users_db[emp_id] = {"password": emp_pass, "name": emp_name, "role": emp_role}
                    save_users(users_db)
                    st.success(f"✅ Employee {emp_name} account created successfully!")
                    st.rerun()
            else:
                st.warning("⚠️ Please fill in all required fields.")

# ==========================================
# Current Employees Directory Table
# ==========================================
st.markdown("### 📋 Authorized Employees Directory")
if users_db:
    df_users = pd.DataFrame.from_dict(users_db, orient='index').reset_index()
    df_users.rename(columns={'index': 'Employee ID (Username)', 'name': 'Full Name', 'role': 'Role', 'password': 'Password'}, inplace=True)
    # Mask passwords for security
    df_users['Password'] = "****" 
    
    st.dataframe(df_users, use_container_width=True, hide_index=True)
