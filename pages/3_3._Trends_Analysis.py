import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_loader import load_data_for_page, load_json_data

st.set_page_config(page_title="Trends Analysis", layout="wide", initial_sidebar_state="expanded")

# Define fields, including the new "Games Released" feature
fields = ['Recommendations', "Peak CCU", 'Average playtime','Reviews', 'Games Released', 'Review score']

colors = ['#D81B60', '#1E88E5', '#FFC107']  # Predefined colors for the lines
dividers = ['red', 'blue', 'orange']

# Title and Description at the top of the app
st.title("Game Success Trends Based on Features and Time")

st.markdown("""
This dashboard helps explore trends in game success metrics based on various features like genres, tags, and categories. 
You can visualize how these features impact success metrics like recommendations, playtime, user scores, and more over different time periods (year or month). 
""")

df = load_data_for_page()

release_dict = load_json_data('release.json')
genres_dict = load_json_data('genres.json')
tags_dict = load_json_data('tags.json')
categories_dict = load_json_data('categories.json')
filters_dict = {
    "Genres" : genres_dict,
    "Tags" : tags_dict,
    "Categories" : categories_dict,
}

# Define all time periods as (year, month) tuples
years = set(release_dict.keys())
min_year, max_year = int(min(years)), int(max(years))
time_periods = [(year, month) for year in range(min_year, max_year + 1) for month in range(1, 13)]
all_ids = set(df['AppID'].astype(str))

n_combinations = 3

plot_placeholder = st.container()
with plot_placeholder:
    plot_columns = st.columns([5, 2])  # Adjust widths for the plot and the time granularity

    # Time granularity selection on the right
    with plot_columns[1]:
        time_granularity = st.radio("Select Time Period", ["Year", "Month"])
        selected_feature = st.radio("Select Feature to Plot", sorted(fields))
    # Feature selection on the left

# Initialize plot data structures for selected combinations
plot_data_list = []
game_ids_list = []

for _ in range(n_combinations + 1):
    plot_data = {
        'year': [tp[0] for tp in time_periods],
        'month': [tp[1] for tp in time_periods],
        "Reviews": [0] * len(time_periods),
        "Positive": [0] * len(time_periods),
        "Review score": [0] * len(time_periods),
        'Games Released': [0] * len(time_periods),
    }
    plot_data_list.append(plot_data)
    game_ids_list.append(set())

# Function to plot selected filters
def plot_selected_filters():
    for i, comb in enumerate(selected_filters_dict.values()):
        if any(comb.values()) or i == n_combinations:
            label = "<br>".join([k[0] + ": " + ", ".join(v) for k, v in comb.items() if v])
            df_plot = pd.DataFrame(plot_data_list[i])

            if time_granularity == "Month":
                df_plot['date'] = pd.to_datetime(df_plot[['year', 'month']].assign(DAY=1))
                x_axis = df_plot['date']
            else:
                df_plot_grouped = df_plot.groupby('year').sum().reset_index()
                # df_plot_grouped['Average Review Score'] = 100 * df_plot_grouped['Positive'] / df_plot_grouped['Reviews']
                x_axis = df_plot_grouped['year']

            # Add primary axis trace with distinct predefined color
            fig.add_trace(go.Scatter(x=x_axis, 
                                     y=df_plot_grouped[selected_feature] if time_granularity == "Year" else df_plot[selected_feature], 
                                     mode='lines', 
                                     name=f'{label}', 
                                     showlegend=True,
                                     line=dict(color=colors[i])))

# Function to aggregate selected filters
def aggregate_selected_filters(current_ids, i):
    game_ids_list[i] = current_ids
    aggregated_values = {field: [0] * len(time_periods) for field in fields}
    for j, (year, month) in enumerate(time_periods):
        year_str = str(year)
        month_str = str(month)
        if year_str in release_dict and month_str in release_dict[year_str]:
            common_ids = current_ids.intersection(set(release_dict[year_str][month_str]))
            if common_ids:
                filtered_df = df[df['AppID'].astype(str).isin(common_ids)]
                aggregated_values['Games Released'][j] = len(common_ids)
                for field in fields[:-2]:
                    aggregated_values[field][j] += filtered_df[field].sum()
                # if aggregated_values['Reviews'][j] > 0:
                #     aggregated_values['Average Review Score'][j] = 100 * aggregated_values['Positive'][j] / aggregated_values['Reviews'][j]
                aggregated_values['Review score'][j] = filtered_df['Review score'].mean()

    aggregated_values['year'] = [tp[0] for tp in time_periods]
    aggregated_values['month'] = [tp[1] for tp in time_periods]

    plot_data_list[i] = aggregated_values

# Explain about the combinations
st.markdown("""
            ### Game Genre, Tags & Category Combinations
            You can select multiple genres, tags, and categories to analyze their combined impact on the success metrics.
            The selected filters are combined using the AND operation to filter the games.
            The data is visualized for each combination separately, and the combinations can be compared in the plot above.
            """)

