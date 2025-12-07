import streamlit as st
import pandas as pd
import plotly.express as px
import os
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="Promethix", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- LOAD OPENAI API KEY (FROM ENV OR SECRETS) ---
api_key = os.getenv("OPENAI_API_KEY")  # Read key from environment or Streamlit secrets
if not api_key:
    st.error("⚠️ Missing OpenAI API key. Add it to your Streamlit secrets or environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # --- READ DATA ---
        df = pd.read_csv(uploaded_file, encoding="latin1")

        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # --- FULL DATASET VIEWER ---
        with st.expander("📄 Open Full Dataset (View Entire Table)"):
            st.dataframe(df)

        # --- SUMMARY STATS ---
        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe())

        # --- CHART SECTION ---
        st.subheader("📉 Data Visualization")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if numeric_cols:
            col1, col2 = st.columns(2)

            with col1:
                chart_type = st.selectbox("Select chart type:", ["Line", "Bar", "Scatter", "Pie"])
            with col2:
                color = st.color_picker("Pick chart color:", "#00BFFF")

            # --- PIE CHART SELECTIONS ---
            if chart_type == "Pie":
                if categorical_cols and numeric_cols:
                    pie_cat = st.selectbox("Categorical column for slices:", categorical_cols)
                    pie_val = st.selectbox("Numeric column for values:", numeric_cols)
                else:
                    st.warning("⚠️ Pie chart requires at least one categorical and one numeric column.")
            else:
                x_axis = st.selectbox("X-axis", df.columns)
                y_axis = st.selectbox("Y-axis", df.columns)

            # --- GENERATE CHART ---
            if st.button("📊 Generate Chart"):
                if chart_type == "Pie":
                    if categorical_cols and numeric_cols:
                        fig = px.pie(df, names=pie_cat, values=pie_val, title=f"Pie Chart of {pie_cat}")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    if not y_axis:
                        st.warning("Please select at least one Y-axis column.")
                    else:
                        if chart_type == "Line":
                            fig = px.line(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart",
                                          color_discrete_sequence=[color])
                        elif chart_type == "Bar":
                            fig = px.bar(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart",
                                         color_discrete_sequence=[color])
                        else:
                            fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart",
                                             color_discrete_sequence=[color])

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
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Analyzing your data..."):
                sample_data = df.head(50).to_string()
                summary_stats = df.describe().to_string()

                prompt = f"""
                You are a professional data analyst. Write a clear, specific, and insightful summary of this dataset.
                Here are summary statistics of the numeric columns:
                {summary_stats}

                And here are the first 50 rows of the dataset:
                {sample_data}
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

        # --- AI QUESTION-ANSWERING SECTION ---
        st.subheader("❓ Ask Questions About the Dataset")
        user_question = st.text_input("Ask the AI anything about your data:")

        if st.button("🔍 Get Answer"):
            if user_question:
                with st.spinner("Thinking..."):
                    sample_data = df.head(50).to_string()
                    summary_stats = df.describe().to_string()

                    prompt = f"""
                    You are a data expert analyzing a dataset. 
                    Here are summary statistics of the numeric columns:
                    {summary_stats}

                    And here are the first 50 rows of the dataset:
                    {sample_data}

                    The user asked the following question:
                    "{user_question}"

                    Provide a clear, specific, expert answer based ONLY on the dataset provided.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a data analysis assistant."},
                            {"role": "user", "content": prompt}
                        ],
                    )

                    st.subheader("💡 AI Answer")
                    st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
