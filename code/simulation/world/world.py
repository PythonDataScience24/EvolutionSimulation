from __future__ import annotations

import random

import pygame

import settings.database
from settings.setting import Setting
import settings.simulation
from helper.noise_function import NoiseFunction
from entities.animal import Animal
from entities.plant import Plant
from helper.direction import Direction
from world.tile import Tile
import pygame_menu


class World(pygame.sprite.Sprite):
    loading_screen_theme = pygame_menu.pygame_menu.themes.THEME_GREEN.copy()
    loading_screen_theme.title = False

    def __init__(self, rect: pygame.Rect, tile_size: int):
        pygame.sprite.Sprite.__init__(self)
        self.age: int = 0

        self.rect: pygame.Rect = rect
        self.image: pygame.Surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.organism_surface: pygame.Surface = self.image.copy()
        self.ground_surface: pygame.Surface = self.image.copy()
        self.generating = False
        self.progress = 0
        self.progress_bar = None

        self.tile_size = tile_size
        self.cols = self.rect.width // tile_size
        self.rows = self.rect.height // tile_size

        self._setup_noise_functions()
        self._setup_progress_bar()

        #region tiles
        self.tiles = pygame.sprite.Group()
        tiles_grid = [[None for _ in range(self.cols)] for _ in range(self.rows)] # Only used for add_neighbors
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.create_tile(row, col)
                tiles_grid[row][col] = tile
                self.tiles.add(tile)
        self.add_neighbors(tiles_grid)
        self.tiles.draw(self.ground_surface)
        #endregion

    #region main methods
    def update(self) -> None:
        """
        Update the world state by incrementing the age and updating the organisms in the simulation.

        Parameters:
            None

        Returns:
            None
        """
        self.age += 1
        settings.simulation.organisms.update()

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the world on the screen.

        This method first blits the ground surface onto the image of the world. Then, it clears any previous drawings on the organism surface by filling it with a transparent color. Next, it draws all the organisms from the simulation onto the organism surface. Finally, it blits the organism surface onto the image of the world and then blits the entire image onto the screen.

        Parameters:
            screen (pygame.Surface): The surface representing the screen where the world will be drawn.

        Returns:
            None
        """
        if self.generating:
            if self.progress_bar:
                self.menu.draw(self.image)
        else:
            self.image.blit(self.ground_surface, self.rect)

            # Clear previous drawings on the organism surface
            self.organism_surface.fill((0, 0, 0, 0))
            settings.simulation.organisms.draw(self.organism_surface)
            self.image.blit(self.organism_surface, self.rect)

        screen.blit(self.image, self.rect)

    def reload(self) -> None:
        """
        Reload the height and moisture values for all tiles in the world.

        This method iterates over all tiles in the world and updates their height and moisture values based on the current noise settings of the world. It then redraws the updated tiles on the ground surface of the world.

        Parameters:
            None

        Returns:
            None
        """
        # TODO rethink if noise method should be transfered to tiles
        tiles: list[Tile] = self.tiles.sprites()
        for tile in tiles:
            tile.height = self.generate_height_values(tile.rect.x, tile.rect.y)
            tile.moisture = self.generate_moisture_values(tile.rect.x, tile.rect.y)
            tile.draw(self.ground_surface)
    #endregion

    #region spawning
    def spawn_animals(self, amount: float = 1) -> None:
        """
        Spawn a specified amount of animals on unoccupied tiles in the world.

        This method randomly selects 'amount' number of tiles from the world's tiles group and attempts to spawn an animal on each selected tile.
        Animals will only be spawned on tiles that are not already occupied by another animal.

        Parameters:
            amount (float, optional): The number of animals to spawn. Defaults to 1.

        Returns:
            None
        """
        # TODO this should ignore tiles that are occupied and only try to spawn on unoccupied tiles
        for tile in random.choices(self.tiles.sprites(), k = amount):
            self.spawn_animal(tile)

    def spawn_plants(self, amount: float = 1) -> None:
        """
        Spawn a specified amount of plants on unoccupied tiles in the world.

        This method randomly selects 'amount' number of tiles from the world's tiles group and attempts to spawn a plant on each selected tile.
        Plants will only be spawned on tiles that are not already occupied by another plant or animal.

        Parameters:
            amount (float, optional): The number of plants to spawn. Defaults to 1.

        Returns:
            None
        """
        # TODO this should ignore tiles that are occupied and only try to spawn on unoccupied tiles
        for tile in random.choices(self.tiles.sprites(), k = amount):
            self.spawn_plant(tile)

    def spawn_animal(self, tile: Tile) -> None:
        """
        Spawn an animal on a specified tile if the tile is not occupied by water or another animal.

        Parameters:
            tile (Tile): The tile on which the animal will be spawned.

        Returns:
            None
        """
        if not(tile.has_water or tile.has_animal()):
            animal = Animal(tile)
            settings.simulation.organisms.add(animal)
            settings.simulation.animals.add(animal)

    def spawn_plant(self, tile: Tile) -> None:
        """
        Spawn a plant on a specified tile if the tile is not occupied by water or another plant.

        Parameters:
            tile (Tile): The tile on which the plant will be spawned.

        Returns:
            None
        """
        if not(tile.has_water or tile.has_plant()):
            plant = Plant(tile)
            settings.simulation.organisms.add(plant)
            settings.simulation.plants.add(plant)
    #endregion

    #region tiles
    def create_tile(self, row: int, col: int) -> Tile:
        """
        Create a new Tile object based on the given row and column coordinates.

        Parameters:
            row (int): The row index of the tile.
            col (int): The column index of the tile.

        Returns:
            Tile: A new Tile object initialized with the specified position, height, moisture, and border status.
        """
        x = col * self.tile_size
        y = row * self.tile_size

        return Tile(
            pygame.Rect(x ,y ,self.tile_size, self.tile_size),
            height = self.generate_height_values(x, y),
            moisture = self.generate_moisture_values(x, y),
            is_border = self.is_border_tile(row=row, col=col),
        )

    def add_neighbors(self, tiles) -> None:
        """
        Add neighbors to each tile in the world based on the grid of tiles provided.

        For each tile in the grid, this method checks the neighboring tiles in the cardinal directions (north, east, south, west) and adds them as neighbors to the current tile. This allows each tile to have references to its adjacent tiles for interaction and calculations.

        Parameters:
            tiles (list[list[Tile]]): A 2D grid of Tile objects representing the world map.

        Returns:
            None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                tile: Tile = tiles[row][col]
                if row > 0:
                    tile.add_neighbor(Direction.NORTH, tiles[row-1][col])
                if col < self.cols - 1:
                    tile.add_neighbor(Direction.EAST, tiles[row][col+1])
                if row < self.rows - 1:
                    tile.add_neighbor(Direction.SOUTH, tiles[row+1][col])
                if col > 0:
                    tile.add_neighbor(Direction.WEST, tiles[row][col-1])

    def is_border_tile(self, row: int, col: int) -> bool:
        """
        Determine if a given tile at the specified row and column coordinates is a border tile.

        A border tile is defined as a tile that is located at the edge of the world grid, meaning it is either in the first row, last row, first column, or last column of the grid.

        Parameters:
            row (int): The row index of the tile.
            col (int): The column index of the tile.

        Returns:
            bool: True if the tile is a border tile, False otherwise.
        """
        return row == 0 or col == 0 or row == self.rows - 1 or col == self.cols - 1

    def get_tiles(self, rect: pygame.Rect) -> list[Tile]:
        """
        Get a list of tiles that intersect with the given rectangle in the world.

        This method takes a pygame Rect object representing a rectangle in global coordinates and transforms it into world coordinates by adjusting its position based on the world's position. It then creates a temporary sprite with the transformed rectangle and checks for collisions with the world's tiles. The method returns a list of Tile objects that intersect with the transformed rectangle.

        Parameters:
            rect (pygame.Rect): A pygame Rect object representing a rectangle in global coordinates.

        Returns:
            list[Tile]: A list of Tile objects that intersect with the given rectangle.
        """
        # Transform rect global coordinates into world coordinates
        rect.x -= self.rect.left
        rect.y -= self.rect.top

        s = pygame.sprite.Sprite()
        s.rect = rect
        return pygame.sprite.spritecollide(s, self.tiles, False)

    def get_tile(self, pos: tuple[int, int]) -> Tile:
        """
        Get the tile at the specified position in the world.

        Parameters:
            pos (tuple[int, int]): The position coordinates (x, y) of the tile in global coordinates.

        Returns:
            Tile: The Tile object at the specified position in the world.
        """
        # Transform global coordinates into world coordinates
        x = pos[0] - self.rect.left
        y = pos[1] - self.rect.top
        
        s = pygame.sprite.Sprite()
        s.rect = pygame.Rect(x, y, 1, 1)
        return pygame.sprite.spritecollideany(s, self.tiles)
    #endregion

    #region noise
    def _setup_noise_functions(self):
        self.moisture_setting: Setting = Setting(1, self.reload, name="Moisture", min=0, max=2, type="onchange")
        self.height_setting: Setting = Setting(1, self.reload, name="Height", min=0, max=2, type="onchange")
        self.scale_setting: Setting = Setting(.001, self.reload, name="Scale", min = 0, max=0.01, type="onchange", increment=.0001)

        self.height_functions: list[NoiseFunction] = []
        self.height_functions_weights: list[float] = []
        self.height_functions.append(NoiseFunction(
            self.reload, factor_x=1, factor_y=1, offset_x=0, offset_y=0,
        ))
        self.height_functions_weights.append(1)
        self.height_functions.append(NoiseFunction(
            self.reload, factor_x=2, factor_y=2, offset_x=4.7, offset_y=2.3
        ))
        self.height_functions_weights.append(.2)
        self.height_functions.append(NoiseFunction(
            self.reload, factor_x=4, factor_y=4, offset_x=19.1, offset_y=16.2
        ))
        self.height_functions_weights.append(.1)

        self.moisture_functions: list[NoiseFunction] = []
        self.moisture_functions_weights: list[float] = []
        self.moisture_functions.append(NoiseFunction(
            self.reload, factor_x=1, factor_y=1, offset_x=0, offset_y=0
        ))
        self.moisture_functions_weights.append(1)

    #region noise generators
    def generate_height_values(self, x: int, y: int) -> float:
        height = NoiseFunction.weigh(x * self.scale_setting._value, y *  self.scale_setting._value, self.height_functions, self.height_functions_weights)
        height += (self.height_setting._value - self.height_setting._mid)
        height = pygame.math.clamp(height, 0, 1)
        return height

    def generate_moisture_values(self, x: int, y: int) -> float:
        moisture = NoiseFunction.weigh(x * self.scale_setting._value, y * self.scale_setting._value, self.moisture_functions, self.moisture_functions_weights)
        moisture += (self.moisture_setting._value - self.moisture_setting._mid)
        moisture = pygame.math.clamp(moisture, 0, 1)
        return moisture

    #endregion

    def randomise_freqs(self):
        self.generating = True
        self.progress = 0

        functions = []
        functions.extend(self.height_functions)
        functions.extend(self.moisture_functions)

        for function in functions:
            function.randomise()
            self.progress += 100 / len(functions)
            self.progress_bar.set_value(self.progress)
            self.menu.draw(pygame.display.get_surface())
            pygame.display.flip()

        self.reload()
        self.generating = False
        self.progress = 0
        self.progress_bar.set_value(self.progress)

    #endregion

    def _setup_progress_bar(self) -> None:
        self.menu = pygame_menu.Menu("", width=self.rect.width, height=self.rect.height, theme=self.loading_screen_theme, position=(self.rect.left,self.rect.top,False))
        self.progress_bar = self.menu.add.progress_bar("Generating World")

    def copy(self) -> World:
        """
        Create a copy of the World instance.

        Note:
            This does not create an exact copy right now as the noise values have random values that are defined in the initialisation.

            This should only be used to create a copy world of the same dimension and tile size

        Returns:
            World: A new World instance with the same dimensions and tile size as the original.
        """
        # TODO not working properly yet as _setup_noise_settings initiates with random variables so not exact copy
        return World(self.rect.copy(), self.tile_size)

    #region static methods
    @staticmethod
    def adjust_dimensions(rect: pygame.Rect, tile_size: int) -> pygame.Rect:
        """
        Adjust the dimensions of a rectangle to be multiples of a given tile size.

        Parameters:
            rect (pygame.Rect): The rectangle whose dimensions need to be adjusted.
            tile_size (int): The size of the tiles to which the dimensions should be adjusted.

        Returns:
            pygame.Rect: A new rectangle with adjusted dimensions that are multiples of the tile size.
        """
        rect.width = (rect.width // tile_size) * tile_size
        rect.height = (rect.height // tile_size) * tile_size

        return rect
    #endregion
