import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from sidebar import notes_sidebar, apply_filters_sidebar

# Load the CSV data
@st.cache_data
def load_csv_data():
    return pd.read_csv('cleaned_games.csv')

# Load the release and tags/genres dictionaries
@st.cache_data
def load_json_data(file):
    with open(file, 'r') as f:
        return json.load(f)

df = load_csv_data()
release_dict = load_json_data('release.json')  # Load the release dates from the JSON
tags_dict = load_json_data('tags.json')        # Load tags from your JSON file
genres_dict = load_json_data('genres.json')    # Load genres from your JSON file

# Sidebar functionality
notes_sidebar()  # Display notes
apply_filters_sidebar()  # Apply filters

# Access the filtered DataFrame from session_state
if 'filtered_df' in st.session_state:
    df = st.session_state['filtered_df']
else:
    st.write("No data available.")

# Columns to display as bar plots
y_categories = ['Average playtime forever', "Peak CCU", 'Reviews', "Review score", 'Recommendations']

# Extract 'Release Year', 'Release Month', and 'Release Quarter' for the entire dataset
df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce', format='mixed')  # Parse date
df['Release Year'] = df['Release date'].dt.year
df['Release Month'] = df['Release date'].dt.month
df['Release Quarter'] = df['Release date'].dt.quarter  # Extract the quarter as an integer

# Function to calculate dynamic y-axis range
def get_y_range(df, column):
    min_value = df[column].min()
    max_value = df[column].max()
    buffer = (max_value - min_value) * 0.2  # Adding a 20% buffer
    return [min_value - buffer, max_value + buffer]

# Dynamic y-axis for global range when comparing
def get_global_y_range(min_value, max_value):
    buffer = (max_value - min_value) * 0.2 # Adding a 20% buffer
    return [max(0, min_value - buffer), max_value + buffer]

# Display the title first
desc, filt = st.columns([2,3])
with desc:
    st.title("Success Based on Release Date")
    st.write("""
    This dashboard allows you to explore the success of games based on their release date. 
    You can filter the data based on tags, genres, and the release year range. 
    The data is grouped by months or quarters, and you can compare two different tag or genre selections.
    """)
with filt:
    with st.expander("Filter Game Data"):
        
        # Year Range Selection (above the graphs)
        years = set(release_dict.keys())
        min_year, max_year = int(min(years)), int(max(years))
        year_range = st.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

        col_1, col_2 = st.columns(2)
        col_3, col_4 = st.columns(2)

        with col_4:
            # Comparison Checkbox
            compare = st.checkbox("Compare Two Tag/Genre Selections")
        
        with col_1:
            # Tag Filter Selection
            selected_tags = st.multiselect("Select Tags to Filter By", sorted(tags_dict.keys()))
            if compare:
                selected_tags_2 = st.multiselect("Select Tags to Filter By (Comparison)", sorted(tags_dict.keys()), key='tags_2')
        with col_2:
            # Genre Filter Selection
            selected_genres = st.multiselect("Select Genres to Filter By", sorted(genres_dict.keys()))
            if compare:
                selected_genres_2 = st.multiselect("Select Genres to Filter By (Comparison)", sorted(genres_dict.keys()), key='genres_2')
        with col_3:
            # Option to show by month or quarter
            group_by = st.radio("Group by:", options=["Months", "Quarters"], horizontal=True)
        

# Filter the data based on the selected year range, tags, and genres
df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]

# Apply tag and genre filters
if selected_tags:
    selected_game_ids = set.intersection(*(set(tags_dict[tag]) for tag in selected_tags))
    df_filtered = df_filtered[df_filtered['AppID'].astype(str).isin(selected_game_ids)]

if selected_genres:
    selected_game_ids_genre = set.intersection(*(set(genres_dict[genre]) for genre in selected_genres))
    df_filtered = df_filtered[df_filtered['AppID'].astype(str).isin(selected_game_ids_genre)]

# Second filter for comparison
if compare:
    df_filtered_2 = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]

    if selected_tags_2:
        selected_game_ids_2 = set.intersection(*(set(tags_dict[tag]) for tag in selected_tags_2))
        df_filtered_2 = df_filtered_2[df_filtered_2['AppID'].astype(str).isin(selected_game_ids_2)]

    if selected_genres_2:
        selected_game_ids_genre_2 = set.intersection(*(set(genres_dict[genre]) for genre in selected_genres_2))
        df_filtered_2 = df_filtered_2[df_filtered_2['AppID'].astype(str).isin(selected_game_ids_genre_2)]

