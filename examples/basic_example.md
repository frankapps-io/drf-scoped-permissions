# Basic Example

This is a minimal example of using drf-scoped-permissions in a Django project.

## Setup

```bash
pip install drf-scoped-permissions
```

## settings.py

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_api_key',
    'drf_scoped_permissions',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'drf_scoped_permissions.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'drf_scoped_permissions.permissions.HasAPIKeyOrGroupScope',
    ],
}
```

## views.py

```python
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    scope_resource = 'posts'  # This enables scope checking
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

## Create API Keys

### Via Django Admin

1. Go to `/admin/`
2. Navigate to "Scoped API keys"
3. Click "Add Scoped API key"
4. Select scopes (checkboxes are auto-generated)
5. Copy the generated key

### Programmatically

```python
from drf_scoped_permissions.models import ScopedAPIKey

api_key, key = ScopedAPIKey.objects.create_key(
    name="Mobile App",
    scopes=["posts.read", "posts.write"]
)

print(f"API Key: {key}")
```

## Usage

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/posts/
```

## List Available Scopes

```bash
python manage.py list_scopes
```
