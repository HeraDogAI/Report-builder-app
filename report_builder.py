
import plotly.io as pio

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.title("📊 Automatic Report Builder")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="latin1")  # handles weird characters
    st.write("### Data Preview", df.head())

    # Column selection
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        st.write("### Data Visualization")

        chart_type = st.selectbox("Choose chart type", ["Line", "Bar", "Scatter"])
        x_col = st.selectbox("X-axis", df.columns)
        y_col = st.selectbox("Y-axis", numeric_cols)

        if chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{chart_type} Chart")
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{chart_type} Chart")
        else:
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{chart_type} Chart")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric columns found for visualization.")
else:
    st.info("👆 Upload a CSV to begin.")
else
st.plotly_chart(fig, use_container_width=True)



