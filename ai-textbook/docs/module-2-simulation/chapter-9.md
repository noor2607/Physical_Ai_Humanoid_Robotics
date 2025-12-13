---
sidebar_position: 5
title: "Chapter 9: Unity Visualization"
---

# Chapter 9: Unity Visualization

## Introduction to Unity for Robotics

Unity is a powerful 3D development platform that has become increasingly popular in robotics for advanced visualization and human-robot interaction. Unlike Gazebo which focuses on physics simulation, Unity excels at creating visually rich environments and intuitive user interfaces. In this chapter, we'll explore how to use Unity for robotics visualization and integrate it with ROS 2 for comprehensive simulation workflows.

## Unity in Robotics Applications

### Advantages of Unity for Robotics

- **High-quality graphics**: Photorealistic rendering capabilities
- **Intuitive UI/UX**: Easy-to-use interface for human-robot interaction
- **Cross-platform deployment**: Runs on multiple platforms including VR/AR
- **Rich asset ecosystem**: Extensive library of 3D models and environments
- **Real-time rendering**: High-performance visualization

### Unity vs. Gazebo

| Aspect | Gazebo | Unity |
|--------|--------|-------|
| Primary Focus | Physics Simulation | Visualization |
| Graphics Quality | Good | Excellent |
| Physics Accuracy | High | Moderate |
| UI/UX | Basic | Advanced |
| Learning Curve | Moderate | Steeper |
| Integration | ROS 2 native | Requires plugins |

## Setting Up Unity for Robotics

### Installing Unity Hub and Editor

