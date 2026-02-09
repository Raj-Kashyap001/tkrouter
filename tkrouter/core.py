"""
Core routing logic, view management, and global state store.
"""
from typing import Dict, Type, Optional, Any, Callable, List
from dataclasses import dataclass, field
import tkinter as tk
from tkrouter.base import View
from tkrouter.async_bridge import AsyncBridge


@dataclass
class RouteConfig:
    """Configuration for a route."""
    name: str
    view_class: Type[View]
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationEntry:
    """Represents an entry in the navigation stack."""
    route_name: str
    params: Dict[str, Any] = field(default_factory=dict)


class StoreObserver:
    """Observer interface for store subscribers."""
    
    def __init__(self, callback: Callable[[str, Any], None]):
        """
        Initialize observer with callback.
        
        Args:
            callback: Function to call when store updates (key, value)
        """
        self.callback = callback
    
    def notify(self, key: str, value: Any) -> None:
        """Notify observer of store change."""
        self.callback(key, value)


class Store:
    """
    Global state store with observer pattern for reactive updates.
    
    Views can subscribe to store changes and receive notifications
    when state is updated.
    """
    
    def __init__(self):
        """Initialize the store."""
        self._state: Dict[str, Any] = {}
        self._observers: Dict[str, List[StoreObserver]] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the store.
        
        Args:
            key: The state key
            default: Default value if key not found
            
        Returns:
            The stored value or default
        """
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the store and notify observers.
        
        Args:
            key: The state key
            value: The value to store
        """
        self._state[key] = value
        self._notify(key, value)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple values at once.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        for key, value in updates.items():
            self.set(key, value)
    
    def subscribe(self, key: str, callback: Callable[[str, Any], None]) -> StoreObserver:
        """
        Subscribe to changes on a specific key.
        
        Args:
            key: The state key to watch
            callback: Function to call when key changes
            
        Returns:
            Observer object for unsubscribing
        """
        observer = StoreObserver(callback)
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(observer)
        return observer
    
    def unsubscribe(self, key: str, observer: StoreObserver) -> None:
        """
        Unsubscribe an observer from a key.
        
        Args:
            key: The state key
            observer: The observer to remove
        """
        if key in self._observers:
            self._observers[key] = [obs for obs in self._observers[key] if obs != observer]
    
    def _notify(self, key: str, value: Any) -> None:
        """Notify all observers of a key change."""
        if key in self._observers:
            for observer in self._observers[key]:
                observer.notify(key, value)
    
    def clear(self) -> None:
        """Clear all state."""
        self._state.clear()
        
    def get_all(self) -> Dict[str, Any]:
        """Get all state as dictionary."""
        return self._state.copy()


class RouterError(Exception):
    """Base exception for router errors."""
    pass


class RouteNotFoundError(RouterError):
    """Raised when a route is not found."""
    pass


