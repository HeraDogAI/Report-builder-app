import streamlit as st
import pandas as pd
import plotly.express as px
import os
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tempfile

# --- PAGE SETUP ---
st.set_page_config(page_title="Promethix", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- LOAD OPENAI API KEY (FROM ENV OR SECRETS) ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Missing OpenAI API key. Add it to Streamlit secrets or environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

generated_chart_path = None
ai_summary_text = ""

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="latin1")

        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # --- FULL DATASET VIEWER ---
        with st.expander("📄 Open Full Dataset (View Entire Table)"):
            st.dataframe(df)

        # --- SUMMARY STATS ---
        st.subheader("📈 Summary Statistics")
        summary_df = df.describe()
        st.dataframe(summary_df)

        # --- CHART SECTION ---
        st.subheader("📉 Data Visualization")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        all_cols = df.columns.tolist()

        if all_cols:
            col1, col2 = st.columns(2)

            with col1:
                chart_type = st.selectbox("Select chart type:", ["Line", "Bar", "Scatter", "Pie"])

            with col2:
                color = st.color_picker("Pick chart color:", "#00BFFF")

            x_axis = st.selectbox("X-axis", df.columns)
            y_axis = st.selectbox("Y-axis", df.columns)

            if st.button("📊 Generate Chart"):
                if chart_type == "Pie":
                    fig = px.pie(df, names=x_axis, values=y_axis, title="Pie Chart")
                else:
                    if chart_type == "Line":
                        fig = px.line(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
                    elif chart_type == "Bar":
                        fig = px.bar(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
                    else:
                        fig = px.scatter(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])

                fig.update_layout(
                    title_x=0.5,
                    template="plotly_white",
                    paper_bgcolor="#F9FAFB",
                    plot_bgcolor="#F9FAFB"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Save chart image temporarily for PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    fig.write_image(tmpfile.name)
                    generated_chart_path = tmpfile.name

        # --- AI ANALYSIS SECTION ---
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Analyzing your data..."):
                summary = summary_df.to_string()
                prompt = f"""
                You are a professional data analyst. Write a clear, specific, insightful summary of this dataset
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

                ai_summary_text = response.choices[0].message.content

                st.subheader("📝 AI Summary")
                st.write(ai_summary_text)

        # --- PDF DOWNLOAD FEATURE ---
        if st.button("📥 Download PDF Report"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                c = canvas.Canvas(pdf_file.name, pagesize=letter)
                width, height = letter

                # Title
                c.setFont("Helvetica-Bold", 18)
                c.drawString(50, height - 50, "Promethix AI Report")

                # AI Summary Text
                c.setFont("Helvetica", 12)
                text_y = height - 100
                for line in ai_summary_text.split("\n"):
                    c.drawString(50, text_y, line)
                    text_y -= 15

                # Insert chart if available
                if generated_chart_path:
                    c.drawImage(ImageReader(generated_chart_path), 50, 200, width=500, preserveAspectRatio=True)

                c.showPage()
                c.save()

                st.success("PDF report generated!")
                st.download_button(
                    label="📄 Download PDF",
                    data=open(pdf_file.name, "rb").read(),
                    file_name="report.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
