import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans

print("="*50)
print("📊 RETAINIQ - CUSTOMER SEGMENTATION PHASE")
print("="*50)

# 1. Load Raw Data
print("Loading raw customer data...")
df = pd.read_csv("ml/data/raw/retainiq_customers.csv")

# 2. Select Features for Segmentation
# Hum customers ko unki 'Value' aur 'Engagement' par segment karenge
segmentation_features = ['tenure', 'monthly_charges', 'total_charges', 'engagement_score']
X_seg = df[segmentation_features].copy()

# 3. Preprocessing Pipeline for Clustering
print("Preprocessing data for clustering (Imputing & Scaling)...")
seg_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])
X_seg_scaled = seg_pipeline.fit_transform(X_seg)

# 4. K-Means Clustering (k=4)
print("Applying K-Means Clustering (k=4 segments)...")
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_seg_scaled)

# 5. Business Logic: Mapping Clusters to Names
# Humne in 4 clusters ko business friendly names diye hain
cluster_mapping = {
    0: "High Value / Loyal",
    1: "Low Value / Dormant",
    2: "Mid Value / Moderate",
    3: "New / At-Risk"
}
df['segment_name'] = df['cluster'].map(cluster_mapping)

# 6. Save the Segmentation Models and Data
print("Saving segmentation models and updated dataset...")
os.makedirs("ml/artifacts/models", exist_ok=True)
joblib.dump(seg_pipeline, "ml/artifacts/models/segmentation_pipeline.joblib")
joblib.dump(kmeans, "ml/artifacts/models/kmeans_model.joblib")

# Hum is segmented data ko save kar lenge taaki API aur UI me use kar sakein
os.makedirs("ml/data/processed", exist_ok=True)
df.to_csv("ml/data/processed/segmented_customers.csv", index=False)

# 7. Print Summary
print("\n📈 Customer Segmentation Summary:")
segment_counts = df['segment_name'].value_counts()
for name, count in segment_counts.items():
    print(f"- {name}: {count} customers")

print("\n✅ Segmentation Phase Complete! Data saved to 'ml/data/processed/segmented_customers.csv'")
print("="*50)