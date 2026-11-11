# django core libs
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

# 3rd party libs
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


# URL of project for Multilingual
urlpatterns = [
    path('admin12321/', admin.site.urls),  # admin path
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redocs/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redocs'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('select2/', include('django_select2.urls')),
    path('', include('apps.users.urls', namespace='users')),
    path('common/', include('apps.common.urls', namespace='common')),
]

# Static and Media files handling
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
