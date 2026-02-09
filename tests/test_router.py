"""
Unit tests for Router class.
"""
import unittest
import tkinter as tk
from tkrouter.core import Router, RouterError, RouteNotFoundError
from tkrouter.base import View


class TestView1(View):
    """Test view 1."""
    def on_enter(self, params=None): pass
    def on_leave(self): pass
    def on_data_received(self, data): pass


class TestView2(View):
    """Test view 2."""
    def on_enter(self, params=None): pass
    def on_leave(self): pass
    def on_data_received(self, data): pass


class TestView3(View):
    """Test view 3."""
    def on_enter(self, params=None): pass
    def on_leave(self): pass
    def on_data_received(self, data): pass


class TestRouter(unittest.TestCase):
    """Test cases for Router class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.router = Router(self.root)
    
    def tearDown(self):
        """Clean up after tests."""
        self.router.shutdown()
        self.root.destroy()
    
    def test_router_initialization(self):
        """Test router initializes correctly."""
        self.assertIsNotNone(self.router.container)
        self.assertIsNotNone(self.router.store)
        self.assertIsNotNone(self.router.async_bridge)
        self.assertEqual(len(self.router._routes), 0)
        self.assertEqual(len(self.router._views), 0)
        self.assertEqual(len(self.router._navigation_stack), 0)
    
    def test_register_route(self):
        """Test registering a route."""
        self.router.register_route('test', TestView1)
        
        self.assertIn('test', self.router._routes)
        self.assertEqual(self.router._routes['test'].view_class, TestView1)
    
    def test_register_route_with_params(self):
        """Test registering a route with default params."""
        default_params = {'key': 'value'}
        self.router.register_route('test', TestView1, params=default_params)
        
        self.assertEqual(self.router._routes['test'].params, default_params)
    
    def test_register_duplicate_route(self):
        """Test registering duplicate route raises error."""
        self.router.register_route('test', TestView1)
        
        with self.assertRaises(RouterError):
            self.router.register_route('test', TestView2)
    
    def test_navigate_to_route(self):
        """Test navigating to a route."""
        self.router.register_route('test', TestView1)
        self.router.navigate('test')
        
        self.assertEqual(self.router.get_current_route(), 'test')
        self.assertEqual(len(self.router._navigation_stack), 1)
    
    def test_navigate_to_nonexistent_route(self):
        """Test navigating to non-existent route raises error."""
        with self.assertRaises(RouteNotFoundError):
            self.router.navigate('nonexistent')
    
    def test_navigate_with_params(self):
        """Test navigating with parameters."""
        self.router.register_route('test', TestView1)
        params = {'user_id': 123}
        self.router.navigate('test', params)
        
        nav_entry = self.router._navigation_stack[-1]
        self.assertEqual(nav_entry.params, params)
    
    def test_navigate_clears_stack(self):
        """Test navigate clears existing navigation stack."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        
        self.router.push('test1')
        self.router.push('test2')
        self.assertEqual(len(self.router._navigation_stack), 2)
        
        self.router.navigate('test1')
        self.assertEqual(len(self.router._navigation_stack), 1)
    
    def test_push_route(self):
        """Test pushing a route onto stack."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        
        self.router.push('test1')
        self.router.push('test2')
        
        self.assertEqual(len(self.router._navigation_stack), 2)
        self.assertEqual(self.router.get_current_route(), 'test2')
    
    def test_push_nonexistent_route(self):
        """Test pushing non-existent route raises error."""
        with self.assertRaises(RouteNotFoundError):
            self.router.push('nonexistent')
    
    def test_pop_route(self):
        """Test popping a route from stack."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        
        self.router.push('test1')
        self.router.push('test2')
        
        result = self.router.pop()
        
        self.assertTrue(result)
        self.assertEqual(len(self.router._navigation_stack), 1)
        self.assertEqual(self.router.get_current_route(), 'test1')
    
    def test_pop_single_route(self):
        """Test popping when only one route in stack."""
        self.router.register_route('test', TestView1)
        self.router.navigate('test')
        
        result = self.router.pop()
        
        self.assertFalse(result)
        self.assertEqual(len(self.router._navigation_stack), 1)
    
    def test_can_pop(self):
        """Test can_pop method."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        
        self.router.push('test1')
        self.assertFalse(self.router.can_pop())
        
        self.router.push('test2')
        self.assertTrue(self.router.can_pop())
        
        self.router.pop()
        self.assertFalse(self.router.can_pop())
    
    def test_get_current_route(self):
        """Test getting current route name."""
        self.router.register_route('test', TestView1)
        self.router.navigate('test')
        
        self.assertEqual(self.router.get_current_route(), 'test')
    
    def test_get_current_route_empty_stack(self):
        """Test getting current route with empty stack."""
        self.assertIsNone(self.router.get_current_route())
    
    def test_get_navigation_stack(self):
        """Test getting navigation stack."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        self.router.register_route('test3', TestView3)
        
        self.router.push('test1')
        self.router.push('test2')
        self.router.push('test3')
        
        stack = self.router.get_navigation_stack()
        
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack[0].route_name, 'test1')
        self.assertEqual(stack[1].route_name, 'test2')
        self.assertEqual(stack[2].route_name, 'test3')
    
    def test_get_navigation_stack_returns_copy(self):
        """Test that get_navigation_stack returns a copy."""
        self.router.register_route('test', TestView1)
        self.router.navigate('test')
        
        stack = self.router.get_navigation_stack()
        stack.append('fake_entry')
        
        # Original stack should not be affected
        self.assertEqual(len(self.router._navigation_stack), 1)
    
    def test_view_caching(self):
        """Test that views are cached after creation."""
        self.router.register_route('test', TestView1)
        
        self.router.navigate('test')
        view1 = self.router._views['test']
        
        self.router.navigate('test')
        view2 = self.router._views['test']
        
        # Should be the same instance
        self.assertIs(view1, view2)
    
    def test_destroy_view(self):
        """Test destroying a view."""
        self.router.register_route('test', TestView1)
        self.router.navigate('test')
        
        self.assertIn('test', self.router._views)
        
        self.router.destroy_view('test')
        
        self.assertNotIn('test', self.router._views)
    
    def test_view_lifecycle_on_navigate(self):
        """Test view lifecycle methods are called on navigate."""
        class LifecycleView(View):
            enter_called = False
            leave_called = False
            
            def on_enter(self, params=None):
                LifecycleView.enter_called = True
            
            def on_leave(self):
                LifecycleView.leave_called = True
            
            def on_data_received(self, data):
                pass
        
        self.router.register_route('test', LifecycleView)
        self.router.navigate('test')
        
        self.assertTrue(LifecycleView.enter_called)
    
    def test_view_lifecycle_on_push(self):
        """Test view lifecycle on push."""
        class LifecycleView1(View):
            leave_called = False
            
            def on_enter(self, params=None): pass
            def on_leave(self):
                LifecycleView1.leave_called = True
            def on_data_received(self, data): pass
        
        class LifecycleView2(View):
            enter_called = False
            
            def on_enter(self, params=None):
                LifecycleView2.enter_called = True
            def on_leave(self): pass
            def on_data_received(self, data): pass
        
        self.router.register_route('view1', LifecycleView1)
        self.router.register_route('view2', LifecycleView2)
        
        self.router.navigate('view1')
        self.router.push('view2')
        
        self.assertTrue(LifecycleView1.leave_called)
        self.assertTrue(LifecycleView2.enter_called)
    
    def test_view_active_state(self):
        """Test view active state tracking."""
        self.router.register_route('test1', TestView1)
        self.router.register_route('test2', TestView2)
        
        self.router.push('test1')
        view1 = self.router._views['test1']
        self.assertTrue(view1.is_active())
        
        self.router.push('test2')
        view2 = self.router._views['test2']
        self.assertFalse(view1.is_active())
        self.assertTrue(view2.is_active())
        
        self.router.pop()
        self.assertTrue(view1.is_active())
        self.assertFalse(view2.is_active())
    
    def test_container_grid_configuration(self):
        """Test container is configured for grid layout."""
        grid_info = self.router.container.grid_info()
        
        self.assertEqual(grid_info['row'], 0)
        self.assertEqual(grid_info['column'], 0)
        # Tkinter may return sticky in different order
        self.assertIn(grid_info['sticky'], ['nsew', 'nesw', 'nwse', 'senw', 'ensw', 'wsen'])
    
    def test_store_accessible(self):
        """Test store is accessible through router."""
        self.router.store.set('test', 'value')
        self.assertEqual(self.router.store.get('test'), 'value')
    
    def test_async_bridge_accessible(self):
        """Test async bridge is accessible through router."""
        def test_func():
            return 42
        
        future = self.router.run_async(test_func)
        result = future.result(timeout=2)
        
        self.assertEqual(result, 42)
    
    def test_multiple_route_registrations(self):
        """Test registering multiple routes."""
        self.router.register_route('route1', TestView1)
        self.router.register_route('route2', TestView2)
        self.router.register_route('route3', TestView3)
        
        self.assertEqual(len(self.router._routes), 3)
    
    def test_navigation_stack_order(self):
        """Test navigation stack maintains correct order."""
        self.router.register_route('route1', TestView1)
        self.router.register_route('route2', TestView2)
        self.router.register_route('route3', TestView3)
        
        self.router.push('route1')
        self.router.push('route2')
        self.router.push('route3')
        
        stack = self.router.get_navigation_stack()
        route_names = [entry.route_name for entry in stack]
        
        self.assertEqual(route_names, ['route1', 'route2', 'route3'])


if __name__ == '__main__':
    unittest.main()