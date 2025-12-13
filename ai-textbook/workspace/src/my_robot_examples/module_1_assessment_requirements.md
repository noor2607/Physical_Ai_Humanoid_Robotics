# Module 1 Assessment Project: Basic ROS 2 Robot System

## Overview
Students will create a complete ROS 2 system that demonstrates understanding of core concepts including nodes, topics, services, and parameters. The project integrates multiple communication patterns and demonstrates practical robotics applications.

## Learning Objectives
Upon completion of this assessment, students will be able to:
- Design and implement a multi-node ROS 2 system
- Integrate publisher-subscriber, service, and parameter communication patterns
- Demonstrate proper ROS 2 node architecture and best practices
- Validate system functionality through testing and simulation

## Project Requirements

### Core Components
1. **Robot Controller Node**:
   - Implement a node that controls a simulated robot's movement
   - Use parameters for configurable speed settings
   - Subscribe to sensor data topics
   - Publish command velocity messages

2. **Sensor Processing Node**:
   - Subscribe to simulated sensor data (e.g., laser scan)
   - Process sensor data to detect obstacles
   - Publish processed information to other nodes

3. **Navigation Service**:
   - Implement a service that accepts destination coordinates
   - Plan a path to the destination considering obstacles
   - Return success/failure status

4. **System Monitor Node**:
   - Monitor the status of all other nodes
   - Publish system health information
   - Handle node failures gracefully

### Communication Patterns
- Use at least 3 different communication patterns (topics, services, parameters)
- Implement proper message types from standard ROS 2 packages
- Ensure appropriate QoS settings for different data types

### Implementation Requirements
- All code must follow ROS 2 Python best practices
- Include proper error handling and logging
- Use parameter server for configuration
- Implement graceful shutdown procedures
- Include documentation and comments for educational purposes

## Evaluation Criteria

### Functionality (50%)
- System successfully implements all required components
- Communication between nodes works correctly
- Service calls complete successfully
- Parameter configuration works as expected

### Code Quality (25%)
- Follows ROS 2 Python best practices
- Proper error handling and logging
- Well-documented with appropriate comments
- Clean, readable code structure

### Design (15%)
- Appropriate use of ROS 2 concepts
- Good node architecture and separation of concerns
- Efficient algorithms for sensor processing

### Documentation (10%)
- Clear README with setup and usage instructions
- Inline documentation explaining key algorithms
- Proper docstrings for classes and functions

## Submission Requirements
- Complete ROS 2 package with all source code
- README.md with setup instructions and usage guide
- Brief report explaining design decisions and challenges overcome
- Launch file to start the complete system

## Optional Enhancements (Bonus Points)
- Add action-based navigation for complex tasks
- Implement dynamic reconfigure parameters
- Add visualization of robot path and obstacles
- Create unit tests for individual components

## Resources
- ROS 2 Humble Hawksbill documentation
- Example code from previous chapters
- Official ROS 2 tutorials
- Course forums for peer assistance