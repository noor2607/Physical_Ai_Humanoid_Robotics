#!/usr/bin/env python3
"""
Validation script for Exercise 1: Basic Gazebo Environment Setup

This script validates that the student's implementation meets the requirements:
1. World file exists and is properly formatted
2. Robot model can be spawned in Gazebo
3. Robot has required sensors (camera and LiDAR)
4. Basic navigation is possible
"""

import os
import sys
import subprocess
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math

class Exercise1Validator(Node):
    """
    Validator node that checks if the exercise requirements are met.
    """

    def __init__(self):
        super().__init__('exercise1_validator')

        # Variables to track validation results
        self.lidar_received = False
        self.camera_received = False
        self.odom_received = False
        self.robot_moved = False
        self.initial_position = None
        self.current_position = None

        # Create subscribers to check if robot is publishing data
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10
        )

        self.camera_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Publisher for robot movement
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('Exercise 1 validator started')

    def lidar_callback(self, msg):
        """Callback to check LiDAR data."""
        if len(msg.ranges) > 0:
            self.lidar_received = True
            self.get_logger().info('LiDAR data received successfully')

    def camera_callback(self, msg):
        """Callback to check camera data."""
        if msg.height > 0 and msg.width > 0:
            self.camera_received = True
            self.get_logger().info('Camera data received successfully')

    def odom_callback(self, msg):
        """Callback to check odometry and track movement."""
        self.odom_received = True

        # Store initial position if not already stored
        if self.initial_position is None:
            self.initial_position = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z
            )
        else:
            # Check if robot has moved significantly
            current_pos = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z
            )
            self.current_position = current_pos

            # Calculate distance moved
            dist_moved = math.sqrt(
                (current_pos[0] - self.initial_position[0])**2 +
                (current_pos[1] - self.initial_position[1])**2 +
                (current_pos[2] - self.initial_position[2])**2
            )

            if dist_moved > 0.1:  # If moved more than 10cm
                self.robot_moved = True

    def validate_world_file(self):
        """Check if the required world file exists."""
        world_file = "simple_room.world"
        # Check in common locations
        possible_paths = [
            f"./{world_file}",
            f"../{world_file}",
            f"../../{world_file}",
            f"../../../{world_file}",
            f"worlds/{world_file}",
            f"simulation/worlds/{world_file}"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.get_logger().info(f'Found world file at: {path}')
                # Try to read and validate basic structure
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if '<sdf' in content and '<world' in content:
                            self.get_logger().info('World file has valid SDF structure')
                            return True
                except:
                    continue

        self.get_logger().warn('World file not found or invalid')
        return False

    def attempt_navigation(self):
        """Try to move the robot to validate navigation capability."""
        self.get_logger().info('Attempting to move robot for navigation validation')

        # Send forward velocity for 3 seconds
        twist = Twist()
        twist.linear.x = 0.5  # Move forward at 0.5 m/s
        twist.angular.z = 0.0

        start_time = time.time()
        while time.time() - start_time < 3.0:
            self.cmd_vel_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.1)

        # Stop the robot
        twist.linear.x = 0.0
        self.cmd_vel_pub.publish(twist)

    def validate_results(self):
        """Validate the results after testing."""
        print("\n" + "="*60)
        print("EXERCISE 1 VALIDATION RESULTS")
        print("="*60)

        # Check world file
        world_valid = self.validate_world_file()
        if world_valid:
            print("✅ PASSED: World file exists and has valid structure")
        else:
            print("❌ FAILED: World file not found or invalid structure")

        # Check LiDAR
        if self.lidar_received:
            print("✅ PASSED: LiDAR sensor data received")
        else:
            print("❌ FAILED: No LiDAR data received")

        # Check camera
        if self.camera_received:
            print("✅ PASSED: Camera sensor data received")
        else:
            print("❌ FAILED: No camera data received")

        # Check odometry
        if self.odom_received:
            print("✅ PASSED: Odometry data received")
        else:
            print("❌ FAILED: No odometry data received")

        # Check movement
        if self.robot_moved:
            print("✅ PASSED: Robot moved successfully (navigation working)")
        else:
            print("❌ FAILED: Robot did not move significantly")

        # Overall result
        required_checks = [world_valid, self.lidar_received, self.camera_received, self.odom_received]
        optional_checks = [self.robot_moved]  # Movement is good but not strictly required for basic setup

        passed_required = sum(required_checks)
        total_required = len(required_checks)

        print(f"\nOverall: {passed_required}/{total_required} required checks passed")

        if passed_required == total_required:
            print("🎉 EXERCISE 1 COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  EXERCISE 1 needs more work.")

        print("="*60)
        return passed_required == total_required

def main(args=None):
    """Main function to run the validation."""
    rclpy.init(args=args)

    validator = Exercise1Validator()

    try:
        print("Starting Exercise 1 validation...")
        print("Make sure your Gazebo simulation is running with your robot.")
        print("Validation will run for 10 seconds to collect data.\n")

        # Run for 10 seconds to collect data
        start_time = time.time()
        while time.time() - start_time < 10.0:
            rclpy.spin_once(validator, timeout_sec=0.1)

        # Attempt navigation
        validator.attempt_navigation()

        # Wait a bit more for movement to register
        start_time = time.time()
        while time.time() - start_time < 2.0:
            rclpy.spin_once(validator, timeout_sec=0.1)

    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    finally:
        # Run final validation
        success = validator.validate_results()
        validator.destroy_node()
        rclpy.shutdown()

        if success:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure

if __name__ == '__main__':
    main()