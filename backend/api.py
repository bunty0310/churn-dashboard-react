import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os

# Initialize a Flask app
app = Flask(__name__)
# Enable CORS to allow requests from your frontend's domain
CORS(app)

# --- Model Loading ---
MODEL_PATH = "saved_artifacts/churn_model.joblib"

def load_model():
    """Loads the model from the specified path."""
    try:
        print(f"Loading model from {MODEL_PATH}...")
        loaded_model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
        return loaded_model
    except Exception as e:
        print(f"FATAL: Could not load model. Error: {e}")
        return None

model = load_model()

# --- API Endpoints ---
@app.route("/api/predict", methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not available, please check server logs.'}), 503
    try:
        data = request.get_json(force=True)
        df = pd.DataFrame(data, index=[0])
        for col in ['tenure', 'SeniorCitizen']: df[col] = pd.to_numeric(df[col])
        for col in ['MonthlyCharges', 'TotalCharges']: df[col] = pd.to_numeric(df[col])
        
        prediction = model.predict(df)
        return jsonify(churn_prediction=int(prediction[0]))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route("/")
def health_check():
    """A simple health check endpoint."""
    return "Backend API is running!"