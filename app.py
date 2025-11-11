import streamlit as st
import pandas as pd

# ----- TITLE -----
st.title("📊 AI-Powered Report Builder Test")

# ----- INSTRUCTIONS -----
st.write("Upload a CSV file to see a preview and basic summary statistics.")

# ----- FILE UPLOADER -----
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Show preview
    st.subheader("Preview of your data")
    st.dataframe(df.head())

    # Show summary stats
    st.subheader("Summary Statistics")
    st.write(df.describe())
else:
    st.info("📂 No file uploaded yet. Please upload a CSV to see results.")
