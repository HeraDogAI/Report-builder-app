import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime, timedelta
from openai import OpenAI

# -------------------------
# APP + API SETUP
# -------------------------
st.set_page_config(page_title="Promethix", layout="wide")
st.title("🤖 Promethix – AI-Powered Report Builder")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Missing OpenAI API key. Add it to Streamlit secrets or environment variables.")
    st.stop()

client = OpenAI(api_key=api_key)

# -------------------------
# PAYWALL SETTINGS
# -------------------------
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/00w5kCbeq4TMces6Ok9MY00"
PAID_USERS = ["customer1@gmail.com"]  # Add real customer emails here

st.markdown(
    """
<script>
let trial = localStorage.getItem("trial_start");
if (!trial) {
    localStorage.setItem("trial_start", new Date().toISOString());
}
</script>
""",
    unsafe_allow_html=True
)

# Read trial start date from browser local storage
trial_start = st.session_state.get("trial_start", None)

if trial_start is None:
    trial_start = datetime.utcnow()
    st.session_state["trial_start"] = trial_start

if isinstance(trial_start, str):
    trial_start = datetime.fromisoformat(trial_start)

trial_end = trial_start + timedelta(days=14)
days_left = (trial_end - datetime.utcnow()).days

# -------------------------
# LOGIN / EMAIL FOR PAYWALL
# -------------------------

user_email = st.text_input("Enter your email to continue (required for trial):")

if user_email:
    if user_email in PAID_USERS:
        st.success("✅ Paid user detected — full access unlocked!")
    else:
        if datetime.utcnow() > trial_end:
            st.error("⛔ Your free trial has expired.")
            st.markdown(
                f"<a href='{STRIPE_CHECKOUT_URL}' target='_blank'><button style='padding:10px 20px; font-size:18px;'>Upgrade for Full Access</button></a>",
                unsafe_allow_html=True,
            )
            st.stop()
        else:
            st.info(f"⏳ Free trial active — **{days_left} days remaining**.")
else:
    st.warning("Please enter your email to begin your free 14-day trial.")
    st.stop()

# -------------------------
# MAIN APP CONTENT (UNLOCKED)
# -------------------------

uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="latin1")

        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        with st.expander("📄 View Full Dataset"):
            st.dataframe(df)

        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe())

        # -------------------------
        # CHARTING
        # -------------------------
        st.subheader("📉 Data Visualization")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        col1, col2 = st.columns(2)

        with col1:
            chart_type = st.selectbox("Select chart type:", ["Line", "Bar", "Scatter", "Pie"])
        with col2:
            color = st.color_picker("Pick chart color:", "#00BFFF")

        if chart_type == "Pie":
            if categorical_cols and numeric_cols:
                pie_cat = st.selectbox("Pie categories:", categorical_cols)
                pie_val = st.selectbox("Pie values:", numeric_cols)
            else:
                st.warning("Pie chart requires 1 categorical + 1 numeric column.")
        else:
            x_axis = st.selectbox("X-axis", df.columns)
            y_axis = st.selectbox("Y-axis", df.columns)

        if st.button("📊 Generate Chart"):
            if chart_type == "Pie":
                fig = px.pie(df, names=pie_cat, values=pie_val)
            elif chart_type == "Line":
                fig = px.line(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
            elif chart_type == "Bar":
                fig = px.bar(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
            else:
                fig = px.scatter(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])

            fig.update_layout(template="plotly_white", title_x=0.5)
            st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # AI SUMMARY
        # -------------------------
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Analyzing your data..."):
                prompt = f"""
                You are a professional data analyst. Provide a clear, insightful summary based on:

                Summary statistics:
                {df.describe().to_string()}

                Sample data:
                {df.head(50).to_string()}
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

        # -------------------------
        # ASK-AI ABOUT DATA
        # -------------------------
        st.subheader("❓ Ask AI About the Dataset")

        question = st.text_input("Ask a question about your data:")
        if st.button("🔍 Get Answer"):
            if question:
                with st.spinner("Thinking..."):
                    prompt = f"""
                    Dataset summary:
                    {df.describe().to_string()}

                    First 50 rows:
                    {df.head(50).to_string()}

                    User question: {question}
                    Provide a concise, dataset-based answer.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a data expert."},
                            {"role": "user", "content": prompt}
                        ],
                    )

                    st.subheader("💡 AI Answer")
                    st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error loading file: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
