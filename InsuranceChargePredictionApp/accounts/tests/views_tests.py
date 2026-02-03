from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm

User = get_user_model()

class ViewsTestCase(TestCase):
    class LoginViewTest(TestCase):
        """Tests pour la vue de connexion"""

        def setUp(self):
            self.client = Client()
            self.login_url = reverse("accounts:login")
            self.profile_url = reverse("accounts:profile")
            self.user = User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Jean",
                last_name="Dupont",
                role="Client"
            )

        def test_login_view_uses_correct_template(self):
            """Vérifie que la vue utilise le bon template"""
            response = self.client.get(self.login_url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/login.html")

        def test_login_view_uses_correct_form(self):
            """Vérifie que la vue utilise le bon formulaire"""
            response = self.client.get(self.login_url)
            self.assertIsInstance(response.context["form"], CustomAuthenticationForm)

        def test_login_with_valid_credentials(self):
            """Teste la connexion avec des identifiants valides"""
            response = self.client.post(self.login_url, {
                "username": "test@example.com",
                "password": "testpass123"
            })
            self.assertRedirects(response, self.profile_url)
            self.assertTrue(response.wsgi_request.user.is_authenticated)

        def test_login_with_invalid_credentials(self):
            """Teste la connexion avec des identifiants invalides"""
            response = self.client.post(self.login_url, {
                "username": "test@example.com",
                "password": "wrongpassword"
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

        def test_login_success_message(self):
            """Vérifie le message de succès après connexion"""
            response = self.client.post(self.login_url, {
                "username": "test@example.com",
                "password": "testpass123"
            }, follow=True)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("Bienvenue Jean Dupont", str(messages[0]))

        def test_login_error_message(self):
            """Vérifie le message d'erreur avec identifiants incorrects"""
            response = self.client.post(self.login_url, {
                "username": "test@example.com",
                "password": "wrongpassword"
            })
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("Les identifiants sont incorrects", str(messages[0]))

        def test_redirect_authenticated_user_from_login(self):
            """Vérifie la redirection si l'utilisateur est déjà connecté"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.login_url)
            self.assertRedirects(response, self.profile_url)

        def test_login_with_email_case_insensitive(self):
            """Teste la connexion avec email en majuscules/minuscules"""
            response = self.client.post(self.login_url, {
                "username": "TEST@EXAMPLE.COM",
                "password": "testpass123"
            })
            self.assertRedirects(response, self.profile_url)

        def test_login_with_empty_fields(self):
            """Teste la connexion avec des champs vides"""
            response = self.client.post(self.login_url, {
                "username": "",
                "password": ""
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

        def test_login_with_partial_empty_fields(self):
            """Teste la connexion avec un champ vide"""
            response = self.client.post(self.login_url, {
                "username": "",
                "password": "testpass123"
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)

    class SignupViewTest(TestCase):
        """Tests pour la vue d'inscription"""

        def setUp(self):
            self.client = Client()
            self.signup_url = reverse("accounts:signup")
            self.login_url = reverse("accounts:login")
            self.profile_url = reverse("accounts:profile")

        def test_signup_view_uses_correct_template(self):
            """Vérifie que la vue utilise le bon template"""
            response = self.client.get(self.signup_url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/signup.html")

        def test_signup_view_uses_correct_form(self):
            """Vérifie que la vue utilise le bon formulaire"""
            response = self.client.get(self.signup_url)
            self.assertIsInstance(response.context["form"], CustomUserCreationForm)

        def test_signup_with_valid_data(self):
            """Teste l'inscription avec des données valides"""
            response = self.client.post(self.signup_url, {
                "email": "newuser@example.com",
                "first_name": "Marie",
                "last_name": "Martin",
                "role": "Client",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!"
            })
            self.assertRedirects(response, self.login_url)
            self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

        def test_signup_with_invalid_data(self):
            """Teste l'inscription avec des données invalides"""
            response = self.client.post(self.signup_url, {
                "email": "invalidemail",
                "first_name": "",
                "last_name": "Martin",
                "role": "Client",
                "password1": "pass",
                "password2": "different"
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(User.objects.filter(email="invalidemail").exists())

        def test_signup_success_message(self):
            """Vérifie le message de succès après inscription"""
            response = self.client.post(self.signup_url, {
                "email": "newuser@example.com",
                "first_name": "Marie",
                "last_name": "Martin",
                "role": "Client",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!"
            }, follow=True)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("Compte créé avec succès", str(messages[0]))

        def test_signup_error_message(self):
            """Vérifie le message d'erreur avec formulaire invalide"""
            response = self.client.post(self.signup_url, {
                "email": "",
                "first_name": "Marie",
                "last_name": "Martin"
            })
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("Veuillez compléter le formulaire", str(messages[0]))

        def test_signup_with_duplicate_email(self):
            """Teste l'inscription avec un email déjà existant"""
            User.objects.create_user(
                email="existing@example.com",
                password="pass123",
                first_name="Existing",
                last_name="User",
                role="Client"
            )
            response = self.client.post(self.signup_url, {
                "email": "existing@example.com",
                "first_name": "New",
                "last_name": "User",
                "role": "Client",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects.filter(email="existing@example.com").count(), 1)

        def test_redirect_authenticated_user_from_signup(self):
            """Vérifie la redirection si l'utilisateur est déjà connecté"""
            user = User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User",
                role="Client"
            )
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.signup_url)
            self.assertRedirects(response, self.profile_url)

        def test_signup_role_assignment(self):
            """Vérifie que le rôle est correctement assigné"""
            self.client.post(self.signup_url, {
                "email": "advisor@example.com",
                "first_name": "John",
                "last_name": "Advisor",
                "role": "Advisor",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!"
            })
            user = User.objects.get(email="advisor@example.com")
            self.assertEqual(user.role, "Advisor")

        def test_signup_password_mismatch(self):
            """Teste l'inscription avec des mots de passe différents"""
            response = self.client.post(self.signup_url, {
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "role": "Client",
                "password1": "ComplexPass123!",
                "password2": "DifferentPass123!"
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(User.objects.filter(email="test@example.com").exists())


    class LogoutViewTest(TestCase):
        """Tests pour la vue de déconnexion"""

        def setUp(self):
            self.client = Client()
            self.logout_url = reverse("accounts:logout")
            self.login_url = reverse("accounts:login")
            self.user = User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Jean",
                last_name="Dupont",
                role="Client"
            )

        def test_logout_redirects_to_login(self):
            """Vérifie la redirection vers la page de connexion après déconnexion"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.logout_url)
            self.assertRedirects(response, self.login_url)

        def test_logout_message(self):
            """Vérifie le message de déconnexion"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.logout_url, follow=True)
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertIn("Vous avez été déconnecté", str(messages[0]))

        def test_user_is_logged_out_after_logout(self):
            """Vérifie que l'utilisateur est bien déconnecté"""
            self.client.login(email="test@example.com", password="testpass123")
            self.client.get(self.logout_url)
            response = self.client.get(reverse("accounts:profile"))
            # Devrait rediriger vers login car non authentifié
            self.assertEqual(response.status_code, 302)

        def test_logout_when_not_authenticated(self):
            """Teste la déconnexion quand l'utilisateur n'est pas connecté"""
            response = self.client.get(self.logout_url)
            self.assertRedirects(response, self.login_url)

        def test_user_sent_back_to_home_after_logout(self):
            """Vérifie que l'utilisateur est redirigé vers la page de connexion après déconnexion"""
            self.client.login(email="test@exemple.com", password="testpass123")
            response = self.client.get(self.logout_url)
            self.assertRedirects(response, self.login_url)


    class ProfileViewTest(TestCase):
        """Tests pour la vue de profil"""

        def setUp(self):
            self.client = Client()
            self.profile_url = reverse("accounts:profile")
            self.login_url = reverse("accounts:login")
            self.user = User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Jean",
                last_name="Dupont",
                role="Client",
                age=30,
                weight=75.0,
                height=1.75
            )

        def test_profile_requires_login(self):
            """Vérifie que le profil nécessite une authentification"""
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(self.login_url, response.url)

        def test_profile_view_for_authenticated_user(self):
            """Vérifie l'accès au profil pour un utilisateur authentifié"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "accounts/profile.html")

        def test_profile_displays_user_information(self):
            """Vérifie que le profil affiche les bonnes informations"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.profile_url)
            self.assertEqual(response.context["user"], self.user)
            self.assertContains(response, "Jean")
            self.assertContains(response, "Dupont")

        def test_profile_uses_correct_form(self):
            """Vérifie que le profil utilise le bon formulaire"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.profile_url)
            self.assertIsInstance(response.context["form"], UserProfileForm)

        def test_profile_update_with_valid_data(self):
            """Teste la mise à jour du profil avec des données valides"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.post(self.profile_url, {
                "first_name": "Jean",
                "last_name": "Dupont",
                "email": "test@example.com",
                "age": 31,
                "weight": 76.0,
                "height": 1.75,
                "gender": "male",
                "smoker": False,
                "children": 2,
                "region": "northeast"
            })
            self.assertRedirects(response, self.profile_url)
            self.user.refresh_from_db()
            self.assertEqual(self.user.age, 31)
            self.assertEqual(self.user.children, 2)

        def test_profile_update_success_message(self):
            """Vérifie le message de succès après mise à jour"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.post(self.profile_url, {
                "first_name": "Jean",
                "last_name": "Dupont",
                "email": "test@example.com",
                "age": 31
            }, follow=True)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("Profil mis à jour avec succès" in str(m) for m in messages))

        def test_profile_update_with_invalid_data(self):
            """Teste la mise à jour du profil avec des données invalides"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.post(self.profile_url, {
                "first_name": "",
                "last_name": "Dupont",
                "email": "invalidemail"
            })
            self.assertEqual(response.status_code, 200)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("Erreur lors de la mise à jour" in str(m) for m in messages))

        def test_profile_update_error_message(self):
            """Vérifie le message d'erreur avec formulaire invalide"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.post(self.profile_url, {
                "email": "invalidemail"
            })
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("Erreur lors de la mise à jour" in str(m) for m in messages))

        def test_profile_form_prepopulated_with_user_data(self):
            """Vérifie que le formulaire est pré-rempli avec les données utilisateur"""
            self.client.login(email="test@example.com", password="testpass123")
            response = self.client.get(self.profile_url)
            form = response.context["form"]
            self.assertEqual(form.instance, self.user)
            self.assertEqual(form.initial.get("age") or form.instance.age, 30)


    class RoleBasedAccessTest(TestCase):
        """Tests pour les permissions basées sur les rôles"""

        def setUp(self):
            self.client = Client()
            self.profile_url = reverse("accounts:profile")
            self.client_user = User.objects.create_user(
                email="client@example.com",
                password="pass123",
                first_name="Client",
                last_name="User",
                role="Client"
            )
            self.advisor_user = User.objects.create_user(
                email="advisor@example.com",
                password="pass123",
                first_name="Advisor",
                last_name="User",
                role="Advisor"
            )

        def test_client_can_access_profile(self):
            """Vérifie qu'un client peut accéder à son profil"""
            self.client.login(email="client@example.com", password="pass123")
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, 200)

        def test_advisor_can_access_profile(self):
            """Vérifie qu'un conseiller peut accéder à son profil"""
            self.client.login(email="advisor@example.com", password="pass123")
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, 200)

        def test_role_persists_after_login(self):
            """Vérifie que le rôle est conservé après connexion"""
            self.client.login(email="advisor@example.com", password="pass123")
            response = self.client.get(self.profile_url)
            self.assertEqual(response.context["user"].role, "Advisor")
