---
sidebar_position: 5
title: "Chapter 4: Python Integration"
---

# Chapter 4: Python Integration

## Overview

In this chapter, you'll learn how to effectively integrate Python with ROS 2. Python is one of the most popular languages for robotics development due to its simplicity, extensive libraries, and strong community support. You'll learn best practices for creating robust Python-based ROS 2 nodes.

## Learning Objectives

After completing this chapter, you will be able to:
- Create well-structured Python ROS 2 packages
- Implement error handling and logging in Python nodes
- Use Python libraries for robotics applications
- Follow Python-specific ROS 2 conventions
- Debug Python ROS 2 applications effectively

## Creating a Well-Structured Python Package

### Package Organization

A well-structured ROS 2 Python package typically follows this organization:

```
my_robot_package/
├── package.xml          # Package metadata
├── setup.py             # Python package setup
├── setup.cfg            # Installation configuration
├── my_robot_package/    # Main Python module
│   ├── __init__.py
│   ├── robot_controller.py
│   ├── sensor_processor.py
│   └── utils/
│       ├── __init__.py
│       └── data_processing.py
├── launch/              # Launch files
│   └── robot_launch.py
├── config/              # Configuration files
│   └── robot_params.yaml
└── test/                # Test files
    └── test_robot_controller.py
```

### Setting Up the Package Structure

Let's create a more comprehensive Python package for robotics:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/robot_controller.py
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String, Float32
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


class RobotController(Node):
    """
    A comprehensive robot controller node demonstrating Python best practices.
    """

    def __init__(self):
        super().__init__('robot_controller')

        # Declare parameters with descriptions
        self.declare_parameter('linear_speed', 0.5,
                              'Linear speed for robot movement')
        self.declare_parameter('angular_speed', 1.0,
                              'Angular speed for robot rotation')
        self.declare_parameter('safety_distance', 0.5,
                              'Minimum distance to obstacles')

        # Get parameter values
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.safety_distance = self.get_parameter('safety_distance').value

        # Set up QoS profiles for different types of data
        sensor_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST
        )

        cmd_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Create publishers
        self.cmd_vel_publisher = self.create_publisher(
            Twist, '/cmd_vel', cmd_qos)
        self.status_publisher = self.create_publisher(
            String, '/robot_status', 10)

        # Create subscribers
        self.scan_subscriber = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, sensor_qos)

        # Create timers
        self.control_timer = self.create_timer(0.1, self.control_loop)

        # Initialize robot state
        self.scan_data = None
        self.robot_state = 'idle'  # idle, moving, avoiding_obstacle
        self.get_logger().info('Robot controller initialized')

    def scan_callback(self, msg):
        """Process laser scan data."""
        self.scan_data = msg
        self.get_logger().debug(f'Received scan with {len(msg.ranges)} points')

    def control_loop(self):
        """Main control loop for robot navigation."""
        if self.scan_data is None:
            return

        # Determine minimum distance to obstacles
        valid_ranges = [r for r in self.scan_data.ranges
                       if not math.isnan(r) and r > 0]

        if not valid_ranges:
            self.get_logger().warn('No valid ranges in scan data')
            return

        min_distance = min(valid_ranges)

        # Create command message
        cmd_msg = Twist()

        if min_distance < self.safety_distance:
            # Obstacle detected, rotate to avoid
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = self.angular_speed
            self.robot_state = 'avoiding_obstacle'
        else:
            # Clear path, move forward
            cmd_msg.linear.x = self.linear_speed
            cmd_msg.angular.z = 0.0
            self.robot_state = 'moving'

        # Publish command
        self.cmd_vel_publisher.publish(cmd_msg)

        # Publish status
        status_msg = String()
        status_msg.data = f'State: {self.robot_state}, Distance: {min_distance:.2f}m'
        self.status_publisher.publish(status_msg)

        self.get_logger().info(f'{status_msg.data}', throttle_duration_sec=1)


def main(args=None):
    """Main function with proper error handling."""
    rclpy.init(args=args)

    try:
        robot_controller = RobotController()
        rclpy.spin(robot_controller)
    except KeyboardInterrupt:
        print('Interrupted by user')
    except Exception as e:
        print(f'Error occurred: {e}')
    finally:
        if 'robot_controller' in locals():
            robot_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Creating a Sensor Processing Module

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/sensor_processor.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
from std_msgs.msg import Float32MultiArray
import numpy as np
from typing import List, Tuple


