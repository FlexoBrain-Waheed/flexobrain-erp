# --- Corrected & Full-View SVG Drawing Function ---
def draw_winding_svg(direction):
    if "Clockwise" in direction and "Anti" not in direction:
        # Clockwise #4: Web opens from TOP, Arrow moves WITH clock
        svg = """
        <svg width="280" height="160" viewBox="0 0 280 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444" />
                </marker>
            </defs>
            <circle cx="90" cy="80" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="80" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="60" y1="80" x2="120" y2="80" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="90" y1="50" x2="90" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 90 30 L 230 30 L 230 55 L 90 55" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="140" y1="30" x2="140" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="190" y1="30" x2="190" y2="55" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 50 50 A 55 55 0 0 1 130 50" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead)"/>
        </svg>
        """
    else:
        # Anti-clockwise #3: Web opens from BOTTOM, Arrow moves AGAINST clock
        svg = """
        <svg width="280" height="160" viewBox="0 0 280 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrowhead_inv" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                    <polygon points="10 0, 0 3.5, 10 7" fill="#ef4444" />
                </marker>
            </defs>
            <circle cx="90" cy="80" r="50" fill="#f0f4ff" stroke="#1e3a8a" stroke-width="3"/>
            <circle cx="90" cy="80" r="18" fill="white" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="60" y1="80" x2="120" y2="80" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <line x1="90" y1="50" x2="90" y2="110" stroke="#1e3a8a" stroke-width="1" stroke-dasharray="3"/>
            <path d="M 90 130 L 230 130 L 230 155 L 90 155" fill="#f9fafb" stroke="#1e3a8a" stroke-width="2"/>
            <line x1="140" y1="130" x2="140" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/>
            <line x1="190" y1="130" x2="190" y2="155" stroke="#1e3a8a" stroke-dasharray="3"/>
            <path d="M 135 110 A 55 55 0 0 1 45 110" fill="none" stroke="#ef4444" stroke-width="4" marker-end="url(#arrowhead_inv)"/>
        </svg>
        """
    return f'<div style="text-align: center; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; overflow: visible;">{svg}</div>'
