from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Administration
admin.site.site_header = "ArtisanConnect • Supervision Mali"
admin.site.site_title = "ArtisanConnect Admin"
admin.site.index_title = "Tableau de bord de supervision"

urlpatterns = [
    # Administration
    path('admin/', admin.site.urls),

    # Web Platform (full Python / Django interface)
    path('', include('apps.web.urls')),

    # REST APIs (v1)
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/metiers/', include('apps.metiers.urls')),
    path('api/v1/artisans/', include('apps.artisans.urls')),
    path('api/v1/demandes/', include('apps.demandes.urls')),
    path('api/v1/devis/', include('apps.devis.urls')),
    path('api/v1/commandes/', include('apps.commandes.urls')),
    path('api/v1/avis/', include('apps.avis.urls')),

    # Documentation Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
