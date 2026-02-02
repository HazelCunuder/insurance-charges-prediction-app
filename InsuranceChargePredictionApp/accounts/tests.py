from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm


User = get_user_model()


class CustomUserModelTest(TestCase):
    """Tests pour le modèle CustomUser"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "role": "Client",
        }

    def test_create_user_with_valid_fields(self):
        """Test de création d'un utilisateur avec des champs valides"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        self.assertEqual(user.role, "Client")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_uniqueness_constraint(self):
        """Test de la contrainte d'unicité sur l'email"""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_role_choices(self):
        """Test des choix de rôle valides"""
        # Test rôle Client
        user_client = User.objects.create_user(
            email="client@example.com",
            password="pass123",
            first_name="Client",
            last_name="Test",
            role="Client"
        )
        self.assertEqual(user_client.role, "Client")
        
        # Test rôle Advisor
        user_advisor = User.objects.create_user(
            email="advisor@example.com",
            password="pass123",
            first_name="Advisor",
            last_name="Test",
            role="Advisor"
        )
        self.assertEqual(user_advisor.role, "Advisor")

    def test_optional_fields(self):
        """Test des champs optionnels (âge, genre, poids, taille, etc.)"""
        user = User.objects.create_user(
            email="optional@example.com",
            password="pass123",
            first_name="Test",
            last_name="User",
            role="Client",
            age=30,
            gender="male",
            weight=75.5,
            height=1.75,
            smoker=True,
            children=2,
            region="northeast"
        )
        
        self.assertEqual(user.age, 30)
        self.assertEqual(user.gender, "male")
        self.assertEqual(user.weight, 75.5)
        self.assertEqual(user.height, 1.75)
        self.assertTrue(user.smoker)
        self.assertEqual(user.children, 2)
        self.assertEqual(user.region, "northeast")

    def test_create_superuser(self):
        """Test de création d'un superutilisateur avec les bons attributs"""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            role="Advisor"
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.email, "admin@example.com")

    def test_create_user_without_email_raises_error(self):
        """Test d'erreur lors de la création d'un utilisateur sans email"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="",
                password="pass123",
                first_name="Test",
                last_name="User"
            )
        self.assertIn("L'adresse email est obligatoire", str(context.exception))

    def test_create_superuser_without_is_staff_raises_error(self):
        """Test d'erreur lors de la création d'un superutilisateur sans is_staff=True"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="pass123",
                first_name="Admin",
                last_name="User",
                is_staff=False
            )
        self.assertIn("Superuser must have is_staff=True", str(context.exception))

    def test_create_superuser_without_is_superuser_raises_error(self):
        """Test d'erreur lors de la création d'un superutilisateur sans is_superuser=True"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                password="pass123",
                first_name="Admin",
                last_name="User",
                is_superuser=False
            )
        self.assertIn("Superuser must have is_superuser=True", str(context.exception))

    def test_username_field_is_email(self):
        """Test que le champ username est supprimé et que l'email est l'identifiant principal"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertIsNone(user.username)

    def test_email_normalization(self):
        """Test de la normalisation de l'email"""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            password="pass123",
            first_name="Test",
            last_name="User",
            role="Client"
        )
        self.assertEqual(user.email, "Test@example.com")

    def test_custom_error_message_for_duplicate_email(self):
        """Test des messages d'erreur personnalisés pour email dupliqué"""
        User.objects.create_user(**self.user_data)
        
        user2 = User(
            email="test@example.com",
            first_name="Another",
            last_name="User",
            role="Client"
        )
        
        with self.assertRaises(ValidationError) as context:
            user2.full_clean()
        
        self.assertIn("email", context.exception.message_dict)

    def test_create_user_method(self):
        """Test de la méthode create_user"""
        user = User.objects.create_user(
            email="method@example.com",
            password="testpass",
            first_name="Method",
            last_name="Test",
            role="Client",
            age=25
        )
        
        self.assertIsInstance(user, CustomUser)
        self.assertEqual(user.email, "method@example.com")
        self.assertTrue(user.check_password("testpass"))
        self.assertEqual(user.age, 25)

    def test_create_superuser_method(self):
        """Test de la méthode create_superuser"""
        superuser = User.objects.create_superuser(
            email="super@example.com",
            password="superpass",
            first_name="Super",
            last_name="User"
        )
        
        self.assertIsInstance(superuser, CustomUser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_boundary_values_for_numeric_fields(self):
        """Test des valeurs limites pour les champs numériques"""
        # Valeurs normales
        user1 = User.objects.create_user(
            email="boundary1@example.com",
            password="pass123",
            first_name="Boundary",
            last_name="Test1",
            age=0,
            weight=0.1,
            height=0.1,
            children=0
        )
        self.assertEqual(user1.age, 0)
        self.assertEqual(user1.children, 0)
        
        # Valeurs élevées
        user2 = User.objects.create_user(
            email="boundary2@example.com",
            password="pass123",
            first_name="Boundary",
            last_name="Test2",
            age=120,
            weight=500.0,
            height=3.0,
            children=20
        )
        self.assertEqual(user2.age, 120)
        self.assertEqual(user2.weight, 500.0)

    def test_database_table_name(self):
        """Test que la table CustomUser est créée avec le bon nom"""
        self.assertEqual(CustomUser._meta.db_table, "accounts_customuser")

    def test_inherited_set_password_method(self):
        """Test de la méthode set_password héritée d'AbstractUser"""
        user = User.objects.create_user(**self.user_data)
        
        user.set_password("newpassword123")
        user.save()
        
        self.assertTrue(user.check_password("newpassword123"))
        self.assertFalse(user.check_password("testpass123"))

    def test_inherited_check_password_method(self):
        """Test de la méthode check_password héritée d'AbstractUser"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_bmi_property(self):
        """Test de la propriété bmi"""
        # Test avec des valeurs valides
        user1 = User.objects.create_user(
            email="bmi1@example.com",
            password="pass123",
            first_name="BMI",
            last_name="Test1",
            weight=70,
            height=1.75
        )
        expected_bmi = round(70 / (1.75 ** 2), 1)
        self.assertEqual(user1.bmi, expected_bmi)
        
        # Test sans poids/taille
        user2 = User.objects.create_user(
            email="bmi2@example.com",
            password="pass123",
            first_name="BMI",
            last_name="Test2"
        )
        self.assertIsNone(user2.bmi)
        
        # Test avec taille zéro
        user3 = User.objects.create_user(
            email="bmi3@example.com",
            password="pass123",
            first_name="BMI",
            last_name="Test3",
            weight=70,
            height=0
        )
        self.assertIsNone(user3.bmi)

    def test_get_short_name_method(self):
        """Test de la méthode get_short_name"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), "Jean")

    def test_get_full_name_method(self):
        """Test de la méthode get_full_name"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), "Jean Dupont")
        
        # Test avec des espaces
        user2 = User.objects.create_user(
            email="spaces@example.com",
            password="pass123",
            first_name="  Marie  ",
            last_name="  Martin  ",
            role="Client"
        )
        self.assertEqual(user2.get_full_name(), "Marie Martin")

    def test_str_method(self):
        """Test de la méthode __str__"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), "Jean Dupont (test@example.com)")

    def test_verbose_names(self):
        """Test des noms verbose du modèle"""
        self.assertEqual(CustomUser._meta.verbose_name, "utilisateur")
        self.assertEqual(CustomUser._meta.verbose_name_plural, "utilisateurs")

    def test_required_fields(self):
        """Test des champs requis"""
        self.assertEqual(
            User.REQUIRED_FIELDS,
            ["first_name", "last_name", "role"]
        )

    def test_gender_choices(self):
        """Test des choix de genre"""
        user_female = User.objects.create_user(
            email="female@example.com",
            password="pass123",
            first_name="Jane",
            last_name="Doe",
            gender="female"
        )
        self.assertEqual(user_female.gender, "female")
        
        user_male = User.objects.create_user(
            email="male@example.com",
            password="pass123",
            first_name="John",
            last_name="Doe",
            gender="male"
        )
        self.assertEqual(user_male.gender, "male")

    def test_region_choices(self):
        """Test des choix de région"""
        regions = ["northeast", "northwest", "southeast", "southwest"]
        
        for i, region in enumerate(regions):
            user = User.objects.create_user(
                email=f"region{i}@example.com",
                password="pass123",
                first_name="Region",
                last_name=f"Test{i}",
                region=region
            )
            self.assertEqual(user.region, region)

    def test_default_values(self):
        """Test des valeurs par défaut"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.role, "Client")
        self.assertFalse(user.smoker)
        self.assertEqual(user.children, 0)
        self.assertTrue(user.is_active)

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

class FormsTests(TestCase):
    """
    Tests à réaliser:

    - Test de validation du formulaire CustomAuthenticationForm
    - Test de validation du formulaire CustomUserCreationForm
    - Test des messages d'erreur personnalisés
    - Test des widgets et attributs HTML des champs de formulaire
    - Test des choix de rôle dans le formulaire d'inscription
    - Test de la soumission du formulaire avec des données valides et invalides
    - Test de l'intégration des formulaires dans les vues correspondantes
    - Test du nettoyage des emails
    - Test des contraintes de mot de passe
    - Test des champs requis et optionnels
    - Test des messages de succès et d'erreur lors de la soumission des formulaires
    - Test des redirections après soumission réussie
    - Test des comportements spécifiques aux rôles lors de l'inscription
    - Test de la réinitialisation du formulaire après soumission réussie
    - Test de la persistance des données du formulaire en cas d'erreur de validation
    - Test de la compatibilité avec les navigateurs courants (via les attributs HTML)
    - Test de l'accessibilité des formulaires (via les attributs HTML)
    - Test des performances de rendu des formulaires        
    """

    