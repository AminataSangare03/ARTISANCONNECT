from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Client

from .models import Avis
from .serializers import AvisSerializer


class AvisViewSet(viewsets.ModelViewSet):
    serializer_class = AvisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artisan', 'client']
    ordering_fields = ['created_at', 'note']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Avis.objects.select_related('client__user', 'artisan__user', 'commande').all()
        if user.role == 'CLIENT':
            return Avis.objects.select_related('client__user', 'artisan__user', 'commande').filter(client__user=user)
        if user.role == 'ARTISAN':
            return Avis.objects.select_related('client__user', 'artisan__user', 'commande').filter(artisan__user=user)
        return Avis.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'CLIENT':
            self.permission_denied(self.request, message='Seuls les clients peuvent publier un avis.')
        commande = serializer.validated_data['commande']
        if commande.client.user != user:
            self.permission_denied(self.request, message='Vous ne pouvez noter que vos propres commandes.')
        if commande.statut != 'CONFIRMEE':
            self.permission_denied(self.request, message='Un avis ne peut être publié que pour une commande confirmée.')
        if Avis.objects.filter(commande=commande).exists():
            self.permission_denied(self.request, message='Un seul avis peut être publié pour cette commande.')
        client_profile, _ = Client.objects.get_or_create(user=user)
        serializer.save(client=client_profile, artisan=commande.artisan)


class ArtisanAvisListView(generics.ListAPIView):
    serializer_class = AvisSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        artisan_id = self.kwargs.get('artisan_id') or self.kwargs.get('pk')
        return Avis.objects.filter(artisan_id=artisan_id).select_related('client__user', 'artisan__user', 'commande')


class ArtisanNoteView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        artisan_id = self.kwargs.get('artisan_id') or self.kwargs.get('pk')
        average = Avis.objects.filter(artisan_id=artisan_id).aggregate(avg_note=models.Avg('note'))['avg_note']
        count = Avis.objects.filter(artisan_id=artisan_id).count()
        return Response({
            'artisan_id': int(artisan_id),
            'note_moyenne': round(float(average or 0), 2),
            'nombre_avis': count,
        })
