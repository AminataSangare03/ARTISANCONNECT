from django.db.models import Avg
from rest_framework import serializers

from apps.metiers.models import Metier

from .models import Artisan, Realisation


class RealisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realisation
        fields = ('id', 'artisan', 'titre', 'description', 'image', 'date_realisation', 'created_at')
        read_only_fields = ('id', 'artisan', 'created_at')


class ArtisanSerializer(serializers.ModelSerializer):
    metier = serializers.PrimaryKeyRelatedField(queryset=Metier.objects.all(), required=False, allow_null=True)
    metier_nom = serializers.CharField(source='metier.nom', read_only=True)
    user = serializers.SerializerMethodField()
    realisations = RealisationSerializer(many=True, read_only=True)
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = (
            'id', 'user', 'metier', 'metier_nom', 'description', 'experience', 'ville', 'quartier', 'adresse',
            'disponibilite', 'tarif_indicatif', 'photo_profil', 'telephone_professionnel',
            'realisations', 'note_moyenne', 'nombre_avis', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        from apps.accounts.serializers import UserSerializer
        return UserSerializer(obj.user).data

    def get_note_moyenne(self, obj):
        avg = obj.avis_recus.aggregate(avg=Avg('note'))['avg']
        return round(float(avg or 0), 2)

    def get_nombre_avis(self, obj):
        return obj.avis_recus.count()


class ArtisanPublicSerializer(serializers.ModelSerializer):
    metier = serializers.StringRelatedField()
    metier_id = serializers.ReadOnlyField(source='metier.id')
    full_name = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='user.email')
    realisations = RealisationSerializer(many=True, read_only=True)
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()

    class Meta:
        model = Artisan
        fields = (
            'id', 'full_name', 'email', 'metier', 'metier_id', 'description', 'experience',
            'ville', 'quartier', 'adresse', 'disponibilite', 'tarif_indicatif',
            'photo_profil', 'telephone_professionnel', 'realisations', 'note_moyenne', 'nombre_avis'
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def get_note_moyenne(self, obj):
        avg = obj.avis_recus.aggregate(avg=Avg('note'))['avg']
        return round(float(avg or 0), 2)

    def get_nombre_avis(self, obj):
        return obj.avis_recus.count()
