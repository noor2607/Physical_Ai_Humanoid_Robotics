---
sidebar_position: 4
title: "Chapter 8: Environment Setup"
---

# Chapter 8: Environment Setup

## Introduction to Simulation Environments

Creating realistic simulation environments is crucial for testing robotic systems before deployment to the physical world. In this chapter, we'll explore how to design, build, and configure complex simulation environments in Gazebo that accurately represent real-world scenarios. We'll cover everything from simple indoor environments to complex outdoor worlds with multiple robots and dynamic elements.

## Environment Design Principles

### Realism vs. Performance Trade-offs

When designing simulation environments, you need to balance:
- **Visual realism**: Detailed models and textures
- **Physics accuracy**: Complex collision meshes and realistic parameters
- **Performance**: Simulation speed and computational requirements

### Modularity

Design environments in modular components that can be:
- Reused across different scenarios
- Easily modified and updated
- Combined to create complex worlds

## Creating Complex Worlds

### Indoor Environments

Let's create a more complex indoor environment with furniture, obstacles, and navigation challenges:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="office_world">
    <!-- Include default environment elements -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Walls -->
    <model name="wall_1">
      <pose>0 5 1 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Furniture: Table -->
    <model name="table">
      <pose>2 2 0.5 0 0 0</pose>
      <link name="table_top">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.5 0.8 0.02</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.5 0.8 0.02</size>
            </box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      <link name="leg_1">
        <pose>-0.6 -0.35 0 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.9</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.9</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.3 0.2 0.1 1</ambient>
            <diffuse>0.3 0.2 0.1 1</diffuse>
          </material>
        </visual>
      </link>
      <!-- Additional legs... -->
    </model>

    <!-- Obstacles: Boxes -->
    <model name="obstacle_1">
      <pose>-3 -2 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.5 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Navigation goal -->
    <model name="goal_marker">
      <pose>4 4 0.05 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.3</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.3</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0 1 0 0.5</ambient>
            <diffuse>0 1 0 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Physics configuration -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
  </world>
</sdf>
```

## Using Model Libraries

Gazebo provides a library of pre-built models that can be included in your worlds:

```xml
<!-- Include a simple robot from the model database -->
<include>
  <uri>model://wheeled_robot</uri>
  <pose>1 1 0 0 0 0</pose>
</include>

<!-- Include a complex building -->
<include>
  <uri>model://simple_building</uri>
  <pose>-5 0 0 0 0 0</pose>
</include>
```

## Creating Custom Models

### Model Structure

A Gazebo model follows this structure:

```
~/.gazebo/models/model_name/
├── model.config
└── mesh/
    ├── visual/
    └── collision/
```

### model.config File

```xml
<?xml version="1.0"?>
<model>
  <name>custom_robot</name>
  <version>1.0</version>
  <sdf version="1.7">model.sdf</sdf>

  <author>
    <name>Your Name</name>
    <email>your.email@example.com</email>
  </author>

  <description>
    A custom robot model for simulation.
  </description>
</model>
```

## Dynamic Environments

### Moving Obstacles

You can create moving obstacles using joints and controllers:

```xml
<model name="moving_obstacle">
  <link name="base_link">
    <visual name="visual">
      <geometry>
        <sphere>
          <radius>0.2</radius>
        </sphere>
      </geometry>
    </visual>
    <collision name="collision">
      <geometry>
        <sphere>
          <radius>0.2</radius>
        </sphere>
      </geometry>
    </collision>
  </link>

  <!-- Attach to a moving platform -->
  <joint name="obstacle_joint" type="prismatic">
    <parent>world</parent>
    <child>base_link</child>
    <axis>
      <xyz>1 0 0</xyz>
      <limit>
        <lower>-5</lower>
        <upper>5</upper>
        <effort>100</effort>
        <velocity>1</velocity>
      </limit>
    </axis>
  </joint>

  <plugin name="joint_controller" filename="libgazebo_ros_joint_pose_trajectory.so">
    <command_topic>joint_trajectory</command_topic>
    <joint_name>obstacle_joint</joint_name>
  </plugin>
</model>
```

## Environment Configuration with ROS 2

### Launch Files for Environment Setup

Create a launch file to start Gazebo with your environment:

```python
#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch Gazebo with custom world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('my_robot_simulation'),
                'worlds',
                'office_world.sdf'
            ])
        }.items()
    )

    # Spawn robot in the world
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'my_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_entity
    ])
```

## Lighting and Atmospheric Effects

### Custom Lighting

Configure lighting for your environment:

```xml
<world name="custom_lighting_world">
  <!-- Custom sun -->
  <light name="custom_sun" type="directional">
    <pose>0 0 10 0 0 0</pose>
    <diffuse>0.8 0.8 0.8 1</diffuse>
    <specular>0.2 0.2 0.2 1</specular>
    <attenuation>
      <range>1000</range>
      <constant>0.9</constant>
      <linear>0.01</linear>
      <quadratic>0.001</quadratic>
    </attenuation>
    <direction>-0.3 0.3 -1</direction>
  </light>

  <!-- Point lights for indoor environments -->
  <light name="room_light" type="point">
    <pose>0 0 3 0 0 0</pose>
    <diffuse>1 1 1 1</diffuse>
    <specular>0.5 0.5 0.5 1</specular>
    <attenuation>
      <range>10</range>
      <constant>0.5</constant>
      <linear>0.1</linear>
      <quadratic>0.01</quadratic>
    </attenuation>
  </light>
</world>
```

## Multi-Robot Environments

### Coordinating Multiple Robots

Create environments with multiple robots:

```xml
<!-- First robot -->
<model name="robot1">
  <pose>1 1 0 0 0 0</pose>
  <!-- Robot definition -->
</model>

<!-- Second robot -->
<model name="robot2">
  <pose>-1 1 0 0 0 0</pose>
  <!-- Robot definition -->
</model>

<!-- Communication between robots -->
<plugin name="multi_robot_comm" filename="libgazebo_ros_multicamera.so">
  <robot_namespace>robot1</robot_namespace>
</plugin>
```

## Environment Validation

### Testing Environment Realism

Validate your environments by:
1. Testing robot navigation in the simulation
2. Comparing sensor data from simulation vs. real hardware
3. Checking physics behavior against real-world expectations
4. Measuring simulation performance

## Best Practices for Environment Setup

1. **Start Simple**: Begin with basic environments and gradually add complexity
2. **Use Realistic Models**: Incorporate models that closely match real-world objects
3. **Consider Performance**: Balance visual quality with simulation speed
4. **Document Environments**: Keep detailed documentation of environment configurations
5. **Version Control**: Store environment files in version control alongside your robot code
6. **Test Scenarios**: Create environments that test specific robot capabilities
7. **Safety Boundaries**: Include safety zones and boundaries to prevent robots from getting lost

## Exercise

Create a warehouse simulation environment with multiple aisles, shelves, and moving obstacles. Add realistic lighting and include at least one robot that can navigate through the environment while avoiding obstacles. Implement a task where the robot must navigate to multiple waypoints in sequence.

## Summary

Creating realistic simulation environments is essential for effective robot testing and development. By carefully designing worlds with appropriate physics, lighting, and obstacles, you can validate robotic algorithms in a safe, repeatable environment before deployment to physical hardware. The modular approach allows for reusable components and scalable environment development.