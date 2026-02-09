"""
Thread-safe async bridge for Tkinter with caching support.
"""
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import tkinter as tk
import queue


@dataclass
class CacheEntry:
    """Represents a cached data entry with timestamp."""
    data: Any
    timestamp: datetime
    ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        return datetime.now() - self.timestamp < self.ttl


class AsyncBridge:
    """
    Thread-safe bridge for running async operations without blocking Tkinter's main loop.
    
    Uses ThreadPoolExecutor for background tasks and a queue-based polling system
    to ensure all UI updates happen on the main thread.
    """
    
    def __init__(self, root: tk.Tk, max_workers: int = 5):
        """
        Initialize the async bridge.
        
        Args:
            root: The root Tkinter window
            max_workers: Maximum number of concurrent background threads
        """
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_lock = threading.Lock()
        self._pending_futures: Dict[str, Future] = {}
        self._callback_queue = queue.Queue()
        self._poll_id = None
        self._start_polling()
        
    def _start_polling(self) -> None:
        """Start polling the callback queue."""
        self._poll_id = self.root.after(10, self._poll_for_callbacks)
        
    def _poll_for_callbacks(self) -> None:
        """Poll the queue for callbacks to execute on the main thread."""
        try:
            # Process as many callbacks as possible in one go
            while True:
                try:
                    callback_func = self._callback_queue.get_nowait()
                    callback_func()
                except queue.Empty:
                    break
        except Exception as e:
            print(f"Error in async callback: {e}")
        finally:
            # Always reschedule unless we're shutting down
            try:
                self._poll_id = self.root.after(10, self._poll_for_callbacks)
            except (tk.TclError, RuntimeError):
                self._poll_id = None
        
    def run_async(
        self,
        func: Callable,
        *args,
        callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ) -> Future:
        """
        Run a function in a background thread and execute callback on main thread.
        
        Args:
            func: The function to run in background
            *args: Positional arguments for func
            callback: Function to call with result on main thread
            error_callback: Function to call if an error occurs
            **kwargs: Keyword arguments for func
            
        Returns:
            Future object representing the async operation
        """
        future = self.executor.submit(func, *args, **kwargs)
        
        def done_callback(fut: Future) -> None:
            try:
                result = fut.result()
                if callback:
                    # Put callback on queue for main thread execution
                    self._callback_queue.put(lambda r=result: callback(r))
            except Exception as e:
                if error_callback:
                    self._callback_queue.put(lambda err=e: error_callback(err))
                else:
                    print(f"Async error: {e}")
        
        future.add_done_callback(done_callback)
        return future
    
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
    ) -> Optional[Future]:
        """
        Run an async operation with caching support.
        
        Args:
            cache_key: Unique key for caching the result
            func: The function to run in background
            *args: Positional arguments for func
            callback: Function to call with result on main thread
            error_callback: Function to call if an error occurs
            ttl_seconds: Time-to-live for cache in seconds
            revalidate: If True, return cached data immediately but fetch fresh data in background
            **kwargs: Keyword arguments for func
            
        Returns:
            Future object if async operation started, None if using cached data
        """
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            
            # Check if we have valid cached data
            if cached and cached.is_valid():
                if callback:
                    # Return cached data immediately via queue for consistency
                    data = cached.data
                    self._callback_queue.put(lambda d=data: callback(d))
                
                # If revalidate is True, fetch fresh data in background
                if not revalidate:
                    return None
        
        # Define wrapper to cache the result
        def cache_wrapper(*a, **kw):
            result = func(*a, **kw)
            with self._cache_lock:
                self._cache[cache_key] = CacheEntry(
                    data=result,
                    timestamp=datetime.now(),
                    ttl=timedelta(seconds=ttl_seconds)
                )
            return result
        
        # Run async with caching
        future = self.run_async(
            cache_wrapper,
            *args,
            callback=callback,
            error_callback=error_callback,
            **kwargs
        )
        
        with self._cache_lock:
            self._pending_futures[cache_key] = future
        
        return future
    
    def invalidate_cache(self, cache_key: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            cache_key: Specific key to invalidate, or None to clear all cache
        """
        with self._cache_lock:
            if cache_key:
                self._cache.pop(cache_key, None)
            else:
                self._cache.clear()
    
    def get_cached(self, cache_key: str) -> Optional[Any]:
        """
        Get cached data if available and valid.
        
        Args:
            cache_key: The cache key to retrieve
            
        Returns:
            Cached data or None if not found or expired
        """
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and cached.is_valid():
                return cached.data
        return None
    
    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        if self._poll_id:
            try:
                self.root.after_cancel(self._poll_id)
            except (tk.TclError, RuntimeError):
                pass
            self._poll_id = None
        self.executor.shutdown(wait=True)