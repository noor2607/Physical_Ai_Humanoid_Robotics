# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/sensor_processor.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2
from std_msgs.msg import Float32MultiArray
import numpy as np
from typing import List, Tuple


class SensorProcessor(Node):
    """
    Processes sensor data and extracts meaningful information.
    """

    def __init__(self):
        super().__init__('sensor_processor')

        # Create subscribers
        self.scan_subscriber = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        # Create publishers
        self.obstacle_publisher = self.create_publisher(Float32MultiArray, '/obstacles', 10)
        self.free_space_publisher = self.create_publisher(Float32MultiArray, '/free_space', 10)

        # Initialize processing parameters
        self.angle_increment = None
        self.get_logger().info('Sensor processor initialized')

    def scan_callback(self, msg: LaserScan):
        """Process incoming laser scan data."""
        self.angle_increment = msg.angle_increment

        # Convert scan ranges to Cartesian coordinates
        points = self.scan_to_cartesian(msg)

        # Process points to find obstacles and free space
        obstacles, free_space = self.process_environment(points)

        # Publish results
        self.publish_obstacles(obstacles)
        self.publish_free_space(free_space)

    def scan_to_cartesian(self, scan_msg: LaserScan) -> List[Tuple[float, float]]:
        """Convert laser scan ranges to Cartesian coordinates."""
        points = []
        angle = scan_msg.angle_min

        for range_val in scan_msg.ranges:
            if not (float('inf') == range_val or float('-inf') == range_val or
                    range_val != range_val):  # Check for inf and NaN
                x = range_val * np.cos(angle)
                y = range_val * np.sin(angle)
                points.append((x, y))
            angle += scan_msg.angle_increment

        return points

    def process_environment(self, points: List[Tuple[float, float]]) -> Tuple[List, List]:
        """Process environment to identify obstacles and free space."""
        # Simple clustering to identify obstacles
        obstacles = []
        free_space = []

        # For demonstration, just categorize points
        for x, y in points:
            distance = np.sqrt(x**2 + y**2)
            if distance < 1.0:  # Close points are obstacles
                obstacles.append((x, y, distance))
            else:  # Far points are free space
                free_space.append((x, y, distance))

        return obstacles, free_space

    def publish_obstacles(self, obstacles: List):
        """Publish obstacle information."""
        if not obstacles:
            return

        msg = Float32MultiArray()
        # Flatten obstacle data into array
        msg.data = [item for sublist in obstacles for item in sublist]
        self.obstacle_publisher.publish(msg)

    def publish_free_space(self, free_space: List):
        """Publish free space information."""
        if not free_space:
            return

        msg = Float32MultiArray()
        # Flatten free space data into array
        msg.data = [item for sublist in free_space for item in sublist]
        self.free_space_publisher.publish(msg)


def main(args=None):
    """Main function for sensor processor."""
    rclpy.init(args=args)

    try:
        processor = SensorProcessor()
        rclpy.spin(processor)
    except KeyboardInterrupt:
        print('Sensor processor interrupted')
    finally:
        if 'processor' in locals():
            processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()