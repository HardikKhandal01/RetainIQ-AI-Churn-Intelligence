import pandas as pd

# 1. Load Data
file_path = "ml/data/raw/retainiq_customers.csv"
df = pd.read_csv(file_path)

print("="*50)
print("🔍 RETAINIQ - DATA UNDERSTANDING REPORT")
print("="*50)

# 2. Basic Info
print(f"\n1. Dataset Shape: {df.shape[0]} Rows, {df.shape[1]} Columns")
print("\n2. Column Data Types:")
print(df.dtypes)

# 3. Missing Values
print("\n3. Missing Values Check:")
missing_data = df.isnull().sum()
print(missing_data[missing_data > 0])

# 4. Target Variable (Churn) Distribution
print("\n4. Churn Distribution (Class Imbalance Check):")
churn_counts = df['churn'].value_counts()
churn_percentage = df['churn'].value_counts(normalize=True) * 100
for index, val in churn_counts.items():
    print(f"Class {index} (Churn={'Yes' if index==1 else 'No'}): {val} customers ({churn_percentage[index]:.2f}%)")

print("\n5. Sample Data (First 3 rows):")
print(df.head(3).to_string())
print("="*50)