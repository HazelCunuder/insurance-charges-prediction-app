from pathlib import Path
import joblib

prediction_model_path = Path(__file__).parent / 'insurance_model.joblib'
rmse_model_path = Path(__file__).parent / 'rmse.joblib'

prediction_model = joblib.load(prediction_model_path)
rmse = joblib.load(rmse_model_path)