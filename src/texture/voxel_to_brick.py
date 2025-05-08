from pathlib import Path

import numpy as np
import argparse
import json


def read_LEGO_Library():
    # read ../lego_library.json
    with open(Path(__file__).parent.parent / 'legogpt' / 'data' / 'lego_library.json', 'r') as file:
        lego_lib = json.load(file)
    return lego_lib

def get_other3points(partID, x, y, z, ori):
    if partID == 13 or partID == 14 or partID == 0:
        return 0, 0, 0, 0, 0, 0
    
    if str(partID) not in lego_lib:
        return 0, 0, 0, 0, 0, 0
    
    part = lego_lib[str(partID)]

    if ori == 0:
        dx = part['height']
        dy = part['width']
    else:
        dx = part['width']
        dy = part['height']

    x1, y1 = x + dx - 1, y
    x2, y2 = x, y + dy - 1
    x3, y3 = x + dx - 1, y + dy - 1

    # max 19
    x1, y1 = min(x1, 19), min(y1, 19)
    x2, y2 = min(x2, 19), min(y2, 19)
    x3, y3 = min(x3, 19), min(y3, 19)

    return x1, y1, x2, y2, x3, y3

def set_base_brick(X=20, Y=20):

    lines = []
    for i in range(0, X):
        for j in range(0, Y):
            x = (i + 0.5) * 20
            y = (j + 0.5) * 20

            line = f"1 15 {x} 0 {y} 0 0 1 0 1 0 -1 0 0 3005.DAT"
            lines.append(line)
            lines.append("0 STEP")

    return lines

