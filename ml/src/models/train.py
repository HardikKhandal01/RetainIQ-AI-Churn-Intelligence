import pandas as pd
import os
import joblib
import json
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

print("="*50)
print("🚀 RETAINIQ - MODEL TRAINING PHASE")
print("="*50)

# 1. Load Processed Data
print("Loading processed data...")
X_train = pd.read_csv("ml/data/processed/X_train.csv")
X_test = pd.read_csv("ml/data/processed/X_test.csv")
y_train = pd.read_csv("ml/data/processed/y_train.csv").values.ravel()
y_test = pd.read_csv("ml/data/processed/y_test.csv").values.ravel()

# 2. Initialize Models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
    "LightGBM": LGBMClassifier(random_state=42, verbose=-1)
}

results = {}
best_model_name = None
best_f1_score = 0
best_model = None

# Ensure directories exist
os.makedirs("ml/artifacts/models", exist_ok=True)
os.makedirs("ml/reports", exist_ok=True)

# 3. Train and Evaluate Each Model
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    
    # Store Metrics
    results[name] = {
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1_Score": round(f1, 4),
        "ROC_AUC": round(roc_auc, 4)
    }
    
    # Save individual model
    filename = name.replace(" ", "_").lower()
    joblib.dump(model, f"ml/artifacts/models/{filename}.joblib")
    
    # Find the best model (optimizing for F1 Score to balance Precision & Recall)
    if f1 > best_f1_score:
        best_f1_score = f1
        best_model_name = name
        best_model = model

# 4. Save Best Model and Report
print(f"\n🏆 Best Model: {best_model_name} (F1 Score: {best_f1_score:.4f})")
joblib.dump(best_model, "ml/artifacts/models/best_model.joblib")

with open("ml/reports/model_metrics.json", "w") as f:
    json.dump(results, f, indent=4)

print("\n📊 Model Comparison Table:")
metrics_df = pd.DataFrame(results).T
print(metrics_df.to_string())
print("\n✅ Training Complete! Artifacts saved to 'ml/artifacts/models/'")
print("="*50)