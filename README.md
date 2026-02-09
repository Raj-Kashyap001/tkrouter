<h1 align="center">TkRouter</h1>

Asynchronous multi-page navigation for Tkinter applications. Build multi-page Tkinter apps with React-like routing, async data loading, and global state management.

## Features

- 🚀 **Navigation**: Push/pop navigation stack similar to React Router
- ⚡ **Async/Await Pattern**: Thread-safe async operations with automatic UI thread scheduling
- 💾 **Caching**: Built-in data caching with TTL and revalidation support
- 🔄 **Lifecycle Hooks**: View lifecycle methods (on_enter, on_leave, on_data_received)
- 🌐 **Global State**: Observable store pattern for reactive state management
- 📦 **Zero Dependencies**: Uses only Python standard library (tkinter, threading, concurrent.futures)
- 🎯 **Type Safe**: Full type hints for better IDE support

## Installation

```bash
pip install tkrouter
```

## Quick Start

```python
import tkinter as tk
from tkrouter import Router, View

# Define a view
class HomeView(View):
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        tk.Label(self, text="Home Page").pack(pady=20)
        tk.Button(self, text="Go to Profile",
                 command=lambda: router.push('profile')).pack()

    def on_enter(self, params=None):
        print("Entered home view")

    def on_leave(self):
        print("Left home view")

    def on_data_received(self, data):
        pass

class ProfileView(View):
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        tk.Label(self, text="Profile Page").pack(pady=20)
        tk.Button(self, text="← Back", command=router.pop).pack()

    def on_enter(self, params=None):
        user_id = params.get('user_id') if params else None
        print(f"Viewing profile: {user_id}")

    def on_leave(self):
        pass

    def on_data_received(self, data):
        pass

# Setup application
root = tk.Tk()
root.geometry("600x400")

router = Router(root)
router.register_route('home', HomeView)
router.register_route('profile', ProfileView)
router.navigate('home')

root.mainloop()
```

## Core Concepts

### 1. Router

The `Router` manages navigation between views and coordinates async operations.

```python
from tkrouter import Router

router = Router(root)

# Register routes
router.register_route('home', HomeView)
router.register_route('profile', ProfileView, params={'default_tab': 'posts'})

# Navigate (replace stack)
router.navigate('home')

# Push to stack
router.push('profile', {'user_id': 123})

# Pop from stack
router.pop()

# Check if can go back
if router.can_pop():
    router.pop()
```

### 2. Views with Lifecycle Hooks

All views inherit from the `View` base class and must implement three lifecycle hooks:

```python
from tkrouter import View

class MyView(View):
    def on_enter(self, params=None):
        """
        Called when view becomes active.
        Use for initialization, data loading, animations.
        """
        user_id = params.get('user_id') if params else None
        self.load_user_data(user_id)

    def on_leave(self):
        """
        Called before navigating away.
        Use for cleanup, saving state, canceling operations.
        """
        self.cancel_pending_requests()

    def on_data_received(self, data):
        """
        Called when async data arrives.
        Use for updating UI with fetched data.
        """
        self.display_user(data)
```

### 3. Async Operations

Execute background tasks without blocking the UI:

```python
import time

def fetch_user_data(user_id):
    time.sleep(2)  # Simulate API call
    return {'id': user_id, 'name': 'John Doe'}

class ProfileView(View):
    def on_enter(self, params=None):
        user_id = params.get('user_id')

        # Run async operation
        self.router.run_async(
            fetch_user_data,
            user_id,
            callback=self.on_data_received,
            error_callback=self.on_error
        )

    def on_data_received(self, data):
        # Update UI (called on main thread)
        self.name_label.config(text=data['name'])

    def on_error(self, error):
        print(f"Error: {error}")
```

### 4. Caching with Revalidation

Cache async results to improve performance:

```python
class ProfileView(View):
    def on_enter(self, params=None):
        user_id = params.get('user_id')

        # Fetch with caching
        self.router.run_async_cached(
            cache_key=f'user_{user_id}',
            func=fetch_user_data,
            user_id=user_id,
            callback=self.on_data_received,
            ttl_seconds=300,  # Cache for 5 minutes
            revalidate=True   # Return cached data immediately, fetch fresh in background
        )
```

**Caching Options:**

- `cache_key`: Unique identifier for cached data
- `ttl_seconds`: Time-to-live in seconds (default: 300)
- `revalidate`: If `True`, returns cached data immediately while fetching fresh data in background

### 5. Global State Management

Share state across views using the observable Store:

