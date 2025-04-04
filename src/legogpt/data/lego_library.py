import json
from pathlib import Path

with open(Path(__file__).parent / 'lego_library.json') as f:
    lego_library = json.load(f)  # Maps brick ID to brick properties

max_brick_dimension = max(max(properties['height'], properties['width']) for properties in lego_library.values())


def _make_dimensions_to_brick_id_dict() -> dict:
    result = {}
    for brick_id, properties in lego_library.items():
        key = (properties['height'], properties['width'])
        if key not in result.keys():
            result[key] = int(brick_id)
    return result


_dimensions_to_brick_id_dict = _make_dimensions_to_brick_id_dict()


def dimensions_to_brick_id(h: int, w: int):
    if h > w:
        h, w = w, h
    try:
        return _dimensions_to_brick_id_dict[(h, w)]
    except KeyError:
        raise ValueError(f'No brick ID for brick of dimensions: {h}x{w}')


def brick_id_to_part_id(brick_id: int) -> str:
    """
    Returns the part ID of the given brick, which is the ID of the brick model used in LDraw files.
    """
    return lego_library[str(brick_id)]['partID']
