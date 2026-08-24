import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

print("="*50)
print("🧠 RETAINIQ - SHAP EXPLAINABILITY PHASE")
print("="*50)

# 1. Load the Best Model and Test Data
print("Loading best model and test data...")
best_model = joblib.load("ml/artifacts/models/best_model.joblib")
X_test = pd.read_csv("ml/data/processed/X_test.csv")

# 2. Initialize SHAP Explainer
print("Calculating SHAP values (this takes a few seconds)...")
# We use a model-agnostic explainer and take a sample of 500 rows to make it fast
explainer = shap.Explainer(best_model.predict, X_test[:500]) 
shap_values = explainer(X_test[:500])

# 3. Save Global Feature Importance Plot (Overall Business Insights)
print("Generating Global Feature Importance (Summary Plot)...")
os.makedirs("ml/reports/figures", exist_ok=True)

plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test[:500], show=False)
plt.savefig("ml/reports/figures/shap_summary.png", bbox_inches='tight')
plt.close()

# 4. Local Explainability (Why is ONE specific customer churning?)
print("\n🔍 Local Explanation for a Single Customer (Customer Index 0):")
sample_idx = 0
sample_data = X_test.iloc[sample_idx]
sample_shap = shap_values[sample_idx]

# Combine feature names, actual values, and their SHAP impact
impacts = pd.DataFrame({
    'Feature': X_test.columns,
    'Actual Value': sample_data.values,
    'SHAP Impact': sample_shap.values
})

# Sort by the absolute impact to find the top drivers
impacts['Abs Impact'] = impacts['SHAP Impact'].abs()
impacts = impacts.sort_values(by='Abs Impact', ascending=False).drop(columns=['Abs Impact'])

print("\nTop 5 factors driving this specific customer's prediction:")
print(impacts.head(5).to_string(index=False))

print("\n✅ Explainability Phase Complete! Global plot saved to 'ml/reports/figures/shap_summary.png'")
print("="*50)