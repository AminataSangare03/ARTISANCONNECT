from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Client, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role_badge', 'statut_badge', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    readonly_fields = ('date_joined', 'updated_at')
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role')}),
    )

    @admin.display(description='Rôle')
    def role_badge(self, obj):
        colors = {
            'ADMIN': 'ac-badge-admin',
            'ARTISAN': 'ac-badge-artisan',
            'CLIENT': 'ac-badge-client',
        }
        cls = colors.get(obj.role, 'ac-badge-muted')
        return format_html('<span class="ac-badge {}">{}</span>', cls, obj.get_role_display())

    @admin.display(description='Statut')
    def statut_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span class="ac-badge ac-badge-success">Actif</span>')
        return mark_safe('<span class="ac-badge ac-badge-danger">Inactif</span>')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'ville', 'quartier')
    search_fields = ('user__email', 'ville', 'quartier')
