from ui import *
from constants import *
from particles import *
from builder import build_card
import pygame as pg

class Card(Mover):
    def __init__(self, p=(width // 2, height // 2)):
        self.image = build_card('test', 'test', 'test')
        self.rect = self.image.get_rect()
        
        self.rect.center = p
        
        super().__init__()
        
    def events(self, input):
        pass
        
    def update(self):
        self.move()
        
    def draw(self, win):
        win.blit(pg.transform.scale(self.image, self.get_scale()), self.rect)

class Playground:
    def __init__(self, win):
        self.window = win
        self.frame = pg.Surface((width, height)).convert()
        
        self.clock = pg.time.Clock()
        
        self.elements = []
        self.effects = []
        self.input = []
        
        self.set_frame()
        
        self.running = True
        
    def set_frame(self):
        pass

    def run(self):
        while self.running:
            
            self.clock.tick(fps)
            
            self.events()
            self.update()
            self.draw()

    def events(self):
        self.input = pg.event.get()
        p = pg.mouse.get_pos()
        
        for e in self.input:
            
            if e.type == pg.QUIT:
                
                self.running = False
                
            elif e.type == pg.KEYDOWN:
                
                if e.key == pg.K_ESCAPE:
                    
                    self.running = False
                    
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                e = SquareRipple((5, 5), (255, 0, 0))
                e.rect.center = p
                self.effects.append(e)
                
            elif e.type == pg.MOUSEBUTTONUP:
                
                pass
                    
        for e in self.elements:
            
            e.events(self.input)
            
    def update(self):
        for e in self.elements:
            e.update()
            
        for e in self.effects.copy():
            e.update()
            if e.is_finished():
                self.effects.remove(e)
            
    def draw(self):
        self.frame.fill((0, 0, 0))
        
        for e in self.elements:
            e.draw(self.frame)
            
        for e in self.effects:
            e.draw(self.frame)
            
        self.window.blit(self.frame, (0, 0))
        
        pg.display.flip()

if __name__ == '__main__':
    
    pg.init()
    win = pg.display.set_mode((width, height))
    p = Playground(win)
    p.run()
    pg.quit()
    
    
    
    
    