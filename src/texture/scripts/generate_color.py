import argparse
import os
import subprocess

import sys
from pathlib import Path

# Add legogpt to the system path
sys.path.append(str(Path(__file__).parent.parent.parent))
from legogpt.data import LegoStructure


def main(input_file: str, output_dir: str, prompt: str):
    input_file = os.path.abspath(input_file)
    output_dir = os.path.abspath(output_dir)

    print('--- Initial Setup ---')
    print(f'Input File: {input_file}')
    print(f'Absolute Output Dir: {output_dir}')
    print(f'Prompt: {prompt}')
    print(f'Current Directory: {os.getcwd()}')
    print('---------------------')

    # Check if input file is .ldr or .txt. If input file is ldr, convert to txt
    if not input_file.endswith('.txt') and not input_file.endswith('.ldr'):
        raise ValueError('Input file must be a .ldr or .txt file.')
    if input_file.endswith('.ldr'):
        new_input_file = input_file.removesuffix('.ldr') + '.txt'
        with open(input_file) as f:
            lego = LegoStructure.from_ldr(f.read())
        with open(new_input_file, 'w') as f:
            f.write(lego.to_txt())
        input_file = new_input_file

    # Make output directories
    texture_output_dir = os.path.join(output_dir, 'texture_output')
    voxel_mesh_dir = os.path.join(output_dir, 'voxel_mesh')
    blender_render_dir = os.path.join(output_dir, 'blender_render')
    os.makedirs(texture_output_dir, exist_ok=True)
    os.makedirs(voxel_mesh_dir, exist_ok=True)
    os.makedirs(blender_render_dir, exist_ok=True)

    subprocess.run(['python', 'voxel_to_uvs.py', '--fname', input_file, '--output', voxel_mesh_dir], check=True)

    print('Generating texture...')
    subprocess.run(
        ['python', 'generate_texture.py',
         '--input_mesh', os.path.join(voxel_mesh_dir, 'voxel_mesh.obj'),
         '--output', texture_output_dir, '--prompt', prompt, '--production'],
        cwd='FlashTex', check=True
    )

    print('Generating color...')
    subprocess.run(
        ['python', 'uvs_to_voxels.py',
         '--fname', os.path.join(texture_output_dir, 'texture_kd.png'),
         '--obj_file', os.path.join(voxel_mesh_dir, 'voxel_mesh.obj'),
         '--mapping_file', os.path.join(voxel_mesh_dir, 'voxel_mapping.json'),
         '--output_dir', voxel_mesh_dir],
        check=True
    )
    subprocess.run(
        ['python', 'voxel_to_brick.py',
         '--lego_file', input_file,
         '--colored_voxels', os.path.join(voxel_mesh_dir, 'colored_voxels.npy'),
         '--ldr_file', os.path.join(voxel_mesh_dir, 'colored_brick.ldr')],
        check=True
    )

    print('Rendering colored bricks...')
    subprocess.run(
        ['python', 'blenderLego_toObj.py',
         '--in_file', os.path.join(voxel_mesh_dir, 'colored_brick.ldr'),
         '--out_file', blender_render_dir],
        check=True
    )

    # Copy final outputs
    image_output = os.path.join(blender_render_dir, 'images/0.png')
    image_dest = os.path.join(output_dir, 'rendered_color.png')
    ldr_output = os.path.join(voxel_mesh_dir, 'colored_brick.ldr')
    ldr_dest = os.path.join(output_dir, 'colored_brick.ldr')
    os.rename(image_output, image_dest)
    os.rename(ldr_output, ldr_dest)

    print(f'Script finished. Check outputs in {output_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate brick colors for a LEGO model.')
    parser.add_argument('input_file', type=str, help='Path to the input LEGO, a .ldr (LDraw) or .txt file.')
    parser.add_argument('output_dir', type=str, help='Path to the directory in which to save the output files.')
    parser.add_argument('prompt', type=str, help='The input text prompt for color generation.')

    args = parser.parse_args()
    main(args.input_file, args.output_dir, args.prompt)
