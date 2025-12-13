# Solution Manual: Basic Publisher-Subscriber System (Module 1, Exercise 1)

## Exercise Information
- **Module**: Module 1 - Robotic Nervous System (ROS 2)
- **Exercise**: Exercise 1 - Basic Publisher-Subscriber System
- **Difficulty**: Beginner
- **Estimated Time**: 2-3 hours
- **Learning Objectives**:
  - Create a basic ROS 2 publisher-subscriber system
  - Understand topic-based communication
  - Implement proper node lifecycle management

## Problem Statement
Create a ROS 2 publisher node that sends "Hello World" messages at 2 Hz and a subscriber node that receives and prints these messages. The publisher should run indefinitely until stopped by the user, and the subscriber should handle incoming messages gracefully.

## Solution Approach

### Step 1: Understand ROS 2 Concepts
- Learn about nodes, topics, publishers, and subscribers
- Understand the publish-subscribe communication pattern
- Review ROS 2 Python client library (rclpy)

### Step 2: Create Publisher Node
- Initialize ROS 2 node
- Create publisher with appropriate message type
- Implement message publishing loop
- Handle node shutdown gracefully

### Step 3: Create Subscriber Node
- Initialize ROS 2 node
- Create subscriber with callback function
- Implement message processing
- Handle node shutdown gracefully

### Step 4: Test and Validate
- Build and source the workspace
- Run both nodes simultaneously
- Verify message exchange
- Test node shutdown

## Code Solution

### Publisher Node (`publisher_member_function.py`)
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Subscriber Node (`subscriber_member_function.py`)
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Package Configuration (`package.xml`)
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>py_publisher_subscriber</name>
  <version>0.0.0</version>
  <description>Examples of minimal publisher/subscriber using rclpy</description>
  <maintainer email="you@todo.todo">Your Name</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

### Setup Configuration (`setup.py`)
```python
from setuptools import setup

package_name = 'py_publisher_subscriber'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@todo.todo',
    description='Examples of minimal publisher/subscriber using rclpy',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = py_publisher_subscriber.publisher_member_function:main',
            'listener = py_publisher_subscriber.subscriber_member_function:main',
        ],
    },
)
```

## Explanation

### Key Concepts Demonstrated:
1. **Node Creation**: Proper initialization of ROS 2 nodes using the Node class
2. **Publisher Setup**: Creating a publisher with topic name and queue size
3. **Timer Callback**: Using timers for periodic message publishing
4. **Subscriber Setup**: Creating a subscriber with a callback function
5. **Message Types**: Using standard message types (std_msgs/String)
6. **Node Lifecycle**: Proper initialization and cleanup of nodes
7. **Logging**: Using ROS 2's built-in logging system

### Important Implementation Details:
- The publisher creates a timer that calls `timer_callback` every 0.5 seconds (2 Hz)
- The subscriber uses a callback function to process incoming messages
- Both nodes use `rclpy.spin()` to keep running until shutdown
- Proper cleanup is performed with `destroy_node()` and `rclpy.shutdown()`

## Alternative Approaches

### Approach 1: Using Classes with Separate Threads
Instead of using ROS 2's built-in timer, you could implement your own threading mechanism, though this is not recommended as it goes against ROS 2 best practices.

### Approach 2: Using Different Message Types
Instead of String messages, you could use custom message types or other standard types like Int32, Float64, etc.

### Approach 3: Adding Parameters
You could make the publishing frequency configurable through ROS 2 parameters.

## Common Mistakes to Avoid

1. **Forgetting to Initialize rclpy**: Always call `rclpy.init()` before creating nodes
2. **Not Properly Cleaning Up**: Always call `destroy_node()` and `rclpy.shutdown()`
3. **Incorrect Topic Names**: Ensure publisher and subscriber use the same topic name
4. **Wrong Message Types**: Ensure publisher and subscriber use compatible message types
5. **Not Sourcing the Workspace**: Remember to source the workspace before running nodes

## Assessment Criteria

### Functionality (50%)
- [ ] Publisher successfully sends messages at 2 Hz
- [ ] Subscriber successfully receives and prints messages
- [ ] Nodes run without errors
- [ ] Proper shutdown when terminated

### Code Quality (30%)
- [ ] Clean, well-commented code
- [ ] Proper error handling
- [ ] Follows ROS 2 Python style guidelines
- [ ] Good variable and function naming

### Understanding (20%)
- [ ] Correct use of ROS 2 concepts (nodes, topics, publishers, subscribers)
- [ ] Proper message type usage
- [ ] Understanding of publish-subscribe pattern
- [ ] Appropriate lifecycle management

## Extension Activities

1. **Modify Message Content**: Change the message to include timestamps or sequence numbers
2. **Add Parameters**: Make publishing frequency configurable through parameters
3. **Multiple Topics**: Create multiple publishers and subscribers on different topics
4. **Custom Message Types**: Create and use custom message types instead of String
5. **Error Handling**: Add robust error handling for network issues

## Troubleshooting

### Common Issues:
- **"Topic not found"**: Check that both nodes are running and topic names match
- **"Module not found"**: Ensure the package is built and workspace is sourced
- **"Permission denied"**: Check file permissions and ensure executable bit is set
- **"Node already exists"**: Make sure node names are unique

### Debugging Steps:
1. Verify the workspace is properly built and sourced
2. Check that topic names match exactly between publisher and subscriber
3. Use `ros2 topic list` to verify the topic exists
4. Use `ros2 topic echo /topic_name` to manually verify messages
5. Check the console output for error messages

---

**Instructor Notes**: This solution demonstrates the fundamental concepts of ROS 2 communication. Students should understand the publish-subscribe pattern and be able to modify the example for different use cases. Encourage students to experiment with different message types and frequencies to deepen their understanding.