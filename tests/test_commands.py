"""
Tests for management commands.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework_api_key.models import APIKey

from drf_scoped_permissions.models import ScopedAPIKey

pytestmark = pytest.mark.django_db


class TestListScopesCommand:
    """Test the list_scopes management command."""

    def test_list_scopes_outputs_discovered_scopes(self):
        """Test that list_scopes command outputs discovered scopes."""
        out = StringIO()
        call_command("list_scopes", stdout=out)
        output = out.getvalue()

        # Should show available scopes header
        assert "Available API Scopes" in output

        # Should find post/posts resource from test URLs
        assert "post" in output.lower()

        # Should show scope actions
        assert "read" in output
        assert "write" in output
        assert "delete" in output

        # Should show total count
        assert "Total:" in output


class TestMigrateApiKeysCommand:
    """Test the migrate_api_keys management command."""

    def test_migrate_api_keys_dry_run(self):
        """Test dry run mode shows info without making changes."""
        legacy_key, _ = APIKey.objects.create_key(name="Dry Run Test Key")
        assert 0 == ScopedAPIKey.objects.count()

        out = StringIO()
        call_command("migrate_api_keys", "--dry-run", stdout=out)
        output = out.getvalue()

        assert "DRY RUN" in output, "Should indicate this is a dry run"
        assert 0 == ScopedAPIKey.objects.count(), "Dry run should not create any keys"
        assert not ScopedAPIKey.objects.filter(prefix=legacy_key.prefix).exists()

    def test_migrate_api_keys_actually_migrates(self):
        """Test that migration actually creates ScopedAPIKey from legacy key."""
        legacy_key, _ = APIKey.objects.create_key(name="Migration Test Key")
        assert ScopedAPIKey.objects.count() == 0

        out = StringIO()
        call_command("migrate_api_keys", stdout=out)
        output = out.getvalue()

        # Should show it was migrated
        assert "MIGRATED" in output
        assert "Migration Test Key" in output

        # Key should now exist in ScopedAPIKey
        migrated_key = ScopedAPIKey.objects.get(prefix=legacy_key.prefix)
        assert migrated_key.name == "Migration Test Key"
        assert migrated_key.scopes == [], "Migrated keys should have empty scopes"
        assert migrated_key.hashed_key == legacy_key.hashed_key
        assert 1 == APIKey.objects.count(), "Legacy key remains intact after migration"

    def test_migrate_api_keys_skips_duplicates(self):
        """Test that existing keys with same prefix are skipped."""
        legacy_key, _ = APIKey.objects.create_key(name="Legacy Key")
        legacy_prefix = legacy_key.prefix

        # Create a ScopedAPIKey with same prefix manually
        ScopedAPIKey.objects.create(
            id=f"{legacy_prefix}.test123",
            name="Existing Scoped Key",
            prefix=legacy_prefix,
            hashed_key="test123",
            scopes=[],
        )
        assert 1 == ScopedAPIKey.objects.filter(prefix=legacy_prefix).count(), (
            "Only one key with that prefix should exist before migration"
        )

        out = StringIO()
        call_command("migrate_api_keys", stdout=out)
        output = out.getvalue()

        # Should skip the duplicate
        assert "SKIP" in output
        assert 1 == ScopedAPIKey.objects.filter(prefix=legacy_prefix).count(), (
            "Should still only have one key with that prefix"
        )
