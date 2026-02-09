"""
Base abstract class for tkrouter views with lifecycle hooks.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import tkinter as tk


class View(ABC, tk.Frame):
    """
    Abstract base class for all views in the router.
    
    All views must inherit from this class and implement required lifecycle methods.
    Views are grid-managed at (0, 0) and use tkraise() for visibility.
    """
    
    def __init__(self, parent: tk.Widget, router: Any, store: Any):
        """
        Initialize the view.
        
        Args:
            parent: The parent Tkinter widget (usually the router container)
            router: Reference to the Router instance for navigation
            store: Reference to the global Store for state management
        """
        super().__init__(parent)
        self.router = router
        self.store = store
        self.grid(row=0, column=0, sticky="nsew")
        self._is_active = False
        
    @abstractmethod
    def on_enter(self, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Called when the view becomes active.
        
        Args:
            params: Optional parameters passed during navigation
        """
        pass
    
    @abstractmethod
    def on_leave(self) -> None:
        """
        Called when the view is being left (before navigating away).
        Use for cleanup, saving state, or canceling operations.
        """
        pass
    
    @abstractmethod
    def on_data_received(self, data: Any) -> None:
        """
        Called when async data is received from background operations.
        
        Args:
            data: The data received from the async operation
        """
        pass
    
    def is_active(self) -> bool:
        """Check if this view is currently active."""
        return self._is_active
    
    def _set_active(self, active: bool) -> None:
        """Internal method to set active state."""
        self._is_active = active