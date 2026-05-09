import streamlit as st
import base64
import os

def load_css():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = os.path.join(base_dir, 'styles', 'main.css')
    
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
def render_chance_badge(chance):
    if chance == "Safe":
        return "🟢 Safe"
    elif chance == "Moderate":
        return "🟡 Moderate"
    elif chance == "Dream":
        return "🔴 Dream"
    return "⚪ Unknown"

def create_insight_card(title, value, subtitle=None):
    st.markdown(f"""
        <div class="insight-card">
            <h4 style='margin-bottom: 5px; color: var(--text-color);'>{title}</h4>
            <h2 style='margin-top: 0; margin-bottom: 5px; color: var(--primary-color);'>{value}</h2>
            {f"<p style='margin:0; font-size: 0.9em; color: var(--text-secondary);'>{subtitle}</p>" if subtitle else ""}
        </div>
    """, unsafe_allow_html=True)
