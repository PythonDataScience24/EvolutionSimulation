from typing import Optional, List
from pygame import Color, Rect, Surface
from organism import Organism
from tile import Tile
from random import randint, random, choice
from config import *
    
class Plant(Organism):
    @property
    def MAX_HEALTH(self) -> float:
        return 100

    @property
    def MAX_ENERGY(self) -> float:
        return 100
    
    PLANT_COLOR = Color("black")
        
    BASE_GROWTH: float = 1
    BASE_GROWTH_CHANCE: float = .01
    
    GROWTH_RATE_INCREASE_BY_WATER: float = 5
    GROWTH_CHANCE_INCREASE_BY_WATER: float = .05
    GROW_FOR_YOURSELF_UNTIL_THRESHOLD: float = .5
    NATURAL_GROWTH_LOSS_PERCENTAGE_THRESHOLD: float = .9
    NATURAL_GROWTH_LOSS_CHANCE: float = .02
    NATURAL_GROWTH_LOSS_AMOUNT: float = 1
    
    MIN_PLANT_COLOR: Color = Color(235, 242, 230, ground_alpha)
    MAX_PLANT_COLOR: Color = Color(76, 141, 29, ground_alpha)
    
    def __init__(self, tile: Tile, shape: Rect|None = None, color: Color|None = None, 
                 health: Optional[float] = None, 
                 energy: Optional[float] = None,):
        if not shape:
            shape = tile.rect
            
        if not color:
            color = Color(randint(20,230), randint(20,230), randint(20,230))
            
        if not health:
            health = self.MAX_HEALTH / 2
            
        if not energy:
            energy = self.MAX_ENERGY / 2
            
        super().__init__(tile, shape, color, health, energy)
        
        self.growth: float = self.BASE_GROWTH
        
    def update(self):
        self.use_energy(2) #TODO make this a variable
        self.gain_energy(random() * 4)
        
        if self.energy > 0:
            self.grow()
        
        if not self.is_alive():
            self.die()
            return
    
    def grow(self):        
        if random() <= self.growth_chance():
            if self.health + self.growth < self.MAX_HEALTH:
                self.use_energy(self.growth)
                self.gain_health(self.growth)
                
            # if self.energy_ratio() > 0.5:
            #     options: List[Tile] = self.tile.get_neighbors()
            #     tile_to_grow: Tile = choice(options)
            #     tile_to_grow.add_plant()
                
    def growth_chance(self):
        return self.BASE_GROWTH_CHANCE - self.tile.calculate_growth_height_penalty(self.BASE_GROWTH_CHANCE)
    
    def draw(self, screen: Surface):
        pass