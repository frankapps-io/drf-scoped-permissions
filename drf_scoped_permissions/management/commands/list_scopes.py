from typing import Any

from django.core.management.base import BaseCommand

from drf_scoped_permissions.utils import discover_scopes_from_urls


class Command(BaseCommand):
    """Management command to list all available API scopes."""

    help = "List all available API scopes discovered from viewsets"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        scopes = discover_scopes_from_urls()

        if not scopes:
            self.stdout.write(
                self.style.WARNING("No scopes found. Make sure your viewsets are registered.")
            )
            return

        self.stdout.write(self.style.SUCCESS("Available API Scopes:"))
        self.stdout.write("")

        total_scopes = 0
        for resource, scope_list in sorted(scopes.items()):
            self.stdout.write(self.style.WARNING(f"{resource}:"))
            for scope in scope_list:
                self.stdout.write(f"  - {scope}")
                total_scopes += 1
            self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(f"Total: {len(scopes)} resources, {total_scopes} scopes")
        )
