from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.commandes.models import Commande

from .models import Devis
from .serializers import DevisSerializer


class DevisViewSet(viewsets.ModelViewSet):
    serializer_class = DevisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['demande', 'statut', 'artisan']
    search_fields = ['description', 'duree_estimee']
    ordering_fields = ['created_at', 'montant']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Devis.objects.select_related('demande__client__user', 'artisan__user').all()
        if user.role == 'CLIENT':
            return Devis.objects.select_related('demande__client__user', 'artisan__user').filter(demande__client__user=user)
        if user.role == 'ARTISAN':
            return Devis.objects.select_related('demande__client__user', 'artisan__user').filter(artisan__user=user)
        return Devis.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'ARTISAN':
            self.permission_denied(self.request, message='Seuls les artisans peuvent créer des devis.')
        artisan = self.request.user.artisan_profile
        demande = serializer.validated_data['demande']
        if demande.metier != artisan.metier:
            self.permission_denied(self.request, message='Le devis doit correspondre au métier de l\'artisan.')
        existing = Devis.objects.filter(demande=demande, artisan=artisan, statut='EN_ATTENTE').exists()
        if existing:
            self.permission_denied(self.request, message='Un devis actif existe déjà pour cette demande.')
        serializer.save(artisan=artisan)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'ARTISAN' and instance.artisan.user != request.user:
            return Response({'detail': 'Vous ne pouvez modifier que vos propres devis.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'CLIENT' and instance.demande.client.user != request.user:
            return Response({'detail': 'Vous ne pouvez modifier que les devis reçus pour vos demandes.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def accepter(self, request, *args, **kwargs):
        devis = self.get_object()
        if request.user.role != 'CLIENT' or devis.demande.client.user != request.user:
            return Response({'detail': 'Seul le propriétaire de la demande peut accepter un devis.'}, status=status.HTTP_403_FORBIDDEN)
        if devis.statut == 'EXPIRE':
            return Response({'detail': 'Ce devis a expiré.'}, status=status.HTTP_400_BAD_REQUEST)
        if devis.demande.statut in {'ACCEPTEE', 'EN_COURS', 'TERMINEE'}:
            return Response({'detail': 'Cette demande est déjà réservée.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            devis.statut = 'ACCEPTE'
            devis.save(update_fields=['statut', 'updated_at'])
            devis.demande.statut = 'ACCEPTEE'
            devis.demande.save(update_fields=['statut', 'updated_at'])
            Devis.objects.filter(demande=devis.demande).exclude(id=devis.id).update(statut='REFUSE')
            Commande.objects.get_or_create(
                devis=devis,
                defaults={
                    'client': devis.demande.client,
                    'artisan': devis.artisan,
                    'date_debut': None,
                    'statut': 'EN_ATTENTE',
                },
            )
        return Response({'detail': 'Devis accepté. Une commande a été créée.'})

    @action(detail=True, methods=['post'])
    def refuser(self, request, *args, **kwargs):
        devis = self.get_object()
        if request.user.role != 'CLIENT' or devis.demande.client.user != request.user:
            return Response({'detail': 'Seul le propriétaire de la demande peut refuser un devis.'}, status=status.HTTP_403_FORBIDDEN)
        devis.statut = 'REFUSE'
        devis.save(update_fields=['statut', 'updated_at'])
        return Response({'detail': 'Devis refusé.'})


class MesDevisView(generics.ListAPIView):
    serializer_class = DevisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return Devis.objects.filter(demande__client__user=user).select_related('demande__client__user', 'artisan__user')
        if user.role == 'ARTISAN':
            return Devis.objects.filter(artisan__user=user).select_related('demande__client__user', 'artisan__user')
        return Devis.objects.none()
