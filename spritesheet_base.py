import pygame as pg

from save import CONSTANTS

CARD_WIDTH, CARD_HEIGHT = CONSTANTS['card_size']
    
class Sheet_Manager:
    CACHE = {}
    
    @classmethod
    def get_sheet(cls, path):
        if path not in cls.CACHE:
            try:
                cls.CACHE[path] = pg.image.load(path).convert()
            except:
                cls.CACHE[path] = None
        return cls.CACHE[path]
        
    @classmethod
    def reload_sheet(cls, path):
        cls.CACHE[path] = pg.image.load(path).convert()
        
class Base_Sheet:
    def __init__(self, names, path):
        self.names = names
        self.path = path
        Sheet_Manager.get_sheet(path)
        
    def failed_to_load(self):
        return not self.sheet
        
    @property
    def sheet(self):
        return Sheet_Manager.get_sheet(self.path)
        
    def refresh_sheet(self):
        Sheet_Manager.reload_sheet(self.path)
        
    def resave_sheet(self, surf):
        pg.image.save(surf, self.path)
        self.refresh_sheet()
        
    def check_name(self, name):
        return name in self.names
        
    def get_image(self, name, size=None):
        if not self.check_name(name):
            return
            
        i = self.names.index(name)
        x, y = ((i % 9) * CARD_WIDTH, (i // 9) * CARD_HEIGHT)
        
        img = pg.Surface((CARD_WIDTH, CARD_HEIGHT)).convert()
        img.blit(self.sheet, (0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT))
        if size:
            img = pg.transform.smoothscale(img, size)
        
        return img
    
    