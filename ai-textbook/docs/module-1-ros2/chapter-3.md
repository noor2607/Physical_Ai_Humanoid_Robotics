---
sidebar_position: 4
title: "Chapter 3: Actions and Parameters"
---

# Chapter 3: Actions and Parameters

## Overview

In this chapter, you'll learn about two advanced ROS 2 communication patterns: actions and parameters. Actions are ideal for long-running tasks that provide feedback, while parameters allow you to configure nodes dynamically.

## Learning Objectives

After completing this chapter, you will be able to:
- Implement action servers and clients for long-running tasks
- Use parameters to configure node behavior
- Understand when to use actions vs services vs topics
- Create feedback-driven robotic applications

## Understanding Actions

Actions are similar to services but designed for long-running tasks. They provide:
- Initial goal request
- Continuous feedback during execution
- Final result when complete
- Ability to cancel ongoing tasks

### Creating an Action Server

Let's create an action server that simulates a robot moving to a goal position:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/fibonacci_action_server.py
import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            self.get_logger().info(f'Feedback: {feedback_msg.sequence}')
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(1)  # Simulate work

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Result: {result.sequence}')

        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Creating an Action Client

Now let's create a client for the action server:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/fibonacci_action_client.py
import time
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci')

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self._action_client.wait_for_server()

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.sequence}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    action_client = FibonacciActionClient()

    action_client.send_goal(10)

    try:
        rclpy.spin(action_client)
    except KeyboardInterrupt:
        pass
    finally:
        action_client.destroy_node()


if __name__ == '__main__':
    main()
```

### Running the Action Example

1. Build the package:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select my_robot_examples
   source install/setup.bash
   ```

2. Run the action server in one terminal:
   ```bash
   ros2 run my_robot_examples fibonacci_action_server
   ```

3. Run the action client in another terminal:
   ```bash
   ros2 run my_robot_examples fibonacci_action_client
   ```

You should see the client receive continuous feedback while the server processes the goal!

## Understanding Parameters

Parameters allow you to configure node behavior without recompiling. They can be set at startup or changed dynamically.

### Creating a Parameter-Based Node

Let's create a node that uses parameters to control its behavior:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/parameter_node.py
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String


class ParameterNode(Node):

    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'my_robot')
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('sensor_enabled', True)

        # Get parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.max_speed = self.get_parameter('max_speed').value
        self.sensor_enabled = self.get_parameter('sensor_enabled').value

        # Create a publisher
        self.publisher = self.create_publisher(String, 'robot_status', 10)

        # Set up a timer to publish status
        self.timer = self.create_timer(1.0, self.timer_callback)

        # Add callback for parameter changes
        self.add_on_set_parameters_callback(self.parameter_callback)

        self.get_logger().info(
            f'Initialized with: name={self.robot_name}, '
            f'speed={self.max_speed}, sensor_enabled={self.sensor_enabled}')

    def timer_callback(self):
        msg = String()
        msg.data = f'{self.robot_name} running at {self.max_speed} m/s'
        self.publisher.publish(msg)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'max_speed' and param.type_ == Parameter.Type.DOUBLE:
                self.max_speed = param.value
                self.get_logger().info(f'Updated max_speed to {self.max_speed}')
            elif param.name == 'robot_name' and param.type_ == Parameter.Type.STRING:
                self.robot_name = param.value
                self.get_logger().info(f'Updated robot_name to {self.robot_name}')
            elif param.name == 'sensor_enabled' and param.type_ == Parameter.Type.BOOL:
                self.sensor_enabled = param.value
                self.get_logger().info(f'Updated sensor_enabled to {self.sensor_enabled}')
        return rclpy.node.SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Running with Parameters

1. Build the package:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select my_robot_examples
   source install/setup.bash
   ```

2. Run the node with parameters:
   ```bash
   ros2 run my_robot_examples parameter_node --ros-args -p robot_name:=turtlebot -p max_speed:=2.5
   ```

## Using Parameters from Launch Files

You can also set parameters using launch files. Create a launch file:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/launch/parameter_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_examples',
            executable='parameter_node',
            name='robot_controller',
            parameters=[
                {'robot_name': 'autobot'},
                {'max_speed': 3.0},
                {'sensor_enabled': True}
            ],
            output='screen'
        )
    ])
```

## Command-Line Parameter Tools

ROS 2 provides command-line tools for working with parameters:

### List Parameters of a Node
```bash
ros2 param list /parameter_node
```

### Get a Parameter Value
```bash
ros2 param get /parameter_node robot_name
```

### Set a Parameter Value
```bash
ros2 param set /parameter_node max_speed 5.0
```

## When to Use Each Communication Pattern

### Use Topics When:
- Streaming continuous data (sensors, robot state)
- Multiple subscribers need the same data
- Publisher doesn't need to know about subscribers
- Real-time performance is critical

### Use Services When:
- Request-response pattern is needed
- Task has a clear beginning and end
- Client needs to wait for a result
- Operation is relatively fast (< few seconds)

### Use Actions When:
- Task takes a long time to complete
- Client needs feedback during execution
- Task can be canceled
- Progress monitoring is important

### Use Parameters When:
- Configuring node behavior
- Values change infrequently
- Need to adjust settings without restarting nodes
- Values are used throughout the node's lifecycle

## Summary

In this chapter, you learned about two advanced ROS 2 communication patterns: actions for long-running tasks with feedback, and parameters for dynamic configuration. You implemented both patterns and learned when to use each one.

In the next chapter, we'll explore how to integrate ROS 2 with Python applications and create more complex examples.

## Practical Exercise

1. Create an action server that simulates a robot navigating to a goal position with feedback about distance remaining
2. Create a parameter-based node that adjusts its behavior based on external configuration
3. Use the command-line tools to inspect and modify parameters while nodes are running

## Resources

- [ROS 2 Actions Documentation](https://docs.ros.org/en/humble/Concepts/About-Actions.html)
- [ROS 2 Parameters Tutorial](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html)
- [ROS 2 Launch Files](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Creating-Launch-Files.html)