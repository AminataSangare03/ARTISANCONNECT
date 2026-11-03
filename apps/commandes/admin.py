from django.contrib import admin

from .models import Commande


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'artisan', 'statut', 'created_at')
    search_fields = ('client__user__email', 'artisan__user__email')
    list_filter = ('statut',)

