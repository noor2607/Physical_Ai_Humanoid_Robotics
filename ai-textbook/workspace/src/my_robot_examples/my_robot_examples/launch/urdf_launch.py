# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/launch/urdf_launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare launch arguments
    urdf_model_path = LaunchConfiguration('urdf_model')
    use_rviz = LaunchConfiguration('use_rviz')

    declare_urdf_model_path = DeclareLaunchArgument(
        name='urdf_model',
        default_value=PathJoinSubstitution(
            [FindPackageShare('my_robot_examples'), 'urdf', 'simple_robot.urdf']
        ),
        description='Absolute path to robot urdf file'
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='True',
        description='Whether to start RVIZ'
    )

    # Launch the robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': PathJoinSubstitution(
            [FindPackageShare('my_robot_examples'), 'urdf', 'simple_robot.urdf']
        )}]
    )

    # Launch the joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )

    # Launch RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # Create launch description
    ld = LaunchDescription()

    # Add the actions
    ld.add_action(declare_urdf_model_path)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(rviz_node)

    return ld