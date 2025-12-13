# Physical AI & Humanoid Robotics - ROS 2 Workspace

This workspace contains ROS 2 packages for the Physical AI & Humanoid Robotics course.

## Setup

1. Make sure you have ROS 2 Humble Hawksbill installed
2. Source the ROS 2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   ```
3. Navigate to this workspace directory
4. Build the packages:
   ```bash
   colcon build --packages-select physical_ai_examples
   ```
5. Source the workspace:
   ```bash
   source install/setup.bash
   ```

## Available Examples

### Publisher/Subscriber Example
Run the publisher:
```bash
ros2 run physical_ai_examples talker
```

In another terminal, run the subscriber:
```bash
ros2 run physical_ai_examples listener
```

This demonstrates basic ROS 2 communication through topics.