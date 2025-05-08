import argparse
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from tqdm import tqdm

# Add path to ImportLDraw module
sys.path.append(str(Path(__file__).parents[2]))

import ImportLDraw
from ImportLDraw.loadldraw.loadldraw import Options, Configure, loadFromFile, FileSystem
import bmesh

PLUGIN_PATH = Path(ImportLDraw.__file__).parent
LDRAW_LIB_PATH = Path.home() / 'ldraw'

bpy.data.scenes[0].render.engine = "CYCLES"

# Set the device_type
bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

# Set the device and feature set
bpy.context.scene.cycles.device = "GPU"

# get_devices() to let Blender detects GPU device
bpy.context.preferences.addons["cycles"].preferences.get_devices()
print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
for d in bpy.context.preferences.addons["cycles"].preferences.devices:
    d["use"] = 0
    if d["name"][:6] == "NVIDIA":
        d["use"] = 1
    print(d["name"], d["use"])

# exec(open(os.path.join(PLUGIN_PATH, "loadldraw/loadldraw.py")).read())

# Set import options and import
isBlender28OrLater = hasattr(bpy.app, "version") and bpy.app.version >= (2, 80)
hasCollections = hasattr(bpy.data, "collections")


def render_lego(
        in_file,
        output_dir,
        idx=0,
        is_last=False,
        reposition_camera=True,
        square_image=True,
        instructionsLook=False,
        empty=False,
        export=False,
        fov=25,
):
    out_file = os.path.join(output_dir, f"images/{idx}.png")
    # Remove all objects but keep the camera
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.select_by_type(type="MESH")
    bpy.ops.object.delete()

    Options.ldrawDirectory = LDRAW_LIB_PATH
    Options.instructionsLook = instructionsLook
    Options.useLogoStuds = False
    Options.useUnofficialParts = True
    Options.gaps = True
    Options.studLogoDirectory = os.path.join(PLUGIN_PATH, "studs")
    Options.LSynthDirectory = os.path.join(PLUGIN_PATH, "lsynth")
    Options.verbose = 1
    Options.overwriteExistingMaterials = True
    Options.overwriteExistingMeshes = True
    Options.scale = 0.01
    Options.createInstances = True  # Multiple bricks share geometry (recommended)
    Options.removeDoubles = True  # Remove duplicate vertices (recommended)
    Options.positionObjectOnGroundAtOrigin = (
        True  # Centre the object at the origin, sitting on the z=0 plane
    )
    Options.flattenHierarchy = (
        False  # All parts are under the root object - no sub-models
    )
    Options.edgeSplit = True  # Add the edge split modifier
    Options.addBevelModifier = (
        True  # Adds a bevel modifier to each part (for rounded edges)
    )
    Options.bevelWidth = 0.5  # Bevel width
    Options.addEnvironmentTexture = True
    Options.scriptDirectory = os.path.join(PLUGIN_PATH, "loadldraw")
    Options.addWorldEnvironmentTexture = True  # Add an environment texture
    Options.addGroundPlane = True  # Add a ground plane
    Options.setRenderSettings = True  # Set render percentage, denoising
    Options.removeDefaultObjects = True  # Remove cube and lamp
    Options.positionCamera = (
        reposition_camera  # Reposition the camera to a good place to see the scene
    )
    Options.cameraBorderPercent = (
        0.05  # Add a percentage border around the repositioned camera
    )

    Configure()

    loadFromFile(None, FileSystem.locate(in_file))

    cam_x, cam_y, cam_z = bpy.context.scene.camera.location
    cam_roll, cam_pitch, cam_yaw = bpy.context.scene.camera.rotation_euler
    # fov = 40
    fov = fov

    if square_image:
        # Set the image size
        bpy.context.scene.render.resolution_x = 512
        bpy.context.scene.render.resolution_y = 512

        # Set the fov
        bpy.context.scene.camera.data.angle = math.radians(fov)
        bpy.context.scene.camera.location = (cam_x, cam_y, cam_z)
        bpy.context.scene.camera.rotation_euler = (cam_roll, cam_pitch, cam_yaw)

    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)

    if is_last:
        # Animate the rotation of the parent object
        fps = 30
        frame_start = 1
        frame_end = 30

        min_x = 10000
        max_x = 0
        min_y = 10000
        max_y = 0
        min_z = 10000
        max_z = 10000
        for obj in bpy.context.scene.objects:
            if obj.name[-4:] != ".DAT":
                continue
            objx, objy, objz = obj.location
            min_x = min(min_x, objx)
            max_x = max(max_x, objx)
            min_y = min(min_y, objy)
            max_y = max(max_y, objy)
            min_z = min(min_z, objz)
            max_z = max(max_z, objz)

        bpy.ops.object.empty_add(
            type="PLAIN_AXES",
            location=(min_x + (max_x - min_x) / 2, min_y + (max_y - min_y) / 2, 0),
        )
        parent_object = bpy.context.object
        parent_object.name = "Voxel_Structure"

        for obj in bpy.context.scene.objects:
            if obj.name[-4:] != ".DAT":
                continue
            if min_z < 0.009:
                obj.location[2] += 0.0096
            child_object = obj
            child_object.select_set(True)
            parent_object.select_set(True)

            bpy.context.view_layer.objects.active = parent_object
            bpy.ops.object.parent_set(type="OBJECT")

        # Set initial rotation
        parent_object.rotation_euler = (0, 0, 0)
        parent_object.keyframe_insert(data_path="rotation_euler", frame=frame_start)

        # Set final rotation (rotate 360 degrees around Z)
        parent_object.rotation_euler = (0, 0, math.radians(360))
        parent_object.keyframe_insert(data_path="rotation_euler", frame=frame_end)

        # Set the scene to play the animation
        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end

        # Set the fov
        bpy.context.scene.camera.data.angle = math.radians(fov)
        bpy.context.scene.camera.location = (
            min_x + (max_x - min_x) / 2 + cam_x,
            min_y + (max_y - min_y) / 2 + cam_y,
            min_z + cam_z,
        )
        bpy.context.scene.camera.rotation_euler = (cam_roll, cam_pitch, cam_yaw)

        # Set up rendering
        bpy.context.scene.render.filepath = os.path.join(
            output_dir, f"spin.mp4"
        )  # Output path
        bpy.context.scene.render.image_settings.file_format = "FFMPEG"  # Video format
        bpy.context.scene.render.ffmpeg.format = "MPEG4"  # Specify MPEG4 format
        bpy.context.scene.render.ffmpeg.codec = "H264"  # Codec for video
        bpy.context.scene.render.fps = fps

        # Render the animation
        bpy.ops.render.render(animation=True)

    if is_last and square_image:
        # Set back the fov
        bpy.context.scene.camera.data.angle = math.radians(fov)
        bpy.context.scene.camera.location = (cam_x, cam_y, cam_z)
        bpy.context.scene.camera.rotation_euler = (cam_roll, cam_pitch, cam_yaw)

    # Export the scene as a obj file
    if export:
        export_scene_to_obj(
            os.path.join(output_dir, f"lego_structure_joint.obj"),
            exclude_objects=["LegoGroundPlane"],
        )


