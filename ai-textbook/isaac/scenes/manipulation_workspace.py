#!/usr/bin/env python3
"""
Script to create a manipulation workspace scene in Isaac Sim
This script demonstrates how to programmatically create a scene for manipulation experiments
"""

import omni
from pxr import Gf, UsdGeom, UsdPhysics, PhysxSchema
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage, get_stage_units
from omni.isaac.core.utils.prims import create_prim, get_prim_at_path
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.sensor import Camera
import numpy as np
import carb


def create_manipulation_scene():
    """
    Create a manipulation experiment scene with table, objects, and robot
    """
    # Get the current stage
    stage = omni.usd.get_context().get_stage()

    # Set up the basic scene
    scene_path = "/World"
    scene_prim = stage.GetPrimAtPath(scene_path)
    if not scene_prim.IsValid():
        scene_prim = create_prim(scene_path, "Xform")

    # Create ground plane
    ground_path = "/World/groundPlane"
    create_prim(
        prim_path=ground_path,
        prim_type="Mesh",
        position=np.array([0, 0, 0]),
        orientation=np.array([0, 0, 0, 1]),
        scale=np.array([10, 10, 1])
    )

    # Add physics properties to ground
    ground_geom = UsdGeom.Mesh.Get(stage, ground_path)
    UsdPhysics.CollisionAPI.Apply(ground_geom.GetPrim())

    # Create a table for manipulation
    table_path = "/World/table"
    create_prim(
        prim_path=table_path,
        prim_type="Cube",
        position=[0.5, 0, 0.4],  # Table at 80cm height (0.4m half height + 0.4m table height)
        scale=[1.2, 0.8, 0.4]   # 120cm x 80cm x 80cm table
    )
    table_geom = UsdGeom.Cube.Get(stage, table_path)
    UsdPhysics.CollisionAPI.Apply(table_geom.GetPrim())

    # Set up physics scene
    physics_scene_path = "/World/physicsScene"
    physics_scene = UsdPhysics.Scene.Define(stage, physics_scene_path)
    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(physics_scene.GetPrim())
    physx_scene.CreateTimeStepsPerSecondAttr(120)  # Higher for manipulation
    physx_scene.CreateMaxSubStepsAttr(2)

    # Add gravity
    physx_scene_api = PhysxSchema.PhysxSceneAPI.Get(stage, physics_scene_path)
    physx_scene_api.CreateGravityAttr().Set(Gf.Vec3f(0.0, 0.0, -9.81))

    # Add various objects for manipulation
    objects_info = [
        {"name": "red_block", "position": [0.3, -0.1, 0.5], "size": 0.05, "color": [0.8, 0.2, 0.2]},
        {"name": "green_block", "position": [0.3, 0.1, 0.5], "size": 0.05, "color": [0.2, 0.8, 0.2]},
        {"name": "blue_block", "position": [0.5, -0.1, 0.5], "size": 0.05, "color": [0.2, 0.2, 0.8]},
        {"name": "yellow_block", "position": [0.5, 0.1, 0.5], "size": 0.05, "color": [0.8, 0.8, 0.2]},
        {"name": "small_sphere", "position": [0.7, 0.0, 0.5], "radius": 0.03, "color": [0.8, 0.4, 0.8]},
        {"name": "cylinder", "position": [0.1, 0.0, 0.5], "radius": 0.04, "height": 0.08, "color": [0.4, 0.8, 0.8]}
    ]

    for i, obj_info in enumerate(objects_info):
        if "size" in obj_info:  # Cube
            prim_path = f"/World/{obj_info['name']}"
            create_prim(
                prim_path=prim_path,
                prim_type="Cube",
                position=obj_info["position"],
                scale=[obj_info["size"], obj_info["size"], obj_info["size"]]
            )
            # Add collision and make dynamic
            cube_geom = UsdGeom.Cube.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(cube_geom.GetPrim())
            UsdPhysics.RigidBodyAPI.Apply(cube_geom.GetPrim())

            # Apply color
            mtl_path = f"/World/Looks/{obj_info['name']}_Mat"
            material = create_prim(mtl_path, "Material")
            preview_surface = create_prim(
                f"{mtl_path}/PreviewSurface",
                "Shader",
                attributes={"inputs:surface": None}
            )
            preview_surface.GetAttribute("inputs:diffuseColor").Set(obj_info["color"])

            binding_api = UsdGeom.MaterialBindingAPI(cube_geom)
            binding_api.Bind(material)

        elif "radius" in obj_info and "height" in obj_info:  # Cylinder
            prim_path = f"/World/{obj_info['name']}"
            create_prim(
                prim_path=prim_path,
                prim_type="Cylinder",
                position=obj_info["position"],
                scale=[obj_info["radius"], obj_info["height"], obj_info["radius"]]
            )
            # Add collision and make dynamic
            cyl_geom = UsdGeom.Cylinder.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(cyl_geom.GetPrim())
            UsdPhysics.RigidBodyAPI.Apply(cyl_geom.GetPrim())

        elif "radius" in obj_info:  # Sphere
            prim_path = f"/World/{obj_info['name']}"
            create_prim(
                prim_path=prim_path,
                prim_type="Sphere",
                position=obj_info["position"],
                scale=[obj_info["radius"], obj_info["radius"], obj_info["radius"]]
            )
            # Add collision and make dynamic
            sph_geom = UsdGeom.Sphere.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(sph_geom.GetPrim())
            UsdPhysics.RigidBodyAPI.Apply(sph_geom.GetPrim())

    # Add a robot arm for manipulation (UR5e as an example)
    # In a real scenario, you would add a reference to a robot USD file
    robot_path = "/World/Robot"
    create_prim(
        prim_path=robot_path,
        prim_type="Xform",
        position=[0, -0.8, 0.8]  # Positioned near the table
    )

    # For this example, we'll create a simple representation of a robot base
    robot_base_path = f"{robot_path}/Base"
    create_prim(
        prim_path=robot_base_path,
        prim_type="Cylinder",
        position=[0, 0, 0.2],
        scale=[0.2, 0.4, 0.2]
    )
    base_geom = UsdGeom.Cylinder.Get(stage, robot_base_path)
    UsdPhysics.CollisionAPI.Apply(base_geom.GetPrim())

    # Add cameras for perception
    # Overhead camera
    overhead_cam_path = "/World/OverheadCamera"
    overhead_camera = Camera(
        prim_path=overhead_cam_path,
        position=np.array([0.5, 0, 1.5]),  # Above the table
        rotation=np.array([-90, 0, 0]),    # Looking down
        frequency=30,
        resolution=(1280, 720)
    )

    # Front camera
    front_cam_path = "/World/FrontCamera"
    front_camera = Camera(
        prim_path=front_cam_path,
        position=np.array([-0.5, -0.5, 0.8]),  # Front view
        rotation=np.array([-15, 0, 30]),       # Angled view
        frequency=30,
        resolution=(1280, 720)
    )

    # Robot wrist camera (attached to end-effector conceptually)
    wrist_cam_path = f"{robot_path}/WristCamera"
    wrist_camera = Camera(
        prim_path=wrist_cam_path,
        position=np.array([0.5, -0.8, 0.9]),   # Near robot
        frequency=30,
        resolution=(640, 480)
    )

    # Add lighting
    # Key light
    key_light_path = "/World/KeyLight"
    create_prim(
        prim_path=key_light_path,
        prim_type="DistantLight",
        position=[2, 2, 3],
        rotation=[-60, -30, 0],
        attributes={"inputs:intensity": 3000}
    )

    # Fill light
    fill_light_path = "/World/FillLight"
    create_prim(
        prim_path=fill_light_path,
        prim_type="DistantLight",
        position=[-2, 1, 2],
        rotation=[-45, 30, 0],
        attributes={"inputs:intensity": 1500}
    )

    # Rim light
    rim_light_path = "/World/RimLight"
    create_prim(
        prim_path=rim_light_path,
        prim_type="DistantLight",
        position=[0, -3, 1],
        rotation=[-20, 0, 0],
        attributes={"inputs:intensity": 2000}
    )

    print("Manipulation scene created successfully!")
    print("Elements added:")
    print("  - Table for manipulation workspace")
    print("  - Various objects for grasping and manipulation")
    print("  - Robot base representation")
    print("  - Multiple cameras for perception")
    print("  - Proper lighting setup")
    print("Scene ready for manipulation experiments")


def setup_manipulation_environment():
    """
    Additional setup for manipulation-specific requirements
    """
    print("Setting up manipulation-specific environment parameters...")

    # In a real Isaac Sim environment, this would include:
    # - Setting up contact sensors on grippers
    # - Configuring force/torque sensors
    # - Setting up grasp detection systems
    # - Configuring object properties for manipulation

    print("Manipulation environment setup complete!")


def main():
    """
    Main function to run the scene creation
    """
    print("Creating manipulation workspace scene in Isaac Sim...")

    # Create the scene
    create_manipulation_scene()

    # Additional setup
    setup_manipulation_environment()

    # Note: In a real Isaac Sim environment, you would typically
    # run this as part of an extension or in the Isaac Sim environment
    # This script serves as a template for scene creation


if __name__ == "__main__":
    main()