#**********************************************
# Process Mining Demo App
# Version 1.2
# 5th September 2024
# Jamie Crossman-Smith
# jamie@bloch.ai
#**********************************************
# This Python code creates a web-based application using Streamlit to demonstrate
# process mining techniques. The application allows users to upload their own CSV
# file containing process data or use a default dataset. It then analyses this
# data to visualise and understand business processes.
#
# The code begins by importing necessary libraries and setting up a default dataset.
# It then defines a main function that handles the core functionality:
# - Loading and processing data
# - Creating a Directly-Follows Graph (DFG) to map out the process flow
# - Visualising this graph using NetworkX and Matplotlib
# - Performing bottleneck analysis
#
# The application displays the process pathways, showing how different activities
# are connected and how frequently they occur. It also provides a detailed breakdown
# of individual case pathways and uses a heatmap to highlight potential bottlenecks
# in the process.
#**********************************************

# Import necessary libraries for the application
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import io
import logging
from typing import Dict, List, Tuple, Optional
import os

log_file_path = os.path.join(os.getcwd(), 'process_mining_errors.log')

# Setup enhanced logging configuration
logging.basicConfig(filename=log_file_path, 
                    level=logging.DEBUG,  
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Redirect Streamlit's logger to our file
streamlit_logger = logging.getLogger('streamlit')
streamlit_logger.setLevel(logging.DEBUG)
streamlit_logger.addHandler(logging.FileHandler(log_file_path))
streamlit_logger.propagate = False

# Test log to check if logging works
logging.info("Application started and logging is working.")

# Default CSV content
DEFAULT_CSV = """
case_id,activity,timestamp
1,Start,2022-01-01 08:00:00
1,Receive Invoice,2022-01-01 08:30:00
1,Validate Invoice,2022-01-01 10:00:00
1,Approve Invoice,2022-01-01 11:00:00
1,Match Purchase Order,2022-01-01 13:00:00
1,Pay Invoice,2022-01-02 09:00:00
1,End,2022-01-02 10:00:00
2,Start,2022-01-02 09:00:00
2,Receive Invoice,2022-01-02 09:15:00
2,Validate Invoice,2022-01-02 10:30:00
2,Approve Invoice,2022-01-02 11:15:00
2,Match Purchase Order,2022-01-02 12:00:00
2,Resolve Discrepancy,2022-01-03 09:00:00
2,Pay Invoice,2022-01-04 09:00:00
2,End,2022-01-04 09:30:00
3,Start,2022-01-03 07:00:00
3,Receive Invoice,2022-01-03 08:00:00
3,Validate Invoice,2022-01-03 09:00:00
3,Match Purchase Order,2022-01-03 10:00:00
3,Approve Invoice,2022-01-03 11:30:00
3,Pay Invoice,2022-01-05 08:00:00
3,End,2022-01-05 09:00:00
4,Start,2022-01-04 08:00:00
4,Receive Invoice,2022-01-04 08:15:00
4,Validate Invoice,2022-01-04 09:00:00
4,Resolve Discrepancy,2022-01-05 10:00:00
4,Match Purchase Order,2022-01-05 11:00:00
4,Approve Invoice,2022-01-05 13:00:00
4,Pay Invoice,2022-01-06 09:00:00
4,End,2022-01-06 10:00:00
"""

# Helper function for styling info boxes
def create_info_box(content: str, title: Optional[str] = None) -> str:
    box_html = f"""
    <div style='padding:15px; background-color:#f9f9f9; border-left: 6px solid #2c3e50; font-family: Arial, sans-serif;'>
    """
    if title:
        box_html += f"<h4>{title}</h4>"
    box_html += f"{content}</div><br>"
    return box_html

# Helper function for creating visualisations
def create_dfg_visualisation(g: nx.DiGraph, start_nodes: List[str], end_nodes: List[str]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(g, seed=42)
    
    node_colors = ['green' if node in start_nodes else 'red' if node in end_nodes else 'lightblue' for node in g.nodes()]
    
    nx.draw(g, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=2000, 
            font_size=10, font_weight='bold', edge_color='gray', arrows=True)
    
    edge_labels = nx.get_edge_attributes(g, 'weight')
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, ax=ax)
    
    return fig

# Helper function for bottleneck analysis
def perform_bottleneck_analysis(df: pd.DataFrame) -> Tuple[pd.Series, plt.Figure]:
    df['next_timestamp'] = df.groupby('case_id')['timestamp'].shift(-1)
    df['duration'] = (df['next_timestamp'] - df['timestamp']).dt.total_seconds() / 3600
    df = df.dropna(subset=['duration'])
    
    filtered_df = df[~df['activity'].isin(['Start', 'End'])]
    activity_durations = filtered_df.groupby('activity')['duration'].mean().sort_values(ascending=False).round(2)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(activity_durations.to_frame().T, cmap='coolwarm', annot=True, ax=ax)
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_title('Average Time Spent on Each Activity (Hours)')
    
    return activity_durations, fig

# Main function
def main():

    # Clear the log file at the start of each run
    with open('process_mining_errors.log', 'w'):
        pass  # This opens the file in write mode and clears its contents

    st.title("🤖 Simplified Process Mining Demo")
    
    st.markdown(create_info_box(
        "Process mining is a data-driven approach to analysing business processes. It takes event logs from IT systems, "
        "allowing companies to map out, visualise, and better understand the actual processes as they occur in real life. "
        "This helps identify inefficiencies, bottlenecks, and areas for improvement in their processes, making it a powerful tool for optimising operations. "
        "Often organsations think as the data is not in one place, or is not clean etc that this means "
        "they cannot use process mining. However, a good data analyst can extract data from different systems, manage missing data, cleanse, merge, and harmonise "
        "the data in such a way that it can be used very effectively in process mining, even tools like excel can do this if needed. "
        "There are several excellent commercial process mining tools that allow you to directly connect and import data from multiple sources such as ERPs. "
        "However, these can be expensive and there are other open-source alternatives available that are particularly suitable if you wish to run process mining as a one off exercise.<br><br>"
        "<b>This demo application defaults to a pre-loaded invoice payment process data set, but you can try your own dataset if you wish "
        "by importing it via the sidebar on the left. 👈</b>",
        "What is Process Mining?"
    ), unsafe_allow_html=True)
    
    # File upload section
    st.sidebar.header("File Upload")
    st.sidebar.markdown("<b>Upload your CSV file to start analysing your process data.</b>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
    
    # Disclaimer
    st.sidebar.markdown("---")
    st.sidebar.markdown(create_info_box(
        "This tool is for educational purposes only. Users are solely responsible for data uploaded; "
        "no liability is assumed by Bloch AI Limited or its directors in any way for any data uploaded, outputs, or results, which should not be relied upon for decision-making. "
        "Do not upload actual, proprietary, or sensitive data. By uploading data, you agree to these terms.",
        "Disclaimer"
    ), unsafe_allow_html=True)
    st.sidebar.markdown("---")

   # Load and process data
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            logging.info(f"Uploaded file processed: {uploaded_file.name}")
        else:
            df = pd.read_csv(io.StringIO(DEFAULT_CSV))
            logging.info("Default CSV data used")
        
        # Validate required columns
        required_columns = {"case_id", "activity", "timestamp"}
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            error_msg = f"CSV file is missing the following columns: {', '.join(missing_columns)}."
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        # Convert timestamp column
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', infer_datetime_format=True)
        invalid_timestamps = df['timestamp'].isnull().sum()
        if invalid_timestamps > 0:
            warning_msg = f"There are {invalid_timestamps} invalid values in the 'timestamp' column. These rows will be skipped."
            st.warning(warning_msg)
            logging.error(warning_msg)
            invalid_timestamps_df = df[df['timestamp'].isnull()]
            st.subheader("Data Error: Invalid DateTime Data")
            st.dataframe(invalid_timestamps_df)
            logging.error(f"Invalid timestamps:\n{invalid_timestamps_df.to_string()}")
            df = df.dropna(subset=['timestamp'])
        
        # Check for short or negative durations
        df = df.sort_values(by=['case_id', 'timestamp'])
        df['next_timestamp'] = df.groupby('case_id')['timestamp'].shift(-1)
        df['duration'] = (df['next_timestamp'] - df['timestamp']).dt.total_seconds() / 3600  # duration in hours
        short_durations = df[df['duration'] < (1 / 60)]  # Less than 1 minute
        if not short_durations.empty:
            warning_msg = f"Warning: {len(short_durations)} activities have very short or negative durations. Please review your dataset."
            st.warning(warning_msg)
            logging.error(warning_msg)
            st.subheader("Data Error: Rows with Short or Negative Durations")
            st.dataframe(short_durations)
            logging.error(f"Short or negative durations:\n{short_durations.to_string()}")
        
        # Display data preview
        st.subheader("1.Data Preview")
        st.dataframe(df.head())
        logging.info(f"Data preview: {df.head().to_string()}")
        
        # Create the Directly-Follows Graph (DFG)
        dfg: Dict[Tuple[str, str], int] = {}
        for case_id, case_df in df.groupby('case_id'):
            case_df = case_df.sort_values('timestamp')
            activities = case_df['activity'].tolist()
            for i in range(len(activities) - 1):
                pair = (activities[i], activities[i + 1])
                dfg[pair] = dfg.get(pair, 0) + 1
        logging.info(f"DFG created with {len(dfg)} edges")
        
        # Create NetworkX graph
        g = nx.DiGraph()
        for (start, end), weight in dfg.items():
            g.add_edge(start, end, weight=weight)
        
        # Identify start and end nodes
        start_nodes = df.groupby('case_id').first()['activity'].unique().tolist()
        end_nodes = df.groupby('case_id').last()['activity'].unique().tolist()
        
        # Visualize the process
        st.subheader("2.Discovered Process Pathways")
        st.markdown(create_info_box(
            "This diagram illustrates the pathways discovered in the process data. "
            "It shows the flow of activities and the frequency of transitions between them. "
            "The data is ordered by the datetimestamp before this network diagram is created."
        ), unsafe_allow_html=True)
        
        fig = create_dfg_visualization(g, start_nodes, end_nodes)
        st.pyplot(fig)
        
        # Print detailed pathways
        st.subheader("3.Detailed Case Pathways")
        st.markdown(create_info_box(
            "Below is a detailed list of the pathways for each case in the process. "
            "This allows you to see the exact sequence of activities for each case."
        ), unsafe_allow_html=True)
        
        for case_id, case_df in df.groupby('case_id'):
            case_df = case_df.sort_values('timestamp')
            activities = case_df['activity'].tolist()
            pathway = " -> ".join(activities)
            st.write(f"**Case {case_id}:** {pathway}")
        
        # Perform bottleneck analysis
        st.subheader("4.Bottleneck Analysis")
        st.markdown(create_info_box(
            "This section identifies potential bottlenecks in the process by analysing "
            "the average time spent on each activity, excluding the Start and End activities."
        ), unsafe_allow_html=True)
        
        activity_durations, bottleneck_fig = perform_bottleneck_analysis(df)
        st.pyplot(bottleneck_fig)
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        st.error(error_msg)
        logging.error(error_msg, exc_info=True)

    # Ensure all logs are written
    #logging.shutdown()

# Run the app
if __name__ == "__main__":
    main()

# After running the app, display the log contents
st.subheader("5.Error Log")
try:
    with open('process_mining_errors.log', 'r') as log_file:
        log_contents = log_file.read()
        if log_contents.strip() == "":
            st.info("No errors have been logged.")
        else:
            st.text(log_contents)
except FileNotFoundError:
    st.warning("Log file not found. No errors have been logged yet.")

# Footer (consider moving this to a separate HTML file)
footer = st.container()
footer.markdown(
    '''
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: black;
        color: white;
        text-align: center;
        padding: 10px 0;
    }
    </style>
    <div class="footer">
        <p>© 2024 Bloch AI LTD - All Rights Reserved. <a href="https://www.bloch.ai" style="color: white;">www.bloch.ai</a></p>
    </div>
    ''',
    unsafe_allow_html=True
)
