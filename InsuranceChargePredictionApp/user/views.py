# user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import CustomUser

class LoginView(FormView):
    template_name = 'user/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('predict:dashboard')  # À adapter selon votre structure
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Bienvenue {user.get_full_name()} !")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Email ou mot de passe incorrect.")
        return super().form_invalid(form)

class SignupView(FormView):
    template_name = 'user/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('user:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = form.cleaned_data['role']
        user.save()
        messages.success(
            self.request,
            "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Corrigez les erreurs ci-dessous.")
        return super().form_invalid(form)

class LogoutView(RedirectView):
    url = reverse_lazy('user:login')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Vous avez été déconnecté.")
        return super().get(request, *args, **kwargs)

# Vues basées sur des fonctions (alternative si préféré)
@login_required
def profile(request):
    return render(request, 'user/profile.html', {'user': request.user})