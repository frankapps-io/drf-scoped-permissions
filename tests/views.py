"""
Test views for testing.
"""

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PostSerializer(serializers.Serializer):
    """Simple serializer for testing."""

    id = serializers.IntegerField()
    title = serializers.CharField()


class PostViewSet(viewsets.ViewSet):
    """Test viewset for posts."""

    scope_resource = "posts"

    def list(self, request):
        return Response([{"id": 1, "title": "Test Post"}])

    def retrieve(self, request, pk=None):
        return Response({"id": pk, "title": "Test Post"})

    def create(self, request):
        return Response({"id": 1, "title": request.data.get("title")})

    def update(self, request, pk=None):
        return Response({"id": pk, "title": request.data.get("title")})

    def partial_update(self, request, pk=None):
        return Response({"id": pk, "title": request.data.get("title")})

    def destroy(self, request, pk=None):
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        return Response({"status": "published"})


class UserProfileViewSet(viewsets.ViewSet):
    """Test viewset with explicit scope_resource different from class name."""

    scope_resource = "profiles"

    def list(self, request):
        return Response([{"id": 1, "username": "testuser"}])

    def retrieve(self, request, pk=None):
        return Response({"id": pk, "username": "testuser"})
