import re
import warnings
from dataclasses import dataclass

import numpy as np

from legogpt.data.lego_library import lego_library, dimensions_to_brick_id
from legogpt.stability_analysis.stability_analysis import stability_score


@dataclass(frozen=True, order=True, kw_only=True)
class LegoBrick:
    """
    Represents a 1-unit-tall rectangular LEGO brick.
    """
    h: int
    w: int
    x: int
    y: int
    z: int

    @property
    def brick_id(self) -> int:
        return dimensions_to_brick_id(self.h, self.w)

    @property
    def ori(self) -> int:
        return 1 if self.h > self.w else 0

    @property
    def area(self) -> int:
        return self.h * self.w

    @property
    def slice_2d(self) -> (slice, slice):
        return slice(self.x, self.x + self.h), slice(self.y, self.y + self.w)

    @property
    def slice(self) -> (slice, slice, int):
        return *self.slice_2d, self.z

    def __repr__(self):
        return self.to_txt()[:-1]

    def to_json(self) -> dict:
        return {
            'brick_id': self.brick_id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'ori': self.ori,
        }

    def to_txt(self) -> str:
        return f'{self.h}x{self.w} ({self.x},{self.y},{self.z})\n'

    @classmethod
    def from_json(cls, brick_json: dict):
        properties = lego_library[str(brick_json['brick_id'])]
        h, w = properties['height'], properties['width']
        if brick_json['ori'] == 1:
            h, w = w, h
        x, y, z = brick_json['x'], brick_json['y'], brick_json['z']
        return cls(h=h, w=w, x=x, y=y, z=z)

    @classmethod
    def from_txt(cls, brick_txt: str):
        brick_txt = brick_txt.strip()
        match = re.fullmatch(r'(\d+)x(\d+) \((\d+),(\d+),(\d+)\)', brick_txt)
        if match is None:
            raise ValueError(f'Text Format brick is ill-formatted: {brick_txt}')

        h, w, x, y, z = map(int, match.group(1, 2, 3, 4, 5))
        brick = cls(h=h, w=w, x=x, y=y, z=z)

        try:
            _ = brick.brick_id
        except ValueError as err:
            raise ValueError(f'Text Format brick ID is not in library: {err}')
        return brick


class LegoStructure:
    """
    Represents a LEGO structure in the form of a list of LEGO bricks.
    """

    def __init__(self, bricks: list[LegoBrick], world_dim: int = 20):
        self.world_dim = world_dim

        # Check if structure starts at ground level
        z0 = min((brick.z for brick in bricks), default=0)
        if z0 != 0:
            warnings.warn('LEGO structure does not start at ground level z=0.')

        # Build structure from bricks
        self.bricks = []
        self.voxel_occupancy = np.zeros((world_dim, world_dim, world_dim), dtype=int)
        for brick in bricks:
            self.add_brick(brick)

    def __len__(self):
        return len(self.bricks)

    def __repr__(self):
        return self.to_txt()

    def to_json(self) -> dict:
        return {str(i + 1): brick.to_json() for i, brick in enumerate(self.bricks)}

    def to_txt(self) -> str:
        return ''.join([brick.to_txt() for brick in self.bricks])

    def add_brick(self, brick: LegoBrick) -> None:
        self.bricks.append(brick)
        self.voxel_occupancy[brick.slice] += 1

    def has_collisions(self) -> bool:
        return np.any(self.voxel_occupancy > 1)

    def has_floating_bricks(self) -> bool:
        return any(self._is_floating(brick) for brick in self.bricks)

    def _is_floating(self, brick: LegoBrick) -> bool:
        if brick.z == 0:
            return False  # Supported by ground
        if np.any(self.voxel_occupancy[*brick.slice_2d, brick.z - 1]):
            return False  # Supported from below
        if brick.z != self.world_dim - 1 and np.any(self.voxel_occupancy[*brick.slice_2d, brick.z + 1]):
            return False  # Supported from above
        return True

    def is_stable(self) -> bool:
        if self.has_collisions() or self.has_floating_bricks():
            return False
        return self.stability_scores().max() < 1

    def stability_scores(self) -> np.ndarray:
        score, _, _, _, _ = stability_score(self.to_json(), lego_library)
        return score

    @classmethod
    def from_json(cls, lego_json: dict):
        bricks = [LegoBrick.from_json(v) for k, v in lego_json.items() if k.isdigit()]
        return cls(bricks)

    @classmethod
    def from_txt(cls, lego_txt: str):
        bricks_txt = lego_txt.split('\n')
        bricks_txt = list(filter(None, bricks_txt))  # Remove blank lines
        bricks = [LegoBrick.from_txt(brick) for brick in bricks_txt]
        return cls(bricks)
