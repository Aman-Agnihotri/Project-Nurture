from flask import Flask, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load the model
model = joblib.load('random_forest_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request
    data = request.get_json(force=True)

    # Make a DataFrame from the data
    df = pd.DataFrame(data, index=[0])

    # Encode categorical variables
    df = pd.get_dummies(df, columns=['Health Portfolio', 'Urban or Rural'])

    # Ensure all columns in the model are present in the DataFrame
    model_columns = list(model.feature_names_in_)
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0

    # Make a prediction
    prediction = model.predict(df[model_columns])

    # Return the prediction
    return {'prediction': prediction[0]}