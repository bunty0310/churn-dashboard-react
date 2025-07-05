# scripts/preprocess.py
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib
import os

# --- Configuration ---
DATA_PATH = 'data/WA_Fn-UseC_-Telco-Customer-Churn.csv'
ARTIFACTS_DIR = 'saved_artifacts' # Directory to save our output
PREPROCESSOR_FILE = 'preprocessor.joblib'
TARGET_COLUMN = 'Churn'

# Create the directory if it doesn't exist
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
print("--- Preprocessing Script Started ---")

# --- Load and Clean Data ---
df = pd.read_csv(DATA_PATH)
# Convert 'TotalCharges' to numbers, forcing errors into 'NaN' (Not a Number)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
# Drop rows with missing 'TotalCharges'
df.dropna(subset=['TotalCharges'], inplace=True)
# Convert the target 'Churn' column to 0s and 1s
df[TARGET_COLUMN] = df[TARGET_COLUMN].apply(lambda x: 1 if x == 'Yes' else 0)

# Separate features (X) from the target (y)
X = df.drop(TARGET_COLUMN, axis=1)

# --- Define Feature Types ---
numerical_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object']).columns.tolist()
# customerID is an identifier, not a feature, so we remove it
if 'customerID' in categorical_features:
    categorical_features.remove('customerID')

# --- Create Transformation Pipelines ---
# For numerical features, we first fill missing values (impute) with the median,
# then scale them to have a mean of 0 and standard deviation of 1.
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])

# For categorical features, we fill missing values with the most frequent value,
# then convert each category into a new column of 0s and 1s (one-hot encoding).
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# --- Combine Transformers ---
# ColumnTransformer applies the correct pipeline to the correct columns.
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)],
    remainder='drop') # Drop any columns that weren't specified

# --- Save the Preprocessor Object ---
# We save this single object which contains all our preprocessing logic.
preprocessor_path = os.path.join(ARTIFACTS_DIR, PREPROCESSOR_FILE)
joblib.dump(preprocessor, preprocessor_path)

print(f"Preprocessing logic saved to {preprocessor_path}")
print("--- Preprocessing Script Finished ---")