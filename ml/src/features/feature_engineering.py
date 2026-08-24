import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

print("Starting Feature Engineering...")

# 1. Load Data
df = pd.read_csv("ml/data/raw/retainiq_customers.csv")

# 2. Separate Features and Target
X = df.drop(columns=['customer_id', 'churn'])
y = df['churn']

# 3. Define Columns
numeric_features = ['tenure', 'monthly_charges', 'total_charges', 'support_tickets', 'engagement_score', 'last_activity_days']
categorical_features = ['contract', 'usage_frequency']

# 4. Create Preprocessing Pipelines
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# 5. Train-Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 6. Fit and Transform Data
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# 7. Get Feature Names for later interpretation (SHAP)
cat_feature_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_features)
all_feature_names = numeric_features + list(cat_feature_names)

# Convert back to DataFrame for easier handling later
X_train_df = pd.DataFrame(X_train_processed, columns=all_feature_names)
X_test_df = pd.DataFrame(X_test_processed, columns=all_feature_names)

# 8. Save Processed Data & Preprocessor
os.makedirs("ml/data/processed", exist_ok=True)
X_train_df.to_csv("ml/data/processed/X_train.csv", index=False)
X_test_df.to_csv("ml/data/processed/X_test.csv", index=False)
y_train.to_csv("ml/data/processed/y_train.csv", index=False)
y_test.to_csv("ml/data/processed/y_test.csv", index=False)

os.makedirs("ml/artifacts/preprocessors", exist_ok=True)
joblib.dump(preprocessor, "ml/artifacts/preprocessors/preprocessor.joblib")

print(f"Feature Engineering Complete!")
print(f"Training set shape: {X_train_df.shape}")
print(f"Test set shape: {X_test_df.shape}")
print("Processed data and preprocessor saved successfully.")