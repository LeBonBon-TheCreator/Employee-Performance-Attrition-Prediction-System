import joblib
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the model and the columns
rf_model = joblib.load('model/attrition_rf_model.pkl')
model_columns = joblib.load('model/model_columns.pkl')

# 2. Extract Importance
importances = rf_model.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': model_columns,
    'Importance': importances
})

# 3. Sort and view Top 10
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

print("--- TOP 10 FEATURES DRIVING PREDICTIONS ---")
print(feature_importance_df.head(10))

# 4. Optional: Visualize it
plt.figure(figsize=(10, 6))
plt.barh(feature_importance_df['Feature'].head(10), feature_importance_df['Importance'].head(10))
plt.xlabel('Gini Importance')
plt.title('Top 10 Features in Attrition Model')
plt.gca().invert_yaxis()
plt.show()