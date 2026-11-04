from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('artisans/', views.artisan_list_view, name='artisan_list'),
    path('artisans/<int:pk>/', views.artisan_detail_view, name='artisan_detail'),
    path('demandes/', views.demande_list_view, name='demande_list'),
    path('demandes/publier/', views.demande_create_view, name='demande_create'),
    path('demandes/<int:pk>/', views.demande_detail_view, name='demande_detail'),
    path('devis/<int:pk>/<str:action>/', views.devis_action_view, name='devis_action'),
    path('commandes/<int:pk>/<str:action>/', views.commande_action_view, name='commande_action'),
    path('dashboard/client/', views.client_dashboard_view, name='client_dashboard'),
    path('dashboard/artisan/', views.artisan_dashboard_view, name='artisan_dashboard'),
    path('realisations/<int:pk>/supprimer/', views.realisation_delete_view, name='realisation_delete'),
    path('connexion/', views.login_view, name='web_login'),
    path('inscription/', views.register_view, name='web_register'),
    path('deconnexion/', views.logout_view, name='web_logout'),
]
