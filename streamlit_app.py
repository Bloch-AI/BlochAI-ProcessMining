import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.inductive   
 import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter   
 as pt_converter
from pm4py.objects.log.obj import EventLog
import io

# Default CSV content (if no file uploaded)
default_csv = """
case_id,activity,timestamp
1,Start,2022-01-01 00:00:00
1,Task A,2022-01-01 01:00:00
1,Task B,2022-01-01 02:00:00
1,End,2022-01-01 03:00:00
2,Start,2022-01-02 00:00:00
2,Task A,2022-01-02 01:00:00
2,Task C,2022-01-02 02:00:00
2,End,2022-01-02 03:00:00
3,Start,2022-01-03 00:00:00
3,Task B,2022-01-03 01:00:00
3,Task C,2022-01-03 02:00:00
3,End,2022-01-03 03:00:00
"""

def main():
    st.title("Process Mining App")

    # File Upload with Error Handling
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv"])
    if uploaded_file is None:
        df = pd.read_csv(io.StringIO(default_csv))
        st.warning("Using default CSV data.")
    else:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return

    # Data Cleaning & Preparation
    df.columns = df.columns.str.lower().str.strip() 
    required_columns = {'case_id', 'activity', 'timestamp'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
        return 

    df = df.rename(columns={
        'case_id': 'case:concept:name',
        'activity': 'concept:name',
        'timestamp': 'time:timestamp'
    })

    try:
        df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
        df = dataframe_utils.convert_timestamp_columns_in_df(df)
        df = df.sort_values(by='time:timestamp')
    except Exception as e: 
        st.error(f"Error preparing data: {e}")
        return

    # Data Preview
    st.subheader("Data Preview")
    st.write(df.head())

    try:
        log = log_converter.apply(df)
        if not isinstance(log, EventLog):
            st.error("The converted log is not an EventLog object.")
            return
    except KeyError as e:
        st.error(f"KeyError during log conversion: {e}")
        return
    except Exception as e:
        st.error(f"Unexpected error during log conversion: {e}")
        return

    # Process Mining and Visualization
    try:
        tree = inductive_miner.apply(log)
        net, initial_marking, final_marking = pt_converter.apply(tree)
    except Exception as e:
        st.error(f"Error during process mining: {e}")
        return

    # Create a directed graph
    G = nx.DiGraph()

    # Add places to the graph
    for place in net.places:
        G.add_node(place.name, shape='circle')

    # Add transitions to the graph with meaningful labels
    for transition in net.transitions:
        if not transition.label:
            G.add_node(transition.name, shape='box', label='silent')
        else:
            G.add_node(transition.name, shape='box', label=transition.label)

    # Add edges to the graph
    for arc in net.arcs:
        G.add_edge(arc.source.name, arc.target.name)

    # Draw the graph with improved spacing
    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.5, iterations=100) 
    node_shapes = nx.get_node_attributes(G, 'shape')
    node_labels = nx.get_node_attributes(G, 'label')

    # Draw nodes with custom shapes
    nx.draw(G, pos, with_labels=False, node_size=5000, node_color='skyblue', ax=ax, edge_color='gray', linewidths=0.5)
    nx.draw_networkx_labels(G, pos, labels={n: n if node_shapes[n] == 'circle' else node_labels[n] for n in G.nodes}, font_size=12, font_color='white', font_weight='bold')
    nx.draw_networkx_nodes(G, pos, nodelist=[n for n in node_shapes if node_shapes[n] == 'circle'], node_shape='o')
    nx.draw_networkx_nodes(G, pos, nodelist=[n for n in node_shapes if node_shapes[n] == 'box'], node_shape='s')

    # Add legend with clear symbols
    legend_elements = [Patch(facecolor='skyblue', edgecolor='k', label='Place (circle)'),
                       Patch(facecolor='skyblue', edgecolor='k', label='Transition (square)')]
    ax.legend(handles=legend_elements, loc='upper left')

    st.pyplot(fig)

    # Summary Statistics
    st.subheader("Summary Statistics")
    try:
        num_cases = len(log)
        st.write("Number of cases:", num_cases)
    except Exception as e:
        st.error(f"Error getting number of cases: {e}")

    try:
        num_events = sum([len(trace) for trace in log])
        st.write("Number of events:", num_events)
    except Exception as e:
        st.error(f"Error getting number of events: {e}")

    # Top 5 Frequent Activities (excluding start and end)
    try:
        top_activities = df['concept:name'].value_counts()
        top_activities = top_activities[~top_activities.index.isin(['start', 'end'])].head(5).reset_index()
        top_activities.columns = ['activity', 'count']
        st.write("Top 5 Frequent Activities:")
        st.bar_chart(top_activities.set_index('activity'))
    except Exception as e:
        st.error(f"Error generating top activities chart: {e}")

if __name__ == "__main__":
    main()
