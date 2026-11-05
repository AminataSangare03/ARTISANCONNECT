from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Client
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)

UserModel = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'Compte créé avec succès.', 'user': UserSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Le refresh token est requis.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (InvalidToken, Exception):
            return Response({'detail': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def patch(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            if not user.check_password(old_password):
                return Response({'detail': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Mot de passe changé avec succès.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = UserModel.objects.filter(email=email).first()
            if user is not None:
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        'Réinitialisation du mot de passe',
                        'Vous pouvez réinitialiser votre mot de passe via le formulaire dédié.',
                        'noreply@artisanconnect.local',
                        [email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            return Response({'detail': 'Si cet email est enregistré, un message de réinitialisation a été envoyé.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'detail': 'Compte désactivé avec succès.'})


class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = getattr(request.user, 'client_profile', None)
        if not profile:
            return Response({'detail': 'Profil client introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'id': profile.id,
            'ville': profile.ville,
            'quartier': profile.quartier,
            'adresse': profile.adresse,
            'updated_at': profile.updated_at,
        })

    def patch(self, request, *args, **kwargs):
        if request.user.role != 'CLIENT':
            return Response({'detail': 'Seuls les clients peuvent modifier leur profil client.'}, status=status.HTTP_403_FORBIDDEN)
        profile, created = Client.objects.get_or_create(user=request.user)
        for field in ('ville', 'quartier', 'adresse'):
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()
        return Response({
            'id': profile.id,
            'ville': profile.ville,
            'quartier': profile.quartier,
            'adresse': profile.adresse,
        })


__all__ = [
    'CustomTokenObtainPairView',
    'TokenRefreshView',
    'RegisterView',
    'LogoutView',
    'MeView',
    'PasswordChangeView',
    'PasswordResetRequestView',
    'DeactivateAccountView',
    'ClientProfileView',
]
