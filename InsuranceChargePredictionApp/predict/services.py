from pathlib import Path
import pandas as pd
import joblib

def predict_charges(age, gender, smoker, weight, height, children, region):
    prediction_model_path = Path(__file__).parent / 'utils' / 'insurance_model.joblib'
    rmse_model_path = Path(__file__).parent / 'utils' / 'rmse.joblib'

    prediction_model = joblib.load(prediction_model_path)
    rmse = joblib.load(rmse_model_path)

    bmi = round(weight / (height ** 2), 2)

    new_data = pd.DataFrame({
        "age": [age],
        "children": [children],
        "smoker": [smoker],
        "bmi": [bmi],
        "sex": [gender],
        "region": [region]
    })

    prediction = prediction_model.predict(new_data)[0]

    range_lower = max(1000, round(prediction - rmse, 2))
    range_upper = round(prediction + rmse, 2)

    return prediction, range_lower, range_upper