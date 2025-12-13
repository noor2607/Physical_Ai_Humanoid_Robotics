---
sidebar_position: 5
title: "Chapter 13: Path Planning"
---

# Chapter 13: Path Planning

## Introduction to Path Planning

Path planning is a critical component of autonomous robotics that determines how a robot should move from its current location to a goal location while avoiding obstacles and optimizing various criteria. In the context of AI-integrated robotics, path planning algorithms must balance efficiency, safety, and adaptability to dynamic environments.

## Types of Path Planning

### Global Path Planning
- Plans the entire path from start to goal
- Uses complete or partial map knowledge
- Algorithms: A*, Dijkstra, RRT, PRM
- Provides optimal or near-optimal solutions

### Local Path Planning
- Plans short-term movements based on immediate sensor data
- Handles dynamic obstacles and unexpected situations
- Algorithms: Dynamic Window Approach (DWA), Trajectory Rollout
- More reactive to environmental changes

### Hybrid Approaches
- Combines global and local planning
- Uses global plan as guide for local planner
- Provides both optimality and adaptability

## Classical Path Planning Algorithms

### A* Algorithm
A widely-used graph-based algorithm that combines Dijkstra's optimality with greedy best-first search efficiency:

```python
#!/usr/bin/env python3

import heapq
import numpy as np

def a_star(grid, start, goal):
    """
    A* path planning algorithm implementation
    """
    rows, cols = grid.shape
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, rows, cols):
            if grid[neighbor] == 1:  # Obstacle
                continue

            tentative_g_score = g_score[current] + distance(current, neighbor)

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

def heuristic(a, b):
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, rows, cols):
    """Get valid neighbors for a position"""
    neighbors = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
        nx, ny = pos[0] + dx, pos[1] + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            neighbors.append((nx, ny))
    return neighbors

def reconstruct_path(came_from, current):
    """Reconstruct path from came_from dictionary"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
```

### Dijkstra's Algorithm
Guaranteed to find the shortest path but can be slower than A*:

```python
def dijkstra(grid, start, goal):
    """
    Dijkstra's algorithm implementation
    """
    rows, cols = grid.shape
    open_set = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, rows, cols):
            if grid[neighbor] == 1:  # Obstacle
                continue

            new_cost = cost_so_far[current] + distance(current, neighbor)

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    return []
```

## Sampling-Based Methods

### Rapidly-exploring Random Trees (RRT)
Effective for high-dimensional spaces and complex environments:

```python
import random

class RRT:
    def __init__(self, start, goal, grid, step_size=1.0):
        self.start = start
        self.goal = goal
        self.grid = grid
        self.step_size = step_size
        self.vertices = [start]
        self.edges = {}

    def plan(self, max_iterations=1000):
        """Plan path using RRT algorithm"""
        for i in range(max_iterations):
            # Sample random point
            rand_point = self.sample_random_point()

            # Find nearest vertex
            nearest = self.nearest_vertex(rand_point)

            # Extend towards random point
            new_point = self.extend_towards(nearest, rand_point)

            if new_point and self.is_valid_position(new_point):
                self.vertices.append(new_point)
                self.edges[new_point] = nearest

                # Check if we're close to goal
                if self.distance(new_point, self.goal) < self.step_size:
                    return self.extract_path(new_point)

        return []  # No path found

    def sample_random_point(self):
        """Sample random point in configuration space"""
        rows, cols = self.grid.shape
        return (random.uniform(0, rows-1), random.uniform(0, cols-1))

    def nearest_vertex(self, point):
        """Find nearest vertex to given point"""
        nearest = self.vertices[0]
        min_dist = self.distance(nearest, point)

        for vertex in self.vertices:
            dist = self.distance(vertex, point)
            if dist < min_dist:
                min_dist = dist
                nearest = vertex

        return nearest

    def extend_towards(self, start, target):
        """Extend from start towards target by step size"""
        dist = self.distance(start, target)
        if dist <= self.step_size:
            return target

        ratio = self.step_size / dist
        new_x = start[0] + ratio * (target[0] - start[0])
        new_y = start[1] + ratio * (target[1] - start[1])

        return (new_x, new_y)

    def is_valid_position(self, pos):
        """Check if position is valid (not in obstacle)"""
        x, y = int(pos[0]), int(pos[1])
        rows, cols = self.grid.shape
        if 0 <= x < rows and 0 <= y < cols:
            return self.grid[x, y] == 0  # 0 = free space, 1 = obstacle
        return False

    def distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def extract_path(self, goal_vertex):
        """Extract path from goal vertex back to start"""
        path = [goal_vertex]
        current = goal_vertex

        while current in self.edges:
            current = self.edges[current]
            path.append(current)

        path.reverse()
        return path
```

## AI-Based Path Planning

### Deep Learning Approaches
Neural networks can learn complex path planning strategies:

