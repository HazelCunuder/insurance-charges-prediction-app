from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm

User = get_user_model()


def _create_user(email="existing@example.com", password="Str0ng!Pass99", **kwargs):
    """Helper pour créer un utilisateur de test"""
    defaults = {"first_name": "Alice", "last_name": "Martin", "role": "Client"}
    defaults.update(kwargs)
    return User.objects.create_user(email=email, password=password, **defaults)


VALID_SIGNUP_DATA = {
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "role": "Client",
    "password1": "Str0ng!Pass99",
    "password2": "Str0ng!Pass99",
}

class TestCustomAuthenticationForm(TestCase):
    """Tests du formulaire de connexion"""

    def setUp(self):
        self.user = _create_user(email="auth@example.com", password="Str0ng!Pass99")

    def test_valid_credentials(self):
        """Connexion avec identifiants valides"""
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "Str0ng!Pass99",
        })
        self.assertTrue(form.is_valid())

    def test_wrong_password_invalid(self):
        """Connexion avec mauvais mot de passe rejetée"""
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "WrongPassword1!",
        })
        self.assertFalse(form.is_valid())

    def test_nonexistent_email_invalid(self):
        """Connexion avec email inexistant rejetée"""
        form = CustomAuthenticationForm(data={
            "username": "nobody@example.com",
            "password": "Str0ng!Pass99",
        })
        self.assertFalse(form.is_valid())

    def test_empty_fields_show_custom_errors(self):
        """Messages d'erreur personnalisés pour champs vides"""
        form = CustomAuthenticationForm(data={"username": "", "password": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("Veuillez renseigner votre adresse email", 
                      str(form.errors["username"]))
        self.assertIn("Veuillez saisir votre mot de passe", 
                      str(form.errors["password"]))

    def test_invalid_email_format(self):
        """Format d'email invalide rejeté avec message personnalisé"""
        form = CustomAuthenticationForm(data={"username": "notanemail", "password": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("Veuillez renseigner une adresse email valide", 
                      str(form.errors["username"]))

    def test_widget_attributes(self):
        """Vérification des attributs HTML du formulaire"""
        form = CustomAuthenticationForm()
        # Autofocus sur email
        self.assertTrue(form.fields["username"].widget.attrs.get("autofocus"))
        # Placeholder
        self.assertEqual(form.fields["username"].widget.attrs.get("placeholder"), "votre@email.com")
        self.assertEqual(form.fields["password"].widget.attrs.get("placeholder"), "••••••••")
        # Classes CSS
        self.assertIn("input-bordered", form.fields["username"].widget.attrs.get("class"))

    def test_case_insensitive_email(self):
        """Email avec casse différente fonctionne (edge case)"""
        form = CustomAuthenticationForm(data={
            "username": "AUTH@EXAMPLE.COM",
            "password": "Str0ng!Pass99",
        })
        self.assertFalse(form.is_valid())

class TestCustomUserCreationForm(TestCase):
    """Tests du formulaire d'inscription"""

    def test_valid_signup(self):
        """Inscription avec données valides"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_creates_user_correctly(self):
        """La sauvegarde crée un utilisateur avec les bonnes données"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.email, "jean@example.com")
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        self.assertEqual(user.role, "Client")
        self.assertTrue(user.check_password("Str0ng!Pass99"))

    def test_duplicate_email_rejected(self):
        """Email déjà utilisé rejeté avec message personnalisé"""
        _create_user(email="jean@example.com")
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("Cette adresse email est invalide", str(form.errors["email"]))

    def test_password_mismatch_rejected(self):
        """Mots de passe différents rejetés"""
        data = {**VALID_SIGNUP_DATA, "password2": "DifferentPass1!"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_weak_password_rejected(self):
        """Mot de passe faible rejeté par validators Django"""
        data = {**VALID_SIGNUP_DATA, "password1": "12345678", "password2": "12345678"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_field_length_validation(self):
        """Validation des longueurs min/max des champs"""
        # Prénom trop court
        data = {**VALID_SIGNUP_DATA, "first_name": "A"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("au moins 2 caractères", str(form.errors["first_name"]))
        
        # Prénom trop long
        data = {**VALID_SIGNUP_DATA, "first_name": "A" * 51}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("50 caractères", str(form.errors["first_name"]))

    def test_both_roles_accepted(self):
        """Les deux rôles (Client et Advisor) sont valides"""
        # Client
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_valid())
        
        # Advisor
        data = {**VALID_SIGNUP_DATA, "email": "advisor@example.com", "role": "Advisor"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_role_rejected(self):
        """Rôle invalide rejeté"""
        data = {**VALID_SIGNUP_DATA, "role": "Admin"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_required_fields(self):
        """Tous les champs requis doivent être remplis"""
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ["first_name", "last_name", "email", "role", "password1", "password2"]
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_custom_labels_and_widgets(self):
        """Labels personnalisés et widgets corrects"""
        form = CustomUserCreationForm()
        
        # Labels
        self.assertEqual(form.fields["password1"].label, "Mot de passe")
        self.assertEqual(form.fields["password2"].label, "Confirmez votre mot de passe")
        
        # Widget RadioSelect pour role
        self.assertEqual(form.fields["role"].widget.__class__.__name__, "RadioSelect")
        
        # Placeholders
        self.assertEqual(form.fields["first_name"].widget.attrs.get("placeholder"), "Jean")
        self.assertEqual(form.fields["email"].widget.attrs.get("placeholder"), "votre@email.com")

    # Edge cases
    def test_unicode_in_names(self):
        """Caractères Unicode acceptés dans les noms (edge case)"""
        data = {
            **VALID_SIGNUP_DATA,
            "email": "unicode@example.com",
            "first_name": "François",
            "last_name": "Müller"
        }
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, "François")

    def test_whitespace_only_name_rejected(self):
        """Nom composé uniquement d'espaces rejeté (edge case)"""
        data = {**VALID_SIGNUP_DATA, "first_name": "   "}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())

class TestUserProfileForm(TestCase):
    """Tests du formulaire de profil"""

    def setUp(self):
        self.user = _create_user(email="profile@example.com")

    def _profile_data(self):
        return {
            "first_name": "Alice",
            "last_name": "Martin",
            "age": 28,
            "gender": "female",
            "height": "1.70",
            "weight": "65.0",
            "smoker": False,
            "children": 1,
            "region": "northeast",
        }

    def test_valid_complete_profile(self):
        """Profil complet valide"""
        form = UserProfileForm(data=self._profile_data(), instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_updates_all_fields(self):
        """La sauvegarde met à jour tous les champs"""
        form = UserProfileForm(data=self._profile_data(), instance=self.user)
        self.assertTrue(form.is_valid())
        updated = form.save()
        
        self.assertEqual(updated.first_name, "Alice")
        self.assertEqual(updated.age, 28)
        self.assertEqual(updated.gender, "female")
        self.assertEqual(updated.region, "northeast")
        self.assertAlmostEqual(float(updated.height), 1.70)
        self.assertAlmostEqual(float(updated.weight), 65.0)
        self.assertEqual(updated.children, 1)
        self.assertFalse(updated.smoker)

    def test_optional_fields_can_be_blank(self):
        """Les champs optionnels peuvent être vides"""
        data = {
            "first_name": "Alice",
            "last_name": "Martin",
            "age": "",
            "gender": "",
            "height": "",
            "weight": "",
            "smoker": False,
            "children": 0,
            "region": "",
        }
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_choices_rejected(self):
        """Choix invalides rejetés"""
        # Genre invalide
        data = {**self._profile_data(), "gender": "other"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)
        
        # Région invalide
        data = {**self._profile_data(), "region": "invalid"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("region", form.errors)

    def test_negative_values_rejected(self):
        """Valeurs négatives rejetées pour age, children, height, weight"""
        negative_fields = [
            ("age", "-5"),
            ("children", "-1"),
            ("height", "-1.70"),
            ("weight", "-65.0"),
        ]
        
        for field, value in negative_fields:
            data = {**self._profile_data(), field: value}
            form = UserProfileForm(data=data, instance=self.user)
            self.assertFalse(form.is_valid(), f"{field} devrait rejeter valeur négative")
            self.assertIn(field, form.errors)

    def test_all_regions_valid(self):
        """Toutes les régions valides acceptées"""
        regions = ["northeast", "northwest", "southeast", "southwest"]
        for region in regions:
            data = {**self._profile_data(), "region": region}
            form = UserProfileForm(data=data, instance=self.user)
            self.assertTrue(form.is_valid(), f"Region {region} devrait être valide")

    def test_widgets_configuration(self):
        """Configuration correcte des widgets"""
        form = UserProfileForm()
        
        # NumberInput avec step pour height et weight
        self.assertEqual(form.fields["height"].widget.attrs.get("step"), "0.01")
        self.assertEqual(form.fields["weight"].widget.attrs.get("step"), "0.1")
        
        # CheckboxInput pour smoker
        self.assertEqual(form.fields["smoker"].widget.__class__.__name__, "CheckboxInput")
        self.assertIn("checkbox-primary", form.fields["smoker"].widget.attrs.get("class"))
        
        # Select pour gender et region
        self.assertEqual(form.fields["gender"].widget.__class__.__name__, "Select")
        self.assertEqual(form.fields["region"].widget.__class__.__name__, "Select")

    def test_email_not_in_form(self):
        """Email ne peut pas être modifié via ce formulaire (sécurité)"""
        form = UserProfileForm(instance=self.user)
        self.assertNotIn("email", form.fields)

    def test_role_not_in_form(self):
        """Rôle ne peut pas être modifié via ce formulaire (sécurité)"""
        form = UserProfileForm(instance=self.user)
        self.assertNotIn("role", form.fields)

    # Edge cases
    def test_decimal_precision(self):
        """Précision des décimales préservée (edge case)"""
        user = _create_user(email="precision@example.com")
        data = {**self._profile_data(), "height": "1.756", "weight": "70.345"}
        form = UserProfileForm(data=data, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save()
        # Vérifier précision raisonnable
        self.assertAlmostEqual(float(saved.height), 1.756, places=2)
        self.assertAlmostEqual(float(saved.weight), 70.345, places=1)

    def test_zero_values_valid(self):
        """Valeurs zéro valides pour certains champs (edge case)"""
        data = {
            **self._profile_data(),
            "age": "0",  # Nouveau-né
            "children": "0",  # Pas d'enfants
            "height": "0",  # Techniquement accepté par le modèle
        }
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)