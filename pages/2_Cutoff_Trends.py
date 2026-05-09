import streamlit as st
from utils.data_loader import load_data
from utils.data_loader import load_data
from utils.ui_components import load_css, render_footer

st.set_page_config(page_title="Cutoff Trends", page_icon="📈", layout="wide")
load_css()
df_main, _, _, _ = load_data()

st.title("📈 Cutoff Trends")
st.markdown("Compare Round 1 vs Round 3 trends.")

if df_main.empty or 'round1_cutoff' not in df_main.columns or 'round3_cutoff' not in df_main.columns:
    st.warning("Insufficient data for trend analysis.")
else:
    trend_df = df_main.dropna(subset=['round1_cutoff', 'round3_cutoff']).copy()
    trend_df['Change'] = trend_df['round3_cutoff'] - trend_df['round1_cutoff']
    
    st.dataframe(
        trend_df[['college_name', 'branch', 'category', 'round1_cutoff', 'round3_cutoff', 'Change']].sort_values('Change', ascending=False),
        use_container_width=True,
        hide_index=True
    )

render_footer()

