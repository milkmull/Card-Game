import pygame as pg

from ..image import get_surface, get_arrow
from .base import Mover, Position, Compound_Object
from .standard import Textbox, Button, Slider

class Scroll_Bar(Compound_Object):
    def __init__(self, height, width=16, extended_rect=None, **kwargs):
        super().__init__()
        self.rect = pg.Rect(0, 0, width, height)
        
        if extended_rect is None:
            extended_rect = self.rect
        self.extended_rect = extended_rect
        
        s = Slider((width, height - (2 * width)), range(height), dir='y', handel_size=(width - 4, 1), color=(255, 255, 255), hcolor=(100, 100, 100), contained=True)
        self.slider = s
        self.add_child(s, anchor_point='center')

        up_arrow = get_arrow('u', (width, width), padding=(6, 6), color=(100, 100, 100), bgcolor=(255, 255, 255))
        down_arrow = pg.transform.flip(up_arrow, False, True)

        self.up_button = Button.image_button(up_arrow, size=up_arrow.get_size(), border_radius=0, func=self.scroll, args=[-1])
        self.add_child(self.up_button, anchor_point='midtop')
        self.down_button = Button.image_button(down_arrow, size=down_arrow.get_size(), border_radius=0, func=self.scroll, args=[1])
        self.add_child(self.down_button, anchor_point='midbottom')

        self.set_height_ratio(1)
        
    @property
    def handel(self):
        return self.slider.handel
        
    @property
    def body(self):
        return self.slider
        
    @property
    def height_ratio(self):
        return self.handel.rect.height / self.body.rect.height
        
    @property
    def scroll_ratio(self):
        return round((self.handel.rect.top - self.body.rect.top) / self.body.rect.height, 3)
        
    def set_height_ratio(self, r):
        top = self.handel.rect.top
        self.handel.rect.height = self.body.rect.height * r
        self.handel.rect.top = top
        self.slider.adjust_handel()
        
    def set_height(self, height):
        self.rect.height = height
        r = self.height_ratio
        self.body.rect.height = height - (2 * self.rect.width)
        self.set_height_ratio(r)

    def is_held(self):
        return self.slider.held
        
    def is_full(self):
        return self.height_ratio == 1

    def can_scroll_down(self):
        return self.handel.rect.bottom < self.body.rect.bottom
        
    def can_scroll_up(self):
        return self.handel.rect.top > self.body.rect.top
        
    def scroll(self, dir):
        self.handel.adjust_offset(0, dir * max({self.handel.rect.height / 2, 1}))
        self.handel.update_position()
        self.slider.adjust_handel()
        
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
        
    def events(self, events):                
        super().events(events)
        
        p = events['p']
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if mbd:
            if self.rect.collidepoint(p) or self.extended_rect.collidepoint(p):
                if mbd.button == 4:
                    self.scroll(-1)
                elif mbd.button == 5:
                    self.scroll(1)

class Scroll_Controller:
    def __init__(self, height=None, extended_rect=None):
        if extended_rect is None:
            extended_rect = self.rect
        if height is None:
            height = self.rect.height
            
        self.scroll_bar = Scroll_Bar(height, extended_rect=extended_rect)
        self.add_child(self.scroll_bar, anchor_point='topright', offset=[self.scroll_bar.rect.width, 0])

        self.bounding_box = Position.rect(self.rect.copy())
        self.add_child(self.bounding_box, anchor_point='midtop')

        self.last_offset = -1
        
    def set_total_height(self, height):
        r = self.rect.height / height
        self.scroll_bar.set_height_ratio(r)
        self.bounding_box.rect.height = height
        r = self.scroll_bar.scroll_ratio
        self.set_window(r)

    def update_window(self):
        current_offset = self.scroll_bar.scroll_ratio
        if current_offset != self.last_offset:
            self.set_window(current_offset)
            self.last_offset = current_offset
        self.update_bar()
        
    def set_window(self, r):
        top = self.bounding_box.rect.top
        self.bounding_box.rect.top = self.rect.top - (self.bounding_box.rect.height * r)
        self.bounding_box.rect.centerx = self.rect.centerx
        self.bounding_box.set_current_offset()
        
    def update_bar(self):
        full = self.scroll_bar.is_full()
        if not full:
            self.scroll_bar.turn_on()
        else:
            self.scroll_bar.turn_off()
 
class Label(Compound_Object):
    def __init__(self, parent, *args, color=(0, 0, 0), height=25, **kwargs):
        super().__init__()
        self.rect = pg.Rect(0, 0, parent.rect.width, height)
        
        self.color = color

        self.textbox = Textbox(*args, **kwargs)
        self.textbox.fit_text(self.rect)
        self.add_child(self.textbox, anchor_point='center')
        
        parent.add_child(self, anchor_point='topleft', offset=[0, -height])
        
    def set_message(self, *args, **kwargs):
        self.textbox.set_message(*args, **kwargs)
        
    def get_message(self):
        return self.textbox.get_message()
        
    def update(self):
        if isinstance(self.parent, Static_Window):
            if self.parent.scroll_bar.visible:
                self.rect.width = self.parent.rect.width + self.parent.scroll_bar.rect.width
            else:
                self.rect.width = self.parent.rect.width
        super().update()
        
    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect, border_top_left_radius=10, border_top_right_radius=10)
        super().draw(surf)