def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_color_distance(color1, color2):
    """Calculate Euclidean distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5

def get_nearest_lego_color(rgb_color):
    """Find the nearest LEGO color code for a given RGB color."""
    # Define LEGO colors as (code, rgb) pairs
    lego_colors = {
        0: hex_to_rgb("#1B2A34"),    # Black
        1: hex_to_rgb("#1E5AA8"),    # Blue
        2: hex_to_rgb("#00852B"),    # Green
        3: hex_to_rgb("#069D9F"),    # Dark_Turquoise
        4: hex_to_rgb("#B40000"),    # Red
        5: hex_to_rgb("#D3359D"),    # Dark_Pink
        6: hex_to_rgb("#543324"),    # Brown
        7: hex_to_rgb("#8A928D"),    # Light_Grey
        8: hex_to_rgb("#545955"),    # Dark_Grey
        9: hex_to_rgb("#97CBD9"),    # Light_Blue
        10: hex_to_rgb("#58AB41"),   # Bright_Green
        11: hex_to_rgb("#00AAA4"),   # Light_Turquoise
        12: hex_to_rgb("#F06D61"),   # Salmon
        13: hex_to_rgb("#F6A9BB"),   # Pink
        14: hex_to_rgb("#FAC80A"),   # Yellow
        15: hex_to_rgb("#F4F4F4"),   # White
        17: hex_to_rgb("#ADD9A8"),   # Light_Green
        18: hex_to_rgb("#FFD67F"),   # Light_Yellow
        19: hex_to_rgb("#D7BA8C"),   # Tan
        20: hex_to_rgb("#AFBED6"),   # Light_Violet
        22: hex_to_rgb("#671F81"),   # Purple
        23: hex_to_rgb("#0E3E9A"),   # Dark_Blue_Violet
        25: hex_to_rgb("#D67923"),   # Orange
        26: hex_to_rgb("#901F76"),   # Magenta
        27: hex_to_rgb("#A5CA18"),   # Lime
        28: hex_to_rgb("#897D62"),   # Dark_Tan
        29: hex_to_rgb("#FF9ECD"),   # Bright_Pink
        30: hex_to_rgb("#A06EB9"),   # Medium_Lavender
        31: hex_to_rgb("#CDA4DE"),   # Lavender
        68: hex_to_rgb("#FDC383"),   # Very_Light_Orange
        69: hex_to_rgb("#8A12A8"),   # Bright_Reddish_Lilac
        70: hex_to_rgb("#5F3109"),   # Reddish_Brown
        71: hex_to_rgb("#969696"),   # Light_Bluish_Grey
        72: hex_to_rgb("#646464"),   # Dark_Bluish_Grey
        73: hex_to_rgb("#7396C8"),   # Medium_Blue
        74: hex_to_rgb("#7FC475"),   # Medium_Green
        77: hex_to_rgb("#FECCCF"),   # Light_Pink
        78: hex_to_rgb("#FFC995"),   # Light_Nougat
        84: hex_to_rgb("#AA7D55"),   # Medium_Nougat
        85: hex_to_rgb("#441A91"),   # Medium_Lilac
        86: hex_to_rgb("#7B5D41"),   # Light_Brown
        89: hex_to_rgb("#1C58A7"),   # Blue_Violet
        92: hex_to_rgb("#BB805A"),   # Nougat
        100: hex_to_rgb("#F9B7A5"),  # Light_Salmon
        110: hex_to_rgb("#26469A"),  # Violet
        112: hex_to_rgb("#4861AC"),  # Medium_Violet
        115: hex_to_rgb("#B7D425"),  # Medium_Lime
        118: hex_to_rgb("#9CD6CC"),  # Aqua
        120: hex_to_rgb("#DEEA92"),  # Light_Lime
        125: hex_to_rgb("#F9A777"),  # Light_Orange
        128: hex_to_rgb("#AD6140"),  # Dark_Nougat
        # 151: hex_to_rgb("#C8C8C8"),  # Very_Light_Bluish_Grey
        191: hex_to_rgb("#FCAC00"),  # Bright_Light_Orange
        212: hex_to_rgb("#9DC3F7"),  # Bright_Light_Blue
        216: hex_to_rgb("#872B17"),  # Rust
        218: hex_to_rgb("#8E5597"),  # Reddish_Lilac
        219: hex_to_rgb("#564E9D"),  # Lilac
        226: hex_to_rgb("#FFEC6C"),  # Bright_Light_Yellow
        232: hex_to_rgb("#77C9D8"),  # Sky_Blue
        272: hex_to_rgb("#19325A"),  # Dark_Blue
        288: hex_to_rgb("#00451A"),  # Dark_Green
        295: hex_to_rgb("#FF94C2"),  # Flamingo_Pink
        308: hex_to_rgb("#352100"),  # Dark_Brown
        313: hex_to_rgb("#ABD9FF"),  # Maersk_Blue
        320: hex_to_rgb("#720012"),  # Dark_Red
        321: hex_to_rgb("#469BC3"),  # Dark_Azure
        322: hex_to_rgb("#68C3E2"),  # Medium_Azure
        323: hex_to_rgb("#D3F2EA"),  # Light_Aqua
        326: hex_to_rgb("#E2F99A"),  # Yellowish_Green
        330: hex_to_rgb("#77774E"),  # Olive_Green
        335: hex_to_rgb("#88605E"),  # Sand_Red
        351: hex_to_rgb("#F785B1"),  # Medium_Dark_Pink
        353: hex_to_rgb("#FF6D77"),  # Coral
        366: hex_to_rgb("#D86D2C"),  # Earth_Orange
        368: hex_to_rgb("#EDFF21"),  # Neon_Yellow
        370: hex_to_rgb("#755945"),  # Medium_Brown
        371: hex_to_rgb("#CCA373"),  # Medium_Tan
        373: hex_to_rgb("#75657D"),  # Sand_Purple
        378: hex_to_rgb("#708E7C"),  # Sand_Green
        379: hex_to_rgb("#70819A"),  # Sand_Blue
        402: hex_to_rgb("#CA4C0B"),  # Reddish_Orange
        422: hex_to_rgb("#915C3C"),  # Sienna_Brown
        423: hex_to_rgb("#543F33"),  # Umber_Brown
        450: hex_to_rgb("#D27744"),  # Fabuland_Brown
        462: hex_to_rgb("#F58624"),  # Medium_Orange
        484: hex_to_rgb("#91501C"),  # Dark_Orange
        503: hex_to_rgb("#BCB4A5"),  # Very_Light_Grey
        507: hex_to_rgb("#FA9C1C"),  # Light_Orange_Brown
        508: hex_to_rgb("#C65127"),  # Fabuland_Red
        509: hex_to_rgb("#CF8A47"),  # Fabuland_Orange
        510: hex_to_rgb("#78FC78"),  # Fabuland_Lime
    }
    
    # Find the color with minimum distance
    min_distance = float('inf')
    nearest_code = 0
    
    for code, lego_rgb in lego_colors.items():
        distance = get_color_distance(rgb_color, lego_rgb)
        if distance < min_distance:
            min_distance = distance
            nearest_code = code
            
    return nearest_code

def get_brick_id_from_dimensions(height, width, lego_lib):
    for k, v in lego_lib.items():
        if (v['height'], v['width']) == (height, width) or (v['width'], v['height']) == (height, width):
            return int(k)
    # fallback: return the smallest brick
    return int(min(lego_lib.keys(), key=lambda k: lego_lib[k]['height'] * lego_lib[k]['width']))

def parse_output_string(output_str, lego_lib):
    """
    Parse the 'output' string from the new JSON format into a list of brick dicts.
    Each dict will have keys: x, y, z, ori, height, width, brick_id.
    """
    bricks = []
    for line in output_str.strip().split('\n'):
        if not line.strip():
            continue
        dims, coords = line.split(' ')
        h_raw, w_raw = map(int, dims.split('x'))
        x, y, z = map(int, coords.strip('()').split(','))
        if h_raw < w_raw:
            height, width = h_raw, w_raw
            ori = 0
        else:
            height, width = w_raw, h_raw
            ori = 1
        brick_id = get_brick_id_from_dimensions(height, width, lego_lib)
        brick = {
            'x': x,
            'y': y,
            'z': z,
            'ori': ori,
            'height': height,
            'width': width,
            'brick_id': brick_id
        }
        bricks.append(brick)
    return bricks

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--ldr_file', type=str, help='Path to LDR file', default="colored_bricks.ldr")
    parser.add_argument('--lego_file', type=str, help='Path to Lego structure file')
    parser.add_argument('--colored_voxels', type=str, help='Path to colored voxels npy file', default="colored_voxels.npy")
    parser.add_argument('--use_base', action='store_true', help='Use base brick')
    args = parser.parse_args()

    lego_lib = read_LEGO_Library()

    if args.lego_file.endswith('.json'):
        with open(args.lego_file, 'r') as f:
            data = json.load(f)['output']
    elif args.lego_file.endswith('.txt'):
        with open(args.lego_file, 'r') as f:
            data = f.read()

    if args.use_base:
        ldr_lines = set_base_brick()
        base_height = 1
    else:
        ldr_lines = []
        base_height = 0
    step_line = "0 STEP"

    colored_voxels = np.load(args.colored_voxels)

    # Parse the new output string format
    bricks = parse_output_string(data, lego_lib)

    for brick in bricks:
        part = lego_lib[str(brick['brick_id'])]

        partID = part['partID']

        y = (brick['z'] + base_height) * -24

        # Getting average color of the brick
        colors = []
        if brick["ori"] == 0:
            h, w = part['height'], part['width']
        else:
            h, w = part['width'], part['height']
        for i in range(brick["x"], brick["x"] + h):
            for j in range(brick["y"], brick["y"] + w):
                c = colored_voxels[i, j, brick["z"]]
                if c.sum() > 0:
                    colors.append(c)

        if len(colors) > 0:
            colors = np.array(colors)
            brick_color = np.mean(colors, axis=0)
        else:
            brick_color = np.zeros(3)
        # brick_color = colored_voxels[brick["x"], brick["y"], brick["z"]]
        
        # Choose color based on RGB values
        if brick_color.sum() > 0:
            # Assuming brick_color is an RGB array
            color = get_nearest_lego_color(tuple(brick_color * 255))
        else:
            color = 184  # Default to red for unstable bricks

        if brick['ori'] == 0:
            x = (brick['x'] + part['height'] * 0.5) * 20
            z = (brick['y'] + part['width'] * 0.5) * 20
            line = f"1 {color} {x} {y} {z} 0 0 1 0 1 0 -1 0 0 {partID}"
        else:
            x = (brick['x'] + part['width'] * 0.5) * 20
            z = (brick['y'] + part['height'] * 0.5) * 20
            line = f"1 {color} {x} {y} {z} -1 0 0 0 1 0 0 0 -1 {partID}"
        ldr_lines.append(line)
        ldr_lines.append(step_line)

    print("\n".join(ldr_lines))
    # Write to ldr file
    with open(args.ldr_file, 'w') as f:
        f.write("\n".join(ldr_lines))
       
if __name__ == '__main__':
    main()