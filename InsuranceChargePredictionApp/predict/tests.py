from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import PredictionForm

User = get_user_model()

class PredictionViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_client = User.objects.create_user(
            email='marie.dupont@gmail.com', 
            first_name='Marie',
            last_name='Dupont',
            password='Marie_Dupont_123', 
            role='Client',
            age=19, 
            gender='female',
            smoker=True,
            region='southwest',
            children=0,
            weight=65.8,
            height=1.75
        )
        
        self.user_advisor = User.objects.create_user(
            email='advisor@test.fr',
            password='Test_Advisor_159',
            role='Advisor'
        )

        self.user_client2 = User.objects.create_user(
            email='jbernard@hotmail.fr', 
            first_name='Jean',
            last_name='Bernard',
            password='Jean_Bernard_123', 
            role='Client',
        )

    # Tests URL et templates

    def test_prediction_view_uses_correct_template(self):
        response = self.client.get(reverse('prediction'))
        self.assertTemplateUsed(response, 'predict/prediction.html')
    
    def test_prediction_view_uses_correct_form(self):
        response = self.client.get(reverse('prediction'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PredictionForm)

    def test_prediction_view_url_returns_correct_http_response(self):
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 200)

        self.client.login(email='marie.dupont@gmail.com', password='Marie_Dupont_123')
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 200)

    def test_prediction_view_unlogged_user_cannot_see_clients_infos(self):
        response = self.client.get(reverse('prediction') + '?user_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_bound)
        self.assertEqual(response.context['form'].initial, {})

    def test_prediction_view_client_only_sees_own_infos(self):
        self.client.login(email='marie.dupont@gmail.com', password='Marie_Dupont_123')
        response = self.client.get(reverse('prediction') + '?user_id=3')
        self.assertEqual(response.status_code, 200)

        expected_infos = {
            'first_name': self.user_client.first_name,
            'last_name': self.user_client.last_name,
            'email': self.user_client.email,
            'age': self.user_client.age,
            'gender': self.user_client.gender,
            'smoker': 'yes' if self.user_client.smoker == True else 'no',
            'region': self.user_client.region,
            'children': self.user_client.children,
            'weight': self.user_client.weight,
            'height': self.user_client.height,
            }
        self.assertEqual(response.context['form'].initial, expected_infos)


    
    # Tests authentification & autorisations

    def test_prediction_view_context_is_advisor_has_correct_value(self):
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.context['is_advisor'], False)

        self.client.login(email='marie.dupont@gmail.com', password='Marie_Dupont_123')
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.context['is_advisor'], False)
        self.client.logout()

        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.context['is_advisor'], True)
    
    def test_prediction_view_advisor_has_correct_clients_list(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction'))

        context_users = response.context['users'].order_by('pk')
        expected_users = User.objects.filter(role='Client').order_by('pk')
        self.assertQuerySetEqual(context_users, expected_users)

    def test_prediction_view_selected_client_returns_correct_infos(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')

    def test_prediction_view_advisor_form_empty_if_invalid_user_id(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction') + '?user_id=5')
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.context['form'].is_bound)
        self.assertEqual(response.context['form'].initial, {})

        




    
    def test_client_sees_prefilled_form(self):
        self.client.login(email='marie.dupont@gmail.com', password='Marie_Dupont_123')
        response = self.client.get(reverse('prediction'))
        self.assertContains(response, 'value="Marie"')
        self.assertContains(response, 'value="Dupont"')
        self.assertContains(response, 'value="19"')
        self.assertContains(response, 'value="female" selected')
        self.assertContains(response, 'value="yes" selected')
        self.assertContains(response, 'value="southwest" selected')
        self.assertContains(response, 'value="0"')
        self.assertContains(response, 'value="65.8"')
        self.assertContains(response, 'value="1.75"')
    








# Tests PredictionView

""" Appel de modèles et templates :
X Utilise le template prediction.html
X Utilise le modèle PredictionForm
 """

""" Réponses HTTP
X Réponse 200 pour l'URL /predict
X URL /predict avec user_id : inaccessible si pas connecté et pas conseiller
X User_id invalide dans l'URL en tant que conseiller : formulaire vide
"""

""" Contexte
X is_advisor est False si client non connecté
X is_advisor est False si client connecté
X is_advisor est True si conseiller connecté
X la liste de clients contient uniquement des user de rôle client
- le selected_user_id correspond bien à l'user_id du client sélectionné
"""

""" Authentification et autorisations
X Client non connecté : formulaire vide, pas de liste de clients
- Client connecté : formulaire pré-rempli avec les bonnes infos, pas de liste clients
- Conseiller connecté : formulaire vide, liste de clients
- Sélection de client : pré-remplit les champs avec les bonnes infos
- Infos client manquantes : champ vide
"""

""" Formulaire : validation et redirection
- Formulaire incomplet : erreur
- Formulaire avec données invalides : erreur
- Tester les différentes valeurs invalides possibles
- Formulaire complet et valide : redirection vers /prediction avec affichage de prédiction et champs conservés
"""

""" Prédiction
- Appel de la fonction dans services.py
- Affichage d'erreur si modèle absent
- Prédiction, range_lower et range_upper : nombres float positifs
- range_lower : minimum 1000
- range_lower < prediction < range_upper
- BMI calculé correctement (weight / height ** 2)
"""