class Router:
    """
    Main router class for managing navigation and views.
    
    Handles route registration, navigation stack, view lifecycle,
    and coordinates with the async bridge for background operations.
    """
    
    def __init__(self, root: tk.Tk, container: Optional[tk.Frame] = None):
        """
        Initialize the router.
        
        Args:
            root: The root Tkinter window
            container: Optional container frame for views (created if not provided)
        """
        self.root = root
        self.container = container or tk.Frame(root)
        self.container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weight for proper resizing
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Initialize components
        self.async_bridge = AsyncBridge(root)
        self.store = Store()
        
        # Route management
        self._routes: Dict[str, RouteConfig] = {}
        self._views: Dict[str, View] = {}
        self._navigation_stack: List[NavigationEntry] = []
        self._current_view: Optional[View] = None
    
    def register_route(
        self,
        name: str,
        view_class: Type[View],
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a route with a view class.
        
        Args:
            name: Unique route name
            view_class: The View class to instantiate for this route
            params: Optional default parameters for the route
        """
        if name in self._routes:
            raise RouterError(f"Route '{name}' is already registered")
        
        self._routes[name] = RouteConfig(
            name=name,
            view_class=view_class,
            params=params or {}
        )
    
    def navigate(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Navigate to a route, replacing current navigation stack.
        
        Args:
            route_name: Name of the route to navigate to
            params: Optional parameters to pass to the view
        """
        if route_name not in self._routes:
            raise RouteNotFoundError(f"Route '{route_name}' not found")
        
        # Clear navigation stack and navigate
        self._navigation_stack.clear()
        self.push(route_name, params)
    
    def push(self, route_name: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Push a new route onto the navigation stack.
        
        Args:
            route_name: Name of the route to navigate to
            params: Optional parameters to pass to the view
        """
        if route_name not in self._routes:
            raise RouteNotFoundError(f"Route '{route_name}' not found")
        
        # Call on_leave on current view
        if self._current_view:
            self._current_view.on_leave()
            self._current_view._set_active(False)
        
        # Add to navigation stack
        nav_entry = NavigationEntry(route_name=route_name, params=params or {})
        self._navigation_stack.append(nav_entry)
        
        # Get or create view
        view = self._get_or_create_view(route_name)
        
        # Set as current and raise to top
        self._current_view = view
        view._set_active(True)
        view.tkraise()
        
        # Call on_enter with params
        view.on_enter(nav_entry.params)
    
    def pop(self) -> bool:
        """
        Pop the current route from the navigation stack and go back.
        
        Returns:
            True if navigation successful, False if stack is empty
        """
        if len(self._navigation_stack) <= 1:
            return False
        
        # Call on_leave on current view
        if self._current_view:
            self._current_view.on_leave()
            self._current_view._set_active(False)
        
        # Remove current from stack
        self._navigation_stack.pop()
        
        # Get previous entry
        prev_entry = self._navigation_stack[-1]
        view = self._get_or_create_view(prev_entry.route_name)
        
        # Set as current and raise to top
        self._current_view = view
        view._set_active(True)
        view.tkraise()
        
        # Call on_enter with params
        view.on_enter(prev_entry.params)
        
        return True
    
    def can_pop(self) -> bool:
        """Check if there are routes to pop."""
        return len(self._navigation_stack) > 1
    
    def get_current_route(self) -> Optional[str]:
        """Get the name of the current route."""
        if self._navigation_stack:
            return self._navigation_stack[-1].route_name
        return None
    
    def get_navigation_stack(self) -> List[NavigationEntry]:
        """Get a copy of the current navigation stack."""
        return self._navigation_stack.copy()
    
    def _get_or_create_view(self, route_name: str) -> View:
        """
        Get existing view instance or create new one.
        
        Args:
            route_name: Name of the route
            
        Returns:
            View instance
        """
        if route_name not in self._views:
            route_config = self._routes[route_name]
            view = route_config.view_class(
                parent=self.container,
                router=self,
                store=self.store
            )
            self._views[route_name] = view
        
        return self._views[route_name]
    
    def destroy_view(self, route_name: str) -> None:
        """
        Destroy a view instance (useful for refreshing a view).
        
        Args:
            route_name: Name of the route whose view to destroy
        """
        if route_name in self._views:
            self._views[route_name].destroy()
            del self._views[route_name]
    
    def run_async(
        self,
        func: Callable,
        *args,
        callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ) -> Any:
        """
        Run an async operation via the async bridge.
        
        Args:
            func: Function to run in background
            *args: Positional arguments
            callback: Callback for result
            error_callback: Callback for errors
            **kwargs: Keyword arguments
            
        Returns:
            Future object
        """
        return self.async_bridge.run_async(
            func, *args,
            callback=callback,
            error_callback=error_callback,
            **kwargs
        )
    
    def run_async_cached(
        self,
        cache_key: str,
        func: Callable,
        *args,
        callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        ttl_seconds: int = 300,
        revalidate: bool = False,
        **kwargs
    ) -> Optional[Any]:
        """
        Run an async operation with caching via the async bridge.
        
        Args:
            cache_key: Unique cache key
            func: Function to run in background
            *args: Positional arguments
            callback: Callback for result
            error_callback: Callback for errors
            ttl_seconds: Cache time-to-live
            revalidate: Whether to revalidate cache
            **kwargs: Keyword arguments
            
        Returns:
            Future object or None if using cached data
        """
        return self.async_bridge.run_async_cached(
            cache_key, func, *args,
            callback=callback,
            error_callback=error_callback,
            ttl_seconds=ttl_seconds,
            revalidate=revalidate,
            **kwargs
        )
    
    def shutdown(self) -> None:
        """Shutdown the router and cleanup resources."""
        self.async_bridge.shutdown()
        for view in self._views.values():
            view.destroy()
        self._views.clear()