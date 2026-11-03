from rest_framework import serializers

from apps.metiers.models import Metier

from .models import Artisan, Realisation


class ArtisanSerializer(serializers.ModelSerializer):
    metier = serializers.PrimaryKeyRelatedField(queryset=Metier.objects.all(), required=False, allow_null=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = (
            'id', 'user', 'metier', 'description', 'experience', 'ville', 'quartier', 'adresse',
            'disponibilite', 'tarif_indicatif', 'photo_profil', 'telephone_professionnel', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        from apps.accounts.serializers import UserSerializer
        return UserSerializer(obj.user).data


class ArtisanPublicSerializer(serializers.ModelSerializer):
    metier = serializers.StringRelatedField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = (
            'id', 'full_name', 'metier', 'description', 'experience', 'ville', 'quartier', 'adresse',
            'disponibilite', 'tarif_indicatif', 'photo_profil', 'telephone_professionnel'
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class RealisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realisation
        fields = ('id', 'artisan', 'titre', 'description', 'image', 'date_realisation', 'created_at')
        read_only_fields = ('id', 'artisan', 'created_at')
