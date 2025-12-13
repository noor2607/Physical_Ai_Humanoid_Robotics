# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/parameter_node.py
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String


class ParameterNode(Node):

    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with descriptions
        self.declare_parameter('robot_name', 'my_robot',
                              'Name of the robot for identification')
        self.declare_parameter('max_speed', 1.0,
                              'Maximum speed of the robot in m/s')
        self.declare_parameter('sensor_enabled', True,
                              'Whether the sensor system is enabled')

        # Get parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.max_speed = self.get_parameter('max_speed').value
        self.sensor_enabled = self.get_parameter('sensor_enabled').value

        # Create publisher for status updates
        self.status_publisher = self.create_publisher(String, 'robot_status', 10)

        # Set up timer for periodic status updates
        self.timer = self.create_timer(1.0, self.status_callback)

        self.get_logger().info(
            f'Initialized with: name={self.robot_name}, '
            f'speed={self.max_speed}, sensor_enabled={self.sensor_enabled}')

    def status_callback(self):
        msg = String()
        msg.data = f'{self.robot_name} running at {self.max_speed} m/s'
        self.status_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()