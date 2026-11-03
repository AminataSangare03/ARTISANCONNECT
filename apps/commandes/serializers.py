from rest_framework import serializers

from .models import Commande


class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = (
            'id', 'devis', 'client', 'artisan', 'date_debut', 'date_fin_prevue', 'date_fin_reelle',
            'statut', 'commentaires', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'client', 'artisan', 'created_at', 'updated_at')
