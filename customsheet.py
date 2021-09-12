import os
import pygame as pg
import save
from constants import *

def init():
    if not os.path.exists('img/customsheet.png'):
        create_blank_sheet()
    if not os.path.exists('img/custom/0.png'):
        create_blank_custom()
    globals()['CUSTOMSHEET'] = Customsheet()

def get_sheet():
    return globals().get('CUSTOMSHEET')
    
def create_blank_sheet():
    pg.image.save(pg.Surface((card_width, card_height)).convert(), 'img/customsheet.png')
    
def create_blank_custom():
    if os.path.exists('img/user.png'):
        img = pg.image.load('img/user.png').convert()
    else:
        img = pg.Surface((1, 1)).convert()
        
    img = pg.transform.smoothscale(img, (card_width - 75, 210))
    pg.image.save(img, 'img/custom/0.png')

class Customsheet:
    def __init__(self):
        self.cards = save.get_data('cards').copy()
        self.names = [c['name'] for c in self.cards]
        self.sheet = pg.image.load('img/customsheet.png').convert()
        
    def refresh(self):
        self.__init__()
        
    def reset(self):
        self.refresh()
        pg.image.save(self.get_image('Player 0'), 'img/customsheet.png')
        self.refresh()
        
    def get_id(self, name):
        if name in self.names:
            return self.names.index(name)
        
    def get_image(self, name, size=None):
        i = self.names.index(name)
        x, y = ((i % 9) * 375, (i // 9) * 525)
        
        img = pg.Surface((375, 525)).convert()
        img.blit(self.sheet, (0, 0), (x, y, 375, 525))
        
        if size:
            img = pg.transform.smoothscale(img, size)
        
        return img
        
    def new_id(self):
        return len(self.cards)