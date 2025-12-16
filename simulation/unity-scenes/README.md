# Unity Scenes for Robotics Simulation

This directory contains Unity scenes for advanced visualization and human-robot interaction as part of the Physical AI & Humanoid Robotics course.

## Setting up Unity for Robotics

### Prerequisites
- Unity Hub installed
- Unity Editor 2022.3 LTS installed
- Unity Robotics Package
- ROS-TCP-Connector
- Unity-Robotics-Hub

### Installation Steps

1. **Install Unity Robotics Hub**:
   - Open Unity Hub
   - Create a new 3D project
   - Go to Window > Package Manager
   - Install "ROS TCP Connector" package

2. **Import Robot Models**:
   - Import robot URDF files using the Unity URDF Importer
   - Configure joint properties and kinematics

3. **Set up ROS Communication**:
   - Configure ROS TCP Connector settings
   - Set up publishers and subscribers for sensor data

### Scene Structure

Each scene should include:

1. **Robot Visualization**:
   - 3D model of the robot
   - Joint articulation
   - Sensor visualization

2. **Environment**:
   - Gazebo-compatible environments
   - Interactive elements
   - Navigation goals

3. **UI Elements**:
   - Robot status displays
   - Control interfaces
   - Sensor data visualization

### Example Scene Setup

```csharp
// Example Unity script for robot control
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;

public class UnityRobotController : MonoBehaviour
{
    ROSConnection ros;
    string cmdVelTopic = "cmd_vel";

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<TwistMsg>(cmdVelTopic);
    }

    void Update()
    {
        // Example: Move robot with arrow keys
        if (Input.GetKey(KeyCode.UpArrow))
        {
            TwistMsg cmd = new TwistMsg();
            cmd.linear = new Vector3Msg(0.5f, 0, 0); // Move forward
            ros.Publish(cmdVelTopic, cmd);
        }
    }
}
```

### Integration with ROS 2

The Unity scenes are designed to work with ROS 2 through the TCP connector:

- Sensor data flows from ROS 2 to Unity for visualization
- Control commands flow from Unity to ROS 2 for robot execution
- TF transforms are synchronized between both systems

## Scene List

- `warehouse_navigation.unity`: Warehouse environment for navigation tasks
- `office_environment.unity`: Indoor office environment
- `sensor_fusion.unity`: Scene focused on sensor data visualization
- `human_robot_interaction.unity`: Scene with UI elements for human-robot interaction

## Running the Unity Scenes

1. Open the Unity project
2. Load the desired scene
3. Configure ROS connection settings
4. Run the scene and connect to your ROS 2 environment
5. Use the Unity interface to control and visualize your robot

## Best Practices

- Keep scenes modular and reusable
- Use prefabs for common robot and environment components
- Implement proper error handling for ROS connections
- Optimize scenes for real-time performance
- Document scene-specific settings and configurations