from django.contrib import admin

from .models import Metier


@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'is_active', 'created_at')
    search_fields = ('nom', 'description')
    list_filter = ('is_active',)
    ordering = ('nom',)

