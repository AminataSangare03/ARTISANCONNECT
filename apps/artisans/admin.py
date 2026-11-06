from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Artisan, Realisation


@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('photo_thumb', 'nom_artisan', 'metier', 'ville_quartier', 'tarif_fcfa', 'experience_display', 'dispo_badge')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'ville', 'quartier', 'metier__nom')
    list_filter = ('disponibilite', 'metier', 'ville')
    ordering = ('-created_at',)

    @admin.display(description='Photo')
    def photo_thumb(self, obj):
        if obj.photo_profil:
            return format_html('<img src="{}" class="ac-admin-thumb" alt="{}">', obj.photo_profil.url, str(obj))
        return mark_safe('<span class="ac-badge ac-badge-muted">Sans photo</span>')

    @admin.display(description='Artisan', ordering='user__last_name')
    def nom_artisan(self, obj):
        return obj.user.get_full_name() or obj.user.email

    @admin.display(description='Localisation')
    def ville_quartier(self, obj):
        parts = [p for p in [obj.quartier, obj.ville] if p]
        return ', '.join(parts) or '-'

    @admin.display(description='Tarif indicatif', ordering='tarif_indicatif')
    def tarif_fcfa(self, obj):
        return f'{int(obj.tarif_indicatif):,} FCFA'.replace(',', ' ')

    @admin.display(description='Expérience')
    def experience_display(self, obj):
        return f'{obj.experience} ans'

    @admin.display(description='Disponibilité')
    def dispo_badge(self, obj):
        if obj.disponibilite:
            return mark_safe('<span class="ac-badge ac-badge-success">Disponible</span>')
        return mark_safe('<span class="ac-badge ac-badge-muted">Occupé</span>')


@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ('image_thumb', 'titre', 'artisan', 'date_realisation')
    search_fields = ('titre', 'description', 'artisan__user__first_name', 'artisan__user__last_name', 'artisan__user__email')
    list_filter = ('date_realisation',)

    @admin.display(description='Aperçu')
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="ac-admin-thumb" style="border-radius: 6px;" alt="{}">', obj.image.url, obj.titre)
        return mark_safe('<span class="ac-badge ac-badge-muted">Sans image</span>')
