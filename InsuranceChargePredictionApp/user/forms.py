from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion avec email comme identifiant principal"""

    username = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "votre@email.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "••••••••",
            }
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription complet avec rôle et validation email"""

    ROLE_CHOICES = [
        ("Client", "Client - Obtenir des prédictions d'assurance"),
        ("Advisor", "Conseiller - Gérer les prédictions clients"),
    ]

    first_name = forms.CharField(
        label="Prénom",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "Jean",
            }
        ),
    )
    last_name = forms.CharField(
        label="Nom",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "Dupont",
            }
        ),
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "votre@email.com",
            }
        ),
    )
    role = forms.ChoiceField(
        label="Type de compte",
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "space-y-2"}),
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs de mot de passe
        self.fields["password1"].widget.attrs.update(
            {
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "••••••••",
            }
        )
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].widget.attrs.update(
            {
                "class": "input input-bordered w-full bg-white/50 backdrop-blur-sm transition-all focus:input-primary",
                "placeholder": "••••••••",
            }
        )
        self.fields["password2"].label = "Confirmation du mot de passe"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
