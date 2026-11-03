from rest_framework import serializers

from .models import Devis


class DevisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devis
        fields = (
            'id', 'demande', 'artisan', 'montant', 'description', 'duree_estimee', 'validite',
            'statut', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'artisan', 'created_at', 'updated_at')
