#!/bin/bash

export INPUT_FILE="$1"
export OUTPUT_DIR="$(realpath "$2")"
export PROMPT="$3"

# Create the base output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "--- Initial Setup ---"
echo "Input File: $INPUT_FILE"
echo "Absolute Output Dir: $OUTPUT_DIR"
echo "Prompt: $PROMPT"
echo "Current Directory: $(pwd)"
echo "---------------------"

mkdir -p "$OUTPUT_DIR/voxel_mesh"

uv run voxel_to_uvs.py --fname "$INPUT_FILE" --output "$OUTPUT_DIR/voxel_mesh"

echo "Generating texture..."

cd FlashTex

python generate_texture.py --input_mesh "$OUTPUT_DIR/voxel_mesh/voxel_mesh.obj"  \
                           --output "$OUTPUT_DIR/texture_output" \
                           --prompt "$PROMPT" --production


echo "Generating color..."

cd ../
uv run uvs_to_voxels.py --fname "$OUTPUT_DIR/texture_output/texture_kd.png" --obj_file "$OUTPUT_DIR/voxel_mesh/voxel_mesh.obj" --mapping_file "$OUTPUT_DIR/voxel_mesh/voxel_mapping.json"  --output_dir "$OUTPUT_DIR/voxel_mesh"

uv run voxel_to_brick.py --lego_file "$INPUT_FILE"  --colored_voxels "$OUTPUT_DIR/voxel_mesh/colored_voxels.npy" --ldr_file "$OUTPUT_DIR/voxel_mesh/colored_brick.ldr"

echo "Rendering colored bricks..."

uv run blenderLego_toObj.py --in_file "$OUTPUT_DIR/voxel_mesh/colored_brick.ldr" --out_file "$OUTPUT_DIR/blender_render" 

cp "$OUTPUT_DIR/blender_render/images/0.png" "$OUTPUT_DIR/rendered_color.png"
cp "$OUTPUT_DIR/voxel_mesh/colored_brick.ldr" "$OUTPUT_DIR/colored_brick.ldr"

echo "Script finished. Check outputs in $OUTPUT_DIR"