import sys

import pygame as pg

from .element.base import Base_Object
from .element.standard import Image, Textbox, Button
from .element.background import Timer, On_Click
from .element.icon import Loading_Icon

def get_window_size():
    return pg.display.get_window_size()
    
def get_window_center():
    w, h = pg.display.get_window_size()
    return (w // 2, h // 2)
    
class Base_Loop:  
    LAST_BATCH = None
    DOUBLE_CLICK_MAX = 10
    HOVER_MAX = 15
    
    def __init__(self, objects, fps=30):
        self.running = False
        self.window = pg.display.get_surface()
        self.clock = pg.time.Clock()
        self.fps = fps
        self.objects = objects
        
        self.click_timer = 0
        self.hover_timer = 0
        self.hover_object = None
        
    @property
    def time_step(self):
        return 30 / self.fps
        
    @property
    def last_batch(self):
        return Base_Loop.LAST_BATCH.copy()

    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, object):
        if object in self.objects:
            self.objects.remove(object)
            
    def get_events(self):
        event_batch = pg.event.get()
        
        self.click_timer += self.time_step

        events = {}
        events['all'] = event_batch
        events['p'] = pg.mouse.get_pos()
        for e in event_batch:
            if e.type == pg.QUIT:
                events['q'] = e
            elif e.type == pg.MOUSEBUTTONDOWN:
                events['mbd'] = e
                if e.button == 1:
                    if self.click_timer < Base_Loop.DOUBLE_CLICK_MAX:
                        events['dub'] = True
                    self.click_timer = 0
            elif e.type == pg.MOUSEBUTTONUP:
                events['mbu'] = e
            elif e.type == pg.KEYDOWN:
                events['kd'] = e
            elif e.type == pg.KEYUP:
                events['ku'] = e
                
        if self.hover_timer > Base_Loop.HOVER_MAX:
            events['hover'] = o
            
        Base_Loop.LAST_BATCH = events.copy()
                
        return events

    def get_event_objects(self):
        return self.objects
        
    def update_hover(self, hit, o):
        if hit:
            if o is self.hover_object:
                self.hover_timer += self.time_step
            else:
                self.hover_object = o
                self.hover_timer = 0
        else:
            self.hover_timer = 0

    def sub_events(self, events):
        hit = False
        
        for o in self.get_event_objects():
            if o.enabled:
                o.events(events)
                if not hit:
                    hit = o.set_cursor()
                    self.update_hover(hit, o)
        if not hit:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            
        return hit

    def events(self):
        hit = False
        events = Base_Loop.get_events()
        p = events.get('p')
        
        if events.get('q'):
            self.exit()
            return
            
        for o in self.objects:
            if o.enabled:
                o.events(events)
                if not hit:
                    hit = o.set_cursor()
                    self.update_hover(hit, o)
        if not hit:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
               
    def update(self):
        for o in self.objects:
            o.update()

    def draw(self):
        self.window.fill((0, 0, 0))
        for o in self.objects:
            if o.visible and not o.window_draw:
                o.draw(self.window)
        pg.display.flip()
        
    def exit(self):
        self.running = False
        
    def quit(self):
        pg.quit()
        sys.exit()
                
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
    def get_window_objects(message='', tsize=25, size=(300, 150), color1=(100, 100, 100), color2=(50, 50, 50), olcolor=(255, 255, 255), **kwargs):
        objects = []
        
        w, h = size
        
        body = pg.Rect(0, 0, w, h)
        upper = pg.Rect(0, 0, w, h - 50)
        lower = pg.Rect(0, 100, w, 50)
        text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
        outline = pg.Rect(0, 0, body.width + 10, body.height + 10)

        s = pg.Surface(outline.size).convert()
        pg.draw.rect(s, olcolor, outline, border_radius=10)
        body.center = outline.center
        pg.draw.rect(s, color1, body, border_radius=10)
        lower.bottomleft = body.bottomleft
        pg.draw.rect(s, color2, lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
        i = Image(s)
        i.rect.center = get_window_center()
        objects.append(i)
        
        body.center = get_window_center()
        upper.topleft = body.topleft
        text_rect.center = upper.center
        lower.bottomleft = body.bottomleft
        
        if message:
            t = Textbox(message, olcolor=(0, 0, 0), **kwargs)
            t.fit_text(text_rect, tsize=tsize)
            t.rect.center = text_rect.center
            t.set_parent(i, anchor_point='center', current_offset=True)
            objects.append(t)
            
        return (objects, (upper, lower))

    @classmethod
    def notice(cls, message, overlay=False, bcolor=(0, 200, 0), **kwargs):
        objects, (_, lower) = cls.get_window_objects(message=message, **kwargs)
        
        b = Button.text_button('ok', size=(150, 25), tsize=25, color2=bcolor)
        b.set_tag('break')
        b.rect.center = lower.center
        b.set_parent(objects[0], anchor_point='center', current_offset=True)
        objects.append(b)
        
        return cls(objects=objects, overlay=overlay)

    @classmethod
    def yes_no(cls, message, overlay=False, yes_btn_color=(0, 200, 0), no_btn_color=(200, 0, 0), **kwargs):
        objects, (_, lower) = cls.get_window_objects(message=message, **kwargs)

        b = Button.text_button('yes', size=(100, 30), tsize=25, color2=yes_btn_color, func=lambda: True)
        b.set_tag('return')
        b.rect.midleft = lower.midleft
        b.rect.x += 20
        b.set_parent(objects[0], anchor_point='center', current_offset=True)
        objects.append(b)
        
        b = Button.text_button('no', size=(100, 30), tsize=25, color2=no_btn_color, func=lambda: False)
        b.set_tag('return')
        b.rect.midright = lower.midright
        b.rect.x -= 20
        b.set_parent(objects[0], anchor_point='center', current_offset=True)
        objects.append(b)

        return cls(objects=objects, overlay=overlay)

    @classmethod
    def loading_screen(cls, func, fargs=[], fkwargs={}, overlay=False, **kwargs):
        objects, (_, lower) = cls.get_window_objects(**kwargs)

        li = Loading_Icon()
        li.rect.topright = objects[0].rect.topright
        li.rect.top += 10
        li.rect.right -= 10
        li.set_parent(objects[0], anchor_point='center', current_offset=True)
        objects.append(li)
        
        o = Base_Object(func=func, args=fargs, kwargs=fkwargs, enable_func=True)
        o.set_tag('return')
        objects.append(o)

        return cls(objects=objects, overlay=overlay)
        
    @classmethod
    def loading_bar(cls, func, fargs=[], fkwargs={}, overlay=False, **kwargs):
        objects, (_, lower) = cls.get_window_objects(**kwargs)

        li = Progress_Bar(auto=True)
        li.rect.topright = objects[0].rect.topright
        li.rect.top += 10
        li.rect.right -= 10
        li.set_parent(objects[0], anchor_point='center', current_offset=True)
        objects.append(li)
        
        o = Base_Object(func=func, args=fargs, kwargs=fkwargs, enable_func=True)
        o.set_tag('return')
        objects.append(o)

        return cls(objects=objects, overlay=overlay)

    @classmethod
    def timed_message(cls, message, timer, overlay=False, can_exit=False, **kwargs):
        objects, _ = cls.get_window_objects(message=message, **kwargs)
        
        t = Timer(timer, func=lambda: 1)
        t.set_tag('return')
        objects.append(t)
        
        if can_exit:
            c = On_Click(func=lambda: 1)
            c.set_tag('return')
            objects.append(c)
        
        return cls(objects=objects, overlay=overlay)

    @classmethod
    def build_and_run(cls, get_objects, *args, overlay=False, **kwargs):
        menu = cls(get_objects=get_objects, args=args, kwargs=kwargs, overlay=overlay)
        menu.run()
        
    @classmethod
    def build_and_run_obj(cls, objects, *args, overlay=False, **kwargs):
        menu = cls(objects=objects, args=args, kwargs=kwargs, overlay=overlay)
        menu.run()

    def __init__(self, get_objects=None, objects=[], args=[], kwargs={}, overlay=False, quit=True, fill_color=(0, 0, 0)):
        if get_objects:
            objects = get_objects(*args, **kwargs)
        super().__init__(objects)
        
        self.get_objects = get_objects
        self.args = args
        self.kwargs = kwargs
        self.return_val = None

        self.fill_color = fill_color
        self.background = None
        if overlay:
            s = self.window.copy()
            o = pg.Surface(s.get_size()).convert_alpha()
            o.fill((0, 0, 0, 180))
            s.blit(o, (0, 0))
            self.background = s

        self.set_funcs()

        self._quit = quit

    def add_object(self, object):
        self.objects.append(object)
        
    def remove_object(self, object):
        while object in self.objects:
            self.objects.remove(object)
        
    def set_funcs(self):
        for o in self.objects.copy():
            o._menu = self
            
            if o.tag == 'break':
                if o._func:
                    exit_func = self.wrap_exit_function(o)
                else:
                    exit_func = self.exit
                o.set_func(exit_func)
            elif o.tag == 'return':
                return_func = self.wrap_return_function(o)
                o.set_func(return_func)
            elif o.tag == 'refresh':
                refresh_func = self.wrap_refresh_function(o)
                o.set_func(refresh_func)
            if o.ohandle:
                self.objects.remove(o)
                
    def wrap_exit_function(self, o):
        f = o._func
        def exit_func(*args, **kwargs):
            f(*args, **kwargs)
            self.exit()
        return exit_func
                
    def wrap_return_function(self, o):
        f = o._func
        def return_func(*args, **kwargs):
            val = f(*args, **kwargs)
            o.return_val = val
            self.set_return(val)
        return return_func
        
    def wrap_refresh_function(self, o):
        f = o._func
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
        
    def quit_or_exit(self):
        if self._quit:
            self.quit()
        self.exit()
        
    def events(self):
        hit = False
        events = self.get_events()
        if events.get('q'):
            self.quit_or_exit()
        e = events.get('kd')
        if e:
            if e.key == pg.K_ESCAPE:
                self.quit_or_exit()
                    
        for o in self.objects:
            if o.enabled:
                o.events(events)
                if not hit:
                    hit = o.set_cursor()
                    self.update_hover(hit, o)
                        
        if not hit:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            
        return events
  
    def draw(self):
        self.window.fill(self.fill_color)
        if self.background:
            self.window.blit(self.background, (0, 0))
        for o in self.objects:
            if o.visible and not o.window_draw:
                o.draw(self.window)
        pg.display.flip()
        
    def lite_draw(self):
        for o in self.objects:
            if o.visible and not o.window_draw:
                o.draw(self.window)
          
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
