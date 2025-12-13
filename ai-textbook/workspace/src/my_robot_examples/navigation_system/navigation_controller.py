#!/usr/bin/env python3
"""
Navigation Controller for Isaac Sim Integration
This module implements navigation controllers that follow planned paths
and handle dynamic obstacle avoidance for robotics applications.
"""

import numpy as np
import math
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class RobotState:
    """Current state of the robot"""
    position: np.ndarray  # [x, y, theta] in world frame
    velocity: np.ndarray  # [vx, vy, omega] in world frame
    linear_speed: float = 0.0
    angular_speed: float = 0.0


class ControlMode(Enum):
    """Navigation control modes"""
    PATH_FOLLOWING = "path_following"
    OBSTACLE_AVOIDANCE = "obstacle_avoidance"
    PURE_PURSUIT = "pure_pursuit"
    DYNAMIC_WINDOW = "dynamic_window"


class PurePursuitController:
    """Pure pursuit path following controller"""

    def __init__(self, lookahead_distance: float = 1.0, max_linear_speed: float = 1.0, max_angular_speed: float = 1.0):
        """
        Initialize pure pursuit controller

        Args:
            lookahead_distance: Distance to look ahead on the path
            max_linear_speed: Maximum linear speed (m/s)
            max_angular_speed: Maximum angular speed (rad/s)
        """
        self.lookahead_distance = lookahead_distance
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.path = None
        self.current_path_idx = 0

    def set_path(self, path):
        """Set the path to follow"""
        self.path = path
        self.current_path_idx = 0

    def calculate_control(self, robot_state: RobotState) -> Tuple[float, float]:
        """
        Calculate linear and angular velocities to follow the path

        Args:
            robot_state: Current robot state

        Returns:
            Tuple of (linear_velocity, angular_velocity)
        """
        if self.path is None or len(self.path.waypoints) == 0:
            return 0.0, 0.0

        # Find the closest point on the path
        closest_idx = self.find_closest_waypoint(robot_state.position)
        self.current_path_idx = closest_idx

        # Find the lookahead point
        lookahead_point = self.find_lookahead_point(robot_state.position)

        if lookahead_point is None:
            return 0.0, 0.0

        # Calculate desired heading to lookahead point
        dx = lookahead_point[0] - robot_state.position[0]
        dy = lookahead_point[1] - robot_state.position[1]
        desired_heading = math.atan2(dy, dx)

        # Calculate heading error
        heading_error = desired_heading - robot_state.position[2]
        # Normalize angle to [-pi, pi]
        heading_error = math.atan2(math.sin(heading_error), math.cos(heading_error))

        # Calculate control outputs
        linear_vel = min(self.max_linear_speed, math.sqrt(dx*dx + dy*dy))
        angular_vel = 2.0 * heading_error  # Proportional controller

        # Limit angular velocity
        angular_vel = max(-self.max_angular_speed, min(self.max_angular_speed, angular_vel))

        return linear_vel, angular_vel

    def find_closest_waypoint(self, robot_pos: np.ndarray) -> int:
        """Find the closest waypoint to the robot"""
        if self.path is None:
            return 0

        min_dist = float('inf')
        closest_idx = 0

        for i, waypoint in enumerate(self.path.waypoints):
            dist = math.sqrt((robot_pos[0] - waypoint.x)**2 + (robot_pos[1] - waypoint.y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        return closest_idx

    def find_lookahead_point(self, robot_pos: np.ndarray) -> Optional[Tuple[float, float]]:
        """Find the lookahead point on the path"""
        if self.path is None:
            return None

        # Start from the closest point and look ahead
        start_idx = self.current_path_idx
        for i in range(start_idx, len(self.path.waypoints)):
            waypoint = self.path.waypoints[i]
            dist = math.sqrt((robot_pos[0] - waypoint.x)**2 + (robot_pos[1] - waypoint.y)**2)

            if dist >= self.lookahead_distance:
                return (waypoint.x, waypoint.y)

        # If no point is far enough, return the last point
        if self.path.waypoints:
            last_point = self.path.waypoints[-1]
            return (last_point.x, last_point.y)

        return None


class DynamicWindowApproach:
    """Dynamic Window Approach for local path planning and obstacle avoidance"""

    def __init__(self, robot_radius: float = 0.3, max_speed: float = 1.0, min_speed: float = 0.1,
                 max_angular_speed: float = 1.0, min_angular_speed: float = -1.0,
                 max_accel: float = 0.5, max_decel: float = -0.5,
                 max_angular_accel: float = 1.0, dt: float = 0.1):
        """
        Initialize Dynamic Window Approach controller

        Args:
            robot_radius: Radius of the robot (m)
            max_speed: Maximum linear speed (m/s)
            min_speed: Minimum linear speed (m/s)
            max_angular_speed: Maximum angular speed (rad/s)
            min_angular_speed: Minimum angular speed (rad/s)
            max_accel: Maximum linear acceleration (m/s^2)
            max_decel: Maximum linear deceleration (m/s^2)
            max_angular_accel: Maximum angular acceleration (rad/s^2)
            dt: Time step for simulation (s)
        """
        self.robot_radius = robot_radius
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.max_angular_speed = max_angular_speed
        self.min_angular_speed = min_angular_speed
        self.max_accel = max_accel
        self.max_decel = max_decel
        self.max_angular_accel = max_angular_accel
        self.dt = dt

    def calculate_control(self, robot_state: RobotState, goal: Tuple[float, float],
                         obstacles: np.ndarray) -> Tuple[float, float]:
        """
        Calculate control commands using Dynamic Window Approach

        Args:
            robot_state: Current robot state
            goal: Goal position (x, y)
            obstacles: Array of obstacle positions [[x1, y1], [x2, y2], ...]

        Returns:
            Tuple of (linear_velocity, angular_velocity)
        """
        # Calculate velocity windows
        vs = self.calculate_velocity_space()
        vd = self.calculate_dynamic_window(robot_state)

        # Find best velocity in the intersection of both windows
        best_vel = (0.0, 0.0)
        best_value = float('-inf')

        for v in np.arange(vd[0], vd[1], (vd[1] - vd[0]) / 10):  # Linear velocity samples
            for omega in np.arange(vd[2], vd[3], (vd[3] - vd[2]) / 10):  # Angular velocity samples
                # Simulate trajectory
                traj = self.predict_trajectory(robot_state, v, omega)

                # Evaluate trajectory
                heading = self.calculate_heading_score(traj, goal)
                dist = self.calculate_distance_score(traj, obstacles)
                vel = self.calculate_velocity_score(v)

                # Combined score
                score = 0.3 * heading + 0.6 * dist + 0.1 * vel

                if score > best_value:
                    best_value = score
                    best_vel = (v, omega)

        return best_vel

    def calculate_velocity_space(self) -> Tuple[float, float, float, float]:
        """Calculate velocity space [v_min, v_max, omega_min, omega_max]"""
        return (self.min_speed, self.max_speed,
                self.min_angular_speed, self.max_angular_speed)

    def calculate_dynamic_window(self, robot_state: RobotState) -> Tuple[float, float, float, float]:
        """Calculate dynamic window based on current velocity and constraints"""
        v_min = max(self.min_speed, robot_state.linear_speed - self.max_decel * self.dt)
        v_max = min(self.max_speed, robot_state.linear_speed + self.max_accel * self.dt)
        omega_min = max(self.min_angular_speed,
                       robot_state.angular_speed - self.max_angular_accel * self.dt)
        omega_max = min(self.max_angular_speed,
                       robot_state.angular_speed + self.max_angular_accel * self.dt)

        return (v_min, v_max, omega_min, omega_max)

    def predict_trajectory(self, robot_state: RobotState, v: float, omega: float) -> np.ndarray:
        """Predict trajectory based on velocity commands"""
        trajectory = []
        state = robot_state.position.copy()

        for _ in range(int(1.0 / self.dt)):  # Predict for 1 second
            # Update position based on motion model
            new_x = state[0] + v * math.cos(state[2]) * self.dt
            new_y = state[1] + v * math.sin(state[2]) * self.dt
            new_theta = state[2] + omega * self.dt

            state = np.array([new_x, new_y, new_theta])
            trajectory.append(state.copy())

        return np.array(trajectory)

    def calculate_heading_score(self, trajectory: np.ndarray, goal: Tuple[float, float]) -> float:
        """Calculate score based on how much the trajectory points toward the goal"""
        if len(trajectory) == 0:
            return 0.0

        last_pos = trajectory[-1]
        goal_angle = math.atan2(goal[1] - last_pos[1], goal[0] - last_pos[0])
        heading_diff = abs(goal_angle - last_pos[2])

        # Convert to score (0 to 1, where 1 is perfect heading)
        return 1.0 - min(heading_diff / math.pi, 1.0)

    def calculate_distance_score(self, trajectory: np.ndarray, obstacles: np.ndarray) -> float:
        """Calculate score based on distance to obstacles"""
        if len(trajectory) == 0 or len(obstacles) == 0:
            return 1.0

        min_dist = float('inf')
        for point in trajectory:
            for obs in obstacles:
                dist = math.sqrt((point[0] - obs[0])**2 + (point[1] - obs[1])**2)
                if dist < min_dist:
                    min_dist = dist

        # Return score based on distance (higher score for safer distance)
        safety_dist = 2.0 * self.robot_radius  # Minimum safe distance
        if min_dist >= safety_dist:
            return 1.0
        else:
            return min_dist / safety_dist

    def calculate_velocity_score(self, v: float) -> float:
        """Calculate score based on velocity (prefer higher velocities)"""
        return v / self.max_speed


class NavigationController:
    """Main navigation controller that integrates different control strategies"""

    def __init__(self, control_mode: ControlMode = ControlMode.PURE_PURSUIT):
        """
        Initialize navigation controller

        Args:
            control_mode: Control strategy to use
        """
        self.control_mode = control_mode
        self.pure_pursuit = PurePursuitController()
        self.dwa = DynamicWindowApproach()
        self.current_goal = None
        self.robot_state = RobotState(
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([0.0, 0.0, 0.0])
        )
        self.path = None
        self.obstacles = np.array([])

    def set_path(self, path):
        """Set the path to follow"""
        self.path = path
        self.pure_pursuit.set_path(path)

    def set_goal(self, goal: Tuple[float, float]):
        """Set the navigation goal"""
        self.current_goal = goal

    def set_obstacles(self, obstacles: np.ndarray):
        """Set obstacle positions for collision avoidance"""
        self.obstacles = obstacles

    def update_robot_state(self, position: np.ndarray, velocity: np.ndarray = None):
        """Update the robot's current state"""
        self.robot_state.position = position
        if velocity is not None:
            self.robot_state.velocity = velocity

    def calculate_control_commands(self) -> Tuple[float, float]:
        """
        Calculate control commands based on current state and control mode

        Returns:
            Tuple of (linear_velocity, angular_velocity)
        """
        if self.control_mode == ControlMode.PURE_PURSUIT:
            return self.pure_pursuit.calculate_control(self.robot_state)
        elif self.control_mode == ControlMode.DYNAMIC_WINDOW:
            if self.current_goal is not None and self.obstacles.size > 0:
                return self.dwa.calculate_control(
                    self.robot_state,
                    self.current_goal,
                    self.obstacles
                )
            else:
                # Fallback to pure pursuit if no obstacles or goal
                return self.pure_pursuit.calculate_control(self.robot_state)
        else:
            # Default to pure pursuit
            return self.pure_pursuit.calculate_control(self.robot_state)

    def is_goal_reached(self, tolerance: float = 0.2) -> bool:
        """Check if the robot has reached the goal"""
        if self.current_goal is None:
            return False

        dist_to_goal = math.sqrt(
            (self.robot_state.position[0] - self.current_goal[0])**2 +
            (self.robot_state.position[1] - self.current_goal[1])**2
        )

        return dist_to_goal <= tolerance

    def switch_control_mode(self, new_mode: ControlMode):
        """Switch to a different control mode"""
        self.control_mode = new_mode


class IsaacNavigationController:
    """
    Isaac Sim specific navigation controller that integrates with Isaac's control systems
    """

    def __init__(self):
        # Initialize the navigation controller
        self.nav_controller = NavigationController(control_mode=ControlMode.PURE_PURSUIT)

        # For Isaac Sim integration, you would:
        # 1. Interface with Isaac's differential base controller
        # 2. Subscribe to LIDAR and other sensor data
        # 3. Handle coordinate transformations between Isaac frames
        # 4. Interface with Isaac's physics engine for accurate simulation

        print("Isaac Navigation Controller initialized")

    def update_from_isaac(self, robot_position: np.ndarray, sensor_data: dict):
        """
        Update controller with data from Isaac Sim

        Args:
            robot_position: Robot position [x, y, z, qx, qy, qz, qw] from Isaac
            sensor_data: Dictionary containing sensor readings from Isaac
        """
        # Convert Isaac position (with quaternion) to 2D pose [x, y, theta]
        x = robot_position[0]
        y = robot_position[1]
        # Convert quaternion to yaw angle
        qw, qx, qy, qz = robot_position[6], robot_position[3], robot_position[4], robot_position[5]
        theta = math.atan2(2*(qw*qz + qx*qy), 1 - 2*(qy*qy + qz*qz))

        position_2d = np.array([x, y, theta])
        self.nav_controller.update_robot_state(position_2d)

        # Process sensor data (e.g., LIDAR) for obstacle detection
        if 'lidar' in sensor_data:
            # Convert LIDAR data to obstacle positions
            lidar_ranges = sensor_data['lidar']
            # Process to get obstacle positions relative to robot
            # This is a simplified example
            pass

    def get_control_commands(self) -> Tuple[float, float]:
        """
        Get control commands to send to Isaac Sim

        Returns:
            Tuple of (linear_velocity, angular_velocity)
        """
        return self.nav_controller.calculate_control_commands()

    def set_navigation_goal(self, goal_x: float, goal_y: float):
        """
        Set a navigation goal in Isaac Sim world coordinates

        Args:
            goal_x: Goal X coordinate in Isaac world frame
            goal_y: Goal Y coordinate in Isaac world frame
        """
        self.nav_controller.set_goal((goal_x, goal_y))

    def set_navigation_path(self, path):
        """
        Set a pre-planned path for the controller to follow

        Args:
            path: Path object with waypoints
        """
        self.nav_controller.set_path(path)

    def is_navigation_complete(self) -> bool:
        """
        Check if navigation to goal is complete

        Returns:
            True if navigation is complete, False otherwise
        """
        return self.nav_controller.is_goal_reached()


def main():
    """
    Example usage of the navigation controller
    """
    print("Initializing Navigation Controller...")

    # Create a navigation controller
    nav_controller = NavigationController(control_mode=ControlMode.PURE_PURSUIT)

    # Simulate robot position updates
    robot_pos = np.array([0.0, 0.0, 0.0])  # x, y, theta
    nav_controller.update_robot_state(robot_pos)

    # Set a goal
    nav_controller.set_goal((5.0, 5.0))

    print("Navigation controller ready for Isaac Sim integration")
    print("The controller can follow paths and avoid obstacles in simulation")
    print("In Isaac Sim, this would connect to robot sensors and control interfaces")

    # Example of switching control modes
    print(f"Current mode: {nav_controller.control_mode}")
    nav_controller.switch_control_mode(ControlMode.DYNAMIC_WINDOW)
    print(f"Switched to mode: {nav_controller.control_mode}")


if __name__ == "__main__":
    main()