```python
# Set state
router.store.set('user', {'id': 1, 'name': 'John'})
router.store.update({'theme': 'dark', 'language': 'en'})

# Get state
user = router.store.get('user')
theme = router.store.get('theme', 'light')  # with default

# Subscribe to changes
class SettingsView(View):
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)

        # Subscribe to theme changes
        self.observer = store.subscribe('theme', self.on_theme_change)

    def on_theme_change(self, key, value):
        print(f"Theme changed to: {value}")
        self.update_ui_theme(value)

    def on_leave(self):
        # Unsubscribe when leaving
        self.store.unsubscribe('theme', self.observer)
```

## Complete Example

Here's a complete example with async data loading, caching, and state management:

```python
import tkinter as tk
from tkinter import ttk
import time
from tkrouter import Router, View

# Simulated API call
def fetch_posts():
    time.sleep(1)
    return [
        {'id': 1, 'title': 'First Post', 'body': 'Hello World'},
        {'id': 2, 'title': 'Second Post', 'body': 'Tkinter Routing'},
    ]

class HomeView(View):
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        ttk.Label(self, text="Home", font=('Arial', 24)).pack(pady=20)
        ttk.Button(self, text="View Posts",
                  command=lambda: router.push('posts')).pack()

    def on_enter(self, params=None):
        pass

    def on_leave(self):
        pass

    def on_data_received(self, data):
        pass

class PostsView(View):
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)

        ttk.Button(self, text="← Back", command=router.pop).pack(anchor='nw')
        ttk.Label(self, text="Posts", font=('Arial', 20)).pack(pady=20)

        self.loading = ttk.Label(self, text="Loading...")
        self.loading.pack()

        self.posts_frame = ttk.Frame(self)
        self.posts_frame.pack(fill='both', expand=True, padx=20)

    def on_enter(self, params=None):
        self.loading.pack()

        # Fetch with caching
        self.router.run_async_cached(
            cache_key='posts',
            func=fetch_posts,
            callback=self.on_data_received,
            ttl_seconds=60
        )

    def on_leave(self):
        pass

    def on_data_received(self, data):
        self.loading.pack_forget()

        for post in data:
            frame = ttk.LabelFrame(self.posts_frame, text=post['title'])
            frame.pack(fill='x', pady=5)
            ttk.Label(frame, text=post['body']).pack(padx=10, pady=10)

# Application setup
root = tk.Tk()
root.title("tkrouter Example")
root.geometry("600x400")

router = Router(root)
router.register_route('home', HomeView)
router.register_route('posts', PostsView)
router.navigate('home')

root.mainloop()
```

## API Reference

### Router

#### Methods

- `register_route(name: str, view_class: Type[View], params: dict = None)` - Register a route
- `navigate(route_name: str, params: dict = None)` - Navigate to route (replace stack)
- `push(route_name: str, params: dict = None)` - Push route onto stack
- `pop() -> bool` - Pop current route from stack
- `can_pop() -> bool` - Check if can pop
- `get_current_route() -> str` - Get current route name
- `run_async(func, *args, callback=None, error_callback=None, **kwargs)` - Run async operation
- `run_async_cached(cache_key, func, *args, callback=None, ttl_seconds=300, revalidate=False, **kwargs)` - Run with caching

#### Properties

- `store: Store` - Global state store
- `async_bridge: AsyncBridge` - Async operation handler

### View

#### Lifecycle Methods (Abstract)

- `on_enter(params: dict = None)` - View entered
- `on_leave()` - View left
- `on_data_received(data: Any)` - Async data received

#### Properties

- `router: Router` - Router instance
- `store: Store` - Global store

### Store

#### Methods

- `get(key: str, default=None) -> Any` - Get value
- `set(key: str, value: Any)` - Set value (notifies observers)
- `update(updates: dict)` - Update multiple values
- `subscribe(key: str, callback: Callable) -> Observer` - Subscribe to changes
- `unsubscribe(key: str, observer: Observer)` - Unsubscribe
- `clear()` - Clear all state
- `get_all() -> dict` - Get all state

## Architecture

### Grid Overlay System

All views are placed in the same grid cell (0, 0) and use `tkraise()` for visibility:

```python
# In View.__init__
self.grid(row=0, column=0, sticky="nsew")

# In Router.push()
view.tkraise()  # Bring view to front
```

### Thread Safety

The async bridge ensures UI updates happen on the main thread:

```python
# Background thread
result = func(*args, **kwargs)

# Schedule callback on main thread
root.after(0, lambda: callback(result))
```

## Best Practices

1. **Always implement all lifecycle hooks** - Even if empty, implement all three methods
2. **Clean up in on_leave** - Cancel pending async operations, unsubscribe from store
3. **Use caching for expensive operations** - API calls, file I/O, computations
4. **Keep views stateless** - Store important state in the global Store
5. **Handle errors gracefully** - Always provide error_callback for async operations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Support

- **Issues**: [GitHub Issues](https://github.com/Raj-Kashyap001/tkrouter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Raj-Kashyap001/tkrouter/discussions)
