"""
Integration tests for tkrouter.
Tests the complete system working together.
"""
import unittest
import tkinter as tk
import time
from tkrouter import Router, View, Store


class HomeView(View):
    """Home view for integration testing."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self.enter_count = 0
        self.leave_count = 0
        self.data_count = 0
        self.last_params = None
        self.last_data = None
    
    def on_enter(self, params=None):
        self.enter_count += 1
        self.last_params = params
    
    def on_leave(self):
        self.leave_count += 1
    
    def on_data_received(self, data):
        self.data_count += 1
        self.last_data = data


class ProfileView(View):
    """Profile view for integration testing."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self.loaded_user_id = None
    
    def on_enter(self, params=None):
        if params:
            self.loaded_user_id = params.get('user_id')
    
    def on_leave(self):
        pass
    
    def on_data_received(self, data):
        pass


class SettingsView(View):
    """Settings view for integration testing."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self.theme_updates = []
        self.observer = None
    
    def on_enter(self, params=None):
        # Subscribe to theme changes
        self.observer = self.store.subscribe('theme', self._on_theme_change)
    
    def on_leave(self):
        # Unsubscribe
        if self.observer:
            self.store.unsubscribe('theme', self.observer)
    
    def on_data_received(self, data):
        pass
    
    def _on_theme_change(self, key, value):
        self.theme_updates.append(value)


class TestIntegration(unittest.TestCase):
    """Integration test cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.router = Router(self.root)
        
        # Register routes
        self.router.register_route('home', HomeView)
        self.router.register_route('profile', ProfileView)
        self.router.register_route('settings', SettingsView)
    
    def tearDown(self):
        """Clean up after tests."""
        self.router.shutdown()
        self.root.destroy()
    
    def test_basic_navigation_flow(self):
        """Test basic navigation between views."""
        # Navigate to home
        self.router.navigate('home')
        self.assertEqual(self.router.get_current_route(), 'home')
        
        # Push to profile
        self.router.push('profile')
        self.assertEqual(self.router.get_current_route(), 'profile')
        
        # Pop back to home
        self.router.pop()
        self.assertEqual(self.router.get_current_route(), 'home')
    
    def test_params_passing(self):
        """Test passing parameters through navigation."""
        self.router.navigate('home')
        self.router.push('profile', {'user_id': 123})
        
        profile_view = self.router._views['profile']
        self.assertEqual(profile_view.loaded_user_id, 123)
    
    def test_lifecycle_hooks_called(self):
        """Test lifecycle hooks are called correctly."""
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        self.assertEqual(home_view.enter_count, 1)
        self.assertEqual(home_view.leave_count, 0)
        
        self.router.push('profile')
        self.assertEqual(home_view.leave_count, 1)
        
        self.router.pop()
        self.assertEqual(home_view.enter_count, 2)
    
    def test_store_integration(self):
        """Test store integration with views."""
        # Set data in store
        self.router.store.set('user', {'name': 'John', 'id': 1})
        
        # Navigate to home
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        # View should have access to store
        user = home_view.store.get('user')
        self.assertEqual(user['name'], 'John')
    
    def test_store_observers(self):
        """Test store observers with views."""
        self.router.navigate('settings')
        settings_view = self.router._views['settings']
        
        # Change theme
        self.router.store.set('theme', 'dark')
        self.router.store.set('theme', 'light')
        
        # View should have received updates
        self.assertEqual(len(settings_view.theme_updates), 2)
        self.assertEqual(settings_view.theme_updates, ['dark', 'light'])
    
    def test_store_observer_cleanup(self):
        """Test store observers are cleaned up on leave."""
        self.router.navigate('settings')
        settings_view = self.router._views['settings']
        
        # Navigate away
        self.router.push('home')
        
        # Change theme
        self.router.store.set('theme', 'dark')
        
        # View should not receive update after leaving
        self.assertEqual(len(settings_view.theme_updates), 0)
    
    def test_async_operation_with_view(self):
        """Test async operations with views."""
        def fetch_data():
            time.sleep(0.1)
            return {'data': 'value'}
        
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        # Run async operation
        future = self.router.run_async(
            fetch_data,
            callback=home_view.on_data_received
        )
        
        # Wait for completion
        future.result(timeout=2)
        
        # Process events
        for _ in range(10):
            self.root.update_idletasks()
            self.root.update()
        
        self.assertEqual(home_view.data_count, 1)
        self.assertEqual(home_view.last_data, {'data': 'value'})
    
    def test_async_cached_operation(self):
        """Test cached async operations."""
        call_count = [0]
        
        def fetch_data():
            call_count[0] += 1
            time.sleep(0.1)
            return {'data': call_count[0]}
        
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        # First call - should fetch
        future1 = self.router.run_async_cached(
            cache_key='test_data',
            func=fetch_data,
            callback=home_view.on_data_received,
            ttl_seconds=60
        )
        if future1:
            future1.result(timeout=2)
        
        # Process events
        for _ in range(10):
            self.root.update_idletasks()
            self.root.update()
        
        # Second call - should use cache
        future2 = self.router.run_async_cached(
            cache_key='test_data',
            func=fetch_data,
            callback=home_view.on_data_received,
            ttl_seconds=60
        )
        if future2:
            future2.result(timeout=2)
        
        # Process events
        for _ in range(10):
            self.root.update_idletasks()
            self.root.update()
        
        # Function should only be called once
        self.assertEqual(call_count[0], 1)
        # But callback called twice
        self.assertEqual(home_view.data_count, 2)
    
    def test_view_state_persistence(self):
        """Test view state persists when navigating away and back."""
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        # Set some state
        initial_enter_count = home_view.enter_count
        
        # Navigate away and back
        self.router.push('profile')
        self.router.pop()
        
        # Should be same instance
        home_view_again = self.router._views['home']
        self.assertIs(home_view, home_view_again)
        
        # Enter count should have increased
        self.assertEqual(home_view.enter_count, initial_enter_count + 1)
    
    def test_complex_navigation_stack(self):
        """Test complex navigation scenarios."""
        # Build a stack
        self.router.navigate('home')
        self.router.push('profile', {'user_id': 1})
        self.router.push('settings')
        
        # Check stack
        stack = self.router.get_navigation_stack()
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack[0].route_name, 'home')
        self.assertEqual(stack[1].route_name, 'profile')
        self.assertEqual(stack[2].route_name, 'settings')
        
        # Pop twice
        self.router.pop()
        self.router.pop()
        
        # Should be back at home
        self.assertEqual(self.router.get_current_route(), 'home')
        self.assertEqual(len(self.router.get_navigation_stack()), 1)
    
    def test_navigate_clears_stack(self):
        """Test navigate clears existing stack."""
        # Build a stack
        self.router.push('home')
        self.router.push('profile')
        self.router.push('settings')
        
        self.assertEqual(len(self.router.get_navigation_stack()), 3)
        
        # Navigate to home
        self.router.navigate('home')
        
        # Stack should be cleared and only have home
        stack = self.router.get_navigation_stack()
        self.assertEqual(len(stack), 1)
        self.assertEqual(stack[0].route_name, 'home')
    
    def test_store_shared_across_views(self):
        """Test store is shared across all views."""
        # Set data before any views
        self.router.store.set('shared_data', 'value')
        
        # Navigate to home
        self.router.navigate('home')
        home_view = self.router._views['home']
        
        # Navigate to profile
        self.router.push('profile')
        profile_view = self.router._views['profile']
        
        # Both should see same store data
        self.assertEqual(home_view.store.get('shared_data'), 'value')
        self.assertEqual(profile_view.store.get('shared_data'), 'value')
        
        # Change from one view
        profile_view.store.set('shared_data', 'new_value')
        
        # Other view should see change
        self.assertEqual(home_view.store.get('shared_data'), 'new_value')
    
    def test_error_handling_in_async(self):
        """Test error handling in async operations."""
        errors = []
        
        def failing_func():
            raise ValueError("Test error")
        
        def error_callback(error):
            errors.append(error)
        
        self.router.navigate('home')
        
        future = self.router.run_async(
            failing_func,
            error_callback=error_callback
        )
        
        # Wait for error
        time.sleep(0.5)
        
        # Process events
        for _ in range(10):
            self.root.update_idletasks()
            self.root.update()
        
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ValueError)
    
    def test_multiple_params_navigation(self):
        """Test navigation with various parameter types."""
        params = {
            'user_id': 123,
            'action': 'edit',
            'filters': {'active': True, 'role': 'admin'},
            'tags': ['tag1', 'tag2']
        }
        
        self.router.navigate('home', params)
        home_view = self.router._views['home']
        
        self.assertEqual(home_view.last_params, params)
        self.assertEqual(home_view.last_params['user_id'], 123)
        self.assertEqual(home_view.last_params['filters']['role'], 'admin')
        self.assertEqual(home_view.last_params['tags'][0], 'tag1')


if __name__ == '__main__':
    unittest.main()