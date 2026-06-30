import pandas as pd
from sklearn.utils import resample

# 1. Load the enriched dataset
df = pd.read_csv("Enriched_Employee_Data.csv")

# 2. Pre-processing: Drop non-numeric identifiers and handle nulls
# drop IDs and dates that can't be used in math models directly
cols_to_drop = ['EmployeeID', 'FirstName', 'LastName', 'PerformanceID', 'HireDate', 'ReviewDate', 'Attrition']
df_model = df.drop(columns=cols_to_drop)

# Fill gaps in performance data for employees who haven't had a review yet
df_model['TenureAtReview'] = df_model['TenureAtReview'].fillna(df_model['TenureAtReview'].median())
df_model['AvgSatisfaction'] = df_model['AvgSatisfaction'].fillna(df_model['AvgSatisfaction'].median())
df_model['PerformanceGap'] = df_model['PerformanceGap'].fillna(0)

# Convert categorical text (Department, JobRole, etc.) into numbers (One-Hot Encoding)
df_model = pd.get_dummies(df_model, drop_first=True)

# 3. Separate the majority (No) and minority (Yes) classes
df_majority = df_model[df_model.AttritionNumeric == 0]
df_minority = df_model[df_model.AttritionNumeric == 1]

print(f"Original Count - Stayed: {len(df_majority)}, Left: {len(df_minority)}")

# 4. Upsample Minority Class
# randomly duplicate 'Yes' cases until we have 1,183 of them
df_minority_upsampled = resample(df_minority, 
                                 replace=True,     # Sample with replacement
                                 n_samples=len(df_majority),    # Match majority class size
                                 random_state=42) 

# 5. Combine back into one balanced dataframe
df_balanced = pd.concat([df_majority, df_minority_upsampled])

# 6. Final check and save
print("New Balanced Counts:")
print(df_balanced.AttritionNumeric.value_counts())

df_balanced.to_csv("Balanced_Employee_Data.csv", index=False)
print("\nSuccess: 'Balanced_Employee_Data.csv' saved.")