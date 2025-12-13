---
sidebar_position: 3
title: "Chapter 2: Nodes, Topics, and Services"
---

# Chapter 2: Nodes, Topics, and Services

## Overview

In this chapter, you'll learn how to create ROS 2 nodes and implement the two primary communication patterns: topics (publish-subscribe) and services (request-response). These patterns form the backbone of most robotic applications.

## Learning Objectives

After completing this chapter, you will be able to:
- Create and run ROS 2 nodes
- Implement publisher-subscriber communication using topics
- Implement request-response communication using services
- Test your nodes using ROS 2 command-line tools

## Understanding Nodes

A node is an executable that uses ROS 2 to communicate with other nodes. Nodes are organized into packages, which are the basic building blocks of ROS 2 software.

### Creating a Package

Let's create a package for our examples:

```bash
cd ~/ai-textbook/workspace/src
ros2 pkg create --build-type ament_python my_robot_examples
```

This creates a basic Python package structure.

## Publisher-Subscriber Pattern (Topics)

The publish-subscribe pattern allows nodes to exchange messages through topics. Publishers send messages to topics, and subscribers receive messages from topics.

### Creating a Publisher Node

Let's create a simple publisher that sends messages:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/talker.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):

    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    node = TalkerNode()

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

### Creating a Subscriber Node

Now let's create a subscriber that receives messages:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/listener.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ListenerNode(Node):

    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # Prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = ListenerNode()

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

### Running the Publisher-Subscriber Example

1. Make sure your files are in the correct location:
   ```bash
   # Check the files exist
   ls ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/
   ```

2. Build the package:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select my_robot_examples
   source install/setup.bash
   ```

3. Run the publisher in one terminal:
   ```bash
   ros2 run my_robot_examples talker
   ```

4. Run the subscriber in another terminal:
   ```bash
   ros2 run my_robot_examples listener
   ```

You should see the publisher sending messages and the subscriber receiving them!

## Service Pattern (Request-Response)

Services provide a request-response communication pattern. A client sends a request to a server and waits for a response.

### Creating a Service Server

Let's create a simple service that adds two numbers:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/add_two_ints_server.py
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):

    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {request.a} + {request.b} = {response.sum}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()

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

### Creating a Service Client

Now let's create a client that calls the service:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/add_two_ints_client.py
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):

    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()

    try:
        a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        b = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        response = node.send_request(a, b)
        node.get_logger().info(f'Result of {a} + {b} = {response.sum}')
    except Exception as e:
        node.get_logger().error(f'Service call failed: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Running the Service Example

1. Build the package again:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select my_robot_examples
   source install/setup.bash
   ```

2. Run the service server in one terminal:
   ```bash
   ros2 run my_robot_examples add_two_ints_server
   ```

3. Run the service client in another terminal:
   ```bash
   ros2 run my_robot_examples add_two_ints_client 5 3
   ```

You should see the server receive the request and the client receive the response!

## Using Command-Line Tools

ROS 2 provides several command-line tools to inspect and debug your system:

### List Topics
```bash
ros2 topic list
```

### Echo a Topic
```bash
ros2 topic echo /chatter std_msgs/msg/String
```

### List Services
```bash
ros2 service list
```

### Call a Service
```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
```

### List Nodes
```bash
ros2 node list
```

## Summary

In this chapter, you learned how to create ROS 2 nodes and implement both the publisher-subscriber and request-response communication patterns. You also learned how to use ROS 2 command-line tools to inspect and debug your system.

In the next chapter, we'll explore actions and parameters, which provide more advanced communication patterns for complex robotic tasks.

## Practical Exercise

1. Create your own publisher-subscriber pair that communicates sensor data (e.g., temperature readings)
2. Create a service that performs a useful robot operation (e.g., move_to_position)
3. Use the command-line tools to inspect your nodes and topics

## Resources

- [ROS 2 Nodes Documentation](https://docs.ros.org/en/humble/Concepts/About-Composition.html)
- [ROS 2 Topics Tutorial](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
- [ROS 2 Services Tutorial](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html)