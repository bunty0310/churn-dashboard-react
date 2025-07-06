# scripts/train.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import os

## --- Configuration ---
DATA_PATH = 'data/WA_Fn-UseC_-Telco-Customer-Churn.csv'
ARTIFACTS_DIR = 'saved_artifacts'
PREPROCESSOR_FILE = os.path.join(ARTIFACTS_DIR, 'preprocessor.joblib')
MODEL_FILE = os.path.join(ARTIFACTS_DIR, 'churn_model.joblib') # Path for the final model
TARGET_COLUMN = 'Churn'

print("--- Training Script Started ---")

## --- Load Data and Preprocessor ---
df = pd.read_csv(DATA_PATH)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df.dropna(subset=['TotalCharges'], inplace=True)
df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(lambda x: 1 if x == 'Yes' else 0)
X = df.drop([TARGET_COLUMN, 'customerID'], axis=1)
y = df[TARGET_COLUMN]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
preprocessor = joblib.load(PREPROCESSOR_FILE)

## --- Model Definition ---
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42))
])

## --- Train and Evaluate ---
print("Training model...")
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy on Test Set: {accuracy:.4f}")

## --- NEW: Save the Final Model Directly ---
# This is the crucial change. We save the entire trained pipeline to a single file.
print(f"Saving final model to {MODEL_FILE}")
joblib.dump(model, MODEL_FILE)

print("--- Training Script Finished ---")