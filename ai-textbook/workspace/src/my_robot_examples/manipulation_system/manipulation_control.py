#!/usr/bin/env python3
"""
Manipulation and Control System for Isaac Sim Integration
This module implements robotic manipulation algorithms, grasp planning,
and control systems for manipulation tasks in Isaac Sim environment.
"""

import numpy as np
import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import time


@dataclass
class ManipulatorJointState:
    """Represents the state of manipulator joints"""
    positions: List[float]      # Joint positions in radians
    velocities: List[float]     # Joint velocities in rad/s
    efforts: List[float]        # Joint efforts in Nm


@dataclass
class ManipulatorState:
    """Represents the state of the manipulator"""
    joint_state: ManipulatorJointState
    ee_pose: np.ndarray         # End-effector pose [x, y, z, qx, qy, qz, qw]
    ee_twist: np.ndarray        # End-effector twist [vx, vy, vz, wx, wy, wz]


@dataclass
class GraspPoint:
    """Represents a potential grasp point on an object"""
    position: np.ndarray        # [x, y, z] position in world frame
    orientation: np.ndarray     # [qx, qy, qz, qw] orientation quaternion
    approach_direction: np.ndarray  # [x, y, z] approach direction
    grasp_width: float          # Required gripper width
    quality: float              # Grasp quality score (0-1)


@dataclass
class ManipulationTask:
    """Represents a manipulation task"""
    task_type: str              # 'pick', 'place', 'move', 'grasp', etc.
    target_object: str          # Name or ID of target object
    target_pose: np.ndarray     # Target pose [x, y, z, qx, qy, qz, qw]
    pre_grasp_offset: float = 0.1  # Distance before grasp
    post_grasp_offset: float = 0.1 # Distance after grasp


class ManipulationMode(Enum):
    """Manipulation control modes"""
    JOINT_SPACE = "joint_space"
    CARTESIAN_SPACE = "cartesian_space"
    IMITATION_LEARNING = "imitation_learning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"


