#!/usr/bin/env python3
"""
Script to create a simple VSLAM scene in Isaac Sim
This script demonstrates how to programmatically create a scene for VSLAM experiments
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


def create_vslam_scene():
    """
    Create a VSLAM experiment scene with various objects and lighting
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
        scale=np.array([20, 20, 1])
    )

    # Add physics properties to ground
    ground_geom = UsdGeom.Mesh.Get(stage, ground_path)
    UsdPhysics.CollisionAPI.Apply(ground_geom.GetPrim())

    # Set up physics scene
    physics_scene_path = "/World/physicsScene"
    physics_scene = UsdPhysics.Scene.Define(stage, physics_scene_path)
    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(physics_scene.GetPrim())
    physx_scene.CreateTimeStepsPerSecondAttr(60)
    physx_scene.CreateMaxSubStepsAttr(1)

    # Add gravity
    physx_scene_api = PhysxSchema.PhysxSceneAPI.Get(stage, physics_scene_path)
    physx_scene_api.CreateGravityAttr().Set(Gf.Vec3f(0.0, 0.0, -9.81))

    # Add various objects to create a rich visual environment for VSLAM
    objects_info = [
        {"name": "cube1", "position": [-3, -3, 0.5], "size": 1.0, "color": [0.8, 0.2, 0.2]},
        {"name": "cube2", "position": [3, -3, 0.5], "size": 1.0, "color": [0.2, 0.8, 0.2]},
        {"name": "cube3", "position": [-3, 3, 0.5], "size": 1.0, "color": [0.2, 0.2, 0.8]},
        {"name": "cube4", "position": [3, 3, 0.5], "size": 1.0, "color": [0.8, 0.8, 0.2]},
        {"name": "cylinder1", "position": [0, -4, 1.0], "radius": 0.5, "height": 2.0, "color": [0.8, 0.4, 0.2]},
        {"name": "cylinder2", "position": [0, 4, 1.0], "radius": 0.5, "height": 2.0, "color": [0.4, 0.2, 0.8]},
        {"name": "sphere1", "position": [-4, 0, 1.0], "radius": 0.7, "color": [0.2, 0.8, 0.8]},
        {"name": "sphere2", "position": [4, 0, 1.0], "radius": 0.7, "color": [0.8, 0.2, 0.8]}
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
            # Add collision and color
            cube_geom = UsdGeom.Cube.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(cube_geom.GetPrim())

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
            # Add collision and color
            cyl_geom = UsdGeom.Cylinder.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(cyl_geom.GetPrim())

        elif "radius" in obj_info:  # Sphere
            prim_path = f"/World/{obj_info['name']}"
            create_prim(
                prim_path=prim_path,
                prim_type="Sphere",
                position=obj_info["position"],
                scale=[obj_info["radius"], obj_info["radius"], obj_info["radius"]]
            )
            # Add collision and color
            sph_geom = UsdGeom.Sphere.Get(stage, prim_path)
            UsdPhysics.CollisionAPI.Apply(sph_geom.GetPrim())

    # Add a robot for VSLAM testing
    # For this example, we'll add a simple wheeled robot
    robot_path = "/World/Robot"
    create_prim(
        prim_path=robot_path,
        prim_type="Xform",
        position=[0, 0, 0.2]
    )

    # Add a simple robot body
    robot_body_path = f"{robot_path}/Body"
    create_prim(
        prim_path=robot_body_path,
        prim_type="Cylinder",
        position=[0, 0, 0.1],
        scale=[0.3, 0.2, 0.3]
    )
    body_geom = UsdGeom.Cylinder.Get(stage, robot_body_path)
    UsdPhysics.CollisionAPI.Apply(body_geom.GetPrim())

    # Add stereo cameras to the robot for VSLAM
    # Left camera
    left_camera_path = f"{robot_path}/LeftCamera"
    left_camera = Camera(
        prim_path=left_camera_path,
        position=np.array([-0.05, 0.1, 0.1]),  # 5cm baseline
        frequency=30,
        resolution=(640, 480)
    )

    # Right camera
    right_camera_path = f"{robot_path}/RightCamera"
    right_camera = Camera(
        prim_path=right_camera_path,
        position=np.array([0.05, 0.1, 0.1]),  # 5cm baseline
        frequency=30,
        resolution=(640, 480)
    )

    # Add lighting
    # Distant light
    light_path = "/World/DistantLight"
    create_prim(
        prim_path=light_path,
        prim_type="DistantLight",
        position=[5, 5, 5],
        rotation=[-45, -45, 0]
    )

    # Add a dome light for ambient lighting
    dome_light_path = "/World/DomeLight"
    create_prim(
        prim_path=dome_light_path,
        prim_type="DomeLight",
        attributes={"inputs:color": (0.2, 0.2, 0.2)}
    )

    print("VSLAM scene created successfully!")
    print("Objects added:")
    for obj in objects_info:
        print(f"  - {obj['name']}")
    print("Robot with stereo cameras added at origin")
    print("Scene ready for VSLAM experiments")


def main():
    """
    Main function to run the scene creation
    """
    print("Creating VSLAM scene in Isaac Sim...")

    # Create the scene
    create_vslam_scene()

    # Note: In a real Isaac Sim environment, you would typically
    # run this as part of an extension or in the Isaac Sim environment
    # This script serves as a template for scene creation


if __name__ == "__main__":
    main()