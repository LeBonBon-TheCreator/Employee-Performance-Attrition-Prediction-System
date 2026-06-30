import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load the balanced dataset
df_balanced = pd.read_csv("Enriched_Employee_Data.csv")

# 2. Create the visualization
plt.figure(figsize=(8, 6))
# Using AttritionNumeric (0 = Stayed, 1 = Left)
ax = sns.countplot(x='AttritionNumeric', data=df_balanced, palette='magma')

# 3. Add labels and title
plt.title("Distribution of Attrition", fontsize=14)
plt.xlabel("Attrition Status (0: Stayed, 1: Left)", fontsize=12)
plt.ylabel("Number of Employees", fontsize=12)
plt.xticks([0, 1], ['Stayed (0)', 'Left (1)'])

# 4. Add data labels on top of the bars for clarity
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                fontsize=11, color='black', 
                xytext=(0, 5), 
                textcoords='offset points')

# 5. Save and Show
plt.savefig("balanced_attrition_distribution.png")
plt.show()

print("Counts after balancing:")
print(df_balanced['AttritionNumeric'].value_counts())