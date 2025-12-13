---
sidebar_position: 6
title: "Chapter 5: URDF - Creating Robot Models"
---

# Chapter 5: URDF - Creating Robot Models

## Overview

In this chapter, you'll learn about URDF (Unified Robot Description Format), the XML-based format used in ROS to describe robot models. URDF allows you to define the physical structure of robots, including links, joints, inertial properties, visual representations, and collision properties.

## Learning Objectives

After completing this chapter, you will be able to:
- Create URDF files to describe robot models
- Define links, joints, and their properties
- Add visual and collision meshes to robot models
- Use Xacro macros to simplify complex URDFs
- Visualize robot models in RViz
- Integrate URDF models with robot state publishers

## Understanding URDF

URDF (Unified Robot Description Format) is an XML format used to describe robots in ROS. It defines:
- **Links**: Rigid bodies of the robot (e.g., chassis, arms, wheels)
- **Joints**: Connections between links (e.g., revolute, prismatic, fixed)
- **Visual Elements**: How the robot appears in simulation and visualization
- **Collision Elements**: How the robot interacts with the environment physically
- **Inertial Properties**: Mass, center of mass, and inertia tensor for physics simulation

## Basic URDF Structure

A basic URDF file has the following structure:

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- Links -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="fixed_joint" type="fixed">
    <parent link="base_link"/>
    <child link="sensor_link"/>
  </joint>

  <link name="sensor_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
    </visual>
  </link>
</robot>
```

## Creating a Simple Robot Model

Let's create a simple differential drive robot model. Create the following file:

```xml
<!-- File: ~/ai-textbook/workspace/src/my_robot_examples/urdf/simple_robot.urdf -->
<?xml version="1.0"?>
<robot name="simple_diff_drive_robot">

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
      <material name="green">
        <color rgba="0 0.8 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.5" iyz="0.0" izz="2.0"/>
    </inertial>
  </link>

  <!-- Left wheel -->
  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Right wheel -->
  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.1" length="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
    </inertial>
  </link>

  <!-- Castor wheel -->
  <link name="caster_wheel">
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="left_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="-0.1 0.25 -0.1" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="right_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="-0.1 -0.25 -0.1" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
  </joint>

  <joint name="caster_wheel_joint" type="fixed">
    <parent link="base_link"/>
    <child link="caster_wheel"/>
    <origin xyz="0.2 0 -0.15"/>
  </joint>

</robot>
```

## Installing and Using Joint State Publisher

To visualize the robot properly, we need to publish joint states. Let's create a launch file that includes the robot state publisher:

```python
# File: ~/ai-textbook/workspace/src/my_robot_examples/my_robot_examples/robot_state_publisher_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math


class RobotStatePublisher(Node):
    """
    Simple robot state publisher for the simple robot model.
    """

    def __init__(self):
        super().__init__('robot_state_publisher')

        # Create publisher for joint states
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Create timer to publish joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)

        # Initialize joint positions
        self.time = 0.0
        self.get_logger().info('Robot state publisher started')

    def publish_joint_states(self):
        # Create joint state message
        msg = JointState()
        msg.name = ['left_wheel_joint', 'right_wheel_joint']
        msg.position = [math.sin(self.time), math.cos(self.time)]
        msg.velocity = [math.cos(self.time), -math.sin(self.time)]
        msg.effort = [0.0, 0.0]

        # Add header
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Publish message
        self.joint_pub.publish(msg)

        # Increment time
        self.time += 0.1


def main(args=None):
    rclpy.init(args=args)

    try:
        publisher = RobotStatePublisher()
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        pass
    finally:
        if 'publisher' in locals():
            publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Visualizing URDF Models

### Using RViz

To visualize your URDF model in RViz:

1. Launch the robot state publisher:
   ```bash
   ros2 run my_robot_examples robot_state_publisher_node
   ```

2. Launch RViz with a configuration that shows the robot:
   ```bash
   rviz2
   ```

3. In RViz:
   - Add a RobotModel display
   - Set the Robot Description to `/robot_description`
   - Set Fixed Frame to `base_link`

### Using Robot State Publisher

For static URDF visualization, you can use the robot_state_publisher package:

```bash
# Launch robot state publisher with URDF
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(cat urdf/simple_robot.urdf)'
```

## Understanding Joint Types

URDF supports several joint types:

### Fixed Joint
- No degrees of freedom
- Connects two links rigidly
```xml
<joint name="fixed_joint" type="fixed">
  <parent link="link1"/>
  <child link="link2"/>
</joint>
```

### Revolute Joint
- Single rotational degree of freedom
- Limited range of motion
```xml
<joint name="revolute_joint" type="revolute">
  <parent link="link1"/>
  <child link="link2"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
</joint>
```

### Continuous Joint
- Single rotational degree of freedom
- Unlimited range of motion
```xml
<joint name="continuous_joint" type="continuous">
  <parent link="link1"/>
  <child link="link2"/>
  <axis xyz="0 0 1"/>
</joint>
```

