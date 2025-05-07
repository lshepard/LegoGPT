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

uv run blenderLego_toObj.py --in_file "$INPUT_FILE" --out_file "$OUTPUT_DIR"


if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: blenderLego_toObj.py did not create directory: $OUTPUT_DIR"
    exit 1
fi

mkdir -p "$OUTPUT_DIR/texture_output"
mkdir -p "$OUTPUT_DIR/texture_render"

echo "Generating texture..."

cd FlashTex

python generate_texture.py --input_mesh "$OUTPUT_DIR/lego_structure_joint.obj"  \
                           --output "$OUTPUT_DIR/texture_output" \
                           --prompt "$PROMPT" --production


echo "Rendering texture..."

cd ../blender-render-toolkit


uv run blender_obj_uv_normal.py --data_path "$OUTPUT_DIR/texture_output" \
                               --obj_name output_mesh \
                               --albedo_map texture_kd.png \
                               --normal_map None \
                               --scale 1.0 \
                               --start_rot_x 270 \
                               --start_rot_z 180 \
                               --output_path "$OUTPUT_DIR/texture_render/"


cd ../

echo "Script finished. Check outputs in $OUTPUT_DIR"