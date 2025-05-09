import argparse
import os
import subprocess

import sys
from pathlib import Path

# Add legogpt to the system path
sys.path.append(str(Path(__file__).parents[2]))
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

    # Check if input file is .ldr or .txt. If input file is txt, convert to ldr for use with blenderLego_toObj.py
    if not input_file.endswith('.txt') and not input_file.endswith('.ldr'):
        raise ValueError('Input file must be a .ldr or .txt file.')
    if input_file.endswith('.txt'):
        new_input_file = input_file.removesuffix('.txt') + '.ldr'
        with open(input_file) as f:
            lego = LegoStructure.from_txt(f.read())
        with open(new_input_file, 'w') as f:
            f.write(lego.to_ldr())
        input_file = new_input_file

    # Make output directories
    texture_output_dir = os.path.join(output_dir, 'texture_output')
    texture_render_dir = os.path.join(output_dir, 'texture_render')
    os.makedirs(texture_output_dir, exist_ok=True)
    os.makedirs(texture_render_dir, exist_ok=True)

    subprocess.run(['python', 'blenderLego_toObj.py', '--in_file', input_file, '--out_file', output_dir],
                   check=True)

    print('Generating texture...')
    subprocess.run(
        ['python', 'generate_texture.py',
         '--input_mesh', os.path.join(output_dir, 'lego_structure_joint.obj'),
         '--output', texture_output_dir, '--prompt', prompt, '--production'],
        cwd='FlashTex', check=True
    )

    print('Rendering texture...')
    subprocess.run(
        ['python', 'blender_obj_uv_normal.py', '--data_path', texture_output_dir,
         '--obj_name', 'output_mesh', '--albedo_map', 'texture_kd.png', '--normal_map', 'None',
         '--scale', '1.0', '--start_rot_x', '270', '--start_rot_z', '180', '--output_path', texture_render_dir],
        cwd='blender-render-toolkit', check=True
    )

    print(f'Script finished. Check outputs in {output_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a texture for a LEGO model and render it.')
    parser.add_argument('input_file', type=str, help='Path to the input LEGO, a .ldr (LDraw) or .txt file.')
    parser.add_argument('output_dir', type=str, help='Path to the directory in which to save the output files.')
    parser.add_argument('prompt', type=str, help='The input text prompt for texture generation.')

    args = parser.parse_args()

    main(args.input_file, args.output_dir, args.prompt)
