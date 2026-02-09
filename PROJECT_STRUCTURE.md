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