class SensorProcessor(Node):
    """
    Processes sensor data and extracts meaningful information.
    """

    def __init__(self):
        super().__init__('sensor_processor')

        # Create subscribers
        self.scan_subscriber = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        # Create publishers
        self.obstacle_publisher = self.create_publisher(
            Float32MultiArray, '/obstacles', 10)
        self.free_space_publisher = self.create_publisher(
            Float32MultiArray, '/free_space', 10)

        # Initialize processing parameters
        self.angle_increment = None
        self.get_logger().info('Sensor processor initialized')

    def scan_callback(self, msg: LaserScan):
        """Process incoming laser scan data."""
        self.angle_increment = msg.angle_increment

        # Convert scan ranges to Cartesian coordinates
        points = self.scan_to_cartesian(msg)

        # Process points to find obstacles and free space
        obstacles, free_space = self.process_environment(points)

        # Publish results
        self.publish_obstacles(obstacles)
        self.publish_free_space(free_space)

    def scan_to_cartesian(self, scan_msg: LaserScan) -> List[Tuple[float, float]]:
        """Convert laser scan ranges to Cartesian coordinates."""
        points = []
        angle = scan_msg.angle_min

        for range_val in scan_msg.ranges:
            if not (float('inf') == range_val or float('-inf') == range_val or
                    range_val != range_val):  # Check for inf and NaN
                x = range_val * np.cos(angle)
                y = range_val * np.sin(angle)
                points.append((x, y))
            angle += scan_msg.angle_increment

        return points

    def process_environment(self, points: List[Tuple[float, float]]) -> Tuple[List, List]:
        """Process environment to identify obstacles and free space."""
        # Simple clustering to identify obstacles
        obstacles = []
        free_space = []

        # For demonstration, just categorize points
        for x, y in points:
            distance = np.sqrt(x**2 + y**2)
            if distance < 1.0:  # Close points are obstacles
                obstacles.append((x, y, distance))
            else:  # Far points are free space
                free_space.append((x, y, distance))

        return obstacles, free_space

    def publish_obstacles(self, obstacles: List):
        """Publish obstacle information."""
        if not obstacles:
            return

        msg = Float32MultiArray()
        # Flatten obstacle data into array
        msg.data = [item for sublist in obstacles for item in sublist]
        self.obstacle_publisher.publish(msg)

    def publish_free_space(self, free_space: List):
        """Publish free space information."""
        if not free_space:
            return

        msg = Float32MultiArray()
        # Flatten free space data into array
        msg.data = [item for sublist in free_space for item in sublist]
        self.free_space_publisher.publish(msg)


def main(args=None):
    """Main function for sensor processor."""
    rclpy.init(args=args)

    try:
        processor = SensorProcessor()
        rclpy.spin(processor)
    except KeyboardInterrupt:
        print('Sensor processor interrupted')
    finally:
        if 'processor' in locals():
            processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Using Python Libraries for Robotics

### NumPy for Mathematical Operations

NumPy is essential for mathematical operations in robotics:

```python
import numpy as np

# Example: Transform calculations
def transform_point(x, y, theta, dx, dy):
    """Apply rotation and translation to a point."""
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    point = np.array([x, y])
    translation = np.array([dx, dy])
    return R @ point + translation

# Example: Distance calculations
def calculate_distances(points):
    """Calculate distances from origin to multiple points."""
    points_array = np.array(points)
    return np.sqrt(np.sum(points_array**2, axis=1))
```

### Matplotlib for Visualization

For debugging and visualization:

```python
import matplotlib.pyplot as plt

def visualize_scan(ranges, angles):
    """Visualize laser scan data."""
    x = [r * np.cos(theta) for r, theta in zip(ranges, angles)]
    y = [r * np.sin(theta) for r, theta in zip(ranges, angles)]

    plt.figure()
    plt.scatter(x, y)
    plt.axis('equal')
    plt.title('Laser Scan Visualization')
    plt.show()
```

## Error Handling and Logging Best Practices

### Comprehensive Error Handling

```python
import traceback
from rclpy.exceptions import ParameterNotDeclaredException


class RobustNode(Node):
    def __init__(self):
        super().__init__('robust_node')

        # Set up error handling
        self.setup_parameters()
        self.setup_communication()
        self.setup_timers()

    def setup_parameters(self):
        """Safely set up parameters with defaults."""
        try:
            self.declare_parameter('param1', 'default_value')
            self.declare_parameter('param2', 1.0)
        except Exception as e:
            self.get_logger().error(f'Failed to declare parameters: {e}')

    def safe_parameter_get(self, param_name, default_value):
        """Safely get parameter with fallback."""
        try:
            return self.get_parameter(param_name).value
        except ParameterNotDeclaredException:
            self.get_logger().warn(f'Parameter {param_name} not declared, using default')
            return default_value
        except Exception as e:
            self.get_logger().error(f'Error getting parameter {param_name}: {e}')
            return default_value

    def message_callback(self, msg):
        """Process message with error handling."""
        try:
            # Process message
            result = self.process_message(msg)
            self.publish_result(result)
        except Exception as e:
            self.get_logger().error(f'Error processing message: {e}')
            self.get_logger().debug(traceback.format_exc())
```

