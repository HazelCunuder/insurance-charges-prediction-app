from django import forms

class PredictionForm(forms.Form):
    """ Formulaire pour générer une prédiction des charges d'assurance. """
    
    GENDER_CHOICES = [('', '- - - - - - -'), ('female', 'Femme'), ('male', 'Homme')]
    SMOKER_CHOICES = [('', '- - - -'), ('yes', 'Oui'), ('no', 'Non')]
    REGION_CHOICES = [('', '- - - - - - - - - - -'), ('northeast', 'Nord-Est'), ('northwest', 'Nord-Ouest'), ('southeast', 'Sud-Est'), ('southwest', 'Sud-Ouest')]

    first_name = forms.CharField(
        label="Prénom", 
        min_length=2,
        max_length=50,
        error_messages={
            'required': 'Veuillez renseigner un prénom.',
            'min_length': 'Le prénom doit comporter au moins 2 caractères.',
            'max_length': 'Le prénom ne peut pas contenir plus de 50 caractères.'
            })

    last_name = forms.CharField(
        label='Nom', 
        min_length=2,
        max_length=50,
        error_messages={
            'required': 'Veuillez renseigner un nom de famille.',
            'min_length': 'Le nom doit comporter au moins 2 caractères.',
            'max_length': 'Le nom ne peut pas contenir plus de 50 caractères.'
        })

    email = forms.EmailField(
        label='Adresse email',
        error_messages={
            'required': "Veuillez renseigner une adresse email.",
            'invalid': "Veuillez renseigner une adresse email valide."
        })

    age = forms.IntegerField(
        label='Âge :', 
        min_value=18, 
        max_value=125,
        error_messages={
            'required': 'Veuillez renseigner un âge.',
            'min_value': 'Le client doit avoir 18 ans minimum.',
            'max_value': 'L\'âge ne peut pas dépasser 125.',
            'invalid': 'L\'âge doit être un nombre entier.'
        })

    gender = forms.ChoiceField(
        label='Genre :', 
        choices=GENDER_CHOICES,
        error_messages={
            'required': 'Veuillez sélectionner un genre.',
            'invalid_choice': 'Ce choix n\'est pas valide.'
        })

    weight = forms.FloatField(
        label='Poids (en kg) :', 
        min_value=30, 
        max_value=250, 
        step_size = 0.1,
        error_messages={
            'required': 'Veuillez renseigner un poids.',
            'min_value': 'Le poids ne peut pas être inférieur à 30 kg.',
            'max_value': 'Le poids ne peut pas dépasser 250 kg.',
            'step_size': 'Le poids doit être un nombre au format 60 ou 60.1.',
            'invalid': 'Le poids doit être un nombre au format 60 ou 60.1.'
        })

    height = forms.FloatField(
        label='Taille (en m) :', 
        min_value=1, 
        max_value=2.50, 
        step_size = 0.01,
        error_messages={
            'required': 'Veuillez renseigner une taille.',
            'min_value': 'La taille ne peut pas être inférieure à 1 mètre.',
            'max_value': 'La taille ne peut pas dépasser 2,5 mètres.',
            'step_size': 'La taille doit être un nombre avec maximum deux décimales (ex : 1.65).',
            'invalid': 'La taille doit être un nombre.'
        })

    smoker = forms.ChoiceField(
        label='Fumeur :', 
        choices=SMOKER_CHOICES,
        error_messages={
            'required': 'Veuillez sélectionner une option.',
            'invalid_choice': 'Ce choix n\'est pas valide.'
        })

    children = forms.IntegerField(
        label='Nombre d\'enfants :', 
        min_value=0, 
        max_value=15,
        error_messages={
            'required': 'Veuillez renseigner le nombre d\'enfants.',
            'min_value': 'Le nombre d\'enfants ne peut pas être négatif.',
            'max_value': 'Le nombre d\'enfants ne peut pas dépasser 15.',
            'invalid': 'Le nombre d\'enfants doit être un nombre entier.'
        })

    region = forms.ChoiceField(
        label='Région :', 
        choices=REGION_CHOICES,
        error_messages={
            'required': 'Veuillez sélectionner une région.',
            'invalid_choice': 'Ce choix n\'est pas valide.'
        })
