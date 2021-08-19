import random
import pygame as pg

def get_particles(num, type, color, rect=None, pos=None):
    particles = []
    
    for _ in range(num):
    
        p = {'type': type, 'c': color}
        
        if rect is not None:
            p['p'] = [random.randrange(rect.left, rect.right), random.randrange(rect.top, rect.bottom)]
        elif pos is not None:
            p['p'] = [pos[0], pos[1]]

        if type == 0:
            p['v'] = [random.randrange(-5, 5), random.randrange(-5, 5)]
            p['a'] = 0.5
            p['t'] = random.randrange(1, 50)
            p['r'] = random.randrange(1, 3)
            
        elif type == 1:
            p['v'] = -2
            p['r'] = random.randrange(1, 10)
            
        particles.append(p)
    
    return particles

def update_particles(particles):
    for p in particles.copy():
        
        type = p['type']
        
        if type == 0:

            p['v'][1] += p['a']
            
            p['p'][0] += p['v'][0]
            p['p'][1] += p['v'][1]
            
            p['t'] -= 1
            if p['t'] <= 0:
                particles.remove(p)
        
        elif type == 1:
            
            p['p'][1] += p['v']
            
            p['r'] -= 1
            if p['r'] <= 0:
                particles.remove(p)
                
def draw_particles(win, particles):
    for p in particles:
        
        pg.draw.circle(win, p['c'], p['p'], p['r'])
        
class Wipe:
    def __init__(self, size, color, pos=(0, 0), dir='x', speed=5):
        self.size = size
        self.color = color
        self.dir = dir
        self.speed = speed
        
        self.target = pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.rect = pg.Rect(0, 0, 0, 0)
        
        if self.dir == 'x':
            self.rect.height = self.target.height
        elif self.dir == 'y':
            self.rect.width = self.target.width
        self.rect.center = self.target.center
        
        self.phase = 0
        
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(self.color)
        
        self.finished = False
        
    def is_finished(self):
        return self.finished
        
    def update(self):
        if not self.finished:
            
            print(True)
        
            self.target.center = self.rect.center
            
            if self.phase == 0:
                
                if self.dir == 'x':
                    
                    if self.rect.width < self.target.width: 
                        self.rect.width += self.speed
                    else:
                        self.phase = 1
                        
                elif self.dir == 'y':
                    
                    if self.rect.height < self.target.height: 
                        self.rect.height += self.speed
                    else:
                        self.phase = 1
                        
            if self.phase == 1:
                
                if self.dir == 'x':
                    
                    if self.rect.width > 0: 
                        self.rect.width -= self.speed
                    else:
                        self.finished = True
                        
                elif self.dir == 'y':
                    
                    if self.rect.height > 0: 
                        self.rect.height -= self.speed
                    else:
                        self.finished = True
                        
            self.image = pg.transform.scale(self.image, self.rect.size)
            self.image.fill(self.color)
            self.rect.center = self.target.center
                    
    def draw(self, win):
        if not self.finished:
            win.blit(self.image, self.rect)
                
class SquareRipple:
    def __init__(self, size, color, pos=(0, 0), speed=5, timer=20, ripples=3, thickness=2, grad=False):
        self.color = color
        self.pos = pos
        
        self.speed = speed
        self.timer = timer
        self.ripples = ripples
        self.thickness = thickness
        
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.ratio = size[0] / size[1]
        
        self.ripples = [self.rect.copy()]
        
        self.finished = False
        
    def is_finished(self):
        return self.finished
        
    def update(self):
        for r in self.ripples:
            r.width += 5
            r.height += 5 * self.ratio
            r.center = self.rect.center

        if self.timer == 0:
            self.finished = True
        else:
            self.timer -= 1
            
    def draw(self, win):
        for r in self.ripples:
            pg.draw.line(win, self.color, r.topleft, r.bottomleft, self.thickness)
            pg.draw.line(win, self.color, r.topleft, r.topright, self.thickness)
            pg.draw.line(win, self.color, r.bottomleft, r.bottomright, self.thickness)
            pg.draw.line(win, self.color, r.topright, r.bottomright, self.thickness)
            
    
        




