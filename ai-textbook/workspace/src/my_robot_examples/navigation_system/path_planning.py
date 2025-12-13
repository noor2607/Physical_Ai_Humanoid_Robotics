#!/usr/bin/env python3
"""
Path Planning and Navigation System for Isaac Sim Integration
This module implements various path planning algorithms and navigation systems
for robotics applications in Isaac Sim environment.
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import math


@dataclass
class Waypoint:
    """Represents a navigation waypoint"""
    x: float
    y: float
    z: float
    tolerance: float = 0.1  # Acceptance radius
    action: Optional[str] = None  # Optional action at waypoint


@dataclass
class Path:
    """Represents a planned path"""
    waypoints: List[Waypoint]
    total_distance: float = 0.0
    path_id: Optional[str] = None


class PathPlannerType(Enum):
    """Types of path planners available"""
    A_STAR = "a_star"
    RRT = "rrt"
    RRT_STAR = "rrt_star"
    D_STAR_LITE = "d_star_lite"
    VISIBILITY_GRAPH = "visibility_graph"


class GridMap:
    """Represents a 2D occupancy grid for path planning"""

    def __init__(self, width: int, height: int, resolution: float = 1.0, origin: Tuple[float, float] = (0, 0)):
        """
        Initialize grid map

        Args:
            width: Map width in grid cells
            height: Map height in grid cells
            resolution: Size of each grid cell in meters
            origin: Origin coordinates (x, y) in world frame
        """
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin = origin
        self.grid = np.zeros((height, width), dtype=np.uint8)  # 0: free, 255: occupied

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        grid_x = int((x - self.origin[0]) / self.resolution)
        grid_y = int((y - self.origin[1]) / self.resolution)
        return grid_x, grid_y

    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates"""
        x = grid_x * self.resolution + self.origin[0]
        y = grid_y * self.resolution + self.origin[1]
        return x, y

    def is_free(self, x: int, y: int) -> bool:
        """Check if grid cell is free (not occupied)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 0
        return False

    def set_occupied(self, x: int, y: int):
        """Mark grid cell as occupied"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 255

    def set_free(self, x: int, y: int):
        """Mark grid cell as free"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 0


class AStarPlanner:
    """A* path planning algorithm implementation"""

    def __init__(self, grid_map: GridMap):
        self.grid_map = grid_map

    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Plan path using A* algorithm

        Args:
            start: Start coordinates (grid_x, grid_y)
            goal: Goal coordinates (grid_x, grid_y)

        Returns:
            List of grid coordinates forming the path, or None if no path found
        """
        # Check if start or goal are occupied
        if not self.grid_map.is_free(start[0], start[1]) or not self.grid_map.is_free(goal[0], goal[1]):
            return None

        # Initialize open and closed sets
        open_set = {start}
        closed_set = set()

        # Initialize costs
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        # Parent tracking for path reconstruction
        came_from = {}

        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))

            if current == goal:
                # Reconstruct path
                path = self.reconstruct_path(came_from, current)
                return path

            open_set.remove(current)
            closed_set.add(current)

            # Check 8-connected neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    neighbor = (current[0] + dx, current[1] + dy)

                    if not (0 <= neighbor[0] < self.grid_map.width and 0 <= neighbor[1] < self.grid_map.height):
                        continue

                    if neighbor in closed_set or not self.grid_map.is_free(neighbor[0], neighbor[1]):
                        continue

                    # Calculate tentative g_score
                    movement_cost = math.sqrt(dx*dx + dy*dy)
                    tentative_g_score = g_score[current] + movement_cost

                    if neighbor not in open_set:
                        open_set.add(neighbor)
                    elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                        continue

                    # This path is the best until now
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)

        # No path found
        return None

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Calculate heuristic distance (Euclidean)"""
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]  # Reverse to get start -> goal path


class RRTPlanner:
    """Rapidly-exploring Random Tree (RRT) path planning algorithm"""

    def __init__(self, grid_map: GridMap, max_iterations: int = 1000, step_size: float = 1.0):
        self.grid_map = grid_map
        self.max_iterations = max_iterations
        self.step_size = step_size

    def plan_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Plan path using RRT algorithm

        Args:
            start: Start coordinates (grid_x, grid_y)
            goal: Goal coordinates (grid_x, grid_y)

        Returns:
            List of grid coordinates forming the path, or None if no path found
        """
        if not self.grid_map.is_free(start[0], start[1]) or not self.grid_map.is_free(goal[0], goal[1]):
            return None

        # Tree structure: {node: parent}
        tree = {start: None}
        nodes = [start]

        for _ in range(self.max_iterations):
            # Sample random point
            rand_point = self.sample_random_point()

            # Find nearest node in tree
            nearest_node = self.find_nearest_node(nodes, rand_point)

            # Steer towards random point
            new_node = self.steer(nearest_node, rand_point)

            # Check if path is collision-free
            if self.is_collision_free(nearest_node, new_node):
                # Add new node to tree
                tree[new_node] = nearest_node
                nodes.append(new_node)

                # Check if we can connect to goal
                if self.is_collision_free(new_node, goal):
                    tree[goal] = new_node
                    path = self.reconstruct_path(tree, start, goal)
                    return path

        return None

    def sample_random_point(self) -> Tuple[int, int]:
        """Sample a random point in the grid"""
        x = np.random.randint(0, self.grid_map.width)
        y = np.random.randint(0, self.grid_map.height)
        return (x, y)

    def find_nearest_node(self, nodes: List[Tuple[int, int]], point: Tuple[int, int]) -> Tuple[int, int]:
        """Find the nearest node in the tree to the given point"""
        nearest = nodes[0]
        min_dist = self.distance(nodes[0], point)

        for node in nodes[1:]:
            dist = self.distance(node, point)
            if dist < min_dist:
                min_dist = dist
                nearest = node

        return nearest

    def steer(self, from_node: Tuple[int, int], to_point: Tuple[int, int]) -> Tuple[int, int]:
        """Steer from from_node towards to_point by step_size"""
        dx = to_point[0] - from_node[0]
        dy = to_point[1] - from_node[1]
        dist = math.sqrt(dx*dx + dy*dy)

        if dist <= self.step_size:
            return to_point

        # Move by step_size in the direction
        scale = self.step_size / dist
        new_x = int(from_node[0] + dx * scale)
        new_y = int(from_node[1] + dy * scale)

        # Ensure within bounds
        new_x = max(0, min(self.grid_map.width - 1, new_x))
        new_y = max(0, min(self.grid_map.height - 1, new_y))

        return (new_x, new_y)

    def is_collision_free(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if path from start to end is collision-free"""
        # Use Bresenham's line algorithm to check all points on the line
        points = self.bresenham_line(start[0], start[1], end[0], end[1])

        for x, y in points:
            if not self.grid_map.is_free(x, y):
                return False

        return True

    def bresenham_line(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """Bresenham's line algorithm to get all points on a line"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1

        if dx > dy:
            err = dx / 2.0
            while x != x1:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        points.append((x, y))
        return points

    def distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def reconstruct_path(self, tree: Dict, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from tree"""
        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = tree[current]

        return path[::-1]  # Reverse to get start -> goal


class NavigationSystem:
    """Main navigation system that integrates path planning and execution"""

    def __init__(self, planner_type: PathPlannerType = PathPlannerType.A_STAR):
        """
        Initialize navigation system

        Args:
            planner_type: Type of path planner to use
        """
        self.planner_type = planner_type
        self.grid_map = None
        self.current_path = None
        self.current_waypoint_idx = 0
        self.robot_position = np.array([0.0, 0.0, 0.0])  # x, y, theta
        self.path_following_active = False

    def set_map(self, grid_map: GridMap):
        """Set the occupancy grid map for navigation"""
        self.grid_map = grid_map

    def plan_path(self, start_pos: Tuple[float, float], goal_pos: Tuple[float, float]) -> Optional[Path]:
        """
        Plan a path from start to goal position

        Args:
            start_pos: Start position (x, y) in world coordinates
            goal_pos: Goal position (x, y) in world coordinates

        Returns:
            Path object or None if no path found
        """
        if self.grid_map is None:
            raise ValueError("Grid map not set")

        # Convert world coordinates to grid coordinates
        start_grid = self.grid_map.world_to_grid(start_pos[0], start_pos[1])
        goal_grid = self.grid_map.world_to_grid(goal_pos[0], goal_pos[1])

        # Create planner based on type
        if self.planner_type == PathPlannerType.A_STAR:
            planner = AStarPlanner(self.grid_map)
        elif self.planner_type == PathPlannerType.RRT:
            planner = RRTPlanner(self.grid_map)
        else:
            raise ValueError(f"Unsupported planner type: {self.planner_type}")

        # Plan path
        grid_path = planner.plan_path(start_grid, goal_grid)

        if grid_path is None:
            return None

        # Convert grid path back to world coordinates
        waypoints = []
        total_distance = 0.0

        for i, (grid_x, grid_y) in enumerate(grid_path):
            x, y = self.grid_map.grid_to_world(grid_x, grid_y)

            # Calculate distance to next point for total distance
            if i > 0:
                prev_x, prev_y = self.grid_map.grid_to_world(grid_path[i-1][0], grid_path[i-1][1])
                dist = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                total_distance += dist

            waypoint = Waypoint(x=x, y=y, z=0.0)  # Assuming 2D navigation
            waypoints.append(waypoint)

        path = Path(waypoints=waypoints, total_distance=total_distance)
        self.current_path = path
        self.current_waypoint_idx = 0
        return path

    def update_robot_position(self, position: np.ndarray):
        """
        Update the robot's current position

        Args:
            position: Robot position as [x, y, theta]
        """
        self.robot_position = position

    def get_next_waypoint(self) -> Optional[Waypoint]:
        """Get the next waypoint in the current path"""
        if self.current_path is None or self.current_waypoint_idx >= len(self.current_path.waypoints):
            return None

        return self.current_path.waypoints[self.current_waypoint_idx]

    def is_waypoint_reached(self, tolerance: float = 0.1) -> bool:
        """Check if the current waypoint has been reached"""
        if self.current_path is None or self.current_waypoint_idx >= len(self.current_path.waypoints):
            return False

        current_waypoint = self.current_path.waypoints[self.current_waypoint_idx]
        distance = math.sqrt(
            (self.robot_position[0] - current_waypoint.x)**2 +
            (self.robot_position[1] - current_waypoint.y)**2
        )

        return distance <= tolerance

    def advance_to_next_waypoint(self):
        """Move to the next waypoint in the path"""
        if self.current_path is not None and self.current_waypoint_idx < len(self.current_path.waypoints) - 1:
            self.current_waypoint_idx += 1

    def is_path_complete(self) -> bool:
        """Check if the entire path has been completed"""
        return (self.current_path is not None and
                self.current_waypoint_idx >= len(self.current_path.waypoints) - 1)

    def stop_navigation(self):
        """Stop the navigation process"""
        self.path_following_active = False
        self.current_path = None
        self.current_waypoint_idx = 0


class IsaacNavigationNode:
    """
    ROS 2 node wrapper for navigation system that integrates with Isaac Sim
    """

    def __init__(self):
        # Initialize navigation system
        self.navigation_system = NavigationSystem(planner_type=PathPlannerType.A_STAR)

        # For Isaac Sim integration, you would:
        # 1. Subscribe to odometry topics from Isaac Sim
        # 2. Subscribe to sensor topics for mapping
        # 3. Publish velocity commands to control the robot
        # 4. Handle coordinate frame transformations

        print("Isaac Navigation node initialized")

    def set_map_from_isaac(self, occupancy_grid):
        """
        Set the map from Isaac Sim occupancy grid
        This would be called when receiving map data from Isaac Sim
        """
        # Convert Isaac Sim occupancy grid to our GridMap format
        # This is a simplified example - in practice, you'd need to convert the actual grid data
        pass

    def navigate_to_goal(self, goal_x: float, goal_y: float) -> bool:
        """
        Navigate to a specific goal position

        Args:
            goal_x: Goal X coordinate in world frame
            goal_y: Goal Y coordinate in world frame

        Returns:
            True if navigation started successfully, False otherwise
        """
        # Get current robot position (would come from Isaac Sim odometry)
        current_pos = (self.navigation_system.robot_position[0],
                      self.navigation_system.robot_position[1])

        # Plan path
        path = self.navigation_system.plan_path(current_pos, (goal_x, goal_y))

        if path is not None:
            print(f"Path planned with {len(path.waypoints)} waypoints, total distance: {path.total_distance:.2f}m")
            self.navigation_system.path_following_active = True
            return True
        else:
            print("Failed to plan path to goal")
            return False

    def update_navigation(self):
        """
        Update navigation based on current robot position
        This would be called in a control loop
        """
        if not self.navigation_system.path_following_active:
            return

        # Get current robot position from Isaac Sim (simplified)
        # In practice, this would come from odometry topic
        current_pos = self.navigation_system.robot_position
        pos_2d = (current_pos[0], current_pos[1])

        # Check if current waypoint is reached
        if self.navigation_system.is_waypoint_reached():
            print(f"Waypoint {self.navigation_system.current_waypoint_idx} reached")

            # Move to next waypoint
            self.navigation_system.advance_to_next_waypoint()

            # Check if path is complete
            if self.navigation_system.is_path_complete():
                print("Navigation complete!")
                self.navigation_system.path_following_active = False
                return

        # Get next waypoint for control purposes
        next_waypoint = self.navigation_system.get_next_waypoint()
        if next_waypoint:
            # Calculate control commands to reach next waypoint
            # This would involve sending velocity commands to Isaac Sim
            dx = next_waypoint.x - current_pos[0]
            dy = next_waypoint.y - current_pos[1]

            # Simple proportional controller (simplified)
            linear_vel = min(0.5, math.sqrt(dx*dx + dy*dy))  # Limit to 0.5 m/s
            angular_vel = math.atan2(dy, dx) - current_pos[2]  # Heading error

            # In Isaac Sim, you would publish these velocities to the robot
            print(f"Commanding: linear_vel={linear_vel:.2f}, angular_vel={angular_vel:.2f}")


def main():
    """
    Example usage of the path planning and navigation system
    """
    print("Initializing Path Planning and Navigation System...")

    # Create a simple grid map (10x10 grid with 0.5m resolution)
    grid_map = GridMap(width=20, height=20, resolution=0.5, origin=(-5.0, -5.0))

    # Add some obstacles to the map (for demonstration)
    for i in range(8, 12):
        for j in range(8, 12):
            grid_map.set_occupied(i, j)  # Obstacle in the center

    # Initialize navigation system
    nav_system = NavigationSystem(planner_type=PathPlannerType.A_STAR)
    nav_system.set_map(grid_map)

    # Plan a path
    start_pos = (-4.0, -4.0)  # Start at bottom-left
    goal_pos = (4.0, 4.0)     # Goal at top-right

    print(f"Planning path from {start_pos} to {goal_pos}")
    path = nav_system.plan_path(start_pos, goal_pos)

    if path:
        print(f"Path found with {len(path.waypoints)} waypoints")
        print(f"Total path distance: {path.total_distance:.2f}m")

        # Simulate robot movement along path
        print("\nSimulating robot navigation:")
        for i, waypoint in enumerate(path.waypoints):
            print(f"  Waypoint {i}: ({waypoint.x:.2f}, {waypoint.y:.2f})")
    else:
        print("No path found!")

    # Create Isaac Navigation Node
    isaac_nav_node = IsaacNavigationNode()

    print("\nNavigation system ready for Isaac Sim integration")
    print("The system can now plan paths and navigate robots in simulation")
    print("In Isaac Sim, this would connect to robot odometry and control topics")


if __name__ == "__main__":
    main()