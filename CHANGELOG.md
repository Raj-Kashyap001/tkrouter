# Changelog

All notable changes to tkrouter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-09

### Added

- Initial release
- Core routing system with push/pop navigation stack
- View base class with lifecycle hooks (on_enter, on_leave, on_data_received)
- Async bridge for thread-safe background operations
- Caching system with TTL and revalidation support
- Global state store with observable pattern
- Full type hints for better IDE support
- Comprehensive documentation and examples
- Zero external dependencies (standard library only)

### Features

- `Router` class for managing navigation
- `View` abstract base class
- `Store` for global state management
- `AsyncBridge` for background operations
- Grid-based overlay navigation system
- Thread-safe UI updates via `after()` scheduling

## [Unreleased]

### Planned Features

- Middleware support for route guards
- Nested routing
- Route parameters in path (e.g., `/user/:id`)
- Animation/transition hooks
- Route history persistence
- Deep linking support

---

## Version Format

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes
