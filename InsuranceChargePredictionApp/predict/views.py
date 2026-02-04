from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import PredictionForm
from django.views.generic import FormView
from .services import predict_charges, ModelNotFoundError
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import ClientInfos, Predictions

User = get_user_model()

class PredictionView(FormView):
    form_class = PredictionForm
    template_name = 'predict/prediction.html'
    success_url = reverse_lazy('prediction')


    def get_initial(self):
        initial = super().get_initial()

        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'role') and self.request.user.role == 'Advisor':
                selected_user_id = self.request.GET.get('user_id')

                if selected_user_id:
                    try:
                        user = User.objects.get(id=selected_user_id)
                        initial = self.get_user_info(user, initial)
                    except User.DoesNotExist:
                        pass
            else:
                initial = self.get_user_info(self.request.user, initial)

        return initial

        
    def get_user_info(self, user, initial):

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

        return initial
    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated and hasattr(self.request.user, 'role') and self.request.user.role == 'Advisor':
            context['users'] = User.objects.filter(role='Client')
            context['selected_user_id'] = self.request.GET.get('user_id', '')
            context['is_advisor'] = True
        else:
            context['is_advisor'] = False

        return context


    def form_valid(self, form):
        try:
            data = form.cleaned_data

            prediction, range_lower, range_upper = predict_charges(
                data['age'], 
                data['gender'], 
                data['smoker'], 
                data['weight'], 
                data['height'], 
                data['children'], 
                data['region']
            )

            context = self.get_context_data()
            context['form'] = form
            context['prediction'] = prediction

            if range_lower and range_upper:
                context['range_lower'] = range_lower
                context['range_upper'] = range_upper
        
        except ModelNotFoundError:
            form.add_error(None, 'Toutes nos excuses, le service de prédiction est momentanément indisponible.')
            return self.form_invalid(form)
        

        try:
            with transaction.atomic():
                client, created = ClientInfos.objects.get_or_create(
                    email = data['email'],
                    first_name = data['first_name'].capitalize(),
                    last_name = data['last_name'].capitalize(),
                    defaults={'user': self.request.user if self.request.user.is_authenticated 
                              and hasattr(self.request.user, 'role') and self.request.user.role == 'Client' 
                              else None}
                )

                Predictions.objects.get_or_create(
                    client = client,
                    prediction = prediction,
                    defaults={
                        'created_by': self.request.user if self.request.user.is_authenticated else None, # Gérer les priorités
                        'range_lower': range_lower if range_lower else None,
                        'range_upper': range_upper if range_upper else None,
                        'age': data['age'], 
                        'gender': data['gender'], 
                        'smoker': data['smoker'], 
                        'weight': data['weight'], 
                        'height': data['height'], 
                        'children': data['children'], 
                        'region': data['region']
                    })

        except Exception:
            print(f"!!! ERREUR DETECTEE : {Exception}")
            context['save_error'] = True
            import traceback
            traceback.print_exc()
        
        return render(self.request, self.template_name, context)