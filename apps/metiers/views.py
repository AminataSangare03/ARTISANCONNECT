from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response

from .models import Metier
from .serializers import MetierSerializer


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class MetierViewSet(viewsets.ModelViewSet):
    serializer_class = MetierSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'ADMIN':
            return Metier.objects.all()
        return Metier.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response({'detail': 'Métier désactivé.'}, status=status.HTTP_200_OK)

