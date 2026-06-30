import pandas as pd

# 1. Load the merged data
df = pd.read_csv("Cleaned_Employee_Data.csv")

# 2. Ensure date columns are in datetime format
df['HireDate'] = pd.to_datetime(df['HireDate'])
df['ReviewDate'] = pd.to_datetime(df['ReviewDate'])

# 3. Handle Logical Errors: Remove records where ReviewDate is before HireDate
initial_count = len(df)
df = df[(df['ReviewDate'] >= df['HireDate']) | (df['ReviewDate'].isna())]
removed_errors = initial_count - len(df)
print(f"Removed {removed_errors} records with logical date inconsistencies.")

# 4. Correct Data Types: Convert ratings back to Integers
# Use 'Int64' (nullable integer) to handle the employees who have no review data
performance_metrics = [
    'EnvironmentSatisfaction', 'JobSatisfaction', 'RelationshipSatisfaction',
    'TrainingOpportunitiesWithinYear', 'TrainingOpportunitiesTaken',
    'WorkLifeBalance', 'SelfRating', 'ManagerRating'
]

for col in performance_metrics:
    df[col] = df[col].astype('Int64')

# 5. Final Verification
#Missing Value Check
print("\nMissing Values Summary:")
print(df.isnull().sum())
#Verify Unique Employee Count
print("Unique Employees:", df['EmployeeID'].nunique())
print(f"Final Dataset Shape: {df.shape}")
print("\nColumn Types after correction:")
print(df[performance_metrics].dtypes)

# 6. Save the final polished dataset
df.to_csv("Final_Cleaned_Employee_Data.csv", index=False)
print("\nSuccess: 'Final_Cleaned_Employee_Data.csv' saved.")