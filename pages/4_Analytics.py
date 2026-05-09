import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.ui_components import load_css

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
load_css()

df_main, _, _, _ = load_data()

st.title("📊 Dashboard Analytics")
st.markdown("Visual insights into KEA Engineering College Admissions.")

if df_main.empty:
    st.warning("Data is still loading or unavailable.")
else:
    # Top colleges by cutoff
    st.subheader("Top 10 Most Competitive Colleges (Computer Science, GM)")
    
    # Filter for CSE and GM
    cs_df = df_main[
        (df_main['branch'].str.contains("COMPUTER SCIENCE", case=False, na=False)) & 
        (df_main['category'] == 'GM')
    ]
    
    if not cs_df.empty and 'round1_cutoff' in cs_df.columns:
        top_10_cs = cs_df.sort_values('round1_cutoff').head(10)
        
        # Abbreviate college names for better chart display
        top_10_cs['short_name'] = top_10_cs['college_name'].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
        
        fig1 = px.bar(
            top_10_cs, 
            x='short_name', 
            y='round1_cutoff',
            color='round1_cutoff',
            color_continuous_scale='Viridis',
            labels={'short_name': 'College', 'round1_cutoff': 'Round 1 Cutoff Rank'},
            hover_data=['college_name', 'city']
        )
        fig1.update_layout(xaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Not enough data to display Top 10 Competitive Colleges chart.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Branch Distribution")
        # We'll use the unique branches offered across all colleges
        branch_counts = df_main['branch'].value_counts().head(10).reset_index()
        branch_counts.columns = ['branch', 'count']
        
        fig2 = px.pie(
            branch_counts, 
            values='count', 
            names='branch',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig2, use_container_width=True)
        
    with col2:
        st.subheader("City-wise College Distribution")
        city_counts = df_main['city'].value_counts().head(10).reset_index()
        city_counts.columns = ['city', 'count']
        
        fig3 = px.bar(
            city_counts,
            x='city',
            y='count',
            color='count',
            color_continuous_scale='Blues'
        )
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig3, use_container_width=True)

    # Line Chart: Round 1 vs Round 3 trends
    st.subheader("Round 1 vs Round 3 Trend Analysis")
    if 'round1_cutoff' in df_main.columns and 'round3_cutoff' in df_main.columns:
        trend_df = df_main.dropna(subset=['round1_cutoff', 'round3_cutoff']).head(50)
        trend_df = trend_df.sort_values('round1_cutoff')
        trend_df['short_name'] = trend_df['college_name'].apply(lambda x: x[:20]) + " (" + trend_df['branch'].apply(lambda x: x[:10]) + ")"
        
        fig4 = px.line(
            trend_df,
            x='short_name',
            y=['round1_cutoff', 'round3_cutoff'],
            labels={'value': 'Cutoff Rank', 'short_name': 'College & Branch', 'variable': 'Round'},
            markers=True
        )
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Round 3 data is required for trend analysis.")
