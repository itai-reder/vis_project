import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from sidebar import notes_sidebar, apply_filters_sidebar

st.set_page_config(page_title="4. Language Support")

# Load the cleaned games data
@st.cache_data
def load_json_data(file):
    with open(file, 'r') as f:
        return json.load(f)

@st.cache_data
def load_csv_data(file):
    return pd.read_csv(file)

# Function to calculate dynamic y-axis range
def get_y_range(df, column):
    min_value = df[column].min()
    max_value = df[column].max()
    buffer = (max_value - min_value) * 0.2
    return [min_value - buffer, max_value + buffer]

# Load data
games_json = load_json_data('cleaned_games.json')
supported_languages = load_json_data('supported_languages.json')
df = apply_filters_sidebar()  # Filtered data

# Flatten the supported_languages.json structure to create a DataFrame
languages_expanded = []
for language, ids in supported_languages.items():
    for game_id in ids:
        languages_expanded.append({'AppID': game_id, 'language': language})

# Create a DataFrame from the flattened supported_languages data
languages_df = pd.DataFrame(languages_expanded)

# Convert AppID to string to match both datasets
df['AppID'] = df['AppID'].astype(str)
languages_df['AppID'] = languages_df['AppID'].astype(str)

# Merge the CSV data with the languages DataFrame on AppID
merged_df = pd.merge(languages_df, df, on='AppID')

# Define success metrics to visualize
success_metrics = ['Games released', 'Average playtime forever', 'Peak CCU', 'Reviews', 'Recommendations', 'Review score']

# General Title and Description
st.title("Language Support Dashboard")
st.write("""
    This dashboard provides an analysis of how language support impacts the success of games. 
    You can explore different views based on language combinations and success metrics.
""")

