# Roadmap

## Current State (v0.3.0)

### What's Done
- [x] Core models: `ScopedAPIKey`, `ScopedGroup`
- [x] Permission class: `HasAPIKeyOrGroupScope`
- [x] Authentication backend: `APIKeyAuthentication`
- [x] Django admin integration with dynamic scope checkboxes (grouped by app)
- [x] Automatic scope discovery from viewsets
- [x] Centralized resource name resolution via `get_resource_name()`
- [x] Management commands: `list_scopes` (grouped by app), `migrate_api_keys`
- [x] Expiry check for API keys
- [x] Opt-in `last_used_at` tracking via `SCOPED_PERMISSIONS_TRACK_LAST_USED`
- [x] N+1 query optimization for user group scopes
- [x] Test coverage at 90% (64 tests)

### Version Requirements
- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+
- djangorestframework-api-key 3.0+

---

## Known Limitations

### Test Coverage Gaps
- `authentication.py` at 84% - custom header path untested
- `permissions.py` lines 191-201 - HTTP method fallback (non-viewset views)

### Code Paths Not Covered
1. **Custom API key header** (`API_KEY_CUSTOM_HEADER`) - documented but untested
2. **Empty scope discovery** - when no viewsets are registered

### Design Decisions to Revisit
1. **Revoked key handling**: Currently `djangorestframework-api-key` filters revoked keys in `get_from_key()`, so our revoked check is never reached. Consider if this is the desired behavior.
2. **Scope separator**: Currently hardcoded as `.` (e.g., `posts.read`). Could be configurable.

---

## v0.2.0 - Completed

### Done
- [x] Centralized scope resource name resolution (`get_resource_name()`)
- [x] Fixed mismatch between scope discovery and permission checking
- [x] Admin scopes grouped by Django app, then by resource
- [x] `list_scopes` command output grouped by app
- [x] Added admin form tests (coverage at 89%)
- [x] Test coverage increased to 90% (64 tests)
- [x] Pre-commit hooks with ruff and version checks

---

## v0.3.0 - Planned Improvements

### Testing
- [ ] Test custom header authentication path
- [ ] Test empty scope discovery scenario

### Features
- [ ] Configurable scope separator (default `.`, allow `:` etc.)
- [ ] Wildcard scopes (e.g., `posts.*` grants all post actions)
- [ ] Scope inheritance (e.g., `posts.write` implies `posts.read`)

### Performance
- [ ] Optional async `last_used_at` tracking (Celery task)
- [ ] Cache user scopes (per-request or short TTL)

### Documentation
- [ ] Add Sphinx docs
- [ ] API reference
- [ ] More examples (microservices, multi-tenant)

---

## v0.4.0 - Future Ideas

### Features
- [ ] JWT claim integration - read scopes directly from JWT `scopes` claim
- [ ] Scope aliases (e.g., `admin` = `["posts.*", "users.*"]`)
- [ ] Rate limiting per scope
- [ ] Audit logging for scope checks
- [ ] Django signals for permission events

### Admin Improvements
- [ ] Scope usage analytics in admin
- [ ] Bulk revoke API keys
- [ ] API key rotation helpers
- [ ] Export/import scopes

### Integrations
- [ ] Django Ninja support
- [ ] GraphQL (Strawberry/Graphene) support
- [ ] OpenAPI/Swagger scope documentation

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Priority areas for contributions:
1. Test coverage improvements
2. Documentation
3. Bug fixes
4. Feature requests with use cases

---

## Notes for Future Development

### Files Overview
```
drf_scoped_permissions/
├── __init__.py          # Package metadata
├── admin.py             # Django admin (89% coverage)
├── apps.py              # App config
├── authentication.py    # API key auth backend (84% coverage)
├── models.py            # ScopedAPIKey, ScopedGroup (100% coverage)
├── permissions.py       # HasAPIKeyOrGroupScope (88% coverage)
├── utils.py             # Scope discovery & resource name resolution (88% coverage)
└── management/commands/
    ├── list_scopes.py       # CLI command (92% coverage)
    └── migrate_api_keys.py  # Migration from legacy API keys (94% coverage)
```

### Key Design Patterns
1. **Backward compatibility**: Empty scopes = unrestricted access (for API keys)
2. **Security default**: Empty scopes = no access (for user groups)
3. **Automatic discovery**: Scopes generated from viewset actions
4. **Explicit override**: `required_scope` attribute on views
5. **Centralized resolution**: `get_resource_name()` ensures discovery and permission checks use the same resource name (`scope_resource` → class name fallback)

### Settings Reference
```python
# settings.py

# Enable last_used_at tracking (default: False)
SCOPED_PERMISSIONS_TRACK_LAST_USED = True
```