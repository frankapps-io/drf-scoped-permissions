# Roadmap

## Current State (v0.1.0)

### What's Done
- [x] Core models: `ScopedAPIKey`, `ScopedGroup`
- [x] Permission class: `HasAPIKeyOrGroupScope`
- [x] Authentication backend: `APIKeyAuthentication`
- [x] Django admin integration with dynamic scope checkboxes
- [x] Automatic scope discovery from viewsets
- [x] Management command: `list_scopes`
- [x] Expiry check for API keys
- [x] Opt-in `last_used_at` tracking via `SCOPED_PERMISSIONS_TRACK_LAST_USED`
- [x] N+1 query optimization for user group scopes
- [x] Test coverage at 71% (36 tests)

### Version Requirements
- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+
- djangorestframework-api-key 3.0+

---

## Known Limitations

### Test Coverage Gaps
- `admin.py` at 32% - admin form logic untested
- `utils.py` at 79% - some edge cases in scope discovery
- `authentication.py` lines 41-43 - custom header path untested
- `permissions.py` lines 190-200 - HTTP method fallback (non-viewset views)

### Code Paths Not Covered
1. **Custom API key header** (`API_KEY_CUSTOM_HEADER`) - documented but untested
2. **Views without `scope_resource` or `basename`** - returns `None` (no scope required)
3. **Empty scope discovery** - when no viewsets are registered

### Design Decisions to Revisit
1. **Revoked key handling**: Currently `djangorestframework-api-key` filters revoked keys in `get_from_key()`, so our revoked check (line 76) is never reached. Consider if this is the desired behavior.
2. **Scope separator**: Currently hardcoded as `.` (e.g., `posts.read`). Could be configurable.

---

## v0.2.0 - Planned Improvements

### Testing
- [ ] Add admin form tests (increase coverage to 80%+)
- [ ] Test custom header authentication path
- [ ] Test edge case: view without scope_resource returns None
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

## v0.3.0 - Future Ideas

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
├── admin.py             # Django admin (32% coverage - needs tests)
├── apps.py              # App config
├── authentication.py    # API key auth backend (84% coverage)
├── models.py            # ScopedAPIKey, ScopedGroup (100% coverage)
├── permissions.py       # HasAPIKeyOrGroupScope (86% coverage)
├── utils.py             # Scope discovery utilities (79% coverage)
└── management/commands/
    └── list_scopes.py   # CLI command (88% coverage)
```

### Key Design Patterns
1. **Backward compatibility**: Empty scopes = unrestricted access (for API keys)
2. **Security default**: Empty scopes = no access (for user groups)
3. **Automatic discovery**: Scopes generated from viewset actions
4. **Explicit override**: `required_scope` attribute on views

### Settings Reference
```python
# settings.py

# Enable last_used_at tracking (default: False)
SCOPED_PERMISSIONS_TRACK_LAST_USED = True
```