from flask import Flask, request, jsonify
import pickle
import re
import string
import os

app = Flask(__name__)

# ------------------ LOAD MODEL ------------------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ------------------ CLEAN TEXT ------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

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
    elif any(word in text for word in ["win", "lottery", "cashback", "prize", "offer", "free", "click"]):
        return "Spam"

    return None

# ------------------ HOME ROUTE ------------------
@app.route("/")
def home():
    return "🚀 Email Intent API is running!"

# ------------------ PREDICT ROUTE ------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "No input text provided"}), 400

        text = data["text"]

        override = keyword_override(text)

        if override:
            prediction = override
            confidence = 95.0
        else:
            cleaned = clean_text(text)
            vec = vectorizer.transform([cleaned])

            prediction = model.predict(vec)[0]
            confidence = float(max(model.predict_proba(vec)[0]) * 100)

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# ------------------ RUN APP (RENDER FIX) ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
