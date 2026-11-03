from django.urls import path

from .views import (
    ClientProfileView,
    CustomTokenObtainPairView,
    DeactivateAccountView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetRequestView,
    RegisterView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('me/', MeView.as_view(), name='me'),
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate'),
    path('client/profile/', ClientProfileView.as_view(), name='client_profile'),
]
