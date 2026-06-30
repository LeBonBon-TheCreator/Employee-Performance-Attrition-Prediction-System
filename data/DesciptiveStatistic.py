import pandas as pd
pd.set_option('display.max_columns', None)

# Load datasets
employee_df = pd.read_csv("Employee.csv")
performance_df = pd.read_csv("PerformanceRating.csv")

# Display basic information
print(employee_df.info())
print(performance_df.info())

# Descriptive statistics for numerical attributes
employee_stats = employee_df.describe()
performance_stats = performance_df.describe()

print("Employee Dataset Descriptive Statistics:")
print(employee_stats)

print("\nPerformance Dataset Descriptive Statistics:")
print(performance_stats)