class InverseKinematicsSolver:
    """Inverse kinematics solver for manipulator control"""

    def __init__(self, joint_limits: List[Tuple[float, float]], max_iterations: int = 100, tolerance: float = 1e-4):
        """
        Initialize IK solver

        Args:
            joint_limits: List of (min, max) tuples for each joint
            max_iterations: Maximum number of iterations for IK solution
            tolerance: Position/orientation tolerance for convergence
        """
        self.joint_limits = joint_limits
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def compute_jacobian(self, joint_positions: List[float], ee_link_idx: int = -1) -> np.ndarray:
        """
        Compute the Jacobian matrix for the manipulator
        This is a simplified implementation - in practice, you'd use a more sophisticated method
        """
        # This is a placeholder - in a real implementation, you'd compute the actual Jacobian
        # based on the manipulator's kinematic structure
        n_joints = len(joint_positions)
        jacobian = np.zeros((6, n_joints))  # 6 DoF: 3 translation + 3 rotation

        # Simplified Jacobian computation (would need actual kinematic model in practice)
        for i in range(n_joints):
            # Compute column i of Jacobian
            # This is a placeholder implementation
            jacobian[:3, i] = np.random.rand(3)  # Translation part
            jacobian[3:, i] = np.random.rand(3)  # Rotation part

        return jacobian

    def solve_ik(self, target_pose: np.ndarray, current_joints: List[float]) -> Optional[List[float]]:
        """
        Solve inverse kinematics using Jacobian transpose method

        Args:
            target_pose: Target end-effector pose [x, y, z, qx, qy, qz, qw]
            current_joints: Current joint positions

        Returns:
            List of joint angles that achieve the target pose, or None if no solution found
        """
        joints = np.array(current_joints, dtype=float)

        for iteration in range(self.max_iterations):
            # Forward kinematics to get current EE pose (simplified)
            current_ee_pose = self.forward_kinematics(joints)

            # Calculate pose error
            pos_error = target_pose[:3] - current_ee_pose[:3]
            rot_error = self.quaternion_difference(target_pose[3:], current_ee_pose[3:])

            # Check if error is within tolerance
            if np.linalg.norm(pos_error) < self.tolerance and np.linalg.norm(rot_error) < self.tolerance:
                # Check joint limits
                if self.check_joint_limits(joints):
                    return joints.tolist()

            # Compute Jacobian
            jacobian = self.compute_jacobian(joints.tolist())

            # Compute pose error vector
            error = np.concatenate([pos_error, rot_error])

            # Update joint angles using Jacobian transpose method
            # In practice, you might use pseudoinverse or damped least squares
            joint_delta = 0.1 * jacobian.T @ error
            joints += joint_delta

            # Apply joint limits
            for i, (min_limit, max_limit) in enumerate(self.joint_limits):
                joints[i] = np.clip(joints[i], min_limit, max_limit)

        # No solution found within iterations
        return None

    def forward_kinematics(self, joint_positions: np.ndarray) -> np.ndarray:
        """
        Compute forward kinematics to get end-effector pose
        This is a simplified implementation
        """
        # Simplified forward kinematics - in practice, you'd use the actual kinematic model
        # This is just a placeholder
        ee_pos = np.array([0.0, 0.0, 0.0])
        ee_quat = np.array([0.0, 0.0, 0.0, 1.0])  # Identity quaternion

        # Add effect of each joint (simplified)
        for i, angle in enumerate(joint_positions):
            # This is a placeholder - real FK would depend on manipulator structure
            ee_pos[0] += 0.1 * math.cos(angle)
            ee_pos[1] += 0.1 * math.sin(angle)

        return np.concatenate([ee_pos, ee_quat])

    def quaternion_difference(self, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        """Calculate the difference between two quaternions"""
        # Convert quaternion difference to axis-angle representation
        # This is a simplified approach
        q_diff = self.quaternion_multiply(q1, self.quaternion_inverse(q2))
        return self.quaternion_to_axis_angle(q_diff)

    def quaternion_multiply(self, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        """Multiply two quaternions"""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

        return np.array([w, x, y, z])

    def quaternion_inverse(self, q: np.ndarray) -> np.ndarray:
        """Calculate inverse of a quaternion"""
        q_inv = q.copy()
        q_inv[1:] = -q_inv[1:]  # Negate vector part
        norm_sq = np.dot(q, q)
        return q_inv / norm_sq if norm_sq != 0 else q_inv

    def quaternion_to_axis_angle(self, q: np.ndarray) -> np.ndarray:
        """Convert quaternion to axis-angle representation"""
        angle = 2 * math.acos(max(-1, min(1, q[0])))  # w component
        s = math.sqrt(1 - q[0]**2) if abs(q[0]) < 1 else 0

        if s < 1e-6:  # When angle is small
            return np.array([0, 0, 0])

        axis = q[1:] / s
        return angle * axis

    def check_joint_limits(self, joints: np.ndarray) -> bool:
        """Check if joint angles are within limits"""
        for i, (min_limit, max_limit) in enumerate(self.joint_limits):
            if joints[i] < min_limit or joints[i] > max_limit:
                return False
        return True


class GraspPlanner:
    """Grasp planning for robotic manipulation"""

    def __init__(self, gripper_width_range: Tuple[float, float] = (0.0, 0.1)):
        """
        Initialize grasp planner

        Args:
            gripper_width_range: Min/max gripper width in meters
        """
        self.min_gripper_width = gripper_width_range[0]
        self.max_gripper_width = gripper_width_range[1]

    def plan_grasps(self, object_info: Dict) -> List[GraspPoint]:
        """
        Plan potential grasps for an object

        Args:
            object_info: Dictionary containing object information
                        Expected keys: 'pose', 'dimensions', 'surface_points', etc.

        Returns:
            List of potential grasp points
        """
        grasps = []

        # Get object properties
        obj_pose = object_info.get('pose', np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]))
        obj_dims = object_info.get('dimensions', np.array([0.1, 0.1, 0.1]))

        # Generate grasp points based on object shape
        if object_info.get('shape', 'box') == 'box':
            grasps.extend(self._plan_box_grasps(obj_pose, obj_dims))
        elif object_info.get('shape', 'box') == 'cylinder':
            grasps.extend(self._plan_cylinder_grasps(obj_pose, obj_dims))
        else:  # sphere or other
            grasps.extend(self._plan_sphere_grasps(obj_pose, obj_dims))

        # Filter grasps based on gripper width
        valid_grasps = []
        for grasp in grasps:
            if self.min_gripper_width <= grasp.grasp_width <= self.max_gripper_width:
                valid_grasps.append(grasp)

        # Sort by quality (highest first)
        valid_grasps.sort(key=lambda g: g.quality, reverse=True)

        return valid_grasps

    def _plan_box_grasps(self, obj_pose: np.ndarray, dimensions: np.ndarray) -> List[GraspPoint]:
        """Plan grasps for a box-shaped object"""
        grasps = []

        # Calculate corner positions in object frame
        half_dims = dimensions / 2.0
        corners = [
            np.array([half_dims[0], half_dims[1], half_dims[2]]),
            np.array([half_dims[0], half_dims[1], -half_dims[2]]),
            np.array([half_dims[0], -half_dims[1], half_dims[2]]),
            np.array([half_dims[0], -half_dims[1], -half_dims[2]]),
            np.array([-half_dims[0], half_dims[1], half_dims[2]]),
            np.array([-half_dims[0], half_dims[1], -half_dims[2]]),
            np.array([-half_dims[0], -half_dims[1], half_dims[2]]),
            np.array([-half_dims[0], -half_dims[1], -half_dims[2]])
        ]

        # Generate grasps from corners
        for i, corner in enumerate(corners):
            # Transform corner to world frame
            world_pos = self._transform_point(corner, obj_pose)

            # Create grasp with appropriate orientation
            # For box grasps, align with surface normals
            if abs(corner[0]) == half_dims[0]:  # Side along x-axis
                orientation = self._align_with_surface_normal(obj_pose[3:], np.array([1, 0, 0]) if corner[0] > 0 else np.array([-1, 0, 0]))
            elif abs(corner[1]) == half_dims[1]:  # Side along y-axis
                orientation = self._align_with_surface_normal(obj_pose[3:], np.array([0, 1, 0]) if corner[1] > 0 else np.array([0, -1, 0]))
            else:  # Side along z-axis
                orientation = self._align_with_surface_normal(obj_pose[3:], np.array([0, 0, 1]) if corner[2] > 0 else np.array([0, 0, -1]))

            grasp = GraspPoint(
                position=world_pos,
                orientation=orientation,
                approach_direction=self._calculate_approach_direction(orientation),
                grasp_width=max(dimensions[1], dimensions[2]) * 0.8,  # Approximate grasp width
                quality=0.8  # High quality for corner grasp
            )
            grasps.append(grasp)

        return grasps

    def _plan_cylinder_grasps(self, obj_pose: np.ndarray, dimensions: np.ndarray) -> List[GraspPoint]:
        """Plan grasps for a cylindrical object"""
        grasps = []

        # Top and bottom center grasps
        radius = dimensions[0] / 2.0
        height = dimensions[2]

        # Top center
        top_pos = np.array([obj_pose[0], obj_pose[1], obj_pose[2] + height/2.0])
        top_grasp = GraspPoint(
            position=top_pos,
            orientation=obj_pose[3:],
            approach_direction=np.array([0, 0, -1]),  # Approach from above
            grasp_width=radius * 1.5,  # Width needed to grasp top
            quality=0.7
        )
        grasps.append(top_grasp)

        # Side grasp (around the cylinder)
        side_pos = np.array([obj_pose[0] + radius, obj_pose[1], obj_pose[2]])
        side_orientation = np.array([0, 0, 0, 1])  # Default orientation
        side_grasp = GraspPoint(
            position=side_pos,
            orientation=side_orientation,
            approach_direction=np.array([-1, 0, 0]),  # Approach from side
            grasp_width=height * 0.8,  # Width for side grasp
            quality=0.9
        )
        grasps.append(side_grasp)

        return grasps

    def _plan_sphere_grasps(self, obj_pose: np.ndarray, dimensions: np.ndarray) -> List[GraspPoint]:
        """Plan grasps for a spherical object"""
        grasps = []

        # Center grasp
        radius = dimensions[0] / 2.0
        center_pos = obj_pose[:3]

        center_grasp = GraspPoint(
            position=center_pos,
            orientation=obj_pose[3:],
            approach_direction=np.array([0, 0, 1]),  # Default approach
            grasp_width=radius * 1.5,  # Width needed for sphere
            quality=0.6
        )
        grasps.append(center_grasp)

        return grasps

    def _transform_point(self, point: np.ndarray, pose: np.ndarray) -> np.ndarray:
        """Transform a point from object frame to world frame"""
        # Extract position and orientation
        pos = pose[:3]
        quat = pose[3:]

        # Convert quaternion to rotation matrix
        rotation_matrix = self._quaternion_to_rotation_matrix(quat)

        # Transform point
        world_point = rotation_matrix @ point + pos
        return world_point

    def _quaternion_to_rotation_matrix(self, q: np.ndarray) -> np.ndarray:
        """Convert quaternion to rotation matrix"""
        w, x, y, z = q
        return np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x**2 + z**2), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x**2 + y**2)]
        ])

    def _align_with_surface_normal(self, obj_quat: np.ndarray, surface_normal: np.ndarray) -> np.ndarray:
        """Align gripper with surface normal"""
        # This is a simplified implementation
        # In practice, you'd compute the appropriate orientation to align with the surface
        return obj_quat  # Return same orientation as object for now

    def _calculate_approach_direction(self, orientation: np.ndarray) -> np.ndarray:
        """Calculate approach direction based on orientation"""
        # Convert orientation quaternion to rotation matrix
        w, x, y, z = orientation
        rotation_matrix = self._quaternion_to_rotation_matrix(orientation)

        # Use the z-axis of the gripper frame as approach direction
        approach_direction = rotation_matrix @ np.array([0, 0, 1])
        return approach_direction


