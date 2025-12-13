# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/robot_controller.py
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String, Float32
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


class RobotController(Node):
    """
    A comprehensive robot controller node demonstrating Python best practices.
    """

    def __init__(self):
        super().__init__('robot_controller')

        # Declare parameters with descriptions
        self.declare_parameter('linear_speed', 0.5,
                              'Linear speed for robot movement')
        self.declare_parameter('angular_speed', 1.0,
                              'Angular speed for robot rotation')
        self.declare_parameter('safety_distance', 0.5,
                              'Minimum distance to obstacles')

        # Get parameter values
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        self.safety_distance = self.get_parameter('safety_distance').value

        # Set up QoS profiles for different types of data
        sensor_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST
        )

        cmd_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST
        )

        # Create publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', cmd_qos)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)

        # Create subscribers
        self.scan_subscriber = self.create_subscription(LaserScan, '/scan', self.scan_callback, sensor_qos)

        # Create timers
        self.control_timer = self.create_timer(0.1, self.control_loop)

        # Initialize robot state
        self.scan_data = None
        self.robot_state = 'idle'  # idle, moving, avoiding_obstacle
        self.get_logger().info('Robot controller initialized')

    def scan_callback(self, msg):
        """Process laser scan data."""
        self.scan_data = msg
        self.get_logger().debug(f'Received scan with {len(msg.ranges)} points')

    def control_loop(self):
        """Main control loop for robot navigation."""
        if self.scan_data is None:
            return

        # Determine minimum distance to obstacles
        valid_ranges = [r for r in self.scan_data.ranges
                       if not math.isnan(r) and r > 0]

        if not valid_ranges:
            self.get_logger().warn('No valid ranges in scan data')
            return

        min_distance = min(valid_ranges)

        # Create command message
        cmd_msg = Twist()

        if min_distance < self.safety_distance:
            # Obstacle detected, rotate to avoid
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = self.angular_speed
            self.robot_state = 'avoiding_obstacle'
        else:
            # Clear path, move forward
            cmd_msg.linear.x = self.linear_speed
            cmd_msg.angular.z = 0.0
            self.robot_state = 'moving'

        # Publish command
        self.cmd_vel_publisher.publish(cmd_msg)

        # Publish status
        status_msg = String()
        status_msg.data = f'State: {self.robot_state}, Distance: {min_distance:.2f}m'
        self.status_publisher.publish(status_msg)

        self.get_logger().info(f'{status_msg.data}', throttle_duration_sec=1)


def main(args=None):
    """Main function with proper error handling."""
    rclpy.init(args=args)

    try:
        robot_controller = RobotController()
        rclpy.spin(robot_controller)
    except KeyboardInterrupt:
        print('Interrupted by user')
    except Exception as e:
        print(f'Error occurred: {e}')
    finally:
        if 'robot_controller' in locals():
            robot_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()