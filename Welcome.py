# Welcome.py

import streamlit as st
from data_loader import load_data_for_page

st.set_page_config(page_title="Welcome", layout="wide")

# Default filters {column: default_value}
default_min_filter = {
    "Reviews": 20.0  # Default filter for reviews at the start
}
default_max_filter = {}
st.session_state["min_filter"] = default_min_filter
st.session_state["max_filter"] = default_max_filter

# Load the sidebar
load_data_for_page()

# Welcome Page
st.title("🎮 Steam Games Data Analysis Project")
st.markdown("""
""")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
Welcome to the **Steam Games Data Analysis Project**!

This site is part of the final project of the Information Visualization course.
The visualizations here are meant to be used as an aid for game developers to help choose what game to create as best as possible.

**Dataset Source**: [Kaggle - Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data)
            
Data for over 80000 games was collected from the Steam Games official website.

Navigate through the pages using the sidebar to explore different aspects of the data.

---------------------------------------
### Navigating the site

On the left you will find 5 tabs, each for a different visualization. press whichever you want to see, explenation for each tab is shown on the tab page.
Below the tabs is a filter option, since there are many games on steam and quite a lot of them have little to no playerbase we added a filter to reduce the amount of games shown, the default filter is set to minimum of 20 reviews but you can choose to filter it as you wish. Please note tht the filter is in effect for all tabs.

---------------------------------------

### Graphs on the site

Each of the graphs youll find here support zoom in, click an area on the graph and drag to choose an area that will be zoomed in, double click anywhere on the graph to zoom back out.
On graphs with several colors used you can click on the color in the legend in order to remove/add that color to the graph.

""")
with col2:
    st.image("steam.jpg", use_column_width=True)
    st.markdown("""
### Measuring Success and Popularity
            
Throughout the visualizations, we measure the success and popularity of games using the following metrics:

- **Average Playtime**: The average player's total time spent playing the game.
- **Peak Concurrent Players**: The highest number of players playing the game at the same time.
- **Reviews**: The number of reviews given by players.
- **Recommendations**: The number of recommendations given by players.
- **Review Score**: The average score given by players.
- **Games Released**: Additional measure not related to success or popularity, this is the number of games released in each category group.

    """)
st.markdown("""
---------------------------------------

Created by:
Michael Mor Yosef | Itai Sharon Reder""")
