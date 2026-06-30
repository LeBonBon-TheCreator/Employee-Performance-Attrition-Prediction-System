import pandas as pd
from sklearn.model_selection import train_test_split

# 1. Load the model-ready dataset
df = pd.read_csv("Balanced_Employee_Data.csv")

# 2. Separate features (X) from the target (y)
X = df.drop('AttritionNumeric', axis=1)
y = df['AttritionNumeric']

# 3. Perform the split
# test_size=0.2 means 20% of data is reserved for testing
# stratify=y ensures the 50/50 balance is maintained in both sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Verification and Output
print(f"Training set size: {X_train.shape[0]} rows")
print(f"Testing set size: {X_test.shape[0]} rows")
print(f"Balance in Training Set: {y_train.value_counts(normalize=True).to_dict()}")

# 5. Save the sets for the next step (Random Forest training)
X_train.to_csv("X_train.csv", index=False)
X_test.to_csv("X_test.csv", index=False)
y_train.to_csv("y_train.csv", index=False)
y_test.to_csv("y_test.csv", index=False)