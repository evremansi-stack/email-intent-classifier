import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv("email_intent_dataset.csv")

X = df['text']
y = df['intent']

# Better vectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2))  # BIG improvement
X_vec = vectorizer.fit_transform(X)

# Split
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

# Better model
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Accuracy check
print("Accuracy:", model.score(X_test, y_test))

# Save
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ Model retrained successfully!")