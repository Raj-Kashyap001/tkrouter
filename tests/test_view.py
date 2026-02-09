"""
Unit tests for View base class.
"""
import unittest
import tkinter as tk
from tkrouter.base import View
from tkrouter.core import Router, Store


class ConcreteView(View):
    """Concrete implementation of View for testing."""
    
    def __init__(self, parent, router, store):
        super().__init__(parent, router, store)
        self.on_enter_called = False
        self.on_leave_called = False
        self.on_data_received_called = False
        self.received_params = None
        self.received_data = None
    
    def on_enter(self, params=None):
        self.on_enter_called = True
        self.received_params = params
    
    def on_leave(self):
        self.on_leave_called = True
    
    def on_data_received(self, data):
        self.on_data_received_called = True
        self.received_data = data


class TestView(unittest.TestCase):
    """Test cases for View base class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.router = Router(self.root)
        self.store = Store()
        
        # Create a frame to act as parent
        self.parent = tk.Frame(self.root)
        self.parent.grid(row=0, column=0)
    
    def tearDown(self):
        """Clean up after tests."""
        self.router.shutdown()
        self.root.destroy()
    
    def test_view_initialization(self):
        """Test view initializes correctly."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        self.assertIsNotNone(view)
        self.assertEqual(view.router, self.router)
        self.assertEqual(view.store, self.store)
        self.assertFalse(view.is_active())
    
    def test_view_is_frame(self):
        """Test view is a Tkinter Frame."""
        view = ConcreteView(self.parent, self.router, self.store)
        self.assertIsInstance(view, tk.Frame)
    
    def test_view_grid_configuration(self):
        """Test view is configured in grid."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        # Check grid info
        grid_info = view.grid_info()
        self.assertEqual(grid_info['row'], 0)
        self.assertEqual(grid_info['column'], 0)
        # Tkinter may return sticky in different order
        self.assertIn(grid_info['sticky'], ['nsew', 'nesw', 'nwse', 'senw', 'ensw', 'wsen'])
    
    def test_view_active_state(self):
        """Test view active state management."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        self.assertFalse(view.is_active())
        
        view._set_active(True)
        self.assertTrue(view.is_active())
        
        view._set_active(False)
        self.assertFalse(view.is_active())
    
    def test_on_enter_lifecycle(self):
        """Test on_enter lifecycle method."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        params = {'user_id': 123}
        view.on_enter(params)
        
        self.assertTrue(view.on_enter_called)
        self.assertEqual(view.received_params, params)
    
    def test_on_leave_lifecycle(self):
        """Test on_leave lifecycle method."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        view.on_leave()
        
        self.assertTrue(view.on_leave_called)
    
    def test_on_data_received_lifecycle(self):
        """Test on_data_received lifecycle method."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        test_data = {'test': 'data'}
        view.on_data_received(test_data)
        
        self.assertTrue(view.on_data_received_called)
        self.assertEqual(view.received_data, test_data)
    
    def test_view_has_router_reference(self):
        """Test view has reference to router."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        self.assertIs(view.router, self.router)
        
        # Test we can use router methods
        self.assertIsNotNone(view.router.store)
    
    def test_view_has_store_reference(self):
        """Test view has reference to store."""
        view = ConcreteView(self.parent, self.router, self.store)
        
        self.assertIs(view.store, self.store)
        
        # Test we can use store methods
        view.store.set('test', 'value')
        self.assertEqual(view.store.get('test'), 'value')
    
    def test_multiple_views_same_parent(self):
        """Test multiple views can share same parent."""
        view1 = ConcreteView(self.parent, self.router, self.store)
        view2 = ConcreteView(self.parent, self.router, self.store)
        
        # Both should be in same grid cell
        self.assertEqual(view1.grid_info()['row'], 0)
        self.assertEqual(view2.grid_info()['row'], 0)
        self.assertEqual(view1.grid_info()['column'], 0)
        self.assertEqual(view2.grid_info()['column'], 0)
    
    def test_view_tkraise(self):
        """Test view can be raised."""
        view1 = ConcreteView(self.parent, self.router, self.store)
        view2 = ConcreteView(self.parent, self.router, self.store)
        
        # Should not raise any errors
        view1.tkraise()
        view2.tkraise()
        view1.tkraise()
    
    def test_abstract_methods_must_be_implemented(self):
        """Test that abstract methods must be implemented."""
        # This should not raise an error because ConcreteView implements all methods
        view = ConcreteView(self.parent, self.router, self.store)
        self.assertIsNotNone(view)
        
        # Attempting to instantiate View directly should fail
        with self.assertRaises(TypeError):
            View(self.parent, self.router, self.store)


class TestViewIntegration(unittest.TestCase):
    """Integration tests for View with Router."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.router = Router(self.root)
    
    def tearDown(self):
        """Clean up after tests."""
        self.router.shutdown()
        self.root.destroy()
    
    def test_view_lifecycle_with_router(self):
        """Test view lifecycle when used with router."""
        self.router.register_route('test', ConcreteView)
        self.router.navigate('test', {'test_param': 'value'})
        
        # Get the view instance
        view = self.router._views['test']
        
        self.assertTrue(view.on_enter_called)
        self.assertEqual(view.received_params, {'test_param': 'value'})
        self.assertTrue(view.is_active())
    
    def test_view_on_leave_called_on_navigation(self):
        """Test on_leave is called when navigating away."""
        self.router.register_route('view1', ConcreteView)
        self.router.register_route('view2', ConcreteView)
        
        self.router.navigate('view1')
        view1 = self.router._views['view1']
        
        self.router.push('view2')
        
        self.assertTrue(view1.on_leave_called)
        self.assertFalse(view1.is_active())


if __name__ == '__main__':
    unittest.main()