class ManipulationController:
    """Main manipulation controller that coordinates manipulation tasks"""

    def __init__(self, manipulator_dof: int = 6, control_mode: ManipulationMode = ManipulationMode.CARTESIAN_SPACE):
        """
        Initialize manipulation controller

        Args:
            manipulator_dof: Degrees of freedom of the manipulator
            control_mode: Control mode to use
        """
        self.manipulator_dof = manipulator_dof
        self.control_mode = control_mode
        self.ik_solver = InverseKinematicsSolver(
            joint_limits=[(-np.pi, np.pi) for _ in range(manipulator_dof)],
            max_iterations=100,
            tolerance=1e-3
        )
        self.grasp_planner = GraspPlanner()
        self.current_state = None
        self.active_task = None
        self.gripper_open = True

    def set_manipulator_state(self, state: ManipulatorState):
        """Set the current state of the manipulator"""
        self.current_state = state

    def execute_manipulation_task(self, task: ManipulationTask) -> bool:
        """
        Execute a manipulation task

        Args:
            task: Manipulation task to execute

        Returns:
            True if task completed successfully, False otherwise
        """
        if self.current_state is None:
            print("Error: Manipulator state not set")
            return False

        print(f"Executing manipulation task: {task.task_type} on {task.target_object}")

        if task.task_type == 'pick':
            return self._execute_pick_task(task)
        elif task.task_type == 'place':
            return self._execute_place_task(task)
        elif task.task_type == 'move':
            return self._execute_move_task(task)
        else:
            print(f"Unknown task type: {task.task_type}")
            return False

    def _execute_pick_task(self, task: ManipulationTask) -> bool:
        """Execute a pick task"""
        print("Planning grasp for pick task...")

        # Plan grasps for the target object
        object_info = {
            'pose': task.target_pose,
            'dimensions': np.array([0.05, 0.05, 0.05]),  # Default dimensions
            'shape': 'box'
        }
        grasps = self.grasp_planner.plan_grasps(object_info)

        if not grasps:
            print("No valid grasps found")
            return False

        # Select the best grasp
        best_grasp = grasps[0]
        print(f"Selected grasp with quality: {best_grasp.quality:.2f}")

        # Execute approach to pre-grasp position
        pre_grasp_pose = best_grasp.position.copy()
        pre_grasp_pose[2] += task.pre_grasp_offset  # Lift above object
        success = self.move_to_pose(pre_grasp_pose, best_grasp.orientation)
        if not success:
            print("Failed to reach pre-grasp position")
            return False

        # Move to grasp position
        grasp_pose = best_grasp.position.copy()
        success = self.move_to_pose(grasp_pose, best_grasp.orientation)
        if not success:
            print("Failed to reach grasp position")
            return False

        # Close gripper
        self.close_gripper()
        print("Gripper closed")

        # Lift object
        lift_pose = grasp_pose.copy()
        lift_pose[2] += task.post_grasp_offset  # Lift object
        success = self.move_to_pose(lift_pose, best_grasp.orientation)
        if not success:
            print("Failed to lift object")
            return False

        print("Pick task completed successfully")
        return True

    def _execute_place_task(self, task: ManipulationTask) -> bool:
        """Execute a place task"""
        print("Executing place task...")

        # Move to position above target
        place_pose = task.target_pose.copy()
        place_pose[2] += task.pre_grasp_offset  # Position above target

        success = self.move_to_pose(place_pose[:3], place_pose[3:])
        if not success:
            print("Failed to reach place position")
            return False

        # Lower to target position
        success = self.move_to_pose(task.target_pose[:3], task.target_pose[3:])
        if not success:
            print("Failed to reach place position")
            return False

        # Open gripper
        self.open_gripper()
        print("Gripper opened")

        # Retract
        retract_pose = place_pose.copy()
        retract_pose[2] += task.post_grasp_offset
        success = self.move_to_pose(retract_pose[:3], place_pose[3:])
        if not success:
            print("Failed to retract after placing")
            return False

        print("Place task completed successfully")
        return True

    def _execute_move_task(self, task: ManipulationTask) -> bool:
        """Execute a move task"""
        print("Executing move task...")

        success = self.move_to_pose(task.target_pose[:3], task.target_pose[3:])
        if success:
            print("Move task completed successfully")
        else:
            print("Move task failed")

        return success

    def move_to_pose(self, position: np.ndarray, orientation: np.ndarray = None) -> bool:
        """
        Move end-effector to a target pose

        Args:
            position: Target position [x, y, z]
            orientation: Target orientation [qx, qy, qz, qw]

        Returns:
            True if movement successful, False otherwise
        """
        if self.current_state is None:
            return False

        # Create target pose
        if orientation is None:
            # Keep current orientation
            target_pose = np.concatenate([position, self.current_state.ee_pose[3:]])
        else:
            target_pose = np.concatenate([position, orientation])

        # Solve inverse kinematics
        current_joints = self.current_state.joint_state.positions
        target_joints = self.ik_solver.solve_ik(target_pose, current_joints)

        if target_joints is None:
            print("IK solution not found")
            return False

        # In a real implementation, you would command the joints
        # For simulation, we'll just update the state
        print(f"Moving to joints: {[f'{j:.3f}' for j in target_joints]}")

        # Update state (in real implementation, this would happen as robot moves)
        # Simulate movement completion
        time.sleep(0.1)  # Simulate movement time

        return True

    def open_gripper(self):
        """Open the gripper"""
        self.gripper_open = True
        print("Gripper opened")

    def close_gripper(self):
        """Close the gripper"""
        self.gripper_open = False
        print("Gripper closed")

    def get_gripper_state(self) -> bool:
        """Get gripper state (True for open, False for closed)"""
        return self.gripper_open


