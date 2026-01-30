from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import PredictionForm
from django.views.generic import FormView
import pandas as pd
from .utils.service import prediction_model, rmse
from django.contrib.auth import get_user_model

User = get_user_model()

class PredictionView(FormView):
    form_class = PredictionForm
    template_name = 'predict/prediction.html'
    success_url = reverse_lazy('prediction')


    def get_initial(self):
        initial = super().get_initial()
        selected_user_id = self.request.GET.get('user_id')

        if selected_user_id:
            try:
                user = User.objects.get(id=selected_user_id)

                if hasattr(user, 'first_name') and user.first_name:
                    initial['first_name'] = user.first_name

                if hasattr(user, 'last_name') and user.last_name:
                    initial['last_name'] = user.last_name

                if hasattr(user, 'email') and user.email:
                    initial['email'] = user.email

                if hasattr(user, 'age') and user.age:
                    initial['age'] = user.age

                if hasattr(user, 'gender') and user.gender:
                    initial['gender'] = user.gender
                
                if hasattr(user, 'weight') and user.weight:
                    initial['weight'] = user.weight
                
                if hasattr(user, 'height') and user.height:
                    initial['height'] = user.height
                
                if hasattr(user, 'children') and user.children is not None:
                    initial['children'] = user.children
                
                if hasattr(user, 'region') and user.region:
                    initial['region'] = user.region

                if hasattr(user, 'smoker') and user.smoker is not None:
                    initial['smoker'] = 'yes' if user.smoker else 'no'


            except User.DoesNotExist:
                pass


        return initial
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(role='Client')
        context['selected_user_id'] = self.request.GET.get('user_id', '')
        return context


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

        prediction = prediction_model.predict(new_data)[0]

        range_lower = max(1000, round(prediction - rmse, 2))
        range_upper = round(prediction + rmse, 2)

        context = self.get_context_data()
        context['form'] = form
        context['prediction'] = round(prediction, 2)
        context['range_lower'] = range_lower
        context['range_upper'] = range_upper

        return render(self.request, self.template_name, context)
        
