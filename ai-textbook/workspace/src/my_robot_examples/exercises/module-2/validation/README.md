# Exercise Validation System for Module 2

This directory contains validation scripts for Module 2 exercises on simulation environments. Each script automatically checks if the student's implementation meets the exercise requirements.

## Validation Scripts

### validate_exercise1.py
Validates Exercise 1: Basic Gazebo Environment Setup
- Checks for proper world file structure
- Validates robot model with camera and LiDAR sensors
- Tests basic navigation capabilities

### validate_exercise2.py
Validates Exercise 2: Sensor Simulation and Data Processing
- Checks for all required sensors (LiDAR, camera, IMU, sonar)
- Validates realistic sensor parameters
- Tests obstacle detection and avoidance

### validate_exercise3.py
Validates Exercise 3: Advanced Environment Creation and Simulation
- Validates multi-robot setup
- Checks coordination algorithms
- Tests collision avoidance between robots

## How to Use

1. Ensure your simulation is running with all required components
2. Run the appropriate validation script:
   ```bash
   ros2 run my_robot_examples validate_exercise1.py
   ```
3. The script will check your implementation and provide feedback
4. Review the results and make necessary improvements

## Validation Criteria

Each script evaluates:
- Required components are present and functional
- Parameters match realistic values
- Algorithms perform as expected
- System behaves correctly under test conditions

## Return Codes

- 0: Validation passed successfully
- 1: Validation failed, improvements needed

## Troubleshooting

If validation fails:
1. Check that all required nodes are running
2. Verify topic names match expected values
3. Ensure proper namespace usage for multi-robot systems
4. Review the validation output for specific issues