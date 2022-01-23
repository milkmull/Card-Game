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

class Line:
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    def intersect(a, b, c, d):
        return Line.ccw(a, c, d) != Line.ccw(b, c, d) and Line.ccw(a, b, c) != Line.ccw(a, b, d)
 
class Mover:
    def __init__(self):
        self.target_rect = None
        self.last_pos = None
        
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel = vec(0, 0)
        self.scale_acc = vec(0, 0)
        
        self.startup_timer = 0
        self.end_timer = 0

        self.moving = False
        self.scaling = False
        
        self.movement_sequence = []
        self.movement_cache = {'v': 5, 'startup_timer': 0, 'end_timer': 0, 'scale': False}
        
    def finished_move(self):
        return self.end_timer == 0 and not (self.moving or self.scaling)
        
    def set_target_rect(self, target_rect, p=None, v=5, startup_timer=0, end_timer=0, scale=False):
        self.target_rect = target_rect
        
        if p is not None:
            self.rect.center = p
            
        p0 = vec(self.rect.centerx, self.rect.centery)
        p1 = vec(target_rect.centerx, target_rect.centery)
        length = p0.distance_to(p1)
        
        if length == 0:
            vel = vec(0, 0)
        else:
            vel = (p1 - p0).normalize() * v

        self.vel = vel
        self.pos = p0
        self.moving = True
        
        if scale:
            frames = length / v
            
            s1 = vec(target_rect.width, target_rect.height)
            s0 = vec(self.rect.width, self.rect.height)
            
            scale_vel = (s1 - s0) / frames
        
            self.scale_vel = scale_vel
            self.scaling = True

        self.startup_timer = startup_timer
        self.end_timer = end_timer
        
        self.movement_cache['v'] = v
        self.movement_cache['startup_timer'] = startup_timer
        self.movement_cache['end_timer'] = end_timer
        self.movement_cache['scale'] = scale
        
        self.last_pos = self.target_rect.center
        
    def cancel(self):
        self.stop_move()
        self.stop_scale()
        self.startup_timer = 0
        self.end_timer = 0
        
    def set_sequence(self, movement_sequence, start=False):
        self.movement_sequence = movement_sequence 
        if start:
            self.start_next_sequence()
        
    def start_next_sequence(self):
        info = self.movement_sequence.pop(0)
        target_rect = info.pop('target')
        self.set_target_rect(target_rect, **info)

    def move(self):
        if not self.finished_move():
        
            p = self.target_rect.center
            if self.last_pos != p:
                self.set_target_rect(self.target_rect, **self.cache)
            self.last_pos = p
            
        if self.startup_timer > 0:
            self.startup_timer -= 1

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
            
            if self.end_timer > 0:
                self.end_timer -= 1
                
        if self.finished_move() and self.movement_sequence:
            self.start_next_sequence()
            
    def done_moving(self):
        x_done = False
        y_done = False
        
        if self.vel.x > 0:
            x_done = self.rect.centerx >= self.target_rect.centerx
        elif self.vel.x < 0:
            x_done = self.rect.centerx <= self.target_rect.centerx
        else:
            x_done = True
            
        if self.vel.y > 0:
            y_done = self.rect.centery >= self.target_rect.centery
        elif self.vel.y < 0:
            y_done = self.rect.centery <= self.target_rect.centery
        else:
            y_done = True
            
        return x_done and y_done
            
    def done_scaling(self):
        w_done = False
        h_done = False
        
        if self.scale_vel.x > 0:
            if self.rect.width >= self.target_rect.width:
                w_done = True
        elif self.scale_vel.x < 0:
            if self.rect.width <= self.target_rect.width:
                w_done = True
        else:
            w_done = True
            
        if self.scale_vel.y > 0:
            if self.rect.height >= self.target_rect.height:
                h_done = True
        elif self.scale_vel.y < 0:
            if self.rect.height <= self.target_rect.height:
                h_done = True
        else:
            h_done = True
            
        return w_done and h_done
     
    def stop_move(self):
        self.rect.center = self.target_rect.center
        self.vel *= 0
        self.moving = False
        
    def stop_scale(self):
        c = self.rect.center
        self.rect.size = self.target_rect.size
        if not self.moving:
            self.rect.center = self.target_rect.center
        else:
            self.rect.center = c
        
        self.scale = vec(self.rect.width, self.rect.height)
        self.scale_vel *= 0
        self.scaling = False

    def reset_timer(self):
        self.end_timer = self.cache['end_timer']
        
    def get_scale(self):
        w = max({int(self.scale.x), 0})
        h = max({int(self.scale.y), 0})
        return (w, h)
       
class Draw_Lines:
    def __init__(self, points, color=(0, 0, 0), width=3):
        self.points = points
        self.color = color
        self.width = width
        
    def set_color(self, color):
        self.color = color
        
    def set_points(self, points):
        self.points = points
        
    def draw(self, surf):
        pg.draw.lines(surf, self.color, False, self.points, width=self.width)

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
        
    def draw(self, surf):
        self.rs.draw(surf)

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
                
    def draw(self, surf):
        if self.anchor:
            points = (self.rect.topleft, self.rect.bottomleft, self.rect.bottomright, self.rect.topright)
            pg.draw.lines(surf, self.color, True, points, self.rad)

