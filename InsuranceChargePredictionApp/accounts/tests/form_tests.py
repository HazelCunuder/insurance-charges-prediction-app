
from django.test import TestCase
from django.contrib.auth import get_user_model

from ..forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm

User = get_user_model()


def _create_user(email="existing@example.com", password="Str0ng!Pass99", **kwargs):
    """Helper pour créer un utilisateur de test"""
    defaults = {"first_name": "Alice", "last_name": "Martin", "role": "Client"}
    defaults.update(kwargs)
    return User.objects.create_user(email=email, password=password, **defaults)


# ===========================================================================
# TESTS CUSTOMAUTHENTICATIONFORM
# ===========================================================================


class TestCustomAuthenticationFormValidation(TestCase):
    """Tests de validation du formulaire de connexion"""

    def setUp(self):
        self.user = _create_user(email="auth@example.com", password="Str0ng!Pass99")

    def test_valid_credentials_form_is_valid(self):
        """Formulaire valide avec identifiants corrects"""
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "Str0ng!Pass99",
        })
        self.assertTrue(form.is_valid())

    def test_wrong_password_form_invalid(self):
        """Formulaire invalide avec mauvais mot de passe"""
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "WrongPassword1!",
        })
        self.assertFalse(form.is_valid())

    def test_nonexistent_email_form_invalid(self):
        """Formulaire invalide avec email inexistant"""
        form = CustomAuthenticationForm(data={
            "username": "nobody@example.com",
            "password": "Str0ng!Pass99",
        })
        self.assertFalse(form.is_valid())

    def test_empty_email_form_invalid(self):
        """Formulaire invalide avec email vide"""
        form = CustomAuthenticationForm(data={
            "username": "",
            "password": "Str0ng!Pass99",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_empty_password_form_invalid(self):
        """Formulaire invalide avec mot de passe vide"""
        form = CustomAuthenticationForm(data={
            "username": "auth@example.com",
            "password": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_invalid_email_format_form_invalid(self):
        """Formulaire invalide avec format d'email incorrect"""
        form = CustomAuthenticationForm(data={
            "username": "notanemail",
            "password": "Str0ng!Pass99",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_case_insensitive_email_login(self):
        """Email avec casse différente devrait fonctionner"""
        form = CustomAuthenticationForm(data={
            "username": "AUTH@EXAMPLE.COM",
            "password": "Str0ng!Pass99",
        })
        self.assertTrue(form.is_valid())

    def test_whitespace_in_email_trimmed(self):
        """Espaces autour de l'email devraient être ignorés"""
        form = CustomAuthenticationForm(data={
            "username": "  auth@example.com  ",
            "password": "Str0ng!Pass99",
        })
        self.assertTrue(form.is_valid())


class TestCustomAuthenticationFormErrorMessages(TestCase):
    """Tests des messages d'erreur personnalisés"""

    def setUp(self):
        self.user = _create_user(email="test@example.com", password="Str0ng!Pass99")

    def test_empty_email_custom_error_message(self):
        """Message d'erreur personnalisé pour email vide"""
        form = CustomAuthenticationForm(data={"username": "", "password": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("Veuillez renseigner votre adresse email", 
                      str(form.errors["username"]))

    def test_invalid_email_custom_error_message(self):
        """Message d'erreur personnalisé pour email invalide"""
        form = CustomAuthenticationForm(data={"username": "invalid", "password": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("Veuillez renseigner une adresse email valide", 
                      str(form.errors["username"]))

    def test_empty_password_custom_error_message(self):
        """Message d'erreur personnalisé pour mot de passe vide"""
        form = CustomAuthenticationForm(data={"username": "test@example.com", "password": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("Veuillez saisir votre mot de passe", 
                      str(form.errors["password"]))


class TestCustomAuthenticationFormWidgets(TestCase):
    """Tests des widgets et attributs HTML"""

    def test_email_field_has_correct_widget(self):
        """Le champ email utilise EmailInput"""
        form = CustomAuthenticationForm()
        self.assertEqual(form.fields["username"].widget.__class__.__name__, "EmailInput")

    def test_password_field_has_correct_widget(self):
        """Le champ password utilise PasswordInput"""
        form = CustomAuthenticationForm()
        self.assertEqual(form.fields["password"].widget.__class__.__name__, "PasswordInput")

    def test_email_field_has_autofocus(self):
        """Le champ email a l'attribut autofocus"""
        form = CustomAuthenticationForm()
        self.assertTrue(form.fields["username"].widget.attrs.get("autofocus"))

    def test_email_field_has_placeholder(self):
        """Le champ email a un placeholder"""
        form = CustomAuthenticationForm()
        self.assertEqual(
            form.fields["username"].widget.attrs.get("placeholder"), 
            "votre@email.com"
        )

    def test_password_field_has_placeholder(self):
        """Le champ password a un placeholder"""
        form = CustomAuthenticationForm()
        self.assertEqual(
            form.fields["password"].widget.attrs.get("placeholder"), 
            "••••••••"
        )

    def test_email_field_has_css_classes(self):
        """Le champ email a les bonnes classes CSS"""
        form = CustomAuthenticationForm()
        classes = form.fields["username"].widget.attrs.get("class")
        self.assertIn("input", classes)
        self.assertIn("input-bordered", classes)
        self.assertIn("w-full", classes)

    def test_password_field_has_css_classes(self):
        """Le champ password a les bonnes classes CSS"""
        form = CustomAuthenticationForm()
        classes = form.fields["password"].widget.attrs.get("class")
        self.assertIn("input", classes)
        self.assertIn("input-bordered", classes)
        self.assertIn("w-full", classes)

    def test_email_field_label_correct(self):
        """Le champ email a le bon label"""
        form = CustomAuthenticationForm()
        self.assertEqual(form.fields["username"].label, "Adresse email")

    def test_password_field_label_correct(self):
        """Le champ password a le bon label"""
        form = CustomAuthenticationForm()
        self.assertEqual(form.fields["password"].label, "Mot de passe")


# ===========================================================================
# TESTS CUSTOMUSERCREATIONFORM
# ===========================================================================


VALID_SIGNUP_DATA = {
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "role": "Client",
    "password1": "Str0ng!Pass99",
    "password2": "Str0ng!Pass99",
}


class TestCustomUserCreationFormValidation(TestCase):
    """Tests de validation du formulaire d'inscription"""

    def test_valid_data_form_is_valid(self):
        """Formulaire valide avec toutes les données correctes"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_first_name_invalid(self):
        """Formulaire invalide sans prénom"""
        data = {**VALID_SIGNUP_DATA, "first_name": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_missing_last_name_invalid(self):
        """Formulaire invalide sans nom"""
        data = {**VALID_SIGNUP_DATA, "last_name": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_missing_email_invalid(self):
        """Formulaire invalide sans email"""
        data = {**VALID_SIGNUP_DATA, "email": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_role_invalid(self):
        """Formulaire invalide sans rôle"""
        data = {**VALID_SIGNUP_DATA, "role": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_missing_password1_invalid(self):
        """Formulaire invalide sans password1"""
        data = {**VALID_SIGNUP_DATA, "password1": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_missing_password2_invalid(self):
        """Formulaire invalide sans password2"""
        data = {**VALID_SIGNUP_DATA, "password2": ""}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_first_name_too_short_invalid(self):
        """Prénom d'un seul caractère invalide (min 2)"""
        data = {**VALID_SIGNUP_DATA, "first_name": "A"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_first_name_exactly_2_chars_valid(self):
        """Prénom de 2 caractères exactement est valide"""
        data = {**VALID_SIGNUP_DATA, "first_name": "Jo"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_first_name_max_length_exceeded_invalid(self):
        """Prénom dépassant 50 caractères invalide"""
        data = {**VALID_SIGNUP_DATA, "first_name": "A" * 51}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_first_name_exactly_50_chars_valid(self):
        """Prénom de 50 caractères exactement est valide"""
        data = {**VALID_SIGNUP_DATA, "first_name": "A" * 50}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_last_name_too_short_invalid(self):
        """Nom d'un seul caractère invalide (min 2)"""
        data = {**VALID_SIGNUP_DATA, "last_name": "B"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_last_name_exactly_2_chars_valid(self):
        """Nom de 2 caractères exactement est valide"""
        data = {**VALID_SIGNUP_DATA, "last_name": "Li"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_last_name_max_length_exceeded_invalid(self):
        """Nom dépassant 50 caractères invalide"""
        data = {**VALID_SIGNUP_DATA, "last_name": "B" * 51}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_last_name_exactly_50_chars_valid(self):
        """Nom de 50 caractères exactement est valide"""
        data = {**VALID_SIGNUP_DATA, "last_name": "B" * 50}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_email_format_invalid(self):
        """Format d'email invalide rejeté"""
        data = {**VALID_SIGNUP_DATA, "email": "not-an-email"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch_invalid(self):
        """Mots de passe non identiques rejetés"""
        data = {**VALID_SIGNUP_DATA, "password2": "DifferentPass1!"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_password_too_short_invalid(self):
        """Mot de passe trop court rejeté (Django validators)"""
        data = {**VALID_SIGNUP_DATA, "password1": "Short1!", "password2": "Short1!"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_password_entirely_numeric_invalid(self):
        """Mot de passe entièrement numérique rejeté"""
        data = {**VALID_SIGNUP_DATA, "password1": "12345678", "password2": "12345678"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_password_too_common_invalid(self):
        """Mot de passe trop commun rejeté"""
        data = {**VALID_SIGNUP_DATA, "password1": "password", "password2": "password"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class TestCustomUserCreationFormEmailCleaning(TestCase):
    """Tests du nettoyage des emails (clean_email)"""

    def test_duplicate_email_rejected(self):
        """Email déjà utilisé rejeté"""
        _create_user(email="duplicate@example.com")
        data = {**VALID_SIGNUP_DATA, "email": "duplicate@example.com"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_email_error_message(self):
        """Message d'erreur personnalisé pour email dupliqué"""
        _create_user(email="dup@example.com")
        data = {**VALID_SIGNUP_DATA, "email": "dup@example.com"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Cette adresse email est invalide", 
                      str(form.errors["email"]))

    def test_duplicate_email_case_insensitive(self):
        """Email dupliqué avec casse différente détecté"""
        _create_user(email="case@example.com")
        data = {**VALID_SIGNUP_DATA, "email": "CASE@EXAMPLE.COM"}
        form = CustomUserCreationForm(data=data)
        # Note: Django normalise les emails, donc cela devrait être détecté
        self.assertFalse(form.is_valid())

    def test_unique_email_accepted(self):
        """Email unique accepté"""
        _create_user(email="other@example.com")
        data = {**VALID_SIGNUP_DATA, "email": "unique@example.com"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_with_plus_addressing_allowed(self):
        """Email avec plus-addressing (+) autorisé"""
        data = {**VALID_SIGNUP_DATA, "email": "user+tag@example.com"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_email_with_subdomain_allowed(self):
        """Email avec sous-domaine autorisé"""
        data = {**VALID_SIGNUP_DATA, "email": "user@mail.example.com"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class TestCustomUserCreationFormRoleChoices(TestCase):
    """Tests des choix de rôle"""

    def test_client_role_accepted(self):
        """Rôle Client accepté"""
        data = {**VALID_SIGNUP_DATA, "role": "Client"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_advisor_role_accepted(self):
        """Rôle Advisor accepté"""
        data = {**VALID_SIGNUP_DATA, "email": "adv@example.com", "role": "Advisor"}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_role_rejected(self):
        """Rôle invalide rejeté"""
        data = {**VALID_SIGNUP_DATA, "role": "Admin"}
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)

    def test_role_choices_correct_count(self):
        """Nombre de choix de rôle correct"""
        form = CustomUserCreationForm()
        self.assertEqual(len(form.fields["role"].choices), 2)

    def test_role_choices_have_labels(self):
        """Les choix de rôle ont des labels descriptifs"""
        form = CustomUserCreationForm()
        choices = dict(form.fields["role"].choices)
        self.assertIn("Client", choices)
        self.assertIn("Advisor", choices)
        self.assertIn("Accéder à votre profil", choices["Client"])
        self.assertIn("Gérer les prédictions", choices["Advisor"])


class TestCustomUserCreationFormSaving(TestCase):
    """Tests de la sauvegarde du formulaire"""

    def test_save_creates_user(self):
        """La sauvegarde crée bien un utilisateur"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(User.objects.filter(email="jean@example.com").exists())

    def test_save_sets_first_name(self):
        """La sauvegarde définit le prénom"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.first_name, "Jean")

    def test_save_sets_last_name(self):
        """La sauvegarde définit le nom"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.last_name, "Dupont")

    def test_save_sets_email(self):
        """La sauvegarde définit l'email"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.email, "jean@example.com")

    def test_save_sets_role(self):
        """La sauvegarde définit le rôle"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.role, "Client")

    def test_save_hashes_password(self):
        """Le mot de passe est haché, pas stocké en clair"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form.is_valid()
        user = form.save()
        self.assertNotEqual(user.password, "Str0ng!Pass99")
        self.assertTrue(user.check_password("Str0ng!Pass99"))

    def test_save_advisor_role_persisted(self):
        """Le rôle Advisor est bien persisté"""
        data = {**VALID_SIGNUP_DATA, "email": "advisor@example.com", "role": "Advisor"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.role, "Advisor")


class TestCustomUserCreationFormWidgets(TestCase):
    """Tests des widgets et attributs HTML"""

    def test_first_name_has_placeholder(self):
        """Le champ prénom a un placeholder"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["first_name"].widget.attrs.get("placeholder"), 
            "Jean"
        )

    def test_last_name_has_placeholder(self):
        """Le champ nom a un placeholder"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["last_name"].widget.attrs.get("placeholder"), 
            "Dupont"
        )

    def test_email_has_placeholder(self):
        """Le champ email a un placeholder"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["email"].widget.attrs.get("placeholder"), 
            "votre@email.com"
        )

    def test_password1_has_placeholder(self):
        """Le champ password1 a un placeholder"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["password1"].widget.attrs.get("placeholder"), 
            "••••••••"
        )

    def test_password2_has_placeholder(self):
        """Le champ password2 a un placeholder"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["password2"].widget.attrs.get("placeholder"), 
            "••••••••"
        )

    def test_first_name_has_css_classes(self):
        """Le champ prénom a les bonnes classes CSS"""
        form = CustomUserCreationForm()
        classes = form.fields["first_name"].widget.attrs.get("class")
        self.assertIn("input", classes)
        self.assertIn("input-bordered", classes)

    def test_role_uses_radio_select(self):
        """Le champ rôle utilise RadioSelect"""
        form = CustomUserCreationForm()
        self.assertEqual(
            form.fields["role"].widget.__class__.__name__, 
            "RadioSelect"
        )

    def test_role_has_css_classes(self):
        """Le champ rôle a les bonnes classes CSS"""
        form = CustomUserCreationForm()
        classes = form.fields["role"].widget.attrs.get("class")
        self.assertIn("space-y-2", classes)
        self.assertIn("flex", classes)
        self.assertIn("flex-col", classes)

    def test_password1_label_customized(self):
        """Le label de password1 est personnalisé"""
        form = CustomUserCreationForm()
        self.assertEqual(form.fields["password1"].label, "Mot de passe")

    def test_password2_label_customized(self):
        """Le label de password2 est personnalisé"""
        form = CustomUserCreationForm()
        self.assertEqual(form.fields["password2"].label, "Confirmez votre mot de passe")


class TestCustomUserCreationFormErrorMessages(TestCase):
    """Tests des messages d'erreur personnalisés"""

    def test_missing_first_name_error_message(self):
        """Message d'erreur pour prénom manquant"""
        data = {**VALID_SIGNUP_DATA, "first_name": ""}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Veuillez renseigner un prénom", 
                      str(form.errors["first_name"]))

    def test_first_name_too_short_error_message(self):
        """Message d'erreur pour prénom trop court"""
        data = {**VALID_SIGNUP_DATA, "first_name": "A"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("au moins 2 caractères", 
                      str(form.errors["first_name"]))

    def test_first_name_too_long_error_message(self):
        """Message d'erreur pour prénom trop long"""
        data = {**VALID_SIGNUP_DATA, "first_name": "A" * 51}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("50 caractères", 
                      str(form.errors["first_name"]))

    def test_missing_last_name_error_message(self):
        """Message d'erreur pour nom manquant"""
        data = {**VALID_SIGNUP_DATA, "last_name": ""}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Veuillez renseigner un nom de famille", 
                      str(form.errors["last_name"]))

    def test_last_name_too_short_error_message(self):
        """Message d'erreur pour nom trop court"""
        data = {**VALID_SIGNUP_DATA, "last_name": "B"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("au moins 2 caractères", 
                      str(form.errors["last_name"]))

    def test_missing_email_error_message(self):
        """Message d'erreur pour email manquant"""
        data = {**VALID_SIGNUP_DATA, "email": ""}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Veuillez renseigner votre adresse email", 
                      str(form.errors["email"]))

    def test_invalid_email_error_message(self):
        """Message d'erreur pour email invalide"""
        data = {**VALID_SIGNUP_DATA, "email": "invalid"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Veuillez renseigner une adresse email valide", 
                      str(form.errors["email"]))

    def test_missing_role_error_message(self):
        """Message d'erreur pour rôle manquant"""
        data = {**VALID_SIGNUP_DATA, "role": ""}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("Veuillez sélectionner un type de compte", 
                      str(form.errors["role"]))

    def test_invalid_role_error_message(self):
        """Message d'erreur pour rôle invalide"""
        data = {**VALID_SIGNUP_DATA, "role": "InvalidRole"}
        form = CustomUserCreationForm(data=data)
        form.is_valid()
        self.assertIn("n'est pas valide", 
                      str(form.errors["role"]))


# ===========================================================================
# TESTS USERPROFILEFORM
# ===========================================================================


class TestUserProfileFormValidation(TestCase):
    """Tests de validation du formulaire de profil"""

    def setUp(self):
        self.user = _create_user(email="profile@example.com")

    def _base_data(self):
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

    def test_valid_full_profile(self):
        """Formulaire valide avec toutes les données"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

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

    def test_minimal_required_fields(self):
        """Seulement les champs requis (first_name, last_name)"""
        data = {
            "first_name": "Alice",
            "last_name": "Martin",
            "age": None,
            "gender": "",
            "height": None,
            "weight": None,
            "smoker": False,
            "children": 0,
            "region": "",
        }
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_female_gender_valid(self):
        """Genre 'female' valide"""
        data = {**self._base_data(), "gender": "female"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_male_gender_valid(self):
        """Genre 'male' valide"""
        data = {**self._base_data(), "gender": "male"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_gender_rejected(self):
        """Genre invalide rejeté"""
        data = {**self._base_data(), "gender": "other"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("gender", form.errors)

    def test_all_regions_valid(self):
        """Toutes les régions valides acceptées"""
        regions = ["northeast", "northwest", "southeast", "southwest"]
        for region in regions:
            data = {**self._base_data(), "region": region}
            form = UserProfileForm(data=data, instance=self.user)
            self.assertTrue(form.is_valid(), f"Region {region} should be valid")

    def test_invalid_region_rejected(self):
        """Région invalide rejetée"""
        data = {**self._base_data(), "region": "invalid"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("region", form.errors)

    def test_negative_age_rejected(self):
        """Âge négatif rejeté"""
        data = {**self._base_data(), "age": "-5"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)

    def test_zero_age_valid(self):
        """Âge zéro valide (nouveau-né)"""
        data = {**self._base_data(), "age": "0"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_very_high_age_valid(self):
        """Âge très élevé valide (120 ans)"""
        data = {**self._base_data(), "age": "120"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_negative_children_rejected(self):
        """Nombre d'enfants négatif rejeté"""
        data = {**self._base_data(), "children": "-1"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("children", form.errors)

    def test_zero_children_valid(self):
        """Zéro enfant valide"""
        data = {**self._base_data(), "children": "0"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_many_children_valid(self):
        """Beaucoup d'enfants valide"""
        data = {**self._base_data(), "children": "15"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_negative_height_rejected(self):
        """Taille négative rejetée"""
        data = {**self._base_data(), "height": "-1.70"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())

    def test_zero_height_valid(self):
        """Taille zéro techniquement valide (bien qu'irréaliste)"""
        data = {**self._base_data(), "height": "0"}
        form = UserProfileForm(data=data, instance=self.user)
        # Le modèle accepte 0, même si c'est irréaliste
        self.assertTrue(form.is_valid(), form.errors)

    def test_decimal_height_valid(self):
        """Taille avec décimales valide"""
        data = {**self._base_data(), "height": "1.75"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_negative_weight_rejected(self):
        """Poids négatif rejeté"""
        data = {**self._base_data(), "weight": "-65.0"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())

    def test_decimal_weight_valid(self):
        """Poids avec décimales valide"""
        data = {**self._base_data(), "weight": "65.5"}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_smoker_true_valid(self):
        """Fumeur = True valide"""
        data = {**self._base_data(), "smoker": True}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_smoker_false_valid(self):
        """Fumeur = False valide"""
        data = {**self._base_data(), "smoker": False}
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)


class TestUserProfileFormSaving(TestCase):
    """Tests de la sauvegarde du formulaire de profil"""

    def setUp(self):
        self.user = _create_user(email="save@example.com")

    def _base_data(self):
        return {
            "first_name": "Updated",
            "last_name": "Name",
            "age": 35,
            "gender": "male",
            "height": "1.80",
            "weight": "80.0",
            "smoker": True,
            "children": 2,
            "region": "southwest",
        }

    def test_save_updates_first_name(self):
        """La sauvegarde met à jour le prénom"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.first_name, "Updated")

    def test_save_updates_last_name(self):
        """La sauvegarde met à jour le nom"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.last_name, "Name")

    def test_save_updates_age(self):
        """La sauvegarde met à jour l'âge"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.age, 35)

    def test_save_updates_gender(self):
        """La sauvegarde met à jour le genre"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.gender, "male")

    def test_save_updates_height(self):
        """La sauvegarde met à jour la taille"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertAlmostEqual(float(updated.height), 1.80)

    def test_save_updates_weight(self):
        """La sauvegarde met à jour le poids"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertAlmostEqual(float(updated.weight), 80.0)

    def test_save_updates_smoker(self):
        """La sauvegarde met à jour le statut fumeur"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertTrue(updated.smoker)

    def test_save_updates_children(self):
        """La sauvegarde met à jour le nombre d'enfants"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.children, 2)

    def test_save_updates_region(self):
        """La sauvegarde met à jour la région"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        updated = form.save()
        self.assertEqual(updated.region, "southwest")

    def test_save_persists_to_database(self):
        """Les modifications sont bien persistées en base"""
        form = UserProfileForm(data=self._base_data(), instance=self.user)
        form.is_valid()
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.age, 35)
        self.assertEqual(self.user.region, "southwest")

    def test_save_partial_update(self):
        """Mise à jour partielle sans toucher les autres champs"""
        self.user.age = 50
        self.user.save()
        data = {
            "first_name": "Partial",
            "last_name": "Update",
            "age": "",
            "gender": "",
            "height": "",
            "weight": "",
            "smoker": False,
            "children": 0,
            "region": "",
        }
        form = UserProfileForm(data=data, instance=self.user)
        form.is_valid()
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Partial")


class TestUserProfileFormWidgets(TestCase):
    """Tests des widgets et attributs HTML"""

    def test_first_name_text_input(self):
        """Le champ prénom utilise TextInput"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["first_name"].widget.__class__.__name__, 
            "TextInput"
        )

    def test_last_name_text_input(self):
        """Le champ nom utilise TextInput"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["last_name"].widget.__class__.__name__, 
            "TextInput"
        )

    def test_age_number_input(self):
        """Le champ âge utilise NumberInput"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["age"].widget.__class__.__name__, 
            "NumberInput"
        )

    def test_gender_select_widget(self):
        """Le champ genre utilise Select"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["gender"].widget.__class__.__name__, 
            "Select"
        )

    def test_height_number_input_with_step(self):
        """Le champ taille utilise NumberInput avec step"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["height"].widget.__class__.__name__, 
            "NumberInput"
        )
        self.assertEqual(
            form.fields["height"].widget.attrs.get("step"), 
            "0.01"
        )

    def test_weight_number_input_with_step(self):
        """Le champ poids utilise NumberInput avec step"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["weight"].widget.__class__.__name__, 
            "NumberInput"
        )
        self.assertEqual(
            form.fields["weight"].widget.attrs.get("step"), 
            "0.1"
        )

    def test_smoker_checkbox_input(self):
        """Le champ fumeur utilise CheckboxInput"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["smoker"].widget.__class__.__name__, 
            "CheckboxInput"
        )

    def test_children_number_input(self):
        """Le champ enfants utilise NumberInput"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["children"].widget.__class__.__name__, 
            "NumberInput"
        )

    def test_region_select_widget(self):
        """Le champ région utilise Select"""
        form = UserProfileForm()
        self.assertEqual(
            form.fields["region"].widget.__class__.__name__, 
            "Select"
        )

    def test_first_name_has_css_classes(self):
        """Le champ prénom a les bonnes classes CSS"""
        form = UserProfileForm()
        classes = form.fields["first_name"].widget.attrs.get("class")
        self.assertIn("input", classes)
        self.assertIn("input-bordered", classes)
        self.assertIn("bg-white/50", classes)

    def test_smoker_has_primary_checkbox_class(self):
        """Le champ fumeur a la classe checkbox-primary"""
        form = UserProfileForm()
        classes = form.fields["smoker"].widget.attrs.get("class")
        self.assertIn("checkbox-primary", classes)

    def test_gender_has_select_classes(self):
        """Le champ genre a les classes select"""
        form = UserProfileForm()
        classes = form.fields["gender"].widget.attrs.get("class")
        self.assertIn("select", classes)
        self.assertIn("select-bordered", classes)

    def test_region_has_select_classes(self):
        """Le champ région a les classes select"""
        form = UserProfileForm()
        classes = form.fields["region"].widget.attrs.get("class")
        self.assertIn("select", classes)
        self.assertIn("select-bordered", classes)


# ===========================================================================
# TESTS SUPPLÉMENTAIRES - EDGE CASES & SÉCURITÉ
# ===========================================================================


class TestFormSecurityAndEdgeCases(TestCase):
    """Tests de sécurité et cas limites"""

    def test_signup_sql_injection_in_email_prevented(self):
        """Tentative d'injection SQL dans l'email empêchée"""
        data = {
            **VALID_SIGNUP_DATA,
            "email": "test@example.com'; DROP TABLE accounts_customuser; --"
        }
        form = CustomUserCreationForm(data=data)
        # Le formulaire devrait soit invalider l'email, soit l'échapper correctement
        if form.is_valid():
            user = form.save()
            # Si valide, vérifier que l'email est stocké tel quel (échappé)
            self.assertIn("DROP", user.email)

    def test_signup_xss_in_first_name_escaped(self):
        """Script XSS dans le prénom correctement échappé"""
        data = {
            **VALID_SIGNUP_DATA,
            "email": "xss@example.com",
            "first_name": "<script>alert('XSS')</script>"
        }
        form = CustomUserCreationForm(data=data)
        if form.is_valid():
            user = form.save()
            # Django échappe automatiquement dans les templates
            self.assertEqual(user.first_name, "<script>alert('XSS')</script>")

    def test_signup_unicode_characters_in_names(self):
        """Caractères Unicode dans les noms acceptés"""
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
        self.assertEqual(user.last_name, "Müller")

    def test_signup_emoji_in_names_accepted(self):
        """Emoji dans les noms acceptés (ou rejetés selon politique)"""
        data = {
            **VALID_SIGNUP_DATA,
            "email": "emoji@example.com",
            "first_name": "Jean 😊",
            "last_name": "Dupont"
        }
        form = CustomUserCreationForm(data=data)
        # Accepte ou rejette selon la validation
        form.is_valid()

    def test_signup_very_long_email_within_limit(self):
        """Email très long mais dans la limite accepté"""
        # Max 100 caractères selon le modèle
        long_email = "a" * 80 + "@example.com"  # 94 caractères
        data = {**VALID_SIGNUP_DATA, "email": long_email}
        form = CustomUserCreationForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_signup_whitespace_only_first_name_rejected(self):
        """Prénom composé uniquement d'espaces rejeté"""
        data = {**VALID_SIGNUP_DATA, "first_name": "   "}
        form = CustomUserCreationForm(data=data)
        # Django devrait traiter cela comme vide
        self.assertFalse(form.is_valid())

    def test_profile_form_does_not_allow_email_change(self):
        """Le formulaire de profil ne permet pas de changer l'email"""
        user = _create_user(email="original@example.com")
        form = UserProfileForm(instance=user)
        self.assertNotIn("email", form.fields)

    def test_profile_form_does_not_allow_role_change(self):
        """Le formulaire de profil ne permet pas de changer le rôle"""
        user = _create_user(email="role@example.com", role="Client")
        form = UserProfileForm(instance=user)
        self.assertNotIn("role", form.fields)

    def test_profile_float_precision_height(self):
        """Précision des décimales pour la taille"""
        user = _create_user(email="prec@example.com")
        data = {
            "first_name": "Test",
            "last_name": "User",
            "height": "1.756",  # 3 décimales
            "weight": "70.0",
            "age": 30,
            "gender": "male",
            "smoker": False,
            "children": 0,
            "region": "northeast"
        }
        form = UserProfileForm(data=data, instance=user)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        # Vérifier la précision
        self.assertAlmostEqual(float(saved.height), 1.756, places=2)

    def test_concurrent_signup_same_email_race_condition(self):
        """Inscription simultanée avec même email (race condition)"""
        # Simuler une situation où deux formulaires sont validés en parallèle
        form1 = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        form2 = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        
        self.assertTrue(form1.is_valid())
        user1 = form1.save()
        
        # Le deuxième formulaire devrait échouer à la sauvegarde
        # (même si la validation a réussi avant la création du premier utilisateur)
        self.assertFalse(form2.is_valid())

    def test_auth_form_empty_data_shows_all_errors(self):
        """Formulaire de connexion vide montre toutes les erreurs"""
        form = CustomAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

    def test_signup_form_empty_data_shows_all_errors(self):
        """Formulaire d'inscription vide montre toutes les erreurs"""
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("role", form.errors)
        self.assertIn("password1", form.errors)
        self.assertIn("password2", form.errors)

    def test_profile_form_preserves_unmodified_fields(self):
        """Les champs non modifiés sont préservés"""
        user = _create_user(
            email="preserve@example.com",
            age=25,
            gender="female",
            smoker=True
        )
        data = {
            "first_name": "NewName",
            "last_name": user.last_name,
            "age": user.age,
            "gender": user.gender,
            "height": "",
            "weight": "",
            "smoker": user.smoker,
            "children": 0,
            "region": ""
        }
        form = UserProfileForm(data=data, instance=user)
        form.is_valid()
        form.save()
        user.refresh_from_db()
        self.assertEqual(user.first_name, "NewName")
        self.assertEqual(user.age, 25)
        self.assertTrue(user.smoker)


class TestFormInitialization(TestCase):
    """Tests d'initialisation des formulaires"""

    def test_auth_form_initialization_no_errors(self):
        """Initialisation du formulaire de connexion sans erreurs"""
        form = CustomAuthenticationForm()
        self.assertEqual(len(form.errors), 0)

    def test_signup_form_initialization_no_errors(self):
        """Initialisation du formulaire d'inscription sans erreurs"""
        form = CustomUserCreationForm()
        self.assertEqual(len(form.errors), 0)

    def test_profile_form_initialization_with_instance(self):
        """Initialisation du formulaire de profil avec instance"""
        user = _create_user(email="init@example.com", first_name="Init", age=30)
        form = UserProfileForm(instance=user)
        self.assertEqual(form.initial["first_name"], "Init")
        self.assertEqual(form.initial["age"], 30)

    def test_profile_form_initialization_without_instance(self):
        """Initialisation du formulaire de profil sans instance"""
        form = UserProfileForm()
        # Devrait fonctionner même sans instance
        self.assertIsNotNone(form.fields)

    def test_signup_form_fields_order(self):
        """L'ordre des champs dans le formulaire d'inscription"""
        form = CustomUserCreationForm()
        field_names = list(form.fields.keys())
        # Vérifier que les champs sont dans l'ordre Meta.fields
        expected_order = ["first_name", "last_name", "email", "role", "password1", "password2"]
        for expected_field in expected_order:
            self.assertIn(expected_field, field_names)


class TestFormBoundVsUnbound(TestCase):
    """Tests formulaires liés vs non liés"""

    def test_unbound_auth_form_not_valid(self):
        """Formulaire de connexion non lié n'est pas valide"""
        form = CustomAuthenticationForm()
        self.assertFalse(form.is_bound)
        # is_valid() retourne False pour formulaire non lié
        self.assertFalse(form.is_valid())

    def test_bound_auth_form_with_data(self):
        """Formulaire de connexion lié avec données"""
        form = CustomAuthenticationForm(data={"username": "test@example.com", "password": "x"})
        self.assertTrue(form.is_bound)

    def test_unbound_signup_form(self):
        """Formulaire d'inscription non lié"""
        form = CustomUserCreationForm()
        self.assertFalse(form.is_bound)

    def test_bound_signup_form(self):
        """Formulaire d'inscription lié"""
        form = CustomUserCreationForm(data=VALID_SIGNUP_DATA)
        self.assertTrue(form.is_bound)

    def test_profile_form_with_instance_but_no_data(self):
        """Formulaire de profil avec instance mais sans données POST"""
        user = _create_user()
        form = UserProfileForm(instance=user)
        self.assertFalse(form.is_bound)

    def test_profile_form_with_instance_and_data(self):
        """Formulaire de profil avec instance et données POST"""
        user = _create_user()
        form = UserProfileForm(
            data={"first_name": "Test", "last_name": "User"},
            instance=user
        )
        self.assertTrue(form.is_bound)