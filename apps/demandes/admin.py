from django.contrib import admin

from .models import DemandeService


@admin.register(DemandeService)
class DemandeServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'client', 'metier', 'statut', 'created_at')
    search_fields = ('titre', 'description', 'client__user__email')
    list_filter = ('statut', 'metier')

