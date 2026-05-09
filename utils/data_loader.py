import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    master_path = os.path.join(base_dir, 'data', 'master_dataset.csv')
    
    if os.path.exists(master_path):
        df = pd.read_csv(master_path)
    else:
        df = pd.DataFrame(columns=[
            "college_name", "branch", "category", "round1_cutoff", 
            "round3_cutoff", "city", "college_type", "intake"
        ])
        
    # Return df along with empty dummy dataframes for compatibility if needed
    return df, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
