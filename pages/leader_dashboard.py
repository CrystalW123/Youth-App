import streamlit as st
import pandas as pd

st.title("Dashboard")

st.write("This will show engagement")

sample_data = pd.DataFrame(
    {
        "metric": ["Quiz Attempts", "Correct Answers", "Topics Requested"],
        "value": [12, 8, 5]
    }
)

st.dataframe(sample_data, width=True)