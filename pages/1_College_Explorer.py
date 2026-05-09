import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.ui_components import load_css

st.set_page_config(page_title="College Explorer", page_icon="🏢", layout="wide")
load_css()

df_main, _, _, _ = load_data()

st.title("🏢 College Explorer")
st.markdown("Browse all colleges, compare branches, and view overall data.")

if df_main.empty:
    st.warning("Data is still loading or unavailable.")
else:
    # Sidebar Filters
    with st.sidebar:
        st.header("Filters")
        
        cities = ["All"] + sorted(df_main['city'].dropna().unique().tolist())
        city = st.selectbox("City", cities)
        
        college_types = ["All", "Government", "Autonomous", "Private"]
        college_type = st.selectbox("Type", college_types)
        
        search_query = st.text_input("Search College Name")
        
    # Apply filters
    filtered_df = df_main.copy()
    
    if city != "All":
        filtered_df = filtered_df[filtered_df['city'] == city]
    if college_type != "All":
        filtered_df = filtered_df[filtered_df['college_type'] == college_type]
    if search_query:
        filtered_df = filtered_df[filtered_df['college_name'].str.contains(search_query, case=False, na=False)]
        
    st.metric("Total Colleges Found", filtered_df['college_name'].nunique())
    
    # Display Data
    display_cols = ['college_name', 'branch', 'city', 'college_type']
    if 'round1_cutoff' in filtered_df.columns: display_cols.append('round1_cutoff')
    if 'round3_cutoff' in filtered_df.columns: display_cols.append('round3_cutoff')
    
    st.dataframe(
        filtered_df[display_cols].sort_values('college_name'),
        use_container_width=True,
        hide_index=True
    )
