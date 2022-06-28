import pygame as pg

from .base import Base_Object

class Timer(Base_Object):
    def __init__(self, start_time, *base_args, reset_timer=False, **base_kwargs):
        self.start_time = start_time
        self.timer = start_time
        self.reset_timer = reset_timer
        super().__init__(*base_args, **base_kwargs)
        
    @property
    def time(self):
        return self.timer
        
    def reset(self):
        self.timer = self.start_time
        
    def update(self):
        if self.timer:
            self.timer -= 1
            if not self.timer:
                self.run_func()
                if self.reset_timer:
                    self.reset()

class On_Click(Base_Object):
    def __init__(self, func, *base_args, button=1, **base_kwargs):
        super().__init__(*base_args, func=func, **base_kwargs)
        self.button = button
        
    def events(self, events):
        e = events.get('mbd')
        if e:
            if e.button == self.button:
                self.run_func()
                
    def update(self):
        pass
        
class Draw_Lines(Base_Object):
    def __init__(self, points, color=(0, 0, 0), width=3):
        super().__init__()
        
        self.points = points
        self.color = color
        self.width = width
        
    def set_color(self, color):
        self.color = color
        
    def set_points(self, points):
        self.points = points
    
    def draw(self, surf):
        pg.draw.lines(surf, self.color, False, self.points, width=self.width)
        
class Button_Timer(Base_Object):
    def __init__(self, button, start_time, new_message):
        super().__init__()
        
        self.button = button
        self.textbox = button.object
        self.new_message = new_message
        self.original_message = self.textbox.get_message()
        self.start_time = start_time
        self.timer = 0

    def update(self):
        if self.button.get_state():
            self.textbox.set_message(self.new_message)
            self.timer = self.start_time
        if self.timer:
            self.timer -= 1
            if self.timer == 0:
                self.textbox.set_message(self.original_message)
