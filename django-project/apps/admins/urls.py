# coding=utf-8
# django libs
from django.urls import path, include

# 3rd party libs
from rest_framework.routers import DefaultRouter

# custom import
from . import views

# Namespace for URLs in this users app
app_name = 'admins'
router = DefaultRouter()
# router.register('', views.ViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.ProfileDetailView.as_view(), name="profile_home"),
    path('update_profile/', views.ProfileUpdateView.as_view(), name="update_profile"),
]

# when user go to path /app_name/ it will show api root page (endpoints list)
urlpatterns += router.urls
