# DRF Scoped Permissions

Resource-scoped API key and group permissions for Django REST Framework.

[![PyPI version](https://badge.fury.io/py/drf-scoped-permissions.svg)](https://badge.fury.io/py/drf-scoped-permissions)
[![Python versions](https://img.shields.io/pypi/pyversions/drf-scoped-permissions.svg)](https://pypi.org/project/drf-scoped-permissions/)
[![Django versions](https://img.shields.io/pypi/djversions/drf-scoped-permissions.svg)](https://pypi.org/project/drf-scoped-permissions/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What is this?

A Django package that adds scope-based permissions to your API keys and user groups. Instead of API keys having full access to everything, you can limit them to specific resources and actions.

Works with API keys (for service-to-service auth), user groups (for regular users), and JWT tokens.

## Features

- Scope-based permissions for API keys and user groups
- Automatic scope discovery from your viewsets
- Django admin integration with checkboxes
- Works alongside existing authentication
- Backward compatible - keys without scopes still work
- Built on `djangorestframework-api-key`

## Installation

```bash
pip install drf-scoped-permissions
```

### Requirements

- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_api_key',
    'drf_scoped_permissions',
]
```

### 2. Run Migrations

```bash
python manage.py migrate drf_scoped_permissions
```

### 3. Use in Your Views

```python
# views.py
from rest_framework import viewsets
from drf_scoped_permissions.permissions import HasAPIKeyOrGroupScope

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAPIKeyOrGroupScope]
    scope_resource = 'posts'  # Auto-generates: posts.read, posts.write, posts.delete
    
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

### 4. Create API Keys in Django Admin

1. Go to Django Admin → API Keys → Scoped API keys
2. Click "Add Scoped API Key"
3. Select scopes (checkboxes are auto-generated from your viewsets)
4. Save and copy the generated key

### 5. Use the API Key

```bash
curl -H "Authorization: Api-Key YOUR_API_KEY" \
     http://localhost:8000/api/posts/
```

## How It Works

### Scope Format

Scopes follow the pattern: `resource.action`

- `posts.read` - Read access to posts (GET, HEAD, OPTIONS)
- `posts.write` - Write access to posts (POST, PUT, PATCH)
- `posts.delete` - Delete access to posts (DELETE)
- `posts.publish` - Custom action access (custom @action methods)

### Auto-Discovery

Scopes are automatically discovered from your viewsets:

```python
# This viewset automatically creates:
# - posts.read (from list/retrieve)
# - posts.write (from create/update/partial_update)
# - posts.delete (from destroy)
# - posts.publish (from custom action)

class PostViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        # Custom action
        pass
```

## Usage Examples

### API Keys (Service Accounts)

```python
from drf_scoped_permissions.models import ScopedAPIKey

# Create API key with limited scopes
api_key, key = ScopedAPIKey.objects.create_key(
    name="Mobile App Backend",
    scopes=["posts.read", "posts.write", "comments.read"]
)

print(f"API Key: {key}")  # Give this to your service
```

### User Groups (Human Users)

```python
from django.contrib.auth.models import Group
from drf_scoped_permissions.models import ScopedGroup

# Create group with scopes
editors = Group.objects.create(name='Editors')
ScopedGroup.objects.create(
    group=editors,
    scopes=["posts.read", "posts.write", "comments.read", "comments.write"]
)

# Add users to group
user.groups.add(editors)
```

### JWT Tokens

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'drf_scoped_permissions.permissions.HasAPIKeyOrGroupScope',
    ],
}

# Scopes from user's groups are automatically checked
# You can also include scopes in JWT claims (see Advanced Usage)
```

### Explicit Scope Requirements

```python
class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [HasAPIKeyOrGroupScope]
    required_scope = 'analytics.export'  # Explicit scope requirement
    
    def list(self, request):
        return Response({'data': 'analytics'})
```

### Custom Actions

```python
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [HasAPIKeyOrGroupScope]
    scope_resource = 'posts'
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        # Requires 'posts.publish' scope
        post = self.get_object()
        post.published = True
        post.save()
        return Response({'status': 'published'})
```

## Advanced Usage

### Backward Compatibility

API keys without scopes have unrestricted access (legacy mode):

```python
# Old API key with no scopes
api_key = ScopedAPIKey.objects.create(name="Legacy Key")
# Scopes: [] (empty) → Full access to everything
```

### Including Scopes in JWT Tokens

```python
# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add user scopes to token
        from drf_scoped_permissions.utils import get_user_scopes
        token['scopes'] = list(get_user_scopes(user))
        
        return token
```

### Management Commands

**List available scopes:**

```bash
python manage.py list_scopes
```

Output:
```
Available API Scopes:

posts:
  - posts.read
  - posts.write
  - posts.delete
  - posts.publish

comments:
  - comments.read
  - comments.write
  - comments.delete
```

**Migrate legacy API keys:**

```bash
# Preview migration
python manage.py migrate_api_keys --dry-run

# Run migration
python manage.py migrate_api_keys
```

### Custom Permission Class

```python
from drf_scoped_permissions.permissions import HasAPIKeyOrGroupScope

class CustomScopePermission(HasAPIKeyOrGroupScope):
    def get_required_scope(self, request, view):
        # Custom logic for determining required scope
        if view.action == 'special_action':
            return 'posts.special'
        return super().get_required_scope(request, view)
```

## Configuration

### Settings

```python
# settings.py

# Track when API keys are last used (default: False)
# When enabled, updates last_used_at on every authenticated request
# Note: This adds a database write per request - enable only if needed
SCOPED_PERMISSIONS_TRACK_LAST_USED = True
```

## Django Admin

The package provides a user-friendly admin interface:

### API Keys Admin
- Create/revoke API keys
- Select scopes via organized checkboxes (grouped by resource)
- View masked keys for security
- Track creation date and last used

### Groups Admin
- Extended Django Groups with scope management
- Same checkbox interface as API keys
- Scopes automatically apply to all users in group

## Security Considerations

### API Key Storage
- Keys are hashed using Django's password hashers
- Only shown once upon creation
- Stored securely in database

### Best Practices
- ✅ Use HTTPS in production
- ✅ Rotate API keys regularly
- ✅ Use minimal scopes (principle of least privilege)
- ✅ Monitor API key usage via `last_used_at`
- ✅ Revoke unused keys

### Not Recommended For
- ❌ User authentication (use Django auth + sessions)
- ❌ Public API keys (they should be server-side only)
- ❌ Mobile app auth (use OAuth2 or JWT)

## Testing

```python
from django.test import TestCase
from drf_scoped_permissions.models import ScopedAPIKey

class APITestCase(TestCase):
    def test_api_key_scopes(self):
        api_key, key = ScopedAPIKey.objects.create_key(
            name="Test Key",
            scopes=["posts.read"]
        )
        
        response = self.client.get(
            '/api/posts/',
            HTTP_AUTHORIZATION=f'Api-Key {key}'
        )
        
        self.assertEqual(response.status_code, 200)
```

## Migration Guide

### From `djangorestframework-api-key`

If you're already using `djangorestframework-api-key`:

1. Install `drf-scoped-permissions`
2. Run migrations: `python manage.py migrate drf_scoped_permissions`
3. Migrate existing API keys:

```bash
# Preview what will be migrated
python manage.py migrate_api_keys --dry-run

# Run the migration
python manage.py migrate_api_keys
```

4. Migrated keys have empty scopes (unrestricted access) - same as before
5. Add scopes via Django admin when ready
6. Once verified, delete legacy keys:

```python
from rest_framework_api_key.models import APIKey
APIKey.objects.all().delete()
```

### From Manual Implementation

1. Replace your custom models with `ScopedAPIKey` and `ScopedGroup`
2. Replace permission classes with `HasAPIKeyOrGroupScope`
3. Update admin to use provided admin classes
4. Remove custom scope discovery code (now automatic)

## Examples

See the [examples directory](examples/) for complete example projects:

- **Basic Setup** - Minimal configuration
- **Microservices** - Service-to-service authentication
- **Multi-tenant** - Scoping by organization
- **JWT Integration** - Token-based auth with scopes

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/yourusername/drf-scoped-permissions.git
cd drf-scoped-permissions
pip install -e ".[dev]"
make install-hooks  # installs pre-commit hook (ruff auto-fix + mypy)
pytest
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built on top of the excellent [djangorestframework-api-key](https://github.com/florimondmanca/djangorestframework-api-key) package.

## Support

- 📖 [Documentation](https://github.com/frankapps-io/drf-scoped-permissions)
- 🐛 [Report Issues](https://github.com/frankapps-io/drf-scoped-permissions/issues)
- 💬 [Discussions](https://github.com/frankapps-io/drf-scoped-permissions/discussions)
- 📧 Email: hello@frankapps.com

## About Frankapps

We help startups ship faster with battle-tested Django tools and consulting.

- 🛠️ **Open Source Tools** - Production-ready packages like this one
- 🚀 **Startup Consulting** - Django/React architecture and best practices
- 📚 **Technical Content** - Guides on building scalable APIs

**Need help with your Django project?** We specialize in helping startups build robust APIs quickly. [Get in touch →](mailto:hello@frankapps.com)

## Similar Projects

- [djangorestframework-api-key](https://github.com/florimondmanca/djangorestframework-api-key) - API keys without scopes
- [django-oauth-toolkit](https://github.com/jazzband/django-oauth-toolkit) - OAuth2 with scopes (more complex)
- [drf-access-policy](https://github.com/rsinger86/drf-access-policy) - Declarative policies (no API key integration)

**DRF Scoped Permissions** combines the simplicity of API keys with the flexibility of scoped permissions.
