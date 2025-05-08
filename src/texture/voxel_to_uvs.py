import numpy as np
import trimesh
from trimesh import util
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

import json
import argparse

def voxel_grid_to_mesh_with_uvs(voxel_grid):
    """Convert a voxel grid to a mesh with UV coordinates"""
    vertices = []
    faces = []
    uvs = []
    voxel_to_uv_mapping = {}
    
    # Calculate total faces first
    total_faces = 0
    for x, y, z in np.argwhere(voxel_grid):
        for nx, ny, nz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
            adjacent = (x + nx, y + ny, z + nz)
            if not (0 <= adjacent[0] < voxel_grid.shape[0] and 
                   0 <= adjacent[1] < voxel_grid.shape[1] and 
                   0 <= adjacent[2] < voxel_grid.shape[2]) or not voxel_grid[adjacent]:
                total_faces += 1
    
    # Calculate atlas size with a small margin
    atlas_size = int(np.ceil(np.sqrt(total_faces)))
    face_size = 0.98 / atlas_size  # Leave a small margin to prevent bleeding
    margin = (1.0 - (atlas_size * face_size)) / (atlas_size + 1)
    current_uv = [margin, margin]  # Start with margin
    
    # For each filled voxel
    for x, y, z in np.argwhere(voxel_grid):
        # Check each face direction
        for face_idx, (dx, dy, dz) in enumerate([
            (1,0,0), (-1,0,0),  # right, left
            (0,1,0), (0,-1,0),  # top, bottom
            (0,0,1), (0,0,-1)   # front, back
        ]):
            # Check if face should be created
            nx, ny, nz = x + dx, y + dy, z + dz
            if not (0 <= nx < voxel_grid.shape[0] and 
                   0 <= ny < voxel_grid.shape[1] and 
                   0 <= nz < voxel_grid.shape[2]) or not voxel_grid[nx, ny, nz]:
                
                # Calculate base vertex index
                base_idx = len(vertices)
                
                # Create vertices for this face
                if dx == 1:      # right face
                    quad = [(x+1,y,z), (x+1,y+1,z), (x+1,y+1,z+1), (x+1,y,z+1)]
                elif dx == -1:   # left face
                    quad = [(x,y,z), (x,y,z+1), (x,y+1,z+1), (x,y+1,z)]
                elif dy == 1:    # top face
                    quad = [(x,y+1,z), (x+1,y+1,z), (x+1,y+1,z+1), (x,y+1,z+1)]
                elif dy == -1:   # bottom face
                    quad = [(x,y,z), (x,y,z+1), (x+1,y,z+1), (x+1,y,z)]
                elif dz == 1:    # front face
                    quad = [(x,y,z+1), (x+1,y,z+1), (x+1,y+1,z+1), (x,y+1,z+1)]
                else:           # back face
                    quad = [(x,y,z), (x,y+1,z), (x+1,y+1,z), (x+1,y,z)]
                
                vertices.extend(quad)
                
                # Calculate UV coordinates with margins
                u, v = current_uv
                quad_uvs = [
                    [u, v],                    # bottom-left
                    [u + face_size, v],        # bottom-right
                    [u + face_size, v + face_size],  # top-right
                    [u, v + face_size]         # top-left
                ]
                uvs.extend(quad_uvs)
                
                # Store UV mapping
                voxel_to_uv_mapping[(x, y, z, face_idx)] = {
                    'uv_min': np.array([u, v]),
                    'uv_max': np.array([u + face_size, v + face_size])
                }
                
                # Create faces (two triangles)
                faces.extend([
                    [base_idx, base_idx + 1, base_idx + 2],
                    [base_idx, base_idx + 2, base_idx + 3]
                ])
                
                # Move to next UV position with margins
                current_uv[0] += face_size + margin
                if current_uv[0] + face_size >= 1.0:
                    current_uv[0] = margin
                    current_uv[1] += face_size + margin
    
    # Create mesh
    vertices = np.array(vertices)
    faces = np.array(faces)
    uvs = np.array(uvs)
    
    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        visual=trimesh.visual.TextureVisuals(uv=uvs)
    )
    
    return mesh, voxel_to_uv_mapping


