from rest_framework import serializers

from .models import Avis


class AvisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avis
        fields = ('id', 'client', 'artisan', 'commande', 'note', 'commentaire', 'created_at', 'updated_at')
        read_only_fields = ('id', 'client', 'artisan', 'created_at', 'updated_at')
