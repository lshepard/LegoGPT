import pytest

from legogpt.data import LegoBrick, LegoStructure


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
    lego_txt = '2x6 (0,0,0)\n2x6 (2,0,0)\n'
    lego_json = {
        '1': {'brick_id': 3, 'x': 0, 'y': 0, 'z': 0, 'ori': 0},
        '2': {'brick_id': 3, 'x': 2, 'y': 0, 'z': 0, 'ori': 0},
    }
    lego_ldr = '1 115 20.0 0 60.0 0 0 1 0 1 0 -1 0 0 2456.DAT\n0 STEP\n' \
               '1 115 60.0 0 60.0 0 0 1 0 1 0 -1 0 0 2456.DAT\n0 STEP\n'

    for lego in [LegoStructure.from_json(lego_json), LegoStructure.from_txt(lego_txt), LegoStructure.from_ldr(lego_ldr)]:
        assert len(lego) == 2
        assert lego.to_json() == lego_json
        assert lego.to_txt() == lego_txt
        assert lego.to_ldr() == lego_ldr


@pytest.mark.parametrize(
    'brick_txt,has_collisions', [
        ('2x6 (0,0,0)\n2x6 (2,0,0)\n', False),
        ('2x6 (0,0,0)\n2x6 (1,0,0)\n', True),
    ])
def test_collision_check(brick_txt: str, has_collisions: bool):
    lego = LegoStructure.from_txt(brick_txt)
    assert lego.has_collisions() == has_collisions


@pytest.mark.parametrize(
    'brick_txt,has_floating_bricks', [
        ('2x6 (0,0,0)\n2x6 (2,0,0)\n', False),
        ('2x6 (0,0,0)\n2x6 (2,0,1)\n', True),
    ])
def test_floating_check(brick_txt: str, has_floating_bricks: bool):
    lego = LegoStructure.from_txt(brick_txt)
    assert lego.has_floating_bricks() == has_floating_bricks


@pytest.mark.parametrize(
    'brick_txt,is_stable', [
        ('2x6 (0,0,0)\n2x6 (2,0,0)\n', True),
        ('2x6 (0,0,0)\n2x6 (2,0,1)\n', False),
    ])
def test_stability_check(brick_txt: str, is_stable: bool):
    lego = LegoStructure.from_txt(brick_txt)
    assert lego.is_stable() == is_stable


@pytest.mark.parametrize(
    'brick_txt,is_in_bounds', [
        ('2x6 (0,0,0)\n', True),
        ('2x6 (18,0,0)\n', True),
        ('2x6 (19,0,0)\n', False),
    ])
def test_in_bounds(brick_txt: str, is_in_bounds: bool):
    lego = LegoStructure([], world_dim=20)
    brick = LegoBrick.from_txt(brick_txt)
    assert lego.brick_in_bounds(brick) == is_in_bounds
