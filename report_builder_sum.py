import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import datetime
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="Promethix", layout="wide")
st.title("🤖 AI-Powered Report Builder")

# --- LOAD OPENAI API KEY ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("⚠️ Missing OpenAI API Key.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- USAGE LIMIT SYSTEM (FREE USERS) ---
if "free_uses" not in st.session_state:
    st.session_state.free_uses = 0

FREE_LIMIT = 3  # number of free AI uses allowed

def check_usage():
    """Blocks AI features once free limit is hit."""
    if not st.session_state.get("access_granted", False):
        if st.session_state.free_uses >= FREE_LIMIT:
            st.warning("🔒 You've reached your free AI usage limit.")
            st.info("Start your 14-day free trial to continue using AI features.")
            paywall()
            st.stop()

def record_ai_use():
    """Count each AI usage."""
    st.session_state.free_uses += 1


# --- TRIAL + PAYWALL SYSTEM ---
STRIPE_CHECKOUT_URL = "https://buy.stripe.com/00w5kCbeq4TMces6Ok9MY00"

# Load stored trials from secrets
try:
    initial_trial_data = json.loads(st.secrets["TRIAL_START_DATES"])
except:
    initial_trial_data = {}

if "trial_data" not in st.session_state:
    st.session_state.trial_data = initial_trial_data

# Track usage WITHOUT email first
if "user_id" not in st.session_state:
    st.session_state.user_id = f"anon_{datetime.datetime.utcnow().timestamp()}"

user_id = st.session_state.user_id

# If user has no existing trial, create one
if user_id not in st.session_state.trial_data:
    st.session_state.trial_data[user_id] = {
        "start": str(datetime.date.today())
    }

start_date = datetime.date.fromisoformat(st.session_state.trial_data[user_id]["start"])
days_used = (datetime.date.today() - start_date).days
days_left = 14 - days_used

def show_paywall():
    """Display after user hits limit OR after trial ends."""
    st.error("⛔ Your 3 free tries have expired.")

    st.markdown("### 💳 Try Promethix FREE for 14 Days!")
    st.markdown(
        f"""
        <a href="{STRIPE_CHECKOUT_URL}" target="_blank">
            <button style="
                padding:15px;
                font-size:18px;
                background:#0066ff;
                color:white;
                border-radius:8px;
                border:none;
                cursor:pointer;
                width: 100%;
            ">
                Upgrade via Stripe — $9.99/month
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.info("Reload the page after purchase to unlock access.")
    st.stop()

# If trial expired → paywall
if days_used > 14:
    show_paywall()

# If usage hits limit → stop AI features
def check_usage():
    if st.session_state.free_uses >= FREE_LIMIT:
        st.warning("🔒 You've reached your 3 free AI uses.")
        st.info(f"Your 14-day trial has {days_left} days left.")
        show_paywall()

def record_ai_use():
    st.session_state.free_uses += 1

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="latin1")

        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # Full dataset
        with st.expander("📄 Full Dataset"):
            st.dataframe(df)

        # Summary statistics
        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe())

        # --- CHARTS ---
        st.subheader("📉 Data Visualization")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        if numeric_cols:
            col1, col2 = st.columns(2)

            with col1:
                chart_type = st.selectbox("Chart Type:", ["Line", "Bar", "Scatter", "Pie"])
            with col2:
                color = st.color_picker("Chart Color:", "#00BFFF")

            if chart_type == "Pie":
                pie_cat = st.selectbox("Categorical Column:", categorical_cols)
                pie_val = st.selectbox("Numeric Column:", numeric_cols)
            else:
                x_axis = st.selectbox("X Axis:", df.columns)
                y_axis = st.selectbox("Y Axis:", df.columns)

            if st.button("📊 Generate Chart"):
                if chart_type == "Pie":
                    fig = px.pie(df, names=pie_cat, values=pie_val, title=f"{pie_cat} Breakdown")
                elif chart_type == "Line":
                    fig = px.line(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
                elif chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])
                else:
                    fig = px.scatter(df, x=x_axis, y=y_axis, color_discrete_sequence=[color])

                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        # --- AI SUMMARY ---
        st.subheader("🧠 AI Summary")

        check_usage()

        if st.button("Generate AI Summary"):
            record_ai_use()
            with st.spinner("Analyzing..."):
                summary_stats = df.describe().to_string()
                sample_data = df.head(50).to_string()

                prompt = f"""
                Analyze the dataset using the summary statistics:
                {summary_stats}

                Here are sample rows:
                {sample_data}

                Write an expert summary with insights and trends.
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a data analyst."},
                        {"role": "user", "content": prompt}
                    ],
                )

                st.write(response.choices[0].message.content)

        # --- AI QUESTION SECTION ---
        st.subheader("❓ Ask AI a Question About Your Data")

        user_question = st.text_input("Your question:")

        check_usage()

        if st.button("Get Answer"):
            record_ai_use()
            with st.spinner("Thinking..."):
                summary_stats = df.describe().to_string()
                sample_data = df.head(50).to_string()

                prompt = f"""
                Dataset summary:
                {summary_stats}

                Sample data:
                {sample_data}

                User question:
                {user_question}

                Provide a clear, accurate answer.
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a data analyst."},
                        {"role": "user", "content": prompt}
                    ],
                )

                st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("👆 Upload a CSV to begin.")
