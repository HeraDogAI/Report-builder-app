import streamlit as st
import pandas as pd
import plotly.express as px
import os
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="AI Report Builder", layout="wide")
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
                if not y_axis:
                    st.warning("Please select at least one Y-axis column.")
                else:
                    if chart_type == "Line":
                        fig = px.line(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart", color_discrete_sequence=[color])
                    elif chart_type == "Bar":
                        fig = px.bar(df, x=x_axis, y=y_axis, title=f"{chart_type} Chart", color_discrete_sequence=[color])
                    else:
                        # For scatter, use only first Y variable
                        fig = px.scatter(df, x=x_axis, y=y_axis[0], title=f"{chart_type} Chart", color_discrete_sequence=[color])

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
                summary = df.describe().to_string()
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

  # --- DOWNLOAD REPORT AS PDF ---
        if ai_summary:
            if st.button("📄 Download Report as PDF"):
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                story.append(Paragraph("AI Report Builder Summary", styles["Title"]))
                story.append(Spacer(1, 12))
                story.append(Paragraph("Dataset Summary Statistics", styles["Heading2"]))
                story.append(Spacer(1, 8))

                # Convert summary stats to table
                stats_data = df.describe().reset_index()
                table_data = [stats_data.columns.tolist()] + stats_data.values.tolist()
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00BFFF")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER')
                ]))
                story.append(table)
                story.append(Spacer(1, 12))

                story.append(Paragraph("AI-Generated Insights", styles["Heading2"]))
                story.append(Spacer(1, 8))
                story.append(Paragraph(ai_summary.replace("\n", "<br/>"), styles["Normal"]))

                doc.build(story)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=buffer,
                    file_name="AI_Report.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
