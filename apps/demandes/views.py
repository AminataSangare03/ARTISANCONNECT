from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Client

from .models import DemandeService
from .serializers import DemandeServiceSerializer


class DemandeServiceViewSet(viewsets.ModelViewSet):
    serializer_class = DemandeServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['metier', 'ville', 'quartier', 'statut']
    search_fields = ['titre', 'description', 'ville', 'quartier']
    ordering_fields = ['created_at', 'budget_indicatif']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return DemandeService.objects.select_related('client__user', 'metier').all()
        if user.role == 'CLIENT':
            return DemandeService.objects.select_related('client__user', 'metier').filter(client__user=user)
        if user.role == 'ARTISAN':
            return DemandeService.objects.select_related('client__user', 'metier').filter(metier__artisans__user=user)
        return DemandeService.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            self.permission_denied(self.request, message='Seuls les clients peuvent publier une demande.')
        client_profile, _ = Client.objects.get_or_create(user=self.request.user)
        serializer.save(client=client_profile)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'CLIENT' and instance.client.user != request.user:
            return Response({'detail': 'Vous ne pouvez modifier que vos demandes.'}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role != 'CLIENT' and request.user.role != 'ADMIN':
            return Response({'detail': 'Un artisan ne peut pas modifier une demande client.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'CLIENT' and instance.client.user != request.user:
            return Response({'detail': 'Vous ne pouvez supprimer que vos demandes.'}, status=status.HTTP_403_FORBIDDEN)
        if instance.statut in {'ACCEPTEE', 'EN_COURS', 'TERMINEE'}:
            return Response({'detail': 'Cette demande ne peut plus être annulée.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.statut = 'ANNULEE'
        instance.save(update_fields=['statut', 'updated_at'])
        return Response({'detail': 'Demande annulée.'}, status=status.HTTP_200_OK)


class MesDemandesView(generics.ListAPIView):
    serializer_class = DemandeServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return DemandeService.objects.filter(client__user=user).select_related('client__user', 'metier')
        if user.role == 'ARTISAN':
            return DemandeService.objects.filter(metier__artisans__user=user).select_related('client__user', 'metier')
        return DemandeService.objects.none()
