# Troubleshooting Guide: Physical AI & Humanoid Robotics Course

## Overview
This guide provides solutions to common issues students may encounter while working through the Physical AI & Humanoid Robotics course. It covers troubleshooting for all modules and technologies used in the course.

## Getting Started Issues

### Environment Setup Problems

#### ROS 2 Installation Issues
**Problem**: ROS 2 fails to install or source properly
**Solution**:
1. Verify your Ubuntu version is supported (20.04 or 22.04 LTS)
2. Check that your locale is set correctly:
   ```bash
   locale  # Should show LANG=en_US.UTF-8
   ```
3. If locale is incorrect:
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```
4. Reinstall ROS 2 following the official installation guide
5. Verify installation:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 --version
   ```

**Problem**: `command not found: ros2`
**Solution**:
1. Ensure ROS 2 is properly installed and sourced
2. Add sourcing to your `.bashrc`:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```

#### Python Environment Issues
**Problem**: Python packages not found or conflicting versions
**Solution**:
1. Create a virtual environment:
   ```bash
   python3 -m venv ~/ros2_env
   source ~/ros2_env/bin/activate
   ```
2. Install packages within the virtual environment
3. Deactivate when finished: `deactivate`

### Simulation Environment Issues

#### Gazebo Problems
**Problem**: Gazebo fails to start or crashes immediately
**Solution**:
1. Check graphics drivers are properly installed:
   ```bash
   nvidia-smi  # For NVIDIA GPUs
   glxinfo | grep "OpenGL renderer"  # Verify OpenGL support
   ```
2. Ensure sufficient system resources (RAM, GPU memory)
3. Try running with software rendering:
   ```bash
   export LIBGL_ALWAYS_SOFTWARE=1
   gazebo
   ```

**Problem**: Models not loading or physics behaving strangely
**Solution**:
1. Verify model paths are correct
2. Check that models follow proper URDF/SDF format
3. Ensure all dependencies are installed:
   ```bash
   sudo apt update
   sudo apt install ros-humble-gazebo-ros-pkgs
   ```

#### Unity Integration Issues
**Problem**: Unity fails to connect to ROS network
**Solution**:
1. Ensure ROS-TCP-Connector is properly installed in Unity
2. Check that both Unity and ROS are on the same network
3. Verify IP addresses and ports match in configuration
4. Check firewall settings block the connection

### Isaac Sim Issues

#### Installation Problems
**Problem**: Isaac Sim fails to install or launch
**Solution**:
1. Verify NVIDIA GPU and drivers are properly installed
2. Check that Isaac Sim requirements are met:
   - Compatible NVIDIA GPU (RTX series recommended)
   - Proper CUDA version
   - Sufficient VRAM (8GB+ recommended)
3. Run Isaac Sim system check:
   ```bash
   python3 -c "import omni; print('Isaac Sim modules loaded successfully')"
   ```

#### Performance Issues
**Problem**: Isaac Sim running slowly or with low frame rates
**Solution**:
1. Reduce physics update rate in simulation settings
2. Simplify models or reduce scene complexity
3. Check GPU memory usage and close other applications
4. Adjust rendering quality settings in Isaac Sim

## Module 1: ROS 2 Troubleshooting

### Node Communication Issues

**Problem**: Publisher and subscriber not communicating
**Solution**:
1. Verify topic names match exactly (case-sensitive)
2. Check that both nodes are running simultaneously
3. Use `ros2 topic list` to verify the topic exists
4. Use `ros2 topic echo /topic_name` to manually check messages
5. Ensure both nodes are on the same ROS domain ID

**Problem**: Node fails to create publisher/subscriber
**Solution**:
1. Check that message type is imported correctly
2. Verify the topic name follows ROS naming conventions
3. Ensure the queue size parameter is valid
4. Check for typos in the message type import

### Workspace and Build Issues

**Problem**: `colcon build` fails
**Solution**:
1. Check for syntax errors in Python files
2. Verify all dependencies are declared in `package.xml`
3. Ensure proper file permissions
4. Clean build directory: `rm -rf build install log`
5. Rebuild: `colcon build`

**Problem**: Package not found after building
**Solution**:
1. Verify the package is in the `src` directory of your workspace
2. Ensure `package.xml` is properly configured
3. Source the workspace after building:
   ```bash
   source install/setup.bash
   ```

## Module 2: Simulation Troubleshooting

### Gazebo-Specific Issues

**Problem**: Robot model falls through the ground
**Solution**:
1. Check that the model has proper collision geometries
2. Verify mass and inertia properties are correctly set
3. Ensure physics parameters are properly configured
4. Check for malformed URDF/SDF files

**Problem**: Sensors not publishing data
**Solution**:
1. Verify sensor plugin is properly loaded
2. Check that sensor topics exist: `ros2 topic list | grep sensor`
3. Ensure sensor configuration parameters are correct
4. Check Gazebo logs for sensor-related errors

### Unity-Specific Issues

**Problem**: Unity scene not updating with ROS data
**Solution**:
1. Verify ROS-TCP-Connector is properly configured
2. Check network connection between Unity and ROS
3. Ensure correct topic names and message types
4. Verify Unity scripts are properly attached to objects

## Module 3: Isaac Troubleshooting

### Perception System Issues

**Problem**: Object detection not working in Isaac Sim
**Solution**:
1. Verify Isaac Sim perception extensions are enabled
2. Check camera calibration parameters
3. Ensure proper lighting conditions in the scene
4. Verify object models have proper textures and materials

**Problem**: Navigation fails or robot gets stuck
**Solution**:
1. Check that navigation stack is properly configured
2. Verify map and localization are working
3. Check that obstacles are properly detected
4. Ensure path planning parameters are appropriate

### AI Integration Issues

**Problem**: AI models not loading or running slowly
**Solution**:
1. Verify CUDA and cuDNN are properly installed
2. Check that GPU has sufficient memory
3. Ensure model files are in the correct location
4. Verify Isaac Sim AI extensions are enabled

## Module 4: VLA Troubleshooting

### Speech Recognition Issues

**Problem**: Speech recognition not working or low accuracy
**Solution**:
1. Check that microphone is properly configured
2. Verify audio input levels are appropriate
3. Ensure quiet environment for testing
4. Check that speech recognition library is properly installed
5. Verify API keys for cloud-based services are valid

**Problem**: Voice commands not being processed
**Solution**:
1. Check that audio input is being received
2. Verify natural language processing pipeline
3. Ensure intent recognition is working
4. Check that command mapping is correct

### LLM Integration Issues

**Problem**: LLM responses taking too long or failing
**Solution**:
1. Verify API keys and network connectivity
2. Check rate limits and quota usage
3. Ensure proper error handling for API failures
4. Verify prompt formatting is correct

**Problem**: LLM generating invalid robot commands
**Solution**:
1. Implement proper output validation
2. Use structured output formats
3. Add safety checks before executing commands
4. Verify LLM response parsing logic

## General Development Issues

### Code Execution Problems

**Problem**: Python scripts fail with import errors
**Solution**:
1. Verify the workspace is properly sourced
2. Check that all dependencies are installed
3. Ensure correct Python version is being used
4. Verify PYTHONPATH includes necessary directories

**Problem**: Permission errors when running scripts
**Solution**:
1. Make script executable: `chmod +x script_name.py`
2. Check file ownership and permissions
3. Run with appropriate user privileges
4. Verify no conflicting processes are running

### Network and Communication Issues

**Problem**: Nodes on different machines cannot communicate
**Solution**:
1. Verify ROS_DOMAIN_ID is the same on all machines
2. Check network connectivity between machines
3. Ensure firewall allows ROS traffic
4. Verify RMW_IMPLEMENTATION is consistent

## Performance Optimization

### System Performance Issues

**Problem**: Slow simulation or high CPU/GPU usage
**Solution**:
1. Reduce simulation update rates
2. Simplify models or reduce scene complexity
3. Close unnecessary applications
4. Check for background processes consuming resources

**Problem**: Memory leaks in long-running nodes
**Solution**:
1. Implement proper cleanup in node destruction
2. Monitor memory usage with system tools
3. Check for circular references in code
4. Use profiling tools to identify memory issues

## FAQ - Frequently Asked Questions

### General Questions

**Q: Can I use Windows for this course?**
A: Yes, but we strongly recommend using Ubuntu 20.04/22.04 LTS for the best experience. If using Windows, install WSL2 with Ubuntu and run ROS 2 from within WSL2.

**Q: What hardware specifications do I need?**
A: Minimum: Intel i7/AMD Ryzen 7, 16GB RAM, modern GPU. Recommended: NVIDIA RTX 3070+, 32GB RAM for Isaac Sim acceleration.

**Q: How do I reset my ROS 2 environment if something goes wrong?**
A: Close all terminals, then open a new terminal and run:
```bash
source /opt/ros/humble/setup.bash
```

### Module-Specific Questions

**Q: How do I know if my ROS 2 installation is working correctly?**
A: Run `ros2 --version` and you should see the ROS 2 version. Also try `ros2 run demo_nodes_cpp talker` in one terminal and `ros2 run demo_nodes_py listener` in another to test communication.

**Q: Why is my Gazebo simulation running very slowly?**
A: This could be due to insufficient GPU resources, complex models, or high physics update rates. Try reducing the physics update rate in the world file or simplifying your robot model.

**Q: How do I debug Isaac Sim issues?**
A: Check the Isaac Sim logs in `~/.nvidia-isaac/logs/`. You can also run Isaac Sim from the command line to see real-time output.

**Q: What should I do if my voice recognition isn't working?**
A: First, verify your microphone is working with a simple audio recording app. Then check that the speech recognition library is properly installed. For cloud-based services, verify your API keys and internet connection.

### Technical Questions

**Q: How do I create a new ROS 2 package?**
A: Use the command: `ros2 pkg create --build-type ament_python package_name`

**Q: What's the difference between a service and an action?**
A: Services are for request-response communication with a quick response. Actions are for long-running tasks that may provide feedback during execution and can be canceled.

**Q: How do I check if my nodes are communicating properly?**
A: Use `ros2 node list` to see active nodes, `ros2 topic list` to see active topics, and `ros2 topic echo /topic_name` to view messages.

## Getting Additional Help

### When to Seek Help
- Issues persist after trying troubleshooting steps
- Errors are not covered in this guide
- Need clarification on concepts or procedures
- Found potential bugs in course materials

### Support Resources
- **Course Discord**: Join the course community for real-time help
- **Instructor Office Hours**: Check the course schedule
- **ROS Answers**: https://answers.ros.org/
- **Isaac Sim Documentation**: https://docs.omniverse.nvidia.com/
- **Course GitHub Issues**: Report problems with course materials

### Information to Include When Seeking Help
1. **Detailed description** of the problem
2. **Error messages** (copy and paste when possible)
3. **Steps taken** before the issue occurred
4. **System information** (OS, ROS 2 version, hardware)
5. **What you've tried** to solve the problem

---

**Note**: This troubleshooting guide will be updated regularly based on common issues reported by students. If you encounter an issue not covered here, please report it to the course staff so we can add it to this guide for future students.