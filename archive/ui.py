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
    
def get_events():
    events = {}
    
    events['p'] = pg.mouse.get_pos()
    
    for e in pg.event.get():
        if e.type == pg.QUIT:
            events['q'] = e
        elif e.type == pg.MOUSEBUTTONDOWN:
            events['mbd'] = e
        elif e.type == pg.MOUSEBUTTONUP:
            events['mbu'] = e
        elif e.type == pg.KEYDOWN:
            events['kd'] = e
        elif e.type == pg.KEYUP:
            events['ku'] = e
            
    return events
    
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
    
    b = Button('ok', color2=bcolor, tag='break')
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
    
    b = Button('yes', color2=(0, 200, 0), func=lambda : True, tag='return')
    b.rect.midleft = lower.midleft
    b.rect.x += 20
    screen.append(b)
    
    b = Button('no', color2=(200, 0, 0), func=lambda : False, tag='return')
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
        
        events = get_events()
        if events.get('q'):
            exit() 
        e = events.get('kd')
        if e:
            if e.key == pg.K_ESCAPE:
                exit()
                    
        for e in elements:
            
            is_button = isinstance(e, Button)
            if is_button:
                if e.get_state():
                    e.reset()
                    
            if hasattr(e, 'events'):
                e.events(events)
                
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

class Base_Object:
    def __init__(self, func=None, args=None, kwargs=None, **attrs):
        self.func = lambda *args, **kwargs: None if func is None else func
        self.args = [] if args is None else args
        self.kwargs = {} if kwargs is None else kwargs

        for k, v in attrs.items():
            setattr(self, k, v)
            
        self.visible = True
        
    def set_visible(self, visible):
        self.visible = visible
        
    def set_func_data(func=None, args=None, kwargs=None):
        if func:
            self.func = func
        if args:
            self.args = args
        if kwargs:
            self.kwargs = kwargs
            
    def events(self, input):
        pass
            
    def update(self):
        self.func(*self.args, **self.kwargs)
        
    def draw(self, surf):
        pass

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

