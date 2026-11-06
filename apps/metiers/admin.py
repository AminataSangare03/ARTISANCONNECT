from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Metier


@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = ('image_thumb', 'nom', 'statut_badge', 'created_at')
    search_fields = ('nom', 'description')
    list_filter = ('is_active',)
    ordering = ('nom',)

    @admin.display(description='Illustration')
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="ac-admin-thumb" style="border-radius: 6px;" alt="{}">', obj.image.url, obj.nom)
        return mark_safe('<span class="ac-badge ac-badge-muted">Sans visuel</span>')

    @admin.display(description='Statut', ordering='is_active')
    def statut_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span class="ac-badge ac-badge-success">Actif</span>')
        return mark_safe('<span class="ac-badge ac-badge-danger">Inactif</span>')
