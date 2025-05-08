import argparse
import os
import subprocess


def main(input_file: str, output_dir: str, prompt: str):
    input_file = os.path.abspath(input_file)
    output_dir = os.path.abspath(output_dir)

    print('--- Initial Setup ---')
    print(f'Input File: {input_file}')
    print(f'Absolute Output Dir: {output_dir}')
    print(f'Prompt: {prompt}')
    print(f'Current Directory: {os.getcwd()}')
    print('---------------------')

    texture_output_dir = os.path.join(output_dir, 'texture_output')
    texture_render_dir = os.path.join(output_dir, 'texture_render')
    os.makedirs(texture_output_dir, exist_ok=True)
    os.makedirs(texture_render_dir, exist_ok=True)

    subprocess.run(['python', 'blenderLego_toObj.py', '--in_file', input_file, '--out_file', output_dir],
                   capture_output=True, check=True)

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
        cwd='blender-render-toolkit', capture_output=True, check=True
    )

    print(f'Script finished. Check outputs in {output_dir}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a texture for a LEGO model and render it.')
    parser.add_argument('input_file', type=str, help='Path to the input LEGO, an LDraw (.ldr) file.')
    parser.add_argument('output_dir', type=str, help='Path to the directory in which to save the output files.')
    parser.add_argument('prompt', type=str, help='The input text prompt for texture generation.')

    args = parser.parse_args()

    main(args.input_file, args.output_dir, args.prompt)
