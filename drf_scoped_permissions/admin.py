from __future__ import annotations

from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.utils.safestring import SafeString, mark_safe
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import ScopedAPIKey, ScopedGroup
from .utils import get_scopes_grouped_by_app, get_scopes_grouped_by_resource


class GroupedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    A checkbox widget that groups choices by resource.

    Expects choices in format: [("resource.action", "Resource: Action"), ...]
    Groups them by resource for a cleaner display.
    """

    def render(
        self, name: str, value: Any, attrs: dict[str, Any] | None = None, renderer: Any = None
    ) -> SafeString:
        if value is None:
            value = []

        # Get scopes grouped by app and resource
        scopes_by_app = get_scopes_grouped_by_app()

        if not scopes_by_app:
            return mark_safe(
                '<p class="help">No scopes discovered. Add required_scopes to your viewsets.</p>'
            )

        html_parts = ['<div class="scope-apps">']

        for app_label, resources in sorted(scopes_by_app.items()):
            html_parts.append('<div class="scope-app">')
            html_parts.append(f'<h3 class="scope-app-header">{app_label}</h3>')
            html_parts.append('<div class="scope-groups">')

            for group_name, scopes in sorted(resources.items()):
                html_parts.append('<fieldset class="scope-group">')
                html_parts.append(f"<legend>{group_name}</legend>")

                for scope_value, scope_label in scopes:
                    checked = "checked" if scope_value in value else ""
                    checkbox_id = f"id_{name}_{scope_value.replace('.', '_')}"
                    html_parts.append(
                        f'<div class="checkbox-row">'
                        f'<label for="{checkbox_id}">'
                        f'<input type="checkbox" name="{name}" value="{scope_value}" '
                        f'id="{checkbox_id}" {checked}> {scope_label}'
                        f"</label></div>"
                    )

                html_parts.append("</fieldset>")

            html_parts.append("</div>")
            html_parts.append("</div>")

        html_parts.append("</div>")
        html_parts.append("""
            <style>
                .scope-apps { }
                .scope-app { margin-bottom: 15px; }
                .scope-app-header { margin: 10px 0 5px; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                .scope-groups { display: flex; flex-wrap: wrap; gap: 20px; }
                .scope-group { border: 1px solid #ccc; padding: 10px; min-width: 200px; }
                .scope-group legend { font-weight: bold; padding: 0 5px; }
                .checkbox-row { margin: 5px 0; }
            </style>
        """)

        return mark_safe("".join(html_parts))

    def value_from_datadict(self, data: Any, files: Any, name: str) -> list[str]:
        """Get list of selected scope values."""
        if hasattr(data, "getlist"):
            return list(data.getlist(name))
        return list(data.get(name, []))


class ScopedAPIKeyForm(forms.ModelForm):
    """Form for ScopedAPIKey with grouped scope checkboxes."""

    scopes = forms.MultipleChoiceField(
        choices=[],  # Populated dynamically
        widget=GroupedCheckboxSelectMultiple,
        required=False,
        help_text="Select which resources and actions this API key can access. Leave all unchecked for unrestricted access.",
    )

    class Meta:
        model = ScopedAPIKey
        fields = ["name", "scopes", "revoked", "expiry_date"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Populate choices from discovered scopes
        scope_groups = get_scopes_grouped_by_resource()
        all_choices: list[tuple[str, str]] = []
        for scopes in scope_groups.values():
            all_choices.extend(scopes)
        self.fields["scopes"].choices = all_choices  # type: ignore[attr-defined]

        # Set initial value from instance
        if self.instance.pk and self.instance.scopes:
            self.fields["scopes"].initial = self.instance.scopes

    def clean_scopes(self) -> list[str]:
        """Ensure scopes is a list."""
        scopes = self.cleaned_data.get("scopes", [])
        if isinstance(scopes, str):
            return [scopes] if scopes else []
        return list(scopes) if scopes else []


@admin.register(ScopedAPIKey)
class ScopedAPIKeyAdmin(APIKeyModelAdmin):
    """Admin interface for ScopedAPIKey with scope management."""

    form = ScopedAPIKeyForm

    list_display = (  # type: ignore[assignment]
        "name",
        "display_scopes",
        "prefix",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
    )
    list_filter = ("revoked", "created")  # type: ignore[assignment]
    search_fields = ("name", "prefix")
    readonly_fields = ()  # type: ignore[assignment]

    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Permissions",
            {
                "fields": ("scopes",),
                "description": "Select which resources and actions this API key can access.",
            },
        ),
        (
            "Status",
            {
                "fields": ("revoked", "expiry_date"),
            },
        ),
    )

    def get_form(
        self,
        request: HttpRequest,
        obj: ScopedAPIKey | None = None,
        change: bool = False,
        **kwargs: Any,
    ) -> type:
        # Explicitly set form fields to avoid Django extracting from fieldsets
        # which includes readonly fields that can't be in the form
        kwargs["fields"] = ["name", "scopes", "revoked", "expiry_date"]
        return super().get_form(request, obj, change, **kwargs)

    @display(description="Scopes")
    def display_scopes(self, obj: ScopedAPIKey) -> str:
        """Display scopes in a human-readable format."""
        if not obj.scopes:
            return "⚠️ Unrestricted (legacy)"

        # Group scopes by resource for display
        grouped: dict[str, list[str]] = {}
        for scope in obj.scopes:
            if "." not in scope:
                continue
            resource, action = scope.split(".", 1)
            if resource not in grouped:
                grouped[resource] = []
            grouped[resource].append(action)

        result = []
        for resource, actions in sorted(grouped.items()):
            result.append(f"{resource}({', '.join(sorted(actions))})")

        return " | ".join(result)


class ScopedGroupForm(forms.ModelForm):
    """Form for ScopedGroup with grouped scope checkboxes."""

    scopes = forms.MultipleChoiceField(
        choices=[],
        widget=GroupedCheckboxSelectMultiple,
        required=False,
        help_text="Select which API resources and actions users in this group can access.",
    )

    class Meta:
        model = ScopedGroup
        fields = ["group", "scopes"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Populate choices from discovered scopes
        scope_groups = get_scopes_grouped_by_resource()
        all_choices: list[tuple[str, str]] = []
        for scopes in scope_groups.values():
            all_choices.extend(scopes)
        self.fields["scopes"].choices = all_choices  # type: ignore[attr-defined]

        # Set initial value from instance
        if self.instance.pk and self.instance.scopes:
            self.fields["scopes"].initial = self.instance.scopes

    def clean_scopes(self) -> list[str]:
        """Ensure scopes is a list."""
        scopes = self.cleaned_data.get("scopes", [])
        if isinstance(scopes, str):
            return [scopes] if scopes else []
        return list(scopes) if scopes else []


class ScopedGroupInline(admin.StackedInline):
    """Inline admin for ScopedGroup."""

    model = ScopedGroup
    form = ScopedGroupForm
    can_delete = False
    verbose_name_plural = "API Scopes"
    fields = ["scopes"]


# Unregister the original Group admin and register our extended version
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """Extended Group admin with API scopes."""

    inlines = [ScopedGroupInline]
