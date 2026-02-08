from typing import Any, Dict, List, Set, Tuple

from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.urls import get_resolver


def get_resource_name(view_or_class: type | object) -> str:
    """Get the scope resource name for a viewset.

    Resolution order:
    1. scope_resource attribute (explicit)
    2. Class name with 'ViewSet' stripped, lowercased (fallback)
    """
    cls = view_or_class if isinstance(view_or_class, type) else type(view_or_class)

    scope_resource = getattr(cls, "scope_resource", None)
    if scope_resource:
        return scope_resource

    return cls.__name__.replace("ViewSet", "").lower()


def discover_scopes_from_urls() -> Dict[str, List[str]]:
    """
    Automatically discover all scopes from registered viewsets.

    Scans all registered URL patterns and extracts scopes from viewsets.

    Returns:
        Dictionary mapping resource names to lists of scope strings
        Example: {'posts': ['posts.read', 'posts.write', 'posts.delete']}
    """
    scopes: Dict[str, Set[str]] = {}
    resolver = get_resolver()

    def extract_scopes(url_patterns: Any, prefix: str = "") -> None:
        """Recursively extract scopes from URL patterns."""
        from rest_framework import viewsets

        for pattern in url_patterns:
            # Handle included URL patterns
            if hasattr(pattern, "url_patterns"):
                extract_scopes(pattern.url_patterns, prefix)

            # Handle viewsets
            callback = getattr(pattern, "callback", None)
            if callback and hasattr(callback, "cls"):
                view_class = callback.cls

                # Only process ViewSets
                if issubclass(view_class, viewsets.ViewSetMixin):
                    basename = get_resource_name(view_class)

                    # Get all actions for this viewset
                    actions = get_viewset_actions(view_class)

                    if basename not in scopes:
                        scopes[basename] = set()

                    scopes[basename].update(actions)

    extract_scopes(resolver.url_patterns)

    # Convert sets to sorted lists and format as scope strings
    formatted_scopes = {}
    for resource, actions in scopes.items():
        formatted_scopes[resource] = [f"{resource}.{action}" for action in sorted(actions)]

    return formatted_scopes


def get_viewset_actions(viewset_class: type) -> Set[str]:
    """
    Get all possible actions for a viewset.

    Includes standard CRUD actions and custom @action decorated methods.

    Args:
        viewset_class: ViewSet class to analyze

    Returns:
        Set of action names (read, write, delete, custom_action, etc.)
    """
    actions = set()

    # Standard actions based on mixins
    if hasattr(viewset_class, "list"):
        actions.add("read")
    if hasattr(viewset_class, "retrieve"):
        actions.add("read")
    if hasattr(viewset_class, "create"):
        actions.add("write")
    if hasattr(viewset_class, "update") or hasattr(viewset_class, "partial_update"):
        actions.add("write")
    if hasattr(viewset_class, "destroy"):
        actions.add("delete")

    # Custom actions (decorated with @action)
    for attr_name in dir(viewset_class):
        attr = getattr(viewset_class, attr_name)

        # Check if it's a custom action
        if hasattr(attr, "mapping"):
            # This is a custom action
            methods = attr.mapping.values() if isinstance(attr.mapping, dict) else []

            # Map HTTP methods to actions
            for method in methods:
                if method in ["list", "retrieve"]:
                    actions.add("read")
                elif method in ["create", "update", "partial_update"]:
                    actions.add("write")
                elif method == "destroy":
                    actions.add("delete")
                else:
                    # Custom action name
                    actions.add(attr_name)

    return actions


def get_all_available_scopes() -> List[tuple]:
    """
    Get all available scopes as a flat list of tuples for choices.

    Returns:
        List of (scope, display_name) tuples
        Example: [('posts.read', 'Posts - Read'), ...]
    """
    scopes_by_resource = discover_scopes_from_urls()
    choices = []

    for _resource, scope_list in sorted(scopes_by_resource.items()):
        for scope in scope_list:
            resource_name, action = scope.split(".", 1)

            # Humanize the names
            resource_display = resource_name.replace("_", " ").title()
            action_display = action.replace("_", " ").title()

            choices.append((scope, f"{resource_display} - {action_display}"))

    return choices


