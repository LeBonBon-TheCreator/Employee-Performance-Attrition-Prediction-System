import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
import joblib

# 1. Load the split datasets
X_train = pd.read_csv("X_train.csv")
X_test = pd.read_csv("X_test.csv")
y_train = pd.read_csv("y_train.csv").values.ravel()
y_test = pd.read_csv("y_test.csv").values.ravel()

# 2. Initialize with Balanced Subsample
# This is the key change to increase sensitivity to salary/distance triggers
rf_model = RandomForestClassifier(
    n_estimators=100, 
    random_state=42,
    class_weight='balanced_subsample'  # <--- Add this parameter
)

# 3. Train the model
rf_model.fit(X_train, y_train)

# 4. Evaluate the model
y_pred = rf_model.predict(X_test)
y_prob = rf_model.predict_proba(X_test)[:, 1]

# Metrics
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)
conf_matrix = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.4f}")
print(f"ROC AUC Score: {roc_auc:.4f}")
print("\nClassification Report:")
print(report)
print("\nConfusion Matrix:")
print(conf_matrix)

# 5. Save the trained model and feature columns
joblib.dump(rf_model, 'attrition_model_test.pkl')
# joblib.dump(list(X_train.columns), 'model_columns.pkl')

print("\nSuccess: New 'Balanced' Model and Column list saved successfully.")