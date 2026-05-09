import streamlit as st
from utils.data_loader import load_data
from utils.ui_components import load_css, render_footer

st.set_page_config(page_title="Seat Matrix", page_icon="🪑", layout="wide")
load_css()
_, _, _, df_seats = load_data()

st.title("🪑 Seat Matrix")
st.markdown("Display total intake distribution.")

if df_seats.empty:
    st.warning("Seat matrix data is still loading or unavailable.")
else:
    with st.sidebar:
        search_query = st.text_input("Search College Name")
        
    filtered_df = df_seats.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['college_name'].str.contains(search_query, case=False, na=False)]
        
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

render_footer()