# ---- Individual Language Expander ----
with st.expander("Individual Language Analysis"):

    # Bar plot, description, and filtering layout
    container = st.container()
    col_desc, col_bar = container.columns([1, 3])

    with col_desc:
        st.subheader("Individual Language Analysis")
        st.write("""
            This section provides an analysis of individual language support.
            You can compare languages and how they affect key metrics.\n
            The bar chart on the right shows the 10 most common languages, as well as the rest of the languages combined as 'Other'.        
        """)

    # Bar chart for games released per language (top n_languages + 'Other')
    language_count = merged_df['language'].value_counts().reset_index()
    language_count.columns = ['language', 'Games Released']

    # Get the top n_languages languages and combine the rest as 'Other'
    n_languages = 10  # Default value
    top_languages = language_count.head(n_languages)
    other_count = language_count['Games Released'][n_languages:].sum()

    if other_count > 0:
        other_row = pd.DataFrame([['Other', other_count]], columns=['language', 'Games Released'])
        language_count = pd.concat([top_languages, other_row])

    # Plotting the bar chart with inverted axes (horizontal bar plot)
    fig_bar_languages = px.bar(language_count, y='language', x='Games Released', title='Games Released per Language (Top + Other)',)
                            #    color='Games Released', color_continuous_scale='viridis_r', orientation='h')
    fig_bar_languages.update_layout(xaxis_title="Number of Games", yaxis_title="Languages")
    fig_bar_languages.update_traces(showlegend=False)

    with col_bar:
        st.plotly_chart(fig_bar_languages, use_container_width=True)

    # ---- Heatmap and Display Options ----
    container = st.container()
    col_display, col_heatmap = container.columns([1, 3])  # Adjusted proportions for heatmap and filters

    with col_display:
        st.subheader("Language Heatmap")

        st.write("""
            This heatmap displays the average success metrics for different languages.\n
            The languages with the highest values for each metric are displayed by default, sorted alphabetically.\n
            You can also select up to 3 languages or combinations of languages to compare, these will appear at the top of the heatmap.
        """)

        # add a bolded text for the display options
        st.markdown("#### **Display Options:**")

        # Minimum number of games for a language to be included
        min_games = st.number_input("Minimum Games per Language to Display", min_value=1, value=10)
        st.write("Languages with fewer games will be excluded from the heatmap, except for the ones you select.")

        # Title for custom language combinations
        st.write("Select up to 3 language combinations to display:")
        err = []
        # Multiselects for custom language combinations (fixed 3 fields)
        custom_languages_1 = st.multiselect(
            "Language Combination 1", options=sorted(languages_df['language'].unique()), key="custom_combo_1"
        )
        err.append(st.empty())
        custom_languages_2 = st.multiselect(
            "Language Combination 2", options=sorted(languages_df['language'].unique()), key="custom_combo_2"
        )
        err.append(st.empty())
        custom_languages_3 = st.multiselect(
            "Language Combination 3", options=sorted(languages_df['language'].unique()), key="custom_combo_3"
        )

    # Initialize heatmap_rows (set of languages to display)
    heatmap_rows = set()

    # 1. Process custom combinations and calculate the metrics of games supporting all selected languages
    custom_combinations = [custom_languages_1, custom_languages_2, custom_languages_3]
    custom_metrics_list = []

    for i, custom_langs in enumerate(custom_combinations):
        if custom_langs:
            n_custom = len(custom_langs)
            custom_df = merged_df[merged_df['language'].isin(custom_langs)]
            combination_df = custom_df.groupby('AppID').filter(lambda x: x['language'].nunique() == n_custom)
            combination_df['language'] = ', '.join(custom_langs)
            if len(combination_df) == 0:
                err[i].write("*No games support all selected languages.")
            custom_metrics = combination_df.groupby('language')[success_metrics[1:]].mean().reset_index()
            custom_metrics['Games released'] = len(combination_df) / n_custom
            heatmap_rows.update(custom_metrics['language'].values)
            custom_metrics_list.append(custom_metrics)

    # 2. Include default high-value languages
    grouped_languages = merged_df.groupby('language')[success_metrics[1:]].mean().reset_index()
    grouped_languages['Games released'] = merged_df['language'].groupby(merged_df['language']).count().values
    filtered_languages = grouped_languages[grouped_languages['Games released'] >= min_games]

    for metric in success_metrics:
        top5_languages = filtered_languages.nlargest(5, metric)
        heatmap_rows.update(top5_languages['language'].values)

    # Filter the languages to include in the heatmap
    heatmap_df = filtered_languages[filtered_languages['language'].isin(heatmap_rows)]

    # Add the custom combinations to the top of the heatmap DataFrame
    if custom_metrics_list:
        custom_metrics_df = pd.concat(custom_metrics_list, ignore_index=True)
        heatmap_df = pd.concat([custom_metrics_df, heatmap_df], ignore_index=True)

    # Normalize the values in each column for independent color scales
    heatmap_normalized = heatmap_df.copy()
    metrics_norm = [metric + "_norm" for metric in success_metrics]
    for i, metric in enumerate(success_metrics):
        min_val = heatmap_normalized[metric].min()
        max_val = heatmap_normalized[metric].max()
        heatmap_normalized[metrics_norm[i]] = (heatmap_normalized[metric] - min_val) / (max_val - min_val)

    # Create hover text with the original values
    hover_text = pd.DataFrame(index=heatmap_df.index)
    for metric in success_metrics:
        if metric in ['Games released', 'Average playtime forever']:
            hover_text[metric] = heatmap_df['language'] + f"<br>{metric}: " + heatmap_df[metric].astype(str)
        else:
            hover_text[metric] = heatmap_df['language'] + f"<br>Avg. {metric}: " + heatmap_df[metric].astype(str)

    # Adjust the height based on the number of languages (40px per language)
    heatmap_height = 40 * len(heatmap_df)

    # Create a heatmap of the selected languages and metrics
    if not heatmap_normalized.empty:
        fig_heatmap = px.imshow(
            heatmap_normalized.set_index('language')[metrics_norm],
            labels=dict(x="Metrics", y="Languages", color="Value"),
            x=success_metrics,  # Metrics on the X-axis
            aspect="auto",
            color_continuous_scale='viridis_r'  # Reversed Viridis color scale
        )
        fig_heatmap.update_layout(
            title="Heatmap of Success Metrics by Language",
            title_y=1,
            xaxis_title="Metrics",    # X-axis for metrics
            yaxis_title="Languages",  # Y-axis for languages
            xaxis_side='top',
            height=heatmap_height,    # Dynamic height based on number of languages
            xaxis_tickangle=45,       # Increase angle of X-axis labels for better readability
            xaxis_ticklen=10          # Add some space between the X-axis labels
        )
        fig_heatmap.update_traces(  # change the hovering information to include custom metric labels
            text=hover_text[success_metrics].values,
            hovertemplate="%{text}<extra></extra>"
        )
        # Update color bar to show "Low" and "High"
        fig_heatmap.update_coloraxes(colorbar=dict(tickvals=[0, 1], ticktext=["Low", "High"]))

        with col_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        with col_heatmap:
            st.write("No languages match the current filters.")

