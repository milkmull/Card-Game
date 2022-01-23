import os

import save

from spritesheet_base import Base_Sheet


from constants import *
from ui import Image_Manager
from custom_card_base import Card
import pygame as pg

def init():
    globals()['SAVE'] = save.get_save()
    globals()['SPRITESHEET'] = Spritesheet()

def get_sheet():
    return globals().get('SPRITESHEET')
    
def load_sounds():
    sounds = {}
    files = os.listdir('snd/cards')
    
    for f in files:
        name = f[:-4]
        
        try:
            sounds[name] = pg.mixer.Sound(f'snd/cards/{f}')
        except pg.error:
            continue
        
    return sounds
    
class Spritesheet:
    def __init__(self):
        self.spritesheet = Base_Sheet(NAMES, 'img/spritesheet.png')
        self.customsheet = Base_Sheet(SAVE.get_custom_names(), 'img/customsheet.png')
        self.extras = {'back': pg.image.load('img/back.png').convert()}
        self.sounds = load_sounds()
        
    def check_name(self, name):
        return self.spritesheet.check_name(name) or self.customsheet.check_name(name) or name in self.extras

    def add_extra(self, info):
        image = Card.build_card(info)
        self.extras[info['name']] = image
        return image
        
    def remove_extra(self, name):
        if name in self.extras:
            del self.extras[name]
            
    def get_image(self, name, scale=(0, 0), olcolor=None):
        scale = tuple(int(s) for s in scale)
        
        img = self.spritesheet.get_image(name)
        if not img:
            img = self.customsheet.get_image(name)
            if not img:
                if name in self.extras:
                    img = self.extras[name]
                else:
                    img = self.add_extra({'name': name, 'description': 'extra'})     
            
        if any(scale):
            img = pg.transform.smoothscale(img, scale)
        elif olcolor is not None:
            img = Image_Manager.rect_outline(img, color=olcolor)

        return img
        
    def get_sound(self, name):
        return self.sounds.get(name)

        