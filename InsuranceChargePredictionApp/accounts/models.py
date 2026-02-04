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

    # Caractéristiques liées à l'assurance (Brief requirements)
    age = models.PositiveIntegerField(_("âge"), null=True, blank=True)
    gender = models.CharField(
        _("genre"),
        max_length=10,
        choices=[("female", _("Femme")), ("male", _("Homme"))],
        null=True,
        blank=True,
    )
    weight = models.FloatField(_("poids (kg)"), null=True, blank=True)
    height = models.FloatField(_("taille (m)"), null=True, blank=True)
    smoker = models.BooleanField(_("fumeur"), default=False)
    children = models.PositiveIntegerField(_("nombre d'enfants"), default=0)
    region = models.CharField(
        _("région"),
        max_length=20,
        choices=[
            ("northeast", _("Nord-Est")),
            ("northwest", _("Nord-Ouest")),
            ("southeast", _("Sud-Est")),
            ("southwest", _("Sud-Ouest")),
        ],
        null=True,
        blank=True,
    )

    @property
    def bmi(self):
        if self.height and self.height > 0 and self.weight:
            return round(self.weight / (self.height**2), 2)
        return None

    # Configuration
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        db_table = "accounts_customuser"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name.strip()} {self.last_name.strip()}"

    def get_short_name(self):
        return self.first_name
