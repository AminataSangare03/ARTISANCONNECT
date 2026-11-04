from django.urls import path

from .views import (
    artisan_dashboard_view,
    artisan_detail_view,
    artisan_list_view,
    client_dashboard_view,
    commande_action_view,
    demande_create_view,
    demande_detail_view,
    demande_list_view,
    devis_action_view,
    home_view,
    login_view,
    logout_view,
    realisation_delete_view,
    register_view,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('artisans/', artisan_list_view, name='artisan_list'),
    path('artisans/<int:pk>/', artisan_detail_view, name='artisan_detail'),
    path('demandes/', demande_list_view, name='demande_list'),
    path('demandes/publier/', demande_create_view, name='demande_create'),
    path('demandes/<int:pk>/', demande_detail_view, name='demande_detail'),
    path('devis/<int:pk>/<str:action>/', devis_action_view, name='devis_action'),
    path('commandes/<int:pk>/<str:action>/', commande_action_view, name='commande_action'),
    path('dashboard/client/', client_dashboard_view, name='client_dashboard'),
    path('dashboard/artisan/', artisan_dashboard_view, name='artisan_dashboard'),
    path('realisations/<int:pk>/supprimer/', realisation_delete_view, name='realisation_delete'),
    path('connexion/', login_view, name='web_login'),
    path('inscription/', register_view, name='web_register'),
    path('deconnexion/', logout_view, name='web_logout'),
    # Aliases
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register_web'),
    path('logout/', logout_view, name='logout_web'),
]
