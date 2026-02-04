from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from accounts.models import CustomUser


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
            role="Client",
        )
        self.assertEqual(user_client.role, "Client")

        # Test rôle Advisor
        user_advisor = User.objects.create_user(
            email="advisor@example.com",
            password="pass123",
            first_name="Advisor",
            last_name="Test",
            role="Advisor",
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
            region="northeast",
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
            role="Advisor",
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.email, "admin@example.com")

    def test_create_user_without_email_raises_error(self):
        """Test d'erreur lors de la création d'un utilisateur sans email"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="", password="pass123", first_name="Test", last_name="User"
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
                is_staff=False,
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
                is_superuser=False,
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
            role="Client",
        )
        self.assertEqual(user.email, "Test@example.com")

    def test_custom_error_message_for_duplicate_email(self):
        """Test des messages d'erreur personnalisés pour email dupliqué"""
        User.objects.create_user(**self.user_data)

        user2 = User(
            email="test@example.com",
            first_name="Another",
            last_name="User",
            role="Client",
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
            age=25,
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
            last_name="User",
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
            children=0,
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
            children=20,
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
            height=1.75,
        )
        expected_bmi = round(70 / (1.75**2), 2)
        self.assertEqual(user1.bmi, expected_bmi)

        # Test sans poids/taille
        user2 = User.objects.create_user(
            email="bmi2@example.com",
            password="pass123",
            first_name="BMI",
            last_name="Test2",
        )
        self.assertIsNone(user2.bmi)

        # Test avec taille zéro
        user3 = User.objects.create_user(
            email="bmi3@example.com",
            password="pass123",
            first_name="BMI",
            last_name="Test3",
            weight=70,
            height=0,
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
            role="Client",
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
        self.assertEqual(User.REQUIRED_FIELDS, ["first_name", "last_name", "role"])

    def test_gender_choices(self):
        """Test des choix de genre"""
        user_female = User.objects.create_user(
            email="female@example.com",
            password="pass123",
            first_name="Jane",
            last_name="Doe",
            gender="female",
        )
        self.assertEqual(user_female.gender, "female")

        user_male = User.objects.create_user(
            email="male@example.com",
            password="pass123",
            first_name="John",
            last_name="Doe",
            gender="male",
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
                region=region,
            )
            self.assertEqual(user.region, region)

    def test_default_values(self):
        """Test des valeurs par défaut"""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.role, "Client")
        self.assertFalse(user.smoker)
        self.assertEqual(user.children, 0)
        self.assertTrue(user.is_active)
