import os
import pandas as pd
import dill  # Use dill instead of joblib
from lime.lime_tabular import LimeTabularExplainer

current_folder = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_folder, 'X_train.csv')

if os.path.exists(csv_path):
    print("File found! Loading data...")
    X_train = pd.read_csv(csv_path)
    
    explainer = LimeTabularExplainer(
        training_data=X_train.values,
        feature_names=X_train.columns.tolist(),
        class_names=['Stay', 'Leave'],
        mode='classification',
        discretize_continuous=False 
    )
    
    # SAVE using dill
    save_path = os.path.join(current_folder, 'lime_explainer.pkl')
    with open(save_path, 'wb') as f:
        dill.dump(explainer, f)
        
    print(f"Explainer saved successfully using DILL at: {save_path}")
else:
    print("Error: File not found.")