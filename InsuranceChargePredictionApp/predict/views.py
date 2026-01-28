from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import PredictionForm
from django.views.generic import FormView
import joblib
import pandas as pd
from pathlib import Path
import __main__



def add_features(X):
    X = X.copy()
    X["smoker"] = X["smoker"].map({"yes": 1, "no": 0})
    X["smoker_obese"] = X["smoker"] * (X["bmi"] >= 30).astype(int)
    X["age"] = X["age"] ** 2
    return X

__main__.add_features = add_features

class PredictionView(FormView):
    form_class = PredictionForm
    template_name = 'predict/prediction.html'
    success_url = reverse_lazy('prediction')

    def form_valid(self, form):
        age = form.cleaned_data.get('age')
        gender = form.cleaned_data.get('gender')
        smoker = form.cleaned_data.get('smoker')
        region = form.cleaned_data.get('region')
        children = form.cleaned_data.get('children')
        weight = form.cleaned_data.get('weight')
        height = form.cleaned_data.get('height')
        bmi = weight / (height ** 2)

        new_data = pd.DataFrame({
            "age": [age],
            "children": [children],
            "smoker": [smoker],
            "bmi": [bmi],
            "sex": [gender],
            "region": [region]
        })

        prediction_model_path = Path(__file__).parent / 'insurance_model.pkl'
        prediction_model = joblib.load(prediction_model_path)
        prediction = prediction_model.predict(new_data)[0]

        context = self.get_context_data()
        context['form'] = form
        context['prediction'] = round(prediction, 2)

        return render(self.request, self.template_name, context)
        
