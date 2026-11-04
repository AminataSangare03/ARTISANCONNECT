from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ArtisanAvisListView, ArtisanNoteView, AvisViewSet

router = DefaultRouter()
router.register(r'', AvisViewSet, basename='avis')

urlpatterns = [
    path('artisans/<int:artisan_id>/avis/', ArtisanAvisListView.as_view(), name='artisan-avis-nested'),
    path('artisans/<int:artisan_id>/note/', ArtisanNoteView.as_view(), name='artisan-note-nested'),
    *router.urls,
]
