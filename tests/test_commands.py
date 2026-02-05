"""
Tests for management commands.
"""

from io import StringIO

import pytest
from django.core.management import call_command

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
