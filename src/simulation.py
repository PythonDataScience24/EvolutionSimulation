import sys
import pygame as pg

import settings.config as config
import settings.gui_settings as gui_settings
from settings.colors import SIMULATION_BACKGROUND_COLOR, MENU_BACKGROUND_COLOR, STAT_BAR_BACKGROUND_COLOR, STAT_BAR_BORDER_COLOR, STAT_BAR_FONT_COLOR
from world.world import World
from entities.organism import Organism
from entities.plant import Plant
from entities.animal import Animal
from world.tile import Tile
from helper.formatter import format_number

class Simulation:
    STARTING_FPS_LIMIT: int = 60
    
    def __init__(self, height: int, width: int, tile_size : int):
        pg.display.init()
        pg.font.init()
        pg.display.set_caption("Evolution Simulation")
        self.screen: pg.Surface = pg.display.set_mode((width, height), pg.HWSURFACE | pg.DOUBLEBUF)
        self.clock: pg.time.Clock = pg.time.Clock()
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
        

    #TODO enable spawning of animals and plants via mouse
    #TODO enable stat displaying of animals and plants by klicking on them via mouse
    #TODO implement settings panel
    #TODO implement menu panel
    def simulate(self):
        """
        The main loop of the simulation. Updates the state of the animals and plants, handles their interactions,
        and manages the spawning of new animals and plants.
        """
        running = True
        is_paused = False
        
        while running:
            event = pg.event.poll()
            
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                print("Key Pressed", event.key)
                if event.key == pg.K_ESCAPE:
                    self.menu_open = not self.menu_open
                    is_paused = self.menu_open  # Pause the simulation when the menu is open
                elif event.key == pg.K_SPACE:
                    is_paused  = not is_paused
                elif event.key == pg.K_RETURN:
                    chance_to_spawn_animals = .001
                    self.world.spawn_animals(chance_to_spawn = chance_to_spawn_animals) 
                elif event.key == pg.K_1 and pg.key.get_mods() & pg.KMOD_ALT: 
                    gui_settings.draw_height_level = not gui_settings.draw_height_level
                    self.world.draw() 
                elif event.key == pg.K_2 and pg.key.get_mods() & pg.KMOD_ALT: 
                    gui_settings.draw_animal_health = not gui_settings.draw_animal_health
                    print("Drawing animal health.")
                    self.world.draw() 
                elif event.key == pg.K_3 and pg.key.get_mods() & pg.KMOD_ALT: 
                    gui_settings.draw_animal_energy = not gui_settings.draw_animal_energy
                    print("Drawing animal energy.")
                    self.world.draw() 
                elif event.key == pg.K_r and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.world = World(self.height, self.width, self.tile_size)
                    self.stat_showing_organism = None
                    self.world.draw() 
                elif event.key == pg.K_UP and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.increase_game_speed = True
                    self.decrease_game_speed = False
                elif event.key == pg.K_DOWN and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.increase_game_speed = False
                    self.decrease_game_speed = True
            
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.increase_game_speed = False
                elif event.key == pg.K_DOWN and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.decrease_game_speed = False
                    
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                tile: Tile = self.world.get_tile(mouse_x, mouse_y)
                
                self.world.draw() 
                self.stat_panels() 
                
                if tile.has_animal():
                    self.stat_showing_organism = tile.animal
                    self.stat_showing_organism.show_stats()
                elif tile.has_plant():
                    self.stat_showing_organism = tile.plant
                    self.stat_showing_organism.show_stats()
                else:
                    if self.stat_showing_organism:
                        self.stat_showing_organism.stat_panel = None
                        self.stat_showing_organism = None
                        
            if not is_paused:
                self.screen.fill(SIMULATION_BACKGROUND_COLOR)  # Fill the screen with a white background
                self.world.update()
                self.world.draw() 
                self.stat_panels()
                
                if self.stat_showing_organism:
                    if self.stat_showing_organism.is_alive() or gui_settings.show_dead_organisms_stats:
                        self.stat_showing_organism.show_stats()
                    else:
                        self.stat_showing_organism.stat_panel = None
                        self.stat_showing_organism = None
                    
            if self.menu_open:
                self.draw_menu()
            else:  
                self.stat_panels()
                
            self.handle_game_speed()
            self.clock.tick(self.fps_max_limit)
            
            pg.display.flip()
                    
    def draw_menu(self):
        # Placeholder for menu drawing logic
        self.screen.fill(MENU_BACKGROUND_COLOR)  # Example: fill the screen with grey
        menu_text = "Simulation Paused - Menu"
        font = pg.font.Font(None, 36)
        text_surface = font.render(menu_text, True, SIMULATION_BACKGROUND_COLOR)
        text_rect = text_surface.get_rect(center=(self.width/2, self.height/2))
        self.screen.blit(text_surface, text_rect)
          
    def handle_game_speed(self):   
        GAME_SPEED_CHANGE: int = 1
        MAX_FPS_LIMIT: int = 300
        
        if self.increase_game_speed and self.fps_max_limit + GAME_SPEED_CHANGE <= MAX_FPS_LIMIT:
            self.fps_max_limit += GAME_SPEED_CHANGE
        elif self.decrease_game_speed and self.fps_max_limit > GAME_SPEED_CHANGE:
            self.fps_max_limit -= GAME_SPEED_CHANGE
       
    def stat_panels(self):
        self.upper_stat_panel()
        self.lower_stat_panel()
         
    def upper_stat_panel(self):
        font_size = int(0.02 * self.height)
        panel_height = int(0.03 * self.height)
        line_width: int = 2

        # Drawing base panel for upper stats
        pg.draw.rect(self.screen, STAT_BAR_BACKGROUND_COLOR, pg.Rect(0, 0, self.width, panel_height))
        pg.draw.line(self.screen, STAT_BAR_BORDER_COLOR, (0, panel_height), (self.width, panel_height), width=line_width)

        # Stats to display in the upper panel
        upper_stats = [
            ("FPS", round(self.clock.get_fps())), 
            ("FPS Max Setting", round(self.fps_max_limit))
        ]
        self.draw_stats(upper_stats, font_size, (panel_height - (font_size / 2)) / 2)

    def lower_stat_panel(self):
        font_size = int(0.02 * self.height)
        panel_height = int(0.03 * self.height)
        line_width: int = 2

        # Drawing base panel for lower stats
        pg.draw.rect(self.screen, STAT_BAR_BACKGROUND_COLOR, pg.Rect(0, self.height - panel_height, self.width, panel_height))
        pg.draw.line(self.screen, STAT_BAR_BORDER_COLOR, (0, self.height - panel_height), (self.width, self.height - panel_height), width=line_width)

        # Stats to display in the lower panel
        lower_stats = [
            ("Organisms birthed", Organism.organisms_birthed),
            ("Organisms died", Organism.organisms_died),
            ("Animals birthed", Animal.animals_birthed),
            ("Animals died", Animal.animals_died),
            ("Plants birthed", Plant.plants_birthed),
            ("Plants died", Plant.plants_died)
        ]
        self.draw_stats(lower_stats, font_size, self.height - (panel_height + (font_size / 2)) / 2)
 
    def draw_stats(self, stats, font_size, panel_y):
        stats_font = pg.font.Font(None, font_size)
        
        stats_texts = []
        for label, value in stats:
            value = format_number(value)
            stats_texts.append(stats_font.render(f"{label}: {value}", True, STAT_BAR_FONT_COLOR))
    
        # Calculate the spacing and positions
        num_stats = len(stats_texts)
        spacing = self.width / (num_stats + 1)
        text_height = panel_y

        # Drawing stat text
        for index, text in enumerate(stats_texts):
            x_position = spacing * (index + 1) - (text.get_width() / 2)
            self.screen.blit(text, (x_position, text_height))  


    