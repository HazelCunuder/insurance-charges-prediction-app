from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestParcoursComplet(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("accounts:signup")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")
        self.predict_url = reverse("prediction")

        self.user_data = {
            "email": "client@test.com",
            "password": "StrongPassword123!",
            "first_name": "Jean",
            "last_name": "Test",
            "role": "Client",
        }

        self.profile_data = {
            "first_name": "Jean",
            "last_name": "Test",
            "age": 35,
            "gender": "male",
            "height": 1.80,
            "weight": 80.0,
            "smoker": False,
            "children": 2,
            "region": "northwest",
        }

    def test_parcours_utilisateur(self):
        """
        Test du parcours complet : Inscription -> Connexion -> Profil -> Prédiction
        """
        # INSCRIPTION
        print("\n--- Etape 1 : Inscription ---")

        # Vérification chargement page inscription
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

        # Soumission formulaire inscription
        signup_data = self.user_data.copy()
        # CustomUserCreationForm attend password1 et password2
        signup_data["password1"] = self.user_data["password"]
        signup_data["password2"] = self.user_data["password"]

        response = self.client.post(self.signup_url, signup_data)

        # Vérification redirection vers login après succès (code 302)
        # Note: Si ça fail ici (200), c'est souvent une erreur de validation formulaire
        if response.status_code != 302:
            print("Erreur formulaire inscription :", response.context["form"].errors)

        self.assertRedirects(response, self.login_url)

        # Vérification création en base
        self.assertTrue(User.objects.filter(email="client@test.com").exists())
        user = User.objects.get(email="client@test.com")
        self.assertEqual(user.first_name, "Jean")

        # CONNEXION
        print("--- Etape 2 : Connexion ---")

        login_data = {
            "username": self.user_data[
                "email"
            ],  # CustomAuthenticationForm utilise 'username' comme champ pour l'email
            "password": self.user_data["password"],
        }

        response = self.client.post(self.login_url, login_data)
        self.assertRedirects(response, self.profile_url)

        # Vérification session active
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # 3. MISE A JOUR PROFIL
        print(" Etape 3 : Mise à jour Profil")

        # Le client est maintenant connecté (session cookie)
        response = self.client.post(self.profile_url, self.profile_data)

        # Redirection vers le profil lui-même (pattern PRG)
        self.assertRedirects(response, self.profile_url)

        # Vérification mise à jour bdd
        user.refresh_from_db()
        self.assertEqual(user.age, 35)
        self.assertEqual(user.weight, 80.0)
        # Vérification calcul propriété BMI
        self.assertIsNotNone(user.bmi)
        self.assertEqual(user.bmi, 24.7)  # 80 / (1.8*1.8) = 24.69... arrondi 24.7

        # 4. PREDICTION
        print("Etape 4 : Prédiction")

        # Accès à la page prédiction (doit être pré-remplie)
        response = self.client.get(self.predict_url)
        self.assertEqual(response.status_code, 200)

        # Vérification pré-remplissage dans le context initial
        initial_data = response.context["form"].initial
        self.assertEqual(initial_data["age"], 35)
        self.assertEqual(initial_data["weight"], 80.0)

        # Soumission du formulaire de prédiction
        predict_data = {
            "age": 35,
            "gender": "male",
            "height": 1.80,
            "weight": 80.0,
            "smoker": "no",
            "children": 2,
            "region": "northwest",
            "first_name": "Jean",  # Champs requis par PredictionForm
            "last_name": "Test",
            "email": "client@test.com",
        }

        response = self.client.post(self.predict_url, predict_data)
        self.assertEqual(response.status_code, 200)

        # Vérification qu'on a bien un résultat
        self.assertIn("prediction", response.context)
        prediction_amount = response.context["prediction"]
        self.assertIsInstance(prediction_amount, float)
        self.assertTrue(prediction_amount > 0)

        print(f"--- Succès ! Montant prédit : {prediction_amount} $ ---")
