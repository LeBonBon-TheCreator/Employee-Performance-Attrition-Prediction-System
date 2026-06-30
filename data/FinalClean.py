import pandas as pd

# Load the data
df = pd.read_csv("Balanced_Employee_Data.csv")

# Drop the columns that still contain nulls
cols_with_nulls = df.columns[df.isnull().any()].tolist()
df = df.drop(columns=cols_with_nulls)

# This makes the data slightly more compatible across all ML libraries
# Convert Boolean (True/False) to Integer (1/0)
bool_cols = df.select_dtypes(include='bool').columns
df[bool_cols] = df[bool_cols].astype(int)

# 3. Save as the ready-to-use version
df.to_csv("Balanced_Employee_Data.csv", index=False)
print("Saved as 'Balanced_Employee_Data.csv'.")