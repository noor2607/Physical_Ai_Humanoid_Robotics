---
sidebar_position: 3
title: "Chapter 7: Sensor Simulation"
---

# Chapter 7: Sensor Simulation

## Introduction to Sensor Simulation

Sensor simulation is a critical component of realistic robot simulation. In this chapter, we'll explore how to simulate various types of sensors in Gazebo, including cameras, LiDAR, IMU, and other sensors commonly used in robotics. Proper sensor simulation allows you to test perception algorithms and sensor fusion techniques before deploying to physical hardware.

## Types of Sensors in Gazebo

### Camera Sensors

Camera sensors simulate RGB cameras and can be configured with various parameters:

```xml
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov> <!-- 60 degrees in radians -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <visualize>true</visualize>
</sensor>
```

### LiDAR Sensors

LiDAR sensors simulate laser range finders and can be configured as ray sensors:

```xml
<sensor name="lidar" type="ray">
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1.0</resolution>
        <min_angle>-3.14159</min_angle>  <!-- -π -->
        <max_angle>3.14159</max_angle>    <!-- π -->
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>30.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <always_on>true</always_on>
  <update_rate>10</update_rate>
  <visualize>true</visualize>
</sensor>
```

### IMU Sensors

IMU sensors simulate inertial measurement units:

```xml
<sensor name="imu" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <visualize>false</visualize>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>2e-4</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>1.7e-2</stddev>
        </noise>
      </z>
    </linear_acceleration>
  </imu>
</sensor>
```

## ROS 2 Integration

Gazebo sensors can be easily integrated with ROS 2 using the `gazebo_ros` packages:

```xml
<sensor name="camera" type="camera">
  <!-- Camera configuration -->
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <frame_name>camera_frame</frame_name>
    <topic_name>image_raw</topic_name>
    <hack_baseline>0.07</hack_baseline>
  </plugin>
</sensor>
```

## Sensor Noise and Realism

Real sensors have noise and imperfections that should be simulated for realistic testing:

### Adding Noise to Sensors

```xml
<sensor name="camera" type="camera">
  <camera>
    <!-- Camera configuration -->
  </camera>
  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.007</stddev>
  </noise>
</sensor>
```

## Example: Complete Robot with Sensors

Here's an example of a simple robot model with multiple sensors:

```xml
<?xml version="1.0" ?>
<robot name="sensor_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.2" radius="0.15"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.2" radius="0.15"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Camera Mount -->
  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.1 0 0.1" rpy="0 0 0"/>
  </joint>

  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </visual>
  </link>

  <!-- Camera Sensor -->
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <update_rate>30</update_rate>
      <camera name="head">
        <horizontal_fov>1.3962634</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.02</near>
          <far>300</far>
        </clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <frame_name>camera_link</frame_name>
        <topic_name>camera/image_raw</topic_name>
      </plugin>
    </sensor>
  </gazebo>

  <!-- LiDAR Mount -->
  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
  </joint>

  <link name="lidar_link">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.05"/>
      </geometry>
    </visual>
  </link>

  <!-- LiDAR Sensor -->
  <gazebo reference="lidar_link">
    <sensor name="lidar" type="ray">
      <ray>
        <scan>
          <horizontal>
            <samples>360</samples>
            <resolution>1</resolution>
            <min_angle>-3.14159</min_angle>
            <max_angle>3.14159</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.1</min>
          <max>30.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
        <topic_name>scan</topic_name>
        <frame_name>lidar_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

## Sensor Data Processing

Once sensors are simulated, you can process their data in ROS 2 nodes:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from cv_bridge import CvBridge
import cv2

class SensorProcessor(Node):
    def __init__(self):
        super().__init__('sensor_processor')

        # Initialize CvBridge for image processing
        self.bridge = CvBridge()

        # Subscribe to camera topic
        self.camera_sub = self.create_subscription(
            Image,
            'camera/image_raw',
            self.camera_callback,
            10)

        # Subscribe to LiDAR topic
        self.lidar_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.lidar_callback,
            10)

        self.get_logger().info('Sensor processor initialized')

    def camera_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Process the image (example: detect edges)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Display the processed image
        cv2.imshow('Camera View', cv_image)
        cv2.imshow('Edges', edges)
        cv2.waitKey(1)

    def lidar_callback(self, msg):
        # Process LiDAR data
        ranges = msg.ranges
        min_range = min(ranges) if ranges else float('inf')

        if min_range < 1.0:  # If obstacle is closer than 1 meter
            self.get_logger().warn(f'Obstacle detected at {min_range:.2f} meters!')

def main(args=None):
    rclpy.init(args=args)

    processor = SensorProcessor()

    try:
        rclpy.spin(processor)
    except KeyboardInterrupt:
        pass
    finally:
        processor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices for Sensor Simulation

1. **Match Real Sensor Specifications**: Configure simulation parameters to match your real sensors as closely as possible
2. **Include Noise Models**: Add realistic noise to sensor data to better reflect real-world conditions
3. **Validate with Real Data**: Compare simulation sensor output with real sensor data when possible
4. **Consider Computational Cost**: Balance sensor realism with simulation performance
5. **Test Edge Cases**: Use simulation to test sensor behavior in challenging conditions that might be difficult to reproduce with real hardware

## Exercise

Create a robot model with both a camera and LiDAR sensor, spawn it in a Gazebo world, and write a ROS 2 node that processes both sensor streams simultaneously to detect obstacles and navigate around them.

## Summary

Sensor simulation is crucial for realistic robot testing and validation. By properly configuring sensor models with appropriate noise characteristics and parameters, you can develop and test perception algorithms in a safe, repeatable environment before deploying to physical hardware.