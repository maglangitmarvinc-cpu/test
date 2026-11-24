"""Immutable data shared by the five themed adventure levels."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LevelConfig:
    name: str
    subtitle: str
    sky: tuple
    floor: tuple
    tile_a: tuple
    tile_b: tuple
    accent: tuple
    obstacles: tuple
    enemies: tuple
    enemy_speed: float
    step_time: float
    ambient: str
    music_notes: tuple
