import streamlit as st
import pandas as pd
from openai import OpenAI

# --- SETUP ---
st.title("🤖 AI-Powered Report Builder")

# Ask user for their OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file and api_key:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # Generate summary statistics
    summary = df.describe().to_string()

    # Display basic stats
    st.subheader("📈 Summary Statistics")
    st.text(summary)

    # --- AI ANALYSIS ---
    if st.button("🧠 Generate AI Summary"):
        with st.spinner("Analyzing your data..."):
            client = OpenAI(api_key=api_key)

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
    st.info("👆 Upload a CSV and enter your API key to get started.")
