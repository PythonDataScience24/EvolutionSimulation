from __future__ import annotations
import pygame
import random
from config import *
from abc import ABC, abstractmethod

"""
The Tile class represents a tile in a game. It is an abstract base class (ABC) that provides common functionality for different types of tiles.

Attributes:
    rect (pygame.Rect): The rectangle representing the tile's position and size.
    cell_size (int): The size of the tile in pixels.
    neighbours (dict): A dictionary of the tile's neighboring tiles, with directions as keys and Tile objects as values.

Methods:
    update(): Abstract method that should be implemented by subclasses to update the tile's state.
    draw(screen: pygame.Surface): Draws the tile on the screen.
    add_neighbor(direction: Direction, tile: Tile): Adds a neighbor tile in the specified direction.
    get_neighbor(direction: Direction) -> Tile: Returns the neighbor tile in the specified direction.
    get_directions() -> list[Direction]: Returns a list of directions to the tile's neighbors.
    get_random_neigbor() -> Tile: Returns a random neighbor tile.
"""
class Tile(ABC):
    def __init__(self, rect: pygame.Rect, cell_size: int):
        self.cell_size = max(cell_size, MIN_TILE_SIZE)
        self.rect = rect
        self.neighbours = {}
        self.temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

    @abstractmethod
    def update(self):
        """
        Abstract method that should be implemented by subclasses to update the tile's state.
        """
        pass

    # TODO: this method does not currently work / display the borders, find a way to fix it
    def draw(self, screen: pygame.Surface):
        """
        Draws the tile on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the tile on.
        """
        pygame.draw.rect(self.temp_surface, tile_border_color, self.rect, tile_outline_thickness)
        #pygame.draw.rect(screen, tile_border_color, self.rect, tile_outline_thickness)
        screen.blit(self.temp_surface, (self.rect.left, self.rect.top))

    def add_neighbor(self, direction: Direction, tile: 'Tile'):
        """
        Adds a neighbor tile in the specified direction.

        Args:
            direction (int): The direction of the neighbor tile.
            @see config for declaration of directions as variables
            tile: The neighbor tile to add.
        """
        if tile is None:
            raise ValueError("Tile is None")

        #if not Direction.is_valid_direction(direction):
        #    raise ValueError("Invalid direction", direction)
        
        self.neighbours[direction] = tile

    def get_neighbor(self, direction: Direction) -> Tile:
        """
        Returns the neighbor tile in the specified direction.

        Args:
            direction (Direction): The direction of the neighbor tile.

        Returns:
            The neighbor tile in the specified direction.
        """
        if direction not in self.neighbours:
            raise ValueError("Invalid direction")
        
        return self.neighbours[direction]

    def get_directions(self) -> list[Direction]:
        """
        Returns a list of directions to the tile's neighbors.

        Returns:
            A list of directions to the tile's neighbors.
        """
        return list(self.neighbours.keys())

    def get_random_neigbor(self) -> Tile:
        """
        Returns a random neighbor tile.

        Returns:
            A random neighbor tile.
        """
        if not self.neighbours:
            raise ValueError("No neighbors available")
        
        return self.neighbours[random.choice(self.get_directions())]