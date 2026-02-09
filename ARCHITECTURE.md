# tkrouter Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Tkinter Root Window                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 Router Container (Frame)                  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  All Views in Same Grid Cell (0,0)                  │  │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │  │
│  │  │  │  View 1  │  │  View 2  │  │  View 3  │  (stack)  │  │  │
│  │  │  │  [back]  │  │ [active] │  │  [back]  │           │  │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘           │  │  │
│  │  │  ↑ Managed by Router via .tkraise()                 │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                            Router                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐      ┌─────────────────┐                     │
│  │ Navigation     │      │  View Registry  │                     │
│  │ Stack          │      │  {name: View}   │                     │
│  │ [Entry, Entry] │      └─────────────────┘                     │
│  └────────────────┘                                              │
│         ↕                                                        │
│  ┌────────────────┐      ┌─────────────────┐                     │
│  │  Async Bridge  │←────→│  Global Store   │                     │
│  │  + Caching     │      │  + Observers    │                     │
│  └────────────────┘      └─────────────────┘                     │
│         ↕                         ↕                              │
└─────────│─────────────────────────│──────────────────────────────┘
          │                         │
          ↓                         ↓
    ┌──────────┐              ┌──────────┐
    │Background│              │  Views   │
    │ Threads  │              │Subscribe │
    └──────────┘              └──────────┘
```

## Data Flow - Navigation

```
User Action
    ↓
router.push('profile', {user_id: 1})
    ↓
┌─────────────────────────────┐
│ 1. Call current.on_leave()  │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ 2. Push to nav stack        │
│    [{route:'profile',       │
│      params:{user_id:1}}]   │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ 3. Get/create view          │
│    view = _views['profile'] │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ 4. Raise view to front      │
│    view.tkraise()           │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ 5. Call view.on_enter()     │
│    with params              │
└─────────────────────────────┘
```

## Data Flow - Async Operation

```
View.on_enter()
    ↓
router.run_async_cached(
    cache_key='user_1',
    func=fetch_user,
    callback=on_data_received
)
    ↓
┌──────────────────────────────┐
│ Check Cache                  │
│ if valid → return cached     │
│ if not → fetch               │
└──────────────────────────────┘
    ↓ (if fetching)
┌──────────────────────────────┐
│ ThreadPoolExecutor           │
│ - Submit to background thread│
└──────────────────────────────┘
    ↓
┌──────────────────────────────┐
│ Background Thread            │
│ result = fetch_user(1)       │
└──────────────────────────────┘
    ↓
┌──────────────────────────────┐
│ Store in Cache               │
│ {key: 'user_1',              │
│  data: result,               │
│  ttl: 300 seconds}           │
└──────────────────────────────┘
    ↓
┌──────────────────────────────┐
│ Schedule on Main Thread      │
│ root.after(0,                │
│   lambda: callback(result))  │
└──────────────────────────────┘
    ↓
┌──────────────────────────────┐
│ View.on_data_received(data)  │
│ - Update UI                  │
│ - All on main thread ✓       │
└──────────────────────────────┘
```

## Store Observable Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                         Store                               │
│  _state = {                                                 │
│    'user': {...},                                           │
│    'theme': 'dark',                                         │
│  }                                                          │
│                                                             │
│  _observers = {                                             │
│    'user': [observer1, observer2],                          │
│    'theme': [observer3]                                     │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
         │
         │ store.set('theme', 'light')
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. Update _state['theme'] = 'light'                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Notify all observers of 'theme'                          │
│    for observer in _observers['theme']:                     │
│        observer.notify('theme', 'light')                    │
└─────────────────────────────────────────────────────────────┘
         ↓
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ View 1   │        │ View 2   │        │ View 3   │
    │ callback │        │ callback │        │ callback │
    └──────────┘        └──────────┘        └──────────┘
         │                   │                   │
         ↓                   ↓                   ↓
    Update UI           Update UI           Update UI
```

## View Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│                      View Lifecycle                        │
└────────────────────────────────────────────────────────────┘

View Created (once)
    ↓
┌──────────────┐
│ __init__()   │  - Setup UI components
└──────────────┘  - Subscribe to store
    ↓             - Create widgets

Navigation → View
    ↓
┌──────────────┐
│ on_enter()   │  - Load data
│              │  - Start async ops
│              │  - Update UI
│              │  - Start timers
└──────────────┘
    ↓
    ... View is active ...

Navigation → Away
    ↓
┌──────────────┐
│ on_leave()   │  - Cancel async ops
│              │  - Save state
│              │  - Cleanup timers
│              │  - Unsubscribe (optional)
└──────────────┘

Async Data Arrives
    ↓
┌───────────────────┐
│ on_data_received()│  - Update UI with data
│                   │  - Handle errors
│                   │  - Store in state
└───────────────────┘
```

## Thread Safety Model

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Thread (Tkinter)                  │
│  - All UI operations                                        │
│  - Event handling                                           │
│  - Widget updates                                           │
└─────────────────────────────────────────────────────────────┘
            ↑                                    ↓
            │ root.after(0, callback)            │ submit task
            │                                    │
┌─────────────────────────────────────────────────────────────┐
│                     ThreadPoolExecutor                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │Thread 1  │  │Thread 2  │  │Thread 3  │  ...              │
│  │ fetch()  │  │ compute()│  │ load()   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘

CRITICAL RULE: Background threads NEVER touch Tkinter widgets directly!
                All UI updates go through root.after() to main thread.
```

## Grid Overlay Navigation

```
┌────────────────────────────────────────────────────┐
│              Container Frame                       │
│  grid_rowconfigure(0, weight=1)                    │
│  grid_columnconfigure(0, weight=1)                 │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Single Grid Cell (0, 0)                     │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐            │  │
│  │  │ View A │ │ View B │ │ View C │            │  │
│  │  │ z=1    │ │ z=2    │ │ z=3    │ ← tkraise  │  │
│  │  └────────┘ └────────┘ └────────┘            │  │
│  │      ↑          ↑          ↑ (visible)       │  │
│  │      All overlapped, one raised              │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘

Each view:
  self.grid(row=0, column=0, sticky="nsew")

Navigation:
  view.tkraise()  # Brings view to front
```

## Package Structure

```
tkrouter/
├── __init__.py          ← Exports: Router, View, Store, AsyncBridge
├── base.py             ← Abstract View class
├── core.py             ← Router + Store implementation
└── async_bridge.py     ← AsyncBridge + CacheEntry

User imports:
    from tkrouter import Router, View

User creates:
    class MyView(View):
        def on_enter(self, params): ...
        def on_leave(self): ...
        def on_data_received(self, data): ...
```

## Key Design Patterns

1. **Router Pattern** - Centralized navigation management
2. **Observer Pattern** - Store notifications to views
3. **Lifecycle Pattern** - Predictable view lifecycle hooks
4. **Bridge Pattern** - Safe async operations
5. **Overlay Pattern** - Grid-based view stacking
6. **Cache Pattern** - TTL-based data caching

## Performance Characteristics

- **View Creation**: O(1) - cached after first creation
- **Navigation**: O(1) - just tkraise()
- **Store Get**: O(1) - dictionary lookup
- **Store Set**: O(n) - notify n observers
- **Cache Check**: O(1) - dictionary lookup
- **Async Operation**: Non-blocking - happens in background

## Memory Management

- Views are created once and cached
- Can call router.destroy_view(name) to free memory
- Cache entries expire based on TTL
- Store state persists until explicitly cleared
