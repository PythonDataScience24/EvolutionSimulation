import sys

import pygame

import helper.formatter
import settings.colors
import settings.gui
import settings.simulation
from entities.animal import Animal
from entities.organism import Organism
from entities.plant import Plant
from world.tile import Tile
from world.world import World


class Simulation:
    STARTING_FPS_LIMIT: int = 60

    def __init__(self, height: int, width: int, tile_size: int):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption("Evolution Simulation")
        self.screen: pygame.Surface = pygame.display.set_mode(
            (width, height), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.height: int = height
        self.width: int = width
        self.tile_size: int = tile_size

        self.world: World = World(height, width, tile_size)

        # Game speed
        self.fps_max_limit: int = self.STARTING_FPS_LIMIT
        self.increase_game_speed: bool = False
        self.decrease_game_speed: bool = False

        self.menu_open: bool = False

        self.stat_showing_organism: Organism | None = None

        self.is_paused = False
        self.running = True

    # TODO enable spawning of animals and plants via mouse
    # TODO enable stat displaying of animals and plants by klicking on them via mouse
    # TODO implement settings panel
    # TODO implement menu panel
    def simulate(self):
        """
        The main loop of the simulation. Updates the state of the animals and plants, handles their interactions,
        and manages the spawning of new animals and plants.
        """
        self.running = True
        self.is_paused = False

        while self.running:
            event: pygame.event.Event = pygame.event.poll()

            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            self.handle_key_down(event)

            self.handle_key_up(event)

            self.handle_mouse_button_down(event)

            if not self.is_paused:
                self.screen.fill(settings.colors.SIMULATION_BACKGROUND_COLOR)
                self.world.update()
                self.world.draw()
                self.stat_panels()
                self.stat_organism()

            if self.menu_open:
                self.draw_menu()
            else:
                self.stat_panels()

            self.handle_game_speed()
            self.clock.tick(self.fps_max_limit)

            pygame.display.flip()

    def stat_organism(self):
        if self.stat_showing_organism:
            if (
                self.stat_showing_organism.is_alive()
                or settings.gui.show_dead_organisms_stats
            ):
                pygame.draw.rect(
                    self.screen,
                    settings.colors.SELECTED_ORGANISM_COLOR,
                    self.stat_showing_organism.shape,
                    width=settings.colors.SELECTED_ORGANISM_RECT_WIDTH,
                )
                self.stat_showing_organism.show_stats()
            else:
                self.stat_showing_organism.stat_panel = None
                self.stat_showing_organism = None

    def handle_key_down(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            print("Key Pressed", event.key)
            if event.key == pygame.K_ESCAPE:
                self.menu_open = not self.menu_open
                self.is_paused = (
                    self.menu_open
                )  # Pause the simulation when the menu is open
            elif event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
            elif event.key == pygame.K_RETURN:
                chance_to_spawn_animals = 0.001
                self.world.spawn_animals(chance_to_spawn=chance_to_spawn_animals)
            elif event.key == pygame.K_1 and pygame.key.get_mods() and pygame.KMOD_ALT:
                settings.gui.draw_height_level = not settings.gui.draw_height_level
                self.world.draw()
            elif event.key == pygame.K_2 and pygame.key.get_mods() and pygame.KMOD_ALT:
                settings.gui.draw_animal_health = not settings.gui.draw_animal_health
                self.world.draw()
            elif event.key == pygame.K_3 and pygame.key.get_mods() and pygame.KMOD_ALT:
                settings.gui.draw_animal_energy = not settings.gui.draw_animal_energy
                self.world.draw()
            elif (
                event.key == pygame.K_r and pygame.key.get_mods() and pygame.KMOD_SHIFT
            ):
                self.world = World(self.height, self.width, self.tile_size)
                self.stat_showing_organism = None
                self.world.draw()
            elif (
                event.key == pygame.K_UP and pygame.key.get_mods() and pygame.KMOD_SHIFT
            ):
                self.increase_game_speed = True
                self.decrease_game_speed = False
            elif (
                event.key == pygame.K_DOWN
                and pygame.key.get_mods()
                and pygame.KMOD_SHIFT
            ):
                self.increase_game_speed = False
                self.decrease_game_speed = True

    def handle_key_up(self, event: pygame.event.Event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP and pygame.key.get_mods() and pygame.KMOD_SHIFT:
                self.increase_game_speed = False
            elif (
                event.key == pygame.K_DOWN
                and pygame.key.get_mods()
                and pygame.KMOD_SHIFT
            ):
                self.decrease_game_speed = False

    def handle_mouse_button_down(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tile: Tile = self.world.get_tile(mouse_x, mouse_y)

            self.world.draw()
            self.stat_panels()

            if tile.has_animal():
                self.stat_showing_organism = tile.animal
                pygame.draw.rect(
                    self.screen,
                    settings.colors.SELECTED_ORGANISM_COLOR,
                    self.stat_showing_organism.shape,
                    width=settings.colors.SELECTED_ORGANISM_RECT_WIDTH,
                )
                self.stat_showing_organism.show_stats()
            elif tile.has_plant():
                self.stat_showing_organism = tile.plant
                pygame.draw.rect(
                    self.screen,
                    settings.colors.SELECTED_ORGANISM_COLOR,
                    self.stat_showing_organism.shape,
                    width=settings.colors.SELECTED_ORGANISM_RECT_WIDTH,
                )
                self.stat_showing_organism.show_stats()
            else:
                if self.stat_showing_organism:
                    self.stat_showing_organism.stat_panel = None
                    self.stat_showing_organism = None

    def draw_menu(self):
        self.screen.fill(settings.colors.MENU_BACKGROUND_COLOR)
        text_surface: pygame.Surface = settings.gui.menu_font.render(
            settings.gui.menu_text,
            True,
            settings.colors.SIMULATION_BACKGROUND_COLOR,
        )
        text_rect = text_surface.get_rect(center=(self.width / 2, self.height / 2))
        self.screen.blit(text_surface, text_rect)

    def handle_game_speed(self):
        if (
            self.increase_game_speed
            and self.fps_max_limit + settings.simulation.GAME_SPEED_CHANGE
            <= settings.simulation.MAX_FPS_LIMIT
        ):
            self.fps_max_limit += settings.simulation.GAME_SPEED_CHANGE
        elif (
            self.decrease_game_speed
            and self.fps_max_limit > settings.simulation.GAME_SPEED_CHANGE
        ):
            self.fps_max_limit -= settings.simulation.GAME_SPEED_CHANGE

    def stat_panels(self):
        self.upper_stat_panel()
        self.lower_stat_panel()

    def upper_stat_panel(self):
        panel_height = int(settings.gui.stat_panel_height_percentage * self.height)
        font_size = int(settings.gui.stat_panel_font_percentage * panel_height)

        # Drawing base panel for upper stats
        pygame.draw.rect(
            self.screen,
            settings.colors.STAT_BAR_BACKGROUND_COLOR,
            pygame.Rect(0, 0, self.width, panel_height),
        )
        pygame.draw.line(
            self.screen,
            settings.colors.STAT_BAR_BORDER_COLOR,
            (0, panel_height),
            (self.width, panel_height),
            width=settings.gui.stat_panel_line_width,
        )

        # Stats to display in the upper panel
        upper_stats = [
            ("FPS", round(self.clock.get_fps())),
            ("FPS Max Setting", round(self.fps_max_limit)),
        ]
        self.draw_stats(upper_stats, font_size, (panel_height - (font_size / 2)) / 2)

    def lower_stat_panel(self):
        panel_height = int(settings.gui.stat_panel_height_percentage * self.height)
        font_size = int(settings.gui.stat_panel_font_percentage * panel_height)

        # Drawing base panel for lower stats
        pygame.draw.rect(
            self.screen,
            settings.colors.STAT_BAR_BACKGROUND_COLOR,
            pygame.Rect(0, self.height - panel_height, self.width, panel_height),
        )
        pygame.draw.line(
            self.screen,
            settings.colors.STAT_BAR_BORDER_COLOR,
            (0, self.height - panel_height),
            (self.width, self.height - panel_height),
            width=settings.gui.stat_panel_line_width,
        )

        # Stats to display in the lower panel
        lower_stats = [
            ("Organisms birthed", Organism.organisms_birthed),
            ("Organisms died", Organism.organisms_died),
            ("Animals birthed", Animal.animals_birthed),
            ("Animals died", Animal.animals_died),
            ("Plants birthed", Plant.plants_birthed),
            ("Plants died", Plant.plants_died),
        ]
        self.draw_stats(
            lower_stats, font_size, self.height - (panel_height + (font_size / 2)) / 2
        )

    def draw_stats(self, stats, font_size, panel_y):
        stats_font = pygame.font.Font(None, font_size)

        stats_texts = []
        for label, value in stats:
            value = helper.formatter.format_number(value)
            stats_texts.append(
                stats_font.render(
                    f"{label}: {value}", True, settings.colors.STAT_BAR_FONT_COLOR
                )
            )

        # Calculate the spacing and positions
        num_stats = len(stats_texts)
        spacing = self.width / (num_stats + 1)
        text_height = panel_y

        # Drawing stat text
        for index, text in enumerate(stats_texts):
            x_position = spacing * (index + 1) - (text.get_width() / 2)
            self.screen.blit(text, (x_position, text_height))