1. Download Unity Hub from [Unity's website](https://unity.com/)
2. Install Unity Editor version 2022.3 LTS (recommended for robotics projects)
3. Install the "Desktop Game Development" module with Windows Build Support (if on Windows) or Linux Build Support

### Unity Robotics Hub

Unity provides a specialized package for robotics development:

1. Install the Unity Robotics Hub from the Unity Asset Store
2. This includes the ROS-TCP-Connector and other robotics-specific tools

## ROS 2 Integration with Unity

### Unity ROS TCP Connector

The ROS-TCP-Connector enables communication between Unity and ROS 2:

```csharp
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Std;

public class RobotController : MonoBehaviour
{
    ROSConnection ros;

    // ROS topic to send messages to
    string robotCommandTopic = "robot_command";

    void Start()
    {
        // Get the ROS connection static instance
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<UInt8Msg>(robotCommandTopic);
    }

    void Update()
    {
        // Example: Send a command when spacebar is pressed
        if (Input.GetKeyDown(KeyCode.Space))
        {
            UInt8Msg command = new UInt8Msg();
            command.data = 1; // Move forward command
            ros.Publish(robotCommandTopic, command);
        }
    }
}
```

### Receiving Messages from ROS 2

```csharp
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Geometry;

public class SensorVisualizer : MonoBehaviour
{
    ROSConnection ros;
    string sensorTopic = "sensor_data";

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.Subscribe<LaserScanMsg>(sensorTopic, SensorCallback);
    }

    void SensorCallback(LaserScanMsg scan)
    {
        // Process sensor data and visualize in Unity
        Debug.Log($"Received scan with {scan.ranges.Length} points");

        // Update visualization based on sensor data
        UpdateVisualization(scan);
    }

    void UpdateVisualization(LaserScanMsg scan)
    {
        // Update Unity objects based on sensor readings
        // For example, create visual representations of obstacles
    }
}
```

## Creating Robot Models in Unity

### Importing Robot Models

Unity can import robot models in various formats:
- **URDF**: Use the Unity Robotics Package to import URDF files
- **FBX/GLB**: Standard 3D model formats
- **STL**: For basic geometry

### Setting up Robot Joints and Kinematics

```csharp
using UnityEngine;

public class RobotArmController : MonoBehaviour
{
    public Transform[] joints; // Array of joint transforms
    public float[] jointAngles; // Current joint angles
    public float[] jointLimitsMin; // Minimum joint limits
    public float[] jointLimitsMax; // Maximum joint limits

    void Start()
    {
        jointAngles = new float[joints.Length];
    }

    void Update()
    {
        // Update joint positions based on angles
        for (int i = 0; i < joints.Length; i++)
        {
            // Apply joint rotation
            joints[i].localRotation = Quaternion.Euler(0, jointAngles[i], 0);
        }
    }

    public void SetJointAngle(int jointIndex, float angle)
    {
        if (jointIndex >= 0 && jointIndex < jointAngles.Length)
        {
            // Apply joint limits
            jointAngles[jointIndex] = Mathf.Clamp(angle,
                jointLimitsMin[jointIndex],
                jointLimitsMax[jointIndex]);
        }
    }
}
```

## Visualization Techniques

### Sensor Data Visualization

Create visual representations of sensor data:

```csharp
using UnityEngine;
using System.Collections.Generic;

public class LaserScanVisualizer : MonoBehaviour
{
    public GameObject rayPrefab; // Prefab for individual rays
    private List<GameObject> rays = new List<GameObject>();

    public void UpdateLaserScan(float[] ranges, float angleMin, float angleMax)
    {
        // Clear previous rays
        foreach (GameObject ray in rays)
        {
            DestroyImmediate(ray);
        }
        rays.Clear();

        float angleIncrement = (angleMax - angleMin) / ranges.Length;

        for (int i = 0; i < ranges.Length; i++)
        {
            if (ranges[i] > 0 && ranges[i] < 30.0f) // Valid range
            {
                float angle = angleMin + (i * angleIncrement);

                // Calculate endpoint of ray
                Vector3 direction = new Vector3(
                    Mathf.Cos(angle) * ranges[i],
                    0,
                    Mathf.Sin(angle) * ranges[i]
                );

                // Create visual ray
                GameObject ray = Instantiate(rayPrefab, transform.position, Quaternion.identity);
                LineRenderer lineRenderer = ray.GetComponent<LineRenderer>();

                if (lineRenderer != null)
                {
                    lineRenderer.SetPosition(0, transform.position);
                    lineRenderer.SetPosition(1, transform.position + direction);
                }

                rays.Add(ray);
            }
        }
    }
}
```

### Camera and Sensor Simulation

Unity can simulate various camera perspectives and sensor views:

```csharp
using UnityEngine;

public class CameraSimulator : MonoBehaviour
{
    public Camera mainCamera;
    public RenderTexture cameraOutput;

    void Start()
    {
        // Set up camera output texture
        cameraOutput = new RenderTexture(640, 480, 24);
        mainCamera.targetTexture = cameraOutput;
    }

    // Method to capture and send camera data to ROS
    public Texture2D CaptureImage()
    {
        RenderTexture.active = cameraOutput;
        Texture2D image = new Texture2D(cameraOutput.width, cameraOutput.height);
        image.ReadPixels(new Rect(0, 0, cameraOutput.width, cameraOutput.height), 0, 0);
        image.Apply();

        return image;
    }
}
```

## Human-Robot Interaction Interfaces

### Creating Intuitive Control Panels

Unity excels at creating user-friendly interfaces:

```csharp
using UnityEngine;
using UnityEngine.UI;
using Unity.Robotics.ROSTCPConnector;

public class RobotControlPanel : MonoBehaviour
{
    public Button moveForwardButton;
    public Button moveBackwardButton;
    public Slider speedSlider;
    public Toggle autonomousModeToggle;

    ROSConnection ros;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();

        // Set up button callbacks
        moveForwardButton.onClick.AddListener(() => SendCommand("forward"));
        moveBackwardButton.onClick.AddListener(() => SendCommand("backward"));

        // Set up slider callback
        speedSlider.onValueChanged.AddListener(OnSpeedChanged);

        // Set up toggle callback
        autonomousModeToggle.onValueChanged.AddListener(OnAutonomousModeChanged);
    }

    void SendCommand(string command)
    {
        // Send command to ROS
        ros.SendServiceMessage<RobotCommandServiceRequest, RobotCommandServiceResponse>(
            "robot_command_service",
            new RobotCommandServiceRequest { command = command, speed = speedSlider.value }
        );
    }

    void OnSpeedChanged(float value)
    {
        // Speed slider changed - update robot speed
        Debug.Log($"Speed changed to: {value}");
    }

    void OnAutonomousModeChanged(bool isOn)
    {
        // Autonomous mode toggle changed
        Debug.Log($"Autonomous mode: {(isOn ? "ON" : "OFF")}");
    }
}
```

## Unity-ROS Bridge Implementation

### Setting up the Bridge

1. **Start the ROS TCP Connector** in Unity:

```csharp
using Unity.Robotics.ROSTCPConnector;

public class RosBridgeSetup : MonoBehaviour
{
    public string rosIPAddress = "127.0.0.1"; // ROS master IP
    public int rosPort = 10000; // ROS TCP port

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Initialize(rosIPAddress, rosPort);
        Debug.Log($"Connected to ROS at {rosIPAddress}:{rosPort}");
    }
}
```

2. **Configure ROS 2 Bridge Node**:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8
from unity_robotics_demo_msgs.msg import FromUnity, ToUnity

class UnityBridge(Node):
    def __init__(self):
        super().__init__('unity_bridge')

        # Publishers to Unity
        self.to_unity_pub = self.create_publisher(ToUnity, 'to_unity', 10)

        # Subscribers from Unity
        self.from_unity_sub = self.create_subscription(
            FromUnity,
            'from_unity',
            self.from_unity_callback,
            10
        )

        # Subscribers for robot data
        self.scan_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info('Unity Bridge initialized')

    def from_unity_callback(self, msg):
        # Handle messages from Unity
        self.get_logger().info(f'Received from Unity: {msg.data}')

    def scan_callback(self, msg):
        # Forward sensor data to Unity
        unity_msg = ToUnity()
        unity_msg.scan_ranges = list(msg.ranges)
        unity_msg.header = msg.header
        self.to_unity_pub.publish(unity_msg)

    def cmd_vel_callback(self, msg):
        # Forward velocity commands from Unity to robot
        self.get_logger().info(f'Velocity command: {msg.linear.x}, {msg.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    bridge = UnityBridge()

    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Performance Optimization

### Optimizing Unity Scenes for Real-time Robotics

1. **Level of Detail (LOD)**: Use LOD groups to reduce geometry complexity at distance
2. **Occlusion Culling**: Hide objects not visible to the camera
3. **Light Baking**: Pre-calculate static lighting to reduce real-time calculations
4. **Object Pooling**: Reuse objects instead of instantiating/destroying frequently

### Managing Large Environments

```csharp
using UnityEngine;
using System.Collections.Generic;

public class EnvironmentManager : MonoBehaviour
{
    public GameObject[] environmentChunks; // Pre-divided environment chunks
    private List<GameObject> activeChunks = new List<GameObject>();
    public float loadDistance = 50f; // Distance to load chunks

    void Update()
    {
        // Check which chunks should be active based on camera position
        Vector3 cameraPos = Camera.main.transform.position;

        foreach (GameObject chunk in environmentChunks)
        {
            float distance = Vector3.Distance(chunk.transform.position, cameraPos);

            if (distance <= loadDistance)
            {
                if (!activeChunks.Contains(chunk))
                {
                    chunk.SetActive(true);
                    activeChunks.Add(chunk);
                }
            }
            else
            {
                if (activeChunks.Contains(chunk))
                {
                    chunk.SetActive(false);
                    activeChunks.Remove(chunk);
                }
            }
        }
    }
}
```

## Best Practices for Unity in Robotics

1. **Modular Design**: Create reusable components and prefabs
2. **Realistic Physics**: Use Unity's physics engine appropriately for robot simulation
3. **Performance Monitoring**: Monitor frame rates and optimize for real-time performance
4. **Cross-platform Testing**: Test on target deployment platforms
5. **Version Control**: Use version control for Unity projects (be mindful of binary files)
6. **Documentation**: Document Unity scenes and component relationships
7. **Safety**: Include safety boundaries and emergency stop functionality

## Exercise

Create a Unity scene that visualizes a mobile robot navigating through a warehouse environment. Implement:
1. A robot model that responds to ROS 2 velocity commands
2. Visualization of LiDAR sensor data as a point cloud or ray visualization
3. A user interface panel that allows manual control of the robot
4. Integration with ROS 2 to receive real sensor data and send control commands

## Summary

Unity provides powerful visualization capabilities that complement Gazebo's physics simulation. By integrating Unity with ROS 2, you can create immersive, high-quality visualization environments for robotics applications. The combination of realistic physics simulation in Gazebo and advanced visualization in Unity provides a comprehensive simulation solution for robotics development and testing.