import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

employee_data = pd.read_csv("Employee.csv")
performance_data = pd.read_csv("PerformanceRating.csv")

# Set general style
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# ==============================
# 1. Histograms for numerical employee attributes
# ==============================
num_cols_emp = ['Age', 'Salary', 'DistanceFromHome (KM)']
employee_data[num_cols_emp].hist(bins=15, edgecolor='black')
plt.suptitle("Distribution of Age, Salary, and Distance from Home")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.show()

# ==============================
# 2. Boxplots for tenure-related variables
# ==============================
tenure_cols = ['YearsAtCompany', 'YearsSinceLastPromotion', 'YearsWithCurrManager']
sns.boxplot(data=employee_data[tenure_cols])
plt.title("Boxplot of Employee Tenure-related Attributes")
plt.ylabel("Years")
plt.show()

# ==============================
# 3. Countplots / Bar charts for categorical employee attributes with values
# ==============================
categorical_cols = ['Gender', 'Department', 'JobRole', 'OverTime']

for col in categorical_cols:
    plt.figure(figsize=(10,6))
    ax = sns.countplot(data=employee_data, x=col, hue='Attrition', palette="Set2")
    
    # Add title and axis labels
    plt.title(f"Attrition Count by {col}")
    plt.xlabel(col)
    plt.ylabel("Number of Employees")
    
    # Rotate x-axis labels if needed
    plt.xticks(rotation=45)
    
    # Add values on top of each bar
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'{height}', 
                    xy=(p.get_x() + p.get_width() / 2, height),
                    xytext=(0, 5),  # vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Show legend
    plt.legend(title='Attrition')
    plt.tight_layout()
    plt.show()

# ==============================
# 4. Histograms for performance dataset
# ==============================
perf_cols = ['SelfRating', 'ManagerRating', 'EnvironmentSatisfaction',
             'JobSatisfaction', 'RelationshipSatisfaction', 'WorkLifeBalance']
performance_data[perf_cols].hist(bins=5, edgecolor='black')
plt.suptitle("Distribution of Performance and Satisfaction Scores")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.show()

# ==============================
# 5. Boxplots for performance metrics
# ==============================
sns.boxplot(data=performance_data[['SelfRating', 'ManagerRating', 'WorkLifeBalance']])
plt.title("Boxplot of Performance Ratings and Work-Life Balance")
plt.ylabel("Score")
plt.show()

# ==============================
# 6. Scatterplot: Salary vs Years at Company, colored by Attrition
# ==============================
sns.scatterplot(data=employee_data, x='YearsAtCompany', y='Salary', hue='Attrition', palette="Set1")
plt.title("Salary vs Years at Company (Colored by Attrition)")
plt.xlabel("Years at Company")
plt.ylabel("Salary")
plt.legend(title='Attrition')
plt.show()

# ==============================
# 7. Scatterplot: Job Satisfaction vs Manager Rating
# ==============================
sns.scatterplot(data=performance_data, x='JobSatisfaction', y='ManagerRating', hue='SelfRating', palette="coolwarm")
plt.title("Manager Rating vs Job Satisfaction (Colored by Self Rating)")
plt.xlabel("Job Satisfaction")
plt.ylabel("Manager Rating")
plt.legend(title="Self Rating") 
plt.show()
