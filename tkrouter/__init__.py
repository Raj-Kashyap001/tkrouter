"""
tkrouter - Modern asynchronous multi-page navigation for Tkinter.
"""
from tkrouter.core import Router, Store, RouterError, RouteNotFoundError
from tkrouter.base import View
from tkrouter.async_bridge import AsyncBridge

__all__ = [
    'Router',
    'Store',
    'View',
    'AsyncBridge',
    'RouterError',
    'RouteNotFoundError',
]

__version__ = '1.0.0'