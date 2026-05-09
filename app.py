import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.predictor import predict_colleges
from utils.ui_components import load_css, create_insight_card, render_chance_badge
import plotly.express as px

# Setup Page
st.set_page_config(
    page_title="KEA College Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css()

# Load Data
df_main, df_r1, df_r3, df_seats = load_data()

# App Header
st.title("🎓 KEA Engineering College Predictor")
st.markdown("<p style='color: var(--text-secondary); margin-top: -15px; margin-bottom: 30px;'>Predict your chances based on actual KEA Cutoffs and Seat Matrix</p>", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    st.header("🎯 Prediction Filters")
    
    # Input Rank
    rank = st.number_input("Your CET Rank", min_value=1, max_value=200000, value=15000, step=100)
    
    # Category
    categories = ['GM', '1G', '2AG', '2BG', '3AG', '3BG', 'SCG', 'STG']
    category = st.selectbox("Category", categories, index=0)
    
    # City Filter
    cities = ["All"]
    if not df_main.empty and 'city' in df_main.columns:
        cities += sorted([c for c in df_main['city'].unique() if pd.notna(c) and c != "Unknown"])
    selected_cities = st.multiselect("Preferred Cities", cities, default=["All"])
    
    # Branch Filter
    branches = ["All"]
    if not df_main.empty and 'branch' in df_main.columns:
        branches += sorted([b for b in df_main['branch'].unique() if pd.notna(b)])
    selected_branches = st.multiselect("Preferred Branches", branches, default=["All"])
    
    # College Type Filter
    college_types = ["All", "Government", "Autonomous", "Private"]
    college_type = st.selectbox("College Type", college_types)
    
    # Round Filter
    round_filter = st.radio("Consider Cutoffs From", ["First Round", "Third Round", "Both"])

# Main Predictor Logic
if df_main.empty:
    st.warning("⚠️ Data is currently being loaded or extracted from PDFs. Please check back in a few moments.")
else:
    # Run Prediction
    results = predict_colleges(
        df_main, rank, 
        category=category, cities=selected_cities, branches=selected_branches, 
        college_type=college_type, round_filter=round_filter
    )
    
    # Global metrics
    total_options = len(results)
    safe_count = len(results[results['chance'] == 'Safe']) if total_options > 0 else 0
    mod_count = len(results[results['chance'] == 'Moderate']) if total_options > 0 else 0
    dream_count = len(results[results['chance'] == 'Dream']) if total_options > 0 else 0
    
    st.markdown("### Top Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Possible Options", total_options)
    m2.metric("🟢 Safe", safe_count)
    m3.metric("🟡 Moderate", mod_count)
    m4.metric("🔴 Dream", dream_count)
    st.markdown("---")
    
    if results.empty:
        st.info("No colleges found matching your criteria in the dynamic rank range.")
    else:
        # Top Recommendations Table
        st.subheader("📋 Predicted Colleges")
        
        # Prepare display dataframe
        display_cols = ['college_name', 'branch', 'city']
        if 'round1_cutoff' in results.columns: display_cols.append('round1_cutoff')
        if 'round3_cutoff' in results.columns: display_cols.append('round3_cutoff')
        if 'intake' in results.columns: display_cols.append('intake')
        display_cols.append('Difference')
        display_cols.append('Chance %')
        display_cols.append('chance')
        
        display_df = results[display_cols].copy()
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "college_name": st.column_config.TextColumn("College Name", width="large"),
                "branch": st.column_config.TextColumn("Branch", width="medium"),
                "city": st.column_config.TextColumn("City"),
                "round1_cutoff": st.column_config.NumberColumn("R1 Cutoff"),
                "round3_cutoff": st.column_config.NumberColumn("R3 Cutoff"),
                "Difference": st.column_config.NumberColumn("Difference"),
                "Chance %": st.column_config.ProgressColumn(
                    "Chance %",
                    help="Estimated probability of admission",
                    format="%f%%",
                    min_value=0,
                    max_value=100,
                ),
                "chance": st.column_config.TextColumn("Classification", width="small")
            }
        )
        
        # Smart Insights Section
        st.subheader("💡 Smart Insights")
        
        insights = []
        if mod_count > safe_count:
            insights.append(f"Most of your options are **Moderate**. You have a fighting chance, but ensure you have backup options.")
        
        if 'trend' in results.columns and len(results) > 0:
            avg_trend = results['trend'].mean()
            if avg_trend > 0:
                insights.append(f"Round 3 cutoffs generally relaxed by an average of **{int(avg_trend)} ranks** for these options.")
            elif avg_trend < 0:
                insights.append(f"Cutoffs tightened between rounds. Round 3 is more competitive for these branches.")
                
        # Popular branch
        if 'branch' in results.columns and len(results) > 0:
            top_branch = results['branch'].value_counts().idxmax()
            insights.append(f"**{top_branch}** is the most common branch in your predicted range.")
            
        for insight in insights:
            st.markdown(f"- {insight}")

