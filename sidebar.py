# sidebar.py
import streamlit as st
import json
import os
import pandas as pd

# File to store the notes
NOTES_FILE = 'notes.json'

# Function to load the notes from the file
def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'r') as f:
            return json.load(f).get('notes', "")
    return ""

# Function to save the notes to the file
def save_notes(notes):
    with open(NOTES_FILE, 'w') as f:
        json.dump({'notes': notes}, f)

# Sidebar notes functionality
def notes_sidebar():
    st.sidebar.header("Session Notes")

    # Load the existing notes
    notes = load_notes()

    # Text area for writing the notes
    updated_notes = st.sidebar.text_area("Write your notes here:", value=notes, height=200)

    # Buttons for saving or clearing the notes
    if st.sidebar.button("Save Notes"):
        save_notes(updated_notes)
        st.sidebar.success("Notes saved successfully!")

    if st.sidebar.button("Delete Notes"):
        save_notes("")
        st.sidebar.info("Notes cleared.")

# Default filters {column: default_value}
default_min_filter = {
    "Reviews": 20.0
    }
# Load the CSV data only once and cache it for efficiency.
@st.cache_data
def load_csv_data():
    return pd.read_csv('cleaned_games.csv')

# Sidebar filters functionality
def apply_filters_sidebar():
    # Load data into session_state if it's not already there
    # if 'df' not in st.session_state:
    #     st.session_state['df'] = load_csv_data()

    # df = st.session_state['df']
    df = load_csv_data()
    # Sidebar filter settings
    st.sidebar.header("🔍 Apply Filters")

    # Multiselect for choosing which features to filter by
    selected_filters = st.sidebar.multiselect(
        "Select features to filter by",
        options=[col for col in df.columns if col not in ['AppID', 'Name', 'Release date', 'Release Year', 'Release Month']],
        default=list(default_min_filter.keys())
    )

    # Apply filters to the DataFrame and store the result in session_state
    for column in selected_filters:
        st.sidebar.write(f"**{column}**")
        if df[column].dtype == 'int64' or df[column].dtype == 'float64':
            min_value = float(df[column].min())
            max_value = float(df[column].max())

            # Inline inputs and slider for numeric filters
            col1, col2 = st.sidebar.columns(2)

            default_min = max(min_value, default_min_filter.get(column, min_value))
            default_max = max_value

            # Use session state to remember the filters
            if f'min_{column}' not in st.session_state:
                st.session_state[f'min_{column}'] = default_min
            if f'max_{column}' not in st.session_state:
                st.session_state[f'max_{column}'] = default_max

            with col1:
                manual_min = st.number_input(
                    f"Min {column}",
                    min_value=min_value,
                    max_value=max_value,
                    value=st.session_state[f"min_{column}"],
                    key=f"min_{column}"
                )
            with col2:
                manual_max = st.number_input(
                    f"Max {column}",
                    min_value=min_value,
                    max_value=max_value,
                    value=st.session_state[f"max_{column}"],
                    key=f"max_{column}"
                )

            selected_range = st.sidebar.slider(
                f"{column} range",
                min_value=min_value,
                max_value=max_value,
                value=(manual_min, manual_max),
                step=(max_value - min_value) / 100,
                key=f"slider_{column}"
            )

            # Filter the dataframe based on the slider range
            df = df[df[column].between(*selected_range)]
            st.session_state['df'] = df

        # Apply boolean or object filters similarly...

    # Save the filtered DataFrame in session_state
    st.session_state['filtered_df'] = df
    return df