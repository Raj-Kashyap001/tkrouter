"""
Demo application showcasing tkrouter features:
- Multi-page navigation
- Async data loading with caching
- Global state management
- Lifecycle hooks
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
import time
from tkrouter import Router, View


# Simulated async data fetching functions
def fetch_user_data(user_id: int) -> Dict[str, Any]:
    """Simulate API call to fetch user data."""
    time.sleep(1)  # Simulate network delay
    return {
        'id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com',
        'posts': user_id * 10
    }


def fetch_posts_data() -> list:
    """Simulate API call to fetch posts."""
    time.sleep(1.5)  # Simulate network delay
    return [
        {'id': i, 'title': f'Post {i}', 'content': f'Content for post {i}'}
        for i in range(1, 6)
    ]


class HomeView(View):
    """Home page with navigation options."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self._setup_ui()
    
    def _setup_ui(self):
        ttk.Label(self, text="Home Page", font=('Arial', 24, 'bold')).pack(pady=20)
        ttk.Label(self, text="Welcome to tkrouter demo").pack(pady=10)
        
        ttk.Button(self, text="View Profile", command=self._go_profile).pack(pady=5)
        ttk.Button(self, text="View Posts", command=self._go_posts).pack(pady=5)
        ttk.Button(self, text="Settings", command=self._go_settings).pack(pady=5)
        
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=20)
    
    def _go_profile(self):
        self.router.push('profile', {'user_id': 1})
    
    def _go_posts(self):
        self.router.push('posts')
    
    def _go_settings(self):
        self.router.push('settings')
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        auth = self.store.get('authenticated', False)
        user = self.store.get('current_user')
        if auth and user:
            self.status_label.config(text=f"Logged in as: {user.get('name', 'Unknown')}")
        else:
            self.status_label.config(text="Not logged in")
    
    def on_leave(self):
        pass
    
    def on_data_received(self, data: Any):
        pass


class ProfileView(View):
    """Profile page with async data loading and caching."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self._setup_ui()
    
    def _setup_ui(self):
        ttk.Button(self, text="← Back", command=self.router.pop).pack(anchor='nw', padx=10, pady=10)
        
        ttk.Label(self, text="Profile", font=('Arial', 20, 'bold')).pack(pady=20)
        
        self.loading_label = ttk.Label(self, text="Loading...", font=('Arial', 12))
        self.loading_label.pack(pady=10)
        
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        ttk.Button(self, text="Refresh (Revalidate Cache)", 
                  command=self._refresh_data).pack(pady=10)
    
    def _refresh_data(self):
        """Force refresh data with cache revalidation."""
        params = {'user_id': self.current_user_id}
        self.on_enter(params)
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        self.current_user_id = params.get('user_id', 1) if params else 1
        self.loading_label.pack()
        self.loading_label.config(text="Loading profile...")
        
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Fetch user data with caching (5 min TTL)
        self.router.run_async_cached(
            cache_key=f'user_{self.current_user_id}',
            func=fetch_user_data,
            user_id=self.current_user_id,
            callback=self.on_data_received,
            ttl_seconds=300,
            revalidate=True  # Return cached immediately, fetch fresh in background
        )
    
    def on_leave(self):
        pass
    
    def on_data_received(self, data: Any):
        self.loading_label.pack_forget()
        
        # Update store with current user
        self.store.set('current_user', data)
        self.store.set('authenticated', True)
        
        # Display user data
        ttk.Label(self.content_frame, text=f"Name: {data['name']}", 
                 font=('Arial', 14)).pack(anchor='w', pady=5)
        ttk.Label(self.content_frame, text=f"Email: {data['email']}", 
                 font=('Arial', 12)).pack(anchor='w', pady=5)
        ttk.Label(self.content_frame, text=f"Total Posts: {data['posts']}", 
                 font=('Arial', 12)).pack(anchor='w', pady=5)


class PostsView(View):
    """Posts list with async loading."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self._setup_ui()
    
    def _setup_ui(self):
        ttk.Button(self, text="← Back", command=self.router.pop).pack(anchor='nw', padx=10, pady=10)
        
        ttk.Label(self, text="Posts", font=('Arial', 20, 'bold')).pack(pady=20)
        
        self.loading_label = ttk.Label(self, text="Loading posts...")
        self.loading_label.pack(pady=10)
        
        # Scrollable frame for posts
        self.canvas = tk.Canvas(self, height=400)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        self.loading_label.pack()
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Fetch posts with caching
        self.router.run_async_cached(
            cache_key='posts_list',
            func=fetch_posts_data,
            callback=self.on_data_received,
            ttl_seconds=180
        )
    
    def on_leave(self):
        pass
    
    def on_data_received(self, data: Any):
        self.loading_label.pack_forget()
        
        for post in data:
            frame = ttk.Frame(self.scrollable_frame, relief='solid', borderwidth=1)
            frame.pack(fill='x', pady=5, padx=5)
            
            ttk.Label(frame, text=post['title'], font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=5)
            ttk.Label(frame, text=post['content']).pack(anchor='w', padx=10, pady=5)


class SettingsView(View):
    """Settings page demonstrating store integration."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self._setup_ui()
        self._subscribe_to_store()
    
    def _setup_ui(self):
        ttk.Button(self, text="← Back", command=self.router.pop).pack(anchor='nw', padx=10, pady=10)
        
        ttk.Label(self, text="Settings", font=('Arial', 20, 'bold')).pack(pady=20)
        
        # Theme setting
        ttk.Label(self, text="Theme:").pack(pady=10)
        self.theme_var = tk.StringVar(value=self.store.get('theme', 'light'))
        ttk.Radiobutton(self, text="Light", variable=self.theme_var, 
                       value='light', command=self._update_theme).pack()
        ttk.Radiobutton(self, text="Dark", variable=self.theme_var, 
                       value='dark', command=self._update_theme).pack()
        
        # User info display
        self.user_info = ttk.Label(self, text="", font=('Arial', 12))
        self.user_info.pack(pady=20)
        
        # Logout button
        ttk.Button(self, text="Logout", command=self._logout).pack(pady=10)
    
    def _subscribe_to_store(self):
        """Subscribe to store changes."""
        self.store.subscribe('current_user', self._on_user_change)
    
    def _on_user_change(self, key: str, value: Any):
        """Called when current_user changes in store."""
        if value:
            self.user_info.config(text=f"Current user: {value.get('name', 'Unknown')}")
        else:
            self.user_info.config(text="No user logged in")
    
    def _update_theme(self):
        theme = self.theme_var.get()
        self.store.set('theme', theme)
    
    def _logout(self):
        self.store.set('authenticated', False)
        self.store.set('current_user', None)
        self.router.navigate('home')
    
    def on_enter(self, params: Optional[Dict[str, Any]] = None):
        user = self.store.get('current_user')
        if user:
            self.user_info.config(text=f"Current user: {user.get('name', 'Unknown')}")
        else:
            self.user_info.config(text="No user logged in")
    
    def on_leave(self):
        pass
    
    def on_data_received(self, data: Any):
        pass


def main():
    """Main application entry point."""
    root = tk.Tk()
    root.title("tkrouter Demo")
    root.geometry("600x500")
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create router
    router = Router(root)
    
    # Register routes
    router.register_route('home', HomeView)
    router.register_route('profile', ProfileView)
    router.register_route('posts', PostsView)
    router.register_route('settings', SettingsView)
    
    # Navigate to home
    router.navigate('home')
    
    # Handle cleanup on close
    def on_closing():
        router.shutdown()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()


if __name__ == '__main__':
    main()