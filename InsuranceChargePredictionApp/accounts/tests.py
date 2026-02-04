from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()


class CustomUserTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(str(user), "Test User (test@example.com)")

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123",
            first_name="Admin",
            last_name="User",
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_user_duplicate_email(self):
        User.objects.create_user(email="test@example.com", password="password123")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="test@example.com", password="password456")

    def test_bmi_calculation(self):
        user = User.objects.create_user(
            email="bmi@example.com",
            password="password",
            weight=70,  # kg
            height=1.75,  # meters
        )
        # BMI = 70 / (1.75 * 1.75) = 22.857... -> rounded to 22.86
        self.assertEqual(user.bmi, 22.86)

    def test_bmi_calculation_missing_data(self):
        user = User.objects.create_user(
            email="nobmi@example.com", password="password", weight=70
        )
        self.assertIsNone(user.bmi)

        user.weight = None
        user.height = 1.75
        self.assertIsNone(user.bmi)