```python
import torch
import torch.nn as nn

class PathPlanningNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(PathPlanningNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Example usage for learning path planning
def train_path_planning_network():
    # This would be trained on examples of optimal paths
    # in various environments
    pass
```

## ROS 2 Navigation Stack Integration

### Navigation2 Framework
The Navigation2 stack provides comprehensive path planning capabilities:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus
import time

class PathPlannerNode(Node):
    def __init__(self):
        super().__init__('path_planner_node')

        # Create action client for navigation
        self.nav_to_pose_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

        # Publisher for path visualization
        self.path_pub = self.create_publisher(Path, '/planned_path', 10)

        self.get_logger().info('Path Planner node initialized')

    def plan_to_pose(self, x, y, theta):
        """Plan and execute navigation to specified pose"""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # Convert theta to quaternion
        from tf_transformations import quaternion_from_euler
        quat = quaternion_from_euler(0, 0, theta)
        goal_msg.pose.pose.orientation.x = quat[0]
        goal_msg.pose.pose.orientation.y = quat[1]
        goal_msg.pose.pose.orientation.z = quat[2]
        goal_msg.pose.pose.orientation.w = quat[3]

        self.nav_to_pose_client.wait_for_server()
        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handle result callback"""
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Navigation succeeded!')
        else:
            self.get_logger().info('Navigation failed')

    def feedback_callback(self, feedback_msg):
        """Handle feedback during navigation"""
        feedback = feedback_msg.feedback
        # Process feedback as needed
        pass

def main(args=None):
    rclpy.init(args=args)

    planner = PathPlannerNode()

    # Example: Plan to a specific location
    planner.plan_to_pose(5.0, 5.0, 0.0)

    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    finally:
        planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Isaac Sim Path Planning Integration

### Simulation-Based Planning
Isaac Sim provides tools for testing path planning algorithms:

```python
from omni.isaac.core import World
from omni.isaac.core.utils.prims import get_prim_at_path
from omni.isaac.core.utils.stage import add_reference_to_stage
import numpy as np

class IsaacPathPlanner:
    def __init__(self, world: World):
        self.world = world
        self.navigation_map = None

    def create_navigation_map(self):
        """Create navigation map from Isaac Sim scene"""
        # Get static obstacles from the scene
        # This is a simplified example
        obstacles = self.get_static_obstacles()

        # Create occupancy grid
        resolution = 0.1  # 10cm resolution
        size = (20, 20)  # 20m x 20m area
        self.navigation_map = np.zeros(size)

        # Mark obstacle locations
        for obstacle in obstacles:
            self.mark_obstacle_in_map(obstacle)

    def get_static_obstacles(self):
        """Get static obstacles from Isaac Sim scene"""
        # This would query the Isaac Sim scene for static objects
        pass

    def mark_obstacle_in_map(self, obstacle):
        """Mark obstacle in navigation map"""
        # Convert obstacle position to grid coordinates
        pass

    def plan_path(self, start, goal):
        """Plan path in Isaac Sim environment"""
        # Use the navigation map to plan path
        # This could use any of the algorithms discussed above
        pass
```

## Motion Planning Considerations

### Robot Kinematics
Path planning must consider:
- Robot dimensions and shape
- Kinematic constraints (differential drive, Ackermann, etc.)
- Dynamic constraints (acceleration, velocity limits)

### Environmental Factors
- Static vs. dynamic obstacles
- Uncertainty in map and localization
- Multi-objective optimization (time, energy, safety)

## Performance Metrics

### Completeness
- Whether the algorithm finds a solution if one exists
- Guaranteed to find optimal solution (if one exists)

### Optimality
- Quality of the solution compared to optimal
- Time optimality vs. distance optimality

### Efficiency
- Time complexity and space complexity
- Real-time performance requirements

### Robustness
- Performance in dynamic environments
- Handling of sensor noise and uncertainty

## Best Practices

1. **Hybrid Planning**: Combine global and local planners for best results
2. **Environment Representation**: Choose appropriate map representation for your application
3. **Algorithm Selection**: Match algorithm to environment characteristics
4. **Parameter Tuning**: Carefully tune parameters for your specific robot and environment
5. **Validation**: Test extensively in simulation before deployment

## Exercise

Implement a complete path planning system using Isaac Sim and ROS 2 that:
1. Creates a navigation map from a simulated environment
2. Implements both global (A*) and local (DWA) planning
3. Integrates with the Navigation2 stack
4. Tests the system in various simulated scenarios
5. Evaluates the performance using appropriate metrics

## Summary

Path planning is a fundamental capability for autonomous robots, enabling them to navigate complex environments safely and efficiently. Modern approaches combine classical algorithms with AI techniques, integrated with tools like Isaac Sim and ROS 2 for comprehensive development and testing.