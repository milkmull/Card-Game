import pygame as pg

from ui.logging import Logging

class Dragger:
    def __init__(self):
        self._held = False
        self._selected = False
        self._hover = False
        self._stuck = False
        self._rel_pos = [0, 0]
        self._htime = 0
        self._pickup = [0, 0]
        
    def is_held(self):
        return self._held
        
    def set_stuck(self, stuck):
        self._stuck = stuck
        
    def start_held(self):
        if not self._stuck:
            self._held = True
            self._selected = True
            self.set_rel_pos()
            self._pickup = self.rect.center
                
    def drop(self):
        self._held = False
        self._htime = 0
        self._pickup = self.rect.center
        
    def get_carry_dist(self):
        x0, y0 = self._pickup
        x1, y1 = self.rect.center
        dx = x1 - x0
        dy = y1 - y0
        if dx or dy:
            return (dx, dy)
        
    def select(self):
        self._selected = True
        
    def deselect(self):
        self._held = False
        self._selected = False
        self._htime = 0
        
    def set_rel_pos(self):
        p = pg.mouse.get_pos()
        px, py = p
        sx, sy = self.rect.topleft
        
        self._rel_pos[0] = px - sx
        self._rel_pos[1] = py - sy
        
    def update_htime(self):
        if self._held and self._htime < 4:
            self._htime += 1
        return self._htime == 4

    def update(self):        
        dx = 0
        dy = 0

        if self._held and self.update_htime():
            x0, y0 = self.rect.topleft
            px, py = pg.mouse.get_pos()
            rx, ry = self._rel_pos
            self.rect.x = px - rx
            self.rect.y = py - ry
            x1, y1 = self.rect.topleft
            
            dx = x1 - x0
            dy = y1 - y0
            
        return (dx, dy)

class Dragger_Manager(Logging):
    def __init__(self, draggers):
        super().__init__()
        
        self.draggers = draggers
        self.held_list = []
        self.ctrl = False
        
        self.rs = Rect_Selector(self.draggers)
        
    def cancel(self):
        self.rs.cancel()

    def update_held_list(self, d):
        if self.ctrl:
            if d not in self.held_list:
                self.held_list.append(d)
                d.start_held()
            else:
                self.remove_held(d)
        else:
            if d not in self.held_list:
                self.reset_held_list()
                self.held_list.append(d)
                d.start_held()
                
    def extend_held_list(self, selection):
        for d in selection:
            if d not in self.held_list:
                self.held_list.append(d)
                d.start_held()
            
    def start_held_list(self):
        for d in self.held_list:
            d.start_held()
        
    def reset_held_list(self):
        for d in self.held_list:
            d.deselect()
        self.held_list.clear()
            
    def drop_held_list(self):
        for d in self.held_list:
            d.drop()
        
    def remove_held(self, d):
        if d in self.held_list:
            self.held_list.remove(d)
            d.deselect()
            
    def select_all(self):
        self.reset_held_list()
        for d in self.draggers:
            self.held_list.append(d)
            d.select()
            
    def select_rect(self, r):
        for d in self.draggers:
            if d.rect.colliderect(r):
                if d not in self.held_list:
                    self.held_list.append(d)
                    d.select()
                    
    def get_selected(self):
        return self.held_list.copy()

    def add_carry_log(self, carried):
        log = {'t': 'carry', 'draggers': carried}
        self.add_log(log)
            
    def events(self, events, rect=True):
        if rect:
            self.rs.events(events)
        else:
            self.cancel()
        
        p = events.get('p')
        kd = events.get('kd')
        ku = events.get('ku')
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        
        a = False
        hit_any = False
        carried = {}
        
        if not mbd or mbu:
            if kd:
                if (kd.key == pg.K_RCTRL) or (kd.key == pg.K_LCTRL):
                    self.ctrl = True
                elif kd.key == pg.K_a:
                    a = True
            elif ku:
                if (ku.key == pg.K_RCTRL) or (ku.key == pg.K_LCTRL):
                    self.ctrl = False
                    
        if self.ctrl and a:
            self.select_all()
        elif mbu:
            selected = self.rs.get_selected()
            self.extend_held_list(selected)

        for d in self.draggers:
            if not getattr(d, 'visible', True):
                continue
            hit = d.rect.collidepoint(p)
            d._hover = hit
            if mbd:
                if mbd.button == 1:
                    if hit:
                        self.update_held_list(d)
                    elif not self.ctrl:
                        if d not in self.held_list:
                            d._selected = False
                            d.drop()
            elif mbu:
                if mbu.button == 1:
                    dist = d.get_carry_dist()
                    if dist:
                        carried[d] = dist
                    d.drop()
                
            if hit:
                hit_any = True
                
        if carried:
            self.add_carry_log(carried)
                
        if mbd:
            if mbd.button == 1 and hit_any:
                self.rs.cancel()
                
        if mbd:
            if mbd.button == 1:
                if not hit_any:
                    self.reset_held_list()
                elif not self.ctrl:
                    self.start_held_list()
                
    def update(self):
        self.rs.update()
        
    def draw(self, surf):
        self.rs.draw(surf)

class Rect_Selector:
    def __init__(self, selection, color=(255, 0, 0), rad=2):
        self.selection = selection
        self.selected = []
        self.anchor = None
        
        self.color = color
        self.rad = rad
        self.rect = pg.Rect(0, 0, 0, 0)
        
    def cancel(self):
        self.anchor = None
        self.selected.clear()

    def update_selected(self):
        self.selected = [s for s in self.selection if self.rect.colliderect(s.rect)]
        
    def get_selected(self):
        return self.selected.copy()
        
    def events(self, events):
        p = events.get('p')
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        
        if mbd:
            if mbd.button == 1:
                self.anchor = p
        elif mbu:
            if mbu.button == 1:
                self.update_selected()
                self.anchor = None
                
    def update(self):
        if self.anchor:
            mx, my = pg.mouse.get_pos()
            ax, ay = self.anchor
            
            w = mx - ax
            h = my - ay
            
            self.rect.size = (abs(w), abs(h))
            self.rect.topleft = self.anchor
            
            if w < 0:
                self.rect.right = ax
            if h < 0:
                self.rect.bottom = ay
                
    def draw(self, surf):
        if self.anchor:
            points = (self.rect.topleft, self.rect.bottomleft, self.rect.bottomright, self.rect.topright)
            pg.draw.lines(surf, self.color, True, points, self.rad)
