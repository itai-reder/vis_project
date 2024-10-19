# app.py

import streamlit as st
from data_loader import load_data

st.set_page_config(page_title="Welcome", layout="wide")

# Load data
df = load_data()

# Clear Cache
if st.button("Clear Cache"):
    st.cache_data.clear()  # Clears @st.cache_data caches
    st.cache_resource.clear()  # Clears @st.cache_resource caches (if you're using this)
    st.success("Cache cleared!")


# Welcome Page
st.title("🎮 Steam Games Data Analysis Project")
st.markdown("""
Welcome to the **Steam Games Data Analysis Project**!

This project analyzes trends and preferences of gamers based on data collected from the Steam platform.

**Dataset Source**: [Kaggle - Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data)

Navigate through the pages using the sidebar to explore different aspects of the data.
""")
