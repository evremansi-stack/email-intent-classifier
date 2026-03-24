import streamlit as st
import requests
import re
import pandas as pd
from supabase import create_client

# ------------------ CONFIG ------------------
API_URL = "https://email-intent-classifier.onrender.com/predict"

SUPABASE_URL = "https://hlktfhghnuohxekeoaqv.supabase.co"
SUPABASE_KEY = "sb_publishable_qR0V7NzXZEo5m_jq5VxW_A_NWyxwVEU"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ PAGE ------------------
st.set_page_config(page_title="Email Intent Classifier", layout="centered")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
h1 { text-align: center; color: #00FFD1; }
.stButton button {
    background: linear-gradient(90deg, #00FFD1, #00C9FF);
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.title("📧 Email Intent Classifier (Cloud AI)")

# ------------------ LOGIN ------------------
st.sidebar.title("🔐 Login")

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

login_btn = st.sidebar.button("Login")
signup_btn = st.sidebar.button("Signup")

user = None

if signup_btn:
    try:
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.sidebar.success("Signup successful!")
    except Exception as e:
        st.sidebar.error(f"Signup Error: {e}")

if login_btn:
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        user = res.user
        st.session_state.user = user
        st.sidebar.success("Logged in!")
    except Exception as e:
        st.sidebar.error(f"Login Error: {e}")

if "user" in st.session_state:
    user = st.session_state.user
    st.sidebar.success(f"Welcome {user.email}")

# ------------------ MAIN APP ------------------
if user:

    def split_sentences(text):
        return re.split(r'[.!?]+| and ', text)

    responses = {
        "Complaint": "⚠️ We are sorry for the inconvenience.",
        "Query": "📩 We will get back to you shortly.",
        "Cancellation": "❌ Cancellation request received.",
        "Order": "🛒 Order request received.",
        "Feedback": "🙏 Thank you for feedback!",
        "Support": "🛠️ Support team will assist.",
        "Spam": "🚫 This is spam."
    }

    st.subheader("Enter Email Text")
    email_input = st.text_area("Type your email here")

    if st.button("🔍 Predict"):

        if email_input.strip() != "":

            parts = split_sentences(email_input)

            for part in parts:
                part = part.strip()
                if part == "":
                    continue

                # ---------------- API CALL ----------------
                try:
                    response = requests.post(API_URL, json={"text": part}, timeout=15)
                    result = response.json()

                    predicted_intent = result.get("prediction", "Error")
                    confidence = result.get("confidence", 0)

                except Exception as e:
                    predicted_intent = "Error"
                    confidence = 0
                    st.error(f"API Error: {e}")

                # ---------------- SAVE TO SUPABASE ----------------
                try:
                    supabase.table("emails").insert({
                        "text": part,
                        "intent": predicted_intent,
                        "confidence": float(confidence),
                        "user_id": user.id
                    }).execute()

                except Exception as e:
                    st.error(f"DB Error: {e}")

                # ---------------- DISPLAY RESULT ----------------
                st.markdown(f"""
                <div style='background:#1e1e2f;padding:15px;border-radius:10px;margin:10px'>
                    <b>Text:</b> {part} <br>
                    <b>Intent:</b> <span style='color:#00FFD1'>{predicted_intent}</span> <br>
                    <b>Confidence:</b> <span style='color:#FFD700'>{confidence:.2f}%</span> <br>
                    {responses.get(predicted_intent, "")}
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("Enter some text")

    # ---------------- DASHBOARD ----------------
    st.markdown("## ☁️ Cloud Dashboard")

    try:
        # Intent summary
        intent_data = supabase.table("intent_summary").select("*").execute()
        df_intent = pd.DataFrame(intent_data.data)

        if not df_intent.empty:
            st.subheader("📊 Intent Distribution")
            st.bar_chart(df_intent.set_index("intent"))

        # Confidence summary
        conf_data = supabase.table("confidence_summary").select("*").execute()
        df_conf = pd.DataFrame(conf_data.data)

        if not df_conf.empty:
            st.subheader("📈 Avg Confidence")
            st.bar_chart(df_conf.set_index("intent"))

        # Daily activity
        daily_data = supabase.table("daily_activity").select("*").execute()
        df_daily = pd.DataFrame(daily_data.data)

        if not df_daily.empty:
            st.subheader("📅 Daily Activity")
            df_daily["day"] = pd.to_datetime(df_daily["day"])
            st.line_chart(df_daily.set_index("day"))

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

else:
    st.warning("🔐 Please login to use the system")
