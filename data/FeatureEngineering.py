import pandas as pd
import numpy as np

# 1. Load the latest cleaned data
df = pd.read_csv("Final_Cleaned_Employee_Data.csv")

# Ensure date columns are recognized as datetime
df['HireDate'] = pd.to_datetime(df['HireDate'])
df['ReviewDate'] = pd.to_datetime(df['ReviewDate'])

# 2. Tenure at Review (Years)
# Calculates how long the employee had been at the company when the review took place
df['TenureAtReview'] = (df['ReviewDate'] - df['HireDate']).dt.days / 365.25

# 3. Average Satisfaction Score
# Aggregates Environment, Job, and Relationship satisfaction into one holistic metric
satisfaction_cols = ['EnvironmentSatisfaction', 'JobSatisfaction', 'RelationshipSatisfaction']
df['AvgSatisfaction'] = df[satisfaction_cols].mean(axis=1)

# 4. Performance Gap
# Difference between SelfRating and ManagerRating (Positive = overconfident, Negative = modest)
df['PerformanceGap'] = df['SelfRating'] - df['ManagerRating']

# 5. Attrition Numeric
# Converts 'Yes'/'No' to 1/0 for use in mathematical models and correlation matrices
df['AttritionNumeric'] = df['Attrition'].map({'Yes': 1, 'No': 0})

# 6. Age Groups
# Binning ages into logical life stages
bins = [18, 30, 40, 50, 65]
labels = ['18-29', '30-39', '40-49', '50+']
df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)

# 7. Salary Tier
# Divides employees into four equal quartiles based on their salary
df['SalaryTier'] = pd.qcut(df['Salary'], q=4, labels=['Low', 'Medium', 'High', 'Executive'])

# 8. Save the final enriched dataset
df.to_csv("Enriched_Employee_Data.csv", index=False)

print(f"Feature engineering complete. New shape: {df.shape}")
print("Sample of engineered features:")
print(df[['EmployeeID', 'TenureAtReview', 'PerformanceGap', 'SalaryTier']].head())