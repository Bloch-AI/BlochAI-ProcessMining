import streamlit as st
import pandas as pd
from pm4py.objects.conversion.log import factory as log_conversion_factory
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet import factory as viz_factory
from pm4py.statistics.traces.generic.log import case_statistics

def main():
    st.title("Process Mining App")

    st.sidebar.header("Upload your CSV file")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])

    if uploaded_file is not None:
        # Load data
        df = pd.read_csv(uploaded_file)

        st.subheader("Data Preview")
        st.write(df.head())

        # Ensure the dataframe has the necessary columns
        if not {'case_id', 'activity', 'timestamp'}.issubset(df.columns):
            st.error("The CSV file must contain 'case_id', 'activity', and 'timestamp' columns.")
            return

        # Convert the dataframe to a pm4py event log
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = dataframe_utils.convert_timestamp_columns_in_df(df)
        df = df.sort_values(by='timestamp')  # Ensure the dataframe is sorted by timestamp
        log = log_conversion_factory.apply(df, parameters={"case_id_key": "case_id", "activity_key": "activity", "timestamp_key": "timestamp"})

        # Apply the inductive miner
        net, initial_marking, final_marking = inductive_miner.apply(log)

        # Visualize the process model
        gviz = viz_factory.apply(net, initial_marking, final_marking, parameters={"format": "svg"})
        st.graphviz_chart(gviz.source)

        st.subheader("Summary Statistics")
        # Calculate and display summary statistics
        st.write("Number of cases:", len(case_statistics.get_all_casestypes(log)))
        st.write("Number of events:", len(log))

        # Display the top 5 frequent activities
        activities_count = df['activity'].value_counts().head()
        st.write("Top 5 Frequent Activities:")
        st.bar_chart(activities_count)

if __name__ == "__main__":
    main()
