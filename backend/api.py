# backend/api.py
import mlflow
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
import os

# Initialize a Flask app.
# The key is 'static_folder'. We tell Flask to serve static files from the
# React app's 'build' directory.
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')

# --- Load the ML Model ---
# This must be done once when the application starts.
print("Loading model from MLflow...")
try:
    # We need to tell mlflow where to find the 'mlruns' folder.
    # os.getcwd() gets the current working directory, which will be the root
    # when run from the Docker container.
    mlflow.set_tracking_uri(f"file://{os.getcwd()}/mlruns")
    # Load the latest registered version of our model.
    model = mlflow.pyfunc.load_model("models:/ChurnPredictorReact/latest")
    print("Model loaded successfully.")
except Exception as e:
    print(f"FATAL: Could not load model. Error: {e}")
    model = None

# --- API Endpoint for Predictions ---
@app.route("/api/predict", methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not available, please check server logs.'}), 503

    try:
        # Get the JSON data sent from the React frontend
        data = request.get_json(force=True)
        # Convert it to a pandas DataFrame
        df = pd.DataFrame(data, index=[0])

        # Ensure data types match what the model was trained on
        for col in ['tenure', 'SeniorCitizen']: df[col] = pd.to_numeric(df[col])
        for col in ['MonthlyCharges', 'TotalCharges']: df[col] = pd.to_numeric(df[col])

        # Use the loaded model to make a prediction
        prediction = model.predict(df)
        # Return the prediction as a JSON object
        return jsonify(churn_prediction=int(prediction[0]))
    except Exception as e:
        # Return a detailed error if something goes wrong
        return jsonify({'error': str(e)}), 400

# --- Serve React Frontend ---
# This is a "catch-all" route. If a request doesn't match the '/api/predict' route,
# it will be handled by this function.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # If the path exists as a file in our static folder (e.g., 'static/css/main.css'), serve it.
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    # Otherwise, serve the main 'index.html' file. This allows React Router to handle the URL.
    else:
        return send_from_directory(app.static_folder, 'index.html')