from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.request import Request

from .models import ScopedAPIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Authentication backend for API keys with scopes.

    Clients should pass the API key in the Authorization header:
        Authorization: Api-Key <api_key>

    The keyword can be overridden via the SCOPED_API_KEY_AUTH_KEYWORD setting.
    Keyword matching is case-insensitive.
    """

    keyword = getattr(settings, "SCOPED_API_KEY_AUTH_KEYWORD", None) or "Api-Key"

    def authenticate(self, request: Request) -> tuple[None, ScopedAPIKey] | None:
        """
        Authenticate the request using an API key.

        Returns:
            Tuple of (user, api_key) if authentication succeeds
            None if no API key is present

        Raises:
            AuthenticationFailed if the API key is invalid
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header:
            # Try custom header if configured
            api_key_header = getattr(request._request.META, "API_KEY_CUSTOM_HEADER", None)
            if api_key_header:
                key = request.META.get(api_key_header, "")
                if key:
                    return self.authenticate_credentials(key)
            return None

        try:
            keyword, key = auth_header.split(None, 1)
        except ValueError:
            return None

        if keyword.lower() != self.keyword.lower():
            return None

        return self.authenticate_credentials(key)

    def authenticate_credentials(self, key: str) -> tuple[None, ScopedAPIKey]:
        """
        Validate the API key and return the associated user.

        Args:
            key: The API key string

        Returns:
            Tuple of (None, api_key) - we don't authenticate as a specific user

        Raises:
            AuthenticationFailed if the key is invalid or revoked
        """
        try:
            # Use the API key crypto to hash and look up the key
            api_key = ScopedAPIKey.objects.get_from_key(key)
        except ScopedAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key") from None

        if api_key.revoked:
            raise exceptions.AuthenticationFailed("API key has been revoked")

        if api_key.has_expired:
            raise exceptions.AuthenticationFailed("API key has expired")

        # Update last used timestamp if enabled (disabled by default for performance)
        if getattr(settings, "SCOPED_PERMISSIONS_TRACK_LAST_USED", False):
            api_key.update_last_used()  # type: ignore[attr-defined]

        # Return (user, auth) - we return (None, api_key) since API keys
        # are not tied to specific users
        return None, api_key  # type: ignore[return-value]

    def authenticate_header(self, request: Request) -> str:
        """
        Return the WWW-Authenticate header value.

        Used when authentication fails to tell the client
        what authentication scheme is expected.
        """
        return self.keyword