class Textbox(Mover, Base_Object):
    pg.freetype.init()
    _FONT = 'arial.ttf'
    FONT = pg.freetype.Font(_FONT)
    setattr(FONT, 'pad', True)
    OLCACHE = {}
    
    @classmethod
    def set_font(cls, font):
        cls_FONT = font
        cls.FONT = pg.freetype.Font(font)
        setattr(cls.FONT, 'pad', True)
        
    @classmethod
    def get_font(cls):
        return cls._FONT
        
    @classmethod
    def render(cls, message='', tsize=20, fgcolor=(255, 255, 255), bgcolor=None, get_rect=False):
        image, rect = cls.FONT.render(message, fgcolor=fgcolor, bgcolor=bgcolor, size=tsize)
        if not get_rect:
            return image
        else:
            return (image, rect)
            
    @classmethod
    def get_outline_points(cls, r):
        if r in cls.OLCACHE:
            points = cls.OLCACHE[r]     
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
            cls.OLCACHE[r] = points
            
        return points
    
    def __init__(self, message='', tsize=10, fgcolor=(255, 255, 255), bgcolor=None, olcolor=None, width=2, anchor='center', fitted=False, font=None, func=None, args=None, kwargs=None):
        self.message = message
        self.original_message = message
        
        self.tsize = tsize
        self.original_tsize = tsize
        self._font = font
        if font is None:
            self._font = Textbox.get_font()
        else:
            self._font = font
        self.font = pg.freetype.Font(self._font)
        setattr(self.font, 'pad', True)
        
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.olcolor = olcolor
        self.width = width
        
        self.image, self.rect = self.render(self.message, get_rect=True)
        self.anchor = anchor
        self.fitted = fitted
        self.fitted_rect = None
        self.allignment_cache = 'c'
        
        self.characters = []
        
        self.timer = 0
        
        Base_Object.__init__(self, func=func, args=args, kwargs=kwargs)
        Mover.__init__(self)
        
        if self.fitted:
            self.set_fitted(True)

    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message
        
    def __eq__(self, other):
        return self.message == other.message and self.fgcolor == other.fgcolor 
   
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
            self.width = r
        
    def set_font_size(self, tsize):
        self.font.size = tsize
        self.tsize = tsize
        
    def set_font(self, font, tsize=None):
        if tsize is not None:
            self.tsize = tsize
        self._font = font
        self.font = pg.freetype.Font(font, size=self.tsize)
        setattr(self.font, 'pad', True)
        
    def set_anchor(self, anchor):
        self.anchor = anchor
        
    def set_fitted(self, fitted, rect=None):
        self.fitted = fitted
        if rect is not None:
            self.fitted_rect = rect
        else:
            self.fitted_rect = self.rect.copy()
        
    def set_message_timer(self, message, timer):
        self.set_message(message)
        self.timer = timer
        
    def get_message(self):
        return self.message

    def get_text_rect(self, text, tsize=None):
        if not tsize:
            tsize = self.tsize
        return self.font.get_rect(text, size=tsize)
    
    def get_image(self):
        return self.image
        
    def get_characters(self):
        return self.characters
        
    def reset(self):
        self.set_message(self.original_message)
        
    def update_image(self):
        self.update_text(self.get_message())
        
    def simple_render(self, message, fgcolor=None, bgcolor=None, tsize=0, get_rect=False):
        if fgcolor is None:
            fgcolor = self.fgcolor
        if not tsize:
            tsize=self.tsize
            
        image, rect = self.font.render(message, fgcolor=fgcolor, bgcolor=bgcolor, size=tsize)
            
        if get_rect:
            return (image, rect)
        else:
            return image
        
    def render(self, message, get_rect=False, track_chars=False):
        image, rect = self.font.render(message, fgcolor=self.fgcolor, size=self.tsize)
        
        if self.olcolor is not None:
            image = self.add_outline(message, image)
            rect = image.get_rect()
            
        if self.bgcolor is not None:
            bg = pg.Surface(rect.size).convert()
            bg.fill(self.bgcolor)
            bg.blit(image, (0, 0))
            image = bg
            
        if track_chars:
            characters = []
            x = 0 if self.olcolor is None else self.width
            for char in message + ' ':
                r = self.get_text_rect(char)
                characters.append((char, r, (x, 0)))
                x += r.width
            self.characters = characters
            
        if get_rect:
            return (image, rect)
        else:
            return image

    def add_outline(self, message, image):
        r = self.width
        points = Textbox.get_outline_points(r)
    
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

    def render_multicolor(self, colors):
        chars = []
        message = self.get_message()
        w = 0
        j = 0
        
        for i, char in enumerate(message):
            color = colors[j % len(colors)]
            self.set_fgcolor(color)
            img, r = self.render(char, get_rect=True)
            chars.append((img, r))
            w += r.width
            if not char.isspace():
                j += 1
            
        h = r.height
        image = pg.Surface((w, h)).convert_alpha()
        x = 0
        y = 0
            
        for char, r in chars:
            r.topleft = (x, y)
            image.blit(char, r)
            x += r.width
            
        self.new_image(image)
        
    def fit_text(self, bounding_rect, tsize=None, allignment='c', new_message=None):
        if new_message is not None:
            self.message = new_message
        message = self.message
        
        if tsize is None:
            tsize = self.original_tsize
        if tsize > bounding_rect.height:
            tsize = bounding_rect.height
        self.set_font_size(tsize)

        lines = [line.split(' ') for line in message.splitlines()]
        if not message or message.endswith('\n'):
            lines.append([''])
        characters = []

        image = pg.Surface(bounding_rect.size).convert_alpha()
        image.fill((0, 0, 0, 0))
        
        max_width, max_height = bounding_rect.size
        while self.tsize > 1:

            space = self.get_text_rect(' ', tsize=tsize).width
            if self.olcolor is not None:
                space -= self.width * 2
            x, y = (0, 0) 
            fail = False
            rendered_lines = []
            current_line = []
            
            for line in lines:

                for word in line:
                    
                    if not word:
                        word = ' '

                    word_surface, word_rect = self.render(word, get_rect=True)
                    w, h = word_rect.size
                    
                    if y + h > max_height:
                        fail = True
                        break
                    
                    if x + w >= max_width:
                        x = 0
                        y += h
                        if y + h >= max_height or x + w >= max_width:
                            fail = True
                            break
                        elif current_line:
                            rendered_lines.append(current_line.copy())
                            current_line.clear()

                    word_rect.topleft = (x, y)
                    current_line.append([word, word_surface, word_rect])
                    if word:
                        x += w
                        if word.strip():
                            x += space
                    
                if fail:
                    self.set_font_size(tsize - 1)
                    tsize = self.tsize
                    break
                else:
                    x = 0
                    y += h
                    if current_line:
                        rendered_lines.append(current_line.copy())
                        current_line.clear()
                
            if not fail:
                if current_line:
                    rendered_lines.append(current_line)
                break

        if rendered_lines:
        
            if allignment == 'c':   
                max_y = rendered_lines[-1][0][2].bottom
                min_y = rendered_lines[0][0][2].top
                
                h = max_y - min_y
                r = pg.Rect(0, 0, 2, h)
                r.centery = bounding_rect.height // 2
                dy = max(r.y - min_y, 0)
                
                for line in rendered_lines: 
                    max_x = max(r.right for _, _, r in line)
                    min_x = min(r.left for _, _, r in line)
                
                    w = max_x - min_x
                    r = pg.Rect(0, 0, w, 2)
                    r.centerx = bounding_rect.width // 2
                    dx = r.x - min_x

                    for info in line:
                        info[2].move_ip(dx, dy)
                            
            elif allignment == 'r':
                w = bounding_rect.width
                for line in rendered_lines:
                    dx = w - line[-1][2].right
                    for info in line:
                        info[2].move_ip(dx, 0)

        for line in rendered_lines:
            for word, surf, r in line:
                
                image.blit(surf, r)
                x, y = r.topleft
                w, h = r.size
                if word.isspace():
                    word = ''
                for char in word:
                    r = self.get_text_rect(char, tsize=tsize)
                    r.topleft = (x, y)
                    characters.append((char, r, (r.x, r.y)))
                    x += r.width  
                r = self.get_text_rect(' ', tsize=tsize)
                r.topleft = (x, y)
                characters.append(('', r, (r.x, r.y)))

        self.characters = characters
        self.allignment_cache = allignment
        self.new_image(image, rect=bounding_rect.copy(), set_pos=False)

    def new_image(self, image, rect=None, set_pos=True):
        if rect is None:
            rect = image.get_rect()
        a = getattr(self.rect, self.anchor, self.rect.center)
        self.image = image
        self.rect = rect
        if set_pos:
            setattr(self.rect, self.anchor, a)
        self.move_characters()
        
    def set_message(self, message):
        self.message = message
        if self.fitted:
            self.fit_text(self.rect, allignment=self.allignment_cache)
        else:
            image, rect = self.render(self.message, get_rect=True, track_chars=True)
            self.new_image(image, rect=rect)
        
    def clear(self):
        self.set_message('')
        
    def move_characters(self):
        rect = self.rect
        for char, r, rel in self.characters:
            rx, ry = rel
            r.topleft = (self.rect.x + rx, self.rect.y + ry)
        
    def update(self):
        self.move_characters()
        self.move()
        
        if self.timer != 0:
            self.timer -= 1
            if self.timer == 0:
                self.clear()
                
        super().update()
    
    def draw(self, win):
        if self.visible:
            win.blit(self.image, self.rect)

