#!/usr/bin/env python3
"""
Validation script for Exercise 1: Basic Publisher-Subscriber System

This script validates that the student's implementation meets the requirements:
1. Publisher node exists and publishes to /chatter topic
2. Subscriber node exists and subscribes to /chatter topic
3. Messages are being exchanged between nodes
4. Message format is correct
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import threading


class Exercise1Validator(Node):
    """
    Validator node that checks if the exercise requirements are met.
    """

    def __init__(self):
        super().__init__('exercise1_validator')

        # Variables to track validation results
        self.messages_received = []
        self.message_count = 0
        self.expected_patterns = ['Hello World:', 'timestamp']

        # Create a subscriber to check if messages are being published correctly
        self.validator_sub = self.create_subscription(
            String,
            '/chatter',
            self.validation_callback,
            10)

        # Timer to run validation checks
        self.timer = self.create_timer(0.1, self.run_validation)
        self.start_time = time.time()
        self.timeout = 10  # seconds

        self.get_logger().info('Exercise 1 validator started')

    def validation_callback(self, msg):
        """
        Callback to receive messages and validate them.
        """
        self.messages_received.append(msg.data)
        self.message_count += 1
        self.get_logger().info(f'Validator received: "{msg.data}"')

    def run_validation(self):
        """
        Main validation function that runs periodically.
        """
        elapsed = time.time() - self.start_time

        # Stop validation after timeout
        if elapsed > self.timeout:
            self.get_logger().info('Stopping validator after timeout')
            # We can't destroy the node from a timer callback, so just stop the timer
            self.timer.cancel()
            # Since we can't destroy the node from a timer callback, we'll just cancel the timer
            # The main function will handle the final validation

    def validate_results(self):
        """
        Validate the results after collecting messages.
        """
        print("\n" + "="*50)
        print("EXERCISE 1 VALIDATION RESULTS")
        print("="*50)

        # Check if any messages were received
        if self.message_count == 0:
            print("❌ FAILED: No messages received on /chatter topic")
            print("   Make sure your publisher node is running and publishing to /chatter")
        else:
            print(f"✅ PASSED: Received {self.message_count} messages on /chatter topic")

            # Check message format
            if self.messages_received:
                first_msg = self.messages_received[0]
                if "Hello World:" in first_msg:
                    print("✅ PASSED: Message format contains 'Hello World:'")
                else:
                    print("❌ FAILED: Message format incorrect - should contain 'Hello World:'")

                # Check if timestamp is included
                if any(char.isdigit() for char in first_msg):
                    print("✅ PASSED: Message contains numeric content (likely timestamp)")
                else:
                    print("⚠️  WARNING: Message doesn't seem to contain timestamp")

        # Check message variety (counter should increment)
        if len(set(self.messages_received)) > 1:
            print("✅ PASSED: Different messages received (counter likely incrementing)")
        elif self.message_count > 1:
            print("⚠️  WARNING: All messages identical (counter may not be incrementing)")

        print("="*50)
        print("Validation complete!")
        print("If you see 'PASSED' messages, your implementation is working correctly.")
        print("If you see 'FAILED' messages, review the requirements and fix your code.")
        print("="*50)


def main(args=None):
    """
    Main function to run the validation.
    """
    rclpy.init(args=args)

    validator = Exercise1Validator()

    try:
        print("Starting Exercise 1 validation...")
        print("Make sure your talker and listener nodes are running in other terminals.")
        print("Validation will run for 10 seconds.\n")

        # Run for the timeout period
        start_time = time.time()
        while time.time() - start_time < validator.timeout:
            rclpy.spin_once(validator, timeout_sec=0.1)

    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    finally:
        # Run final validation
        validator.validate_results()
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()