class IsaacManipulationController:
    """
    Isaac Sim specific manipulation controller that integrates with Isaac's control systems
    """

    def __init__(self):
        # Initialize the manipulation controller
        self.manip_controller = ManipulationController(
            manipulator_dof=6,
            control_mode=ManipulationMode.CARTESIAN_SPACE
        )

        # For Isaac Sim integration, you would:
        # 1. Interface with Isaac's manipulator controller
        # 2. Subscribe to manipulator joint state
        # 3. Handle coordinate transformations between Isaac frames
        # 4. Interface with Isaac's physics engine for grasp simulation

        print("Isaac Manipulation Controller initialized")

    def update_from_isaac(self, manipulator_state: ManipulatorState):
        """
        Update controller with manipulator state from Isaac Sim

        Args:
            manipulator_state: Current manipulator state from Isaac Sim
        """
        self.manip_controller.set_manipulator_state(manipulator_state)

    def execute_task_in_isaac(self, task: ManipulationTask) -> bool:
        """
        Execute a manipulation task in Isaac Sim

        Args:
            task: Manipulation task to execute

        Returns:
            True if task completed successfully, False otherwise
        """
        return self.manip_controller.execute_manipulation_task(task)

    def move_manipulator_to_pose(self, x: float, y: float, z: float,
                                qx: float = 0.0, qy: float = 0.0,
                                qz: float = 0.0, qw: float = 1.0) -> bool:
        """
        Move manipulator to a specific pose in Isaac Sim world coordinates

        Args:
            x, y, z: Position coordinates
            qx, qy, qz, qw: Orientation quaternion

        Returns:
            True if movement successful, False otherwise
        """
        position = np.array([x, y, z])
        orientation = np.array([qx, qy, qz, qw])
        return self.manip_controller.move_to_pose(position, orientation)

    def open_gripper_in_isaac(self):
        """Open the gripper in Isaac Sim"""
        self.manip_controller.open_gripper()

    def close_gripper_in_isaac(self):
        """Close the gripper in Isaac Sim"""
        self.manip_controller.close_gripper()

    def get_gripper_state_in_isaac(self) -> bool:
        """Get gripper state from Isaac Sim"""
        return self.manip_controller.get_gripper_state()


