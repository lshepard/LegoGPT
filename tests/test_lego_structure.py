from legogpt.data.lego_structure import LegoBrick, LegoStructure


def test_lego_brick():
    brick_txt = '6x2 (0,1,2)\n'
    brick_json = {'brick_id': 3, 'x': 0, 'y': 1, 'z': 2, 'ori': 1}
    for brick in [LegoBrick.from_json(brick_json), LegoBrick.from_txt(brick_txt)]:
        assert brick.brick_id == 3
        assert brick.ori == 1
        assert brick.area == 12
        assert brick.slice_2d == (slice(0, 6), slice(1, 3))
        assert brick.slice == (slice(0, 6), slice(1, 3), 2)
        assert brick.to_json() == brick_json
        assert brick.to_txt() == brick_txt


def test_lego_structure():
    lego_txt = '2x6 (0,0,0)\n2x6 (0,2,0)\n'
    lego_json = {
        '1': {'brick_id': 3, 'x': 0, 'y': 0, 'z': 0, 'ori': 0, },
        '2': {'brick_id': 3, 'x': 0, 'y': 2, 'z': 0, 'ori': 0, },
    }

    for structure in [LegoStructure.from_json(lego_json), LegoStructure.from_txt(lego_txt)]:
        assert len(structure) == 2
        assert structure.to_json() == lego_json
        assert structure.to_txt() == lego_txt
