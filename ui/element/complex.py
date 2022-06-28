import pygame as pg

from ..image import get_arrow
from ..icons.icons import icons
from .base import Compound_Object
from .standard import Image, Textbox, Button
from .window import Live_Window

class Dropdown(Compound_Object):
    @staticmethod
    def to_dict(selection):
        return {k: None for k in selection}
        
    @staticmethod
    def find_default(selection, data=None):
        if data is None:
            data = selection
        key = list(selection)[0]
        value = data[key]
        if not value:
            return key
        return Dropdown.find_default(value)
        
    def __init__(self, selection, selected=None, **kwargs):
        super().__init__(**kwargs)
        kwargs.pop('size', None)

        if isinstance(selection, (list, tuple, set)):
            selection = self.to_dict(selection)
        self.selection = selection
        
        if selected is None:
            selected = Dropdown.find_default(self.selection)
            
        self.current = Textbox(selected, **kwargs)
        self.current.fit_text(self.padded_rect)
        self.current.rect.topleft = self.padded_rect.topleft
        self.add_child(self.current, current_offset=True)
        
        kwargs.pop('border_radius', None)

        down_arrow = get_arrow('d', (self.padded_rect.height - 6, self.padded_rect.height - 6))
        self.drop_down = Button.image_button(down_arrow, func=self.open, border_radius=0, **kwargs)
        self.drop_down.outline_color = None
        self.drop_down.rect.midright = self.padded_rect.midright
        self.add_child(self.drop_down, current_offset=True)
        
        self.right_arrow = pg.transform.rotate(down_arrow, 90)

        self.windows = {}

        self.leftover = kwargs
        
    @property
    def button_kwargs(self):
        button_kwargs = self.leftover.copy()
        button_kwargs.pop('outline_color', None)
        return button_kwargs
        
    @property
    def current_value(self):
        return self.current.get_message()
        
    @property
    def is_open(self):
        return self.windows
        
    def set_value(self, val):
        self.current.set_message(val)
        if self.is_open:
            self.close()
        self.run_func()
        
    def flip_arrow(self):
        image = self.drop_down.first_born
        image.set_image(pg.transform.flip(image.image, False, True))
            
    def open(self):
        self.flip_arrow()
        self.new_window(self.selection)
        self.drop_down.set_func(self.close)
        
    def close(self):
        self.flip_arrow()
        for w in self.windows:
            self.remove_child(w)
        self.windows.clear()
        self.drop_down.set_func(self.open)

    def new_window(self, data, last=None, level=0):  
        found = False
        
        for w, info in self.windows.copy().items():
            if info['level'] >= level:
                self.remove_child(w)
                self.windows.pop(w)
                if info['parent']:
                    info['parent'].color1 = info['color']
                if info['parent'] is last:
                    found = True
        
        if found:
            return
                   
        buttons = []
        for k, v in data.items():
            if v is None:
                b = Button.text_button(
                    k,
                    size=(self.rect.width - 10, self.rect.height),
                    func=self.set_value,
                    args=[k],
                    border_radius=0,
                    **self.button_kwargs
                )
            else:
                b = Button.text_button(
                    k,
                    size=(self.rect.width - 10, self.rect.height),
                    func=self.new_window,
                    args=[v],
                    border_radius=0,
                    **self.button_kwargs
                ) 
                b.set_args(kwargs={'last': b, 'level': level + 1})
                
                i = Image(self.right_arrow)
                i.rect.midright = b.rect.midright
                i.rect.x -= 5
                b.add_child(i, current_offset=True)
                
            buttons.append(b)
            
        h = sum([b.rect.height for b in buttons[:7]])
        window = Live_Window(size=(self.rect.width - 10, h), draw_rect=True, **self.leftover)
        
        self.windows[window] = {
            'parent': last,
            'level': level,
            'color': getattr(last, 'color1', None)
        }

        if last is not None:
            window.rect.topleft = last.rect.topright
            last.color1 = last.color2
        else:
            window.rect.midtop = self.rect.midbottom
        self.add_child(window, current_offset=True)
        window.join_objects(buttons, ypad=0)
        
    def events(self, events):
        super().events(events)
        
        mbd = events.get('mbd')
        if mbd:
            if mbd.button == 1 or mbd.button == 3:
                if self.is_open:
                    self.close()

    def draw(self, surf):
        self.draw_rect(surf)
        super().draw(surf)
 