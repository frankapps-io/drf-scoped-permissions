"""Management command to migrate legacy APIKey instances to ScopedAPIKey."""

from typing import Any

from django.core.management.base import BaseCommand

from drf_scoped_permissions.models import ScopedAPIKey


class Command(BaseCommand):
    """Migrate existing APIKey instances to ScopedAPIKey."""

    help = "Migrate legacy rest_framework_api_key APIKey instances to ScopedAPIKey"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without making changes",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            from rest_framework_api_key.models import APIKey
        except ImportError:
            self.stderr.write(self.style.ERROR("rest_framework_api_key is not installed"))
            return

        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - no changes will be made\n"))

        # Get existing prefixes to avoid duplicates
        existing_prefixes = set(ScopedAPIKey.objects.values_list("prefix", flat=True))

        legacy_keys = APIKey.objects.all()
        migrated = 0
        skipped = 0

        for old_key in legacy_keys:
            if old_key.prefix in existing_prefixes:
                self.stdout.write(
                    f"  SKIP: {old_key.name} (prefix {old_key.prefix} already exists)"
                )
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"  WOULD MIGRATE: {old_key.name} ({old_key.prefix})")
            else:
                ScopedAPIKey.objects.create(
                    id=old_key.id,
                    name=old_key.name,
                    prefix=old_key.prefix,
                    hashed_key=old_key.hashed_key,
                    created=old_key.created,
                    revoked=old_key.revoked,
                    expiry_date=old_key.expiry_date,
                    scopes=[],  # Empty = unrestricted access
                )
                self.stdout.write(f"  MIGRATED: {old_key.name} ({old_key.prefix})")

            migrated += 1

        self.stdout.write("")
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Would migrate {migrated} keys, skip {skipped} duplicates")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Migrated {migrated} keys, skipped {skipped} duplicates")
            )
            if migrated > 0:
                self.stdout.write(
                    self.style.WARNING(
                        "\nIMPORTANT: Legacy API keys still exist in the original table.\n"
                        "They will continue to work until you revoke or delete them.\n"
                        "Once migration is verified, delete legacy keys via:\n"
                        "  from rest_framework_api_key.models import APIKey\n"
                        "  APIKey.objects.all().delete()\n"
                        "\nMigrated keys have empty scopes (unrestricted access).\n"
                        "Use the admin to add scopes as needed."
                    )
                )
