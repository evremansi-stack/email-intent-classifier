import streamlit as st
import pickle
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
st.sidebar.write("Model: Logistic Regression")
st.sidebar.write("Version: 2.0")
st.sidebar.write("Developer: You 😎")

# ------------------ LOAD MODEL ------------------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ------------------ CLEAN TEXT ------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# ------------------ SPLIT SENTENCES (NO NLTK) ------------------
def split_sentences(text):
    return re.split(r'[.!?]+| and ', text)

# ------------------ KEYWORD OVERRIDE ------------------
def keyword_override(text):
    text = text.lower()

    if any(word in text for word in ["refund", "not working", "defective", "bad", "damage"]):
        return "Complaint"
    elif "cancel" in text:
        return "Cancellation"
    elif any(word in text for word in ["order", "buy", "purchase"]):
        return "Order"
    elif any(word in text for word in ["thank", "love", "great", "good", "awesome"]):
        return "Feedback"
    elif any(word in text for word in ["help", "support", "issue"]):
        return "Support"
    
    return None

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

# ------------------ INPUT WITH SESSION ------------------
# ------------------ SESSION INIT ------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ------------------ BUTTONS ------------------
col1, col2 = st.columns(2)

predict_clicked = col1.button("🔍 Predict Intent")
clear_clicked = col2.button("🧹 Clear")

# ------------------ CLEAR LOGIC (BEFORE INPUT BOX) ------------------
if clear_clicked:
    st.session_state.input_text = ""

# ------------------ INPUT BOX ------------------
email_input = st.text_area(
    "✉️ Enter your email text here:",
    key="input_text"
)

# ------------------ CLEAR FUNCTION ------------------
if clear_clicked:
    st.session_state.input_text = ""
    st.rerun()

# ------------------ PREDICTION ------------------
if predict_clicked:

    if email_input.strip() != "":

        parts = split_sentences(email_input)

        st.markdown("## 📊 Detected Intents")

        for part in parts:
            part = part.strip()
            if part == "":
                continue

            override = keyword_override(part)

            if override:
                predicted_intent = override
                confidence = 95.0
            else:
                cleaned = clean_text(part)
                email_vector = vectorizer.transform([cleaned])

                prediction = model.predict(email_vector)
                probs = model.predict_proba(email_vector)

                predicted_intent = prediction[0]
                confidence = max(probs[0]) * 100

            st.markdown(f"""
            <div class="result-box">
                <p><b>📝 Text:</b> {part}</p>
                <p><b>🎯 Intent:</b> <span class="intent">{predicted_intent}</span></p>
                <p><b>📈 Confidence:</b> <span class="confidence">{confidence:.2f}%</span></p>
                <div class="suggestion">
                    💡 {responses[predicted_intent]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter some email text.")