class Image_Manager:
    def get_surface(size, color=(0, 0, 0), width=1, olcolor=None, **border_kwargs):
        s = pg.Surface(size).convert()
        r = s.get_rect()
        if border_kwargs:
            s.fill((0, 0, 1))
            s.set_colorkey((0, 0, 1))
            pg.draw.rect(s, color, r, **border_kwargs)
        else:
            s.fill(color)
        if olcolor:
            pg.draw.rect(s, olcolor, r, width=width, **border_kwargs)
        return s

    def rect_outline(img, color=(0, 0, 0), width=2):
        ol = img.copy()
        ol.fill(color)
        w, h = img.get_size()
        img = pg.transform.smoothscale(img, (w - (width * 2), h - (width * 2)))
        ol.blit(img, (width, width))
        return ol
        
    def get_arrow(dir, size, padding=(0, 0), color=(255, 255, 255), bgcolor=(0, 0, 0, 0)):
        s = pg.Surface(size).convert_alpha()
        s.fill(bgcolor)
        w, h = size
        top = (w // 2, padding[1] // 2)
        bottomleft = (padding[0] // 2, h - (padding[1] // 2))
        bottomright = (w - (padding[0] // 2), h - (padding[1] // 2))
        pg.draw.polygon(s, color, (top, bottomleft, bottomright))
        
        a = 0
        if dir == 'd':
            a = 180
        elif dir == 'l':
            a = 90
        elif dir == 'r':
            a = -90
        if a:
            s = pg.transform.rotate(s, a)
            
        return s
     
class Base_Loop:
    LAST_EVENT_BATCH = []
    
    @classmethod
    def get_events(cls):
        event_batch = pg.event.get()
        cls.LAST_EVENT_BATCH = event_batch
        
        events = {}
        events['p'] = pg.mouse.get_pos()
        for e in event_batch:
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
        
    def __init__(self, objects, fps=30):
        self.running = False
        self.window = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = fps
        self.objects = objects

    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, object):
        if object in self.objects:
            self.objects.remove(object)

    def events(self):
        hit = False
        events = Base_Loop.get_events()
        p = events.get('p')
        
        if events.get('q'):
            self.quit()
            return
            
        for o in self.objects:
            if o.enabled:
                o.events(events)
                if not hit:
                    hit = o.set_cursor()
        if not hit:
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                            
 
    def update(self):
        for o in self.objects:
            o.update()

    def draw(self):
        self.window.fill((0, 0, 0))
        for o in self.objects:
            if o.visible:
                o.draw(self.window)
        pg.display.flip()
        
    def quit(self):
        self.running = False
                
    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self.events()
            if not self.running:
                break
            self.update()
            self.draw()

class Menu(Base_Loop):
    @staticmethod
    def get_window_objects(message='', color1=(100, 100, 100), color2=(50, 50, 50), olcolor=(255, 255, 255)):
        objects = []
        
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
        objects.append(i)
        
        body.center = (WIDTH // 2, HEIGHT // 2)
        upper.topleft = body.topleft
        text_rect.center = upper.center
        lower.bottomleft = body.bottomleft
        
        if message:
            t = Textbox(message, olcolor=(0, 0, 0))
            t.fit_text(text_rect, tsize=25)
            t.rect.center = text_rect.center
            t.set_parent(i.rect, anchor_point='center', current_offset=True)
            objects.append(t)
            
        return (objects, (upper, lower))

    @classmethod
    def notice(cls, message, overlay=False, bcolor=(0, 200, 0), **kwargs):
        objects, (_, lower) = Menu.get_window_objects(message=message, **kwargs)
        
        b = Button.text_button('ok', size=(150, 25), tsize=25, color2=bcolor)
        b.set_tag('break')
        b.rect.center = lower.center
        b.set_parent(objects[0].rect, anchor_point='center', current_offset=True)
        objects.append(b)
        
        return cls(objects=objects, overlay=overlay)

    @classmethod
    def yes_no(cls, message, overlay=False, yes_btn_color=(0, 200, 0), no_btn_color=(200, 0, 0), **kwargs):
        objects, (_, lower) = Menu.get_window_objects(message=message, **kwargs)

        b = Button.text_button('yes', size=(100, 30), tsize=25, color2=yes_btn_color, func=lambda: True)
        b.set_tag('return')
        b.rect.midleft = lower.midleft
        b.rect.x += 20
        b.set_parent(objects[0].rect, anchor_point='center', current_offset=True)
        objects.append(b)
        
        b = Button.text_button('no', size=(100, 30), tsize=25, color2=no_btn_color, func=lambda: False)
        b.set_tag('return')
        b.rect.midright = lower.midright
        b.rect.x -= 20
        b.set_parent(objects[0].rect, anchor_point='center', current_offset=True)
        objects.append(b)

        return cls(objects=objects, overlay=overlay)

    @classmethod
    def loading_screen(cls, func, fargs=[], fkwargs={}, overlay=False, **kwargs):
        objects, (_, lower) = Menu.get_window_objects(**kwargs)

        li = LoadingIcon()
        li.rect.topright = objects[0].rect.topright
        li.rect.top += 10
        li.rect.right -= 10
        li.set_parent(objects[0].rect, anchor_point='center', current_offset=True)
        objects.append(li)
        
        o = Base_Object(func=func, args=fargs, kwargs=fkwargs)
        o.set_tag('return')
        objects.append(o)

        return cls(objects=objects, overlay=overlay)

    @classmethod
    def timed_message(cls, message, timer, overlay=False, **kwargs):
        objects, _ = Menu.get_window_objects(message=message, **kwargs)
        
        t = Timer(timer, func=lambda: 1)
        t.set_tag('return')
        objects.append(t)
        
        return cls(objects=objects, overlay=overlay)

    @classmethod
    def make_and_run(cls, get_objects, *args, overlay=False, **kwargs):
        menu = cls(get_objects=get_objects, args=args, kwargs=kwargs, overlay=overlay)
        menu.run()
        
    @classmethod
    def make_and_run_obj(cls, objects, *args, overlay=False, **kwargs):
        menu = cls(objects=objects, args=args, kwargs=kwargs, overlay=overlay)
        menu.run()

    def __init__(self, get_objects=None, objects=[], args=[], kwargs={}, overlay=False):
        if get_objects:
            objects = get_objects(*args, **kwargs)
        super().__init__(objects, fps=60)
        
        self.get_objects = get_objects
        self.args = args
        self.kwargs = kwargs
        self.return_val = None

        self.background = None
        if overlay:
            s = self.window.copy()
            o = pg.Surface(s.get_size()).convert_alpha()
            o.fill((0, 0, 0, 180))
            s.blit(o, (0, 0))
            self.background = s

        self.set_funcs()
        
    def set_funcs(self):
        for o in self.objects:
            if o.tag == 'break':
                if o.func:
                    quit_func = self.wrap_quit_function(o)
                else:
                    quit_func = self.quit
                o.set_func(quit_func)
            elif o.tag == 'return':
                return_func = self.wrap_return_function(o)
                o.set_func(return_func)
            elif o.tag == 'refresh':
                refresh_func = self.wrap_refresh_function(o)
                o.set_func(refresh_func)
                
    def wrap_quit_function(self, o):
        f = o.func
        def quit_func(*args, **kwargs):
            f(*args, **kwargs)
            self.quit()
        return quit_func
                
    def wrap_return_function(self, o):
        f = o.func
        def return_func(*args, **kwargs):
            val = f(*args, **kwargs)
            o.return_val = val
            self.set_return(val)
        return return_func
        
    def wrap_refresh_function(self, o):
        f = o.func
        def refresh_func(*args, **kwargs):
            f(*args, **kwargs)
            self.refresh()
        return refresh_func
        
    def refresh(self):
        self.objects = self.get_objects(*self.args, **self.kwargs)
        self.set_funcs()
                
    def set_return(self, val):
        self.return_val = val
        
    def get_return(self):
        r = self.return_val
        self.return_val = None
        return r
        
    def exit(self):
        pg.quit()
        sys.exit()
        
    def events(self):
        hit = False
        events = self.get_events()
        if events.get('q'):
            self.exit()
        e = events.get('kd')
        if e:
            if e.key == pg.K_ESCAPE:
                self.exit()
                    
        for o in self.objects:
            if o.enabled:
                o.events(events)
                if not hit:
                    hit = o.set_cursor()
        if not hit:
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
  
    def draw(self):
        self.window.fill((0, 0, 0))
        if self.background:
            self.window.blit(self.background, (0, 0))
        for o in self.objects:
            if o.visible:
                o.draw(self.window)
        pg.display.flip()
          
    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self.events()
            if not self.running:
                break
            self.update()
            if self.return_val is not None:
                return self.return_val
            self.draw()

class Base_Object:    
    def __init__(self, func=None, args=[], kwargs={}, tag=None, **okwargs):
        if tag is None:
            tag = str(id(self))
        self.tag = tag
        self.visible = True
        self.enabled = True
        self.hit = False

        self.enable_func = bool(func)
        if func:
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.return_val = None
            
        for name, value in okwargs.items():
            setattr(self, name, value)
        
    def set_tag(self, tag):
        self.tag = tag
        
    def get_tag(self):
        return self.tag
        
    def set_visible(self, visible):
        self.visible = visible
        
    def set_enabled(self, enabled):
        self.enabled = enabled
        
    def hit_mouse(self):
        if hasattr(self, 'rect'):
            return self.rect.collidepoint(pg.mouse.get_pos())
        
    def set_func(self, func, args=None, kwargs=None):    
        self.func = func
        if args is not None:
            self.args = args
        elif not self.enable_func:
            self.args = []
        if kwargs is not None:
            self.kwargs = kwargs
        elif not self.enable_func:
            self.kwargs = {}
        self.enable_func = True

    def get_return(self):
        r = self.return_val
        self.return_val = None
        return r
        
    def set_cursor(self):
        pass
        
    def events(self, events):
        pass
        
    def update(self):
        if self.enable_func:
            r = self.func(*self.args, **self.kwargs)
            if r is not None:
                self.return_val = r
        
    def draw(self, surf):
        pass

class Position:
    @staticmethod
    def center_objects_y(objects, rect=None, padding=10):
        objects = [o for o in objects if hasattr(o, 'rect')]
        r = pg.Rect(0, 0, 0, 0)
        for o in objects:
            r.height += o.rect.height + padding
        if rect:
            r.centery = rect.centery
        else:
            r.centery = HEIGHT // 2
        y = r.top + padding
        for o in objects:
            o.rect.top = y
            y += o.rect.height + padding
            
    @staticmethod
    def center_objects_x(objects, rect=None, padding=10):
        objects = [o for o in objects if hasattr(o, 'rect')]
        r = pg.Rect(0, 0, 0, 0)
        for o in objects:
            r.width += o.rect.width + padding
        if rect:
            r.centerx = rect.centerx
        else:
            r.centerx = WIDTH // 2
        x = r.left + padding
        for o in objects:
            o.rect.left = x
            x += o.rect.width + padding
        
    @classmethod
    def center_objects(cls, objects, rect=None, padding=(10, 10)):
        cls.center_objects_y(objects, rect=rect, padding=padding[0])
        cls.center_objects_x(objects, rect=rect, padding=padding[1])
        
    def __init__(self, rect=None, parent_rect=None, offset=None, anchor_point='topleft', children=None, contain=False):
        if rect:
            self.rect = rect
        self.parent_rect = parent_rect
        if offset is None:
            offset = [0, 0]
        self.offset = offset
        self.anchor_point = anchor_point

        if children is None:
            children = []
        self.children = children
        
        self.contain = contain

    def set_children(self, children):
        self.children = children
        
    def add_children(self, children):
        self.children += children
        
    def add_child(self, child):
        self.children.append(child)
        
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            
    def clear_children(self):
        self.set_children([])

    def get_children(self):
        return self.children

    def set_parent(self, parent_rect, offset=None, anchor_point='topleft', contain=False, current_offset=False):
        self.parent_rect = parent_rect
        self.anchor_point = anchor_point
        if offset is None:
            if current_offset:
                offset = self.get_current_offset()
            else:
                offset = [0, 0]
        self.offset = offset
        self.contain = contain
        self.update_position()

    def set_anchor(self, anchor_point, offset=None):
        self.anchor_point = anchor_point
        if offset is None:
            offset = [0, 0]
        self.offset = offset

    def get_relative_position(self):
        self.update_position()
        return [self.rect.x - self.parent_rect.x, self.rect.y - self.parent_rect.y]
        
    def set_to_relative(self):
        self.rect.topleft = self.get_relative_position()
        
    def freeze(self):
        self.offset = self.get_relative_position()
        self.anchor_point = 'topleft'
        
    def get_offset(self):
        return self.offset.copy()
                
    def adjust_offset(self, dx, dy):
        self.offset[0] += dx
        self.offset[1] += dy
        if self.contain:
            self.set_contain()
            
    def set_current_offset(self):
        sx, sy = getattr(self.rect, self.anchor_point)
        px, py = getattr(self.parent_rect, self.anchor_point)
        self.offset[0] = sx - px
        self.offset[1] = sy - py
        if self.contain:
            self.set_contain()
            
    def get_current_offset(self):
        sx, sy = getattr(self.rect, self.anchor_point)
        px, py = getattr(self.parent_rect, self.anchor_point)
        return (sx - px, sy - py)
            
    def set_y_offset(self, dy):
        self.offset[1] = dy
        
    def set_x_offset(self, dx):
        self.offset[0] = dx
        
    def set_offset(self, dx, dy):
        self.offset = [dx, dy]
        
    def set_contain(self):
        setattr(self.rect, self.anchor_point, getattr(self.parent_rect, self.anchor_point))
        self.rect.x += self.offset[0]
        self.rect.y += self.offset[1]
        ax, ay = self.adjust_limits()
        self.offset[0] += ax
        self.offset[1] += ay

    def adjust_limits(self):
        x0, y0 = self.rect.topleft
        if self.rect.top < self.parent_rect.top:
            self.rect.top = self.parent_rect.top
        elif self.rect.bottom > self.parent_rect.bottom:
            self.rect.bottom = self.parent_rect.bottom
        if self.rect.left < self.parent_rect.left:
            self.rect.left = self.parent_rect.left
        elif self.rect.right > self.parent_rect.right:
            self.rect.right = self.parent_rect.right
        return (self.rect.x - x0, self.rect.y - y0)

    def update_position(self, all=False):
        if self.parent_rect:
            setattr(self.rect, self.anchor_point, getattr(self.parent_rect, self.anchor_point))
            self.rect.x += self.offset[0]
            self.rect.y += self.offset[1]
            if self.contain:
                self.adjust_limits()
        if all:
            self.update_children()
                
    def update_children(self):
        for c in self.get_children():
            c.update_position()
            c.update_children()
            
    def draw_on(self, surf, rect):
        dx, dy = rect.topleft
        self.rect.move_ip(-dx, -dy)
        self.update_children()
        self.draw(surf)
        self.rect.move_ip(dx, dy)
        self.update_children()

class Timer(Base_Object):
    def __init__(self, start_time, *base_args, reset_timer=False, **base_kwargs):
        self.start_time = start_time
        self.timer = start_time
        self.reset_timer = reset_timer
        super().__init__(*base_args, **base_kwargs)
        
    def reset(self):
        self.timer = self.start_time
        
    def update(self):
        if self.timer:
            self.timer -= 1
            if not self.timer:
                super().update()
                if self.reset_timer:
                    self.reset()

class On_Click(Base_Object):
    def __init__(self, func, *base_args, button=1, **base_kwargs):
        super().__init__(*base_args, func=func, **base_kwargs)
        self.button = button
        
    def events(self, events):
        e = events.get('mbd')
        if e:
            if e.button == self.button:
                self.func(*self.args, **self.kwargs)
                
    def update(self):
        pass

class Image(Base_Object, Position): 
    @classmethod
    def from_style(cls, *args, **kwargs):
        img = Image_Manager(*args, **kwargs)
        return cls(img)
        
    def __init__(self, image, bgcolor=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.bgcolor = bgcolor
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
    def set_background(self, color):
        self.bgcolor = color
        
    def clear_background(self):
        self.bgcolor = None
        
    def scale(self, size):
        self.image = pg.transform.smoothscale(self.image, size)
        self.rect.size = size
        
    def update(self):
        self.update_position()
        
    def draw(self, surf):
        if self.bgcolor is not None:
            pg.draw.rect(surf, self.bgcolor, self.rect)
        surf.blit(self.image, self.rect)

class Textbox(Base_Object, Position):
    pg.freetype.init()
    _FONT = 'arial.ttf'
    FONT = pg.freetype.Font(_FONT)
    FONT.pad = True
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
    def render_text(cls, message, tsize=20, fgcolor=(255, 255, 255), bgcolor=None):
        image, _ = cls.FONT.render(message, fgcolor=fgcolor, bgcolor=bgcolor, size=tsize)
        return image
        
    @classmethod
    def render_text_to(cls, surf, *args, pos=(0, 0), **kwargs):
        image = cls.render_text(*args, **kwargs)
        surf.blit(image, pos)
            
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
    
    @classmethod
    def static_textbox(cls, *args, **kwargs):
        image = cls.render_text(*args, **kwargs)
        i = Image(image)
        return i
    
    def __init__(self, message, tsize=10, fgcolor=(255, 255, 255), bgcolor=None, olcolor=None, width=2, anchor='center', fitted=False, font=None):
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
        self.font.pad = True
        
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

        Base_Object.__init__(self)
        Position.__init__(self)
        
        if self.fitted:
            self.set_fitted(True)

    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message
        
    def __eq__(self, other):
        return self.message == other.message and self.fgcolor == other.fgcolor 
        
    def set_visible(self, visible):
        self.visible = visible
   
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
            
    def update_position(self):
        super().update_position()
        self.move_characters()
        
    def update(self):
        self.update_position()        
        super().update()
    
    def draw(self, surf):
        surf.blit(self.image, self.rect)

class Button(Base_Object, Position):
    @classmethod
    def text_button(cls, message, size=None, padding=(0, 0), center_offset=(0, 0), tsize=20, text_kwargs={}, **kwargs):
        t = Textbox(message, tsize=tsize, **text_kwargs)
        b = cls(**kwargs)
        b.join_object(t, size=size, padding=padding, center_offset=center_offset)
        return b
        
    @classmethod
    def image_button(cls, image, size=None, color1=(0, 0, 0, 0), border_radius=0, padding=(0, 0), center_offset=(0, 0), **kwargs):
        i = Image(image)
        b = cls(color1=color1, border_radius=border_radius, **kwargs)
        b.join_object(i, size=size, padding=padding, center_offset=center_offset)
        return b

    def __init__(self, size=None, color1=(0, 0, 0), color2=(100, 100, 100), border_radius=5, func=lambda *args, **kwargs: None, args=[], kwargs={}, tag=None):
        self.size = size
        if not size:
            size = (0, 0)
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.padding = (0, 0)
        self.object = None

        self.color1 = color1
        self.color2 = color2
        self.current_color = color1
        self.border_radius = border_radius

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.return_val = None

        self.active = False
        self.pressed = False
        self.update_object = True
        
        Base_Object.__init__(self, tag=tag)
        Position.__init__(self)
        
    def get_state(self):
        return self.pressed
        
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

    def clear_args(self):
        self.set_args(args=[], kwargs={})
        
    def get_return(self, reset=True):
        r = self.return_val
        if reset:
            self.return_val = None
        return r
        
    def join_object(self, object, size=None, padding=(0, 0), center_offset=(0, 0), update_object=True):
        if size is None:
            size = object.rect.size
        w, h = size
        if any(padding):
            w += (2 * padding[0])
            h += (2 * padding[1])
        if any(center_offset):
            w += (2 * abs(center_offset[0]))
            h += (2 * abs(center_offset[1]))
        self.size = (w, h)
        self.padding = padding
        
        c = self.rect.center
        self.rect.size = self.size
        self.rect.center = c

        self.object = object
        object.set_parent(self.rect, anchor_point='center', offset=center_offset)
        self.set_children([object])
        self.update_object = update_object
        
    def get_object(self):
        return self.object
        
    def set_cursor(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True

    def click_down(self):
        if self.active:
            self.pressed = True
            self.return_val = self.func(*self.args, **self.kwargs)

    def events(self, events):
        p = events['p']
        if self.rect.collidepoint(p):
            self.active = True  
        else:  
            self.active = False

        mbd = events.get('mbd')
        mbu = events.get('mbu')
        if mbd:
            if mbd.button == 1:
                self.click_down()  
        elif mbu:
            if mbu.button == 1:
                self.pressed = False
                
        if self.object and self.update_object:
            self.object.events(events)
            
    def update(self):
        self.update_position()
        if self.active and self.current_color != self.color2:
            self.current_color = self.color2       
        elif not self.active and self.current_color != self.color1:
            self.current_color = self.color1  
        
        if self.object and self.update_object:
            self.object.update()
  
    def draw(self, surf):
        if self.current_color != (0, 0, 0, 0):
            pg.draw.rect(surf, self.current_color, self.rect, border_radius=self.border_radius)
        if self.object and self.update_object:
            self.object.draw(surf)

class Input(Base_Object, Position):
    VALID_CHARS = set(range(32, 127))
    VALID_CHARS.add(9)
    VALID_CHARS.add(10)
    
    TK = Tk()
    
    @classmethod
    def copy_to_clipboard(cls, text):
        cls.TK.clipboard_clear()
        cls.TK.clipboard_append(text.strip())
        
    @classmethod
    def get_clip(cls):
        try:
            text = cls.TK.clipboard_get().strip()  
        except:
            text = '' 
        return text
        
    @classmethod
    def get_renderable_chars(cls):
        return [chr(i) for i in cls.VALID_CHARS]
        
    @staticmethod
    def positive_int_check(char):
        return char.isnumeric()
        
    @classmethod
    def input_from_image(cls, image, padding=(5, 5), **kwargs):
        size = image.get_size()
        input = cls(size, **kwargs)
        input.image = image
        input.padding = padding
        return input

    def __init__(self, size, message='type here', tsize=20, padding=(5, 5), color=(0, 0, 0, 0), length=99, check=lambda char: True, fitted=False, scroll=False, allignment='c', **kwargs):      
        self.textbox = Textbox(message, tsize=tsize, fitted=fitted, **kwargs)

        w, h = size
        w = size[0] + (2 * padding[0])
        if not fitted: 
            h = self.textbox.rect.height + (2 * padding[1])
        else:
            h = size[1] + (2 * padding[1])
        self.base_image = pg.Surface((w, h)).convert_alpha()
        self.image = None
        self.padding = padding
 
        self.color = color
        self.base_image.fill(color)
        self.rect = self.base_image.get_rect()

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
        
        self.text_rect = self.rect.inflate(-padding[0], -padding[1])
        self.update_message(self.textbox.get_message())
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
        if not self.fitted:
            anchor = 'topleft'
            offset = list(padding)
        else:
            anchor = 'center'
            offset = [0, 0]
        self.textbox.set_parent(self.rect, anchor_point=anchor, offset=offset)
        self.add_child(self.textbox)
     
    def get_chars(self):
        return self.textbox.characters

    def get_message(self):
        return self.textbox.get_message()

    def update_message(self, message):
        if self.check_message(message):
            self.textbox.set_message(message)
            if self.fitted:
                self.textbox.fit_text(self.text_rect, tsize=self.tsize, allignment=self.allignment)

    def check_message(self, text):
        return all({ord(char) in Input.VALID_CHARS and self.check(char) for char in text})

    def set_index(self, index):
        index = max({index, 0})
        index = min({index, len(self.get_message())})
        self.index = index
              
    def highlight_word(self):
        i = j = self.index
        m = self.get_message()
        
        if i not in range(len(m)):
            i -= 1

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
        i = min(range(len(chars)), key=lambda i: vec(chars[i][1].center).distance_to(p), default=0)
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
                self.textbox.rect.x += self.padding[0]
                self.textbox.set_current_offset()
  
    def send_keys(self, text):
        if self.selection:
            self.replace_selection('')
        m = self.get_message()
        message = m[:self.index] + text + m[self.index:]
        self.update_message(message)
        self.set_index(self.index + len(text))

    def shift_textbox(self):
        if self.textbox.rect.width + self.padding[0] < self.rect.width:
            self.textbox.rect.midleft = self.rect.midleft
            self.textbox.rect.x += self.padding[0]
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
                    self.textbox.rect.right = self.rect.right - self.padding[0]
        self.textbox.set_current_offset()
        
    def set_cursor(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            return True
                    
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
            
        self.update_position()
        
        if self.scroll and self.active:
            self.shift_textbox()

        self.textbox.update()
        
    def draw(self, surf):
        x0, y0 = self.rect.topleft
        dx = -x0
        dy = -y0

        if not self.image:
            self.base_image.fill(self.color)
        else:
            self.base_image.blit(self.image, (0, 0))

        if self.selection:
            chars = self.get_chars()[:-1]
            i, j = self.selection
            for _, r, _ in chars[min(i, j):max(i, j)]:
                pg.draw.rect(self.base_image, (0, 102, 255), r.move(dx, dy))

        self.base_image.blit(self.textbox.image, self.textbox.rect.move(dx, dy))
        
        if self.active and self.timer > 0:
            chars = self.get_chars()
            if chars:
                if self.index in range(len(chars)):
                    r = chars[self.index][1].move(dx, dy)
                    pg.draw.line(self.base_image, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
            else:
                r = self.textbox.get_text_rect(' ', tsize=self.tsize)
                if self.fitted:
                    r.center = self.rect.center
                    r.move_ip(dx, dy)
                    pg.draw.line(self.base_image, self.textbox.fgcolor, r.midtop, r.midbottom, width=2)
                else:
                    r.midleft = self.rect.midleft
                    r.move_ip(dx, dy)
                    pg.draw.line(self.base_image, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
                    
        surf.blit(self.base_image, self.rect)

class Flipper(Base_Object, Position):
    @classmethod
    def numeric_flipper(cls, ran, tsize=20, **kwargs):
        objects = []
        for i in ran:
            tb = Textbox.static_textbox(str(i), tsize=tsize)
            tb.set_tag(i)
            objects.append(tb)
        return cls(objects, **kwargs)
            
    def __init__(self, objects, index=0, size=None, color=(0, 0, 0, 0)):
        self.objects = objects
        self.index = index

        if size is None:
            w = max({o.rect.width for o in objects})
            h = max({o.rect.height for o in objects})
            size = (w, h)
        self.base_image = pg.Surface(size).convert_alpha()
        self.color = color
        self.base_image.fill(color)
        self.rect = self.base_image.get_rect()
        
        left_arrow = Image_Manager.get_arrow('l', (15, 15))
        right_arrow = pg.transform.rotate(left_arrow, 180)
        self.left_arrow = Button.image_button(left_arrow, func=self.flip, args=[-1])
        self.right_arrow = Button.image_button(right_arrow, func=self.flip, args=[1])
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
        self.left_arrow.set_parent(self.rect, anchor_point='midleft', offset=(-self.left_arrow.rect.width, 0))
        self.right_arrow.set_parent(self.rect, anchor_point='midright', offset=(self.right_arrow.rect.width, 0))
        
        for o in self.objects:
            o.set_parent(self.rect, anchor_point='center')
        
        self.set_children([self.left_arrow, self.right_arrow])
        
    def get_children(self):
        return self.children + self.objects

    def flip(self, dir):
        self.index = (self.index + dir) % len(self.objects)
        
    def get_current_option(self):
        return self.objects[self.index]
        
    def get_current_tag(self):
        return self.objects[self.index].tag
        
    def events(self, events):
        for o in self.children:
            o.events(events)
        self.objects[self.index].events(events)
            
    def update(self):
        self.update_position()
        for o in self.children:
            o.update()
        self.objects[self.index].update()
        
    def draw(self, surf):
        self.base_image.fill(self.color)
        self.right_arrow.draw(surf)
        self.left_arrow.draw(surf)
        self.objects[self.index].draw_on(self.base_image, rect=self.rect)
        surf.blit(self.base_image, self.rect)

class Scroll_Bar(Base_Object, Position):
    def __init__(self, height, total_height=0, width=16, extended_rect=None, color1=(255, 255, 255), color2=(100, 100, 100)):
        self.rect = pg.Rect(0, 0, width , height)
        self.body = Position(rect=pg.Rect(0, 0, width, height - (2 * width)), parent_rect=self.rect, anchor_point='center')
        self.handel = Position(rect=pg.Rect(0, 0, width - 4, 1), parent_rect=self.body.rect, anchor_point='midtop', contain=True)
        if not extended_rect:
            extended_rect = self.rect
        self.extended_rect = extended_rect
        
        self.image = pg.Surface(self.body.rect.size).convert()
        self.image.fill(color1)
        
        self.rel_pos = None
        self.last_pos = self.rect.top

        up_arrow = Image_Manager.get_arrow('u', (width, width), padding=(6, 6), color=(100, 100, 100), bgcolor=(255, 255, 255))
        down_arrow = pg.transform.rotate(up_arrow, 180)

        self.up_button = Button.image_button(up_arrow, size=up_arrow.get_size(), border_radius=0, func=self.scroll, args=[-1])
        self.up_button.set_parent(self.rect, anchor_point='midtop')
        self.down_button = Button.image_button(down_arrow, size=down_arrow.get_size(), border_radius=0, func=self.scroll, args=[1])
        self.down_button.set_parent(self.rect, anchor_point='midbottom')
        
        self.color1 = color1
        self.color2 = color2

        self.height_ratio = 1
        self.set_height_ratio(1)
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
        self.set_children([self.body, self.handel, self.up_button, self.down_button])

    def is_held(self):
        return self.rel_pos is not None
        
    def is_full(self):
        return self.height_ratio == 1
        
    def set_height_ratio(self, r):
        top = self.handel.rect.top
        self.handel.rect.height = self.body.rect.height * r
        self.handel.rect.top = top
        self.height_ratio = r

    def get_scroll_ratio(self):
        return round((self.handel.rect.top - self.body.rect.top) / self.body.rect.height, 3)
        
    def can_scroll_down(self):
        return self.handel.rect.bottom < self.body.rect.bottom
        
    def can_scroll_up(self):
        return self.handel.rect.top > self.body.rect.top
        
    def scroll(self, dir):
        self.handel.adjust_offset(0, dir * max({self.handel.rect.height / 2, 1}))
        
    def go_to_bottom(self):
        while self.can_scroll_down():
            self.scroll(-1)
            
    def go_to_top(self):
        while self.can_scroll_up():
            self.scroll(1)
            
    def set_rel_pos(self, p):
        y0 = p[1]
        y1 = self.handel.rect.top
        dy = y1 - y0
        self.rel_pos = dy
        
    def set_cursor(self):
        set = False
        set = self.up_button.set_cursor()
        if not set:
            set = self.down_button.set_cursor()
            if not set:
                if self.handel.rect.collidepoint(pg.mouse.get_pos()):
                    pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    set = True
        return set
        
    def events(self, events):                
        self.up_button.events(events)
        self.down_button.events(events)
        
        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if mbd:
            if mbd.button == 1:   
                if self.handel.rect.collidepoint(p):
                    self.set_rel_pos(p)
                elif self.body.rect.collidepoint(p):
                    self.set_rel_pos(self.handel.rect.center)
            elif self.rect.collidepoint(p) or self.extended_rect.collidepoint(p):
                if mbd.button == 4:
                    self.scroll(-1)
                elif mbd.button == 5:
                    self.scroll(1)
        elif mbu:
            self.rel_pos = None
            self.handel.freeze()
                
    def update(self):
        self.update_position()
        self.body.update_position()
        
        if self.rel_pos is not None:
            y = pg.mouse.get_pos()[1]
            self.handel.rect.top = y + self.rel_pos
            self.handel.set_current_offset()
        else:
            self.handel.update_position()

        self.up_button.update()
        self.down_button.update()
        
        full = self.is_full()
        self.set_visible(not full)
        self.set_enabled(not full)

    def draw(self, surf):
        surf.blit(self.image, self.body)
        pg.draw.rect(surf, self.color2, self.handel.rect)
        self.up_button.draw(surf)
        self.down_button.draw(surf)

class Pane_Base(Base_Object, Position):
    @classmethod
    def pane_from_image(cls, image, **kwargs):
        size = image.get_size()
        pane = cls(size, **kwargs)
        image = pg.transform.smoothscale(image, pane.base_image.get_size())
        pane.image = image
        return pane
        
    def __init__(self, size, color=(0, 0, 0, 0), label='', label_height=20, label_color=(0, 0, 0), hide_label=False, **text_kwargs):
        self.size = size
        self.base_image = pg.Surface(size).convert_alpha()
        self.color = color
        self.image = None
        self.base_image.fill(color)
        self.rect = self.base_image.get_rect()

        self.label = Textbox(label, **text_kwargs)
        self.label.fit_text(pg.Rect(0, 0, self.rect.width, label_height), tsize=label_height)
        label_rect = self.label.rect.copy()

        self.label_color = label_color
        self.hide_label = hide_label

        self.scroll_bar = Scroll_Bar(self.rect.height, extended_rect=self.rect)
        self.last_offset = -1
        
        self.objects = []

        self.orientation_cache = {'xpad': 5, 'ypad': 5, 'dir': 'y', 'pack': False}
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
        self.bounding_rect = Position(rect=self.rect.copy(), parent_rect=self.rect, anchor_point='centerx')
        self.label_rect = Position(rect=label_rect, parent_rect=self.rect, offset=[0, -label_rect.height])
        self.label.set_parent(label_rect, anchor_point='center')
        self.scroll_bar.set_parent(self.rect, anchor_point='topright', offset=[self.scroll_bar.rect.width, 0])
        
        self.set_children([self.bounding_rect, self.scroll_bar, self.label_rect, self.label])

    def get_children(self):
        return self.children + self.objects
 
    def get_total_rect(self):
        return pg.Rect(self.rect.x, self.label_rect.rect.y, self.label_rect.rect.width, self.rect.height + self.label_rect.rect.height)
  
    def is_same(self, objects):
        if len(objects) == len(self.objects):
            return all({objects[i] == self.objects[i] for i in range(len(objects))})
        else:
            return False
            
    def get_visible(self):
        return [o for o in self.objects if self.rect.colliderect(o.rect)]
        
    def sort_objects(self, key):
        objects = sorted(self.objects, key=key)
        self.join_objects(objects, **self.orientation_cache)
    
    def clear(self):
        self.join_objects([])
        self.image.fill(self.color)
    
    def join_objects(self, objects, xpad=5, ypad=5, dir='y', pack=False, force=False, scroll=False, move=False):
        same = self.is_same(objects)

        if not same or force:
            x = 0
            y = 0
            
            if dir == 'y':   
                for o in objects:
                    if pack:
                        if self.rect.y + y + ypad + o.rect.height > self.rect.bottom:
                            x += o.rect.width + xpad
                            y = 0 
                        offset = [x + xpad, y + ypad]
                        o.set_parent(self.bounding_rect.rect, offset=offset)   
                    else:
                        offset = [0, y + ypad]  
                        o.set_parent(self.bounding_rect.rect, anchor_point='midtop', offset=offset)
                    y += o.rect.height + ypad
                    
            elif dir == 'x':
                for o in objects:
                    if pack:
                        if self.rect.x + x + xpad + o.rect.width > self.rect.right:
                            x = 0
                            y += o.rect.height + ypad  
                        offset = [x + xpad, y + ypad]
                        o.set_parent(self.bounding_rect.rect, offset=offset)    
                    else:
                        offset = [x + xpad, 0]  
                        o.set_parent(self.bounding_rect.rect, anchor_point='midleft', offset=offset)  
                    x += o.rect.width + xpad
                    
            self.objects = objects.copy()
            self.orientation_cache = {'xpad': xpad, 'ypad': ypad, 'dir': dir, 'pack': pack}
            self.set_total_height()
                
        elif same and move:
            for i in range(len(self.objects)):
                objects[i].offset = self.objects[i].get_offset()

    def set_total_height(self):
        h = self.rect.height
        if self.objects: 
            ymin = min({o.rect.top for o in self.objects})
            ymax = max({o.rect.bottom for o in self.objects})
            pad = 2 * self.orientation_cache['ypad']
            h = max({(ymax - ymin) + pad, h})
            
        r = self.rect.height / h 
        self.scroll_bar.set_height_ratio(r)
        
        self.bounding_rect.rect.height = h
        r = self.scroll_bar.get_scroll_ratio()
        self.set_window(r)
        
    def update_window(self):
        current_offset = self.scroll_bar.get_scroll_ratio()
        if current_offset != self.last_offset:
            self.set_window(current_offset)
            self.last_offset = current_offset
                
    def set_window(self, r):
        top = self.bounding_rect.rect.top
        self.bounding_rect.rect.top = self.rect.top - (self.bounding_rect.rect.height * r)
        self.bounding_rect.adjust_offset(0, self.bounding_rect.rect.top - top)
        self.bounding_rect.freeze()
        
        if self.image is None:
            self.base_image.fill(self.color)
        else:
            self.base_image.blit(self.image, (0, 0))
        for o in self.objects: 
            o.update_position()
            if o.rect.colliderect(self.rect):
                o.draw_on(self.base_image, self.rect)
                
    def set_cursor(self):
        return self.scroll_bar.set_cursor()

    def events(self, events):
        self.scroll_bar.events(events)
                        
    def update(self):
        self.update_position()
        self.bounding_rect.update_position()
        self.scroll_bar.update()
        self.update_window()
        
        if self.scroll_bar.is_full():
            self.label_rect.rect.width = self.rect.width
        else:
            self.label_rect.rect.width = self.rect.width + self.scroll_bar.rect.width
        self.label_rect.update_position()
        self.label.update()
        
    def draw_label(self, surf):
        pg.draw.rect(surf, self.label_color, self.label_rect.rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(surf)

    def draw(self, surf):
        if self.color != (0, 0, 0, 0) or self.objects or self.image:
            surf.blit(self.base_image, self.rect)
        if not self.hide_label:
            pg.draw.rect(surf, self.label_color, self.label_rect.rect, border_top_left_radius=10, border_top_right_radius=10)
            self.label.draw(surf)
        if not self.scroll_bar.visible:
            self.scroll_bar.draw(surf)
 
class Pane_Alt(Pane_Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        up_arrow = Image_Manager.get_arrow('u', (self.rect.width, 20), bgcolor=(0, 0, 0, 90), padding=(240, 14))
        down_arrow = pg.transform.rotate(up_arrow, 180)
        self.scroll_bar.up_button.join_object(Image(up_arrow))
        self.scroll_bar.down_button.join_object(Image(down_arrow))
        
        self.scroll_bar.up_button.set_parent(self.rect, anchor_point='topleft')
        self.scroll_bar.down_button.set_parent(self.rect, anchor_point='bottomleft')
        
        self.label.rect.width = self.rect.width
        
    def events(self, events):
        if not self.scroll_bar.is_full():
            self.scroll_bar.events(events)
                        
    def update(self):
        self.update_position()
        self.bounding_rect.update_position()
        self.scroll_bar.up_button.update()
        self.scroll_bar.down_button.update()
        self.update_window()

        self.label_rect.update_position()
        self.label.update()
        
    def draw_label(self, surf):
        pg.draw.rect(surf, self.label_color, self.label_rect.rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(surf)

    def draw(self, surf):
        if self.color != (0, 0, 0, 0) or self.objects or self.image:
            surf.blit(self.base_image, self.rect)
        if not self.hide_label:
            pg.draw.rect(surf, self.label_color, self.label_rect.rect, border_top_left_radius=10, border_top_right_radius=10)
            self.label.draw(surf)
        if self.scroll_bar.can_scroll_down():
            self.scroll_bar.down_button.draw(surf)
        if self.scroll_bar.can_scroll_up():
            self.scroll_bar.up_button.draw(surf)

class Semi_Live_Pane(Pane_Base):
    def set_window(self, r):
        top = self.bounding_rect.rect.top
        self.bounding_rect.rect.top = self.rect.top - (self.bounding_rect.rect.height * r)
        self.bounding_rect.adjust_offset(0, self.bounding_rect.rect.top - top)
        self.bounding_rect.freeze()

        for o in self.objects: 
            o.update_position()
            
    def join_objects(self, *args, **kwargs):
        super().join_objects(*args, **kwargs)
        for o in self.objects:
            o.set_visible(False)
            
    def set_cursor(self):
        return self.scroll_bar.set_cursor()
            
    def draw(self, surf):
        if not self.image:
            self.base_image.fill(self.color)
        else:
            self.base_image.blit(self.image, (0, 0))
        
        for o in self.objects:
            if o.rect.colliderect(self.rect):
                o.draw_on(self.base_image, self.rect)

        surf.blit(self.base_image, self.rect)
        pg.draw.rect(surf, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(surf)
        if self.scroll_bar.visible:
            self.scroll_bar.draw(surf)

class Live_Pane(Pane_Base):
    def set_window(self, r):
        top = self.bounding_rect.rect.top
        self.bounding_rect.rect.top = self.rect.top - (self.bounding_rect.rect.height * r)
        self.bounding_rect.adjust_offset(0, self.bounding_rect.rect.top - top)
        self.bounding_rect.freeze()

        for o in self.objects: 
            o.update_position()
            
    def events(self, events):
        self.scroll_bar.events(events)
        for o in self.objects:
            o.events(events)
            
    def update(self):
        super().update()
        for o in self.objects:
            o.update()
                    
    def draw(self, surf):
        if not self.image:
            self.base_image.fill(self.color)
        else:
            self.base_image.blit(self.image, (0, 0))
        
        for o in self.objects:
            if o.rect.colliderect(self.rect):
                o.draw_on(self.base_image, self.rect)

        surf.blit(self.base_image, self.rect)
        pg.draw.rect(surf, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)
        self.label.draw(surf)
        if not self.scroll_bar.is_full():
            self.scroll_bar.draw(surf)

class Popup_Base(Pane_Base, Mover):
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
                if self.label_rect.rect.collidepoint(p):
                    if self.timer < 10:
                        self.locked = not self.locked
                    self.timer = 0
        
        if self.get_total_rect().inflate(50, 0).collidepoint(p):
            if not self.t:
                t = self.get_target()
                self.t = t
                self.o = self.rect.copy()
            if self.target_rect != self.t:
                self.set_target_rect(self.t, v=15)
                
        elif not self.locked and not self.scroll_bar.is_held() and self.t:
            self.set_target_rect(self.o, v=15)
        
    def update(self):
        self.move()
        super().update()
        
        for o in self.objects: 
            o.update_position() 
        
        if self.timer < 15:
            self.timer += 1
        
        if self.finished_move():
            if self.target_rect == self.o:
                self.t = None
                self.o = None
            
    def draw(self, surf):
        if self.is_visible():
        
            surf.blit(self.base_image, self.rect)
            if not self.scroll_bar.is_full():
                self.scroll_bar.draw(surf)
                
            if self.locked: 
                color = tuple(max(rgb - 50, 0) for rgb in self.label_color)
                pg.draw.rect(surf, color, self.label_rect, width=5, border_top_left_radius=10, border_top_right_radius=10)

        pg.draw.rect(surf, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)  
        self.label.draw(surf)

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

    def events(self, events):
        p = events['p']
        mbd = events.get('mbd')
        
        if self.is_visible():
            self.scroll_bar.events(events)
            for o in self.objects:
                o.events(events)
                if o.rect.collidepoint(p):
                    break
        
        total_rect = self.get_total_rect()
        
        if mbd:
            if mbd.button == 1:
                if total_rect.collidepoint(p):
                    if self.timer < 10:
                        self.locked = not self.locked
                    self.timer = 0
        
        if total_rect.inflate(50, 0).collidepoint(p):
            if not self.t:
                t = self.get_target()
                self.t = t
                self.o = self.rect.copy()
            if self.target_rect != self.t:
                self.set_target_rect(self.t, v=15)
        elif not self.locked and not self.scroll_bar.is_held() and self.t:
            self.set_target_rect(self.o, v=15)
        
    def update(self):
        self.move()
        super().update()
        
        if self.timer < 15:
            self.timer += 1
        
        if self.target_rect == self.o and self.finished_move():
            self.t = None
            self.o = None
            
    def draw(self, surf):
        if self.is_visible():
            
            self.base_image.fill(self.color)
            
            for o in self.objects:
                if o.rect.colliderect(self.rect):
                    o.draw_on(self.base_image, self.rect)
        
            surf.blit(self.base_image, self.rect)
            if not self.scroll_bar.is_full():
                self.scroll_bar.draw(surf)
                
            if self.locked: 
                color = tuple(max({rgb - 50, 0}) for rgb in self.color)
                pg.draw.rect(surf, color, self.rect, width=5)

        pg.draw.rect(surf, self.label_color, self.label_rect, border_top_left_radius=10, border_top_right_radius=10)  
        self.label.draw(surf)

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
            b = Button.image_button(Sectioned_Slider.get_arrows(10), func=self.set_open_pane, args=[p])
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
        
    def draw(self, surf):
        for p in self.panes:
            if p is self.open_pane:
                p.draw(surf)
            else:
                p.draw_label(surf)
        for b in self.buttons:
            b.draw(surf)

class Slider(Base_Object, Position):
    def __init__(self, size, ran, dir='x', handel_size=None, color=(255, 255, 255), hcolor=(0, 0, 0), flipped=False, func=lambda *args, **kwargs: None, args=[], kwargs={}):
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.color = color
        
        if handel_size is None:
            if dir == 'x':
                handel_size = (10, self.rect.height * 2)
                anchor = 'midleft'
            elif dir == 'y':
                handel_size = (self.rect.width * 2, 10)
                anchor = 'midtop'
        self.handel = Position(rect=pg.Rect(0, 0, handel_size[0], handel_size[1]))
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
            
        Base_Object.__init__(self)
        Position.__init__(self)
        
        self.handel.set_parent(self.rect, anchor_point=anchor)
        self.add_child(self.handel)
        
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
            self.handel.rect.centery = self.rect.centery
            if self.handel.rect.centerx > self.rect.right:
                self.handel.rect.centerx = self.rect.right
            elif self.handel.rect.centerx < self.rect.left:
                self.handel.rect.centerx = self.rect.left
        elif self.dir == 'y':
            self.handel.rect.centerx = self.rect.centerx
            if self.handel.rect.centery > self.rect.bottom:
                self.handel.rect.centery = self.rect.bottom
            elif self.handel.rect.centery < self.rect.top:
                self.handel.rect.centery = self.rect.top
        self.handel.set_current_offset()
        
    def events(self, events):
        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if mbd:
            if mbd.button == 1:
                if self.handel.rect.collidepoint(p) or self.rect.collidepoint(p):
                    self.held = True

        elif mbu:
            if mbu.button == 1:
                self.held = False
                
    def update(self):
        if self.held:
            p = pg.mouse.get_pos()
            self.handel.rect.center = p
            self.func(*self.args, **self.kwargs) 
        self.adjust_handel()

    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect)
        pg.draw.rect(surf, self.handel_color, self.handel.rect)

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

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        pg.draw.rect(surf, (255, 255, 255), self.rect, width=1)
        pg.draw.rect(surf, self.hcolor, self.handel.rect)
        pg.draw.rect(surf, (255, 255, 255), self.handel.rect, width=3)

class LoadingIcon(Base_Object, Position):
    DA = 4.71239
    def __init__(self, rad=50, color=(0, 0, 255)):
        self.rect = pg.Rect(0, 0, rad // 2, rad // 2)
        
        self.rad = rad
        self.color = color
        
        self.angle = 0
        
        Base_Object.__init__(self)
        Position.__init__(self)
        
    def update(self):
        self.angle -= 0.1
        
    def draw(self, surf):
        pg.draw.arc(surf, self.color, self.rect, self.angle, self.angle + LoadingIcon.DA, width=4)
    
    
    
    
    
    
    