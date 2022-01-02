import os
from constants import *
from ui import rect_outline
from custom_card_base import Card
import pygame as pg

def init():
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
        self.names = NAMES
        self.sheet = pg.image.load('img/spritesheet.png').convert()
        self.extras = {'back': pg.image.load('img/back.png').convert()}
        self.sounds = load_sounds()
        
    def add_extra(self, name):
        self.extras[name] = create_text(name)
        
    def check_name(self, name):
        return any(n == name for n in self.names)

    def add_player_card(self, info, color):
        name = info['name']
        description = info['description']
        tags = info['tags']
        image = info['image']

        img = Card.build_card(name, description, tags, color=color, image=image)
        self.extras[name] = img
        
    def remove_player_card(self, name):
        if name in self.extras:
            del self.extras[name]
 
    def get_image_by_name(self, name):
        i = self.names.index(name)
        x, y = ((i % 9) * 375, (i // 9) * 525)
        
        img = pg.Surface((375, 525)).convert()
        img.blit(self.sheet, (0, 0), (x, y, 375, 525))

        return img

    def get_image(self, name, color=(255, 255, 255), scale=(cw, ch), olcolor=None):
        scale = [int(s) for s in scale]
        
        if not self.check_name(name):
            
            if name in self.extras:
                img = self.extras[name]
            else:
                img = Card.build_card(name, '', ['extra'], color=color)
                self.extras[name] = img
                
        else:
            
            img = self.get_image_by_name(name)
            
        img = pg.transform.smoothscale(img, scale)
        
        if scale == [cw, ch] and olcolor is not None:
            img = rect_outline(img, color=olcolor)

        return img
        
    def get_sound(self, name):
        return self.sounds.get(name)

        