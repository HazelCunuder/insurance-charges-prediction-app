from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomAuthenticationForm, CustomUserCreationForm, UserProfileForm
from .models import CustomUser


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("home") # Redirige vers l'accueil par défaut

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Bienvenue {user.get_full_name()} !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Email ou mot de passe incorrect.")
        return super().form_invalid(form)


class SignupView(FormView):
    template_name = "accounts/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = form.cleaned_data["role"]
        user.save()
        messages.success(self.request,"Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Corrigez les erreurs ci-dessous.")
        return super().form_invalid(form)


class LogoutView(RedirectView):
    url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
        return super().get(request, *args, **kwargs)


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Erreur lors de la mise à jour.")
    else:
        form = UserProfileForm(instance=request.user)
        return render(request, "accounts/profile.html", {"user": request.user, "form": form})