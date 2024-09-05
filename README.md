
# 🔍 Bloch.ai - Simplified Process Mining Demo

This Streamlit app is a demonstration of how process mining can be used to analyse and optimise business processes. The app provides users with a clear visualisation of process flows, identifies bottlenecks, and allows for exploration of process paths through a pre-loaded dataset or a user-provided dataset.

## Features

- **Process Pathway Visualisation:** Discover and visualise the pathways in your business process using a Directly-Follows Graph (DFG).
- **Bottleneck Analysis:** Analyse and identify bottlenecks by examining the average duration of each process step.
- **Custom Data Upload:** Upload your own CSV file to explore and analyse your specific process data.
- **Pre-loaded Demo Dataset:** The app comes with a pre-loaded invoice processing dataset for immediate exploration.

## How to Use

1. **Upload a CSV File:** (Optional) Upload your CSV file containing process data with columns for `case_id`, `activity`, and `timestamp`.
2. **Explore the Pre-loaded Dataset:** If no file is uploaded, the app will use the default invoice processing dataset.
3. **View Summary Statistics:** Get an overview of the number of cases and process steps in the dataset.
4. **Visualise Process Pathways:** See the process flow in the form of a Directly-Follows Graph.
5. **Analyse Bottlenecks:** Examine where the process spends the most time and identify potential inefficiencies.

## Dataset

The app uses a pre-loaded invoice processing dataset, which simulates a typical business process with multiple steps such as `Receive Invoice`, `Validate Invoice`, `Approve Invoice`, etc. Users can also upload their own dataset to see how process mining can be applied to different contexts.

## Visualizations

- **Process Pathways Diagram:** A Directly-Follows Graph that shows the flow of activities in the process.
- **Bottleneck Analysis Heatmap:** A heatmap displaying the average time spent on each activity to identify bottlenecks.

## Technologies Used

- **Python**
- **Streamlit**
- **Pandas**
- **NetworkX**
- **Matplotlib**
- **Seaborn**

## Running the App

To run the app locally:

1. **Clone this repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**

   ```bash
   streamlit run streamlit_app.py
   ```

## Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [NetworkX Documentation](https://networkx.github.io/documentation/stable/)
- [Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/)
- [Seaborn Documentation](https://seaborn.pydata.org/)

## About

This app was created by Bloch AI LTD. It is distributed under the GNU GENERAL PUBLIC LICENSE, Version 3. For more information, visit [www.bloch.ai](https://www.bloch.ai).
