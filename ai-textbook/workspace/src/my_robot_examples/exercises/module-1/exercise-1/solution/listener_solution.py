#!/usr/bin/env python3
"""
Basic Publisher-Subscriber System - Listener (Subscriber) Solution

This is the solution code for Exercise 1. It implements a ROS 2 subscriber node
that receives messages from a topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ListenerNode(Node):
    """
    A simple subscriber node that receives messages from a topic.
    """

    def __init__(self):
        super().__init__('listener')

        # Create a subscription to String messages on the '/chatter' topic
        self.subscription = self.create_subscription(
            String,
            '/chatter',
            self.listener_callback,
            10)  # QoS depth

        # Prevent unused variable warning
        self.subscription

        self.get_logger().info('Listener node initialized')

    def listener_callback(self, msg):
        """
        Callback function that is called when a message is received.
        This function logs the received message to the console.
        """
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    """
    Main function to initialize and run the listener node.
    """
    rclpy.init(args=args)

    try:
        node = ListenerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()