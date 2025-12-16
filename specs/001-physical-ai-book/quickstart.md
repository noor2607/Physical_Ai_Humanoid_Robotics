# Quickstart Guide: Physical AI & Humanoid Robotics Course Book

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04/22.04 LTS or Windows 10/11 with WSL2
- **CPU**: Intel i7 or AMD Ryzen 7 (8+ cores recommended)
- **GPU**: NVIDIA RTX 3070 or higher (for Isaac Sim acceleration)
- **RAM**: 32GB or more
- **Storage**: 1TB SSD
- **Network**: Stable internet connection for package downloads and LLM access

### Software Dependencies
1. **ROS 2**: Install Humble Hawksbill or later
2. **Gazebo**: Garden or Fortress version
3. **Unity**: Personal or Pro edition (2022.3 LTS recommended)
4. **NVIDIA Isaac**: Isaac Sim and Isaac ROS packages
5. **Python**: 3.8 or higher with pip
6. **Git**: Version control system
7. **Docker**: For containerized environments (optional but recommended)

## Setup Process

### 1. Environment Setup
```bash
# Install ROS 2 (Ubuntu)
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo apt install curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
sudo rosdep init
rosdep update
source /opt/ros/humble/setup.bash
```

### 2. Gazebo Installation
```bash
# Install Gazebo Garden
sudo apt install ignition-garden
# Or for Fortress (if preferred)
sudo apt install gazebo-fortress
```

### 3. NVIDIA Isaac Setup
```bash
# Install Isaac ROS dependencies
sudo apt update
sudo apt install nvidia-isaac-core
# Follow NVIDIA's Isaac Sim installation guide for your GPU
# Download Isaac Sim from NVIDIA Developer website
```

### 4. Unity Installation
```bash
# Download Unity Hub from Unity website
# Install Unity 2022.3 LTS with Linux Build Support
# Install ROS-TCP-Connector package for ROS communication
```

### 5. Course Materials Setup
```bash
# Clone the course repository
git clone https://github.com/[organization]/physical-ai-course.git
cd physical-ai-course

# Create workspace
mkdir -p ~/physical_ai_ws/src
cd ~/physical_ai_ws

# Source ROS environment
source /opt/ros/humble/setup.bash

# Build workspace
colcon build --symlink-install
source install/setup.bash
```

## Running the First Example

### 1. Basic ROS 2 Node
```bash
# Navigate to examples
cd ~/physical_ai_ws/src
# Create a new package
ros2 pkg create --build-type ament_python beginner_tutorials
cd beginner_tutorials

# Create a simple publisher node
# (Content from Chapter 1 examples)
```

### 2. Simulation Environment
```bash
# Launch Gazebo simulation
ros2 launch gazebo_ros empty_world.launch.py

# Launch Isaac Sim environment
# Follow Isaac Sim quickstart guide
```

### 3. Unity Visualization
```bash
# Open Unity project
# Import ROS-TCP-Connector
# Configure connection to ROS network
```

## Course Navigation

### Module Structure
1. **Module 1**: Robotic Nervous System (ROS 2) - Weeks 1-3
2. **Module 2**: Digital Twin (Gazebo & Unity) - Weeks 4-6
3. **Module 3**: AI-Robot Brain (NVIDIA Isaac) - Weeks 7-10
4. **Module 4**: Vision-Language-Action (VLA) - Weeks 11-13

### Exercise Execution
1. Navigate to the exercise directory: `cd ~/physical_ai_ws/src/exercises/module_X/chapter_Y/exercise_Z`
2. Review the README.md for exercise requirements
3. Run the setup script: `./setup.sh`
4. Execute the exercise: `python3 exercise.py`
5. Validate results: `./validate.sh`

## Troubleshooting

### Common Issues
- **GPU Acceleration**: Ensure NVIDIA drivers are properly installed and Isaac Sim is configured correctly
- **ROS Network**: Verify ROS_DOMAIN_ID and RMW_IMPLEMENTATION are consistent across all terminals
- **Simulation Performance**: Reduce physics update rate or simplify models if experiencing lag

### Getting Help
- Check the course FAQ at [website]/faq
- Join the course Discord for real-time support
- Submit issues on the course GitHub repository