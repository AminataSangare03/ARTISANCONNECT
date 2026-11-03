from django.contrib import admin

from .models import Avis


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('artisan', 'client', 'note', 'created_at')
    search_fields = ('artisan__user__email', 'client__user__email', 'commentaire')
    list_filter = ('note',)