## Debugging Python ROS 2 Applications

### Using Python Debugging Tools

```python
import pdb
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class DebuggableNode(Node):
    def __init__(self):
        super().__init__('debuggable_node')

        # Set up debugging
        self.debug_enabled = self.declare_parameter('debug', False).value

    def debug_point(self, message):
        """Add debug points that can be toggled."""
        if self.debug_enabled:
            self.get_logger().debug(message)
            # Optionally break into debugger
            if self.declare_parameter('break_at_debug', False).value:
                pdb.set_trace()
```

## Testing Python ROS 2 Nodes

### Creating Unit Tests

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/test/test_robot_controller.py
import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from my_robot_examples.robot_controller import RobotController


class TestRobotController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = RobotController()
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def tearDown(self):
        self.node.destroy_node()

    def test_parameter_initialization(self):
        """Test that parameters are properly initialized."""
        linear_speed = self.node.get_parameter('linear_speed').value
        self.assertEqual(linear_speed, 0.5)

    def test_node_creation(self):
        """Test that node is created successfully."""
        self.assertIsNotNone(self.node)


if __name__ == '__main__':
    unittest.main()
```

## Launch Files for Python Nodes

Create a launch file to start multiple nodes:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/launch/robot_system_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get package share directory
    pkg_share = get_package_share_directory('my_robot_examples')

    return LaunchDescription([
        # Robot controller node
        Node(
            package='my_robot_examples',
            executable='robot_controller',  # This will be the entry point
            name='robot_controller',
            parameters=[
                os.path.join(pkg_share, 'config', 'robot_params.yaml')
            ],
            output='screen',
            respawn=True
        ),

        # Sensor processor node
        Node(
            package='my_robot_examples',
            executable='sensor_processor',
            name='sensor_processor',
            output='screen',
            respawn=True
        )
    ])
```

## Configuration Files

Create a YAML configuration file:

```yaml
# File: ~/ai-textbook/workspace/src/my_robot_examples/config/robot_params.yaml
/**:
  ros__parameters:
    linear_speed: 0.8
    angular_speed: 1.5
    safety_distance: 0.7
    debug: false
```

## Setup Configuration

Update the setup.py file to include entry points:

```python
# Update ~/ai-textbook/workspace/src/my_robot_examples/setup.py
from setuptools import find_packages, setup

package_name = 'my_robot_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/robot_system_launch.py']),
        ('share/' + package_name + '/config',
            ['config/robot_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Physical AI Course',
    maintainer_email='info@physical-ai-course.com',
    description='Examples for Physical AI & Humanoid Robotics Course',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_controller = my_robot_examples.robot_controller:main',
            'sensor_processor = my_robot_examples.sensor_processor:main',
            'parameter_node = my_robot_examples.parameter_node:main',
            'talker = my_robot_examples.talker:main',
            'listener = my_robot_examples.listener:main',
            'add_two_ints_server = my_robot_examples.add_two_ints_server:main',
            'add_two_ints_client = my_robot_examples.add_two_ints_client:main',
            'fibonacci_action_server = my_robot_examples.fibonacci_action_server:main',
            'fibonacci_action_client = my_robot_examples.fibonacci_action_client:main',
        ],
    },
)
```

## Running the Examples

1. Build the package:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select my_robot_examples
   source install/setup.bash
   ```

2. Run individual nodes:
   ```bash
   ros2 run my_robot_examples robot_controller
   ```

3. Run with launch file:
   ```bash
   ros2 launch my_robot_examples robot_system_launch.py
   ```

## Summary

In this chapter, you learned how to effectively integrate Python with ROS 2, following best practices for code structure, error handling, and testing. You created well-structured Python nodes with proper parameter handling, logging, and debugging capabilities.

In the next chapter, we'll explore URDF (Unified Robot Description Format) for describing robots in XML.

## Practical Exercise

1. Create a Python node that integrates multiple sensors and processes their data
2. Implement proper error handling and logging in your node
3. Create a launch file that starts multiple nodes with different configurations
4. Write unit tests for your Python nodes

## Resources

- [ROS 2 Python Developer Guide](https://docs.ros.org/en/humble/How-To-Guides/Developing-Python-package.html)
- [Python ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
- [NumPy Documentation](https://numpy.org/doc/)
- [Python Testing in ROS 2](https://docs.ros.org/en/humble/How-To-Guides/Colcon-Tutorial.html#test-with-colcon)