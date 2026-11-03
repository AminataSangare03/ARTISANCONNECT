from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DevisViewSet, MesDevisView

router = DefaultRouter()
router.register(r'', DevisViewSet, basename='devis')

urlpatterns = [
    *router.urls,
    path('mes-devis/', MesDevisView.as_view(), name='mes-devis'),
]