def load_lego(fname):
    if fname.endswith('.json'):
        f = open(fname)
        content = json.load(f)
        f.close()
        return content['output']
    elif fname.endswith('.txt'):
        with open(fname, 'r') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file extension: {fname}")

def json2vox(task_graph, dim=[20, 20, 20]):
    X_SIZE, Y_SIZE, Z_SIZE = dim
    target_voxel = np.zeros((X_SIZE, Y_SIZE, Z_SIZE), dtype=np.uint8)
    
    # Get the output string and split into lines
    output_str = task_graph
    brick_specs = output_str.strip().split('\n')
    
    # Process each brick specification
    for spec in brick_specs:
        # Parse the brick specification
        # Format: "heightxwidth (x,y,z)"
        dims_str, coords_str = spec.split(' ')
        height, width = map(int, dims_str.split('x'))
        x, y, z = map(int, coords_str.strip('()').split(','))
        
        # Fill the voxel grid for this brick
        target_voxel[x:x+height, y:y+width, z] = 1
    
    return target_voxel

def save_mesh_as_obj(mesh, filename="output.obj"):
    """
    Save the mesh and its UV coordinates to an OBJ file
    
    Args:
        mesh: trimesh.Trimesh object with UV coordinates in mesh.visual
        filename: output OBJ filename
    """
    vertices = mesh.vertices
    faces = mesh.faces
    uvs = mesh.visual.uv
    
    with open(filename, 'w') as f:
        # Write MTL reference
        f.write("mtllib material.mtl\n")
        f.write("usemtl material0\n")
        
        # Write vertices
        for v in vertices:
            f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
        
        # Write texture coordinates (flip v coordinate for standard UV space)
        for uv in uvs:
            f.write(f'vt {uv[0]:.6f} {1-uv[1]:.6f}\n')  # Flip V coordinate
        
        # Write faces with correct UV indices
        # In our case, each vertex has its own UV coordinate
        for i, face in enumerate(faces):
            # Each vertex index needs its corresponding UV index
            # UV indices match vertex indices in our case
            f.write(f'f {face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}\n')


def save_mapping(mapping, filename="voxel_mapping.json"):
    """Save the voxel-to-UV mapping information"""
    # Convert numpy arrays to lists for JSON serialization
    serializable_mapping = {}
    for key, value in mapping.items():
        serializable_mapping[str(key)] = {
            'uv_min': value['uv_min'].tolist() if isinstance(value['uv_min'], np.ndarray) else value['uv_min'],
            'uv_max': value['uv_max'].tolist() if isinstance(value['uv_max'], np.ndarray) else value['uv_max']
        }
    
    with open(filename, 'w') as f:
        json.dump(serializable_mapping, f, indent=2)



# Example usage with visualization
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fname", type=str)
    parser.add_argument("--output", type=str, default="./out/color/")
    args = parser.parse_args()

    fname = args.fname
    lego_json = load_lego(fname)
    dimension = [20, 20, 20]
    voxel_grid = json2vox(lego_json, dim=dimension)

    voxel_grid = np.swapaxes(voxel_grid, 2, 1)
    voxel_grid = voxel_grid[::-1, :, ::-1]
    voxel_grid = voxel_grid.astype(bool)

    print(voxel_grid.shape)

    os.makedirs(args.output, exist_ok=True)
    
    # Convert to mesh with UV mapping
    mesh, mapping = voxel_grid_to_mesh_with_uvs(voxel_grid)
    

    save_mesh_as_obj(mesh, os.path.join(args.output, "voxel_mesh.obj"))
    save_mapping(mapping, os.path.join(args.output, "voxel_mapping.json"))    
