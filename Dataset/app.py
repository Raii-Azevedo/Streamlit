import streamlit as st
import pandas as pd

# Allow the user to upload a CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# If a file is uploaded, proceed with reading and processing it
if uploaded_file is not None:
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file, sep=',')
        
        # Remove extra spaces from column names
        df.columns = df.columns.str.strip()

        # Check if 'Datas' column exists, if not, let the user know
        if 'Datas' not in df.columns:
            st.warning("The 'Datas' column is missing from the dataset. Please check the file.")
            df['Datas'] = pd.to_datetime('now')  # Add a placeholder column or handle accordingly if needed

        # Convert 'Datas' to datetime if it's available
        if 'Datas' in df.columns:
            try:
                df['Datas'] = pd.to_datetime(df['Datas'], errors='coerce')  # 'coerce' will put NaT for invalid data
                df = df.dropna(subset=['Datas'])  # Drop rows with invalid dates
            except Exception as e:
                st.error(f"Error while trying to convert the 'Datas' column to datetime: {e}")
                st.stop()

        # Title of the app
        st.title("Download DataFrame")

        # Initial message
        st.markdown(
            """
            Select the desired columns and apply filters to create the final DataFrame, 
            then download the filtered dataset as a CSV file.
            """
        )

        # Display the DataFrame (first 10 rows)
        st.header("Dataset Preview")
        st.dataframe(df.head(10))

        # Sidebar - Filters and column selection
        with st.sidebar:
            st.markdown(
                """
                <style>
                .sidebar .sidebar-content {
                    background-color: #f0f0f0;  /* Light gray background */
                }
                </style>
                """, unsafe_allow_html=True
            )

            # Section for selecting columns to display
            st.subheader("Select Columns to Display")
            selected_columns = st.multiselect(
                "Choose the columns to include in the dataset:",
                options=df.columns.tolist(),
                default=df.columns.tolist()  # By default, select all columns
            )

            # Date range filter (only apply if 'Datas' column exists)
            if 'Datas' in df.columns:
                st.subheader("Filter by Date Range")
                min_date = df['Datas'].min().date()  # Convert to 'date'
                max_date = df['Datas'].max().date()  # Convert to 'date'

                # Allow user to select a date range
                start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
                end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # Filter the DataFrame based on date selections (if 'Datas' exists)
        filtered_df = df
        if 'Datas' in df.columns:
            filtered_df = filtered_df[(filtered_df['Datas'].dt.date >= start_date) & (filtered_df['Datas'].dt.date <= end_date)]

        # Dynamically filter by other available columns (e.g., 'Motivo', 'Markets', etc.)
        for column in df.columns:
            if column not in ['Datas']:  # Skip 'Datas' since it's handled separately
                if column in df.columns:
                    unique_values = df[column].dropna().unique()
                    st.subheader(f"Filter by {column}")
                    selected_values = st.multiselect(
                        f"Select {column} to filter:",
                        options=["All"] + unique_values.tolist(),
                        default=["All"]  # By default, select 'All'
                    )

                    if "All" not in selected_values:
                        filtered_df = filtered_df[filtered_df[column].isin(selected_values)]

        # Filter columns based on user selection
        filtered_df = filtered_df[selected_columns]

        # Display the filtered DataFrame with selected columns
        st.header("Dataset after Applying Filters and Selections")
        st.dataframe(filtered_df)

        # Add download button for the filtered DataFrame
        if not filtered_df.empty:
            @st.cache_data
            def convert_df(df):
                """Convert the DataFrame to CSV"""
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(filtered_df)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to display with the selected filters.")
        
    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")
