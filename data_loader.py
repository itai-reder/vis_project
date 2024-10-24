import streamlit as st
import pandas as pd
import json

# Cached function to load CSV data
@st.cache_data
def load_csv_data():
    return pd.read_csv('cleaned_games.csv')

# Cached function to load JSON data
@st.cache_data
def load_json_data(file):
    with open(file, 'r') as f:
        return json.load(f)
    
# Function to filter the JSON data after applying the CSV filters
def filter_json_data(json_data, filtered_csv_df, json_key_column='AppID'):
    filtered_keys = set(filtered_csv_df[json_key_column].astype(str).tolist())
    return {key: json_data[key] for key in json_data if key in filtered_keys}

# Sidebar filters functionality, which remembers user selections between pages
def apply_filters_sidebar(df):
    st.sidebar.header("🔍 Apply Filters")

    min_filter = st.session_state.get('min_filter', {})
    max_filter = st.session_state.get('max_filter', {})
    # Multiselect for choosing which features to filter by
    selected_filters = st.sidebar.multiselect(
        "Select features to filter by",
        options=[col for col in df.columns if col not in ['AppID', 'Name', 'Release date']],
        # default=list(min_filter.keys())  # Default filters are set here
        default = min_filter.keys()
    )

    # Remove filters that are not selected anymore from the session state
    for column in min_filter.copy():
        if column not in selected_filters:
            min_filter.pop(column)

    # Apply filters to the DataFrame and store the result in session_state
    for column in selected_filters:
        st.sidebar.write(f"**{column}**")
        if df[column].dtype == 'int64' or df[column].dtype == 'float64':
            min_value = float(df[column].min())
            max_value = float(df[column].max())

            # Inline inputs and slider for numeric filters
            col1, col2 = st.sidebar.columns(2)

            default_min = max(min_value, min_filter.get(column, min_value))
            default_max = min(max_value, max_filter.get(column, max_value))

            with col1:
                manual_min = st.number_input(
                    f"Min {column}",
                    min_value=min_value,
                    max_value=max_value,
                    value=default_min,
                    key=f"min_{column}"
                )
                st.write(f"(Min: {min_value})")
            with col2:
                manual_max = st.number_input(
                    f"Max {column}",
                    min_value=min_value,
                    max_value=max_value,
                    value=default_max,
                    key=f"max_{column}"
                )
                st.write(f"(Max: {max_value})")

            st.session_state[f"min_filter"][column] = manual_min
            st.session_state[f"max_filter"][column] = manual_max

            df = df[(df[column] >= manual_min) & (df[column] <= manual_max)]
            st.session_state['filtered_df'] = df

    # Save the filtered DataFrame in session_state for later use
    st.session_state['filtered_df'] = df
    return df

# Function to be called in each page to load the CSV and JSON data
def load_data_for_page():
    return apply_filters_sidebar(load_csv_data())