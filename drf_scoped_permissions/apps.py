from django.apps import AppConfig


class DrfScopedPermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_scoped_permissions"
    verbose_name = "DRF Scoped Permissions"

    def ready(self):
        """Import signal handlers."""
        pass  # Add signal handlers here if needed
