import pygame as pg
from ui import *

WIDTH = 1024
HEIGHT = 576

class Game:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        
        self.running = True
        
        self.elements = self.set_screen()
        
    def set_screen(self):
        screen = []
               
        p = Pane((100, 100), color=(100, 100, 100), live=True)
        p.rect.center = (WIDTH // 2, HEIGHT // 2)
        screen.append(p)
        
        ob = [Button((100, 30), message=str(i)) for i in range(100)]
        p.join_objects(ob)
        
        screen += ob
        
        return screen
        
    def run(self):
        while self.running:
            self.clock.tick(30)
            self.events()
            self.update()
            self.draw()
        
    def events(self):
        input = pg.event.get()
        
        for event in input:
            if event.type == pg.QUIT:
                self.running = False
                
        for e in self.elements:
            e.events(input)
                
    def update(self):
        for e in self.elements:
            e.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for e in self.elements:
            e.draw(self.screen)
        pg.display.flip()
        
pg.init()
pg.display.set_mode((WIDTH, HEIGHT))
g = Game()
g.run()
pg.quit()



