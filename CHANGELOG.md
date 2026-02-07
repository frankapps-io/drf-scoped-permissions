# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-02-07

### Added
- migration command to convert existing API keys to `ScopedAPIKey` with empty copes (access to all resources)
- documentation on migrating existing API keys to the new model

[0.1.1]: https://github.com/frankapps-io/drf-scoped-permissions/releases/tag/v0.1.1

## [0.1.0] - 2025-02-04

### Added
- Initial release
- `ScopedAPIKey` model extending `djangorestframework-api-key`
- `ScopedGroup` model for user group scopes
- `HasAPIKeyOrGroupScope` permission class
- Automatic scope discovery from registered viewsets
- Django admin interface with dynamic scope checkboxes
- `list_scopes` management command
- Support for custom actions in viewsets
- Backward compatibility with unsecured API keys
- JWT token integration utilities
- Comprehensive documentation and examples

### Features
- ✅ Unified permission model for API keys and user groups
- ✅ Auto-discovery of scopes from viewsets
- ✅ Django Admin integration
- ✅ Backward compatible legacy mode
- ✅ Production-ready security practices
- ✅ Full type hints support

[0.1.0]: https://github.com/frankapps-io/drf-scoped-permissions/releases/tag/v0.1.0
