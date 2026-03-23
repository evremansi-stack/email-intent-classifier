import streamlit as st
import requests
import re
import string

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
    transition: 0.3s;
}

.stButton button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
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

.suggestion {
    background: #2c2c3e;
    padding: 10px;
    border-radius: 10px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Model: Cloud API (Render)")
st.sidebar.write("Version: 3.0")
st.sidebar.write("Developer: You 😎")

# ------------------ API URL ------------------
API_URL = "https://email-intent-classifier.onrender.com/predict"

# ------------------ SPLIT SENTENCES ------------------
def split_sentences(text):
    return re.split(r'[.!?]+| and ', text)

# ------------------ RESPONSES ------------------
responses = {
    "Complaint": "⚠️ We are sorry for the inconvenience. Our team will resolve this soon.",
    "Query": "📩 We will get back to you shortly.",
    "Cancellation": "❌ Your cancellation request is being processed.",
    "Order": "🛒 Your order request has been received.",
    "Feedback": "🙏 Thank you for your valuable feedback!",
    "Support": "🛠️ Our support team will assist you shortly.",
    "Spam": "🚫 This message is flagged as spam."
}

# ------------------ HEADER ------------------
st.markdown("<h1>📧 AI Email Intent Classifier</h1>", unsafe_allow_html=True)
st.markdown("<h3>Understand emails smarter ⚡</h3>", unsafe_allow_html=True)

# ------------------ SESSION INIT ------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ------------------ BUTTONS ------------------
col1, col2 = st.columns(2)

predict_clicked = col1.button("🔍 Predict Intent")
clear_clicked = col2.button("🧹 Clear")

# ------------------ CLEAR LOGIC ------------------
if clear_clicked:
    st.session_state.input_text = ""
    st.rerun()

# ------------------ INPUT BOX ------------------
email_input = st.text_area(
    "✉️ Enter your email text here:",
    key="input_text"
)

# ------------------ PREDICTION ------------------
if predict_clicked:

    if email_input.strip() != "":

        parts = split_sentences(email_input)

        st.markdown("## 📊 Detected Intents")

        for part in parts:
            part = part.strip()
            if part == "":
                continue

            try:
                response = requests.post(
                    API_URL,
                    json={"text": part},
                    timeout=5
                )

                result = response.json()

                predicted_intent = result.get("prediction", "Error")
                confidence = result.get("confidence", 0)

            except:
                predicted_intent = "Error"
                confidence = 0

            st.markdown(f"""
            <div class="result-box">
                <p><b>📝 Text:</b> {part}</p>
                <p><b>🎯 Intent:</b> <span class="intent">{predicted_intent}</span></p>
                <p><b>📈 Confidence:</b> <span class="confidence">{confidence:.2f}%</span></p>
                <div class="suggestion">
                    💡 {responses.get(predicted_intent, "No suggestion available")}
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter some email text.")
