import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data_for_page

# Set the page configuration
st.set_page_config(page_title="Game Price", layout="wide", initial_sidebar_state="expanded")

df = load_data_for_page()

# Create price bins with free games in a separate bin
price_bins = [-0.01, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
bin_labels = ['Free', '(0,10]', '(10,20]', '(20,30]', '(30,40]', '(40,50]', '(50,60]', 
              '(60,70]', '(70,80]', '(80,90]', '(90,100]', '>100']

df['Price Bin'] = pd.cut(df['Price'], bins=price_bins, labels=bin_labels, include_lowest=True, right=True)

# Drop rows where Price Bin is NaN (i.e., prices outside the specified range)
df = df.dropna(subset=['Price Bin'])

# Convert the Price Bin to a categorical type with ordered categories
df['Price Bin'] = pd.Categorical(df['Price Bin'], categories=bin_labels, ordered=True)

y_categories = ['Games released', 'Average playtime', "Peak CCU", 'Reviews', "Review score", 'Recommendations']

# Function to calculate dynamic y-axis range
def get_y_range(df, column):
    min_value = df[column].min()
    max_value = df[column].max()
    buffer = (max_value - min_value) * 0.2  # Adding a 20% buffer
    return [max(0, min_value - buffer), max_value + buffer]

col1, col2 =  st.columns([3, 1])
with col1: # Description
    st.title("💰 Price vs Popularity Analysis")
    st.write("""
             This page analyzes the relationship between the price of games and their popularity based on various metrics.
             The data is grouped into price bins to compare the average values of different metrics.
             Use the sorting options to view the data in ascending or descending order based on the selected metric.
             """)
with col2: # Sorting option
    sort_by = st.radio("Sort by:", options=["Price Bin", "Ascending", "Descending"], index=0)

# Apply dimension-specific filters

columns = st.columns(2)

y_ordered = y_categories[1:] + [y_categories[0]]
for i, target_dimension in enumerate(y_ordered):
    if target_dimension == "Games released":
        agg_data = df.groupby('Price Bin').size().reset_index(name='Games released')
    else:
        target_df = df[df[target_dimension] > 0] if target_dimension in ("Average playtime", "Peak CCU") else df
        # Aggregate the data by Price Bin
        agg_data = target_df.groupby('Price Bin')[target_dimension].mean().reset_index()
        agg_data['Games released'] = target_df.groupby('Price Bin').size().values

    # Sort the data
    if sort_by != "Price Bin":
        agg_data = agg_data.sort_values(by=target_dimension, ascending=(sort_by == "Ascending"))

    # Create the bar plot
    fig = px.bar(agg_data, x='Price Bin', y=target_dimension,
                title=f'{target_dimension} by Price Bin' + (" (Averaged per bin)" if target_dimension != "Games released" else ""),
                labels={'Price Bin': 'Price Bin ($)', target_dimension: f'Average {target_dimension}'},
                color='Games released', color_continuous_scale='Viridis_r')
                # text=target_dimension)

    fig.update_yaxes(range=get_y_range(agg_data, target_dimension), 
                     tickformat='.0%' if target_dimension == 'Review score' else None)
    
    if target_dimension in ("Average playtime", "Peak CCU"):
        fig.add_annotation(
            dict(font=dict(size=18), x=0, y=1.05,
                showarrow=False, text=f"*Excluding games with 0 {target_dimension}",
                xref="paper", yref="paper", xanchor='left', yanchor='bottom')
)

    # Update layout to show labels and apply visual enhancements
    # fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
    fig.update_layout(title_font_size=24, xaxis_title_font_size=18, yaxis_title_font_size=18, uniformtext_minsize=8, uniformtext_mode='hide',
                      coloraxis_colorbar=dict(yanchor="top", y=1.05, x=1, xanchor="right", orientation="h"))
    with columns[int(i>2)]:
        st.plotly_chart(fig, use_container_width=True)
