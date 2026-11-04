from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DemandeServiceViewSet, MesDemandesView

router = DefaultRouter()
router.register(r'', DemandeServiceViewSet, basename='demandes')

urlpatterns = [
    path('mes-demandes/', MesDemandesView.as_view(), name='mes-demandes'),
    *router.urls,
]
