from django.contrib import admin
from django.utils.html import format_html

from .models import Commande


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_nom', 'artisan_nom', 'montant_total', 'statut_badge', 'created_at')
    search_fields = ('client__user__email', 'client__user__first_name', 'client__user__last_name', 'artisan__user__email', 'artisan__user__first_name', 'artisan__user__last_name')
    list_filter = ('statut',)
    ordering = ('-created_at',)

    @admin.display(description='Client', ordering='client__user__last_name')
    def client_nom(self, obj):
        return obj.client.user.get_full_name() or obj.client.user.email

    @admin.display(description='Artisan', ordering='artisan__user__last_name')
    def artisan_nom(self, obj):
        return obj.artisan.user.get_full_name() or obj.artisan.user.email

    @admin.display(description='Montant validé', ordering='devis__montant')
    def montant_total(self, obj):
        if obj.devis and obj.devis.montant:
            return f'{int(obj.devis.montant):,} FCFA'.replace(',', ' ')
        return '-'

    @admin.display(description='Statut', ordering='statut')
    def statut_badge(self, obj):
        classes = {
            'EN_ATTENTE': 'ac-badge-warning',
            'CONFIRMEE': 'ac-badge-client',
            'EN_COURS': 'ac-badge-artisan',
            'TERMINEE': 'ac-badge-success',
            'ANNULEE': 'ac-badge-danger',
        }
        cls = classes.get(obj.statut, 'ac-badge-muted')
        return format_html('<span class="ac-badge {}">{}</span>', cls, obj.get_statut_display())
