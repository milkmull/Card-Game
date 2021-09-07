import pygame as pg
import save

def init():
    globals()['CUSTOMSHEET'] = Customsheet()

def get_sheet():
    return globals().get('CUSTOMSHEET')

class Customsheet:
    def __init__(self):
        self.cards = save.get_data('cards').copy()
        self.names = [c['name'] for c in self.cards]
        self.sheet = pg.image.load('img/customsheet.png').convert()
        
    def refresh(self):
        self.__init__()
        
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