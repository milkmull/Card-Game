import pygame as pg

from .base import Compound_Object

class Loading_Icon(Compound_Object):
    DA = 4.71239
    def __init__(self, rad=50, color=(0, 0, 255)):
        super().__init__()
        self.rect = pg.Rect(0, 0, rad // 2, rad // 2)
        
        self.rad = rad
        self.color = color
        
        self.angle = 0
        
    def update(self):
        self.angle -= 0.1
        super().update()
        
    def draw(self, surf):
        pg.draw.arc(surf, self.color, self.rect, self.angle, self.angle + Loading_Icon.DA, width=4)
 