class Button_Base:
    def __init__(self, size=None, padding=(0, 0), color1=(0, 0, 0), color2=(100, 100, 100), border_radius=10, tag='', suppress=False, func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.size = size
        if size is None:
            size = (1, 1)
        self.rect = pg.Rect(0, 0, size[0], size[1]).inflate(*padding)
        self.padding = padding
        
        self.color1 = color1
        self.color2 = color2
        self.current_color = color1
        self.border_radius = border_radius
        
        self.tag = tag
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.return_val = None
        
        self.visible = True
        self.active = False
        self.pressed = False
        self.disabled = False
        self.suppress = suppress
        
    def set_tag(self, tag):
        self.tag = tag
        
    def get_tag(self):
        return self.tag

    def set_size(self, w, h):
        self.rect.size = (w, h)
        
    def get_state(self):
        return self.pressed
        
    def disable(self):
        self.disabled = True
        self.state = 0
        self.current_color = self.color1
        
    def enable(self):
        self.disabled = False
        
    def set_visible(self, visible):
        self.visible = visible
        
    def set_suppress(self, suppress):
        self.suppress = suppress
        
    def reset(self):
        self.pressed = False
        
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
        
    def get_return(self, reset=True):
        r = self.return_val
        if reset:
            self.return_val = None
        return r
        
    def clear_args(self):
        self.args.clear()
        self.kwargs.clear()
  
    def update_rect(self, size):
        if self.size is None or any(self.padding):
            c = self.rect.center
            self.rect.size = size
            self.rect.inflate_ip(*self.padding)
            self.rect.center = c
  
    def click_down(self):
        if self.active:
            self.pressed = True
            self.return_val = self.func(*self.args, **self.kwargs)

    def events(self, events):
        if self.visible:
        
            p = events['p']
            if self.rect.collidepoint(p):
                self.active = True  
            else:  
                self.active = False
                
            if not self.disabled:
            
                mbd = events.get('mbd')
                mbu = events.get('mbu')
                if mbd:
                    if mbd.button == 1:
                        self.click_down()  
                elif mbu:
                    if mbu.button == 1:
                        self.pressed = False
            
    def update(self):
        if self.visible:
            if not self.disabled:
                if self.active and self.current_color != self.color2:
                    self.current_color = self.color2       
                elif not self.active and self.current_color != self.color1:
                    self.current_color = self.color1   
  
    def draw(self, win):
        if self.visible and not self.suppress:
            pg.draw.rect(win, self.current_color, self.rect, border_radius=self.border_radius)

class Button(Button_Base):
    def __init__(self, message, tsize=20, size=None, padding=(0, 0), color1=(0, 0, 0), color2=(100, 100, 100), tcolor=(255, 255, 255), border_radius=10, tag='', func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.textbox = Textbox(message, tsize=tsize, fgcolor=tcolor)
        if size is None:
            size = self.textbox.rect.size
        super().__init__(size=size, padding=padding, color1=color1, color2=color2, border_radius=border_radius, tag=tag, func=func, args=args, kwargs=kwargs)
        self.update_rect(self.textbox.rect.size)

        self.max_timer = 0
        self.timer = 0
        self.tmessage = ''

    def set_timer_rule(self, timer, message):
        self.max_timer = timer
        self.tmessage = message

    def get_message(self):
        return self.textbox.get_message()
        
    def set_message(self, message, tcolor=None):    
        if tcolor is not None:
            self.textbox.set_fgcolor(tcolor)
        self.textbox.set_message(message)
        self.update_rect(self.textbox.rect.size)
        
    def click_down(self):
        super().click_down()
        if self.active:
            if self.max_timer:
                self.set_message(self.tmessage)
                self.timer = self.max_timer
            
    def update(self):
        if self.visible:
            self.textbox.update()
            
        super().update()
                
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.set_message(self.textbox.original_message)
  
    def draw(self, win):
        if self.visible:
            super().draw(win)
            self.textbox.rect.center = self.rect.center
            self.textbox.rect.y -= 1
            self.textbox.draw(win)

class Image_Button(Button_Base):
    def __init__(self, image, size=None, padding=(0, 0), color1=(0, 0, 0), color2=(100, 100, 100), border_radius=10, tag='', suppress=False, func=lambda *args, **kwargs: None, args=[], kwargs={}): 
        if size is None:
            size = image.get_size()
        elif any(padding):
            w, h = size
            pw, ph = padding
            image = pg.transform.smoothscale(image, (w - (2 * pw), h - (2 * ph)))
            padding = (0, 0)
        self.image = Image(image)
        super().__init__(size=size, padding=padding, color1=color1, color2=color2, border_radius=border_radius, tag=tag, suppress=suppress, func=func, args=args, kwargs=kwargs)
        self.update_rect(self.image.rect.size)
        
    def draw(self, win):
        super().draw(win)
        self.image.rect.center = self.rect.center
        self.image.draw(win)

class Input:
    VALID_CHARS = set(range(32, 127))
    VALID_CHARS.add(9)
    VALID_CHARS.add(10)
    
    TK = Tk()
    
    @classmethod
    def copy_to_clipboard(cls, text):
        cls.TK.clipboard_append(text.strip())
        
    @classmethod
    def get_clip(cls):
        try:
            text = cls.TK.clipboard_get().strip()  
        except:
            text = '' 
        return text
        
    @staticmethod
    def positive_int_check(char):
        return char.isnumeric()

    def __init__(self, size, message='type here', tsize=20, color=(0, 0, 0, 0), tcolor=(255, 255, 255), length=99, check=lambda char: True, fitted=False, scroll=False, allignment='c'):      
        self.textbox = Textbox(message, tsize=tsize, fgcolor=tcolor, anchor='topleft', fitted=fitted)
        if not fitted:
            w = size[0]
            self.image = pg.Surface((w, self.textbox.rect.height + 10)).convert_alpha()
        else:
            self.image = pg.Surface(size).convert_alpha()
        self.color = color
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.fitted = fitted
        self.allignment = allignment
        self.scroll = scroll
        self.tsize = tsize
     
        self.length = length
        self.check = check

        self.last_click = 0
        self.clicks = 1
        self.active = False
        
        self.index = 0
        self.selecting = False
        self.selection = []
        
        self.btimer = 0
        self.timer = 0
        self.backspace = False
        self.bhold = False
        
        self.ctrl = False
        self.copy = False
        self.paste = False
        self.cut = False
        self.all = False

        self.last_message = message
        self.logs = []

        self.update_message(self.textbox.get_message())
     
    def get_chars(self):
        return self.textbox.characters

    def get_message(self):
        return self.textbox.get_message()

    def update_message(self, message):
        if self.check_message(message):
            self.textbox.set_message(message)
            if self.fitted:
                self.textbox.fit_text(self.rect, tsize=self.tsize, allignment=self.allignment)

    def check_message(self, text):
        return all(ord(char) in Input.VALID_CHARS for char in text) and self.check(text)

    def set_index(self, index):
        index = max(index, 0)
        index = min(index, len(self.get_message()))
        self.index = index
              
    def highlight_word(self):
        i = j = self.index
        m = self.get_message()
        
        if i not in range(len(m)):
            return
        
        istop = False
        jstop = False

        while not (istop and jstop):

            if not istop:
                if i == 0:
                    istop = True
                elif m[i] == ' ' or m[i] == '\n':
                    i += 1
                    istop = True
                else:
                    i -= 1

            if not jstop:
                if j == len(m) or m[j] == ' ' or m[j] == '\n':
                    jstop = True
                else:
                    j += 1

        self.selection = [i, j]
        self.set_index(j)
        
    def highlight_full(self):
        m = self.get_message()
        self.selection = [0, len(m)]
        self.set_index(len(m))
   
    def get_selection(self):
        if self.selection:
            i, j = self.selection
            return self.get_message()[min(i, j):max(i, j)]
        return ''

    def replace_selection(self, text):
        m = self.get_message()
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
                m = self.get_message()
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
            m = self.get_message()
            message = m[:self.index] + m[min(self.index + 1, len(m)):]
            self.update_message(message)
            self.set_index(self.index - 1)
         
    def shift_index(self, dir):
        if dir == 'r':
            if self.selection:
                self.set_index(max(self.selection))
            else:
                self.set_index(self.index + 1)
            
        elif dir == 'l':
            if self.selection:
                self.set_index(min(self.selection))
            else:
                self.set_index(self.index - 1)
                
        self.selection.clear()
        
    def get_closest_index(self, p=None):
        if p is None:
            p = pg.mouse.get_pos()
        chars = self.get_chars()
        i = min(range(len(chars)), key=lambda i: vec(chars[i][1].center).distance_to(p))
        r = chars[i][1]
        if p[0] - r.centerx >= 0:
            i += 1
        return i

    def close(self):
        if self.active:
            self.active = False
            m = self.get_message()
            if not m.strip():
                self.textbox.reset()
                m = self.get_message()
            if self.last_message != m:
                self.logs.append({'t': 'val', 'i': self, 'm': (self.last_message, m)})
                self.last_message = m
            self.selection.clear()
            if self.scroll:
                self.textbox.rect.midleft = self.rect.midleft
  
    def send_keys(self, text):
        if self.selection:
            self.replace_selection('')
        m = self.get_message()
        message = m[:self.index] + text + m[self.index:]
        self.update_message(message)
        self.set_index(self.index + len(text))

    def shift_textbox(self):
        if self.textbox.rect.width < self.rect.width:
            self.textbox.rect.midleft = self.rect.midleft
        else:
            self.textbox.rect.centery = self.rect.centery
            chars = self.get_chars()
            if self.index in range(len(chars)):
                r = chars[self.index][1]
                if not self.rect.contains(r):
                    if r.left < self.rect.left:
                        dx = self.rect.left - r.left
                    else:
                        dx = self.rect.right - r.right
                    self.textbox.rect.x += dx
                if self.textbox.rect.right < self.rect.right and self.textbox.rect.left < self.rect.left:
                    self.textbox.rect.right = self.rect.right
                    
    def update_click_timer(self):
        current_click = pg.time.get_ticks()
        timer = current_click - self.last_click
        self.last_click = current_click
        if timer < 170:
            self.clicks += 1
        else:
            self.clicks = 1
        return self.clicks

    def click_down(self, button):
        p = pg.mouse.get_pos()
        
        if self.rect.collidepoint(p) or self.textbox.rect.collidepoint(p):
            clicks = self.update_click_timer()

            if clicks == 1:
                if not self.active:
                    self.active = True
                    self.set_index(len(self.get_message()))                       
                else:
                    self.selecting = True
                    i = self.get_closest_index(p=p)
                    self.set_index(i)
                self.selection.clear()
                
            elif clicks == 2:
                self.highlight_word()
                
            elif clicks == 3:
                self.highlight_full()

        else:
            self.close()
        
    def click_up(self, button):
        p = pg.mouse.get_pos()
        
        self.selecting = False
        if self.selection:
            if self.selection[0] == self.selection[1]:
                self.selection.clear()
        
    def events(self, events):
        click = False
        sent = False

        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        kd = events.get('kd')
        ku = events.get('ku')

        if mbd:
            if mbd.button == 1:
                click = True   
            self.click_down(mbd.button)
            
        elif mbu:
            self.click_up(mbu.button)
                
        elif self.active:

            if kd:
                
                if kd.key == pg.K_BACKSPACE:
                    self.backspace = True
                    
                elif (kd.key == pg.K_RCTRL) or (kd.key == pg.K_LCTRL):
                    self.ctrl = True
                elif kd.key == pg.K_c:
                    self.copy = True
                elif kd.key == pg.K_x:
                    self.cut = True
                elif kd.key == pg.K_v: 
                    self.paste = True
                elif kd.key == pg.K_a:
                    self.all = True
                    
                elif kd.key == pg.K_DELETE:
                    self.delete()
                    
                elif kd.key == pg.K_RIGHT:
                    self.shift_index('r')
                elif kd.key == pg.K_LEFT:
                    self.shift_index('l')
                    
                elif kd.key == pg.K_RETURN:
                    if not self.fitted:
                        self.close()
                    else:
                        self.send_keys('\n')
                        
                elif kd.key == pg.K_TAB:
                    self.send_keys('    ')
                    sent = True
                        
                if not sent:
                    if not (self.ctrl or self.backspace) and hasattr(kd, 'unicode'):
                        char = kd.unicode
                        if char:
                            self.send_keys(char)
                        
            elif ku:
                
                if ku.key == pg.K_BACKSPACE:
                    self.backspace = False
                    self.bhold = False
                    self.btimer = 0
                
                elif (ku.key == pg.K_RCTRL) or (ku.key == pg.K_LCTRL):
                    self.ctrl = False
                elif ku.key == pg.K_c:
                    self.copy = False
                elif ku.key == pg.K_x:
                    self.cut = False
                elif ku.key == pg.K_v: 
                    self.paste = False
                elif ku.key == pg.K_a:
                    self.all = False
                        
        if self.ctrl:
        
            if self.copy:
                text = self.get_selection()
                Input.copy_to_clipboard(text)
                self.copy = False
                
            elif self.cut:
                if self.selection:
                    text = self.get_selection()
                    Input.copy_to_clipboard(text)
                    self.replace_selection('')
                    self.cut = False  
                    
            elif self.paste:
                text = Input.get_clip()
                if self.selection:
                    self.replace_selection(text)
                else:
                    self.send_keys(text)
                self.paste = False
                
            elif self.all:
                self.highlight_full()
                self.all = False
            
        elif self.backspace:
            self.back()
       
        if self.selecting:
            
            if click:
                self.selection = [self.index, self.index]   

            else:
                i = self.get_closest_index(p=p)
                if i not in self.selection:
                    self.selection[1] = i

            self.set_index(self.selection[1])
        
    def update(self):
        self.btimer -= 1
        
        self.timer -= 1
        if self.timer == -25:
            self.timer *= -1

        if not self.fitted:
            if self.scroll:
                self.shift_textbox()
            else:
                self.textbox.rect.midleft = self.rect.midleft
        else:
            self.textbox.rect.center = self.rect.center
            self.textbox.rect.y += 1
                
        self.textbox.update()
        
    def draw(self, win):
        x0, y0 = self.rect.topleft
        dx = -x0
        dy = -y0

        self.image.fill(self.color)

        if self.selection:
            chars = self.get_chars()[:-1]
            i, j = self.selection
            for _, r, _ in chars[min(i, j):max(i, j)]:
                pg.draw.rect(self.image, (0, 102, 255), r.move(dx, dy))

        self.image.blit(self.textbox.image, self.textbox.rect.move(dx, dy))
        
        if self.active and self.timer > 0:
            chars = self.get_chars()
            if chars:
                if self.index in range(len(chars)):
                    r = chars[self.index][1].move(dx, dy)
                    pg.draw.line(self.image, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
            else:
                r = self.textbox.get_text_rect(' ', tsize=self.tsize)
                if self.fitted:
                    r.center = self.rect.center
                    r.move_ip(dx, dy)
                    pg.draw.line(self.image, self.textbox.fgcolor, r.midtop, r.midbottom, width=2)
                else:
                    r.midleft = self.rect.midleft
                    r.move_ip(dx, dy)
                    pg.draw.line(self.image, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
                    
        win.blit(self.image, self.rect)

class Counter:
    ARROW_CACHE = {}
    
    @classmethod
    def get_arrows(cls, size):
        if size not in cls.ARROW_CACHE:
            left_arrow = pg.Surface((size, size)).convert_alpha()
            left_arrow.fill((0, 0, 0, 0))
            right_arrow = left_arrow.copy()
            r = left_arrow.get_rect()
            pg.draw.polygon(left_arrow, (255, 255, 255), (r.topright, r.bottomright, r.midleft))
            pg.draw.polygon(right_arrow, (255, 255, 255), (r.topleft, r.bottomleft, r.midright))
            cls.ARROW_CACHE[size] = (left_arrow, right_arrow)
        return cls.ARROW_CACHE[size]

    def __init__(self, options, option=None, tsize=30, tag=''):
        self.options = options
        self.index = 0

        self.tsize = tsize
        self.textbox = Textbox(f' {self.get_current_option()} ', tsize=tsize)
        left_arrow, right_arrow = Counter.get_arrows(self.textbox.rect.height - 20)
        self.left_button = Image_Button(left_arrow, padding=(10, 10), border_radius=0, func=self.incriment, args=[-1])
        self.right_button = Image_Button(right_arrow, padding=(10, 10), border_radius=0, func=self.incriment, args=[1])
        
        w = self.textbox.rect.width + self.left_button.rect.width + self.right_button.rect.width
        h = max(self.textbox.rect.height, self.left_button.rect.height, self.right_button.rect.height)
        self.rect = pg.Rect(0, 0, w, h)
        
        if option:
            self.set_option(option)
            
        self.tag = tag
        self.disabled = False
        
        self.update()
        
    def get_current_option(self):
        return self.options[self.index]
        
    def set_option(self, option):
        if option in self.options:
            self.index = self.options.index(option)
            self.update_message()
            
    def update_message(self):
        r = self.textbox.rect
        self.textbox.set_message(f' {self.get_current_option()} ')
        self.textbox.fit_text(r, tsize=self.tsize)
        
    def disable(self):
        self.disabled = True
        
    def enable(self):
        self.disabled = False
        
    def get_tag(self):
        return self.tag
        
    def incriment(self, dir):
        self.index = (self.index + dir) % len(self.options)
        self.update_message()
        
    def events(self, input):
        if not self.disabled:
            self.left_button.events(input)
            self.right_button.events(input)
        
    def update(self):
        self.left_button.rect.topleft = self.rect.topleft
        self.textbox.rect.midleft = self.left_button.rect.midright
        self.right_button.rect.midleft = self.textbox.rect.midright
        
        if not self.disabled:
            self.left_button.update()
            self.right_button.update()
        
    def draw(self, win):
        self.textbox.draw(win)
        
        if not self.disabled:
            self.left_button.draw(win)
            self.right_button.draw(win)

class Scroll_Bar:
    ARROW_CACHE = {}
    
    @classmethod
    def get_arrows(cls, size):
        if size not in cls.ARROW_CACHE:
            arrow = pg.Surface((size, size)).convert()
            arrow.fill((255, 255, 255))
            r = arrow.get_rect()
            w, h = r.size
            pg.draw.polygon(arrow, (100, 100, 100), ((3, h - 3), (w - 3, h - 3), (w / 2, 3)))
            up_arrow = arrow
            down_arrow = pg.transform.rotate(up_arrow, 180)
            cls.ARROW_CACHE[size] = (up_arrow, down_arrow)
        return cls.ARROW_CACHE[size]
    
    def __init__(self, height, total_height=0, width=16, extended_rect=None, color1=(255, 255, 255), color2=(100, 100, 100)):
        self.rect = pg.Rect(0, 0, width , height)
        self.handel = pg.Rect(0, 0, width - 4, 1)
        self.body = pg.Rect(0, 0, width, height - (2 * width))
        self.image = pg.Surface(self.body.size).convert()
        self.image.fill(color1)
        if not extended_rect:
            extended_rect = self.rect
        self.extended_rect = extended_rect
        
        self.rel_pos = None
        self.last_pos = self.rect.top
        
        up_arrow, down_arrow = Scroll_Bar.get_arrows(width)
        self.up_button = Image_Button(up_arrow, size=up_arrow.get_size(), border_radius=0, func=self.scroll, args=[-1])
        self.down_button = Image_Button(down_arrow, size=down_arrow.get_size(), border_radius=0, func=self.scroll, args=[1])
        
        self.color1 = color1
        self.color2 = color2
        
        self.height = self.body.height
        if not total_height:
            total_height = self.height
        self.total_height = total_height
        self.set_total_height(total_height)
        
    def is_held(self):
        return self.rel_pos is not None
        
    def is_full(self):
        return self.handel.height == self.body.height
        
    def set_total_height(self, total_height):
        self.total_height = total_height
        top = self.handel.top
        r = self.height / self.total_height
        self.handel.height = self.height * r
        self.handel.top = top
        
    def get_offset(self):
        return round((self.handel.top - self.body.top) / self.height, 2)
        
    def can_scroll_down(self):
        return self.handel.bottom < self.body.bottom
        
    def can_scroll_up(self):
        return self.handel.top > self.body.top
        
    def scroll(self, dir):
        self.handel.top += (dir * max(self.handel.height / 2, 1))
        self.adjust_handel()
        
    def go_to_bottom(self):
        while self.can_scroll_down():
            self.scroll(-1)
            
    def go_to_top(self):
        while self.can_scroll_up():
            self.scroll(1)

    def adjust_handel(self):
        self.handel.centerx = self.body.centerx
        if self.handel.top < self.body.top:
            self.handel.top = self.body.top
        elif self.handel.bottom > self.body.bottom:
            self.handel.bottom = self.body.bottom
            
    def set_rel_pos(self, p):
        y0 = p[1]
        y1 = self.handel.top
        dy = y1 - y0
        self.rel_pos = dy
            
    def events(self, events):                
        self.up_button.events(events)
        self.down_button.events(events)
        
        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if mbd:
            if mbd.button == 1:   
                if self.handel.collidepoint(p):
                    self.set_rel_pos(p)
                elif self.body.collidepoint(p):
                    self.set_rel_pos(self.handel.center)
            elif self.rect.collidepoint(p) or self.extended_rect.collidepoint(p):
                if mbd.button == 4:
                    self.scroll(-1)
                elif mbd.button == 5:
                    self.scroll(1)
        elif mbu:
            self.rel_pos = None
                
    def update(self):
        self.body.center = self.rect.center
        
        current_pos = self.body.top
        if current_pos != self.last_pos:
            dy = current_pos - self.last_pos
            self.handel.y += dy
            self.last_pos = current_pos
        if self.rel_pos is not None:
            y = pg.mouse.get_pos()[1]
            self.handel.top = y + self.rel_pos
        self.adjust_handel()

        self.up_button.rect.midtop = self.rect.midtop
        self.up_button.update()
        self.down_button.rect.midbottom = self.rect.midbottom
        self.down_button.update()

    def draw(self, win):
        win.blit(self.image, self.body)
        pg.draw.rect(win, self.color2, self.handel)
        self.up_button.draw(win)
        self.down_button.draw(win)

class Pane_Base:
    def __init__(self, size, color=(0, 0, 0, 0), label='', text_kwargs={}, label_height=20, label_color=(0, 0, 0), hide_label=False):
        self.size = size
        self.image = pg.Surface(size).convert_alpha()
        self.color = color
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.bounding_rect = self.rect.copy()
        self.bound_offset = 0
        
        self.label = Textbox(label, **text_kwargs)
        label_rect = pg.Rect(0, 0, self.rect.width + 16, label_height)
        self.label.fit_text(label_rect, tsize=label_height)
        self.label_rect = self.label.rect.copy()
        self.label_color = label_color
        self.hide_label = hide_label

        self.scroll_bar = Scroll_Bar(self.rect.height, extended_rect=self.rect)
        self.last_offset = -1
        
        self.objects = []

        self.orientation_cache = {'xpad': 5, 'ypad': 5, 'dir': 'y', 'pack': False}
        self.rel_pos = {}
        
    def get_total_rect(self):
        return pg.Rect(self.rect.x, self.label_rect.y, self.label_rect.width, self.rect.height + self.label_rect.height)
  
    def is_same(self, objects):
        if len(objects) == len(self.objects):
            return all(objects[i] == self.objects[i] for i in range(len(objects)))
        else:
            return False
            
    def get_visible(self):
        return [o for o in self.objects if self.rect.contains(o.rect)]
        
    def sort_objects(self, key):
        objects = sorted(self.objects, key=key)
        self.join_objects(objects, **self.orientation_cache)
    
    def clear(self):
        self.join_objects([])
        self.image.fill(self.color)
    
    def join_objects(self, objects, xpad=5, ypad=5, dir='y', pack=False, force=False, scroll=False, move=False):
        same = self.is_same(objects)

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
            self.set_total_height()
                
        elif same and move:
            for i in range(len(self.objects)):
                objects[i].rect = self.objects[i].rect.copy()

    def set_total_height(self):
        h = 0
        if self.objects:
            heights = [self.rel_pos[id(o)][1] for o in self.objects]
            y0 = min(heights)
            y1 = max(heights)
            h = max(y1 - y0, h)
            h += (2 * self.orientation_cache['ypad'])
            
        h = max(h, self.scroll_bar.body.height)
        
        self.scroll_bar.set_total_height(h)
        self.bounding_rect.height = h
        offset = self.scroll_bar.get_offset()
        self.set_window(offset)
        
    def update_window(self):
        current_offset = self.scroll_bar.get_offset()
        if current_offset != self.last_offset:
            self.set_window(current_offset)
            self.last_offset = current_offset
                
    def set_window(self, offset):
        self.bounding_rect.top = self.rect.top - (self.bounding_rect.height * offset)
        self.bound_offset = self.rect.top - self.bounding_rect.top
        self.scroll()
        self.redraw()
        
    def scroll(self):
        if self.objects:
            sx, sy = self.bounding_rect.topleft
            for o in self.objects: 
                rx, ry = self.rel_pos[id(o)]
                o.rect.x = sx + rx
                o.rect.y = sy + ry
      
    def redraw(self):
        self.image.fill(self.color)
            
        for o in self.objects:
            dx = o.rect.x - self.rect.x
            dy = o.rect.y - self.rect.y

            tl = o.rect.topleft 
            o.rect.topleft = (dx, dy)
            o.draw(self.image)
            o.rect.topleft = tl

    def events(self, events):
        self.scroll_bar.events(events)
                        
    def update(self):
        self.bounding_rect.centerx = self.rect.centerx
        self.bounding_rect.top = self.rect.top - self.bound_offset
        
        self.scroll_bar.rect.topleft = self.rect.topright
        self.scroll_bar.update()
        self.update_window()
        
        if self.scroll_bar.is_full():
            self.label.rect.midbottom = self.rect.midtop
            self.label_rect.width = self.rect.width
        else:
            self.label.rect.bottomleft = self.rect.topleft
            self.label_rect.width = self.rect.width + self.scroll_bar.rect.width
        self.label_rect.bottomleft = self.rect.topleft
        self.label.update()
        
    def draw_label(self, win):
        pg.draw.rect(win, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(win)

    def draw(self, win):
        if self.color != (0, 0, 0, 0) or self.objects:
            win.blit(self.image, self.rect)
        if not self.hide_label:
            pg.draw.rect(win, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)
            self.label.draw(win)
        if not self.scroll_bar.is_full():
            self.scroll_bar.draw(win)
        
class Live_Pane(Pane_Base):
    def redraw(self):
        pass
        
    def events(self, events):
        self.scroll_bar.events(events)
        
        for o in self.objects:
            if hasattr(o, 'events'):
                o.events(events)
            
    def update(self):
        super().update()
        
        for o in self.objects:
            rx, ry = self.rel_pos[id(o)]
            sx, sy = self.bounding_rect.topleft
            o.rect.x = sx + rx
            o.rect.y = sy + ry
            
            if hasattr(o, 'update'):
                o.update()
                    
    def draw(self, win):
        self.image.fill(self.color)
        
        for o in self.objects:
            dx = o.rect.x - self.rect.x
            dy = o.rect.y - self.rect.y
            tl = o.rect.topleft 
            o.rect.topleft = (dx, dy)
            o.draw(self.image)
            o.rect.topleft = tl

        win.blit(self.image, self.rect)
        pg.draw.rect(win, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(win)
        if not self.scroll_bar.is_full():
            self.scroll_bar.draw(win)

class Base_Popup(Pane_Base, Mover):
    def __init__(self, *args, **kwargs):
        Pane_Base.__init__(self, *args, **kwargs)
        self.t = None
        self.o = None
        
        self.timer = 0
        self.locked = False
        
        Mover.__init__(self) 
        
    def is_visible(self):
        return self.t != self.o
        
    def get_target(self):
        return self.rect.move(0, -self.rect.height)

    def events(self, events):
        super().events(events)
        
        p = events['p']
        mbd = events.get('mbd')

        if mbd:
            if mbd.button == 1:
                if self.label_rect.collidepoint(p):
                    if self.timer < 10:
                        self.locked = not self.locked
                    self.timer = 0
        
        if self.get_total_rect().inflate(50, 0).collidepoint(p):
            if not self.t:
                t = self.get_target()
                self.t = t
                self.o = self.rect.copy()
            if self.target != self.t:
                self.set_target(self.t, v=15)
        elif not self.locked and not self.scroll_bar.is_held() and self.t:
            self.set_target(self.o, v=15)
        
    def update(self):
        self.move()
        super().update()
        self.scroll()
        
        if self.timer < 15:
            self.timer += 1
        
        if self.finished():
            if self.target == self.o:
                self.t = None
                self.o = None
            
    def draw(self, win):
        if self.is_visible():
        
            win.blit(self.image, self.rect)
            if not self.scroll_bar.is_full():
                self.scroll_bar.draw(win)
                
            if self.locked: 
                color = tuple(max(rgb - 50, 0) for rgb in self.label_color)
                pg.draw.rect(win, color, self.label_rect, width=5, border_top_left_radius=10, border_top_right_radius=10)

        pg.draw.rect(win, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)  
        self.label.draw(win)

class Live_Popup(Live_Pane, Mover):
    def __init__(self, *args, **kwargs):
        Live_Pane.__init__(self, *args, **kwargs)
        self.t = None
        self.o = None
        
        self.timer = 0
        self.locked = False
        
        Mover.__init__(self)
        
    def is_visible(self):
        return self.t != self.o
        
    def get_target(self):
        return self.rect.move(0, -self.rect.height)

    def events(self, input):
        p = pg.mouse.get_pos()
        super().events(input)
        
        for e in input:
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.label_rect.collidepoint(p):
                        if self.timer < 10:
                            self.locked = not self.locked
                        self.timer = 0
            break
        
        if self.get_total_rect().inflate(50, 0).collidepoint(p):
            if not self.t:
                t = self.get_target()
                self.t = t
                self.o = self.rect.copy()
            if self.target != self.t:
                self.set_target(self.t, v=10)
        elif not self.locked and not self.scroll_bar.is_held() and self.t:
            self.set_target(self.o)
        
    def update(self):
        self.move()
        super().update()
        
        if self.timer < 15:
            self.timer += 1
        
        if self.target == self.o and self.finished():
            self.t = None
            self.o = None
            
    def draw(self, win):
        if self.is_visible():
            self.image.fill(self.color)
            
            for o in self.objects:
                dx = o.rect.x - self.rect.x
                dy = o.rect.y - self.rect.y
                tl = o.rect.topleft 
                o.rect.topleft = (dx, dy)
                o.draw(self.image)
                o.rect.topleft = tl

            win.blit(self.image, self.rect)
            if not self.scroll_bar.is_full():
                self.scroll_bar.draw(win)
                
            if self.locked: 
                color = tuple(max(rgb - 50, 0) for rgb in self.label_color)
                pg.draw.rect(win, color, self.label_rect, width=5, border_top_left_radius=10, border_top_right_radius=10)

        pg.draw.rect(win, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)  
        self.label.draw(win)

class Sectioned_Slider:
    ARROW_CACHE = {}
    
    @classmethod
    def get_arrows(cls, size):
        if size not in cls.ARROW_CACHE:
            arrow = pg.Surface((size, size)).convert()
            arrow.fill((255, 255, 255))
            r = arrow.get_rect()
            w, h = r.size
            pg.draw.polygon(arrow, (100, 100, 100), ((3, 3), (w - 3, 3), (w / 2, h - 3)))
            cls.ARROW_CACHE[size] = arrow
        return cls.ARROW_CACHE[size]
        
    def __init__(self, labels, objects, size=(100, 100)):
        self.panes = []
        self.buttons = []
        for l, o in zip(labels, objects):
            p = Live_Pane(size, label=l, label_color=(100, 100, 100))
            p.join_objects(o)
            self.panes.append(p)
            b = Image_Button(Sectioned_Slider.get_arrows(10), func=self.set_open_pane, args=[p])
            self.buttons.append(b)
            
        height = sum(p.label_rect.height for p in self.panes)
        self.rect = pg.Rect(0, 0, size[0], height)
        
        self.open_pane = None
        
    def set_open_pane(self, p):
        self.open_pane = p
        
    def events(self, events):
        for b in self.buttons:
            b.events(events)
            
        if self.open_pane:
            self.open_pane.events(events)
        
    def update(self):
        x, y = self.rect.topleft
        for p, b in zip(self.panes, self.buttons):
            p.rect.topleft = (x, y)
            b.rect.center = p.label_rect.midright
            b.rect.x -= 25
            p.update()
            b.update()
            if p is self.open_pane:
                y += p.rect.height + p.label_rect.height
            else:
                y += p.label_rect.height
        
    def draw(self, win):
        for p in self.panes:
            if p is self.open_pane:
                p.draw(win)
            else:
                p.draw_label(win)
        for b in self.buttons:
            b.draw(win)

class Slider:
    def __init__(self, size, ran, dir, handel_size=None, color=(255, 255, 255), hcolor=(0, 0, 0), flipped=False, func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.color = color
        
        if handel_size is None:
            if dir == 'x':
                handel_size = (10, self.rect.height * 2)
            elif dir == 'y':
                handel_size = (self.rect.width * 2, 10)
        self.handel = pg.Rect(0, 0, handel_size[0], handel_size[1])
        self.handel_color = hcolor
        
        self.held = False
        self.flipped = False
        
        self.range = ran
        self.dir = dir
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
        if flipped:
            self.flip()
        
    def flip(self):
        self.flipped = not self.flipped

    def get_state(self):
        self.adjust_handel()
        
        if self.dir == 'x':
            dx = self.handel.centerx - self.rect.x
            ratio = dx / self.rect.width 
        elif self.dir == 'y':
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
            
        if self.dir == 'x':   
            dx = ratio * self.rect.width
            self.handel.centerx = dx + self.rect.x
        elif self.dir == 'y':
            dy = ratio * self.rect.height
            self.handel.centery = dy + self.rect.y
            
    def adjust_handel(self):
        if self.dir == 'x':
            self.handel.centery = self.rect.centery
            if self.handel.centerx > self.rect.right:
                self.handel.centerx = self.rect.right
            elif self.handel.centerx < self.rect.left:
                self.handel.centerx = self.rect.left
        elif self.dir == 'y':
            self.handel.centerx = self.rect.centerx
            if self.handel.centery > self.rect.bottom:
                self.handel.centery = self.rect.bottom
            elif self.handel.centery < self.rect.top:
                self.handel.centery = self.rect.top
        
    def events(self, events):
        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if mbd:
            if mbd.button == 1:
                if self.handel.collidepoint(p) or self.rect.collidepoint(p):
                    self.held = True

        elif mbu:
            if mbu.button == 1:
                self.held = False
                
    def update(self):
        if self.held:
            p = pg.mouse.get_pos()
            self.handel.center = p
            self.func(*self.args, **self.kwargs)
            
        self.adjust_handel()

    def draw(self, win):
        pg.draw.rect(win, self.color, self.rect)
        pg.draw.rect(win, self.handel_color, self.handel)

class RGBSlider(Slider):
    RGB = ('r', 'g', 'b')
    def __init__(self, size, dir, rgb, handel_size=None, hcolor=None, flipped=False, func=lambda *args, **kwargs: None, args=[], kwargs={}):
        super().__init__(size, range(255), dir, handel_size=handel_size, hcolor=hcolor, func=func, args=args, kwargs=kwargs)
        
        self.rgb = RGBSlider.RGB.index(rgb)
        self.hcolor = hcolor

        surf = pg.Surface((255, 1)).convert()
        color = [0, 0, 0]
        for x in self.range:
            color[self.rgb] = x
            surf.set_at((x, 0), color)
        if self.dir == 'y':
            surf = pg.transform.rotate(surf, -90)
        self.image = pg.transform.scale(surf, self.rect.size)
        
        if flipped:
            self.flip()
            
    def flip(self):
        super().flip()
        if self.dir == 'x':
            self.image = pg.transform.flip(self.image, True, False) 
        elif self.dir == 'y':
            self.image = pg.transform.flip(self.image, False, True)
            
    def get_color(self):
        color = [0, 0, 0]
        color[self.rgb] = self.get_state()
        return color
        
    def update(self):
        super().update()
        if self.handel_color is None:
            self.hcolor = self.get_color()

    def draw(self, win):
        win.blit(self.image, self.rect)
        pg.draw.rect(win, (255, 255, 255), self.rect, width=1)
        pg.draw.rect(win, self.hcolor, self.handel)
        pg.draw.rect(win, (255, 255, 255), self.handel, width=3)

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
    
    
    
    
    
    
    