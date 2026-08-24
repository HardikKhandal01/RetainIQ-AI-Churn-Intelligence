import pandas as pd
import numpy as np
import os

# Set seed for reproducibility
np.random.seed(42)
num_customers = 10000

print("Generating RetainIQ SaaS Customer Dataset...")

# 1. Basic Features
customer_ids = [f"CUS-{i:06d}" for i in range(1, num_customers + 1)]
tenure = np.random.randint(1, 72, size=num_customers) # 1 to 72 months
monthly_charges = np.random.uniform(20.0, 150.0, size=num_customers)
total_charges = tenure * monthly_charges * np.random.uniform(0.95, 1.05, size=num_customers)

# 2. Categorical Features
contract_options = ['Month-to-month', 'One year', 'Two year']
contract = np.random.choice(contract_options, size=num_customers, p=[0.5, 0.3, 0.2])

usage_frequency = np.random.choice(['Low', 'Medium', 'High'], size=num_customers, p=[0.2, 0.5, 0.3])
support_tickets = np.random.randint(0, 10, size=num_customers)
engagement_score = np.random.randint(1, 100, size=num_customers)
last_activity_days = np.random.randint(0, 60, size=num_customers)

# 3. Create Churn Logic (The hidden pattern ML needs to find)
# We calculate a hidden "churn_risk_score" based on business logic
churn_risk = np.zeros(num_customers)

# Higher risk if Month-to-month
churn_risk += np.where(contract == 'Month-to-month', 0.3, 0.0)
# Higher risk if low usage
churn_risk += np.where(usage_frequency == 'Low', 0.2, 0.0)
# Higher risk if lots of support tickets
churn_risk += (support_tickets * 0.05)
# Higher risk if not active recently
churn_risk += (last_activity_days * 0.005)
# Lower risk if highly engaged
churn_risk -= (engagement_score * 0.002)

# Convert risk score to probability (Sigmoid-like approach for bounding)
churn_prob = 1 / (1 + np.exp(- (churn_risk - 0.5) * 3))

# Generate final Churn labels (1 = Churned, 0 = Retained) based on probabilities
churn = (np.random.rand(num_customers) < churn_prob).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'customer_id': customer_ids,
    'tenure': tenure,
    'monthly_charges': np.round(monthly_charges, 2),
    'total_charges': np.round(total_charges, 2),
    'contract': contract,
    'usage_frequency': usage_frequency,
    'support_tickets': support_tickets,
    'engagement_score': engagement_score,
    'last_activity_days': last_activity_days,
    'churn': churn
})

# Add some realistic missing values to total_charges (to practice handling them)
missing_idx = np.random.choice(df.index, size=15, replace=False)
df.loc[missing_idx, 'total_charges'] = np.nan

# Save to the correct folder
output_dir = "ml/data/raw"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "retainiq_customers.csv")
df.to_csv(output_path, index=False)

print(f"Dataset generated successfully with {len(df)} rows!")
print(f"Saved to: {output_path}")