import joblib
import pandas as pd
import os

class MLService:
    def __init__(self):
        # We need to go up FOUR directories to reach the root 'retainiq' folder
        # file: backend/app/services/ml_service.py -> backend/app/services -> backend/app -> backend -> root
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Load Churn Models
        self.preprocessor = joblib.load(os.path.join(base_path, "ml/artifacts/preprocessors/preprocessor.joblib"))
        self.churn_model = joblib.load(os.path.join(base_path, "ml/artifacts/models/best_model.joblib"))
        
        # Load Segmentation Models
        self.seg_pipeline = joblib.load(os.path.join(base_path, "ml/artifacts/models/segmentation_pipeline.joblib"))
        self.kmeans_model = joblib.load(os.path.join(base_path, "ml/artifacts/models/kmeans_model.joblib"))
        
        self.cluster_mapping = {
            0: "High Value / Loyal",
            1: "Low Value / Dormant",
            2: "Mid Value / Moderate",
            3: "New / At-Risk"
        }

    def predict(self, customer_data: dict):
        """Single Prediction Method for the Form UI"""
        df = pd.DataFrame([customer_data])
        
        # 1. Churn Prediction
        X_processed = self.preprocessor.transform(df)
        churn_prob = self.churn_model.predict_proba(X_processed)[0][1]
        
        # 2. Segmentation
        seg_features = ['tenure', 'monthly_charges', 'total_charges', 'engagement_score']
        X_seg = df[seg_features]
        X_seg_scaled = self.seg_pipeline.transform(X_seg)
        cluster_id = self.kmeans_model.predict(X_seg_scaled)[0]
        segment_name = self.cluster_mapping[cluster_id]
        
        # Determine Risk Level
        if churn_prob < 0.25: risk = "Low"
        elif churn_prob < 0.50: risk = "Medium"
        elif churn_prob < 0.75: risk = "High"
        else: risk = "Critical"
        
        return {
            "churn_probability": round(float(churn_prob), 4),
            "risk_level": risk,
            "segment": segment_name
        }

    def predict_bulk(self, df: pd.DataFrame):
        """Bulk Prediction Method for CSV Uploads"""
        # 1. Churn Prediction for all rows
        X_processed = self.preprocessor.transform(df)
        churn_probs = self.churn_model.predict_proba(X_processed)[:, 1]
        
        # 2. Segmentation for all rows
        seg_features = ['tenure', 'monthly_charges', 'total_charges', 'engagement_score']
        X_seg = df[seg_features]
        X_seg_scaled = self.seg_pipeline.transform(X_seg)
        cluster_ids = self.kmeans_model.predict(X_seg_scaled)
        
        results = []
        for i in range(len(df)):
            prob = float(churn_probs[i])
            cluster_id = int(cluster_ids[i])
            segment_name = self.cluster_mapping[cluster_id]
            
            if prob < 0.25: risk = "Low"
            elif prob < 0.50: risk = "Medium"
            elif prob < 0.75: risk = "High"
            else: risk = "Critical"
            
            if risk == 'Critical': action = "Immediate Call + 20% Discount"
            elif risk == 'High': action = "Schedule Success Call"
            else: action = "Standard Engagement"
            
            results.append({
                "customer_id": str(df.iloc[i].get('customer_id', f'CUS-{i}')),
                "monthly_charges": float(df.iloc[i].get('monthly_charges', 0)),
                "churn_probability": round(prob, 4),
                "risk_level": risk,
                "segment": segment_name,
                "action": action
            })
        return results
        
ml_service = MLService()