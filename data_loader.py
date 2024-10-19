# data_loader.py

import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_games.csv", index_col=0)
    
    # Handle different date formats
    df['Release date'] = pd.to_datetime(
        df['Release date'], 
        errors='coerce', 
        format='%b %d, %Y'
    )
    df['Release date'] = df['Release date'].fillna(
        pd.to_datetime(df['Release date'], format='%m/%d/%Y', errors='coerce')
    )
    
    # Extract year and month
    df['Release Year'] = df['Release date'].dt.year
    df['Release Month'] = df['Release date'].dt.month
    
    return df
