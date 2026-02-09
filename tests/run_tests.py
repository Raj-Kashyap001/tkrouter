#!/usr/bin/env python3
"""
Test runner for tkrouter.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py test_store   # Run specific test module
"""
import sys
import unittest
import os

# Add parent directory to path so we can import tkrouter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests(verbosity=1):
    """Run all tests in the tests directory."""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_name, verbosity=1):
    """Run a specific test module."""
    loader = unittest.TestLoader()
    
    # Try to load the test module
    try:
        suite = loader.loadTestsFromName(test_name)
    except Exception as e:
        print(f"Error loading test '{test_name}': {e}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def print_usage():
    """Print usage information."""
    print(__doc__)


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    # Check for help
    if '-h' in args or '--help' in args:
        print_usage()
        return 0
    
    # Check for verbose flag
    verbosity = 2 if '-v' in args or '--verbose' in args else 1
    args = [arg for arg in args if arg not in ['-v', '--verbose']]
    
    # Run tests
    if not args:
        # Run all tests
        print("Running all tests...\n")
        success = run_all_tests(verbosity=verbosity)
    else:
        # Run specific test
        test_name = args[0]
        print(f"Running test: {test_name}\n")
        success = run_specific_test(test_name, verbosity=verbosity)
    
    # Return exit code
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())