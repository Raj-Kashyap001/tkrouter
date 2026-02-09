"""
Unit tests for Store class.
"""
import unittest
from tkrouter.core import Store


class TestStore(unittest.TestCase):
    """Test cases for Store class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.store = Store()
    
    def tearDown(self):
        """Clean up after tests."""
        self.store.clear()
    
    def test_store_initialization(self):
        """Test store initializes empty."""
        self.assertEqual(self.store.get_all(), {})
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        self.store.set('key1', 'value1')
        self.assertEqual(self.store.get('key1'), 'value1')
    
    def test_get_with_default(self):
        """Test getting non-existent key with default."""
        result = self.store.get('nonexistent', 'default')
        self.assertEqual(result, 'default')
    
    def test_get_without_default(self):
        """Test getting non-existent key without default."""
        result = self.store.get('nonexistent')
        self.assertIsNone(result)
    
    def test_update_multiple_values(self):
        """Test updating multiple values at once."""
        updates = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        self.store.update(updates)
        
        self.assertEqual(self.store.get('key1'), 'value1')
        self.assertEqual(self.store.get('key2'), 'value2')
        self.assertEqual(self.store.get('key3'), 'value3')
    
    def test_overwrite_existing_value(self):
        """Test overwriting existing value."""
        self.store.set('key', 'old_value')
        self.store.set('key', 'new_value')
        self.assertEqual(self.store.get('key'), 'new_value')
    
    def test_subscribe_and_notify(self):
        """Test subscribing to store changes."""
        callback_data = []
        
        def callback(key, value):
            callback_data.append((key, value))
        
        observer = self.store.subscribe('test_key', callback)
        self.store.set('test_key', 'test_value')
        
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], ('test_key', 'test_value'))
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same key."""
        callback1_data = []
        callback2_data = []
        
        def callback1(key, value):
            callback1_data.append((key, value))
        
        def callback2(key, value):
            callback2_data.append((key, value))
        
        self.store.subscribe('key', callback1)
        self.store.subscribe('key', callback2)
        self.store.set('key', 'value')
        
        self.assertEqual(len(callback1_data), 1)
        self.assertEqual(len(callback2_data), 1)
        self.assertEqual(callback1_data[0], ('key', 'value'))
        self.assertEqual(callback2_data[0], ('key', 'value'))
    
    def test_unsubscribe(self):
        """Test unsubscribing from store changes."""
        callback_data = []
        
        def callback(key, value):
            callback_data.append((key, value))
        
        observer = self.store.subscribe('key', callback)
        self.store.set('key', 'value1')
        
        self.store.unsubscribe('key', observer)
        self.store.set('key', 'value2')
        
        # Should only have been called once (before unsubscribe)
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0], ('key', 'value1'))
    
    def test_subscribe_different_keys(self):
        """Test subscribing to different keys."""
        callback1_data = []
        callback2_data = []
        
        def callback1(key, value):
            callback1_data.append((key, value))
        
        def callback2(key, value):
            callback2_data.append((key, value))
        
        self.store.subscribe('key1', callback1)
        self.store.subscribe('key2', callback2)
        
        self.store.set('key1', 'value1')
        self.store.set('key2', 'value2')
        
        self.assertEqual(len(callback1_data), 1)
        self.assertEqual(len(callback2_data), 1)
        self.assertEqual(callback1_data[0], ('key1', 'value1'))
        self.assertEqual(callback2_data[0], ('key2', 'value2'))
    
    def test_clear(self):
        """Test clearing all store state."""
        self.store.set('key1', 'value1')
        self.store.set('key2', 'value2')
        self.store.clear()
        
        self.assertEqual(self.store.get_all(), {})
    
    def test_get_all(self):
        """Test getting all state as dictionary."""
        self.store.set('key1', 'value1')
        self.store.set('key2', 'value2')
        
        all_state = self.store.get_all()
        self.assertEqual(all_state, {'key1': 'value1', 'key2': 'value2'})
    
    def test_get_all_returns_copy(self):
        """Test that get_all returns a copy, not reference."""
        self.store.set('key', 'value')
        all_state = self.store.get_all()
        all_state['new_key'] = 'new_value'
        
        # Original store should not be affected
        self.assertIsNone(self.store.get('new_key'))
    
    def test_complex_data_types(self):
        """Test storing complex data types."""
        test_data = {
            'dict': {'nested': 'value'},
            'list': [1, 2, 3],
            'tuple': (1, 2, 3),
            'int': 42,
            'float': 3.14,
            'bool': True,
            'none': None
        }
        
        for key, value in test_data.items():
            self.store.set(key, value)
        
        for key, value in test_data.items():
            self.assertEqual(self.store.get(key), value)
    
    def test_update_notifies_observers(self):
        """Test that update() triggers notifications."""
        callback_data = []
        
        def callback(key, value):
            callback_data.append((key, value))
        
        self.store.subscribe('key1', callback)
        self.store.subscribe('key2', callback)
        
        self.store.update({'key1': 'value1', 'key2': 'value2'})
        
        self.assertEqual(len(callback_data), 2)
        self.assertIn(('key1', 'value1'), callback_data)
        self.assertIn(('key2', 'value2'), callback_data)


if __name__ == '__main__':
    unittest.main()