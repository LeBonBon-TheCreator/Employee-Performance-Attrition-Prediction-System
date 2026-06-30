import joblib
model = joblib.load('attrition_rf_model.pkl')

# This will print the exact 55 names and the order they must be in
print(model.feature_names_in_)