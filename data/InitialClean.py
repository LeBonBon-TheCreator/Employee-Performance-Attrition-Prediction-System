import pandas as pd
import re

# Load datasets
employee_df = pd.read_csv("Employee.csv")
performance_df = pd.read_csv("PerformanceRating.csv")

print("--- Step 0: Initial Data Load ---")
print(f"Employee Data Shape: {employee_df.shape}")
print(f"Performance Data Shape: {performance_df.shape}")

# 1. Standardize Column Names
print("\n--- Step 1: Cleaning Column Names ---")
def clean_column_names(df):
    # Removes special characters and spaces from column headers
    df.columns = [re.sub(r'\W+', '', col) for col in df.columns]
    return df

employee_df = clean_column_names(employee_df)
performance_df = clean_column_names(performance_df)
print(f"Employee Columns: {employee_df.columns.tolist()[:5]}...") 
print(f"Performance Columns: {performance_df.columns.tolist()[:5]}...")

# 2. Check and Remove Duplicates
print("\n--- Step 2: Removing Duplicates ---")
print(f"Employee Duplicates before: {employee_df.duplicated().sum()}")
employee_df = employee_df.drop_duplicates()
print(f"Employee Duplicates after: {employee_df.duplicated().sum()}")

print(f"Performance Duplicates before: {performance_df.duplicated().sum()}")
performance_df = performance_df.drop_duplicates()
print(f"Performance Duplicates after: {performance_df.duplicated().sum()}")

# 3. Date Conversion
print("\n--- Step 3: Datetime Conversion ---")
employee_df['HireDate'] = pd.to_datetime(employee_df['HireDate'], errors='coerce')
performance_df['ReviewDate'] = pd.to_datetime(performance_df['ReviewDate'], errors='coerce')
print(f"Employee HireDate Dtype: {employee_df['HireDate'].dtype}")
print(f"Performance ReviewDate Dtype: {performance_df['ReviewDate'].dtype}")
print(f"Invalid dates (NaT) in HireDate: {employee_df['HireDate'].isna().sum()}")

# 4. Standardize Categorical Data 
print("\n--- Step 4: Stripping Whitespace ---")
def strip_whitespace(df):
    cat_cols = df.select_dtypes(include=['object', 'string']).columns
    df[cat_cols] = df[cat_cols].apply(lambda x: x.str.strip())
    return df

employee_df = strip_whitespace(employee_df)
performance_df = strip_whitespace(performance_df)
print("Whitespace stripping completed.")

# 5. Handle One-to-Many: Keep the Latest Review per Employee
print("\n--- Step 5: Filtering Latest Performance Review ---")
print(f"Total reviews before filter: {len(performance_df)}")
performance_latest = (performance_df.sort_values(by='ReviewDate', ascending=False)
                      .drop_duplicates(subset='EmployeeID', keep='first'))
print(f"Reviews kept (one per employee): {len(performance_latest)}")

# 6. Merge Datasets
print("\n--- Step 6: Merging Datasets ---")
merged_df = pd.merge(employee_df, performance_latest, on='EmployeeID', how='left')
print(f"Final Merged Shape: {merged_df.shape}")
print(f"Employees without matching reviews (expected): {merged_df['PerformanceID'].isnull().sum()}")

# Save the final result
merged_df.to_csv("Cleaned_Employee_Data.csv", index=False)
print("\nSuccess: 'Cleaned_Employee_Data.csv' saved.")