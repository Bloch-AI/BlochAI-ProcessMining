import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.traces.generic.log import case_statistics

def main():
    st.title("Process Mining App")

    st.sidebar.header("Upload your CSV file")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

    if uploaded_file is not None:
        # Load data with explicit encoding (e.g., 'utf-8')
        df = pd.read_csv(uploaded_file, encoding='utf-8')  # Assuming UTF-8, adjust if needed

        st.subheader("Data Preview")
        st.write(df.head())

        # Column Checks (made more robust)
        required_columns = {'case_id', 'activity', 'timestamp'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
            return

        # Data Preparation (with error handling for date parsing)
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except pd.errors.OutOfBoundsDatetime:
            st.error("Timestamp values are out of bounds. Check the format (e.g., YYYY-MM-DD HH:MM:SS).")
            return

        df = dataframe_utils.convert_timestamp_columns_in_df(df)
        df = df.sort_values(by='timestamp')
        log = log_converter.apply(df, parameters={
            "case_id_key": "case_id",
            "activity_key": "activity",
            "timestamp_key": "timestamp"
        })

        # Process Mining and Visualization
        net, initial_marking, final_marking = inductive_miner.apply(log)

        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes to the graph
        for node in net.places:
            G.add_node(node.name)
        for node in net.transitions:
            G.add_node(node.name)

        # Add edges to the graph
        for edge in net.arcs:
            G.add_edge(edge.source.name, edge.target.name)

        # Draw the graph
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, ax=ax)
        st.pyplot(fig)

        # Summary Statistics
        st.subheader("Summary Statistics")
        st.write("Number of cases:", len(case_statistics.get_all_casestypes(log)))
        st.write("Number of events:", len(log))

        # Top 5 Frequent Activities
        top_activities = df['activity'].value_counts().head(5)  # Limit to top 5
        st.write("Top 5 Frequent Activities:")
        st.bar_chart(top_activities)

if __name__ == "__main__":
    main()
