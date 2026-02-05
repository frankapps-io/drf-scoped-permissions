from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.request import Request

from .models import ScopedAPIKey, ScopedGroup

if TYPE_CHECKING:
    from rest_framework.views import APIView


class HasAPIKeyOrGroupScope(permissions.BasePermission):
    """
    Permission class that checks scopes for both API keys and user groups.

    - API Keys: Checks scopes stored on the ScopedAPIKey model
    - Users: Checks scopes from all ScopedGroups the user belongs to
    - Superusers: Always granted access

    Scopes are determined automatically from:
    1. view.required_scope (explicit scope)
    2. view.scope_resource + HTTP method → action mapping
    3. view.basename + HTTP method → action mapping

    Example:
        class PostViewSet(ModelViewSet):
            permission_classes = [HasAPIKeyOrGroupScope]
            scope_resource = 'posts'
            # Auto-generates: posts.read, posts.write, posts.delete
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the request has permission to access the view.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if permission is granted, False otherwise
        """
        # Check API key authentication first
        if self._is_api_key_request(request):
            return self._check_api_key_permission(request, view)

        # Check user-based authentication (JWT, session, etc.)
        if request.user and request.user.is_authenticated:
            return self._check_user_permission(request, view)

        return False

    def _is_api_key_request(self, request: Request) -> bool:
        """Check if the request is authenticated via API key."""
        return hasattr(request, "auth") and isinstance(request.auth, ScopedAPIKey)

    def _check_api_key_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the API key has the required scope.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if the API key has the required scope
        """
        api_key: ScopedAPIKey = request.auth

        # Backward compatible: empty scopes = unrestricted access
        if not api_key.scopes:
            return True

        required_scope = self.get_required_scope(request, view)

        # No scope required
        if not required_scope:
            return True

        return api_key.has_scope(required_scope)

    def _check_user_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if the user has the required scope through their groups.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            True if the user has the required scope
        """
        # Superusers bypass all checks
        if request.user.is_superuser:
            return True

        required_scope = self.get_required_scope(request, view)

        # No scope required
        if not required_scope:
            return True

        # Get all scopes from user's groups
        user_scopes = self._get_user_scopes(request.user)

        # Empty scopes = no access (different from API keys for security)
        if not user_scopes:
            return False

        return required_scope in user_scopes

    def _get_user_scopes(self, user) -> set:
        """
        Get all scopes from the user's groups.

        Args:
            user: Django user instance

        Returns:
            Set of scope strings
        """
        scopes = set()
        # Single query with JOIN instead of N+1 queries
        scoped_groups = ScopedGroup.objects.filter(group__in=user.groups.all())
        for scoped_group in scoped_groups:
            scopes.update(scoped_group.scopes)
        return scopes

    def get_required_scope(self, request: Request, view: APIView) -> str | None:
        """
        Determine the required scope for this request.

        Priority:
        1. Explicit view.required_scope
        2. Auto-generated from view.scope_resource or view.basename

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            Required scope string or None
        """
        # Explicit scope takes precedence
        if hasattr(view, "required_scope"):
            return view.required_scope

        # Get resource name
        resource = getattr(view, "scope_resource", None)
        if not resource and hasattr(view, "basename"):
            resource = view.basename

        if not resource:
            return None

        # Determine action from view.action or HTTP method
        action = self._get_action(request, view)

        return f"{resource}.{action}"

    def _get_action(self, request: Request, view: APIView) -> str:
        """
        Determine the action from the view or HTTP method.

        Args:
            request: The incoming request
            view: The view being accessed

        Returns:
            Action string (read, write, delete, or custom action name)
        """
        # For viewsets with actions
        if hasattr(view, "action") and view.action:
            action_name = view.action

            # Map standard CRUD actions to read/write/delete
            if action_name in ["list", "retrieve"]:
                return "read"
            elif action_name in ["create", "update", "partial_update"]:
                return "write"
            elif action_name == "destroy":
                return "delete"
            else:
                # Custom action - use the action name directly
                return action_name

        # Fall back to HTTP method mapping
        action_map = {
            "GET": "read",
            "HEAD": "read",
            "OPTIONS": "read",
            "POST": "write",
            "PUT": "write",
            "PATCH": "write",
            "DELETE": "delete",
        }

        return action_map.get(request.method, "read")
