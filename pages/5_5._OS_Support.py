import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from data_loader import load_data_for_page

st.set_page_config(page_title="OS Support", layout="wide", initial_sidebar_state="expanded")

df = load_data_for_page()

# Access the filtered DataFrame from session_state
if 'filtered_df' in st.session_state:
    df = st.session_state['filtered_df']
else:
    st.write("No data available.")

# Custom color palette for OS and combinations
colors = {
    'Windows': "#E69F00",
    'Mac': "#56B4E9",        
    'Linux': "#009E73",       
    'W': "#E69F00",         
    'M': "#56B4E9",         
    'L': "#009E73",         
    'W+M': "#F0E442",        
    'W+L': "#0072B2",        
    'M+L': "#D55E00",        
    'W+M+L': "#CC79A7",      
    "1": "#bee9e8",  # Light Blue for 1 OS
    "2": "#62b6cb",  # Medium Blue for 2 OS
    "3": "#1b4965"   # Dark Blue for 3 OS
}

# Set the custom order for the OS and OS Combinations
os_order = ['Windows', 'Mac', 'Linux']
os_combination_order = ['W', 'M', 'L', 'W+M', 'W+L', 'M+L', 'W+M+L']

# Add OS combination column (shortened names)
df['OS_combination'] = df.apply(lambda row: '+'.join([os[0] for os in ['Windows', 'Mac', 'Linux'] if row[os]]), axis=1)
df['OS_count'] = df.apply(lambda row: len([os for os in ['Windows', 'Mac', 'Linux'] if row[os]]), axis=1).astype(str)

# Create new DataFrame where each game is repeated for every OS it supports (name it "OS_repeated")
os_repeated = pd.DataFrame()

for os in ['Windows', 'Mac', 'Linux']:
    os_df = df[df[os]].copy()  # Filter for each OS
    os_df['OS'] = os  # Add a column to indicate the OS (Windows, Mac, Linux)
    os_repeated = pd.concat([os_repeated, os_df], ignore_index=True)

# Ensure the OS and OS_combination columns follow the specified order
os_repeated['OS'] = pd.Categorical(os_repeated['OS'], categories=os_order, ordered=True)
df['OS_combination'] = pd.Categorical(df['OS_combination'], categories=os_combination_order, ordered=True)

# Function to calculate dynamic y-axis range
def get_y_range(df, column):
    min_value = df[column].min()
    max_value = df[column].max()
    buffer = (max_value - min_value) * 0.2
    return [max(0, min_value - buffer), max_value + buffer]

# Function to apply 5% threshold in pie chart
def apply_pie_threshold(df, value_column, name_column):
    total = df[value_column].sum()
    df = df.groupby(name_column).sum().reset_index()
    return df

# General title and description at the top
st.title("Operating System Support Analysis")
st.write("""
    This dashboard explores how supporting different operating systems impacts the success of video games.
    The visualizations include combinations of Windows, Mac, and Linux support, as well as individual operating systems.
    You can examine metrics such as reviews, recommendations, and review scores.
""")

# Define success metrics (features)
success_metrics = ['Average playtime', 'Peak CCU', 'Reviews', 'Recommendations', 'Review score']

# Data visualizations
data_types = {
    "OS Combinations": 'OS_combination',
    "OS Count": 'OS_count',
    "Individual OS": 'OS'
}

# Custom descriptions for each data type
subheaders = {
    "Individual OS": "This section shows looks at each operating system individually. You can see how many games support each OS, and the average success metrics for each OS.",
    "OS Count": "This section shows the number of operating systems each game supports. You can see how many games support 1, 2, or 3 operating systems, and the average success metrics for each OS count.",
    "OS Combinations": "This section shows combinations of operating systems. You can see how many games support each combination, and the average success metrics for each combination."
}
descriptions = {
    "Individual OS": "Each individual operating system (Windows, Mac, Linux) is displayed separately, regardless of whether the game supports multiple systems, meaning one game can affect multiple OS.",
    "OS Count": "The number of operating systems each game supports is shown (1, 2, or 3). This aggregates games that support multiple operating systems.",
    "OS Combinations": "Combinations of operating systems are represented by their first letters (W for Windows, M for Mac, L for Linux). For example, 'W+M+L' means the game supports all three systems."
}

# Move "Individual OS" to the top
data_types = dict(reversed(list(data_types.items())))

for data_type, column in data_types.items():
    with st.expander(f"{data_type} Visualizations"):

        st.subheader(f"{data_type} Analysis")
        st.write(subheaders[data_type])
        st.write(descriptions[data_type])

        plots = st.columns(3) + st.columns(3)

        with plots.pop(1):
            # Pie chart for OS Combinations (unordered)
            data_source = df if column != 'OS' else os_repeated
            game_count = data_source.groupby(column).size().reset_index(name='count')
            game_count = apply_pie_threshold(game_count, 'count', column)

            if data_type == 'Individual OS':  # Bar plot instead of pie
                fig_pie = px.bar(game_count, y=column, x='count', title=f"Games Released for {data_type}",
                                color=column, color_discrete_map=colors)
                fig_pie.update_traces(showlegend=False)
            else:
                if data_type == 'OS Count': # ordered
                    fig_pie = px.pie(game_count, values='count', names=column, title=f"Games Released for {data_type}",
                                    color=column, color_discrete_map=colors, category_orders={"OS_count": ["1", "2", "3"]})
                else: # unordered
                    fig_pie = px.pie(game_count, values='count', names=column, title=f"Games Released for {data_type}",
                                    color=column, color_discrete_map=colors)
                # Custom label format to include combination and percentage
                fig_pie.update_traces(
                    texttemplate="%{label}: %{percent}",  # Shows combination and percentage
                    textposition="auto",  # Automatically moves text outside if the slice is too small
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
                )

                # Move legend to the bottom
                fig_pie.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="right", x=1))

            st.plotly_chart(fig_pie, use_container_width=True)



            for i, metric in enumerate(success_metrics):
                data_grouped = data_source.groupby(column)[metric].mean().reset_index()
                data_grouped['count'] = data_source.groupby(column).size().values  # Add count column for bar plot

                # Scale the 'count' column for size between 5 and 30
                size_scaled = np.interp(data_grouped['count'], (data_grouped['count'].min(), data_grouped['count'].max()), [5, 30])
                
                with plots[i]:  # Dot plots where x-group, y-metric, size-count, color-group

                    # Create the scatter plot
                    fig = px.scatter(data_grouped, y=metric, x=column, size=size_scaled, color=column, text=column,
                                    title=f"{metric} by {data_type}",
                                    color_discrete_map=colors, size_max=30, custom_data=['count'],
                                    category_orders={
                                        "OS": os_order,
                                        "OS_combination": os_combination_order
                                    })

                    # Handle OS Count: Set only 1, 2, 3 as x-axis ticks
                    if data_type == 'OS Count':
                        fig.update_xaxes(tickmode='array', tickvals=[1, 2, 3], ticktext=['1', '2', '3'])

                    # Pass the 'count' value as custom data
                    fig.update_traces(
                        hovertemplate=f"<b>%{{text}}</b><br>{metric}: %{{y}}<br>Count: %{{customdata}}<extra></extra>"
                    )

                    fig.update_traces(textposition='top center')
                    fig.update_layout(showlegend=False)

                    st.plotly_chart(fig, use_container_width=True)