class Static_Window(Compound_Object, Scroll_Controller):
    def __init__(self, image=None, **kwargs):
        kwargs.pop('from_surface', None)
        kwargs.pop('outline_dir', None)
        Compound_Object.__init__(self, from_surface=True, outline_dir=True, **kwargs)
        Scroll_Controller.__init__(self)
        
        self.current_image = self.image.copy()

        self.objects = []
        self.orientation_cache = {'xpad': 5, 'ypad': 5, 'dir': 'y', 'pack': False}
        
    def __bool__(self):
        return bool(self.objects)

    def set_color(self, color):
        self.color = color
        self.image.fill(color)
        self.refresh_image()

    def get_label(self, *args, **kwargs):
        label = Label(self, *args, **kwargs)
        return label
        
    def add_label(self, *args, **kwargs):
        Label(self, *args, **kwargs)
 
    def resize(self, w=None, h=None, anchor_point='center'):
        if w is None:
            w = self.rect.width
        if h is None:
            h = self.rect.height
        self.size = (w, h)
        p = getattr(self.rect, anchor_point)
        self.rect.size = (w, h)
        setattr(self.rect, anchor_point, p)
        self.bounding_box.rect.width = w
        self.image = pg.transform.smoothscale(self.image, (w, h))
        self.current_image = self.image.copy()
        self.scroll_bar.set_height(self.rect.height)
        
    def get_children(self):
        return self.children + self.objects
        
    def get_objects(self):
        return self.objects
  
    def is_same(self, objects):
        if len(objects) == len(self.objects):
            return all({objects[i] == self.objects[i] for i in range(len(objects))})
        else:
            return False
            
    def get_visible(self):
        return [o for o in self.objects if self.rect.colliderect(o.rect)]
        
    def sort_objects(self, key):
        objects = sorted(self.objects, key=key)
        self.join_objects(objects)
    
    def clear(self):
        if self.objects:
            self.join_objects([])
            self.refresh_image()

    def refresh_image(self):
        self.current_image.blit(self.image, (0, 0))
        
    def refresh(self):
        self.join_objects(self.objects, force=True)
        self.scroll_bar.refresh()
        
    def add_object(self, object):
        self.join_objects(self.objects + [object])
        
    def remove_object(self, object):
        if object in self.objects:
            objects = self.objects.copy()
            objects.remove(object)
            self.join_objects(objects)
    
    def join_objects(self, objects, xpad=None, ypad=None, dir=None, pack=None, force=False, move=False):
        if xpad is None:
            xpad = self.orientation_cache['xpad']
        if ypad is None:
            ypad = self.orientation_cache['ypad']
        if dir is None:
            dir = self.orientation_cache['dir']
        if pack is None:
            pack = self.orientation_cache['pack']

        same = self.is_same(objects)

        if not same or force:
            x = 0
            y = 0
            wmax = 0
            hmax = 0

            if dir == 'y':   
                for o in objects:
                    if pack:
                        if self.rect.y + y + ypad + o.rect.height > self.rect.bottom:
                            y = 0 
                            x += wmax + xpad
                            wmax = 0
                        offset = [x + xpad, y + ypad]
                        o.set_parent(self.bounding_box, offset=offset)   
                    else:
                        offset = [0, y + ypad]  
                        o.set_parent(self.bounding_box, anchor_point='midtop', offset=offset)
                    y += o.rect.height + ypad
                    if o.rect.width > wmax:
                        wmax = o.rect.width
                    
            elif dir == 'x':
                for o in objects:
                    if pack:
                        if self.rect.x + x + xpad + o.rect.width > self.rect.right:
                            x = 0
                            y += hmax + ypad 
                            hmax = 0
                        offset = [x + xpad, y + ypad]
                        o.set_parent(self.bounding_box, offset=offset)    
                    else:
                        offset = [x + xpad, 0]  
                        o.set_parent(self.bounding_box, anchor_point='midleft', offset=offset)  
                    x += o.rect.width + xpad
                    if o.rect.height > hmax:
                        hmax = o.rect.height

            self.objects = objects.copy()
            self.orientation_cache = {'xpad': xpad, 'ypad': ypad, 'dir': dir, 'pack': pack}
            self.set_total_height()
                
        elif same and move and objects:
            for i in range(len(self.objects)):
                o0 = self.objects[i]
                o1 = objects[i]
                o1.position_copy_from(o0)
                self.objects[i] = o1
                
    def join_objects_custom(self, offsets, objects, force=False, move=False):
        same = self.is_same(objects)

        if not same or force:
 
            for (x, y), o in zip(offsets, objects):
                offset = [x, y] 
                o.set_parent(self.bounding_box, anchor_point='topleft', offset=offset)

            self.objects = objects.copy()
            self.set_total_height()
                
        elif same and move and objects:
            for i in range(len(self.objects)):
                o0 = self.objects[i]
                o1 = objects_list[i]
                o1.position_copy_from(o0)
                self.objects[i] = o1

    def set_total_height(self):
        h = self.rect.height
        if self.objects: 
            ymin = min({o.rect.top for o in self.objects})
            ymax = max({o.rect.bottom for o in self.objects})
            pad = 2 * self.orientation_cache['ypad']
            h = max({(ymax - ymin) + pad, h})
            
        super().set_total_height(h)
                
    def set_window(self, r):
        super().set_window(r)
        self.redraw()
                
    def redraw(self):
        self.refresh_image()
        for o in self.objects: 
            o.update_position()
            if o.rect.colliderect(self.rect):
                o.draw_on(self.current_image, self.rect)

    def set_cursor(self):
        return self.scroll_bar.set_cursor()
                        
    def update(self):
        super().update()
        self.update_window()
        
        for o in self.objects:
            o.update_position()
            visible_and_enabled = self.visible and self.rect.colliderect(o.rect)
            o.set_visible(visible_and_enabled)
            o.set_enabled(visible_and_enabled)

    def draw(self, surf):
        surf.blit(self.current_image, self.rect)
        super().draw(surf)
            
