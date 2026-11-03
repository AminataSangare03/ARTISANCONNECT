from django.contrib import admin

from .models import Artisan, Realisation


@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('user', 'metier', 'ville', 'disponibilite', 'tarif_indicatif')
    search_fields = ('user__email', 'ville', 'quartier', 'metier__nom')
    list_filter = ('disponibilite', 'metier')


@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ('artisan', 'titre', 'date_realisation')
    search_fields = ('titre', 'artisan__user__email')

