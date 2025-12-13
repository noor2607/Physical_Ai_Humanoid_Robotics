#!/usr/bin/env python3
"""
Basic Publisher-Subscriber System - Talker (Publisher) Solution

This is the solution code for Exercise 1. It implements a ROS 2 publisher node
that sends messages to a topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class TalkerNode(Node):
    """
    A simple publisher node that sends messages to a topic.
    """

    def __init__(self):
        super().__init__('talker')

        # Create a publisher for String messages on the '/chatter' topic
        self.publisher = self.create_publisher(String, '/chatter', 10)

        # Create a timer that calls the timer_callback function every 0.5 seconds (2 Hz)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Initialize a counter variable to track message number
        self.counter = 0

        self.get_logger().info('Talker node initialized')

    def timer_callback(self):
        """
        Callback function for the timer. This function:
        1. Creates a String message
        2. Sets the message data to "Hello World: [counter] [timestamp]"
        3. Publishes the message
        4. Logs the published message
        5. Increments the counter
        """
        msg = String()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        msg.data = f'Hello World: {self.counter} {timestamp}'

        self.publisher.publish(msg)
        self.get_logger().info(f'Published: "{msg.data}"')

        self.counter += 1


def main(args=None):
    """
    Main function to initialize and run the talker node.
    """
    rclpy.init(args=args)

    try:
        node = TalkerNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()