class Live_Window(Static_Window):   
    def set_cursor(self):
        for o in self.objects:
            if hasattr(o, 'set_cursor'):
                if o.visible and o.enabled:
                    if o.set_cursor():
                        return True
        return super().set_cursor()
        
    def join_objects(self, *args, **kwargs):
        super().join_objects(*args, **kwargs)
        for o in self.objects:
            o.set_window_draw(True)
            
    def events(self, events):
        super().events(events)
        for o in self.objects:
            if o.visible and o.enabled:
                o.events(events)
            
    def update(self):
        super().update()
        for o in self.objects:
            o.update()

    def draw(self, surf):
        self.current_image.blit(self.image, (0, 0))
        super().draw(surf)
        surf.set_clip(self.rect)
        for o in self.objects:
            if o.visible:
                o.draw(surf)
        surf.set_clip(None)
        
class Popup_Base(Mover):
    def __init__(self, dir='y', vel=15):
        super().__init__()
        self.dir = dir
        self._vel = vel
        
        self.t = None
        self.o = None
        
        self.inflation = [50, 50]

        self.force_up = False
        self.force_down = False
        
    @property
    def sense_rect(self):
        return self.rect.inflate(self.inflation[0], self.inflation[1])
        
    def start_force_up(self):
        self.force_up = True
        self.force_down = False
    
    def start_force_down(self):
        self.force_up = False
        self.force_down = True
        
    def set_inflation(self, x=None, y=None):
        if x:
            self.inflation[0] = x
        if y:
            self.inflation[1] = y
            
    def is_visible(self):
        return self.t != self.o
        
    def get_target(self):
        if self.dir == 'y':
            return self.rect.move(0, -self.rect.height)
        elif self.dir == '-y':
            return self.rect.move(0, self.rect.height)
        elif self.dir == 'x':
            return self.rect.move(self.rect.width, 0)
        elif self.dir == '-x':
            return self.rect.move(-self.rect.width, 0)
            
    def popup_events(self, events):
        p = events['p']

        if (self.sense_rect.collidepoint(p) and not self.force_down) or self.force_up:
            if not self.t:
                t = self.get_target()
                self.t = t
                self.o = self.rect.copy()
            if self.target_rect != self.t:
                self.set_target_rect(self.t, v=self._vel)
                
        elif not self.scroll_bar.is_held() and self.t:
            self.set_target_rect(self.o, v=self._vel)
            
    def stop_move(self):
        super().stop_move()
        if self.target_rect == self.o:
            self.t = None
            self.o = None

class Static_Popup(Static_Window, Popup_Base):
    def __init__(self, *args, dir='y', vel=15, **kwargs):
        Static_Window.__init__(self, *args, **kwargs)
        Popup_Base.__init__(self, dir=dir, vel=vel)
        
    def events(self, events):
        super().events(events)
        self.popup_events(events)
        
    def update(self):
        self.move()
        super().update()
        
    def draw(self, surf):
        if self.is_visible():
            super().draw(surf)

class Live_Popup(Live_Window, Popup_Base):
    def __init__(self, *args, dir='y', vel=15, **kwargs):
        Static_Window.__init__(self, *args, **kwargs)
        Popup_Base.__init__(self, dir=dir, vel=vel)
        
    def events(self, events):
        super().events(events)
        self.popup_events(events)
        
    def update(self):
        self.move()
        super().update()
        
    def draw(self, surf):
        if self.is_visible():
            super().draw(surf)

