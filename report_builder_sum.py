import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="AI Report Builder", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- API KEY INPUT ---
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    # --- READ DATA ---
    try:
        df = pd.read_csv(uploaded_file, encoding="latin1")
        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # --- SUMMARY STATS ---
        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe())

        # --- CHART SECTION ---
        st.subheader("📉 Data Visualization")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            col1, col2 = st.columns(2)

            with col1:
                chart_type = st.selectbox("Select chart type:", ["Line", "Bar", "Scatter"])
            with col2:
                color = st.color_picker("Pick chart color:", "#00BFFF")

            x_axis = st.selectbox("X-axis", df.columns)
            y_axis = st.selectbox("Y-axis", df.columns)

            if st.button("📊 Generate Chart"):
                if chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart", color_discrete_sequence=[color])
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart", color_discrete_sequence=[color])
                else:
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart", color_discrete_sequence=[color])

                fig.update_layout(
                    title_x=0.5,
                    template="plotly_white",
                    title_font=dict(size=22),
                    paper_bgcolor="#F9FAFB",
                    plot_bgcolor="#F9FAFB"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for visualization.")

        # --- AI ANALYSIS SECTION ---
        if api_key:
            if st.button("🧠 Generate AI Summary"):
                with st.spinner("Analyzing your data..."):
                    client = OpenAI(api_key=api_key)

                    summary = df.describe().to_string()
                    prompt = f"""
                    You are a data analyst. Write a clear, insightful summary of this dataset
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
            st.info("🔑 Enter your API key to enable AI summaries.")

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
