# Lab Exercise 2: Path Planning in Dynamic Environment

## Overview
In this lab, you will implement and evaluate path planning algorithms in a dynamic environment with moving obstacles. You will compare different approaches for handling dynamic environments and implement a system that can replan paths in real-time as obstacles move.

## Learning Objectives
- Implement A* and RRT algorithms for static path planning
- Extend algorithms to handle dynamic environments
- Implement local planning for obstacle avoidance
- Evaluate path planning performance in dynamic scenarios

## Prerequisites
- Understanding of graph search algorithms
- Familiarity with ROS 2 navigation stack
- Knowledge of collision detection
- Basic understanding of motion planning

## Setup Instructions
1. Launch Isaac Sim with the dynamic environment scene
2. Ensure you have the navigation stack properly configured
3. Verify that your robot can receive sensor data and publish commands

## Exercise Tasks

### Task 1: Static Path Planning Implementation (20 points)
Implement A* and RRT algorithms for static path planning.

**Requirements:**
- Implement A* algorithm with appropriate heuristic
- Implement RRT algorithm with proper sampling
- Visualize the search tree and final path
- Compare path quality and computation time

**Code skeleton to complete:**
```python
def a_star_planner(self, start, goal, occupancy_grid):
    # Implement A* algorithm
    # Use Manhattan distance heuristic
    # Return optimal path
    pass

def rrt_planner(self, start, goal, occupancy_grid):
    # Implement RRT algorithm
    # Use random sampling in configuration space
    # Return feasible path
    pass

def visualize_path(self, path, occupancy_grid):
    # Visualize the planned path on the grid
    # Show search tree for RRT
    pass
```

### Task 2: Dynamic Path Planning (30 points)
Extend your path planning to handle moving obstacles.

**Requirements:**
- Implement time-parameterized path planning
- Add obstacle prediction and avoidance
- Implement replanning when obstacles block the path
- Handle dynamic constraints (velocity, acceleration)

**Code skeleton to complete:**
```python
def predict_obstacle_trajectory(self, obstacle_state):
    # Predict future positions of moving obstacles
    # Use constant velocity model
    # Return predicted trajectory
    pass

def dynamic_a_star(self, start, goal, dynamic_obstacles):
    # Implement time-parameterized A*
    # Consider obstacle motion in planning
    # Return space-time path
    pass

def replan_if_blocked(self, current_path, new_obstacles):
    # Check if current path is blocked by new obstacles
    # Replan if necessary
    # Return updated path
    pass
```

### Task 3: Local Planning and Obstacle Avoidance (25 points)
Implement local planning for real-time obstacle avoidance.

**Requirements:**
- Implement Dynamic Window Approach (DWA) for local planning
- Integrate with global path planner
- Handle sensor noise and uncertainty
- Implement smooth trajectory generation

**Code skeleton to complete:**
```python
def dynamic_window_approach(self, robot_state, goal, obstacles):
    # Implement DWA algorithm
    # Calculate velocity space
    # Evaluate trajectories
    # Return optimal velocity command
    pass

def trajectory_rollout(self, v, omega, dt, steps):
    # Simulate robot trajectory
    # Predict future poses
    # Evaluate for collisions
    pass

def integrate_local_global(self, global_path, robot_pose):
    # Integrate local and global planners
    # Follow global path while avoiding local obstacles
    # Handle path tracking errors
    pass
```

### Task 4: System Evaluation and Optimization (25 points)
Evaluate your system in various dynamic scenarios.

**Requirements:**
- Test in environments with different obstacle densities
- Measure success rate and computation time
- Analyze path quality and safety metrics
- Optimize algorithm parameters

**Evaluation metrics to implement:**
- Success rate in reaching goal
- Average path length vs optimal
- Computation time per planning cycle
- Safety margin from obstacles
- Number of replanning events

## Deliverables
1. **Complete path planning implementation** - Your working code
2. **Algorithm comparison report** - Compare A* vs RRT vs DWA
3. **Performance analysis** - Analysis of computational requirements
4. **Video demonstration** - Show your system navigating dynamic environment

## Evaluation Criteria
- **Functionality (50%)**: Does the system successfully navigate dynamic environments?
- **Code Quality (20%)**: Is the code well-structured and documented?
- **Performance (20%)**: How efficient and safe is the implementation?
- **Analysis (10%)**: Quality of algorithm comparison and insights

## Advanced Challenges (Bonus: up to 10 points)
- Implement RRT* for optimal path planning
- Add learning-based prediction for obstacle motion
- Implement multi-robot path planning with coordination

## Resources
- ROS 2 Navigation2 tutorials
- Isaac Sim navigation examples
- Motion planning literature and papers
- Provided path planning template code

## Submission Instructions
- Submit your complete code files
- Include a PDF report with algorithm comparison
- Provide a brief video showing navigation in dynamic environment
- Submit via the course management system

## Estimated Time: 8-12 hours