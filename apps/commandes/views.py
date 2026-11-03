from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Commande
from .serializers import CommandeSerializer


class CommandeViewSet(viewsets.ModelViewSet):
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'client', 'artisan']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Commande.objects.select_related('client__user', 'artisan__user', 'devis').all()
        if user.role == 'CLIENT':
            return Commande.objects.select_related('client__user', 'artisan__user', 'devis').filter(client__user=user)
        if user.role == 'ARTISAN':
            return Commande.objects.select_related('client__user', 'artisan__user', 'devis').filter(artisan__user=user)
        return Commande.objects.none()

    @action(detail=True, methods=['post'])
    def demarrer(self, request, *args, **kwargs):
        commande = self.get_object()
        if request.user.role != 'ARTISAN' or commande.artisan.user != request.user:
            return Response({'detail': 'Seul l\'artisan concerné peut démarrer la commande.'}, status=status.HTTP_403_FORBIDDEN)
        if commande.statut not in {'EN_ATTENTE', 'CONFIRMEE'}:
            return Response({'detail': 'Transition de statut non autorisée.'}, status=status.HTTP_400_BAD_REQUEST)
        commande.statut = 'EN_COURS'
        commande.date_debut = __import__('django.utils.timezone').utils.timezone.now()
        commande.save(update_fields=['statut', 'date_debut', 'updated_at'])
        return Response({'detail': 'Commande démarrée.'})

    @action(detail=True, methods=['post'])
    def terminer(self, request, *args, **kwargs):
        commande = self.get_object()
        if request.user.role != 'ARTISAN' or commande.artisan.user != request.user:
            return Response({'detail': 'Seul l\'artisan concerné peut terminer la commande.'}, status=status.HTTP_403_FORBIDDEN)
        if commande.statut != 'EN_COURS':
            return Response({'detail': 'La commande doit être en cours pour être terminée.'}, status=status.HTTP_400_BAD_REQUEST)
        commande.statut = 'TERMINEE'
        commande.date_fin_reelle = __import__('django.utils.timezone').utils.timezone.now()
        commande.save(update_fields=['statut', 'date_fin_reelle', 'updated_at'])
        return Response({'detail': 'Prestation terminée.'})

    @action(detail=True, methods=['post'])
    def confirmer(self, request, *args, **kwargs):
        commande = self.get_object()
        if request.user.role != 'CLIENT' or commande.client.user != request.user:
            return Response({'detail': 'Seul le client concerné peut confirmer la prestation.'}, status=status.HTTP_403_FORBIDDEN)
        if commande.statut != 'TERMINEE':
            return Response({'detail': 'La prestation doit être terminée avant confirmation.'}, status=status.HTTP_400_BAD_REQUEST)
        commande.statut = 'CONFIRMEE'
        commande.save(update_fields=['statut', 'updated_at'])
        return Response({'detail': 'Prestation confirmée par le client.'})

    @action(detail=True, methods=['post'])
    def annuler(self, request, *args, **kwargs):
        commande = self.get_object()
        if request.user.role not in {'CLIENT', 'ARTISAN'}:
            return Response({'detail': 'Action non autorisée.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'CLIENT' and commande.client.user != request.user:
            return Response({'detail': 'Vous ne pouvez annuler que vos commandes.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == 'ARTISAN' and commande.artisan.user != request.user:
            return Response({'detail': 'Vous ne pouvez annuler que vos commandes.'}, status=status.HTTP_403_FORBIDDEN)
        if commande.statut in {'TERMINEE', 'CONFIRMEE'}:
            return Response({'detail': 'Une commande terminée ne peut pas être annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        commande.statut = 'ANNULEE'
        commande.save(update_fields=['statut', 'updated_at'])
        return Response({'detail': 'Commande annulée.'})

