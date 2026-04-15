import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from supabase import create_client, Client

# --- Page configuration ---
st.set_page_config(page_title="Smart Scheduler", page_icon="🗓️", layout="wide")

# --- Authentication Setup ---
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import auth
auth.require_role(["production", "admin"])
auth.logout_button()

# --- Version Control ---
st.markdown("<div style='text-align: right; color: gray; font-size: 12px;'>Version No. 01 - FlexoBrain AI Scheduler</div>", unsafe_allow_html=True)

# ==========================================
# --- Supabase Database Connection (Secure) ---
# ==========================================
@st.cache_resource
def init_connection():
    # Safely fetching credentials from Streamlit Secrets
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# ==========================================
# --- Main UI: Smart Scheduling Board ---
# ==========================================
st.title("🗓️ FlexoBrain Smart Scheduler")
st.markdown("Optimize your production queue to minimize setup time, web changes, and wash-ups.")
st.markdown("---")

# --- Fetch Pending Orders ---
def fetch_pending_orders():
    try:
        response = supabase.table("job_orders").select("id, order_number, customer_name, material_type, thickness_micron, label_width_mm, repeat_length_mm, colors_count, status").eq("status", "pending").execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

pending_orders = fetch_pending_orders()

if not pending_orders:
    st.success("🎉 Queue is clear! No pending orders to schedule.")
else:
    # Convert to DataFrame for Analysis
    df = pd.DataFrame(pending_orders)
    
    # --- FlexoBrain Smart Insights (AI Logic) ---
    st.subheader("🧠 Smart Optimization Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("💡 **Web & Material Optimization**")
        material_groups = df.groupby('material_type').size()
        for mat, count in material_groups.items():
            st.write(f"- You have **{count}** orders using **{mat}**. Group them to save material splicing time.")
            
    with col2:
        st.success("⚙️ **Cylinder & Repeat Optimization**")
        repeat_groups = df.groupby('repeat_length_mm').size()
        for rep, count in repeat_groups.items():
            if count > 1:
                st.write(f"- 🚀 **{count}** orders use the **{rep}mm** cylinder. Run them sequentially to skip cylinder changes!")

    st.markdown("---")
    
    # --- Interactive Sequencing Board ---
    st.subheader("📋 Production Sequence Planner")
    st.caption("Drag columns or sort by clicking headers to plan your perfect run. (Priority feature coming soon)")
    
    # Clean up dataframe for display
    display_df = df[['order_number', 'customer_name', 'material_type', 'thickness_micron', 'repeat_length_mm', 'label_width_mm', 'colors_count']]
    display_df.columns = ['Order No.', 'Customer', 'Material', 'Thickness (µ)', 'Cylinder/Repeat (mm)', 'Web Width (mm)', 'Colors']
    
    # Show interactive dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )
    
    # --- Action Area ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("💾 Save Optimal Sequence to Production Board", type="primary", use_container_width=True, help="Will reorder the Kanban board based on your selection.")
