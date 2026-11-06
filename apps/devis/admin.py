from django.contrib import admin
from django.utils.html import format_html

from .models import Devis


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ('id', 'demande_titre', 'artisan_nom', 'montant_fcfa', 'duree_estimee', 'statut_badge', 'created_at')
    search_fields = ('demande__titre', 'artisan__user__email', 'artisan__user__first_name', 'artisan__user__last_name', 'description')
    list_filter = ('statut',)
    ordering = ('-created_at',)

    @admin.display(description='Demande associée', ordering='demande__titre')
    def demande_titre(self, obj):
        return obj.demande.titre

    @admin.display(description='Artisan', ordering='artisan__user__last_name')
    def artisan_nom(self, obj):
        return obj.artisan.user.get_full_name() or obj.artisan.user.email

    @admin.display(description='Montant proposé', ordering='montant')
    def montant_fcfa(self, obj):
        return f'{int(obj.montant):,} FCFA'.replace(',', ' ')

    @admin.display(description='Statut', ordering='statut')
    def statut_badge(self, obj):
        classes = {
            'EN_ATTENTE': 'ac-badge-warning',
            'ACCEPTE': 'ac-badge-success',
            'REFUSE': 'ac-badge-danger',
            'EXPIRE': 'ac-badge-muted',
            'ANNULE': 'ac-badge-danger',
        }
        cls = classes.get(obj.statut, 'ac-badge-muted')
        return format_html('<span class="ac-badge {}">{}</span>', cls, obj.get_statut_display())
