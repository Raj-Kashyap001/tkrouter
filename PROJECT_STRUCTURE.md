# tkrouter - Complete Project Structure

This document explains the complete file structure of the tkrouter package ready for PyPI publishing.

## Directory Layout

```
tkrouter/
│
├── tkrouter/                   # Main package directory
│   ├── __init__.py             # Package initialization & exports
│   ├── base.py                 # Abstract View base class
│   ├── core.py                 # Router, Store, navigation logic
│   └── async_bridge.py         # Async operations & caching
│
├── examples/                   # Example applications
│   ├── quick_start.py          # Simple 2-page example
│   └── user_management.py      # Full-featured demo with async
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── run_tests.py            # Run All Tests
│   ├── test_router.py
│   ├── test_store.py
│   ├── test_intigration.py
│   └── test_async_bridge.py
│
├── pyproject.toml              # Python package configuration
├── README.md                   # Main documentation
├── LICENSE                     # MIT License
├── MANIFEST.in                 # Additional files to include in package
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version history
└── PROJECT_STRUCTURE.md        # This file
```

## File Descriptions

### Core Package Files

#### `tkrouter/__init__.py` (17 lines)

- Package initialization
- Exports main classes: Router, Store, View, AsyncBridge
- Defines **version**
- Defines **all** for clean imports

#### `tkrouter/base.py`

- Abstract base class `View`
- Lifecycle hooks: on_enter, on_leave, on_data_received
- Grid management setup
- Active state tracking

#### `tkrouter/core.py`

- `Router` class - main navigation controller
- `Store` class - observable state management
- `RouteConfig`, `NavigationEntry` - data classes
- Navigation stack implementation
- View lifecycle management
- Error classes: RouterError, RouteNotFoundError

#### `tkrouter/async_bridge.py`

- `AsyncBridge` class - thread-safe async operations
- `CacheEntry` - cached data with TTL
- ThreadPoolExecutor integration
- Cache management with revalidation
- Main thread callback scheduling

### Examples

#### `examples/quick_start.py`

- Minimal example with 2 views
- Basic navigation demonstration
- Perfect for learning the basics

#### `examples/user_management.py`

- Complete application example
- Async data loading
- Cache revalidation
- Store subscriptions
- Multiple views with different purposes

### Configuration Files

#### `pyproject.toml`

- Modern Python packaging configuration (PEP 621)
- Package metadata
- Dependencies (none - stdlib only!)
- Build system configuration
- Classifiers for PyPI

#### `MANIFEST.in`

- Specifies additional files to include
- Ensures README, LICENSE are packaged
- Includes examples in distribution

#### `.gitignore`

- Python-specific ignore patterns
- Build artifacts
- Virtual environments
- IDE files
- OS-specific files

### Documentation

#### `README.md`

- Complete package documentation
- Installation instructions
- Quick start guide
- Core concepts explanation
- API reference
- Best practices
- Complete examples

#### `CHANGELOG.md`

- Version history
- Feature additions
- Bug fixes
- Breaking changes
- Planned features

#### `LICENSE`

- MIT License
- Copyright notice
- Permission terms

## File Sizes

```
13 text files.
12 unique files.
6  files ignored.

github.com/AlDanial/cloc v 2.08  T=0.03 s (379.0 files/s, 56943.5 lines/s)
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Markdown                         4            140              0            559
Python                           6            222            291            549
TOML                             1              3              0             35
Text                             1              0              0              4
-------------------------------------------------------------------------------
SUM:                            12            365            291           1147
-------------------------------------------------------------------------------
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone or create project
git init
git add .
git commit -m "Initial commit"
```

### 2. Install Development Tools

```bash
pip install --upgrade pip setuptools wheel twine build
```

### 3. Local Testing

```bash
# Install package locally in editable mode
pip install -e .

# Test it works
python examples/quick_start.py
python examples/demo.py
```

### 4. Build Package

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

### 5. Test on TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ tkrouter
```

### 6. Publish to PyPI

```bash
python -m twine upload dist/*
```

### 7. Tag Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Package Installation

Once published, users install with:

```bash
pip install tkrouter
```

## Import Structure

Users import from the package like this:

```python
# Main imports
from tkrouter import Router, View, Store

# If needed
from tkrouter import AsyncBridge, RouterError, RouteNotFoundError
```

## Dependencies

**Runtime:** NONE (only Python standard library)
**Build:** setuptools, wheel
**Dev:** twine, build

This makes tkrouter extremely portable and easy to deploy.

## Architecture Summary

**Design Pattern:** Grid Overlay Navigation

- All views occupy same grid cell (0, 0)
- Visibility managed via `tkraise()`
- No widget destruction on navigation (cached)

**Thread Safety:** Async Bridge Pattern

- Background threads for heavy operations
- UI updates via `root.after(0, callback)`
- Never touch Tkinter from background threads

**State Management:** Observer Pattern

- Global Store for shared state
- Subscribe/unsubscribe to specific keys
- Automatic notification on changes

**Lifecycle:** View Lifecycle Hooks

- on_enter: Initialization, data loading
- on_leave: Cleanup, save state
- on_data_received: Handle async results

## Future Enhancements

Potential features for v2.0:

1. Route middleware/guards
2. Nested routing
3. Path parameters (`/user/:id`)
4. Transition animations
5. Route history persistence
6. Deep linking
7. Lazy view loading
8. Route aliases

## Support & Contribution

- GitHub Issues: For bugs and features
- Pull Requests: Welcome!
- Discussions: For questions and ideas

## License

MIT License - See LICENSE file