def join_objects(objects_to_join):
    """Join multiple objects into one"""
    bpy.ops.object.select_all(action="DESELECT")

    for obj in objects_to_join:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = objects_to_join[0]
    bpy.ops.object.join()

    return bpy.context.view_layer.objects.active


def remove_internal_faces(obj):
    """
    Remove internal faces that aren't visible from outside
    """
    # Get the mesh
    mesh = obj.data
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Create a BMesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Directions to cast rays from
    directions = [
        Vector((1, 0, 0)),
        Vector((-1, 0, 0)),
        Vector((0, 1, 0)),
        Vector((0, -1, 0)),
        Vector((0, 0, 1)),
        Vector((0, 0, -1)),
    ]

    # Scale rays based on object size
    max_dim = max(obj.dimensions)
    ray_length = max_dim * 2

    # Store visible faces
    visible_faces = set()

    # For each face
    for face in tqdm(bm.faces):
        # Get face center in world space
        face_center = obj.matrix_world @ face.calc_center_median()

        # Check visibility from each direction
        for direction in directions:
            ray_origin = face_center + (direction * ray_length)
            ray_direction = -direction

            # Cast ray using scene ray_cast
            result = bpy.context.scene.ray_cast(depsgraph, ray_origin, ray_direction)

            if result[0]:  # If ray hit something
                # Convert hit point back to local space
                hit_face = None
                min_dist = float("inf")

                # Find the closest face to the hit point
                for f in bm.faces:
                    f_center = obj.matrix_world @ f.calc_center_median()
                    dist = (result[1] - f_center).length
                    if dist < min_dist:
                        min_dist = dist
                        hit_face = f

                if hit_face == face:
                    visible_faces.add(face.index)
                    break

    # Delete non-visible faces
    faces_to_delete = [f for f in bm.faces if f.index not in visible_faces]
    if faces_to_delete:
        bmesh.ops.delete(bm, geom=faces_to_delete, context="FACES")

    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def smart_uv_unwrap_lego(obj):
    """Perform Smart UV unwrapping optimized for LEGO objects"""
    if obj.type != "MESH":
        return

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")

    # Remove existing UV maps
    while obj.data.uv_layers:
        obj.data.uv_layers.remove(obj.data.uv_layers[0])

    # Create new UV map
    obj.data.uv_layers.new(name="UVMap")

    # LEGO-optimized parameters
    bpy.ops.uv.smart_project(
        angle_limit=45.0,
        island_margin=0.005,
        area_weight=0.75,
        correct_aspect=True,
        scale_to_bounds=True,
    )

    bpy.ops.object.mode_set(mode="OBJECT")


