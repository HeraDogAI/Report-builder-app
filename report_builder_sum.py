import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# --- APP SETUP ---
st.set_page_config(page_title="AI Report Builder", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- GET OPENAI API KEY FROM ENVIRONMENT ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ OpenAI API key not found. Set OPENAI_API_KEY in Streamlit secrets or environment variables.")
    st.stop()

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    # --- READ DATA ---
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # --- SUMMARY STATS ---
    st.subheader("📈 Summary Statistics")
    summary = df.describe().to_string()
    st.text(summary)

    # --- AI ANALYSIS ---
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
