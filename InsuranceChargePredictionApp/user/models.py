from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse email est obligatoire"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé étendant AbstractUser de Django.
    Remplace complètement l'ancien UserAuthentification vulnérable.
    """

    ROLE_CHOICES = [("Client", _("Client")), ("Advisor", _("Conseiller"))]

    # Suppression du champ username (utilisation de l'email comme identifiant principal)
    username = None

    # Champs personnalisés
    email = models.EmailField(
        _("adresse email"),
        unique=True,
        max_length=100,
        error_messages={
            "unique": _("Un utilisateur avec cette adresse email existe déjà."),
        },
    )
    first_name = models.CharField(_("prénom"), max_length=50)
    last_name = models.CharField(_("nom de famille"), max_length=30)
    role = models.CharField(
        _("rôle"), max_length=10, choices=ROLE_CHOICES, default="Client"
    )

    # Configuration
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        db_table = "user_customuser"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class UserPrediction(models.Model):  # Correction de la faute de frappe "Predictiction"
    """
    Modèle pour les prédictions d'assurance liées à un utilisateur.
    Remplace l'ancien UserPredictiction avec calculs sécurisés.
    """

    GENDER_CHOICES = [("female", _("Femme")), ("male", _("Homme"))]
    SMOKER_CHOICES = [("yes", _("Oui")), ("no", _("Non"))]
    REGION_CHOICES = [
        ("northeast", _("Nord-Est")),
        ("northwest", _("Nord-Ouest")),
        ("southeast", _("Sud-Est")),
        ("southwest", _("Sud-Ouest")),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="predictions",
        verbose_name=_("utilisateur"),
    )
    user_age = models.PositiveIntegerField(_("âge"))
    user_gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, verbose_name=_("genre")
    )
    user_height = models.FloatField(_("taille (en m)"))
    user_weight = models.FloatField(_("poids (en kg)"))
    user_smoker = models.CharField(
        max_length=3, choices=SMOKER_CHOICES, verbose_name=_("fumeur ?")
    )
    user_children = models.PositiveIntegerField(_("nombre d'enfants"))
    user_region = models.CharField(
        max_length=9, choices=REGION_CHOICES, verbose_name=_("région de résidence")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("date de création")
    )

    class Meta:
        verbose_name = _("prédiction")
        verbose_name_plural = _("prédictions")
        db_table = "user_prediction"
        ordering = ["-created_at"]

    @property
    def bmi(self):
        """Calcule l'IMC en évitant les divisions par zéro"""
        if self.user_height and self.user_height > 0:
            return round(self.user_weight / (self.user_height**2), 1)
        return None

    def __str__(self):
        gender_str = _("femme") if self.user_gender == "female" else _("homme")
        smoker_str = _("fumeur") if self.user_smoker == "yes" else _("non-fumeur")
        bmi_str = f"IMC {self.bmi}" if self.bmi else _("IMC indisponible")
        return (
            f"Prédiction #{self.id} - {gender_str}, {self.user_age} ans, "
            f"{smoker_str}, {bmi_str}, {self.user_children} enfant(s)"
        )
