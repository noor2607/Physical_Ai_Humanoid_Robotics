#!/usr/bin/env python3
"""
Test runner for all modules in the Physical AI & Humanoid Robotics course
"""

import unittest
import sys
import os

# Add the test directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import individual test modules
from test_voice_to_action import suite as voice_to_action_suite
from test_llm_integration import suite as llm_integration_suite
from test_cognitive_planning import suite as cognitive_planning_suite


def create_test_suite():
    """Create a comprehensive test suite combining all module tests."""
    # Create a master test suite
    master_suite = unittest.TestSuite()

    # Add individual module test suites
    master_suite.addTest(voice_to_action_suite())
    master_suite.addTest(llm_integration_suite())
    master_suite.addTest(cognitive_planning_suite())

    return master_suite


def run_tests():
    """Run all tests and return the result."""
    # Create the master test suite
    suite = create_test_suite()

    # Create a test runner
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True  # Capture stdout/stderr during tests
    )

    # Run the tests
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*50)
    print("TEST RUN SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "0%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    return result


def run_specific_module(module_name):
    """Run tests for a specific module."""
    if module_name == "voice_to_action":
        suite = voice_to_action_suite()
    elif module_name == "llm_integration":
        suite = llm_integration_suite()
    elif module_name == "cognitive_planning":
        suite = cognitive_planning_suite()
    else:
        print(f"Unknown module: {module_name}")
        print("Available modules: voice_to_action, llm_integration, cognitive_planning")
        return None

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    print("Physical AI & Humanoid Robotics - Comprehensive Test Suite")
    print("="*60)

    if len(sys.argv) > 1:
        # Run specific module tests
        module_name = sys.argv[1]
        print(f"Running tests for module: {module_name}")
        result = run_specific_module(module_name)
    else:
        # Run all tests
        print("Running all tests...")
        result = run_tests()

    # Exit with appropriate code
    if result and (result.failures or result.errors):
        sys.exit(1)
    else:
        print("\nAll tests passed! ✓")
        sys.exit(0)