#!/usr/bin/env python3
"""
Unit tests for the cognitive_planning.py module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from dataclasses import asdict

# Add the voice_control module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'my_robot_examples', 'voice_control'))

from cognitive_planning import (
    Action,
    Task,
    WorldState,
    HTNPlanner,
    CognitivePlanner,
    IsaacSimActionExecutor
)


class TestAction(unittest.TestCase):
    """Test cases for Action dataclass"""

    def test_action_creation(self):
        """Test creating Action with various attributes."""
        action = Action(
            name="navigate",
            parameters={"target_location": "kitchen"},
            preconditions=["robot_at(start_location)"],
            effects=["robot_at(target_location)"]
        )

        self.assertEqual(action.name, "navigate")
        self.assertEqual(action.parameters["target_location"], "kitchen")
        self.assertIn("robot_at(start_location)", action.preconditions)
        self.assertIn("robot_at(target_location)", action.effects)


class TestTask(unittest.TestCase):
    """Test cases for Task dataclass"""

    def test_task_creation(self):
        """Test creating Task with various attributes."""
        action1 = Action(name="navigate", parameters={"target": "kitchen"}, preconditions=[], effects=[])
        action2 = Action(name="grasp", parameters={"object": "cup"}, preconditions=[], effects=[])

        task = Task(
            name="fetch_object",
            parameters={"object_name": "cup", "location": "kitchen"},
            subtasks=[action1, action2]
        )

        self.assertEqual(task.name, "fetch_object")
        self.assertEqual(task.parameters["object_name"], "cup")
        self.assertEqual(len(task.subtasks), 2)
        self.assertEqual(task.subtasks[0].name, "navigate")


class TestWorldState(unittest.TestCase):
    """Test cases for WorldState dataclass"""

    def test_world_state_creation(self):
        """Test creating WorldState with various attributes."""
        world_state = WorldState(
            robot_pose=(1.0, 2.0, 0.0),
            robot_orientation=(0.0, 0.0, 0.0, 1.0),
            objects={"ball": (1.5, 2.5, 0.5), "box": (3.0, 1.0, 0.5)},
            robot_capabilities=["navigation", "grasping", "manipulation"],
            environment_map={"rooms": ["kitchen", "living_room"]}
        )

        self.assertEqual(world_state.robot_pose, (1.0, 2.0, 0.0))
        self.assertEqual(len(world_state.objects), 2)
        self.assertIn("navigation", world_state.robot_capabilities)
        self.assertIn("kitchen", world_state.environment_map["rooms"])


class TestHTNPlanner(unittest.TestCase):
    """Test cases for HTNPlanner class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.planner = HTNPlanner()

    def test_initialization(self):
        """Test that HTNPlanner initializes correctly."""
        self.assertIsNotNone(self.planner)

    def test_decompose_task_method_exists(self):
        """Test that decompose_task method exists."""
        self.assertTrue(hasattr(self.planner, 'decompose_task'))

    def test_validate_task_preconditions_method_exists(self):
        """Test that validate_task_preconditions method exists."""
        self.assertTrue(hasattr(self.planner, 'validate_task_preconditions'))

    def test_execute_plan_with_monitoring_method_exists(self):
        """Test that execute_plan_with_monitoring method exists."""
        self.assertTrue(hasattr(self.planner, 'execute_plan_with_monitoring'))


class TestCognitivePlanner(unittest.TestCase):
    """Test cases for CognitivePlanner class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_executor = Mock(spec=IsaacSimActionExecutor)
        self.planner = CognitivePlanner(self.mock_executor)

    def test_initialization(self):
        """Test that CognitivePlanner initializes correctly."""
        self.assertIsNotNone(self.planner)
        self.assertEqual(self.planner.action_executor, self.mock_executor)

    def test_create_plan_method_exists(self):
        """Test that create_plan method exists."""
        self.assertTrue(hasattr(self.planner, 'create_plan'))

    def test_execute_plan_method_exists(self):
        """Test that execute_plan method exists."""
        self.assertTrue(hasattr(self.planner, 'execute_plan'))

    def test_update_plan_based_on_feedback_method_exists(self):
        """Test that update_plan_based_on_feedback method exists."""
        self.assertTrue(hasattr(self.planner, 'update_plan_based_on_feedback'))


class TestIsaacSimActionExecutor(unittest.TestCase):
    """Test cases for IsaacSimActionExecutor class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.executor = IsaacSimActionExecutor()

    def test_initialization(self):
        """Test that IsaacSimActionExecutor initializes correctly."""
        self.assertIsNotNone(self.executor)

    def test_execute_action_method_exists(self):
        """Test that execute_action method exists."""
        self.assertTrue(hasattr(self.executor, 'execute_action'))

    def test_get_robot_state_method_exists(self):
        """Test that get_robot_state method exists."""
        self.assertTrue(hasattr(self.executor, 'get_robot_state'))

    def test_validate_action_feasibility_method_exists(self):
        """Test that validate_action_feasibility method exists."""
        self.assertTrue(hasattr(self.executor, 'validate_action_feasibility'))


def suite():
    """Create a test suite combining all test cases."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAction))
    suite.addTest(unittest.makeSuite(TestTask))
    suite.addTest(unittest.makeSuite(TestWorldState))
    suite.addTest(unittest.makeSuite(TestHTNPlanner))
    suite.addTest(unittest.makeSuite(TestCognitivePlanner))
    suite.addTest(unittest.makeSuite(TestIsaacSimActionExecutor))
    return suite


if __name__ == '__main__':
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())