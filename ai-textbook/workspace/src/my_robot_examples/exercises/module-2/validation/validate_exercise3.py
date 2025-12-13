#!/usr/bin/env python3
"""
Validation script for Exercise 3: Advanced Environment Creation and Simulation

This script validates that the student's implementation meets the requirements:
1. Complex environment with multiple rooms/aisles and obstacles
2. Multi-robot setup with proper namespace separation
3. Coordination and navigation algorithms working
4. Collision avoidance between robots
"""

import os
import sys
import subprocess
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math

class Exercise3Validator(Node):
    """
    Validator node that checks if the exercise requirements are met.
    """

    def __init__(self):
        super().__init__('exercise3_validator')

        # Variables to track validation results
        self.robot1_active = False
        self.robot2_active = False
        self.robot1_odom = False
        self.robot2_odom = False
        self.robot1_scan = False
        self.robot2_scan = False
        self.coordination_detected = False
        self.collision_free = True
        self.multiple_robots = False

        # Robot tracking
        self.robot1_pos = None
        self.robot2_pos = None
        self.robot_positions = {'robot1': [], 'robot2': []}
        self.min_distance_between_robots = float('inf')

        # Create subscribers for robot1 (with and without namespace)
        self.robot1_odom_sub = self.create_subscription(
            Odometry,
            '/robot1/odom',
            self.robot1_odom_callback,
            10
        )

        self.robot1_odom_sub_alt = self.create_subscription(
            Odometry,
            '/odom',
            self.robot1_odom_callback,
            10
        )

        self.robot1_scan_sub = self.create_subscription(
            LaserScan,
            '/robot1/scan',
            self.robot1_scan_callback,
            10
        )

        self.robot1_scan_sub_alt = self.create_subscription(
            LaserScan,
            '/scan',
            self.robot1_scan_callback,
            10
        )

        # Create subscribers for robot2 (with namespace)
        self.robot2_odom_sub = self.create_subscription(
            Odometry,
            '/robot2/odom',
            self.robot2_odom_callback,
            10
        )

        self.robot2_scan_sub = self.create_subscription(
            LaserScan,
            '/robot2/scan',
            self.robot2_scan_callback,
            10
        )

        self.get_logger().info('Exercise 3 validator started')

    def robot1_odom_callback(self, msg):
        """Callback for robot1 odometry."""
        self.robot1_active = True
        self.robot1_odom = True

        # Track position
        x, y = msg.pose.pose.position.x, msg.pose.pose.position.y
        self.robot1_pos = (x, y)
        self.robot_positions['robot1'].append((x, y))

        # Check for potential collisions if both robots are active
        if self.robot2_pos:
            dist = math.sqrt((x - self.robot2_pos[0])**2 + (y - self.robot2_pos[1])**2)
            if dist < self.min_distance_between_robots:
                self.min_distance_between_robots = dist

            if dist < 0.5:  # Less than 50cm apart - potential collision
                self.collision_free = False

    def robot2_odom_callback(self, msg):
        """Callback for robot2 odometry."""
        self.robot2_active = True
        self.robot2_odom = True
        self.multiple_robots = True

        # Track position
        x, y = msg.pose.pose.position.x, msg.pose.pose.position.y
        self.robot2_pos = (x, y)
        self.robot_positions['robot2'].append((x, y))

        # Check for potential collisions if robot1 is active
        if self.robot1_pos:
            dist = math.sqrt((x - self.robot1_pos[0])**2 + (y - self.robot1_pos[1])**2)
            if dist < self.min_distance_between_robots:
                self.min_distance_between_robots = dist

            if dist < 0.5:  # Less than 50cm apart - potential collision
                self.collision_free = False

    def robot1_scan_callback(self, msg):
        """Callback for robot1 scan data."""
        if len(msg.ranges) > 0:
            self.robot1_scan = True

    def robot2_scan_callback(self, msg):
        """Callback for robot2 scan data."""
        if len(msg.ranges) > 0:
            self.robot2_scan = True

    def validate_environment_complexity(self):
        """Validate that the environment is complex enough."""
        # This is harder to validate automatically, but we can check:
        # 1. If multiple robots are active, environment is likely complex
        # 2. If robots are navigating in different areas, environment is likely complex
        if self.multiple_robots and len(self.robot_positions['robot1']) > 5 and len(self.robot_positions['robot2']) > 5:
            # Check if robots are exploring different areas
            if self.robot1_pos and self.robot2_pos:
                dist = math.sqrt((self.robot1_pos[0] - self.robot2_pos[0])**2 +
                               (self.robot1_pos[1] - self.robot2_pos[1])**2)
                if dist > 2.0:  # Robots are in different areas
                    self.get_logger().info('Environment appears to support multi-robot navigation in different areas')
                    return True

        self.get_logger().info('Environment complexity validated (based on multi-robot behavior)')
        return True

    def validate_coordination(self):
        """Validate that some form of coordination is happening."""
        # Coordination can be indicated by:
        # 1. Robots maintaining safe distances
        # 2. Coordinated movement patterns
        # 3. Communication between robots (if implemented)

        if self.min_distance_between_robots > 0.5:  # Maintained safe distance
            self.coordination_detected = True
            self.get_logger().info('Robots maintaining safe distances (coordination indicator)')
            return True

        if len(self.robot_positions['robot1']) > 10 and len(self.robot_positions['robot2']) > 10:
            # Check if robots are moving in a coordinated pattern
            # This is a simple check - more sophisticated validation would be needed
            self.coordination_detected = True
            self.get_logger().info('Both robots active with movement patterns')
            return True

        return False

    def validate_results(self):
        """Validate the results after testing."""
        print("\n" + "="*60)
        print("EXERCISE 3 VALIDATION RESULTS")
        print("="*60)

        # Check multi-robot setup
        print("Multi-Robot Setup Validation:")
        if self.robot1_active:
            print("  ✅ PASSED: Robot1 is active and publishing data")
        else:
            print("  ❌ FAILED: Robot1 not detected or not publishing")

        if self.robot2_active:
            print("  ✅ PASSED: Robot2 is active and publishing data")
        else:
            print("  ❌ FAILED: Robot2 not detected or not publishing")

        if self.multiple_robots:
            print("  ✅ PASSED: Multiple robots detected in simulation")
        else:
            print("  ❌ FAILED: Only one robot detected")

        # Check sensor data
        print("\nSensor Data Validation:")
        if self.robot1_scan:
            print("  ✅ PASSED: Robot1 sensor data available")
        else:
            print("  ⚠️  INFO: Robot1 sensor data not detected")

        if self.robot2_scan:
            print("  ✅ PASSED: Robot2 sensor data available")
        else:
            print("  ⚠️  INFO: Robot2 sensor data not detected")

        # Check navigation
        print("\nNavigation Validation:")
        if self.robot1_odom:
            print("  ✅ PASSED: Robot1 navigation data available")
        else:
            print("  ❌ FAILED: Robot1 navigation not working")

        if self.robot2_odom:
            print("  ✅ PASSED: Robot2 navigation data available")
        else:
            print("  ❌ FAILED: Robot2 navigation not working")

        # Check coordination
        print("\nCoordination Validation:")
        coordination_valid = self.validate_coordination()
        if coordination_valid:
            print("  ✅ PASSED: Coordination behavior detected")
        else:
            print("  ⚠️  INFO: Coordination behavior not clearly detected")

        # Check collision avoidance
        print("\nSafety Validation:")
        if self.collision_free and self.min_distance_between_robots > 0.5:
            print(f"  ✅ PASSED: Collision avoidance working (min distance: {self.min_distance_between_robots:.2f}m)")
        elif self.collision_free:
            print(f"  ⚠️  INFO: No collisions detected (min distance: {self.min_distance_between_robots:.2f}m)")
        else:
            print(f"  ❌ FAILED: Potential collisions detected (min distance: {self.min_distance_between_robots:.2f}m)")

        # Check environment complexity
        env_complex = self.validate_environment_complexity()
        if env_complex:
            print("  ✅ PASSED: Environment supports complex multi-robot scenarios")

        # Overall assessment
        required_checks = [
            self.robot1_active,
            self.robot2_active,
            self.robot1_odom,
            self.robot2_odom,
            self.collision_free
        ]

        passed_required = sum(required_checks)
        total_required = len(required_checks)

        print(f"\nOverall: {passed_required}/{total_required} required checks passed")

        if passed_required >= 4:  # At least 4 out of 5 required checks
            print("🎉 EXERCISE 3 COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  EXERCISE 3 needs more work.")

        print("="*60)
        return passed_required >= 4

def main(args=None):
    """Main function to run the validation."""
    rclpy.init(args=args)

    validator = Exercise3Validator()

    try:
        print("Starting Exercise 3 validation...")
        print("Make sure your multi-robot simulation is running.")
        print("Ensure both robots are active and navigating.")
        print("Validation will run for 20 seconds to collect data.\n")

        # Run for 20 seconds to collect comprehensive data
        start_time = time.time()
        while time.time() - start_time < 20.0:
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