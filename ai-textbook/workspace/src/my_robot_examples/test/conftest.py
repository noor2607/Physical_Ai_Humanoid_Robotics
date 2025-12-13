"""
Pytest configuration for the Physical AI & Humanoid Robotics course
"""

import pytest
import sys
import os

# Add the voice_control module to the path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'my_robot_examples', 'voice_control'))


@pytest.fixture
def sample_robot_state():
    """Provide a sample RobotState for testing."""
    from llm_integration import RobotState
    return RobotState(
        position=[1.0, 2.0, 0.0],
        orientation=[0.0, 0.0, 0.0, 1.0],
        battery_level=85.5,
        gripper_status="open",
        joint_positions={"arm_joint_1": 0.5, "arm_joint_2": -0.3}
    )


@pytest.fixture
def sample_environment_state():
    """Provide a sample EnvironmentState for testing."""
    from llm_integration import EnvironmentState
    return EnvironmentState(
        objects=[{"name": "ball", "position": [1.0, 1.0, 0.5], "type": "graspable"}],
        obstacles=[{"position": [2.0, 2.0, 0.0], "size": [1.0, 1.0, 1.0]}],
        navigation_map={"rooms": ["kitchen", "living_room"], "connections": [("kitchen", "living_room")]},
        lighting_conditions="bright"
    )


@pytest.fixture
def sample_world_state():
    """Provide a sample WorldState for testing."""
    from cognitive_planning import WorldState
    return WorldState(
        robot_pose=(1.0, 2.0, 0.0),
        robot_orientation=(0.0, 0.0, 0.0, 1.0),
        objects={"ball": (1.5, 2.5, 0.5), "box": (3.0, 1.0, 0.5)},
        robot_capabilities=["navigation", "grasping", "manipulation"],
        environment_map={"rooms": ["kitchen", "living_room"]}
    )


@pytest.fixture
def mock_isaac_interface():
    """Provide a mock IsaacSimInterface for testing."""
    from unittest.mock import Mock
    from voice_to_action import IsaacSimInterface

    mock = Mock(spec=IsaacSimInterface)
    mock.execute_action.return_value = True
    mock.get_robot_state.return_value = {"position": [0, 0, 0], "status": "idle"}
    return mock


@pytest.fixture
def sample_action():
    """Provide a sample Action for testing."""
    from cognitive_planning import Action
    return Action(
        name="navigate",
        parameters={"target_location": "kitchen"},
        preconditions=["robot_at(start_location)"],
        effects=["robot_at(target_location)"]
    )


@pytest.fixture
def sample_task():
    """Provide a sample Task for testing."""
    from cognitive_planning import Task, Action
    action1 = Action(name="navigate", parameters={"target": "kitchen"}, preconditions=[], effects=[])
    action2 = Action(name="grasp", parameters={"object": "cup"}, preconditions=[], effects=[])

    return Task(
        name="fetch_object",
        parameters={"object_name": "cup", "location": "kitchen"},
        subtasks=[action1, action2]
    )


def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Add markers to tests based on their names
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)