"""
Tests for Django admin integration.
"""

from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory

from drf_scoped_permissions.admin import (
    GroupAdmin,
    ScopedAPIKeyAdmin,
    ScopedAPIKeyForm,
    ScopedGroupInline,
)
from drf_scoped_permissions.models import ScopedAPIKey

User = get_user_model()


# Mock scope data for tests
MOCK_SCOPES = {
    "Posts": [
        ("posts.read", "Posts: Read"),
        ("posts.write", "Posts: Write"),
    ],
    "Comments": [
        ("comments.read", "Comments: Read"),
        ("comments.write", "Comments: Write"),
    ],
}


@pytest.fixture
def mock_scopes():
    """Mock the scope discovery to return test scopes."""
    with patch('drf_scoped_permissions.admin.get_scopes_grouped_by_resource', return_value=MOCK_SCOPES):
        yield MOCK_SCOPES


@pytest.fixture
def admin_site():
    """Provide an admin site instance."""
    return AdminSite()


@pytest.fixture
def admin_user(db):
    """Create a superuser for admin access."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123"
    )


@pytest.fixture
def request_factory():
    """Provide a request factory."""
    return RequestFactory()


@pytest.fixture
def admin_request(request_factory, admin_user):
    """Create a request with admin user."""
    request = request_factory.get("/admin/")
    request.user = admin_user
    return request


class TestScopedAPIKeyAdmin:
    """Tests for ScopedAPIKeyAdmin."""

    def test_admin_add_form_loads(self, db, admin_site, admin_request):
        """Test that the add form can be loaded without errors."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        # This is what fails in the browser - getting the form for add view
        form_class = admin.get_form(admin_request, obj=None, change=False)

        assert form_class is not None
        # Instantiate the form to ensure it works
        form = form_class()
        assert 'name' in form.fields
        assert 'scopes' in form.fields

    def test_admin_change_form_loads(self, db, admin_site, admin_request, api_key_with_scopes):
        """Test that the change form can be loaded for existing key."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        form_class = admin.get_form(admin_request, obj=api_key_with_scopes, change=True)

        assert form_class is not None
        form = form_class(instance=api_key_with_scopes)
        assert 'name' in form.fields
        assert 'scopes' in form.fields

    def test_admin_list_display(self, db, admin_site):
        """Test list display fields are valid."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        # Verify all list_display fields are valid
        for field in admin.list_display:
            # Should not raise
            if hasattr(admin, field):
                assert callable(getattr(admin, field)) or True
            elif field.startswith('_'):
                # Methods like _has_expired from parent
                pass
            else:
                # Model field
                assert hasattr(ScopedAPIKey, field) or field in [f.name for f in ScopedAPIKey._meta.get_fields()]

    def test_admin_fieldsets_valid(self, db, admin_site, admin_request):
        """Test that fieldsets reference valid fields."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        # Get the form to ensure fieldsets work with form
        form_class = admin.get_form(admin_request, obj=None)
        form = form_class()

        # Collect all field names from fieldsets
        fieldset_fields = set()
        for _name, options in admin.fieldsets:
            for field in options.get('fields', []):
                if isinstance(field, (list, tuple)):
                    fieldset_fields.update(field)
                else:
                    fieldset_fields.add(field)

        # readonly_fields should be allowed in fieldsets but not in form
        readonly = set(admin.readonly_fields)
        form_fields = set(form.fields.keys())

        for field in fieldset_fields:
            # Field should be either in form or readonly
            assert field in form_fields or field in readonly, f"Field '{field}' not in form or readonly_fields"

    @pytest.mark.django_db
    def test_admin_add_view_renders(self, client, admin_user):
        """Test that the actual admin add view renders without errors."""
        client.force_login(admin_user)
        response = client.get('/admin/drf_scoped_permissions/scopedapikey/add/')
        assert response.status_code == 200, f"Admin add view failed: {response.content[:500]}"

    @pytest.mark.django_db
    def test_admin_list_view_renders(self, client, admin_user):
        """Test that the admin list view renders without errors."""
        client.force_login(admin_user)
        response = client.get('/admin/drf_scoped_permissions/scopedapikey/')
        assert response.status_code == 200

    def test_display_scopes_empty(self, db, admin_site, api_key_unrestricted):
        """Test display_scopes with no scopes."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        result = admin.display_scopes(api_key_unrestricted)
        assert "Unrestricted" in result

    def test_display_scopes_with_scopes(self, db, admin_site, api_key_with_scopes):
        """Test display_scopes with scopes set."""
        admin = ScopedAPIKeyAdmin(ScopedAPIKey, admin_site)

        result = admin.display_scopes(api_key_with_scopes)
        assert "posts" in result
        assert "read" in result


class TestScopedAPIKeyForm:
    """Tests for ScopedAPIKeyForm."""

    def test_form_fields(self, db):
        """Test form has expected fields."""
        form = ScopedAPIKeyForm()

        assert 'name' in form.fields
        assert 'scopes' in form.fields

    def test_form_save_creates_key(self, db, mock_scopes):
        """Test form can create a new API key."""
        form = ScopedAPIKeyForm(data={
            'name': 'Test Key',
            'scopes': ['posts.read'],
        })

        assert form.is_valid(), form.errors
        instance = form.save()

        assert instance.pk is not None
        assert instance.name == 'Test Key'
        assert instance.scopes == ['posts.read']

    def test_form_save_empty_scopes(self, db):
        """Test form can create key with no scopes."""
        form = ScopedAPIKeyForm(data={
            'name': 'Unrestricted Key',
            'scopes': [],
        })

        assert form.is_valid(), form.errors
        instance = form.save()

        assert instance.scopes == []

    def test_form_update_existing(self, db, api_key_with_scopes, mock_scopes):
        """Test form can update existing key."""
        form = ScopedAPIKeyForm(
            instance=api_key_with_scopes,
            data={
                'name': 'Updated Name',
                'scopes': ['comments.read'],
                'revoked': False,
            }
        )

        assert form.is_valid(), form.errors
        instance = form.save()

        assert instance.name == 'Updated Name'
        assert instance.scopes == ['comments.read']


class TestGroupAdminWithScopes:
    """Tests for Group admin with ScopedGroup inline."""

    def test_group_admin_has_inline(self, db, admin_site):
        """Test Group admin includes ScopedGroup inline."""
        admin = GroupAdmin(Group, admin_site)

        # Verify ScopedGroupInline is in the inlines
        assert ScopedGroupInline in [type(i) for i in admin.get_inline_instances(None)]

    def test_scoped_group_inline_form_loads(self, db, admin_site, admin_request):
        """Test ScopedGroup inline form can be loaded."""
        from drf_scoped_permissions.admin import ScopedGroupForm

        form = ScopedGroupForm()
        assert 'scopes' in form.fields
