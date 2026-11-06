from django.contrib import admin
from django.utils.html import format_html

from .models import DemandeService


@admin.register(DemandeService)
class DemandeServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'client_nom', 'metier', 'ville_quartier', 'budget_fcfa', 'statut_badge', 'created_at')
    search_fields = ('titre', 'description', 'client__user__email', 'client__user__first_name', 'client__user__last_name', 'ville', 'quartier')
    list_filter = ('statut', 'metier', 'ville')
    ordering = ('-created_at',)

    @admin.display(description='Client', ordering='client__user__last_name')
    def client_nom(self, obj):
        return obj.client.user.get_full_name() or obj.client.user.email

    @admin.display(description='Localisation')
    def ville_quartier(self, obj):
        parts = [p for p in [obj.quartier, obj.ville] if p]
        return ', '.join(parts) or '-'

    @admin.display(description='Budget indicatif', ordering='budget_indicatif')
    def budget_fcfa(self, obj):
        return f'{int(obj.budget_indicatif):,} FCFA'.replace(',', ' ')

    @admin.display(description='Statut', ordering='statut')
    def statut_badge(self, obj):
        classes = {
            'EN_ATTENTE': 'ac-badge-warning',
            'EN_COURS': 'ac-badge-artisan',
            'ACCEPTEE': 'ac-badge-success',
            'TERMINEE': 'ac-badge-success',
            'ANNULEE': 'ac-badge-danger',
        }
        cls = classes.get(obj.statut, 'ac-badge-muted')
        return format_html('<span class="ac-badge {}">{}</span>', cls, obj.get_statut_display())
