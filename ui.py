import pygame as pg
from pygame.math import Vector2 as vec
import pygame.freetype
import sys
from tkinter import Tk

def init():
    win = pg.display.get_surface()
    WIDTH, HEIGHT = win.get_size()

    globals()['WIDTH'] = WIDTH
    globals()['HEIGHT'] = HEIGHT
    
#menu stuff---------------------------------------------

def exit():
    pg.quit()
    sys.exit()

def new_screen(text, wait=0):
    win = pg.display.get_surface()
    win.fill((0, 0, 0))

    for t in text:
        win.blit(t.get_image(), t.rect)
        
    pg.display.update()
    
    if wait:
        pg.time.wait(wait)
        
def new_message(message, wait=0):
    win = pg.display.get_surface()
    
    win.fill((0, 0, 0))
    m = Textbox(message, 20)
    m.rect.center = (WIDTH / 2, HEIGHT / 2)
        
    win.blit(m.get_image(), m.rect)
    pg.display.update()
    
    if wait:
        pg.time.wait(wait)
        
    pg.event.clear()

def center_buttons_y(btns):
    h = max(b.rect.bottom for b in btns) - min(b.rect.top for b in btns)
    r = pg.Rect(0, 0, 2, h)
    r.centery = HEIGHT // 2

    dy = r.y - min(b.rect.top for b in btns)
    
    for b in btns:
        b.rect = b.rect.move(0, dy)
        
def center_buttons_x(btns):
    w = max(b.rect.right for b in btns) - min(b.rect.left for b in btns)
    r = pg.Rect(0, 0, w, 2)
    r.centerx = WIDTH // 2

    dx = r.x - min(b.rect.left for b in btns)
    
    for b in btns: 
        b.rect = b.rect.move(dx, 0)
        
    return r

