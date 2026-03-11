# --- تقسيم المنطقة العلوية لإضافة الأيقونة على اليمين ---
col_title, col_icon = st.columns([5, 1]) 

with col_title:
    st.title("📝 Create New Job Order - OPP Label (Wrap Around)")

with col_icon:
    st.markdown(
        """
        <div style="border: 2px solid #ddd; padding: 10px; border-radius: 10px; text-align: center; background-color: white; display: flex; justify-content: center;">
            <svg width="120" height="70" viewBox="0 0 120 70" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#555" />
                    </marker>
                </defs>
                
                <rect x="14" y="10" width="12" height="4" rx="1" fill="#ddd" stroke="#555" stroke-width="1.5"/>
                <rect x="10" y="15" width="20" height="40" rx="4" fill="#f9f9f9" stroke="#555" stroke-width="1.5"/>
                <rect x="10" y="30" width="20" height="15" fill="#ddd" stroke="#555" stroke-width="1.5"/>
                
                <path d="M 90 20 C 100 20, 105 27, 105 35 C 105 43, 100 50, 90 50" fill="#f0f0f0" stroke="#555" stroke-width="1.5"/>
                <path d="M 90 20 L 50 20 L 50 50 L 90 50 Z" fill="#fff" stroke="#555" stroke-width="1.5"/>
                <ellipse cx="90" cy="35" rx="6" ry="15" fill="#f9f9f9" stroke="#555" stroke-width="1.5"/>
                <ellipse cx="90" cy="35" rx="2" ry="5" fill="#fff" stroke="#555" stroke-width="1.5"/>
                
                <rect x="55" y="25" width="25" height="20" rx="2" fill="#313131"/>
                <text x="67.5" y="38" font-family="Arial" font-size="7" fill="#fff" text-anchor="middle">LABEL</text>
                
                <line x1="50" y1="60" x2="100" y2="60" stroke="#555" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
            </svg>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.markdown("---")
