from flask import Flask, request, jsonify
import pickle
import re
import string

# Create Flask app
app = Flask(__name__)

# Load trained model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Text cleaning function
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Create prediction route
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    
    if "email" not in data:
        return jsonify({"error": "No email provided"}), 400

    email = clean_text(data["email"])
    vector = vectorizer.transform([email])
    prediction = model.predict(vector)[0]

    return jsonify({"predicted_intent": prediction})

# Run server
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
