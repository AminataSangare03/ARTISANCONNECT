from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ArtisanAvisListView, ArtisanNoteView, AvisViewSet

router = DefaultRouter()
router.register(r'', AvisViewSet, basename='avis')

urlpatterns = [
    *router.urls,
    path('artisans/<int:artisan_id>/avis/', ArtisanAvisListView.as_view(), name='artisan-avis'),
    path('artisans/<int:artisan_id>/note/', ArtisanNoteView.as_view(), name='artisan-note'),
]
