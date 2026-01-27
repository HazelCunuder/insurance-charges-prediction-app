from django.db import models
from django.contrib.auth.hashers import make_password


class UserAuthentification(models.Model):
    ROLE_CHOICES = [('Client', 'Client'), ('Advisor', 'Conseiller')]

    user_first_name = models.CharField(max_length=50, verbose_name='Prénom')
    user_last_name = models.CharField(max_length=30, verbose_name='Nom de famille')
    user_email = models.EmailField(max_length=100, verbose_name='Adresse mail')
    user_password = make_password(str(models.CharField(max_length=50, verbose_name='Mot de passe')), salt=None, hasher='default')

    def __str__(self):
        return f'Utilisateur : {self.first_name} {self.last_name} ({self.email})'


class UserPrediction(models.Model):
    GENDER_CHOICES = [('female', 'Femme'), ('male', 'Homme')]
    SMOKER_CHOICES = [('yes', 'Oui'), ('no', 'Non')]
    REGION_CHOICES = [('northeast', 'Nord-Est'), ('northwest', 'Nord-Ouest'), ('southeast', 'Sud-Est'), ('southwest', 'Sud-Ouest')]

    user_id = models.ForeignKey(UserAuthentification, on_delete=models.CASCADE)
    user_age = models.PositiveIntegerField(verbose_name='Âge')
    user_gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name='Genre')

    user_height = models.FloatField(verbose_name='Taille (en m)')
    user_weight = models.FloatField(verbose_name='Poids (en kg)')

    user_smoker = models.CharField(max_length=3, choices=SMOKER_CHOICES, verbose_name='Êtes-vous fumeur ?')
    user_children = models.PositiveIntegerField(verbose_name='Nombre d\'enfants')
    user_region = models.CharField(max_length=9, choices=REGION_CHOICES, verbose_name='Région de résidence')

    def __str__(self):
        return f'Utilisateur n° {self.id} : {'femme' if self.user_gender == 'female' else 'homme'}, {self.user_age} ans, {'fumeur' if self.user_smoker == 'yes' else 'non fumeur'}, IMC {self.user_bmi}, {self.user_children} enfant(s).'
