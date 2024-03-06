from __future__ import annotations
import pygame

MIN_WATER_VALUE = 0
MAX_WATER_VALUE = 10
MIN_GRASS_VALUE = 0
MAX_GRASS_VALUE = 10

# Settings
LAND_PERCENTAGE = .9
DRAW_WATER_LEVEL = True
SURROUNDED_BY_WATER = True
MIN_TILE_SIZE = 4

tile_outline_thickness = 1

# Alpha values for grids
ground_alpha = 255
ground_font_alpha = 100
surface_alpha = 255
sky_alpha = 100

# Colors
tile_border_color = pygame.Color("black")
dirt_color = pygame.Color(155, 118, 83, ground_alpha)
min_grass_color = pygame.Color(235, 242, 230, ground_alpha)
max_grass_color = pygame.Color(76, 141, 29, ground_alpha)
min_water_color = pygame.Color(204, 229, 233, ground_alpha)
max_water_color = pygame.Color(26, 136, 157, ground_alpha)

from enum import Enum

class ExtendedEnum(Enum):
    @classmethod
    def get_options(cls):
        return list(map(lambda c: c.value, cls))

class Direction(ExtendedEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    
    @staticmethod
    def is_valid_direction(direction : Direction) -> bool:
        return direction in Direction.get_options()