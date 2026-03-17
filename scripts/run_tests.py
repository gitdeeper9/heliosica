#!/usr/bin/env python3
"""
Run HELIOSICA test suite
"""

import os
import sys
import unittest
import time
import argparse
from datetime import datetime


class TestRunner:
    """Run all tests or specific test modules"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.start_time = None
        self.end_time = None
        self.results = {}
    
    def discover_tests(self, pattern='test_*.py'):
        """Discover all tests"""
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
        return unittest.defaultTestLoader.discover(test_dir, pattern=pattern)
    
    def run_unit_tests(self):
        """Run unit tests only"""
        print("\n" + "=" * 60)
        print("Running Unit Tests")
        print("=" * 60)
        
        suite = unittest.defaultTestLoader.discover(
            os.path.join('tests', 'unit'),
            pattern='test_*.py'
        )
        
        return self._run_suite(suite, "unit")
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n" + "=" * 60)
        print("Running Integration Tests")
        print("=" * 60)
        
        suite = unittest.defaultTestLoader.discover(
            os.path.join('tests', 'integration'),
            pattern='test_*.py'
        )
        
        return self._run_suite(suite, "integration")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("Running All Tests")
        print("=" * 60)
        
        suite = self.discover_tests()
        return self._run_suite(suite, "all")
    
    def _run_suite(self, suite, name):
        """Run a test suite"""
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        
        start = time.time()
        result = runner.run(suite)
        elapsed = time.time() - start
        
        self.results[name] = {
            'tests': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'elapsed': elapsed,
            'success': result.wasSuccessful()
        }
        
        return result
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_time = 0
        
        for name, result in self.results.items():
            print(f"\n{name.upper()}:")
            print(f"  Tests run: {result['tests']}")
            print(f"  Failures: {result['failures']}")
            print(f"  Errors: {result['errors']}")
            print(f"  Skipped: {result['skipped']}")
            print(f"  Time: {result['elapsed']:.2f}s")
            print(f"  Status: {'✅ PASS' if result['success'] else '❌ FAIL'}")
            
            total_tests += result['tests']
            total_failures += result['failures']
            total_errors += result['errors']
            total_time += result['elapsed']
        
        print("\n" + "-" * 60)
        print(f"TOTAL:")
        print(f"  Tests run: {total_tests}")
        print(f"  Failures: {total_failures}")
        print(f"  Errors: {total_errors}")
        print(f"  Total time: {total_time:.2f}s")
        
        if total_failures == 0 and total_errors == 0:
            print("\n✅ ALL TESTS PASSED")
        else:
            print(f"\n❌ {total_failures + total_errors} TESTS FAILED")
    
    def run_single_test(self, test_name):
        """Run a single test by name"""
        print(f"\nRunning test: {test_name}")
        
        # Try to find the test
        if test_name.endswith('.py'):
            test_name = test_name[:-3]
        
        # Look in unit tests first
        module_path = f'tests.unit.{test_name}'
        try:
            suite = unittest.defaultTestLoader.loadTestsFromName(module_path)
            if suite.countTestCases() > 0:
                return self._run_suite(suite, test_name)
        except (ImportError, AttributeError):
            pass
        
        # Try integration tests
        module_path = f'tests.integration.{test_name}'
        try:
            suite = unittest.defaultTestLoader.loadTestsFromName(module_path)
            if suite.countTestCases() > 0:
                return self._run_suite(suite, test_name)
        except (ImportError, AttributeError):
            pass
        
        print(f"❌ Test '{test_name}' not found")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run HELIOSICA tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--test', type=str, help='Run specific test (e.g., test_dbm)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    if args.test:
        runner.run_single_test(args.test)
    elif args.unit:
        runner.run_unit_tests()
    elif args.integration:
        runner.run_integration_tests()
    else:  # default to all
        runner.run_all_tests()
    
    runner.print_summary()


if __name__ == '__main__':
    main()
