from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import Client, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile_picture',
            'role',
            'is_active',
            'date_joined',
            'updated_at',
        )
        read_only_fields = ('id', 'date_joined', 'updated_at')


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ('id', 'user', 'ville', 'quartier', 'adresse', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    ville = serializers.CharField(required=False, allow_blank=True)
    quartier = serializers.CharField(required=False, allow_blank=True)
    adresse = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'role',
            'ville',
            'quartier',
            'adresse',
        )

    def validate_role(self, value):
        if value == 'ADMIN':
            raise serializers.ValidationError('La création d\'un compte administrateur est réservée aux comptes autorisés.')
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'CLIENT')
        ville = validated_data.pop('ville', '')
        quartier = validated_data.pop('quartier', '')
        adresse = validated_data.pop('adresse', '')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, role=role, **validated_data)
        if role == 'CLIENT':
            Client.objects.create(user=user, ville=ville, quartier=quartier, adresse=adresse)
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_picture')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
