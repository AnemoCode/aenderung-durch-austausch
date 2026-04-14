from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'name', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'name']
    list_filter = ['is_staff', 'is_active']

    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        (_('Persönliche Daten'), {'fields': ['name']}),
        (_('Berechtigungen'), {'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']}),
        (_('Wichtige Daten'), {'fields': ['last_login', 'date_joined']}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'name', 'password1', 'password2'],
        }),
    ]

    # BaseUserAdmin expects a `username_field`; map it to email
    readonly_fields = ['last_login', 'date_joined']
