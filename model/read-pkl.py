import pickle

file_path = 'model/model_columns.pkl' 

try:
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    
    print("Data successfully loaded:")
    # You can now use the 'data' variable as a normal Python object
    print(data) 

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