### Prismatic Joint
- Single translational degree of freedom
- Limited range of motion
```xml
<joint name="prismatic_joint" type="prismatic">
  <parent link="link1"/>
  <child link="link2"/>
  <axis xyz="1 0 0"/>
  <limit lower="0" upper="0.5" effort="100" velocity="1"/>
</joint>
```

## Using Xacro to Simplify URDF

Xacro is a macro language that helps simplify complex URDF files. Create a Xacro version of our robot:

```xml
<!-- File: ~/ai-textbook/workspace/src/my_robot_examples/urdf/simple_robot.xacro -->
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="simple_diff_drive_robot_xacro">

  <!-- Constants -->
  <xacro:property name="PI" value="3.1415926535897931"/>

  <!-- Wheel macro -->
  <xacro:macro name="wheel" params="prefix reflect">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="0.1" length="0.05"/>
        </geometry>
        <material name="black">
          <color rgba="0 0 0 1"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="0.1" length="0.05"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.5"/>
        <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.002"/>
      </inertial>
    </link>

    <joint name="${prefix}_wheel_joint" type="continuous">
      <parent link="base_link"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="-0.1 ${reflect * 0.25} -0.1" rpy="${PI/2} 0 0"/>
      <axis xyz="0 0 1"/>
    </joint>
  </xacro:macro>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
      <material name="green">
        <color rgba="0 0.8 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.6 0.4 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.5" iyz="0.0" izz="2.0"/>
    </inertial>
  </link>

  <!-- Use the wheel macro -->
  <xacro:wheel prefix="left" reflect="1"/>
  <xacro:wheel prefix="right" reflect="-1"/>

  <!-- Castor wheel -->
  <link name="caster_wheel">
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.0001" ixy="0.0" ixz="0.0" iyy="0.0001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="caster_wheel_joint" type="fixed">
    <parent link="base_link"/>
    <child link="caster_wheel"/>
    <origin xyz="0.2 0 -0.15"/>
  </joint>

</robot>
```

## Loading Xacro Files

To load a Xacro file, you need to convert it to URDF first:

```bash
# Convert Xacro to URDF
xacro simple_robot.xacro > simple_robot_converted.urdf

# Or use in launch files with parameter server
ros2 param set /robot_state_publisher robot_description "$(xacro simple_robot.xacro)"
```

## Advanced URDF Features

### Transmission Elements
Define how actuators connect to joints:

```xml
<transmission name="left_wheel_trans">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_wheel_joint">
    <hardwareInterface>hardware_interface/VelocityJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_wheel_motor">
    <hardwareInterface>hardware_interface/VelocityJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

### Gazebo Extensions
Add Gazebo-specific properties:

```xml
<gazebo reference="base_link">
  <material>Gazebo/Green</material>
  <mu1>0.2</mu1>
  <mu2>0.2</mu2>
</gazebo>

<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>0.5</wheel_separation>
    <wheel_diameter>0.2</wheel_diameter>
  </plugin>
</gazebo>
```

## Creating a URDF Launch File

Create a launch file to load the robot model:

```python
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
        ).perform(None)}]
    )

    # Launch the joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )

    # Launch RViz
    rviz_node = Node(
        condition=launch.conditions.IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # Launch our custom robot state publisher
    custom_state_publisher = Node(
        package='my_robot_examples',
        executable='robot_state_publisher_node',
        name='custom_robot_state_publisher'
    )

    # Create launch description
    ld = LaunchDescription()

    # Add the actions
    ld.add_action(declare_urdf_model_path)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(rviz_node)
    ld.add_action(custom_state_publisher)

    return ld
```

## Testing URDF Models

### Checking URDF Syntax
```bash
# Check URDF for errors
check_urdf /path/to/robot.urdf

# Or with xacro
xacro /path/to/robot.xacro | check_urdf /dev/stdin
```

### Viewing URDF Tree
```bash
# View the URDF tree structure
urdf_to_graphiz /path/to/robot.urdf
```

## Summary

In this chapter, you learned how to create robot models using URDF, the XML-based format for describing robots in ROS. You created a simple differential drive robot model, learned about different joint types, and explored how to use Xacro to simplify complex URDFs. You also learned how to visualize robot models in RViz and integrate them with robot state publishers.

This completes Module 1: Robotic Nervous System (ROS 2). You now have a comprehensive understanding of ROS 2 fundamentals, from basic communication patterns to robot modeling.

## Practical Exercise

1. Create a URDF model for a simple robot arm with at least 3 joints
2. Use Xacro macros to simplify the URDF
3. Visualize your robot in RViz
4. Create a launch file that loads your robot model and displays it in RViz
5. Add Gazebo extensions to your URDF for simulation

## Resources

- [URDF Documentation](https://wiki.ros.org/urdf)
- [Xacro Documentation](https://wiki.ros.org/xacro)
- [Robot State Publisher](https://wiki.ros.org/robot_state_publisher)
- [RViz Visualization](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Getting-Started-With-Rviz/Getting-Started-With-Rviz.html)
- [Gazebo Integration](https://classic.gazebosim.org/tutorials?tut=ros2_overview)