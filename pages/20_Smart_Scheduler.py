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
# --- Universal Database Connection ---
# ==========================================
@st.cache_resource
def init_connection():
    try:
        # Fetching the secrets
        raw_url = st.secrets.get("SUPABASE_URL", "")
        raw_key = st.secrets.get("SUPABASE_KEY", "")
        
        # Radical Cleanup: Remove ALL invisible spaces, newlines, and literal quotes
        clean_url = str(raw_url).strip().replace('"', '').replace("'", "").replace("\n", "")
        clean_key = str(raw_key).strip().replace('"', '').replace("'", "").replace("\n", "")
        
        if not clean_url or not clean_key:
            st.error("⚠️ Credentials missing. Check Streamlit Secrets.")
            st.stop()
            
        return create_client(clean_url, clean_key)
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        st.stop()

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"⚠️ DB Error: {e}")
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
