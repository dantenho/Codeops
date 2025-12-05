import json
import os

import pandas as pd
import streamlit as st


def load_data():
    if os.path.exists('history.json'):
        with open('history.json', 'r') as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

def show():
    st.header("Dashboard")
    st.markdown("### System Overview")

    df = load_data()

    if not df.empty:
        # Process metrics
        total_runs = df['run_id'].nunique()
        latest_run = df.iloc[-1]
        avg_duration = df['duration'].astype(float).mean() / 1000
        conflict_rate = (df['status'].str.contains('conflict').sum() / len(df)) * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sync Runs", str(total_runs))
        col2.metric("Avg Duration", f"{avg_duration:.2f}s")
        col3.metric("Conflict Rate", f"{conflict_rate:.1f}%")
        col4.metric("Latest Status", latest_run['status'])

        st.markdown("### Sync History")

        # Duration Chart
        st.subheader("Sync Duration (ms)")
        st.line_chart(df[['timestamp', 'duration']].set_index('timestamp'))

        # Recent Data Table
        st.subheader("Recent Activity")
        st.dataframe(df.tail(10))
    else:
        st.warning("No metrics history found. Run the GitHub Action to generate data.")

if __name__ == "__main__":
    show()
