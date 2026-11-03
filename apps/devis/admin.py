from django.contrib import admin

from .models import Devis


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ('id', 'demande', 'artisan', 'montant', 'statut', 'created_at')
    search_fields = ('demande__titre', 'artisan__user__email')
    list_filter = ('statut',)

