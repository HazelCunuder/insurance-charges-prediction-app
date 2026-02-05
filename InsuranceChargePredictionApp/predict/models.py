from django.db import models
from django.conf import settings


class ClientInfos(models.Model):
    """Modèle avec les informations de contact des utilisateurs ayant généré une prédiction. """
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    # Client supprimé : on garde ses infos comme un client non connecté
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, blank=True, 
        on_delete=models.SET_NULL, 
        related_name='client_profiles')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['first_name', 'last_name', 'email'],
                name = 'unique_client_profile'
            )]

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'



class Predictions(models.Model):
    """Modèle avec les informations utilisées pour générer une prédiction et les résultats associés. """
    
    date = models.DateTimeField(auto_now_add=True)

    # Infos de contact client supprimées : inutile de garder les prédictions associées
    client = models.ForeignKey('ClientInfos', 
                               on_delete=models.CASCADE,
                               related_name='predictions')
    
    # Conseiller supprimé : on garde les prédictions liées
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='prediction_creator')

    prediction = models.DecimalField(max_digits=8, decimal_places=2)
    range_lower = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    range_upper = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    age = models.PositiveIntegerField()
    weight = models.FloatField()
    height = models.FloatField()
    children = models.PositiveIntegerField(default=0)

    gender = models.CharField(max_length=6, verbose_name='Genre', choices=[('male', 'Homme'), ('female', 'Femme')])
    smoker = models.CharField(max_length=3, verbose_name='Fumeur', choices=[('yes', 'Oui'), ('no', 'Non')])
    
    REGION_CHOICES = [('southwest', 'Sud-Ouest'), ('southeast', 'Sud-Est'), ('northwest', 'Nord-Ouest'), ('northeast', 'Nord-Est')]
    region = models.CharField(max_length=10, choices=REGION_CHOICES)

    def __str__(self):
        return f'Client {self.client} : {self.prediction} €'