# ---- Languages Count Expander ----
with st.expander("Languages Count"):

    # Custom binning logic for language count
    def assign_language_bins(count):
        if count == 1:
            return "One"
        elif count <= 4:
            return "2-4"
        elif count <= 9:
            return "5-9"
        else:
            return "10+"

    # Creating the 'language_count' column to show how many languages each game supports
    df['language_count'] = df['AppID'].apply(lambda x: len(games_json[x]['supported_languages']))

    # Apply the custom bin logic
    df['language_count_bins'] = df['language_count'].apply(assign_language_bins)

    # Custom manual sorting for bins
    bins_order = ["One", "2-4", "5-9", "10+"]

    # Custom colors for the bins, "ordered" color palette
    bin_colors = ["#90e0ef", "#00b4d8", "#0077b6", "#03045e"]

    container = st.container()
    # col_desc, col_pie = container.columns([1, 3])  # Adjusted column sizes for title/description and bar plot

    # with col_desc:
    st.subheader("Languages Count Analysis")
    st.write(f"""
        This section shows an analysis of the selected success metrics across the number of languages supported.
        The games have been categorized into custom bins based on how many languages they support.
    """)
    st.write(f"Games are grouped into the following language count bins: One, 2-4, 5-9, and 10+.")
    
    plots = st.columns(3) + st.columns(3)

    with plots.pop(1):
        # Bar plot showing the distribution of games across the language count bins
        game_count_pie = df.groupby('language_count_bins').size().reset_index(name='game_count')
        game_count_pie['language_count_bins'] = pd.Categorical(game_count_pie['language_count_bins'], categories=bins_order, ordered=True)
        game_count_pie = game_count_pie.sort_values(by='language_count_bins')
        game_count_pie['count'] = df['language_count_bins'].value_counts().values
        fig_pie = px.pie(game_count_pie, values='count', names='language_count_bins', title="Games Released by Language Count",
                         color='language_count_bins', color_discrete_map=dict(zip(bins_order, bin_colors)))
        # Custom label format to include combination and percentage
        fig_pie.update_traces(
            texttemplate="%{label}<br>%{percent}",  # Shows combination and percentage
            textposition="auto",  # Automatically moves text outside if the slice is too small
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        fig_pie.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="right", x=1))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Bar plots for each success metric based on the language count bins
    for i, metric in enumerate(success_metrics[1:]):
        metric_data = df.groupby('language_count_bins')[metric].mean().reset_index()
        metric_data['language_count_bins'] = pd.Categorical(metric_data['language_count_bins'], categories=bins_order, ordered=True)
        metric_data = metric_data.sort_values(by='language_count_bins')
        metric_data['count'] = df['language_count_bins'].value_counts().values

        fig_pie = px.scatter(metric_data, x='language_count_bins', y=metric, size='count',
                             color='language_count_bins', color_discrete_map=dict(zip(bins_order, bin_colors)),
                             title=f"{metric} by Language Count")
        fig_pie.update_layout(xaxis_title="Number of Supported Languages (Binned)", yaxis_title=metric, showlegend=False)
        fig_pie.update_yaxes(range=get_y_range(metric_data, metric))
        with plots[i]:
            st.plotly_chart(fig_pie, use_container_width=True)
