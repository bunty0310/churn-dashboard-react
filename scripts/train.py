# scripts/train.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import mlflow
import os

# --- Configuration ---
DATA_PATH = 'data/WA_Fn-UseC_-Telco-Customer-Churn.csv'
ARTIFACTS_DIR = 'saved_artifacts'
PREPROCESSOR_FILE = 'preprocessor.joblib'
TARGET_COLUMN = 'Churn'
# Name your experiment in MLflow
MLFLOW_EXPERIMENT_NAME = "Churn_Prediction_App_V1"

# --- MLflow Setup ---
# Set MLflow to save experiment runs in a local folder named 'mlruns'
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

print("--- Training Script Started ---")

# --- Load Data ---
df = pd.read_csv(DATA_PATH)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df.dropna(subset=['TotalCharges'], inplace=True)
df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(lambda x: 1 if x == 'Yes' else 0)

# Drop the identifier column before training
X = df.drop([TARGET_COLUMN, 'customerID'], axis=1)
y = df[TARGET_COLUMN]

# Split data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# --- Load Preprocessor ---
preprocessor = joblib.load(os.path.join(ARTIFACTS_DIR, PREPROCESSOR_FILE))

# --- MLflow Experiment Run ---
# The 'with' block ensures everything within it is logged to a single run
with mlflow.start_run() as run:
    # --- Log Model Parameters ---
    # These are the settings for our RandomForest model
    n_estimators = 150
    max_depth = 10
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)

    # --- Create and Train Model ---
    # We create a final Scikit-learn pipeline that first preprocesses the data,
    # then passes it to the classifier.
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42))])

    print("Training model...")
    model.fit(X_train, y_train)

    # --- Evaluate and Log Metrics ---
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)
    print(f"Model Accuracy on Test Set: {accuracy:.4f}")

    # --- Log the Model ---
    # This is the most important step for deployment. It saves the entire pipeline
    # and registers it in the MLflow Model Registry.
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="churn_model", # Folder name within the run artifacts
        registered_model_name="ChurnPredictorReact" # Name to find it later
    )
    print(f"Model logged successfully. Run ID: {run.info.run_id}")

print("--- Training Script Finished ---")