# Process All Games
aggregate_selected_filters(all_ids, n_combinations)

# ---- Position the combinations on the same level ----
comb_cols = st.columns(n_combinations)

# Layout the filters (stacked) in each combination
selected_filters_dict = {}
for i, col in enumerate(comb_cols):
    with col:
        st.subheader(f"Combination {i+1}", divider=dividers[i])

        # Multiselects stacked in each combination
        selected_filters_dict[i] = {
            "Genres": st.multiselect(f"Genres", options=sorted(genres_dict.keys()), key=f"G{i}"),
            "Tags": st.multiselect(f"Tags", options=sorted(tags_dict.keys()), key=f"T{i}"),
            "Categories": st.multiselect(f"Categories", options=sorted(categories_dict.keys()), key=f"C{i}")
        }

    # combinations = [{filt: selected_filters_dict[filt][i] for filt in filters_dict} for i in range(n_combinations)]

# Process each combination
for i in range(n_combinations):
    current_ids = all_ids
    if any(filter_val for filter_val in selected_filters_dict[i].values()):
        for filt, selected_filter in selected_filters_dict[i].items():
            if selected_filter:
                for ids in selected_filter:
                    current_ids = current_ids.intersection(set(filters_dict[filt][ids]))
                aggregate_selected_filters(current_ids, i)
    else:
        # Reset if no selection
        game_ids_list[i].clear()
        for field in fields:
            plot_data_list[i][field] = [0] * len(time_periods)
        plot_data_list[i]['Games Released'] = [0] * len(time_periods)

# ---- Dual Axis Plot for Each Combination (displayed even if no selection) ----
for i in range(n_combinations):
    with comb_cols[i]:
        # st.subheader(f"Combination {i+1}: {', '.join([f'{filt}: {', '.join(selected_filters_dict[i][filt])}' for filt in filters_dict if selected_filters_dict[i][filt]])}")

        fig_comb = make_subplots(specs=[[{"secondary_y": True}]])
        df_plot = pd.DataFrame(plot_data_list[i])

        if time_granularity == "Month":
            df_plot['date'] = pd.to_datetime(df_plot[['year', 'month']].assign(DAY=1))
            x_axis = df_plot['date']
        else:
            df_plot_grouped = df_plot.groupby('year').sum().reset_index()
            # df_plot_grouped['Average Review Score'] = 100 * df_plot_grouped['Positive'] / df_plot_grouped['Reviews']
            x_axis = df_plot_grouped['year']

        # Left axis: Line plot for the selected feature
        fig_comb.add_trace(go.Scatter(x=x_axis,
                                    y=df_plot_grouped[selected_feature] if time_granularity == "Year" else df_plot[selected_feature],
                                    mode='lines',
                                    name=f'{selected_feature}',
                                    line=dict(color="black")),
                        secondary_y=False)

        # Right axis: Bar plot for Games Released with lower opacity
        fig_comb.add_trace(go.Bar(x=x_axis,
                                y=df_plot_grouped['Games Released'] if time_granularity == "Year" else df_plot['Games Released'],
                                name="Games Released",
                                marker=dict(color=dividers[i], opacity=0.5)),
                        secondary_y=True)

        # Update layout for the dual axis plot
        fig_comb.update_layout(
            title=f"Comb. {i+1} - Avg. playtime & Games released",
            xaxis_title="Date" if time_granularity == "Month" else "Year",
            # legend above the plot
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
    )
        )

        fig_comb.update_yaxes(title_text=selected_feature, secondary_y=False)
        fig_comb.update_yaxes(title_text="Games Released", secondary_y=True)

        # Display the combination plot
        st.plotly_chart(fig_comb, use_container_width=True)


# Use the placeholder to display the plot
# with plot_placeholder:
# Layout for the feature selection and the plot on the same level
with plot_placeholder:

    with plot_columns[0]:
            
        fig = go.Figure()
        label = "All Games"
        df_plot = pd.DataFrame(plot_data_list[n_combinations])

        if time_granularity == "Month":
            df_plot['date'] = pd.to_datetime(df_plot[['year', 'month']].assign(DAY=1))
            x_axis = df_plot['date']
        else:
            df_plot_grouped = df_plot.groupby('year').sum().reset_index()
            # df_plot_grouped['Average Review Score'] = 100 * df_plot_grouped['Positive'] / df_plot_grouped['Reviews']
            x_axis = df_plot_grouped['year']

        fig.add_trace(go.Scatter(x=x_axis,
                                y=df_plot_grouped[selected_feature] if time_granularity == "Year" else df_plot[selected_feature],
                                mode='lines',
                                name=label,
                                showlegend=True,
                                line=dict(color="black")))

        plot_selected_filters()


        fig.update_layout(
            yaxis=dict(title=selected_feature),
            xaxis_title="Date (Month)" if time_granularity == "Month" else "Year",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)