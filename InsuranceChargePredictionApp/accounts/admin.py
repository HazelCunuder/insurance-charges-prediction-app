# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserPrediction

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

@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_age', 'bmi', 'user_smoker', 'created_at')
    list_filter = ('user_smoker', 'user_gender', 'user_region')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'bmi')
    ordering = ('-created_at',)
    
    def bmi(self, obj):
        return obj.bmi
    bmi.short_description = 'IMC'