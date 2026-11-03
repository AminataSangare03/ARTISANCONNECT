from rest_framework import serializers

from .models import Metier


class MetierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metier
        fields = ('id', 'nom', 'description', 'image', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')
