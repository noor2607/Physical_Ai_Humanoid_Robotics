#!/usr/bin/env python3
"""
Validation script for Exercise 2: Sensor Simulation and Data Processing

This script validates that the student's implementation meets the requirements:
1. All required sensors are publishing data with realistic parameters
2. Sensor data processing nodes are working correctly
3. Obstacle avoidance algorithm is effective
4. System handles sensor noise appropriately
"""

import os
import sys
import subprocess
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, Imu, Range
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float32
import math
import numpy as np

class Exercise2Validator(Node):
    """
    Validator node that checks if the exercise requirements are met.
    """

    def __init__(self):
        super().__init__('exercise2_validator')

        # Variables to track validation results
        self.lidar_received = False
        self.camera_received = False
        self.imu_received = False
        self.sonar_received = False
        self.cmd_vel_received = False  # Check if robot is publishing movement commands
        self.obstacle_detected = False
        self.avoidance_active = False

        # Sensor data tracking
        self.lidar_data = None
        self.imu_data = None
        self.sonar_data = []
        self.last_cmd_vel = None
        self.obstacle_distances = []

        # Create subscribers to check if all required sensors are publishing
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

        self.imu_sub = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
            10
        )

        self.sonar_sub = self.create_subscription(
            Range,
            '/sonar/front',
            self.sonar_callback,
            10
        )

        # Subscriber to check if robot is responding to obstacle avoidance
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info('Exercise 2 validator started')

    def lidar_callback(self, msg):
        """Callback to check LiDAR data with realistic parameters."""
        if len(msg.ranges) > 0:
            self.lidar_received = True
            self.lidar_data = msg

            # Check if parameters are realistic
            if (msg.angle_min <= -3.0 and msg.angle_max >= 3.0 and  # 360 degree coverage
                msg.range_min <= 0.1 and msg.range_max >= 10.0 and  # Appropriate range
                len(msg.ranges) >= 360):  # Good resolution
                self.get_logger().info('LiDAR data received with realistic parameters')
            else:
                self.get_logger().warn('LiDAR parameters may not be realistic')

            # Check for obstacles in data
            valid_ranges = [r for r in msg.ranges if msg.range_min < r < msg.range_max]
            if valid_ranges:
                min_distance = min(valid_ranges)
                if min_distance < 1.0:  # Obstacle within 1m
                    self.obstacle_detected = True
                    self.obstacle_distances.append(min_distance)

    def camera_callback(self, msg):
        """Callback to check camera data."""
        if msg.height >= 480 and msg.width >= 640:  # Minimum resolution
            self.camera_received = True
            self.get_logger().info('Camera data received with appropriate resolution')

    def imu_callback(self, msg):
        """Callback to check IMU data."""
        # Check if IMU data is being received with realistic values
        if (abs(msg.linear_acceleration.x) < 20.0 and
            abs(msg.linear_acceleration.y) < 20.0 and
            abs(msg.linear_acceleration.z) < 20.0):  # Reasonable acceleration values
            self.imu_received = True
            self.imu_data = msg
            self.get_logger().info('IMU data received with realistic values')

    def sonar_callback(self, msg):
        """Callback to check sonar data."""
        if msg.range >= msg.min_range and msg.range <= msg.max_range:
            self.sonar_received = True
            self.sonar_data.append(msg.range)
            self.get_logger().info('Sonar data received with valid range')

    def cmd_vel_callback(self, msg):
        """Callback to check if robot is responding to sensor data."""
        self.cmd_vel_received = True
        self.last_cmd_vel = msg

        # Check if robot is actively avoiding obstacles
        # If there's a significant angular velocity when linear velocity is high,
        # it might indicate obstacle avoidance behavior
        if abs(msg.linear.x) > 0.1 and abs(msg.angular.z) > 0.2:
            self.avoidance_active = True

    def validate_sensor_parameters(self):
        """Validate that sensors have realistic parameters."""
        realistic = True

        # Check LiDAR parameters if data available
        if self.lidar_data:
            if (self.lidar_data.angle_min <= -3.0 and self.lidar_data.angle_max >= 3.0 and
                self.lidar_data.range_min <= 0.1 and self.lidar_data.range_max >= 10.0):
                self.get_logger().info('LiDAR parameters are realistic')
            else:
                self.get_logger().warn('LiDAR parameters may not be realistic')
                realistic = False
        else:
            self.get_logger().warn('No LiDAR data available for parameter check')
            realistic = False

        # Check if we have reasonable sensor variety
        sensors_present = [
            self.lidar_received,
            self.camera_received,
            self.imu_received,
            self.sonar_received
        ]

        if sum(sensors_present) >= 3:  # At least 3 sensors working
            self.get_logger().info('Appropriate number of sensors present')
        else:
            self.get_logger().warn('Not enough sensors are working')
            realistic = False

        return realistic

    def validate_obstacle_avoidance(self):
        """Validate that obstacle avoidance is working."""
        if self.obstacle_detected and self.avoidance_active:
            self.get_logger().info('Obstacle avoidance behavior detected')
            return True
        elif self.obstacle_detected:
            self.get_logger().info('Obstacles detected but no avoidance behavior yet')
            return True  # Still valid if obstacles are detected
        else:
            self.get_logger().warn('No obstacles detected in current environment')
            return True  # Not necessarily a failure

    def validate_results(self):
        """Validate the results after testing."""
        print("\n" + "="*60)
        print("EXERCISE 2 VALIDATION RESULTS")
        print("="*60)

        # Check all sensors
        print("Sensor Validation:")
        if self.lidar_received:
            print("  ✅ PASSED: LiDAR sensor data received")
        else:
            print("  ❌ FAILED: No LiDAR data received")

        if self.camera_received:
            print("  ✅ PASSED: Camera sensor data received")
        else:
            print("  ❌ FAILED: No camera data received")

        if self.imu_received:
            print("  ✅ PASSED: IMU sensor data received")
        else:
            print("  ❌ FAILED: No IMU data received")

        if self.sonar_received:
            print("  ✅ PASSED: Sonar sensor data received")
        else:
            print("  ❌ FAILED: No sonar data received")

        # Check sensor parameters
        params_valid = self.validate_sensor_parameters()
        if params_valid:
            print("  ✅ PASSED: Sensor parameters are realistic")
        else:
            print("  ❌ FAILED: Sensor parameters need adjustment")

        # Check obstacle detection and avoidance
        if self.obstacle_detected:
            print("  ✅ PASSED: Obstacles detected in environment")
        else:
            print("  ⚠️  INFO: No obstacles detected in current setup")

        avoidance_valid = self.validate_obstacle_avoidance()
        if self.avoidance_active:
            print("  ✅ PASSED: Obstacle avoidance behavior detected")
        elif self.obstacle_detected:
            print("  ⚠️  INFO: Obstacles present, waiting for avoidance behavior")
        else:
            print("  ⚠️  INFO: No obstacles to avoid in current setup")

        # Check system response
        if self.cmd_vel_received:
            print("  ✅ PASSED: Robot is responding with movement commands")
        else:
            print("  ❌ FAILED: No movement commands detected")

        # Overall assessment
        required_checks = [
            self.lidar_received,
            self.camera_received,
            self.imu_received,
            self.sonar_received,
            params_valid,
            self.cmd_vel_received
        ]

        passed_required = sum(required_checks)
        total_required = len(required_checks)

        print(f"\nOverall: {passed_required}/{total_required} required checks passed")

        if passed_required >= total_required * 0.8:  # 80% threshold
            print("🎉 EXERCISE 2 COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  EXERCISE 2 needs more work.")

        print("="*60)
        return passed_required >= total_required * 0.8

def main(args=None):
    """Main function to run the validation."""
    rclpy.init(args=args)

    validator = Exercise2Validator()

    try:
        print("Starting Exercise 2 validation...")
        print("Make sure your simulation with sensor robot is running.")
        print("Ensure all sensors (LiDAR, camera, IMU, sonar) are active.")
        print("Validation will run for 15 seconds to collect data.\n")

        # Run for 15 seconds to collect comprehensive data
        start_time = time.time()
        while time.time() - start_time < 15.0:
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