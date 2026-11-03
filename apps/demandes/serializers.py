from rest_framework import serializers

from apps.metiers.models import Metier

from .models import DemandeService


class DemandeServiceSerializer(serializers.ModelSerializer):
    metier = serializers.PrimaryKeyRelatedField(queryset=Metier.objects.filter(is_active=True))

    class Meta:
        model = DemandeService
        fields = (
            'id', 'client', 'metier', 'titre', 'description', 'ville', 'quartier', 'adresse',
            'budget_indicatif', 'date_souhaitee', 'statut', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'client', 'created_at', 'updated_at')