def create_lightmap_uvs(obj, margin=0.1):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = obj.data.uv_layers.new(name="Lightmap")

    for face in bm.faces:
        face.select = True

    bpy.ops.uv.lightmap_pack(
        PREF_CONTEXT='SEL_FACES',
        PREF_PACK_IN_ONE=True,
        PREF_NEW_UVLAYER=False,
        PREF_BOX_DIV=12,
        PREF_MARGIN_DIV=margin
    )

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    return uv_layer


def export_scene_to_obj(filepath, exclude_objects=None, remove_internal=True):
    """
    Export the scene to an OBJ file, combining all meshes into one

    Args:
        filepath (str): Full path for the output OBJ file
        exclude_objects (list): List of object names to exclude from export
        remove_internal (bool): Whether to remove internal faces before UV unwrapping
    """
    if exclude_objects is None:
        exclude_objects = []

    if not filepath.lower().endswith(".obj"):
        filepath += ".obj"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Get mesh objects
    mesh_objects = [
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name not in exclude_objects
    ]

    if not mesh_objects:
        print("No mesh objects to export!")
        return

    # Create copies
    copied_objects = []
    for obj in mesh_objects:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(new_obj)
        copied_objects.append(new_obj)

    # Join objects
    joined_object = join_objects(copied_objects)

    # # Remove internal faces if requested
    # if remove_internal:
    #     remove_internal_faces(joined_object)

    # UV unwrap
    # smart_uv_unwrap_lego(joined_object)
    # lightmap_uv_unwrap_lego(joined_object)
    lightmap_uvs = create_lightmap_uvs(
        joined_object,
        margin=0.00,  # 5% margin between UV islands
    )

    # Select only our object
    bpy.ops.object.select_all(action="DESELECT")
    joined_object.select_set(True)
    bpy.context.view_layer.objects.active = joined_object

    # Export
    bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)

    # Clean up
    mesh_data = joined_object.data
    bpy.data.objects.remove(joined_object, do_unlink=True)
    bpy.data.meshes.remove(mesh_data)

    print(f"Scene exported to: {filepath} as a single mesh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_file", type=str, help="Path to LDR file")
    parser.add_argument("--out_file", type=str, help="Path to output image file")
    parser.add_argument("--instructions_look", type=bool, help="Whether to look at the instructions", default=False)
    parser.add_argument("--fov", type=int, help="Field of view", default=25)
    args = parser.parse_args()

    # Get the absolute path of the input file
    in_file = os.path.abspath(args.in_file)
    out_file = os.path.abspath(args.out_file)
    out_dir = os.path.dirname(out_file)
    os.makedirs(os.path.join(out_dir), exist_ok=True)
    render_lego(
        in_file, out_file, square_image=True, instructionsLook=args.instructions_look, export=True, fov=args.fov
    )
    print(f"Rendered image to {out_file}")
