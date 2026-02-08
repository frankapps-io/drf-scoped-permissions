from typing import Any

from django.core.management.base import BaseCommand

from drf_scoped_permissions.utils import discover_scopes_with_apps


class Command(BaseCommand):
    """Management command to list all available API scopes."""

    help = "List all available API scopes discovered from viewsets"

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        scopes_with_apps = discover_scopes_with_apps()

        if not scopes_with_apps:
            self.stdout.write(
                self.style.WARNING("No scopes found. Make sure your viewsets are registered.")
            )
            return

        self.stdout.write(self.style.SUCCESS("Available API Scopes:"))
        self.stdout.write("")

        # Group by app label
        by_app: dict[str, dict[str, list[str]]] = {}
        for resource, (app_label, scope_list) in scopes_with_apps.items():
            if app_label not in by_app:
                by_app[app_label] = {}
            by_app[app_label][resource] = scope_list

        total_scopes = 0
        for app_label, resources in sorted(by_app.items()):
            self.stdout.write(self.style.MIGRATE_HEADING(f"[{app_label}]"))
            for resource, scope_list in sorted(resources.items()):
                self.stdout.write(self.style.WARNING(f"  {resource}:"))
                for scope in scope_list:
                    self.stdout.write(f"    - {scope}")
                    total_scopes += 1
            self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(f"Total: {len(scopes_with_apps)} resources, {total_scopes} scopes")
        )
