from pathlib import Path
import pandas as pd
import joblib

class ModelNotFoundError(Exception):
    pass

def predict_charges(age, gender, smoker, weight, height, children, region):

    try:
        prediction_model_path = Path(__file__).parent / 'utils' / 'insurance_model.joblib'
        prediction_model = joblib.load(prediction_model_path)
    except FileNotFoundError:
        raise ModelNotFoundError('Le service de prédiction est introuvable.')

    
    if not(30 <= weight <= 250):
        raise ValueError('Le poids renseigné est incorrect.')
    
    if not(1 <= height <= 2.5):
        raise ValueError('La taille renseignée est incorrecte.')
    
    bmi = round(weight / (height ** 2), 2)

    if bmi < 13:
        raise ValueError('Le BMI n\'est pas valide.')


    new_data = pd.DataFrame({
        "age": [age],
        "children": [children],
        "smoker": [smoker],
        "bmi": [bmi],
        "sex": [gender],
        "region": [region]
    })

    prediction = round(prediction_model.predict(new_data)[0], 2)


    try:
        rmse_model_path = Path(__file__).parent / 'utils' / 'rmse.joblib'
        rmse = joblib.load(rmse_model_path)

        range_lower = max(float(1000), round(prediction - rmse, 2))
        range_upper = round(prediction + rmse, 2)
    except Exception:
        return prediction, None, None


    return prediction, range_lower, range_upper