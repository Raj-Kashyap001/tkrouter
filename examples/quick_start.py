"""
Quick start example for tkrouter.
Demonstrates basic navigation between two views.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
from tkrouter import Router, View


class HomeView(View):
    """Simple home page."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        
        # Title
        ttk.Label(
            self, 
            text="Home Page", 
            font=('Arial', 24, 'bold')
        ).pack(pady=40)
        
        # Navigation button
        ttk.Button(
            self, 
            text="Go to About Page", 
            command=lambda: router.push('about')
        ).pack(pady=10)
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        print("Entered Home")
    
    def on_leave(self):
        print("Left Home")
    
    def on_data_received(self, data: Any):
        pass


class AboutView(View):
    """Simple about page."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        
        # Back button
        ttk.Button(
            self, 
            text="← Back", 
            command=router.pop
        ).pack(anchor='nw', padx=10, pady=10)
        
        # Title
        ttk.Label(
            self, 
            text="About Page", 
            font=('Arial', 24, 'bold')
        ).pack(pady=40)
        
        # Content
        ttk.Label(
            self, 
            text="This is a simple tkrouter demo.\nPress Back to return to Home."
        ).pack(pady=10)
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        print("Entered About")
    
    def on_leave(self):
        print("Left About")
    
    def on_data_received(self, data: Any):
        pass


def main():
    """Main application entry point."""
    # Create root window
    root = tk.Tk()
    root.title("tkrouter Quick Start")
    root.geometry("500x300")
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create router
    router = Router(root)
    
    # Register routes
    router.register_route('home', HomeView)
    router.register_route('about', AboutView)
    
    # Navigate to home
    router.navigate('home')
    
    # Handle cleanup on close
    def on_closing():
        router.shutdown()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the app
    root.mainloop()


if __name__ == '__main__':
    main()