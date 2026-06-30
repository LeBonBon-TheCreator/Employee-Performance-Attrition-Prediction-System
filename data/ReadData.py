import pandas as pd

employee_data = pd.read_csv("Employee.csv")
performance_data = pd.read_csv("PerformanceRating.csv")

# Dataset dimensions
employee_data.shape
performance_data.shape

# Dataset attributes / structure
employee_data.info()
performance_data.info()