# Handle grouping by month or quarter
if group_by == "Months":
    group_column = 'Release Month'
    x_axis_label = 'Month'
    # Group by Release Month for the filtered data, averaging over the years
    aggregated_data = df_filtered.groupby('Release Month').agg({col : 'mean' for col in y_categories}).reset_index()
    aggregated_data['Games released'] = df_filtered.groupby('Release Month').size().values
    # For the overall data (line for all games, filtered by year range)
    aggregated_all_data = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])].groupby('Release Month').agg({col : 'mean' for col in y_categories}).reset_index()
    aggregated_all_data['Games released'] = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])].groupby('Release Month').size().values
    # Handle comparison data if applicable
    if compare:
        aggregated_data_2 = df_filtered_2.groupby('Release Month').agg({col : 'mean' for col in y_categories}).reset_index()
        aggregated_data_2['Games released'] = df_filtered_2.groupby('Release Month').size().values
else:
    group_column = 'Release Quarter'
    x_axis_label = 'Quarter'
    # Group by Release Quarter for the filtered data, averaging over the years
    aggregated_data = df_filtered.groupby('Release Quarter').agg({col : 'mean' for col in y_categories}).reset_index()
    aggregated_data['Games released'] = df_filtered.groupby('Release Quarter').size().values
    # For the overall data (line for all games, filtered by year range)
    aggregated_all_data = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])].groupby('Release Quarter').agg({col : 'mean' for col in y_categories}).reset_index()
    aggregated_all_data['Games released'] = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])].groupby('Release Quarter').size().values
    # Handle comparison data if applicable
    if compare:
        aggregated_data_2 = df_filtered_2.groupby('Release Quarter').agg({col : 'mean' for col in y_categories}).reset_index()
        aggregated_data_2['Games released'] = df_filtered_2.groupby('Release Quarter').size().values

# Placeholder for y-axis categories (you can replace these with actual column names)
import plotly.graph_objects as go

# Define background colors for the graphs
background_colors = ['#f9fbe7', '#e0f7fa', '#fce4ec', '#f3e5f5', '#e8f5e9', '#fff3e0']

# Create the bar plots for all y-categories
figs = []
for i, y_category in enumerate(['Games released'] + y_categories):
    # Create a new figure for each graph
    fig = go.Figure()

    # Calculate the global min and max values for each category
    global_min = min(aggregated_all_data[y_category].min(), aggregated_data[y_category].min())
    global_max = max(aggregated_all_data[y_category].max(), aggregated_data[y_category].max())

    if compare:
        # Include the comparison data in the global range
        global_min = min(global_min, aggregated_data_2[y_category].min())
        global_max = max(global_max, aggregated_data_2[y_category].max())

    # Add data for the overall dataset
    fig.add_trace(go.Bar(
        x=aggregated_all_data[group_column],
        y=aggregated_all_data[y_category],
        name=f'All {y_category}',
        marker_color='blue',
        width=0.5 if len(aggregated_all_data[group_column]) == 1 else None  # Adjust bar width if only 1 bar
    ))

    # Add filtered data (only if filters are applied)
    if not df_filtered.empty and (selected_tags or selected_genres):
        if compare:
            # Grouped bar plot
            fig.add_trace(go.Bar(
                x=aggregated_data[group_column],
                y=aggregated_data[y_category],
                name=f'{y_category} (Filtered)',
                marker_color='orange',
                width=0.5 if len(aggregated_data[group_column]) == 1 else None
            ))

            fig.add_trace(go.Bar(
                x=aggregated_data_2[group_column],
                y=aggregated_data_2[y_category],
                name=f'{y_category} (Comparison)',
                marker_color='black',
                width=0.5 if len(aggregated_data_2[group_column]) == 1 else None
            ))
        else:
            # Single bar plot for filtered data
            fig.add_trace(go.Bar(
                x=aggregated_data[group_column],
                y=aggregated_data[y_category],
                name=f'{y_category} (Filtered)',
                marker_color='orange',
                width=0.5 if len(aggregated_data[group_column]) == 1 else None
            ))

    # Set titles for the x and y axis and for the graph
    fig.update_layout(
        title=f'{y_category} Over {x_axis_label}s (Averaged Over Years)',
        xaxis_title=x_axis_label,
        yaxis_title=f'Average {y_category}',
        plot_bgcolor=background_colors[i],  # Set background color
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins to make the graph shorter
        height=250  # Set graph height (short)
    )

    # Use global min and max for y-axis range
    fig.update_yaxes(range=get_global_y_range(global_min, global_max), 
                     tickformat=".0%" if y_category == 'Review score' else None)

    # Ensure all months or quarters are shown on the x-axis
    if group_by == "Months":
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),  # Ensure all months from 1 to 12 are shown
            ticktext=[str(month) for month in range(1, 13)]
        )
    else:
        fig.update_xaxes(
            tickmode='array',
            tickvals=[1, 2, 3, 4],  # Ensure all quarters (1-4) are shown
            ticktext=['Q1', 'Q2', 'Q3', 'Q4']
        )

    # Add the figure to the list
    figs.append(fig)

# Display the figures, 2x2
for c, col in enumerate(st.columns(2)):
    with col:
        for i in range(c*3, c*3+3):
            st.plotly_chart(figs[i], use_container_width=True)