import numpy as np
import trimesh
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import argparse
import os

def load_mapping(filename="voxel_mapping.json"):
    """Load the voxel-to-UV mapping information"""
    with open(filename) as f:
        mapping_str = json.load(f)
    
    # Convert string keys back to tuples
    mapping = {}
    for key_str, value in mapping_str.items():
        # Remove parentheses and split by comma
        key_parts = key_str.strip('()').split(',')
        key = tuple(int(x) for x in key_parts)
        mapping[key] = {
            'uv_min': np.array(value['uv_min']),
            'uv_max': np.array(value['uv_max'])
        }
    return mapping

def get_voxel_average_color(texture_image, voxel_coords, face_idx, voxel_to_uv_mapping):
    """Get average color of a voxel face from the texture image"""
    mapping = voxel_to_uv_mapping[(voxel_coords[0], voxel_coords[1], voxel_coords[2], face_idx)]
    uv_min = mapping['uv_min']
    uv_max = mapping['uv_max']
    
    # Convert UV coordinates to pixel coordinates
    h, w = texture_image.shape[:2]
    px_min = (np.array(uv_min) * [w, h]).astype(int)
    px_max = (np.array(uv_max) * [w, h]).astype(int)
    
    # Get region from texture
    region = texture_image[px_min[1]:px_max[1], px_min[0]:px_max[0]]
    
    # Calculate average color
    return np.mean(region, axis=(0,1))

def reconstruct_voxel_grid(mapping, dimension=-1):
    """Reconstruct voxel grid dimensions from mapping"""
    if dimension == -1:
        max_x = max_y = max_z = 0
        for key in mapping.keys():
            x, y, z, _ = key
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_z = max(max_z, z)
    else:
        max_x, max_y, max_z = dimension
        max_x -= 1
        max_y -= 1
        max_z -= 1
    
    # Add 1 to get correct dimensions
    return np.zeros((max_x + 1, max_y + 1, max_z + 1), dtype=bool)

def visualize_colored_voxel_grid(voxel_grid, sampled_colors, title="Colored Voxel Grid", output_file="colored_voxels.png"):
    """Visualize the voxel grid with sampled colors"""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a color array for each voxel
    colored_voxels = np.zeros((*voxel_grid.shape, 4))  # RGBA
    
    # Create a dictionary to store colors for each voxel position
    voxel_colors_dict = {}
    
    # Collect all colors for each voxel position
    for voxel_key, color in sampled_colors.items():
        pos = voxel_key[:3]
        if pos not in voxel_colors_dict:
            voxel_colors_dict[pos] = []
        voxel_colors_dict[pos].append(color)
    
    # Average colors for each voxel
    for pos, colors in voxel_colors_dict.items():
        x, y, z = pos
        avg_color = np.mean(colors, axis=0)
        # Handle both RGB and RGBA textures
        if len(avg_color) == 3:
            colored_voxels[x,y,z] = [*avg_color/255, 1.0]  # RGB + alpha
        else:
            colored_voxels[x,y,z] = avg_color/255  # RGBA already present
        voxel_grid[x,y,z] = True
    
    # Plot filled voxels with their colors
    ax.voxels(voxel_grid, 
              facecolors=colored_voxels,
              edgecolor='black',
              linewidth=0.5)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    
    # Set equal aspect ratio
    ax.set_box_aspect([1,1,1])
    
    # Adjust view angle for better visualization
    ax.view_init(elev=30, azim=45)
    
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()

    return colored_voxels

def mesh_to_colored_voxels(obj_file="voxel_mesh.obj", 
                          mapping_file="voxel_mapping.json",
                          texture_file="texture.png",
                          output_file="colored_voxels.png"):
    """Convert a textured mesh back to colored voxels"""
    # Load the mesh
    mesh = trimesh.load(obj_file)
    print(f"Loaded mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
    
    # Load the mapping
    mapping = load_mapping(mapping_file)
    print(f"Loaded mapping with {len(mapping)} voxel faces")
    
    # Load the texture
    texture = plt.imread(texture_file)
    if texture.dtype == np.float32:
        texture = (texture * 255).astype(np.uint8)
    print(f"Loaded texture with shape {texture.shape}")
    
    # Reconstruct voxel grid
    voxel_grid = reconstruct_voxel_grid(mapping, dimension=[20, 20, 20])
    print(f"Reconstructed voxel grid with shape {voxel_grid.shape}")
    
    # Sample colors
    sampled_colors = {}
    for voxel_key in mapping.keys():
        coords = voxel_key[:3]
        face_idx = voxel_key[3]
        color = get_voxel_average_color(texture, coords, face_idx, mapping)
        sampled_colors[voxel_key] = color
    
    # Visualize the result
    colored_voxels = visualize_colored_voxel_grid(voxel_grid, sampled_colors, output_file=output_file)
    
    return voxel_grid, sampled_colors, colored_voxels

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname", type=str, default="/data/speedy/Projects/lego/LegoGPT/texture_pipeline/FlashTex/output/brick_texture/guitar/parlor/texture_kd.png")
    parser.add_argument("--obj_file", type=str, default="/data/speedy/Projects/lego/LegoGPT/texture_pipeline/brick_texture/voxel_mesh.obj")
    parser.add_argument("--mapping_file", type=str, default="/data/speedy/Projects/lego/LegoGPT/texture_pipeline/brick_texture/voxel_mapping.json")
    parser.add_argument("--output_dir", type=str, default="out/")
    args = parser.parse_args()

    # Convert mesh back to colored voxels
    voxel_grid, sampled_colors, colored_voxels = mesh_to_colored_voxels(texture_file=args.fname, obj_file=args.obj_file, 
                                                                        mapping_file=args.mapping_file,
                                                                        output_file=os.path.join(args.output_dir, "colored_voxels.png"))


    # # Check if the voxel grid is the same as the original voxel grid
    # from voxel_to_uvs import json2vox, load_json
    # fname = "../example/task_graph.json"
    # lego_json = load_json(fname)
    # dimension = [20, 20, 20]
    # original_voxel_grid = json2vox(lego_json, dim=dimension)

    # original_voxel_grid = np.swapaxes(original_voxel_grid, 2, 1)
    # print(original_voxel_grid.shape, voxel_grid.shape)
    # print(np.all(original_voxel_grid == (colored_voxels.sum(axis=3) > 0)))

    # union = np.logical_or(original_voxel_grid, colored_voxels.sum(axis=3) > 0)

    # # visualize the union
    # from matplotlib import pyplot as plt
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.voxels(union, edgecolor='black', linewidth=0.5)
    # plt.savefig("union_voxels.png", bbox_inches='tight', dpi=300)
    # plt.close()


    print(colored_voxels.shape, voxel_grid.shape)
    colored_voxels = colored_voxels[::-1, :, ::-1]
    colored_voxels = np.swapaxes(colored_voxels, 2, 1)

    # Save the colored voxels to a file
    np.save(os.path.join(args.output_dir, "colored_voxels.npy"), colored_voxels) # colored_voxels shape: (20, 20, 20, 4)