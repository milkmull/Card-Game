import pygame as pg

from ..logging import Logging
from ..image import get_arrow
from .base import Compound_Object
from .standard import Image, Textbox, Button, Input, Slider, Input, Check_Box
from .window import Static_Window, Live_Window
from .complex import Dropdown

class Alt_Static_Window(Static_Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        up_arrow = get_arrow('u', (self.rect.width, 15), padding=(self.rect.width + 10, 10), color=(255, 255, 255), bgcolor=(50, 50, 50, 100))
        down_arrow = pg.transform.rotate(up_arrow, 180)

        self.scroll_bar.up_button.join_object(Image(up_arrow))
        self.scroll_bar.up_button.border_radius = 0
        self.add_child(self.scroll_bar.up_button, anchor_point='midtop')
        
        self.scroll_bar.down_button.join_object(Image(down_arrow))
        self.scroll_bar.down_button.border_radius = 0
        self.add_child(self.scroll_bar.down_button, anchor_point='midbottom')
        
        self.scroll_bar.turn_off()

    def draw(self, surf):
        surf.blit(self.current_image, self.rect)
        if not self.scroll_bar.is_full():
            if self.scroll_bar.can_scroll_up():
                self.scroll_bar.up_button.draw(surf)
            if self.scroll_bar.can_scroll_down():
                self.scroll_bar.down_button.draw(surf)
                
class Logged_Input(Input, Logging):
    def __init__(self, *args, **kwargs):
        Input.__init__(self, *args, **kwargs)
        Logging.__init__(self)
        
        self.last_message = self.message
        
    def open(self):
        m = self.message
        self.last_message = m
        if m == self.default:
            self.clear()
        self.active = True
        self.set_index(len(self.message))
        if self.hl:
            self.highlight_full()

    def close(self):
        if self.active:
            self.active = False
            m = self.message
            if not m.strip():
                self.textbox.reset()
                m = self.message
            if self.last_message != m:
                self.add_log({'t': 'val', 'o': self, 'v': (self.last_message, m)})
            self.selection.clear()
            if self.scroll:
                self.textbox.rect.midleft = self.rect.midleft
                self.textbox.rect.x += self.left_pad
                self.textbox.set_current_offset()
  
class Logged_Check_Box(Check_Box, Logging):
    def __init__(self, *args, **kwargs):
        Check_Box.__init__(self, *args, **kwargs)
        Logging.__init__(self)
        
    def set_state(self, state, d=False):
        state0 = self.state
        super().set_state(state)
        state1 = self.state
        if not d and state1 != state0:
            self.add_log({'t': 'val', 'o': self, 'v': (state0, state1)})
            
class Logged_Dropdown(Dropdown, Logging):
    def __init__(self, *args, **kwargs):
        Dropdown.__init__(self, *args, **kwargs)
        Logging.__init__(self)
        
    def set_value(self, val, d=False):
        value0 = self.current_value
        super().set_value(val)
        value1 = self.current_value
        if not d and value1 != value0:
            self.add_log({'t': 'val', 'o': self, 'v': (value0, value1)})
  
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
        
class Dropdown_Multi_Select(Compound_Object):
    def __init__(self, selection, max_select, selected=[]):
        super().__init__()
        self.rect = pg.Rect(0, 0, 100, 20)
            
        self.selection = selection
        self.slots = []
        y = self.rect.y
        for _ in range(max_select):
            tb = Textbox('')
            tb.rect.topleft = (self.rect.x, y)
            self.add_child(tb, current_offset=True)
            
            b = Button.text_button('X', func=self.remove_value, tsize=15)
            b.set_args(args=[tb, b])
            b.turn_off()
            b.rect.midleft = tb.rect.midright
            b.rect.x += 5
            self.add_child(b, current_offset=True)
            
            self.slots.append((tb, b))
            
            y += tb.rect.height
        
        down_arrow = get_arrow('d', (16, 16))
        self.drop_down = Button.image_button(down_arrow, func=self.open)
        self.drop_down.rect.midleft = self.rect.midright
        self.add_child(self.drop_down, current_offset=True)
        
        self.buttons = {v: Button.text_button(v, func=self.add_value, args=[v], border_radius=0) for v in self.selection}

        self.window = Live_Window((self.rect.width, self.rect.width + 50))
        self.window.join_objects(list(self.buttons.values()))
        self.window.rect.topleft = self.slots[-1][0].rect.bottomleft
        self.add_child(self.window, current_offset=True)
        self.window.turn_off()
    
    @property
    def current_values(self):
        values = []
        for tb, b in self.slots:
            m = tb.get_message()
            if m:
                values.append(m)
        return values
        
    def is_open(self):
        return self.window.visible
        
    def add_value(self, val):
        added = False
        for tb, b in self.slots:
            if not tb.get_message():
                tb.set_message(val)
                tb.update_position()
                b.turn_on()
                b.rect.midleft = tb.rect.midright
                b.rect.x += 5
                b.set_current_offset()
                added = True
                break
        self.close()
        
        return added
        
    def shift_down(self):
        y = self.rect.y
        for tb, b in sorted(self.slots, key=lambda s: 0 if s[0].get_message() else 1):
            tb.rect.topleft = (self.rect.x, y)
            tb.set_current_offset()
            b.rect.midleft = tb.rect.midright
            b.rect.x += 5
            b.set_current_offset()
            y += tb.rect.height
        
    def remove_value(self, tb, b):
        tb.clear()
        b.turn_off()
        self.shift_down()
        
    def flip_arrow(self):
        img = self.drop_down.object
        img.set_image(pg.transform.flip(img.image, False, True))
            
    def open(self):
        self.flip_arrow()
        cvs = self.current_values
        buttons = [b for v, b in self.buttons.items() if v not in cvs]
        self.window.join_objects(buttons)
        self.window.turn_on()
        self.drop_down.set_func(self.close)
                
    def close(self):
        if self.is_open():
            self.flip_arrow()
            self.window.turn_off()
            self.drop_down.set_func(self.open)
  