def notice(message, color1=(100, 100, 100), color2=(50, 50, 50), bcolor=(0, 200, 0), olcolor=(255, 255, 255)):
    screen = []
    
    body = pg.Rect(0, 0, 300, 150)
    upper = pg.Rect(0, 0, 300, 100)
    lower = pg.Rect(0, 100, 300, 50)
    text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
    outline = pg.Rect(0, 0, body.width + 10, body.height + 10)
    
    s = pg.Surface(outline.size).convert()
    pg.draw.rect(s, olcolor, outline, border_radius=10)
    body.center = outline.center
    pg.draw.rect(s, color1, body, border_radius=10)
    lower.bottomleft = body.bottomleft
    pg.draw.rect(s, color2, lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
    i = Image(s)
    i.rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.append(i)
    
    body.center = (WIDTH // 2, HEIGHT // 2)
    upper.topleft = body.topleft
    text_rect.center = upper.center
    lower.bottomleft = body.bottomleft
    
    t = Textbox(message, olcolor=(0, 0, 0))
    t.fit_text(text_rect, tsize=25)
    t.rect.center = text_rect.center
    screen.append(t)
    
    b = Button((200, 30), 'ok', color2=bcolor, tag='break')
    b.rect.center = lower.center
    screen.append(b)

    return screen

def yes_no(message, color1=(100, 100, 100), color2=(50, 50, 50), olcolor=(255, 255, 255)):
    screen = []
    
    body = pg.Rect(0, 0, 300, 150)
    upper = pg.Rect(0, 0, 300, 100)
    lower = pg.Rect(0, 100, 300, 50)
    text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
    outline = pg.Rect(0, 0, body.width + 10, body.height + 10)
    
    s = pg.Surface(outline.size).convert()
    pg.draw.rect(s, olcolor, outline, border_radius=10)
    body.center = outline.center
    pg.draw.rect(s, color1, body, border_radius=10)
    lower.bottomleft = body.bottomleft
    pg.draw.rect(s, color2, lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
    i = Image(s)
    i.rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.append(i)
    
    body.center = (WIDTH // 2, HEIGHT // 2)
    upper.topleft = body.topleft
    text_rect.center = upper.center
    lower.bottomleft = body.bottomleft
    
    t = Textbox(message, olcolor=(0, 0, 0))
    t.fit_text(text_rect, tsize=25)
    t.rect.center = text_rect.center
    screen.append(t)
    
    b = Button((120, 30), 'yes', color2=(0, 200, 0), func=lambda : True, tag='return')
    b.rect.midleft = lower.midleft
    b.rect.x += 20
    screen.append(b)
    
    b = Button((120, 30), 'no', color2=(200, 0, 0), func=lambda : False, tag='return')
    b.rect.midright = lower.midright
    b.rect.x -= 20
    screen.append(b)

    return screen
    
def loading_screen(message='loading...', color1=(100, 100, 100), color2=(50, 50, 50), olcolor=(255, 255, 255)):
    screen = []
    
    body = pg.Rect(0, 0, 300, 150)
    upper = pg.Rect(0, 0, 300, 100)
    lower = pg.Rect(0, 100, 300, 50)
    text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
    outline = pg.Rect(0, 0, body.width + 10, body.height + 10)
    
    s = pg.Surface(outline.size).convert()
    pg.draw.rect(s, olcolor, outline, border_radius=10)
    body.center = outline.center
    pg.draw.rect(s, color1, body, border_radius=10)
    lower.bottomleft = body.bottomleft
    pg.draw.rect(s, color2, lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
    i = Image(s)
    i.rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.append(i)
    
    body.center = (WIDTH // 2, HEIGHT // 2)
    upper.topleft = body.topleft
    text_rect.center = upper.center
    lower.bottomleft = body.bottomleft
    
    t = Textbox(message, olcolor=(0, 0, 0))
    t.fit_text(text_rect, tsize=25)
    t.rect.center = text_rect.center
    screen.append(t)
    
    li = LoadingIcon()
    li.rect.topright = body.topright
    li.rect.top += 5
    li.rect.right -= 5
    screen.append(li)

    return screen

#menu mechanics------------------------------------------------------------------------

def mini_loop(elements, input=[]):
    win = pg.display.get_surface()

    for e in elements:

        is_button = isinstance(e, Button)
    
        if hasattr(e, 'events'):
            e.events(input)
                
        if isinstance(e, Button):
            if e.get_state():
                break
                
    for e in elements:
            
        if hasattr(e, 'update'):
            e.update()
            
    win.fill((0, 0, 0))
            
    for e in elements:
        
        if hasattr(e, 'draw'):
            e.draw(win)

    pg.display.flip()
    
def check_break(elements):
    for e in elements:
        
        if isinstance(e, Button):
            
            if e.get_tag() == 'break':
                
                if e.get_state():
                    
                    return True
                
    return False

def get_return(elements):
    for e in elements:
        if isinstance(e, Button): 
            if e.get_tag() == 'return':
                r = e.get_return()
                if r is not None:
                    return r

def check_refresh(elements, set_screen, args, kwargs):
    for e in elements:
    
        if isinstance(e, Button):
            
            if e.get_tag() == 'refresh':
                
                if e.get_state():

                    return (set_screen(*args, **kwargs), True)
                
    return (elements, False)

def menu(set_screen, args=[], kwargs={}, overlay=False, func=None, fargs=[], fkwargs={}):
    win = pg.display.get_surface()
    clock = pg.time.Clock()
    
    elements = set_screen(*args, **kwargs)
    skip = False
    input = []
    
    def exit():
        pg.quit()
        sys.exit()
    
    if overlay:
        s = pg.Surface(win.get_size()).convert_alpha()
        s.fill((0, 0, 0, 180))
        win.blit(s, (0, 0))
        pg.display.flip()
    
    while True:
        clock.tick(30)
        p = pg.mouse.get_pos()
        
        input = pg.event.get()
        
        for e in input:     
            if e.type == pg.QUIT:
                exit() 
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    exit()
                    
        for e in elements:
            
            is_button = isinstance(e, Button)
            if is_button:
                if e.get_state():
                    e.reset()
                    
            if hasattr(e, 'events'):
                e.events(input)
                
            if is_button:
                if e.get_state():
                    break
                    
        elements, skip = check_refresh(elements, set_screen, args, kwargs)
        
        if not skip:
            if check_break(elements):
                break
            skip = False

        r = get_return(elements)
        if r is not None:
            return r
                    
        for e in elements:
            if hasattr(e, 'update'):
                e.update()
                
        win.fill((0, 0, 0))
                
        for e in elements:
            if hasattr(e, 'draw'):
                e.draw(win)
                
        if func:
            exit = func(*fargs, **fkwargs)
            if exit:
                break
                
        if overlay:
            pg.display.update([e.rect for e in elements])
        else:
            pg.display.flip()


def transition(e1, e2):
    s1 = pg.Surface((WIDTH, HEIGHT)).convert()
    r1 = s1.get_rect()
    for e in e1:
        e.draw(s1)
        
    s2 = pg.Surface((WIDTH, HEIGHT)).convert()
    r2 = s2.get_rect()
    for e in e1:
        e.draw(s1)
        
    r2.rect.topleft = r1.rect.topright
    
    win = pg.display.get_surface()
    clock = pg.time.Clock()
    
    while True:
        clock.tick(30)
        
        r1.x -= 5
        r2.x -= 5
        
        win.blit(s1, r1)
        win.blit(s2, r2)
        
        if r2.x <= 0:
            r2.x = 0
            break

#clipboard stuff----------------------------------------

def copy_to_clipboard(text):
    Tk().clipboard_append(text)
    
def get_clip():
    try:
        text = Tk().clipboard_get()    
    except:
        text = ''
        
    return text
    
#drawing stuff------------------------------------------------------------

def rect_outline(img, color=(0, 0, 0), ol_size=2):
    ol = img.copy()
    ol.fill(color)

    w, h = img.get_size()
    img = pg.transform.smoothscale(img, (w - (ol_size * 2), h - (ol_size * 2)))
    ol.blit(img, (ol_size, ol_size))
    
    return ol
    
#other--------------------------------------------------------------------

def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

def intersect(a, b, c, d):
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)
    
#-------------------------------------------------------------------------

class Mover:
    def __init__(self):
        self.target = None
        self.last_pos = None
        
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel = vec(0, 0)
        self.scale_acc = vec(0, 0)
        
        self.timer1 = 0
        self.timer2 = 0

        self.moving = False
        self.scaling = False
        
        self.sequence = []
        self.cache = {'v': 5, 'timer1': 0, 'timer2': 0, 'scale': False}
        
    def finished(self):
        return self.timer2 == 0 and not (self.moving or self.scaling)
        
    def set_target(self, target, p=None, v=5, timer1=0, timer2=0, scale=False):
        self.target = target
        
        if p is not None:
            self.rect.center = p
            
        p0 = vec(self.rect.centerx, self.rect.centery)
        p1 = vec(target.centerx, target.centery)
        
        length = (p1 - p0).length()
        
        if length == 0:
            vel = vec(0, 0)
        else:
            vel = (p1 - p0).normalize() * v

        self.vel = vel
        self.pos = p0
        self.moving = True
        
        if scale:
        
            frames = length / v
            
            s1 = vec(target.width, target.height)
            s0 = vec(self.rect.width, self.rect.height)
            
            scale_vel = (s1 - s0) / frames
        
            self.scale_vel = scale_vel
            self.scaling = True

        self.timer1 = timer1
        self.timer2 = timer2
        
        self.cache['v'] = v
        self.cache['timer1'] = timer1
        self.cache['timer2'] = timer2
        self.cache['scale'] = scale
        
        self.last_pos = self.target.center
        
    def cancel(self):
        self.stop_move()
        self.stop_scale()
        
        self.timer1 = 0
        self.timer2 = 0
        
    def set_sequence(self, sequence, start=False):
        self.sequence = sequence
        
        if start:
            self.next_sequence()
        
    def next_sequence(self):
        info = self.sequence.pop(0)
        self.set_target(info['target'], p=info.get('p'), v=info.get('v', 5), timer1=info.get('timer1', 0), timer2=info.get('timer2', 0), scale=info.get('scale', False))

    def move(self):
        if not self.finished():
        
            p = self.target.center
            if self.last_pos != p:
                self.set_target(self.target, v=self.cache['v'], timer1=self.cache['timer1'], timer2=self.cache['timer2'], scale=self.cache['scale'])
            self.last_pos = p
            
        if self.timer1 > 0:
            self.timer1 -= 1

        elif self.moving or self.scaling:
            
            if self.moving:
            
                self.pos += self.vel  
                self.rect.center = (self.pos.x, self.pos.y)
                
                if self.done_moving():
                    self.stop_move()
 
            if self.scaling:
            
                self.scale += self.scale_vel
                self.rect.size = self.get_scale()
                self.rect.center = (self.pos.x, self.pos.y)

                if self.done_scaling():
                    self.stop_scale()
                
        else:
            
            if self.timer2 > 0:
                self.timer2 -= 1
                
        if self.finished() and self.sequence:
            self.next_sequence()
            
    def done_scaling(self):
        w_done = False
        h_done = False
        
        if self.scale_vel.x > 0:
            if self.rect.width >= self.target.width:
                w_done = True
        elif self.scale_vel.x < 0:
            if self.rect.width <= self.target.width:
                w_done = True
        else:
            w_done = True
            
        if self.scale_vel.y > 0:
            if self.rect.height >= self.target.height:
                h_done = True
        elif self.scale_vel.y < 0:
            if self.rect.height <= self.target.height:
                h_done = True
        else:
            h_done = True
            
        return w_done and h_done
        
    def done_moving(self):
        x_done = False
        y_done = False
        
        if self.vel.x > 0:
            if self.rect.centerx >= self.target.centerx:
                x_done = True
        elif self.vel.x < 0:
            if self.rect.centerx <= self.target.centerx:
                x_done = True
        else:
            x_done = True
            
        if self.vel.y > 0:
            if self.rect.centery >= self.target.centery:
                y_done = True
        elif self.vel.y < 0:
            if self.rect.centery <= self.target.centery:
                y_done = True
        else:
            y_done = True
            
        return x_done and y_done
            
    def stop_move(self):
        self.rect.center = self.target.center
        self.vel *= 0
        self.moving = False
        
    def stop_scale(self):
        c = self.rect.center
        self.rect.size = self.target.size
        self.rect.center = c
        if not self.moving:
            self.rect.center = self.target.center
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel *= 0
        self.scaling = False

    def reset_timer(self):
        self.timer2 = self.cache['timer2']
        
    def get_scale(self):
        w = max(int(self.scale.x), 0)
        h = max(int(self.scale.y), 0)
        return (w, h)

class Image:
    def __init__(self, image, bgcolor=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.bgcolor = bgcolor
        
    def set_background(self, color):
        self.bgcolor = color
        
    def clear_background(self):
        self.bgcolor = None
        
    def draw(self, win):
        if self.bgcolor is not None:
            pg.draw.rect(win, self.bgcolor, self.rect)
        win.blit(self.image, self.rect)
        
class Draw_Lines:
    def __init__(self, points, color=(0, 0, 0), width=3):
        self.points = points
        self.color = color
        self.width = width
        
    def set_color(self, color):
        self.color = color
        
    def set_points(self, points):
        self.points = points
        
    def draw(self, win):
        pg.draw.lines(win, self.color, False, self.points, width=self.width)

class FreeImage:
    def __init__(self, image, bound=None):
        self.image = image
        self.original = self.image.copy()
        self.rect = self.image.get_rect()
 
        self.bound = bound
        
        self.last_pos = pg.mouse.get_pos()
        self.held = False
        
        self.rects = {}
        self.set_rects()
        
    def set_rects(self):
        r = pg.Rect(0, 0, 15, 15)
        r.center = self.rect.topleft
        self.rects['tl'] = r
        
        r = pg.Rect(0, 0, 15, 15)
        r.center = self.rect.bottomleft
        self.rects['bl'] = r
        
        r = pg.Rect(0, 0, 15, 15)
        r.center = self.rect.topright
        self.rects['tr'] = r
        
        r = pg.Rect(0, 0, 15, 15)
        r.center = self.rect.bottomright
        self.rects['br'] = r
        
    def adjust_rects(self):
        self.rects['tl'].center = self.rect.topleft
        self.rects['bl'].center = self.rect.bottomleft
        self.rects['tr'].center = self.rect.topright
        self.rects['br'].center = self.rect.bottomright
        
    def move(self):
        if self.held:
        
            x0, y0 = self.last_pos
            x1, y1 = pg.mouse.get_pos()
            
            dx = x1 - x0
            dy = y1 - y0
            
            self.rect = self.rect.move(dx, dy)
            self.last_pos = (x1, y1)
            
        self.adjust_rects()
            
    def zoom_in(self):
        c = self.rect.center
        self.image = pg.transform.scale(self.image, (round(self.rect.width * 1.25), round(self.rect.height * 1.25)))
        self.rect = self.image.get_rect()
        self.rect.center = c
        
    def zoom_out(self):
        c = self.rect.center
        self.image = pg.transform.scale(self.image, (round(self.rect.width // 1.25), round(self.rect.height // 1.25)))
        self.rect = self.image.get_rect()
        self.rect.center = c
        
    def collision(self):
        if self.bound:
            
            if self.rect.right > self.bound.right:
                self.rect.right = self.bound.right
            elif self.rect.left < self.bound.left:
                self.rect.left = self.bound.left
                
            if self.rect.bottom > self.bound.bottom:
                self.rect.bottom = self.bound.bottom
            elif self.rect.top < self.bound.top:
                self.rect.top = self.bound.top
        
    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input:
            
            if e.type == pg.MOUSEBUTTONDOWN:
                
                if self.rect.collidepoint(p):
                
                    if e.button == 1:

                        self.held = True
                        self.last_pos = p
                            
                    elif e.button == 4:
                        
                        self.zoom_in()
                        
                    elif e.button == 5:
                        
                        self.zoom_out()
                
            elif e.type == pg.MOUSEBUTTONUP:
                
                if e.button == 1:
                
                    self.held = False
                
    def update(self):
        self.move()

        self.collision()
        
    def draw(self, win):
        win.blit(self.image, self.rect)
        
        p = pg.mouse.get_pos()
        
        for r in self.rects.values():
            
            if r.collidepoint(p):
                
                pg.draw.rect(win, (255, 0, 0), r)

class DraggerManager:
    def __init__(self, draggers):
        self.draggers = draggers
        self.held_list = []
        self.ctrl = False
        
        self.rs = Rect_Selector(self.draggers)
        
        self.log_queue = []
        
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
        self.log_queue.append(log)
        
    def get_logs(self):
        logs = self.log_queue.copy()
        self.log_queue.clear()
        return logs
        
    def get_next_log(self):
        if self.log_queue:
            return self.log_queue.pop(-1)

    def events(self, input):
        self.rs.events(input)
        
        p = pg.mouse.get_pos()
        
        click_down = False
        click_up = False
        a = False
        
        for e in input:
            
            if e.type == pg.MOUSEBUTTONDOWN:
                click_down = True    
            elif e.type == pg.MOUSEBUTTONUP:
                click_up = True
                
            elif e.type == pg.KEYDOWN:
                if (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    self.ctrl = True
                elif e.key == pg.K_a:
                    a = True
            elif e.type == pg.KEYUP:
                if (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    self.ctrl = False
                    
        if self.ctrl and a:
            self.select_all()
        elif click_up:
            selected = self.rs.get_selected()
            self.extend_held_list(selected)
             
        hit_any = False
        
        carried = {}
             
        for d in self.draggers:
            if not getattr(d, 'visible', True):
                continue
            hit = d.rect.collidepoint(p)
            d._hover = hit
            if click_down:
                if hit:
                    self.update_held_list(d)
                elif not self.ctrl:
                    if d not in self.held_list:
                        d._selected = False
                        d.drop()
            elif click_up:
                dist = d.get_carry_dist()
                if dist:
                    carried[d] = dist
                d.drop()
                
            if hit:
                hit_any = True
                
        if carried:
            self.add_carry_log(carried)
                
        if click_down and hit_any:
            self.rs.cancel()
                
        if click_down:
            if not hit_any:
                self.reset_held_list()
            elif not self.ctrl:
                self.start_held_list()
                
    def update(self):
        self.rs.update()
        
    def draw(self, win):
        self.rs.draw(win)

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

    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input:
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.anchor = p
                break
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.update_selected()
                    self.anchor = None
                break
                
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
                
    def draw(self, win):
        if self.anchor:
            points = (self.rect.topleft, self.rect.bottomleft, self.rect.bottomright, self.rect.topright)
            pg.draw.lines(win, self.color, True, points, self.rad)

class Textbox(Mover):
    def __init__(self, message, tsize=10, anchor='center', font='arial.ttf', fgcolor=(255, 255, 255), bgcolor=None, olcolor=None, olrad=2):
        self.message = message
        self.original_message = message
        
        self.tsize = tsize
        self._font = font
        self.font = pg.freetype.Font(font, tsize)
        setattr(self.font, 'pad', True)
        
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.olcolor = olcolor
        self.olrad = olrad
        self.olcache = {}
        
        self.image, self.rect = self.render(self.message, get_rect=True)
        self.anchor = anchor
        
        self.characters = []
        
        self.timer = 0
        
        super().__init__()
        
    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message
        
    def __eq__(self, other):
        return self.message == other.message and self.fgcolor == other.fgcolor
        
    def set_message(self, message):
        self.message = message
        
    def set_antialiased(self, antialiased):
        setattr(self.font, 'antialiased', antialiased)
        
    def set_kerning(self, kerning):
        setattr(self.font, 'kerning', kerning)
        
    def set_underline(self, underline):
        setattr(self.font, 'underline', underline)
        
    def set_strong(self, strong):
        setattr(self.font, 'strong', strong)
        
    def set_oblique(self, oblique):
        setattr(self.font, 'oblique', oblique)
        
    def set_wide(self, wide):
        setattr(self.font, 'wide', wide)
        
    def set_fgcolor(self, fgcolor):
        self.fgcolor = fgcolor
        
    def set_bgcolor(self, bgcolor):
        self.bgcolor = bgcolor
        
    def set_olcolor(self, olcolor, r=None):
        self.olcolor = olcolor
        if r is not None:
            self.olrad = r
        
    def set_font_size(self, tsize):
        self.font.size = tsize
        self.tsize = tsize
        
    def set_font(self, font, tsize=None):
        if tsize is not None:
            self.tsize = tsize
        self._font = font
        self.font = pg.freetype.Font(font, self.tsize)
        setattr(self.font, 'pad', True)
        
    def set_anchor(self, anchor):
        self.anchor = anchor
        
    def set_message_timer(self, message, timer):
        self.update_message(message)
        self.timer = timer
        
    def get_message(self):
        return self.message

    def get_text_rect(self, text):
        return self.font.get_rect(text)
        
    def get_image(self):
        return self.image
        
    def get_characters(self):
        return self.characters
        
    def reset(self):
        self.update_message(self.original_message)
        
    def update_image(self):
        self.update_text(self.get_message())
        
    def add_outline(self, message, image):
        r = self.olrad
        if r in self.olcache:
            points = self.olcache[r]     
        else:
            x, y, e = r, 0, 1 - r
            points = []

            while x >= y:
            
                points.append((x, y))
                y += 1
                if e < 0:
                    e += 2 * y - 1 
                else:
                    x -= 1
                    e += 2 * (y - x) - 1
                    
            points += [(y, x) for x, y in points if x > y]
            points += [(-x, y) for x, y in points if x]
            points += [(x, -y) for x, y in points if y]
            points.sort() 
            self.olcache[r] = points
            
        w, h = image.get_size()
        w = w + 2 * r
        
        osurf = pg.Surface((w, h + 2 * r)).convert_alpha()
        osurf.fill((0, 0, 0, 0))
        surf = osurf.copy()
        outline = self.simple_render(message, fgcolor=self.olcolor)
        osurf.blit(outline, (0, 0))
        
        for dx, dy in points:
            surf.blit(osurf, (dx + r, dy + r))
            
        surf.blit(image, (r, r))
        image = surf
        
        return image
        
    def simple_render(self, message, fgcolor=None, bgcolor=None, tsize=0, get_rect=False):
        if fgcolor is None:
            fgcolor = self.fgcolor
            
        image, rect = self.font.render(message, fgcolor=fgcolor, bgcolor=bgcolor, size=tsize)
            
        if get_rect:
            return (image, rect)
        else:
            return image
        
    def render(self, message, get_rect=False, track_chars=False):
        image, rect = self.font.render(message, fgcolor=self.fgcolor)
        
        if self.olcolor is not None:
            image = self.add_outline(message, image)
            rect = image.get_rect()
            
        if self.bgcolor is not None:
            scaled = pg.Rect(0, 0, rect.width, rect.height)
            bg = pg.Surface(scaled.size).convert()
            bg.fill(self.bgcolor)
            bg.blit(image, (0, 0))
            image = bg
            
        if track_chars:
            characters = []
            x = 0 if self.olcolor is None else self.olrad
            for char in message + ' ':
                r = self.get_text_rect(char)
                characters.append((char, r, (x, 0)))
                x += r.width
            self.characters = characters
            
        if get_rect:
            return (image, rect)
        else:
            return image
           
    def render_multicolor(self, colors):
        chars = []
        message = self.get_message()
        
        width = 0
        j = 0
        
        for i in range(len(message)):
            
            char = message[i]
            color = colors[j % len(colors)]
            self.set_fgcolor(color)
            
            img, r = self.render(char, get_rect=True)
            chars.append((img, r))
            
            width += r.width
            
            if not char.isspace():
                j += 1
            
        height = r.height
        
        image = pg.Surface((width, height)).convert_alpha()
        x = 0
        y = 0
            
        for char, r in chars:
            r.topleft = (x, y)
            image.blit(char, r)
            
            x += r.width
            
        self.new_image(image)
           
    def fit_text(self, bounding_rect, tsize=None, centered=True, new_message=None):
        if new_message is not None:
            self.message = new_message
        message = self.message
        
        if tsize is None:
            tsize = bounding_rect.height
        elif tsize > bounding_rect.height:
            tsize = bounding_rect.height
        self.set_font_size(tsize)
        
        words = [word.split(' ') for word in message.splitlines()]
        characters = []
        
        image = pg.Surface(bounding_rect.size).convert_alpha()
        image.fill((0, 0, 0, 0))

        while True:

            space = self.get_text_rect(' ').width
            if self.olcolor is not None:
                space -= self.olrad * 2
            max_width, max_height = bounding_rect.size
            x, y = (0, 0)
            
            over_y = False
            rendered_lines = []
            current_line = []
            
            for line in words:
        
                for word in line:
                
                    word_surface, word_rect = self.render(word, get_rect=True)
                    w, h = word_rect.size
                    
                    if y + h > max_height:
                        over_y = True
                        break
                    
                    if x + w >= max_width:
                        x = 0
                        y += h
                        if y + h > max_height or x + w >= max_width:
                            over_y = True
                            break
                        else:
                            rendered_lines.append(current_line.copy())
                            current_line.clear()

                    word_rect.topleft = (x, y)
                    current_line.append([word, word_surface, word_rect])
                    x += w + space
                    
                if over_y and tsize > 1:
                    self.set_font_size(tsize - 1)
                    tsize = self.tsize
                    break
                    
                x = 0
                y += h
                
            if not over_y:
                rendered_lines.append(current_line)
                break
                
        if centered and rendered_lines[0]:
                
            max_y = rendered_lines[-1][0][2].bottom
            min_y = rendered_lines[0][0][2].top

            h = max_y - min_y
            r = pg.Rect(0, 0, 2, h)
            r.centery = bounding_rect.height // 2

            dy = max(r.y - min_y, 0)
            
            for line in rendered_lines: 
                for info in line:
                    info[2].move_ip(0, dy)
      
        for line in rendered_lines:
        
            if centered and line:
                
                max_x = max(r.right for _, _, r in line)
                min_x = min(r.left for _, _, r in line)
            
                w = max_x - min_x
                r = pg.Rect(0, 0, w, 2)
                r.centerx = bounding_rect.width // 2

                dx = r.x - min_x
                
                for info in line: 
                    info[2].move_ip(dx, 0)

            for word, surf, r in line:
                image.blit(surf, r)
                
                x, y = r.topleft
                w, h = r.size
                for char in word:
                    r = self.get_text_rect(char)
                    r.topleft = (x, y)
                    characters.append((char, r, (r.x, r.y)))
                    x += r.width
                    
                if r is not line[-1][2]:
                    r = self.get_text_rect(' ')
                    r.topleft = (x, y)
                    characters.append((' ', r, (r.x, r.y)))

        self.characters = characters
        
        self.new_image(image, rect=bounding_rect.copy())
           
    def new_image(self, image, rect=None):
        if rect is None:
            rect = image.get_rect()

        a = getattr(self.rect, self.anchor, self.rect.topleft)
        self.image = image
        self.rect = rect
        setattr(self.rect, self.anchor, a)
        
        self.move_characters()
        
    def update_message(self, message):
        self.message = message
        image, rect = self.render(self.message, get_rect=True, track_chars=True)
        self.new_image(image, rect=rect)
        
    def clear(self):
        self.update_message('')
        
    def move_characters(self):
        rect = self.rect

        for char, r, rel in self.characters:
            rx, ry = rel
            r.topleft = (self.rect.x + rx, self.rect.y + ry)
        
    def events(self, input):
        pass
        
    def update(self):
        self.move_characters()
        self.move()
        
        if self.timer != 0:
            self.timer -= 1
            if self.timer == 0:
                self.clear()
    
    def draw(self, win):
        win.blit(self.get_image(), self.rect)

class Button:
    def __init__(self, size, message, color1=(0, 0, 0), color2=(100, 100, 100), tcolor=(255, 255, 255), border_radius=10, tag='', func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.rect = pg.Rect(0, 0, size[0], size[1])
        r = self.rect.copy()
        r.width -= 5
        r.height -= 5
        self.text_rect = r
        self.textbox = Textbox(message, tsize=r.height, fgcolor=tcolor)
        self.textbox.fit_text(r)
        
        self.max_timer = 0
        self.timer = 0
        self.tmessage = ''

        self.color1 = color1
        self.color2 = color2
        self.current_color = color1
        self.border_radius = border_radius
        
        self.tag = tag
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.return_val = None
        
        self.active = False
        self.pressed = False
        
        self.disabled = False
        
        self.visible = True
        
    def set_timer_rule(self, timer, message):
        self.max_timer = timer
        self.tmessage = message
        
    def set_tag(self, tag):
        self.tag = tag
        
    def get_tag(self):
        return self.tag
        
    def get_state(self):
        return self.pressed
        
    def disable(self):
        self.disabled = True
        self.state = 0
        self.current_color = self.color1
        
    def enable(self):
        self.disabled = False
        
    def get_return(self, reset=True):
        r = self.return_val
        if reset:
            self.return_val = None
        return r
        
    def set_func(self, func, args=None, kwargs=None):
        self.func = func
        if args is not None:
            self.args = args
        if kwargs is not None:
            self.kwargs = kwargs
        
    def set_args(self, args=None, kwargs=None):
        if args is not None:
            self.args = args
        if kwargs is not None:
            self.kwargs = kwargs
        
    def clear_args(self):
        self.args.clear()
        self.kwargs.clear()
        
    def set_visible(self, visible):
        self.visible = visible
        
    def reset(self):
        self.pressed = False
        
    def events(self, input):
        if self.visible:
        
            p = pg.mouse.get_pos()

            if self.rect.collidepoint(p):
                self.active = True  
            else:  
                self.active = False
                
            if not self.disabled:
                
                for e in input:
                    
                    if e.type == pg.MOUSEBUTTONDOWN:
                        if e.button == 1:
                            if self.active:
                                
                                self.pressed = True
                                self.return_val = self.func(*self.args, **self.kwargs)
                                
                                if self.max_timer:
                                    self.update_message(self.tmessage)
                                    self.timer = self.max_timer
                                
                    elif e.type == pg.MOUSEBUTTONUP:
                        if e.button == 1:
                            self.pressed = False
            
    def update(self):
        self.textbox.rect.center = self.rect.center
        self.textbox.rect.y -= 1
        
        if self.visible:
        
            self.textbox.update()
            
            if not self.disabled:
            
                if self.active and self.current_color != self.color2:
                    self.current_color = self.color2       
                elif not self.active and self.current_color != self.color1:
                    self.current_color = self.color1   
                
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.update_message(self.textbox.original_message)
  
    def draw(self, win):
        if self.visible:
            pg.draw.rect(win, self.current_color, self.rect, border_radius=self.border_radius)
            self.textbox.draw(win)
        
    def get_message(self):
        return self.textbox.get_message()
        
    def update_message(self, message, tcolor=None):    
        self.textbox.update_message(message)
        if tcolor is not None:
            self.textbox.set_fgcolor(tcolor)
            
        self.textbox.fit_text(self.text_rect)

class Input:
    def __init__(self, size, message='type here', tsize=30, color=(0, 0, 0, 0), tcolor=(255, 255, 255), length=99, check=lambda char: True, fitted=False, scroll=False):
        self.image = pg.Surface(size).convert_alpha()
        self.color = color
        self.image.fill(color)
        
        self.rect = pg.Rect(0, 0, 0, 0)
        self.rect.size = size
        
        self.tsize = tsize
        
        self.active = False
        
        self.index = 0
        
        self.btimer = 0
        self.backspace = False
        self.bhold = False
        
        self.selecting = False
        self.selection = []
        
        self.copy = [0, 0]
        self.cut = [0, 0]
        self.paste = [0, 0]
        self.all = [0, 0]
        
        self.length = length
        self.check = check
        
        self.timer = 0
        
        self.fitted = fitted
        self.scroll = scroll
        
        self.last_message = message
        self.logs = []
        
        self.textbox = Textbox(message, tsize=tsize, fgcolor=tcolor, anchor='topleft')
        self.update_message(self.textbox.get_message())
        
    def set_index(self, index):
        index = max(index, 0)
        index = min(index, len(self.textbox.get_message()))
        
        self.index = index
        
    def check_index(self):
        self.index = max(self.index, 0)
        self.index = min(self.index, len(self.textbox.get_message()))
        
    def get_chars(self):
        return self.textbox.characters
        
    def copy_to_clipboard(self, text):
        Tk().clipboard_append(text.strip())
  
    def get_clip(self):
        try:
            text = Tk().clipboard_get().strip()  
        except:
            text = ''
            
        return text
        
    def get_selection(self):
        if self.selection:
            i, j = self.selection
            return self.textbox.get_message()[min(i, j):max(i, j)]
        return ''
        
    def get_selected_chars(self):
        chars = self.get_chars()
        i, j = self.selection
        return chars[min(i, j):max(i, j)]
        
    def get_message(self):
        return self.textbox.get_message()
        
    def update_message(self, message):
        if self.check_message(message):
            if self.fitted:
                self.textbox.set_message(message)
                self.textbox.fit_text(self.rect, tsize=self.tsize)
            else:
                self.textbox.update_message(message)
        
    def close(self):
        if self.active:
            self.active = False
            m = self.textbox.get_message()
            if not m.strip():
                self.textbox.reset()
                m = self.textbox.get_message()
            if self.last_message != m:
                self.logs.append({'t': 'val', 'i': self, 'm': (self.last_message, m)})
                self.last_message = m
            self.selection.clear()
        
    def get_logs(self):
        return_logs = self.logs.copy()
        self.logs.clear()
        return return_logs
        
    def check_message(self, text):
        passed = False
        if text is not None:
            if (all(31 < ord(char) < 127 for char in text) and self.check(text)):# or (self.fitted and text == '\n'):
                if 0 <= len(text) <= self.length:
                      passed = True
        return passed
        
    def highlight_word(self):
        i = self.index
        j = self.index 
        
        m = self.textbox.get_message()
        
        if i not in range(len(m)):
            return
        
        istop = False
        jstop = False

        while not (istop and jstop):

            if not istop:
                if i == 0:
                    istop = True
                elif m[i] == ' ':
                    i += 1
                    istop = True
                else:
                    i -= 1

            if not jstop:
                if j == len(m) or m[j] == ' ':
                    jstop = True
                else:
                    j += 1

        self.selection = [i, j]
        self.set_index(j)
        
    def highlight_full(self):
        m = self.textbox.get_message()
        self.selection = [0, len(m)]
        self.set_index(len(m))
           
    def send_keys(self, text):
        m = self.textbox.get_message()
        message = m[:self.index] + text + m[self.index:]
        self.update_message(message)
        self.set_index(self.index + len(text))
                    
    def replace_selection(self, text):
        m = self.textbox.get_message()
        i, j = self.selection
        message = m[:min(i, j)] + text + m[max(i, j):] 
        self.update_message(message)
        self.set_index(min(i, j))
        self.selection.clear()
            
    def back(self):
        if self.btimer <= 0:
            
            if self.selection:
                self.replace_selection('')
            else:
                m = self.textbox.get_message()
                message = m[:max(self.index - 1, 0)] + m[self.index:]
                self.update_message(message)
                self.set_index(self.index - 1)
            
            if not self.bhold:
                self.btimer = 15
                self.bhold = True
            else:
                self.btimer = 2
                
    def delete(self):
        if self.selection:
            self.replace_selection('')
        else:
            m = self.textbox.get_message()
            message = m[:self.index] + m[min(self.index + 1, len(m)):]
            self.update_message(message)
            self.set_index(self.index - 1)
        
    def shift_textbox(self):
        if self.textbox.rect.width < self.rect.width:
            self.textbox.rect.midleft = self.rect.midleft
        else:
            chars = self.get_chars()
            if self.index in range(len(chars)):
                r = chars[self.index][1]
                dx = r.x - self.textbox.rect.x
                self.textbox.rect.midleft = self.rect.midleft
                if dx > self.rect.width:
                    self.textbox.rect.x = (self.textbox.rect.x - dx) + self.rect.width 
        
    def events(self, input):
        click = False
        p = pg.mouse.get_pos()

        for e in input:
        
            if e.type == pg.MOUSEBUTTONDOWN:
                
                if e.button == 1:
                
                    click = True
                    
                    if self.rect.collidepoint(p) or self.textbox.rect.collidepoint(p):

                        if self.timer <= 25:
                        
                            if not self.active:
                                self.active = True
                                self.set_index(len(self.textbox.get_message()))                       
                            else:
                                self.selecting = True
                                for i, info in enumerate(self.get_chars()):
                                    if info[1].collidepoint(p):
                                        if p[0] - info[1].centerx >= 0:
                                            i += 1
                                        self.set_index(i)
                                        break
                                        
                            self.selection.clear()
                          
                        elif self.selection:
                            self.highlight_full()
                        else:
                            self.highlight_word()
                            
                        self.timer = 34

                    else:
                        self.close()
                    
            elif e.type == pg.MOUSEBUTTONUP:
                self.selecting = False
                if self.selection:
                    if self.selection[0] == self.selection[1]:
                        self.selection.clear()
                    
            elif self.active:

                if e.type == pg.KEYDOWN:
                    
                    if e.key == pg.K_BACKSPACE:
                        self.backspace = True
                        
                    elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                        self.copy[0] = 1
                        self.cut[0] = 1
                        self.paste[0] = 1
                        self.all[0] = 1
                    elif e.key == pg.K_c:
                        self.copy[1] = 1
                    elif e.key == pg.K_x:
                        self.cut[1] = 1
                    elif e.key == pg.K_v: 
                        self.paste[1] = 1
                    elif e.key == pg.K_a:
                        self.all[1] = 1
                        
                    elif e.key == pg.K_DELETE:
                        self.delete()
                        
                    elif e.key == pg.K_SPACE:
                        self.send_keys(' ')
                        
                    elif e.key == pg.K_RIGHT:
                        if self.selection:
                            self.set_index(max(self.selection))
                        else:
                            self.set_index(self.index + 1)
                        self.selection.clear()
                        self.timer = 25
                    elif e.key == pg.K_LEFT:
                        if self.selection:
                            self.set_index(min(self.selection))
                        else:
                            self.set_index(self.index - 1)
                        self.selection.clear()
                        self.timer = 25
                        
                    elif e.key == pg.K_RETURN:
                        self.close()
                    
                    if hasattr(e, 'unicode') and not self.copy[0]:
                        if self.selection:
                            self.replace_selection('')
                        char = e.unicode.strip()
                        if char:
                            self.send_keys(char)
                            
                elif e.type == pg.KEYUP:
                    
                    if e.key == pg.K_BACKSPACE:
                        
                        self.backspace = False
                        self.bhold = False
                        self.btimer = 0
                    
                    elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                        self.copy[0] = 0
                        self.cut[0] = 0
                        self.paste[0] = 0 
                        self.all[0] = 0
                    elif e.key == pg.K_c:
                        self.copy[1] = 0
                    elif e.key == pg.K_x:
                        self.cut[1] = 0
                    elif e.key == pg.K_v: 
                        self.paste[1] = 0
                    elif e.key == pg.K_a:
                        self.all[1] = 0
                        
        if all(self.copy):
            text = self.get_selection()
            self.copy_to_clipboard(text)
            self.copy = [0, 0]
            
        elif all(self.cut):
            if self.selection:
                text = self.get_selection()
                self.copy_to_clipboard(text)
                self.replace_selection('')
                self.cut = [0, 0]
                        
        elif all(self.paste):
            text = self.get_clip()
            if self.selection:
                self.replace_selection(text)
            else:
                self.send_keys(text)
            self.paste = [0, 0]
            
        elif all(self.all):
            self.highlight_full()
            self.all = [0, 0]
            
        elif self.backspace:
            self.back()
       
        if self.selecting:
            
            if click:
                self.selection = [self.index, self.index]   
            else:
                chars = self.get_chars()
                for i in range(len(chars)):
                    r = chars[i][1]
                    if r.collidepoint(p):
                        if p[0] - r.centerx >= 0:
                            i += 1
                        if i not in self.selection:
                            self.selection[1] = i
                            break

            self.set_index(self.selection[1])

    def update(self):
        self.timer -= 1
        self.btimer -= 1
        
        if self.timer == -25:
            self.timer *= -1

        if not self.fitted:
            if self.scroll:
                self.shift_textbox()
            else:
                self.textbox.rect.topleft = self.rect.topleft
        else:
            self.textbox.rect.center = self.rect.center
            self.textbox.rect.y += 1
                
        self.textbox.update()
        
    def draw(self, win):
        win.blit(self.image, self.rect)
        
        if self.selection:
            chars = self.get_chars()
            i, j = self.selection
            for _, r, _ in chars[min(i, j):max(i, j)]:
                pg.draw.rect(win, (0, 102, 255), r)

        self.textbox.draw(win)
        
        if self.active and self.timer > 0:
            chars = self.get_chars()
            if chars:
                if self.index in range(len(chars)):
                    r = chars[self.index][1]
                    pg.draw.line(win, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
            else:
                r = self.textbox.get_text_rect(' ')
                if self.fitted:
                    r.center = self.rect.center
                    pg.draw.line(win, self.textbox.fgcolor, r.midtop, r.midbottom, width=2)
                else:
                    r.midleft = self.rect.midleft
                    pg.draw.line(win, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)

class Counter:
    def __init__(self, options, option=None, tsize=30, tag=''):
        self.options = options
        self.index = 0

        self.textbox = Textbox(f' {self.get_current_option()} ', tsize=tsize)
        
        self.upbutton = Button((tsize, tsize), '>', func=self.incriment_up, border_radius=100)
        self.downbutton = Button((tsize, tsize), '<', func=self.incriment_down, border_radius=100)

        w = self.textbox.rect.width + self.upbutton.rect.width + self.downbutton.rect.width
        h = self.textbox.rect.height
        
        self.rect = pg.Rect(0, 0, w, h)
        
        if option:
            self.set_option(option)
            
        self.tag = tag
        
        self.disabled = False
        
        self.update()
        
    def disable(self):
        self.disabled = True
        
    def enable(self):
        self.disabled = False
        
    def get_tag(self):
        return self.tag
        
    def get_current_option(self):
        return self.options[self.index]
        
    def update_message(self):
        r = self.textbox.rect
        self.textbox.update_message(f' {self.get_current_option()} ')
        self.textbox.fit_text(r)
        
    def set_option(self, option):
        if option in self.options:
            
            self.index = self.options.index(option)
            self.update_message()
            
    def set_index(self, index):
        self.index = index % len(self.options)
        self.update_message()
        
    def incriment_up(self):
        self.index = (self.index + 1) % len(self.options)
        self.update_message()
        
    def incriment_down(self):
        self.index = (self.index - 1) % len(self.options)
        self.update_message()
        
    def events(self, input):
        if not self.disabled:
            self.upbutton.events(input)
            self.downbutton.events(input)
        
    def update(self):
        self.downbutton.rect.topleft = self.rect.topleft
        self.textbox.rect.midleft = self.downbutton.rect.midright
        self.upbutton.rect.midleft = self.textbox.rect.midright
        
        if not self.disabled:
            self.upbutton.update()
            self.downbutton.update()
        
    def draw(self, win):
        self.textbox.draw(win)
        
        if not self.disabled:
            self.upbutton.draw(win)
            self.downbutton.draw(win)
               
class Hole:
    def __init__(self, rad, color=(255, 255, 255)):
        self.radius = rad
        
        self.color = color
        self.rect = pg.Rect(0, 0, self.radius * 2, self.radius * 2)
        
        self.status = False
        
    def get_status(self):
        return self.status
        
    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input:
            
            if e.type == pg.MOUSEBUTTONDOWN:
                
                if self.rect.collidepoint(p):
                    
                    self.status = not self.status
                    
                    break
                    
    def update(self):
        pass
        
    def draw(self, win):
        pg.draw.circle(win, self.color, self.rect.center, self.radius)
        
        if self.status:
        
            pg.draw.circle(win, (0, 0, 0), self.rect.center, self.radius // 2)
 
class Pane:
    def __init__(self, size, label='', label_space=0, color=(0, 0, 0, 0), tsize=25, tcolor=(255, 255, 255), ul=False, live=False):
        self.size = size
        
        self.image = pg.Surface(self.size).convert_alpha()
        self.color = color
        self.image.fill(self.color)

        self.message = label
        self.label = Textbox(self.message, tsize=tsize, fgcolor=tcolor)
        self.label.set_underline(ul)
        self.label_space = label_space
        self.label.fit_text(pg.Rect(0, 0, self.size[0], tsize))
        self.tab = self.label.rect
        
        self.rect = self.image.get_rect()
        
        self.ctimer = 0
        
        self.scroll_buttons = (Button((self.rect.width, 20), '^', color1=(0, 0, 0), color2=(0, 0, 0),
                                       func=self.scroll, args=['u'], border_radius=0), 
                               Button((self.rect.width, 20), 'v', color1=(0, 0, 0), color2=(0, 0, 0),
                                       func=self.scroll, args=['d'], border_radius=0))

        self.objects = []
        
        self.live = live
        
        self.orientation_cache = {'xpad': 5, 'ypad': 5, 'dir': 'y', 'pack': False}
        self.rel_pos = {}
        
    def set_live(self, live):
        self.live = live
                
    def is_same(self, objects):
        if len(objects) == len(self.objects):
            return all(objects[i] == self.objects[i] for i in range(len(objects)))
        else:
            return False
            
    def sort_objects(self, key):
        objects = sorted(self.objects, key=key)
        self.join_objects(objects, **self.orientation_cache)
  
    def join_objects(self, objects, xpad=5, ypad=5, dir='y', pack=False, force=False, scroll=False, move=False, key=None):
        if key is None:
            same = self.is_same(objects)
        else:
            same = key(objects, self.objects)

        if not same or force:
            self.rel_pos.clear()
            
            x = 0
            y = 0
            
            if dir == 'y':
                
                for o in objects:
                    
                    if pack:
                        if self.rect.y + y + ypad + o.rect.height > self.rect.bottom:
                            x += o.rect.width + xpad
                            y = 0  
                        o.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)       
                    else:
                        o.rect.midtop = (self.rect.centerx, self.rect.y + y + ypad)  
                    self.rel_pos[id(o)] = [o.rect.x - self.rect.x, o.rect.y - self.rect.y]

                    y += o.rect.height + ypad
                    
            elif dir == 'x':
                
                for o in objects:

                    if pack:
                        if self.rect.x + x + xpad + o.rect.width > self.rect.right:
                            x = 0
                            y += o.rect.height + ypad  
                        o.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)   
                    else:
                        o.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)  
                    self.rel_pos[id(o)] = [o.rect.x - self.rect.x, o.rect.y - self.rect.y]
                        
                    x += o.rect.width + xpad
                    
            self.objects = objects.copy()
            self.orientation_cache = {'xpad': xpad, 'ypad': ypad, 'dir': dir, 'pack': pack}
            self.redraw()
            
            if scroll:
                self.go_to_bottom()
                
        elif same and move:
            for i in range(len(self.objects)):
                objects[i].rect = self.objects[i].rect.copy()
            
    def add_object(self, object, xpad=None, ypad=None, dir=None, pack=None):
        if xpad is None:
            xpad = self.orientation_cache['xpad']
        if ypad is None:
            ypad = self.orientation_cache['ypad'] 
        if dir is None:
            dir = self.orientation_cache['dir']
        if pack is None:
            pack = self.orientation_cache['pack']
            
        objects = self.objects + [object]
        self.join_objects(objects, xpad=xpad, ypad=ypad, dir=dir, pack=pack)
        
    def clear(self):
        self.join_objects([])
            
    def get_visible(self):
        return [o for o in self.objects if self.rect.contains(o.rect)]
        
    def can_scroll_up(self):
        return any(o.rect.top < self.rect.top for o in self.objects)
        
    def go_to_top(self):
        while self.can_scroll_up(): 
            self.scroll('u')
        
    def can_scroll_down(self):
        return any(o.rect.bottom > self.rect.bottom for o in self.objects)
        
    def go_to_bottom(self):
        while self.can_scroll_down():
            self.scroll('d')
        
    def scroll(self, dir):
        if self.objects:
  
            if dir == 'd' and self.can_scroll_down():
                for o in self.objects: 
                    o.rect.y -= 25  
                    self.rel_pos[id(o)][1] -= 25
                self.redraw()

            elif dir == 'u' and self.can_scroll_up():
                for o in self.objects:
                    o.rect.y += 25
                    self.rel_pos[id(o)][1] += 25
                self.redraw()
                
    def redraw(self):
        if self.color:
            self.image.fill(self.color)
            
        for o in self.objects:
            dx = o.rect.x - self.rect.x
            dy = o.rect.y - self.rect.y

            tl = o.rect.topleft 
            o.rect.topleft = (dx, dy)
            if hasattr(o, 'update'):
                o.update()
            o.draw(self.image)
            o.rect.topleft = tl
        
    def sort(self, key):
        self.objects.sort(key=key)
        self.redraw()
        
    def get_cropped_x(self):
        return [o for o in self.objects if o.rect.right > self.rect.right or o.rect.left < self.rect.left]
        
    def get_cropped_y(self):
        return [o for o in self.objects if o.rect.bottom > self.rect.bottom or o.rect.top < self.rect.top]
        
    def events(self, input):
        p = pg.mouse.get_pos()
        
        for b in self.scroll_buttons:
            b.events(input)
            
        for e in input:
            if e.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(p):
                    if e.button == 4 and self.can_scroll_up():
                        self.scroll('u')
                    elif e.button == 5 and self.can_scroll_down():
                        self.scroll('d')
                    
            break
            
        if self.live:
            for e in self.objects:
                if hasattr(e, 'set_visible'):
                    if self.rect.contains(e.rect):
                        e.set_visible(True)
                    else:
                        e.set_visible(False)
                        
    def update(self):
        self.scroll_buttons[0].rect.midtop = self.rect.midtop
        self.scroll_buttons[1].rect.midbottom = self.rect.midbottom
        self.label.rect.midbottom = self.rect.midtop
        self.label.rect.y -= self.label_space
        
        for b in self.scroll_buttons:
            b.update()
            
        if self.live:
            for o in self.objects:
                rx, ry = self.rel_pos[id(o)]
                sx, sy = self.rect.topleft
                o.rect.x = sx + rx
                o.rect.y = sy + ry
        
    def draw(self, win):
        if not self.live:
            if self.color != (0, 0, 0, 0) or self.objects:
                win.blit(self.image, self.rect)
            
        self.label.draw(win)
        
        if self.can_scroll_up():
            self.scroll_buttons[0].draw(win)
        if self.can_scroll_down():
            self.scroll_buttons[1].draw(win)
 
class Context_Manager:
    def __init__(self, buttons, bgcolor=(255, 255, 255), width=100):
        self.buttons = buttons  
        height = sum(b.rect.height for b in self.buttons) + 10
        self.rect = pg.Rect(0, 0, width, height)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill((0, 0, 0))
        pg.draw.rect(self.image, bgcolor, self.rect, border_radius=5)
        self.image.set_colorkey((0, 0, 0))
        
        self.visible = False
        
    def open(self):
        p = pg.mouse.get_pos()
        px, py = p
        
        if py - self.rect.height > 0:
            self.rect.bottomleft = (px + 5, py - 5)
        else:
            self.rect.topleft = (px + 5, py + 5)
        self.move()
        self.visible = True
        
    def close(self):
        self.visible = False
        
    def is_open(self):
        return self.visible
        
    def set_args(self, args=[], kwargs={}):
        for b in self.buttons:
            b.set_args(args=args, kwargs=kwargs)
        
    def move(self):
        x, y = self.rect.topleft
        x += 5
        y += 5
        for b in self.buttons:
            b.rect.topleft = (x, y)
            y += b.rect.height
            
    def get_button_by_label(self, label):
        for b in self.buttons:
            if b.label == label:
                return b
        
    def events(self, input):
        if self.visible:
            for b in self.buttons:
                b.events(input)
                
        for e in input:
            if e.type == pg.MOUSEBUTTONDOWN:
                self.close()
                break
            
    def update(self):
        if self.visible:
            for b in self.buttons:
                b.update()
        
    def draw(self, win):
        if self.visible:
            win.blit(self.image, self.rect)
            for b in self.buttons:
                b.draw(win)

class Popup(Pane):
    def __init__(self, size, slide_dir='u', label='', color=(0, 0, 0, 0), tsize=15, tcolor=(255, 255, 255)):
        super().__init__(size, label=label, color=color, tsize=tsize, tcolor=tcolor)
        
        self.slide_dir = slide_dir
        self.target = self.rect.copy()

        self.timer = 0
        
        self.click_timer = 0
        self.locked = False
        
    def set_pos(self):
        if self.slide_dir == 'u':
            
            self.target.midbottom = self.rect.midtop
            self.tab.midbottom = self.rect.midtop
            
        elif self.slide_dir == 'd':
            
            self.target.midtop = self.rect.midbottom
            self.tab.midtop = self.rect.midbottom
            
        elif self.slide_dir == 'l':
            
            self.target.midright = self.rect.midleft
            self.tab.midright = self.rect.midleft
            
        elif self.slide_dir == 'r':
            
            self.target.midleft = self.rect.midright
            self.tab.midleft = self.rect.midright
        
    def adjust_pos(self, dx, dy):
        if dx or dy:

            self.tab.x += dx
            self.tab.y += dy
            
            for o in self.objects:
                
                o.rect.x += dx
                o.rect.y += dy
        
    def open(self):
        x1, y1 = self.rect.topleft
        
        if self.slide_dir == 'u':
            
            self.rect.y -= 20
            
            if self.rect.y < self.target.y:
                
                self.rect.y = self.target.y
          
        elif self.slide_dir == 'd':
            
            self.rect.y += 20
            
            if self.rect.y > self.target.y:
                
                self.rect.y = self.target.y
                
        elif self.slide_dir == 'l':
            
            self.rect.x -= 20
            
            if self.rect.x < self.target.x:
                
                self.rect.x = self.target.x
                
        elif self.slide_dir == 'r':
            
            self.rect.x += 20
            
            if self.rect.x > self.target.x:
                
                self.rect.x = self.target.x

        dx = self.rect.x - x1
        dy = self.rect.y - y1
        self.adjust_pos(dx, dy)
      
    def close(self):
        x1, y1 = self.rect.topleft
        
        if self.slide_dir == 'u':
            
            self.rect.y += 20
            
            if self.rect.y > self.target.bottom:
                
                self.rect.y = self.target.bottom
          
        elif self.slide_dir == 'd':
            
            self.rect.y -= 20
            
            if self.rect.bottom < self.target.y:
                
                self.rect.bottom = self.target.y
                
        elif self.slide_dir == 'l':
            
            self.rect.x += 20
            
            if self.rect.x > self.target.right:
                
                self.rect.x = self.target.right
                
        elif self.slide_dir == 'r':
            
            self.rect.x -= 20
            
            if self.rect.right < self.target.x:
                
                self.rect.right = self.target.x

        dx = self.rect.x - x1
        dy = self.rect.y - y1
        self.adjust_pos(dx, dy)
      
    def is_closed(self):
        return not self.rect.colliderect(self.target)
        
    def is_open(self):
        return self.rect.colliderect(self.target)
      
    def auto_open(self, time=50):
        self.timer = time
      
    def events(self, input):
        super().events(input)
        
        p = pg.mouse.get_pos()
        
        for e in input: 
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.tab.collidepoint(p) or self.rect.collidepoint(p):
                        if self.click_timer > 20:
                            self.click_timer = 0
                        else:
                            self.locked = not self.locked       
                break

        if self.tab.collidepoint(p) or self.rect.collidepoint(p) or self.timer > 0 or self.locked:
            self.open() 
        else:
            self.close()
            
    def update(self):
        super().update()

        if self.timer > 0:
            self.timer -= 1
        if self.click_timer < 40:
            self.click_timer += 1

class Slider:
    def __init__(self, ran, size, bcolor=(255, 255, 255), hcolor=(0, 0, 0), func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.range = ran
        
        self.size = size
        
        self.rect = pg.Rect(0, 0, self.size[0], self.size[1])
        
        self.held = False
        self.flipped = False
        
        self.bcolor = bcolor
        self.hcolor = hcolor
        
        self.value = 0
        
        if self.rect.width > self.rect.height: 
            self.orientation = 'x'
            self.handel = pg.Rect(0, 0, 10, self.rect.height + 10)
        elif self.rect.width < self.rect.height:
            self.orientation = 'y'
            self.handel = pg.Rect(0, 0, self.rect.width + 10, 10)
            
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.return_val = None
       
    def collision(self):
        if self.orientation == 'x':
        
            if self.handel.centerx > self.rect.right:
                self.handel.centerx = self.rect.right
            elif self.handel.centerx < self.rect.left:
                self.handel.centerx = self.rect.left
            self.handel.centery = self.rect.centery
            
        elif self.orientation == 'y':
            
            if self.handel.centery > self.rect.bottom:
                self.handel.centery = self.rect.bottom
            elif self.handel.centery < self.rect.top:
                self.handel.centery = self.rect.top
            self.handel.centerx = self.rect.centerx
            
    def get_state(self):
        self.collision()
        
        if self.orientation == 'x':
            dx = self.handel.centerx - self.rect.x
            ratio = dx / self.rect.width 
        elif self.orientation == 'y':
            dy = self.handel.centery - self.rect.y
            ratio = dy / self.rect.height
            
        if self.flipped:
            ratio = 1 - ratio

        full = len(self.range)
        shift = self.range[0]

        state = (full * ratio) + shift

        return round(state)
            
    def set_state(self, value):
        state = round(value)
        
        full = len(self.range)
        shift = self.range[0]
        
        ratio = (state - shift) / full
        
        if self.flipped:
            ratio = 1 - ratio
            
        if self.orientation == 'x':   
            dx = ratio * self.rect.width
            self.handel.centerx = dx + self.rect.x
        elif self.orientation == 'y':
            dy = ratio * self.rect.height
            self.handel.centery = dy + self.rect.y

    def flip(self):
        self.flipped = True

    def get_return(self, reset=True):
        r = self.return_val
        if reset:
            self.return_val = None
        return r
        
    def set_func(self, func, args=None, kwargs=None):
        self.func = func
        if args is not None:
            self.args = args
        if kwargs is not None:
            self.kwargs = kwargs
        
    def set_args(self, args=None, kwargs=None):
        if args is not None:
            self.args = args
        if kwargs is not None:
            self.kwargs = kwargs
        
    def clear_args(self):
        self.args.clear()
        self.kwargs.clear()

    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input:
            
            if e.type == pg.MOUSEBUTTONDOWN:
                if self.handel.collidepoint(p) or self.rect.collidepoint(p):
                    self.held = True
                    
            elif e.type == pg.MOUSEBUTTONUP: 
                self.held = False
                
    def update(self):
        if self.held:
            self.handel.center = pg.mouse.get_pos()
            self.return_val = self.func(*self.args, self.get_state(), **self.kwargs)
            
        self.collision()
            
    def draw(self, win):
        pg.draw.rect(win, self.bcolor, self.rect)
        pg.draw.rect(win, self.hcolor, self.handel)
        
class RGBSlider(Slider):
    def __init__(self, size, rgb, hcolor=None, flipped=True, func=lambda *args, **kwargs: None, args=[], kwargs={}):
        super().__init__(range(255), size, func=func, args=args, kwargs=kwargs)
        
        self.hcolor = hcolor
        
        self.rgb = rgb

        if self.orientation == 'x':
        
            surf = pg.Surface((255, 1)).convert()
            
            if self.rgb == 'r':  
                for x in range(255):    
                    surf.set_at((x, 0), (x, 0, 0))      
            elif self.rgb == 'g':   
                for x in range(255):           
                    surf.set_at((x, 0), (0, x, 0))              
            elif self.rgb == 'b':              
                for x in range(255):                   
                    surf.set_at((x, 0), (0, 0, x))
                    
        elif self.orientation == 'y':
        
            surf = pg.Surface((1, 255)).convert()
            
            if self.rgb == 'r':  
                for y in range(255):    
                    surf.set_at((0, y), (y, 0, 0))      
            elif self.rgb == 'g':   
                for y in range(255):           
                    surf.set_at((0, y), (0, y, 0))              
            elif self.rgb == 'b':              
                for y in range(255):                   
                    surf.set_at((0, y), (0, 0, y))
                    
        self.image = pg.transform.scale(surf, self.size)
        
        if flipped:
            self.flip()
        
    def flip(self):
        super().flip()
        
        if self.orientation == 'x':
            self.image = pg.transform.flip(self.image, True, False) 
        elif self.orientation == 'y':
            self.image = pg.transform.flip(self.image, False, True)
        
    def get_color(self):
        if self.rgb == 'r':
            color = (self.get_state(), 0, 0)
        elif self.rgb == 'g':
            color = (0, self.get_state(), 0)
        elif self.rgb == 'b':
            color = (0, 0, self.get_state())
    
        return color
        
    def update(self):
        super().update()
        
        if self.hcolor is None:
            self.hcolor = self.get_color()
        
    def draw(self, win):
        win.blit(self.image, self.rect)
        pg.draw.rect(win, self.hcolor, self.handel)

class LoadingIcon:
    def __init__(self, rad=50, color=(0, 0, 255)):
        self.rect = pg.Rect(0, 0, rad // 2, rad // 2)
        
        self.rad = rad
        self.color = color
        
        self.angle = 0
        
    def update(self):
        self.angle -= 0.1
        
    def draw(self, win):
        pg.draw.arc(win, self.color, self.rect, self.angle, self.angle + 4.71239, width=4)
    
    
    
    
    
    
    