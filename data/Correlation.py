import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

employee_data = pd.read_csv("Employee.csv")
performance_data = pd.read_csv("PerformanceRating.csv")
pd.set_option('display.max_columns', None)

# Select numerical columns from employee and performance datasets
employee_numeric = employee_data.select_dtypes(include=['int64', 'float64'])
performance_numeric = performance_data.select_dtypes(include=['int64', 'float64'])

# Compute correlation matrices
employee_corr = employee_numeric.corr()
performance_corr = performance_numeric.corr()

# Display correlation matrices in terminal
print("Employee Dataset Correlation Matrix:")
print(employee_corr.round(2))

print("\nPerformance Dataset Correlation Matrix:")
print(performance_corr.round(2))

# Plot employee correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(employee_corr, annot=True, fmt=".2f")
plt.title("Employee Dataset Correlation Matrix")
plt.show()

# Plot performance correlation heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(performance_corr, annot=True, fmt=".2f")
plt.title("Performance Dataset Correlation Matrix")
plt.show()