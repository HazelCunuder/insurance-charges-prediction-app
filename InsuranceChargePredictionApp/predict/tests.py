from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import PredictionForm
from .services import predict_charges, ModelNotFoundError
from unittest.mock import patch, MagicMock

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
            'weight': self.user_client.weight,
            'height': self.user_client.height,
            'children': self.user_client.children,
            'region': self.user_client.region,
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

        self.assertEqual(initial_data.get('email'), 'jbernard@hotmail.fr')
        self.assertContains(response, 'name="email" value="jbernard@hotmail.fr"')



class PredictionViewFormTests(TestCase):

    def setUp(self):
        self.data = {
            'first_name': 'Alice',
            'last_name': 'Marchand',
            'email': 'alice.marchand@gmail.com',
            'age': 20,
            'gender': 'female',
            'smoker': 'no',
            'weight': 78.5,
            'height': 1.78,
            'children': 2,
            'region': 'southeast',
            }


    def test_prediction_form_incomplete_returns_error(self):
        data_incomplete = {
            'first_name': 'Alice',
            'last_name': 'Marchand',
            'gender': 'female',
            'smoker': 'no',
            'children': 2,
            'height': 1.78
        }

        response = self.client.post(reverse('prediction'), data=data_incomplete)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('weight', form.errors)


    def test_predicttion_form_valid_keeps_data(self):
        response = self.client.post(reverse('prediction'), data=self.data)

        form = response.context['form']
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['age'], 20)
        self.assertEqual(form.cleaned_data['smoker'], 'no')


    """ Formulaire : validation et redirection
    - Formulaire avec données invalides : erreur
    """

    @patch('predict.views.predict_charges')
    def test_prediction_view_form_validation_calls_predict_charges(self, mock_predict):
        mock_predict.return_value = (3000.50, 1000, 7000.50)

        response = self.client.post(reverse('prediction'), data=self.data)

        mock_predict.assert_called_once_with(20, 'female', 'no', 78.5, 1.78, 2, 'southeast')
        self.assertEqual(response.context['prediction'], 3000.50)
        self.assertEqual(response.context['range_lower'], 1000)
        self.assertEqual(response.context['range_upper'], 7000.50)


    @patch('predict.services.joblib.load')
    def test_prediction_view_handles_loading_model_error(self, mock_load):
        mock_load.side_effect = FileNotFoundError
        response = self.client.post(reverse('prediction'), data=self.data)
        form = response.context['form']

        self.assertIn('le service de prédiction est momentanément indisponible', form.non_field_errors()[0])
        self.assertContains(response, 'le service de prédiction est momentanément indisponible')
        self.assertNotContains(response, 'Résultat de la prédiction')


    @patch('predict.services.joblib.load')
    def test_prediction_view_handles_rmse_loading_error(self, mock_load):
        mock_model = MagicMock()
        mock_model.predict.return_value = [5263.25]
        mock_load.side_effect = [mock_model, FileNotFoundError]

        response = self.client.post(reverse('prediction'), data=self.data)
        self.assertContains(response, '5263,25')
        self.assertNotIn('range_lower', response.context)
        self.assertNotIn('range_upper', response.context)
        self.assertNotContains(response, 'Fourchette')



class PredictChargesTest(TestCase):

    def setUp(self):
        self.prediction, self.range_lower, self.range_upper = predict_charges(
            age=18, 
            gender='male', 
            smoker='no', 
            weight=70, 
            height=1.8, 
            children=0, 
            region='northwest'
        )

        self.prediction_extreme, self.range_lower_extreme, self.range_upper_extreme = predict_charges(
            age=65, 
            gender='female', 
            smoker='no', 
            weight=150, 
            height=1.75, 
            children=3, 
            region='southeast'
        )


    def test_predict_charges_output_format(self):
        self.assertIsInstance(self.prediction, float)
        self.assertIsInstance(self.range_lower, float)
        self.assertIsInstance(self.range_upper, float)


    def test_predict_charges_valid_values(self):
        # Test avec valeurs basses
        self.assertGreaterEqual(self.range_lower, float(1000))
        self.assertGreater(self.prediction, self.range_lower)
        self.assertGreater(self.range_upper, self.prediction)

        # Test avec valeurs extrêmes
        self.assertGreaterEqual(self.range_lower_extreme, float(1000))
        self.assertGreater(self.prediction_extreme, self.range_lower_extreme)
        self.assertGreater(self.range_upper_extreme, self.prediction_extreme)
    

    @patch('predict.services.pd.DataFrame')
    def test_predict_charges_bmi_calculation(self, mock_df_class):
        try:
            predict_charges(
                age=30, 
                gender='female', 
                smoker='no', 
                weight=80, 
                height=1.75, 
                children=1, 
                region='southwest'
            )
        except:
            pass

        sent_dataframe = mock_df_class.call_args[0][0]
        expected_bmi = 26.12
        actual_bmi = sent_dataframe['bmi'][0]
        self.assertEqual(expected_bmi, actual_bmi)


    @patch('predict.services.joblib.load')
    def test_predict_charges_returns_error_if_model_not_found(self, mock_load):
        mock_load.side_effect = FileNotFoundError

        with self.assertRaises(ModelNotFoundError) as cm:
            predict_charges(
                age=30, 
                gender='female', 
                smoker='no', 
                weight=80, 
                height=1.75, 
                children=1, 
                region='southwest'
            )
        
        self.assertEqual(str(cm.exception), 'Le service de prédiction est introuvable.')


    @patch('predict.services.joblib.load')
    def test_predict_charges_returns_none_if_rmse_not_found(self, mock_load):
        mock_model = MagicMock()
        mock_model.predict.return_value = [3658.90]
        mock_load.side_effect = [mock_model, FileNotFoundError]

        prediction, range_lower, range_upper = predict_charges(
            age=30, 
            gender='female', 
            smoker='no', 
            weight=80, 
            height=1.75, 
            children=1, 
            region='southwest'
        )

        self.assertEqual(prediction, 3658.90)
        self.assertIsNone(range_lower)
        self.assertIsNone(range_upper)