def main():
    """
    Example usage of the manipulation and control system
    """
    print("Initializing Manipulation and Control System...")

    # Create a manipulation controller
    manip_controller = ManipulationController()

    # Example: Create a pick task
    target_pose = np.array([0.5, 0.0, 0.1, 0.0, 0.0, 0.0, 1.0])  # [x, y, z, qx, qy, qz, qw]
    pick_task = ManipulationTask(
        task_type='pick',
        target_object='red_block',
        target_pose=target_pose,
        pre_grasp_offset=0.1,
        post_grasp_offset=0.1
    )

    # Create a dummy manipulator state (in practice, this would come from Isaac Sim)
    dummy_state = ManipulatorState(
        joint_state=ManipulatorJointState(
            positions=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            velocities=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            efforts=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ),
        ee_pose=np.array([0.3, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0]),
        ee_twist=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    )

    manip_controller.set_manipulator_state(dummy_state)

    # Execute the pick task
    print("Executing pick task...")
    success = manip_controller.execute_manipulation_task(pick_task)
    print(f"Pick task result: {'Success' if success else 'Failed'}")

    # Create Isaac manipulation controller
    isaac_manip_controller = IsaacManipulationController()

    print("\nManipulation system ready for Isaac Sim integration")
    print("The system can plan grasps, control manipulator motion, and execute tasks")
    print("In Isaac Sim, this would connect to manipulator controllers and physics simulation")


if __name__ == "__main__":
    main()