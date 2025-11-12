import streamlit as st
import pandas as pd
import plotly.express as px
import os
from openai import OpenAI

# --- APP SETUP ---
st.set_page_config(page_title="AI Report Builder", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- GET API KEY ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ OpenAI API key not found. Set OPENAI_API_KEY in your environment or Streamlit secrets.")
    st.stop()

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # --- SUMMARY STATS ---
    st.subheader("📈 Summary Statistics")
    summary = df.describe().to_string()
    st.text(summary)

    # --- CHART BUILDER ---
    st.subheader("📉 Data Visualization")

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_columns) < 2:
        st.warning("Need at least two numeric columns for charting.")
    else:
        x_axis = st.selectbox("Select X-axis:", options=numeric_columns)
        y_axis = st.multiselect("Select Y-axis (you can choose multiple):", options=numeric_columns, default=[numeric_columns[1]])

        if y_axis:
            chart_type = st.selectbox("Chart Type:", ["Line", "Bar", "Scatter"])

            # Generate chart dynamically
            if chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, title=f"{', '.join(y_axis)} vs {x_axis}")
            elif chart_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"{', '.join(y_axis)} vs {x_axis}")
            else:
                fig = px.scatter(df, x=x_axis, y=y_axis[0], color=y_axis[0], title=f"{y_axis[0]} vs {x_axis}")

            st.plotly_chart(fig, use_container_width=True)

    # --- AI SUMMARY ---
    if st.button("🧠 Generate AI Summary"):
        with st.spinner("Analyzing your data..."):
            client = OpenAI(api_key=api_key)
            prompt = f"""
            You are a professional data analyst. Write a clear, insightful summary of this dataset
            based on the following summary statistics:
            {summary}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful data analyst."},
                    {"role": "user", "content": prompt}
                ],
            )

            st.subheader("📝 AI Summary")
            st.write(response.choices[0].message.content)
else:
    st.info("👆 Upload a CSV to get started.")

