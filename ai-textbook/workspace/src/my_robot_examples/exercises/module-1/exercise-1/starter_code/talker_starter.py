#!/usr/bin/env python3
"""
Basic Publisher-Subscriber System - Talker (Publisher) Starter Code

This is the starter code for Exercise 1. Your task is to complete the implementation
of a ROS 2 publisher node that sends messages to a topic.

Requirements:
1. Create a node named 'talker'
2. Publish std_msgs/msg/String messages to the topic '/chatter'
3. Send messages at 2 Hz frequency
4. Each message should contain: "Hello World: [counter] [timestamp]"
5. Log published messages to the console
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    """
    A simple publisher node that sends messages to a topic.
    """

    def __init__(self):
        super().__init__('talker')

        # TODO: Create a publisher for String messages on the '/chatter' topic
        # Hint: Use self.create_publisher()

        # TODO: Create a timer that calls the timer_callback function every 0.5 seconds (2 Hz)
        # Hint: Use self.create_timer()

        # TODO: Initialize a counter variable to track message number

        self.get_logger().info('Talker node initialized')

    def timer_callback(self):
        """
        Callback function for the timer. This function should:
        1. Create a String message
        2. Set the message data to "Hello World: [counter] [timestamp]"
        3. Publish the message
        4. Log the published message
        5. Increment the counter
        """
        # TODO: Complete this function
        pass


def main(args=None):
    """
    Main function to initialize and run the talker node.
    """
    # TODO: Initialize rclpy
    # TODO: Create the TalkerNode
    # TODO: Spin the node
    # TODO: Properly shut down when interrupted
    pass


if __name__ == '__main__':
    main()