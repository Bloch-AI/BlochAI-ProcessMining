import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.visualization.process_tree import visualizer as pt_visualizer

def main():
    st.title("Process Mining App")

    st.sidebar.header("Upload your CSV file")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

    if uploaded_file is not None:
        # Load data with explicit encoding (e.g., 'utf-8')
        df = pd.read_csv(uploaded_file, encoding='utf-8')  # Assuming UTF-8, adjust if needed

        st.subheader("Data Preview")
        st.write(df.head())

        # Ensure the column names are consistent
        df.columns = [col.lower().strip() for col in df.columns]

        # Column Checks (made more robust)
        required_columns = {'case_id', 'activity', 'timestamp'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
            return

        # Rename columns to match pm4py expectations
        df.rename(columns={
            'case_id': 'case:concept:name',
            'activity': 'concept:name',
            'timestamp': 'time:timestamp'
        }, inplace=True)

        # Data Preparation (with error handling for date parsing)
        try:
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
        except pd.errors.OutOfBoundsDatetime:
            st.error("Timestamp values are out of bounds. Check the format (e.g., YYYY-MM-DD HH:MM:SS).")
            return
        except Exception as e:
            st.error(f"Error parsing timestamps: {e}")
            return

        df = dataframe_utils.convert_timestamp_columns_in_df(df)
        df = df.sort_values(by='time:timestamp')

        # Debugging step: Display the first few rows after preparation
        st.subheader("Data Preview After Preparation")
        st.write(df.head())

        try:
            log = log_converter.apply(df)
        except KeyError as e:
            st.error(f"KeyError during log conversion: {e}")
            return
        except Exception as e:
            st.error(f"Unexpected error during log conversion: {e}")
            return

        # Process Mining and Visualization
        try:
            tree = inductive_miner.apply(log)
        except Exception as e:
            st.error(f"Error during process mining: {e}")
            return

        # Visualize Process Tree
        gviz = pt_visualizer.apply(tree)
        pt_visualizer.view(gviz)

        # Summary Statistics
        st.subheader("Summary Statistics")
        st.write("Number of cases:", len(case_statistics.get_all_casestypes(log)))
        st.write("Number of events:", len(log))

        # Top 5 Frequent Activities
        top_activities = df['concept:name'].value_counts().head(5)  # Limit to top 5
        st.write("Top 5 Frequent Activities:")
        st.bar_chart(top_activities)

if __name__ == "__main__":
    main()
