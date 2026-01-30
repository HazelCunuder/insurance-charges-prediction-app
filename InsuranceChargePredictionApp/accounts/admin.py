from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Champs affichés dans la liste
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Champs dans le formulaire d'édition
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Champs pour la création d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    # Utiliser email comme champ principal
    readonly_fields = ('last_login', 'date_joined')