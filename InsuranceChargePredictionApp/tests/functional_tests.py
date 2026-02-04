from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestClientJourney(TestCase):

    # Functional test for Client user journey

    def setUp(self):

        # Client HTTP pour simuler un navigateur
        self.client = Client()

        # URLs de l'application
        self.signup_url = reverse("accounts:signup")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")
        self.predict_url = reverse("prediction")

        # Données utilisateur pour les tests
        self.email = "client@test.com"
        self.password = "StrongPassword123!"

        # Données profil
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

    # HELPERS

    def register_user(self):
        """Register a user and return the User object"""
        response = self.client.post(
            self.signup_url,
            {
                "email": self.email,
                "password1": self.password,
                "password2": self.password,
                "first_name": "Jean",
                "last_name": "Test",
                "role": "Client",
            },
        )
        # Vérifie la redirection vers login
        self.assertRedirects(response, self.login_url)
        return User.objects.get(email=self.email)

    def login_user(self):
        """Log in the user"""
        response = self.client.post(
            self.login_url,
            {
                "username": self.email,
                "password": self.password,
            },
        )
        self.assertRedirects(response, self.profile_url)
        return response

    # TESTS

    def test_signup(self):
        # Test: A visitor can sign up

        # Action
        user = self.register_user()

        # Vérifications
        self.assertEqual(user.email, "client@test.com")
        self.assertEqual(user.role, "Client")

    def test_login(self):

        # Preparation: we need a user first
        self.register_user()

        # Action: login
        self.login_user()

        # The redirection is verified in the helper

    def test_profile_update(self):

        # A logged-in user can update their profile

        # Preparation
        self.register_user()
        self.login_user()

        # Action: update profile
        # We send profile_data which contains age, height, etc.
        response = self.client.post(self.profile_url, self.profile_data)

        # Verification
        # Check that we redirect to profile page (PRG pattern)
        self.assertRedirects(response, self.profile_url)

        # Check DB update
        user = User.objects.get(email=self.email)
        self.assertEqual(user.age, 35)
        self.assertEqual(user.region, "northwest")

    def test_prediction(self):

        # A user with a complete profile can get a prediction

        # Full preparation
        self.register_user()
        self.login_user()
        self.client.post(self.profile_url, self.profile_data)

        # verify pre-filling
        response = self.client.get(self.predict_url)
        initial = response.context["form"].initial
        self.assertEqual(initial["age"], 35)

        # submit the prediction
        predict_data = {
            **self.profile_data,
            "smoker": "no",  # Expected format for the form
            "email": self.email,
        }
        response = self.client.post(self.predict_url, predict_data)

        # Vérifications
        self.assertEqual(response.status_code, 200)
        self.assertIn("prediction", response.context)

        prediction = response.context["prediction"]
        self.assertIsInstance(prediction, float)
        self.assertGreater(prediction, 0)


class TestAdvisorJourney(TestCase):
    # Test for Advisor journey

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("accounts:signup")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")

    def test_advisor_signup(self):
        # An advisor can sign up with the Advisor role
        response = self.client.post(
            self.signup_url,
            {
                "email": "assureur@test.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
                "first_name": "Marie",
                "last_name": "Dupont",
                "role": "Advisor",
            },
        )

        self.assertRedirects(response, self.login_url)

        user = User.objects.get(email="assureur@test.com")
        self.assertEqual(user.role, "Advisor")


class TestSecurity(TestCase):
    # Basic security tests

    def test_profile_requires_login(self):
        # An unauthenticated visitor cannot access the profile
        client = Client()
        response = client.get(reverse("accounts:profile"))

        # Should redirect to login (code 302)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
