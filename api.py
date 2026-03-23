from flask import Flask, request, jsonify
import pickle
import os

# ------------------ INIT APP ------------------
app = Flask(__name__)

# ------------------ LOAD MODEL ------------------
try:
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
except Exception as e:
    print("Error loading model:", e)

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

        # Transform input
        vect = vectorizer.transform([text])

        # Predict
        prediction = model.predict(vect)[0]
        confidence = max(model.predict_proba(vect)[0]) * 100

        return jsonify({
            "prediction": str(prediction),
            "confidence": round(float(confidence), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ RUN APP (RENDER FIX) ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port)