def discover_scopes_with_apps() -> Dict[str, Tuple[str, List[str]]]:
    """
    Discover scopes from URLs with Django app label information.

    Returns:
        Dictionary mapping resource names to (app_label, scope_list) tuples
        Example: {'posts': ('blog', ['posts.read', 'posts.write'])}
    """
    scopes: Dict[str, Set[str]] = {}
    app_labels: Dict[str, str] = {}
    resolver = get_resolver()

    def extract_scopes(url_patterns: Any, prefix: str = "") -> None:
        from rest_framework import viewsets

        for pattern in url_patterns:
            if hasattr(pattern, "url_patterns"):
                extract_scopes(pattern.url_patterns, prefix)

            callback = getattr(pattern, "callback", None)
            if callback and hasattr(callback, "cls"):
                view_class = callback.cls

                if issubclass(view_class, viewsets.ViewSetMixin):
                    basename = get_resource_name(view_class)

                    actions = get_viewset_actions(view_class)

                    if basename not in scopes:
                        scopes[basename] = set()

                    scopes[basename].update(actions)

                    # Track app label
                    if basename not in app_labels:
                        app_config = apps.get_containing_app_config(view_class.__module__)
                        app_labels[basename] = (
                            str(app_config.verbose_name) if app_config else "Other"
                        )

    extract_scopes(resolver.url_patterns)

    result = {}
    for resource, actions in scopes.items():
        scope_list = [f"{resource}.{action}" for action in sorted(actions)]
        app_label = app_labels.get(resource, "Other")
        result[resource] = (app_label, scope_list)

    return result


def get_scopes_grouped_by_resource() -> Dict[str, List[tuple]]:
    """
    Get scopes organized by resource for grouped display.

    Returns:
        Dictionary mapping resource display names to lists of (scope, action_display) tuples
        Example: {'Posts': [('posts.read', 'Read'), ('posts.write', 'Write')], ...}
    """
    scopes_by_resource = discover_scopes_from_urls()
    grouped: Dict[str, List[tuple[str, str]]] = {}

    for resource, scope_list in sorted(scopes_by_resource.items()):
        resource_display = resource.replace("_", " ").title()
        grouped[resource_display] = []

        for scope in scope_list:
            _, action = scope.split(".", 1)
            action_display = action.replace("_", " ").title()
            grouped[resource_display].append((scope, action_display))

    return grouped


def get_scopes_grouped_by_app() -> Dict[str, Dict[str, List[tuple]]]:
    """
    Get scopes organized by app and then by resource.

    Returns:
        Dictionary mapping app labels to dictionaries of resource display names
        to lists of (scope, action_display) tuples.
        Example: {'Blog': {'Posts': [('posts.read', 'Read'), ...]}}
    """
    scopes_with_apps = discover_scopes_with_apps()
    grouped: Dict[str, Dict[str, List[tuple[str, str]]]] = {}

    for resource, (app_label, scope_list) in sorted(scopes_with_apps.items()):
        if app_label not in grouped:
            grouped[app_label] = {}

        resource_display = resource.replace("_", " ").title()
        grouped[app_label][resource_display] = []

        for scope in scope_list:
            _, action = scope.split(".", 1)
            action_display = action.replace("_", " ").title()
            grouped[app_label][resource_display].append((scope, action_display))

    return grouped


def get_user_scopes(user: AbstractUser) -> Set[str]:
    """
    Get all scopes for a user from their groups.

    Args:
        user: Django user instance

    Returns:
        Set of scope strings
    """
    from .models import ScopedGroup

    scopes = set()

    for group in user.groups.all():
        try:
            scoped_group = ScopedGroup.objects.get(group=group)
            scopes.update(scoped_group.scopes)
        except ScopedGroup.DoesNotExist:
            continue

    return scopes
