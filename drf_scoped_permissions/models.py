from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from rest_framework_api_key.models import AbstractAPIKey


class ScopedAPIKey(AbstractAPIKey):
    """
    API Key model with scope-based permissions.

    Scopes are stored as a JSON array of strings in the format:
    ["resource.action", "resource2.action", ...]

    Examples:
        ["posts.read", "posts.write", "comments.read"]
    """

    scopes = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "API scopes this key has access to. "
            "Format: ['resource.action', ...]. "
            "Leave empty for unrestricted access (legacy mode)."
        )
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text="Last time this API key was used"
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Scoped API key"
        verbose_name_plural = "Scoped API keys"

    def has_scope(self, required_scope: str) -> bool:
        """
        Check if this API key has the required scope.

        Args:
            required_scope: Scope string in format "resource.action"

        Returns:
            True if the key has the scope, False otherwise
        """
        if not self.scopes:
            # Empty scopes = unrestricted access (backward compatible)
            return True

        return required_scope in self.scopes

    def update_last_used(self) -> None:
        """Update the last_used_at timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

    def __str__(self) -> str:
        scope_count = len(self.scopes) if self.scopes else "unrestricted"
        return f"{self.name} ({scope_count} scopes)"


class ScopedGroup(models.Model):
    """
    Extends Django's Group model with API scopes.

    Allows assigning scopes to user groups for JWT/session authentication.
    Users inherit all scopes from their groups.
    """

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="scoped_group",
        help_text="Django group to extend with scopes"
    )

    scopes = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "API scopes users in this group have access to. "
            "Format: ['resource.action', ...]. "
            "Empty list = no API access."
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drf_scoped_permissions_group"
        verbose_name = "Scoped group"
        verbose_name_plural = "Scoped groups"

    def has_scope(self, required_scope: str) -> bool:
        """
        Check if this group has the required scope.

        Args:
            required_scope: Scope string in format "resource.action"

        Returns:
            True if the group has the scope, False otherwise
        """
        return required_scope in self.scopes

    def __str__(self) -> str:
        scope_count = len(self.scopes) if self.scopes else 0
        return f"{self.group.name} ({scope_count} scopes)"
