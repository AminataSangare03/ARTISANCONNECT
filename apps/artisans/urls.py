from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.avis.views import ArtisanAvisListView, ArtisanNoteView

from .views import ArtisanDetailView, ArtisanListView, ArtisanProfileView, RealisationViewSet

router = DefaultRouter()
router.register(r'realisations', RealisationViewSet, basename='realisations')

urlpatterns = [
    path('', ArtisanListView.as_view(), name='artisan-list'),
    path('<int:pk>/', ArtisanDetailView.as_view(), name='artisan-detail'),
    path('<int:pk>/avis/', ArtisanAvisListView.as_view(), name='artisan-avis'),
    path('<int:pk>/note/', ArtisanNoteView.as_view(), name='artisan-note'),
    path('me/', ArtisanProfileView.as_view(), name='artisan-me'),
    path('profile/', ArtisanProfileView.as_view(), name='artisan-profile'),
    *router.urls,
]
