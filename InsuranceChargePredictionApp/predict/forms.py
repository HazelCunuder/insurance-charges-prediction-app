from django import forms

class PredictionForm(forms.Form):
    GENDER_CHOICES = [('female', 'Femme'), ('male', 'Homme')]
    SMOKER_CHOICES = [('yes', 'Oui'), ('no', 'Non')]
    REGION_CHOICES = [('northeast', 'Nord-Est'), ('northwest', 'Nord-Ouest'), ('southeast', 'Sud-Est'), ('southwest', 'Sud-Ouest')]

    age = forms.IntegerField(label='Âge :', min_value=18, max_value=120, required=True)
    gender = forms.ChoiceField(label='Genre :', choices=GENDER_CHOICES, required=True)

    weight = forms.IntegerField(label='Poids (en kg) :', min_value=30, max_value=250, required=True)
    height = forms.FloatField(label='Taille (en m) :', min_value=1, max_value=2.20, required=True)

    smoker = forms.ChoiceField(label='Fumeur :', choices=SMOKER_CHOICES, required=True)
    children = forms.IntegerField(label='Nombre d\'enfants :', min_value=0, max_value=10, required=True)
    region = forms.ChoiceField(label='Région :', choices=REGION_CHOICES)
