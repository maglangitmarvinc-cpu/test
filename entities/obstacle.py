"""A level obstacle occupies one grid cell but is drawn as a 3D prop."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Obstacle:
    x: int
    y: int
    kind: str

    @property
    def cell(self):
        return self.x, self.y
