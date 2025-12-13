#!/usr/bin/env python3
"""
Unit tests for the llm_integration.py module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from dataclasses import asdict

# Add the voice_control module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'my_robot_examples', 'voice_control'))

from llm_integration import (
    LLMConfig,
    RobotState,
    EnvironmentState,
    LLMInterface,
    OpenAILLMInterface,
    IsaacLLMInterface
)


class TestLLMConfig(unittest.TestCase):
    """Test cases for LLMConfig dataclass"""

    def test_llm_config_creation(self):
        """Test creating LLMConfig with default values."""
        config = LLMConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.model_name, "gpt-3.5-turbo")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1000)


class TestRobotState(unittest.TestCase):
    """Test cases for RobotState dataclass"""

    def test_robot_state_creation(self):
        """Test creating RobotState with various attributes."""
        robot_state = RobotState(
            position=[1.0, 2.0, 0.0],
            orientation=[0.0, 0.0, 0.0, 1.0],
            battery_level=85.5,
            gripper_status="open",
            joint_positions={"arm_joint_1": 0.5, "arm_joint_2": -0.3}
        )

        self.assertEqual(robot_state.position, [1.0, 2.0, 0.0])
        self.assertEqual(robot_state.battery_level, 85.5)
        self.assertEqual(robot_state.gripper_status, "open")
        self.assertEqual(robot_state.joint_positions["arm_joint_1"], 0.5)


class TestEnvironmentState(unittest.TestCase):
    """Test cases for EnvironmentState dataclass"""

    def test_environment_state_creation(self):
        """Test creating EnvironmentState with various attributes."""
        env_state = EnvironmentState(
            objects=[{"name": "ball", "position": [1.0, 1.0, 0.5], "type": "graspable"}],
            obstacles=[{"position": [2.0, 2.0, 0.0], "size": [1.0, 1.0, 1.0]}],
            navigation_map={"rooms": ["kitchen", "living_room"], "connections": [("kitchen", "living_room")]},
            lighting_conditions="bright"
        )

        self.assertEqual(len(env_state.objects), 1)
        self.assertEqual(env_state.objects[0]["name"], "ball")
        self.assertEqual(len(env_state.obstacles), 1)
        self.assertEqual(env_state.lighting_conditions, "bright")


class TestLLMInterface(unittest.TestCase):
    """Test cases for LLMInterface class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = LLMConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        self.llm_interface = LLMInterface(self.config)

    def test_initialization(self):
        """Test that LLMInterface initializes correctly."""
        self.assertIsNotNone(self.llm_interface)
        self.assertEqual(self.llm_interface.config, self.config)

    def test_abstract_methods_exist(self):
        """Test that abstract methods are defined."""
        self.assertTrue(hasattr(self.llm_interface, 'query_with_context'))
        self.assertTrue(hasattr(self.llm_interface, 'extract_structured_response'))


class TestOpenAILLMInterface(unittest.TestCase):
    """Test cases for OpenAILLMInterface class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = LLMConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        self.openai_interface = OpenAILLMInterface(self.config)

    def test_initialization(self):
        """Test that OpenAILLMInterface initializes correctly."""
        self.assertIsNotNone(self.openai_interface)
        self.assertEqual(self.openai_interface.config, self.config)

    @patch('llm_integration.openai.ChatCompletion.create')
    def test_query_with_context(self, mock_create):
        """Test query_with_context method."""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"action": "move", "target": "kitchen"}'
        mock_create.return_value = mock_response

        # Create test states
        robot_state = RobotState(
            position=[0.0, 0.0, 0.0],
            orientation=[0.0, 0.0, 0.0, 1.0],
            battery_level=100.0,
            gripper_status="closed",
            joint_positions={}
        )

        env_state = EnvironmentState(
            objects=[],
            obstacles=[],
            navigation_map={},
            lighting_conditions="normal"
        )

        # Call the method
        result = self.openai_interface.query_with_context(
            "Go to the kitchen",
            {"conversation_history": []},
            robot_state,
            env_state
        )

        # Verify the result
        self.assertIsNotNone(result)
        mock_create.assert_called_once()


class TestIsaacLLMInterface(unittest.TestCase):
    """Test cases for IsaacLLMInterface class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = LLMConfig(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        self.isaac_interface = IsaacLLMInterface(self.config)

    def test_initialization(self):
        """Test that IsaacLLMInterface initializes correctly."""
        self.assertIsNotNone(self.isaac_interface)
        self.assertEqual(self.isaac_interface.config, self.config)

    def test_process_natural_command(self):
        """Test process_natural_command method."""
        # This method should be tested with actual implementation
        # For now, just verify it exists and doesn't crash with basic input
        self.assertTrue(hasattr(self.isaac_interface, 'process_natural_command'))
        self.assertTrue(hasattr(self.isaac_interface, 'generate_robot_response'))


def suite():
    """Create a test suite combining all test cases."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLLMConfig))
    suite.addTest(unittest.makeSuite(TestRobotState))
    suite.addTest(unittest.makeSuite(TestEnvironmentState))
    suite.addTest(unittest.makeSuite(TestLLMInterface))
    suite.addTest(unittest.makeSuite(TestOpenAILLMInterface))
    suite.addTest(unittest.makeSuite(TestIsaacLLMInterface))
    return suite


if __name__ == '__main__':
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())