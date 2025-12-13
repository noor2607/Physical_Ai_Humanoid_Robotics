# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/robot_state_publisher_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math


class RobotStatePublisherNode(Node):
    """
    Simple robot state publisher for the simple robot model.
    """

    def __init__(self):
        super().__init__('robot_state_publisher_node')

        # Create publisher for joint states
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Create timer to publish joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)

        # Initialize joint positions
        self.time = 0.0
        self.get_logger().info('Robot state publisher started')

    def publish_joint_states(self):
        # Create joint state message
        msg = JointState()
        msg.name = ['left_wheel_joint', 'right_wheel_joint']
        msg.position = [math.sin(self.time), math.cos(self.time)]
        msg.velocity = [math.cos(self.time), -math.sin(self.time)]
        msg.effort = [0.0, 0.0]

        # Add header
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Publish message
        self.joint_pub.publish(msg)

        # Increment time
        self.time += 0.1


def main(args=None):
    rclpy.init(args=args)

    try:
        publisher = RobotStatePublisherNode()
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        print('Robot state publisher interrupted')
    finally:
        if 'publisher' in locals():
            publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()