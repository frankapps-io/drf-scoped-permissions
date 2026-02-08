"""
Test URLs configuration.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"profiles", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
