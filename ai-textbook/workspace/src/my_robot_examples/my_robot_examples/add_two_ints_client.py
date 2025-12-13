# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/add_two_ints_client.py
import sys
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):

    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsClient()

    try:
        a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        b = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        response = node.send_request(a, b)
        node.get_logger().info(f'Result of {a} + {b} = {response.sum}')
    except Exception as e:
        node.get_logger().error(f'Service call failed: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()