import streamlit as st
import requests
import re
from supabase import create_client

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Email Intent Classifier", layout="centered")

# ------------------ DARK UI ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

h1 {
    text-align: center;
    color: #00FFD1;
    font-size: 40px;
}

h3 {
    text-align: center;
    color: #bbbbbb;
}

.stTextArea textarea {
    background-color: #1e1e2f;
    color: white;
    border-radius: 12px;
    border: 1px solid #00FFD1;
}

.stButton button {
    background: linear-gradient(90deg, #00FFD1, #00C9FF);
    color: black;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 20px;
}

.result-box {
    background: #1e1e2f;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
    box-shadow: 0 0 10px rgba(0,255,209,0.3);
}

.intent {
    color: #00FFD1;
    font-weight: bold;
}

.confidence {
    color: #FFD700;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Model: Cloud API (Render)")
st.sidebar.write("Database: Supabase")
st.sidebar.write("Version: 4.0")

# ------------------ CONFIG ------------------
API_URL = "https://email-intent-classifier.onrender.com/predict"

SUPABASE_URL = "https:hlktfhghnuohxekeoaqv.supabase.co"
SUPABASE_KEY = "sb_publishable_qR0V7NzXZEo5m_jq5VxW_A_NWyxwVEU"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ FUNCTIONS ------------------
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

# ------------------ HEADER ------------------
st.markdown("<h1>📧 AI Email Intent Classifier</h1>", unsafe_allow_html=True)
st.markdown("<h3>Cloud-powered Email Analysis ⚡</h3>", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ------------------ BUTTONS ------------------
col1, col2 = st.columns(2)
predict_clicked = col1.button("🔍 Predict")
clear_clicked = col2.button("🧹 Clear")

if clear_clicked:
    st.session_state.input_text = ""
    st.rerun()

# ------------------ INPUT ------------------
email_input = st.text_area("Enter email:", key="input_text")

# ------------------ PREDICTION ------------------
if predict_clicked:

    if email_input.strip() != "":

        parts = split_sentences(email_input)

        for part in parts:
            part = part.strip()
            if part == "":
                continue

            try:
                response = requests.post(API_URL, json={"text": part}, timeout=5)
                result = response.json()

                predicted_intent = result.get("prediction", "Error")
                confidence = result.get("confidence", 0)

                # 🔥 SAVE TO SUPABASE
                try:
                    supabase.table("emails").insert({
                        "text": part,
                        "intent": predicted_intent,
                        "confidence": confidence
                    }).execute()
                except:
                    pass  # avoid crash if DB fails

            except:
                predicted_intent = "Error"
                confidence = 0

            st.markdown(f"""
            <div class="result-box">
                <p><b>Text:</b> {part}</p>
                <p><b>Intent:</b> <span class="intent">{predicted_intent}</span></p>
                <p><b>Confidence:</b> <span class="confidence">{confidence:.2f}%</span></p>
                <p>{responses.get(predicted_intent, "")}</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Enter some text")
