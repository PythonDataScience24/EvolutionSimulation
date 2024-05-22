import pygame_menu
import random

class Setting():
    # TODO think of amking value an optional argument and if _mid existst then setting value equal to it else it being 0
    def __init__(self, value: float, *args, name: str = "None", min: float = None, max: float = None, type: str = "onreturn", **kwargs,) -> None:
        self._value = value
        self._name = name
        self._min = min
        self._max = max
        self._mid =  None
        if self._max is not None and self._min is not None:
            if "increment" in kwargs:
                self.increment = kwargs["increment"]
            else:
                self.increment = (self._max-self._min)/100
            self._mid = (self._max-self._min) / 2
        
        self._onreturn = False
        self._onchange = False
        if type == "onreturn":
            self._onreturn = True
        elif type == "onchange":
            self._onchange= True
        else:
            raise ValueError(f"{type} is not a valid type.")
        
        self.post_update_methods: list = []
        for arg in args:
            if not callable(arg):
                raise ValueError("args must be callable.")
            self.post_update_methods.append(arg)
        
    def set_value(self, new_value: float):
        if self._max is not None:
            if new_value >= self._max:
                new_value = self._max
        if self._min is not None:
            if new_value <= self._min:
                new_value = self._min
        self._value = new_value
        if self.post_update_methods:
            for method in self.post_update_methods:
                method()

    def randomise_value(self, type = "uniform"):
        if type == "uniform":
            self.set_value(random.uniform(self._min, self._max))
        elif type == "gauss":
            self.set_value(random.gauss(self._mid, self._mid/2))
        else:
            raise ValueError("Type not defined")
        self.widget.set_value(self._value)
            
    def add_controller_to_menu(self, menu: pygame_menu.Menu, randomiser = False):
        self.widget = None
        if self._min is not None and self._max is not None:
            self.widget = menu.add.range_slider(self._name, default=self._value, range_values=(self._min, self._max), increment=self.increment)
        else:
            self.widget = menu.add.text_input(self._name + ": ", input_type=pygame_menu.pygame_menu.locals.INPUT_INT)

        if self._onreturn:
            self.widget.set_onreturn(self.set_value)
        elif self._onchange:
            self.widget.set_onchange(self.set_value)

        if randomiser:
            randomiser_buttom = menu.add.button("Randomise", self.randomise_value)
            height = max(self.widget.get_height(), randomiser_buttom.get_height()) + 10 # TODO fix the usage of +10 (throws error)
            frame = menu.add.frame_h(menu.get_width(inner=True), height)
            frame.pack(self.widget, align=pygame_menu.pygame_menu.locals.ALIGN_LEFT)
            frame.pack(randomiser_buttom, align=pygame_menu.pygame_menu.locals.ALIGN_RIGHT)