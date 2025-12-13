# Exercise 1: Basic Gazebo Environment Setup

## Objective
Create a simple Gazebo environment with basic physics and objects, and spawn a robot model to navigate through the environment.

## Prerequisites
- Completed Module 1 (ROS 2 fundamentals)
- Basic understanding of URDF
- Gazebo installed and configured

## Learning Outcomes
- Understand Gazebo world file structure
- Create basic objects in Gazebo
- Spawn a robot model in the simulation
- Control the robot using ROS 2 commands

## Task Description

### Part 1: Create a Simple World (30 points)
Create a Gazebo world file named `simple_room.world` that includes:
- A ground plane
- Four walls forming a 10x10m room
- Two obstacles (boxes) placed in the middle of the room
- A goal marker (colored cylinder) in one corner

### Part 2: Robot Setup (30 points)
- Use the provided simple robot model (or create your own URDF)
- Ensure the robot has proper collision, visual, and inertial properties
- Add a camera sensor to the robot facing forward
- Add a LiDAR sensor with 360-degree scanning capability

### Part 3: Navigation (40 points)
- Launch the world with your robot positioned in one corner
- Use ROS 2 tools to control the robot to navigate to the goal marker
- Avoid collisions with the obstacles
- Document the approach used for navigation

## Implementation Steps

1. Create the world file in SDF format
2. Define the robot model in URDF format
3. Create a launch file to start Gazebo with your world
4. Test the simulation and document your results

## Evaluation Criteria
- World file correctly formatted and loads without errors (20 points)
- Robot model properly defined and spawns correctly (20 points)
- Robot can navigate through the environment (30 points)
- Documentation and code quality (30 points)

## Submission Requirements
- World file (simple_room.world)
- Robot URDF file
- Launch file
- README with instructions
- Brief report on navigation approach

## Difficulty Level: Intermediate
Estimated completion time: 4-6 hours

## Resources
- Gazebo documentation
- ROS 2 robot setup tutorials
- URDF tutorials
- Example world files from the course materials