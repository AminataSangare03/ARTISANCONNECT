from django.contrib import admin
from django.utils.html import format_html

from .models import Avis


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'artisan_nom', 'client_nom', 'stars_display', 'commentaire_extrait', 'created_at')
    search_fields = ('artisan__user__email', 'artisan__user__first_name', 'artisan__user__last_name', 'client__user__email', 'client__user__first_name', 'client__user__last_name', 'commentaire')
    list_filter = ('note', 'created_at')
    ordering = ('-created_at',)

    @admin.display(description='Artisan', ordering='artisan__user__last_name')
    def artisan_nom(self, obj):
        return obj.artisan.user.get_full_name() or obj.artisan.user.email

    @admin.display(description='Client', ordering='client__user__last_name')
    def client_nom(self, obj):
        return obj.client.user.get_full_name() or obj.client.user.email

    @admin.display(description='Note', ordering='note')
    def stars_display(self, obj):
        stars = '★' * obj.note + '☆' * (5 - obj.note)
        return format_html('<span style="color: #F59E0B; font-weight: 700; letter-spacing: 1px;">{}</span> <span style="font-size: 0.8rem; color: var(--ac-text-muted);">({}/5)</span>', stars, obj.note)

    @admin.display(description='Commentaire')
    def commentaire_extrait(self, obj):
        if len(obj.commentaire) > 60:
            return obj.commentaire[:60] + '...'
        return obj.commentaire or '-'
