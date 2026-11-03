from rest_framework.routers import DefaultRouter

from .views import MetierViewSet

router = DefaultRouter()
router.register(r'', MetierViewSet, basename='metiers')
urlpatterns = router.urls
