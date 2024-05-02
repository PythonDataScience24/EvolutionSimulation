from __future__ import annotations

from random import random

class Gene():
    def __init__(self, max_value: float, min_value: float, value: float = None, mutation_range: float = 1) -> None:
        self._max_value: float = max_value
        self._min_value: float = min_value
        
        if not value:
            self.value: float = random() * (max_value - min_value)
        else:
            self._value: float = value
        
        self._mutation_range: float = mutation_range
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value: float):
        if value > self._max_value:
            self._value = self._max_value
            return
        if value < self._min_value:
            self._value = self._min_value
            return
        self._value = value
        
    def copy(self) -> Gene:
        return Gene(self._max_value, self._min_value, self.value, self._mutation_range)
    
    def mutate(self) -> None:
        self.value += (self._mutation_range * 2 * random()) - self._mutation_range