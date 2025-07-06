# backend/api.py
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
import joblib
import os

## --- App & Model Loading ---
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')

# Path to the model file inside the container
MODEL_PATH = "/app/saved_artifacts/churn_model.joblib"

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

## --- API Endpoints ---
@app.route("/api/predict", methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not available'}), 503
    try:
        data = request.get_json(force=True)
        df = pd.DataFrame(data, index=[0])
        for col in ['tenure', 'SeniorCitizen']: df[col] = pd.to_numeric(df[col])
        for col in ['MonthlyCharges', 'TotalCharges']: df[col] = pd.to_numeric(df[col])
        
        prediction = model.predict(df)
        return jsonify(churn_prediction=int(prediction[0]))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

## --- Serve React Frontend ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')