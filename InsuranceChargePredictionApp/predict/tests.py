from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import PredictionForm
from .services import predict_charges
from unittest.mock import patch

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

    def test_prediction_view_only_advisors_see_clients_list(self):
        response = self.client.get(reverse('prediction'))
        self.assertNotIn('users', response.context)

        self.client.login(email='marie.dupont@gmail.com', password='Marie_Dupont_123')
        response = self.client.get(reverse('prediction'))
        self.assertNotIn('users', response.context)
        self.client.logout()

        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction'))
        self.assertIn('users', response.context)

    def test_prediction_view_advisor_has_correct_clients_list(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction'))

        context_users = response.context['users'].order_by('pk')
        expected_users = User.objects.filter(role='Client').order_by('pk')
        self.assertQuerySetEqual(context_users, expected_users)

    def test_prediction_view_advisor_form_empty_if_invalid_user_id(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        response = self.client.get(reverse('prediction') + '?user_id=5')
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.context['form'].is_bound)
        self.assertEqual(response.context['form'].initial, {})

    def test_prediction_view_selected_client_id_is_correct(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        target_user_id = self.user_client.id
        response = self.client.get(reverse('prediction') + f'?user_id={target_user_id}')
        self.assertEqual(int(response.context['selected_user_id']), target_user_id)

    def test_prediction_view_selected_client_returns_correct_infos(self):
        self.client.login(email='advisor@test.fr', password='Test_Advisor_159')
        target_user_id = self.user_client2.id
        response = self.client.get(reverse('prediction') + f'?user_id={target_user_id}')

        initial_data = response.context['form'].initial
        self.assertEqual(initial_data.get('weight'), None)
        self.assertNotContains(response, 'name="weight" value="')

        self.assertEqual(initial_data.get('email'), "jbernard@hotmail.fr")
        self.assertContains(response, 'name="email" value="jbernard@hotmail.fr"')


    # Tests validation du formulaire



    # Test prédiction

    @patch('predict.views.predict_charges')
    def test_prediction_view_form_validation_calls_predict_charges(self, mock_predict):
        mock_predict.return_value = (3000.50, 1000, 7000.50)
        data = {
            'first_name': 'Alice',
            'last_name': 'Marchand',
            'email': 'alice.marchand@gmail.com',
            'age': 20,
            'gender': 'male',
            'smoker': 'no',
            'weight': 78.5,
            'height': 1.78,
            'children': 2,
            'region': 'southeast',
            }
        response = self.client.post(reverse('prediction'), data=data)

        mock_predict.assert_called_once_with(20, 'male', 'no', 78.5, 1.78, 2, 'southeast')
        self.assertEqual(response.context['prediction'], 3000.50)
        self.assertEqual(response.context['range_lower'], 1000)
        self.assertEqual(response.context['range_upper'], 7000.50)


class PredictChargesTest(TestCase):
    def test_predict_charges_output_format(self):
        prediction, range_lower, range_upper = predict_charges(
            age=20, 
            gender='female', 
            smoker='yes', 
            weight=70, 
            height=1.8, 
            children=2, 
            region='southeast'
        )

        self.assertIsInstance(prediction, float)
        self.assertIsInstance(range_lower, float)
        self.assertIsInstance(range_upper, float)


""" Formulaire : validation et redirection
- Formulaire incomplet : erreur
- Formulaire avec données invalides : erreur
- Tester les différentes valeurs invalides possibles
- Formulaire complet et valide : redirection vers /prediction avec affichage de prédiction et champs conservés
"""

""" Prédiction
X Appel de la fonction dans services.py
- Affichage d'erreur si modèle absent
- Prédiction, range_lower et range_upper : nombres float positifs
- range_lower : minimum 1000
- range_lower < prediction < range_upper
- BMI calculé correctement (weight / height ** 2)
"""


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
"""

""" Authentification et autorisations
X Liste de clients non visible si utilisateur non connecté ou client connecté
X Conseiller connecté : formulaire vide, liste de clients
X Le selected_user_id correspond bien à l'user_id du client sélectionné
X Sélection de client : pré-remplit les champs avec les bonnes infos
X Infos client manquantes : champ vide
"""



