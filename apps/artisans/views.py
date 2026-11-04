from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.metiers.models import Metier

from .models import Artisan, Realisation
from .serializers import ArtisanPublicSerializer, ArtisanSerializer, RealisationSerializer


class IsArtisanOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ('ARTISAN', 'ADMIN')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'ADMIN':
            return True
        return obj.artisan.user == request.user


class ArtisanProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArtisanSerializer

    def get(self, request, *args, **kwargs):
        try:
            artisan = request.user.artisan_profile
        except Artisan.DoesNotExist:
            return Response({'detail': 'Aucun profil artisan trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ArtisanSerializer(artisan).data)

    def post(self, request, *args, **kwargs):
        if request.user.role != 'ARTISAN':
            return Response({'detail': 'Le rôle ARTISAN est requis pour créer un profil artisan.'}, status=status.HTTP_403_FORBIDDEN)
        if hasattr(request.user, 'artisan_profile'):
            return Response({'detail': 'Un profil artisan existe déjà pour cet utilisateur.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        metier_id = data.get('metier')
        if metier_id is None:
            return Response({'detail': 'Le métier est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            metier = Metier.objects.get(id=metier_id, is_active=True)
        except Metier.DoesNotExist:
            return Response({'detail': 'Métier introuvable ou inactif.'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            artisan = Artisan.objects.create(user=request.user, metier=metier, **{
                'description': data.get('description', ''),
                'experience': data.get('experience', 0),
                'ville': data.get('ville', ''),
                'quartier': data.get('quartier', ''),
                'adresse': data.get('adresse', ''),
                'disponibilite': data.get('disponibilite', True),
                'tarif_indicatif': data.get('tarif_indicatif', 0),
                'telephone_professionnel': data.get('telephone_professionnel', ''),
            })
            if 'photo_profil' in request.FILES:
                artisan.photo_profil = request.FILES['photo_profil']
                artisan.save(update_fields=['photo_profil'])
        return Response(ArtisanSerializer(artisan).data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        try:
            artisan = request.user.artisan_profile
        except Artisan.DoesNotExist:
            return Response({'detail': 'Aucun profil artisan trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArtisanSerializer(artisan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ArtisanSerializer(artisan).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtisanListView(generics.ListAPIView):
    queryset = Artisan.objects.filter(user__is_active=True).select_related('user', 'metier').prefetch_related('realisations', 'avis_recus')
    serializer_class = ArtisanPublicSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['metier', 'ville', 'quartier', 'disponibilite']
    search_fields = ['user__first_name', 'user__last_name', 'metier__nom', 'ville', 'quartier']
    ordering_fields = ['tarif_indicatif', 'experience', 'ville']


class ArtisanDetailView(generics.RetrieveAPIView):
    queryset = Artisan.objects.filter(user__is_active=True).select_related('user', 'metier').prefetch_related('realisations', 'avis_recus')
    serializer_class = ArtisanPublicSerializer
    permission_classes = [AllowAny]


class RealisationViewSet(viewsets.ModelViewSet):
    serializer_class = RealisationSerializer
    permission_classes = [IsArtisanOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artisan']
    search_fields = ['titre', 'description']
    ordering_fields = ['date_realisation', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if self.request.method in permissions.SAFE_METHODS:
            return Realisation.objects.select_related('artisan__user').all()
        if user.is_authenticated and user.role == 'ADMIN':
            return Realisation.objects.select_related('artisan__user').all()
        if user.is_authenticated and user.role == 'ARTISAN':
            return Realisation.objects.select_related('artisan__user').filter(artisan__user=user)
        return Realisation.objects.none()

    def perform_create(self, serializer):
        if not self.request.user or not self.request.user.is_authenticated or self.request.user.role != 'ARTISAN':
            self.permission_denied(self.request, message='Seuls les artisans peuvent ajouter leurs réalisations.')
        if not hasattr(self.request.user, 'artisan_profile'):
            self.permission_denied(self.request, message='Veuillez d\'abord compléter votre profil artisan.')
        artisan = self.request.user.artisan_profile
        serializer.save(artisan=artisan)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role != 'ADMIN' and instance.artisan.user != request.user:
            return Response({'detail': 'Vous ne pouvez supprimer que vos réalisations.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({'detail': 'Réalisation supprimée.'}, status=status.HTTP_204_NO_CONTENT)
