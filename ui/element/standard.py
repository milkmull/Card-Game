import os
from tkinter import Tk

import pygame as pg
from pygame.math import Vector2 as vec
import pygame.freetype

from ..color import tint, shade
from ..image import get_surface, get_arrow, crop
from ..icons.icons import icons
from .base import Position, Compound_Object

class Image(Compound_Object): 
    @classmethod
    def from_style(cls, *args, **kwargs):
        return cls(get_surface(*args, **kwargs))
        
    def __init__(self, image, bgcolor=None, **kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.rect = self.image.get_rect()
        self.bgcolor = bgcolor
        
    def get_image(self):
        return self.image
        
    def set_image(self, image, keep_scale=True):
        c = self.rect.center
        if keep_scale:
            self.image = pg.transform.smoothscale(image, self.rect.size)
        else:
            self.image = image
            self.rect.size = image.get_size()
        self.rect.center = c
        
    def set_background(self, color):
        self.bgcolor = color
        
    def clear_background(self):
        self.bgcolor = None
        
    def set_colorkey(self, key):
        self.image.set_colorkey(key)
        
    def fill(self, color):
        self.image.fill(color)
        
    def scale(self, size):
        self.image = pg.transform.smoothscale(self.image, size)
        self.rect.size = size
        
    def draw(self, surf):
        if self.bgcolor is not None:
            pg.draw.rect(surf, self.bgcolor, self.rect)
        surf.blit(self.image, self.rect)
        super().draw(surf)

class Textbox(Compound_Object):
    pg.freetype.init()
    FONTS = {
        'pygame': pg.freetype.Font(None),
        'icons': pg.freetype.Font('ui/icons/icons.ttf')
    }
    FONT_PATHS = ['ui/icons']

    OLCACHE = {}
    
    @classmethod
    def add_font_path(cls, path):
        cls.FONT_PATHS.append(path)

    @classmethod
    def get_font(cls, name='pygame'):
        file = f'{name}.ttf'
        if name not in cls.FONTS:
            for path in cls.FONT_PATHS:
                if file in os.listdir(path):
                    font = pg.freetype.Font(f'{path}/{name}.ttf')
                    cls.FONTS[name] = font
                    break
            else:
                name = 'pygame'
        return cls.FONTS[name]
        
    @classmethod
    def find_font_path(cls, name):
        file = f'{name}.ttf'
        for path in cls.FONT_PATHS:
            if file in os.listdir(path):
                return f'{path}/{file}'
        
    @classmethod
    def render_text(cls, message, font='pygame', tsize=20, fgcolor=(255, 255, 255), bgcolor=None, olcolor=None, width=2):
        if isinstance(font, str):
            font = cls.get_font(font)
        image, _ = font.render(message, fgcolor=fgcolor, size=tsize)
        
        if olcolor is not None:
            image = cls.add_outline(message, image, font, tsize, olcolor, width=width)
            
        if bgcolor is not None:
            bg = pg.Surface(image.get_size()).convert()
            bg.fill(bgcolor)
            bg.blit(image, (0, 0))
            image = bg

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
    def add_outline(cls, message, image, font, tsize, olcolor, width=2):
        points = cls.get_outline_points(width)
    
        w, h = image.get_size()
        w = w + 2 * width
        
        osurf = pg.Surface((w, h + 2 * width)).convert_alpha()
        osurf.fill((0, 0, 0, 0))
        surf = osurf.copy()
        outline = cls.render_text(message, font=font, tsize=tsize, fgcolor=olcolor)
        osurf.blit(outline, (0, 0))
        
        for dx, dy in points:
            surf.blit(osurf, (dx + width, dy + width))
            
        surf.blit(image, (width, width))
        image = surf
        
        return image
    
    @classmethod
    def static_textbox(cls, *args, **kwargs):
        image = cls.render_text(*args, **kwargs)
        i = Image(image)
        return i
    
    def __init__(
        self,
        message,
        font=None,
        tsize=20,
        fgcolor=(255, 255, 255),
        bgcolor=None,
        olcolor=None,
        width=2,
        anchor='center',
        fitted=False,
        allignment='c',
        **kwargs
    ):
        super().__init__()
        
        self.message = message
        self.original_message = message

        self.font = pg.freetype.Font(Textbox.find_font_path(font))
        self.font.pad = True
        self.tsize = tsize
        self.original_tsize = tsize

        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.olcolor = olcolor
        self.width = width

        self.image, self.rect = self.render(self.message, get_rect=True)
        self.anchor = anchor
        self.fitted = fitted
        self.fitted_rect = None
        self.allignment = allignment

        self.characters = []
            
        if kwargs:
            if kwargs.get('antialiased', False):
                self.set_antialiased(True)
            if kwargs.get('kerning', False):
                self.set_kerning(True)
            if kwargs.get('underline', False):
                self.set_underline(True)
            if kwargs.get('strong', False):
                self.set_strong(True)
            if kwargs.get('oblique', False):
                self.set_oblique(True)
            if kwargs.get('wide', False):
                self.set_wide(True)
                
        if message == 'test':
            print(self.__dict__)

    def __str__(self):
        return self.message
        
    def __repr__(self):
        return self.message
        
    def __eq__(self, other):
        return self.message == getattr(other, 'message', None) and self.fgcolor == getattr(other, 'fgcolor', None)
        
    def __bool__(self):
        return bool(self.message)
        
    @property
    def default_color(self):
        if sum(self.fgcolor) < 382:
            return tint(self.fgcolor, factor=1.5)
        else:
            return shade(self.fgcolor, factor=2)
   
    def set_antialiased(self, antialiased):
        self.font.antialiased = antialiased
        
    def set_kerning(self, kerning):
        self.font.kerning = kerning
        
    def set_underline(self, underline):
        self.font.underline = underline
        
    def set_strong(self, strong):
        self.font.strong = strong
        
    def set_oblique(self, oblique):
        self.font.oblique = oblique
        
    def set_wide(self, wide):
        self.font.wide = wide
        
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
        
    def set_anchor(self, anchor):
        self.anchor = anchor
        
    def set_fitted(self, fitted, rect=None):
        self.fitted = fitted
        if rect is not None:
            self.fitted_rect = rect
        else:
            self.fitted_rect = self.rect.copy()
        
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
        
    def render(self, message, get_rect=False, track_chars=False, fgcolor=None):
        if fgcolor is None:
            fgcolor = self.fgcolor
            
        image, rect = self.font.render(message, fgcolor=self.fgcolor, size=self.tsize)
        
        if self.olcolor is not None:
            image = Textbox.add_outline(message, image, self.font, self.tsize, self.olcolor, width=self.width)
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
        
    def fit_text(self, bounding_rect, tsize=None, allignment=None, new_message=None, width_only=False):
        if new_message is not None:
            self.message = new_message
        message = self.message
        
        if tsize is None:
            tsize = self.original_tsize
        if tsize > bounding_rect.height:
            tsize = bounding_rect.height
        self.set_font_size(tsize)
        
        if allignment is None:
            allignment = self.allignment

        lines = [line.split(' ') for line in message.splitlines()]
        if not message or message.endswith('\n'):
            lines.append([''])
        characters = []

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
                
        if width_only:
            max_y = rendered_lines[-1][0][2].bottom
            min_y = rendered_lines[0][0][2].top
            bounding_rect.height = max_y - min_y
                
        if self.bgcolor is None:
            image = pg.Surface(bounding_rect.size).convert_alpha()
            image.fill((0, 0, 0, 0))
        else:
            image = pg.Surface(bounding_rect.size).convert()
            image.fill(self.bgcolor)

        if rendered_lines:
        
            if allignment == 'c':   
                max_y = rendered_lines[-1][0][2].bottom
                min_y = rendered_lines[0][0][2].top
                
                h = max_y - min_y
                r = pg.Rect(0, 0, 2, h)
                r.centery = bounding_rect.height // 2
                dy = max(r.y - min_y, 0)
                
                for line in rendered_lines: 
                    max_x = max({r.right for _, _, r in line})
                    min_x = min({r.left for _, _, r in line})
                
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
        self.allignment = allignment
        self.new_image(image, rect=bounding_rect.copy(), set_pos=False)
        
    def crop_fitted(self):
        l = min({c[1].left for c in self.characters})
        r = max({c[1].right for c in self.characters})
        t = min({c[1].top for c in self.characters})
        b = max({c[1].bottom for c in self.characters})
        
        w = r - l
        h = b - t
        
        img = crop(self.image, 0, 0, w, h)
        self.new_image(img)

    def new_image(self, image, rect=None, set_pos=True):
        if rect is None:
            rect = image.get_rect()
        a = getattr(self.rect, self.anchor, self.rect.center)
        self.image = image
        self.rect = rect
        if set_pos:
            setattr(self.rect, self.anchor, a)
        self.move_characters()
        
    def update_style(self, message=None, tsize=None, fgcolor=None, bgcolor=None, olcolor=None, width=None, **kwargs): 
        if tsize is not None:
            self.tsize = tsize
        if fgcolor is not None:
            self.fgcolor = fgcolor
        if bgcolor is not None:
            self.bgcolor = bgcolor
        if olcolor is not None:
            self.olcolor = olcolor
        if width is not None:
            self.width = width
        
        if kwargs:
            if kwargs.get('antialiased'):
                self.set_antialiased(antialiased)
            if kwargs.get('kerning'):
                self.set_kerning(kerning)
            if kwargs.get('underline'):
                self.set_underline(underline)
            if kwargs.get('strong'):
                self.set_strong(strong)
            if kwargs.get('oblique'):
                self.set_oblique(oblique)
            if kwargs.get('wide'):
                self.set_wide(wide)
                
        if message is not None:
            self.set_message(message)

    def set_message(self, message):
        self.message = message
        if self.fitted:
            self.fit_text(self.rect)
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
    
    def draw(self, surf):
        if self.bgcolor is not None:
            pg.draw.rect(surf, self.bgcolor, self.rect)
        surf.blit(self.image, self.rect)
        super().draw(surf)
        
    def to_static(self):
        return Image(self.image)
        
class Button(Compound_Object):
    @classmethod
    def text_button(cls, *args, abs_fit=False, anchor_point='center', **kwargs):
        self = cls(**kwargs)
        tb = Textbox(*args, **self.get_leftover())
        if tb.fitted:
            tb.fit_text(self.padded_rect)
        self.join_object(tb, abs_fit=abs_fit, anchor_point=anchor_point)
        return self
        
    @classmethod
    def image_button(cls, *args, abs_fit=False, anchor_point='center', **kwargs):
        self = cls(**kwargs)
        i = Image(*args, **self.get_leftover())
        self.join_object(i, abs_fit=abs_fit, anchor_point=anchor_point)
        return self

    def __init__(self, color=(0, 0, 0), color2=(100, 100, 100), **kwargs):
        super().__init__(draw_rect=True, color=color, **kwargs)

        self.colors = {
            False: color,
            True: color2
        }

        self.pressed = False
        
    @property
    def active(self):
        return self.rect.collidepoint(pg.mouse.get_pos())

    @property
    def color(self):
        return self.colors[self.active]
        
    @property
    def color1(self):
        return self.colors[False]
        
    @property
    def color2(self):
        return self.colors[True]
        
    @color1.setter
    def color1(self, color):
        self.colors[False] = color
        
    @color2.setter
    def color2(self, color):
        self.colors[True] = color
            
    def get_state(self):
        return self.pressed
        
    def reset(self):
        self.pressed = False
        
    def invert(self):
        self.colors = {not k: v for k, v in self.colors.items()}

    def set_cursor(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True

    def events(self, events):
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        if mbd:
            if mbd.button == 1:
                if self.active:
                    self.pressed = True
                    self.run_func()
                    events.pop('mbd')
                
        elif mbu:
            if mbu.button == 1:
                self.pressed = False
                
        super().events(events)
        
class Input(Compound_Object):
    VALID_CHARS = set(range(32, 127))
    VALID_CHARS.add(9)
    VALID_CHARS.add(10)
    
    TK = Tk()
    TK.withdraw()
    
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
        
    @staticmethod
    def alnum_check(char):
        return char.isalnum() or char.isspace()

    def __init__(
        self,
        message='',
        default='type here',
        length=99,
        check=lambda char: True,
        full_check=lambda text: True,
        scroll=False,
        size_lock=False,
        highlight=False,
        lines=0,
        double_click=False,
        **kwargs
    ):      

        super().__init__(**kwargs)
        if not message:
            message = default
        self.textbox = Textbox(message, **self.get_leftover())
        self.textbox.fit_text(self.padded_rect)
        self.default = default
        
        self.fgcolor = self.textbox.fgcolor
        self.default_color = self.textbox.default_color

        self.scroll = scroll

        self.length = length
        self.max_lines = lines
        self.check = check
        self.full_check = full_check

        self.last_click = 0
        self.clicks = 1
        self.active = False
        self.double_click = double_click
        
        self.index = 0
        self.selecting = False
        self.selection = []
        self.hl = highlight
        
        self.btimer = 0
        self.timer = 0
        self.backspace = False
        self.bhold = False
        
        self.ctrl = False
        self.copy = False
        self.paste = False
        self.cut = False
        self.all = False

        self.update_message(self.message)

        if not self.textbox.fitted:
            anchor = 'topleft'
            offset = [self.left_pad, self.top_pad + self.special_pad]
        else:
            anchor = 'center'
            offset = [0, self.special_pad]
        self.add_child(self.textbox, anchor_point=anchor, offset=offset)
        
    @property
    def lines(self):
        return len(f'{self.message} '.splitlines())

    @property
    def message(self):
        return self.textbox.get_message()
        
    @property
    def characters(self):
        return self.textbox.characters
        
    @property
    def text_color(self):
        if self.message == self.default:
            return self.default_color
        else:
            return self.fgcolor
        
    def is_filled(self):
        return self.message != self.default

    def update_message(self, message, force=False):
        if (self.check_message(message) and len(message) <= self.length) or force:
            self.textbox.set_fgcolor(self.text_color)
            self.textbox.set_message(message)

    def check_message(self, text):
        return all({ord(char) in Input.VALID_CHARS and self.check(char) for char in text}) and self.full_check(text)

    def set_index(self, index):
        index = max({index, 0})
        index = min({index, len(self.message)})
        self.index = index
              
    def highlight_word(self):
        i = j = self.index
        m = self.message
        
        if m and i not in range(len(m)):
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
        m = self.message
        self.selection = [0, len(m)]
        self.set_index(len(m))
   
    def get_selection(self):
        if self.selection:
            i, j = self.selection
            return self.message[min(i, j):max(i, j)]
        return ''

    def replace_selection(self, text):
        m = self.message
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
                m = self.message
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
            m = self.message
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
        chars = self.characters
        i = min(range(len(chars)), key=lambda i: vec(chars[i][1].center).distance_to(p), default=0)
        r = chars[i][1]
        if p[0] - r.centerx >= 0:
            i += 1
        return i
        
    def open(self):
        m = self.message
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
                self.update_message(self.default)
            self.selection.clear()
            if self.scroll:
                self.textbox.rect.midleft = self.rect.midleft
                self.textbox.rect.x += self.left_pad
                self.textbox.set_current_offset()
                
    def clear(self):
        self.update_message('')
  
    def send_keys(self, text):
        if self.selection:
            self.replace_selection('')
        m = self.message
        message = m[:self.index] + text + m[self.index:]
        self.update_message(message)
        self.set_index(self.index + len(text))

    def shift_textbox(self):
        if self.textbox.rect.width + self.x_pad < self.rect.width:
            self.textbox.rect.topleft = (self.rect.x + self.left_pad, self.rect.y + self.top_pad + self.special_pad)  
        else:
            self.textbox.rect.y = self.rect.y + self.top_pad + self.special_pad
            chars = self.characters
            if self.index in range(len(chars)):
                r = chars[self.index][1]
                if not self.rect.collidepoint(r.center):
                    if r.centerx < self.rect.left:
                        dx = self.rect.left - r.left
                    else:
                        dx = self.rect.right - r.right
                    self.textbox.rect.x += dx
                if self.textbox.rect.right < self.rect.right and self.textbox.rect.left < self.rect.left:
                    self.textbox.rect.right = self.rect.right - self.right_pad
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
                    if not self.double_click:
                        self.open()                       
                else:
                    self.selecting = True
                    i = self.get_closest_index(p=p)
                    self.set_index(i)
                if not self.hl:
                    self.selection.clear()
                
            elif clicks == 2:
                if not self.active and self.double_click:
                    self.open()
                else:
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

            for e in events.get('all'):
            
                if e.type == pg.KEYDOWN:
                    kd = e

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
                            self.run_func()
                            self.close()
                        elif not self.scroll and self.lines < self.max_lines:
                            self.send_keys('\n')
                            
                    elif kd.key == pg.K_TAB:
                        self.send_keys('    ')
                        sent = True
                            
                    if not sent:
                        if not (self.ctrl or self.backspace) and hasattr(kd, 'unicode'):
                            char = kd.unicode
                            if char:
                                self.send_keys(char)
                                
                elif e.type == pg.KEYUP:
                    ku = e
                
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

        if self.scroll and self.active:
            self.shift_textbox()

        super().update()
        
    def draw(self, surf):
        self.draw_rect(surf)

        surf.set_clip(self.rect)
        if self.selection:
            chars = self.characters[:-1]
            i, j = self.selection
            for _, r, _ in chars[min(i, j):max(i, j)]:
                pg.draw.rect(surf, (0, 102, 255), r.move(0, -self.special_pad))
        self.textbox.draw(surf)
        surf.set_clip(None)

        if self.active and self.timer > 0:
            chars = self.characters
            if chars:
                if self.index in range(len(chars)):
                    r = chars[self.index][1].move(0, -self.special_pad)
                    pg.draw.line(surf, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
            else:
                r = self.textbox.get_text_rect(' ')
                if self.textbox.fitted:
                    r.center = (self.rect.centerx, self.rect.centery - self.special_pad)
                    pg.draw.line(surf, self.textbox.fgcolor, r.midtop, r.midbottom, width=2)
                else:
                    r.midleft = (self.rect.x, self.rect.centery - self.special_pad)
                    pg.draw.line(surf, self.textbox.fgcolor, r.topleft, r.bottomleft, width=2)
  
class Text_Flipper(Compound_Object):
    @classmethod
    def counter(cls, ran, **kwargs):
        return cls([str(i) for i in ran], **kwargs)
 
    def __init__(self, selection, index=0, size=(1, 1), text_kwargs={}, **kwargs):
        super().__init__(**kwargs)
        self.rect = pg.Rect(0, 0, size[0], size[1])
        
        self.selection = selection
        self.index = index
        self.textbox = Textbox(self.selection[index], **text_kwargs)
        
        left_arrow = get_arrow('l', (15, 15))
        right_arrow = pg.transform.flip(left_arrow, True, False)
        self.left_button = Button.image_button(left_arrow, func=self.flip, args=[-1])
        self.right_button = Button.image_button(right_arrow, func=self.flip, args=[1])

        self.add_child(self.left_button, anchor_point='midleft', offset=(-self.left_button.rect.width, 0))
        self.add_child(self.textbox, anchor_point='center')
        self.add_child(self.right_button, anchor_point='midright', offset=(self.right_button.rect.width, 0))
        
    @property
    def current_value(self):
        return self.selection[self.index]
        
    def flip(self, dir):
        self.index = (self.index + dir) % len(self.selection)
        self.textbox.set_message(self.current_value)
        self.run_func()
        
class Image_Flipper(Compound_Object):
    def __init__(self, selection, index=0, size=None, **kwargs):
        super().__init__(**kwargs)
        
        if size is None:
            w = max({i.rect.width for i in selection})
            h = max({i.rect.height for i in selection})
            size = (w, h)
        self.rect = pg.Rect(0, 0, size[0], size[1])
        
        self.selection = selection
        self.index = index

        left_arrow = get_arrow('l', (15, 15))
        right_arrow = pg.transform.flip(left_arrow, True, False)
        self.left_button = Button.image_button(left_arrow, func=self.flip, args=[-1])
        self.right_button = Button.image_button(right_arrow, func=self.flip, args=[1])

        self.add_child(self.left_button, anchor_point='midleft', offset=(-self.left_button.rect.width, 0))
        self.add_child(self.current_value, anchor_point='center')
        self.add_child(self.right_button, anchor_point='midright', offset=(self.right_button.rect.width, 0))
        
    @property
    def current_value(self):
        return self.selection[self.index]
        
    def flip(self, dir):
        self.remove_child(self.current_value)
        self.index = (self.index + dir) % len(self.selection)
        self.add_child(self.current_value, anchor_point='center')
        self.run_func()
        
class Slider(Compound_Object):
    def __init__(self, size, ran, dir='x', handel_size=None, color=(255, 255, 255), hcolor=(0, 0, 0), flipped=False, contained=False, **kwargs):
        super().__init__(**kwargs)
        self.rect = pg.Rect(0, 0, size[0], size[1])
        self.color = color

        if dir == 'x':
            if handel_size is None:
                handel_size = (10, self.rect.height * 2)
            anchor = 'midleft'
        elif dir == 'y':    
            if handel_size is None:
                handel_size = (self.rect.width * 2, 10)
            anchor = 'midtop'
            
        self.handel = Position.rect(pg.Rect(0, 0, handel_size[0], handel_size[1]))
        self.handel_color = hcolor
        
        self.held = False
        self.flipped = False
        self.contained = contained
        
        self.range = ran
        self.dir = dir

        if flipped:
            self.flip()
            
        self.add_child(self.handel, anchor_point=anchor)

        self.set_state_as_ratio(0)
        
    def flip(self):
        self.flipped = not self.flipped
        
    def adjust_handel(self):
        if self.dir == 'x':
            self.handel.rect.centery = self.rect.centery
            if not self.contained:
            
                if self.handel.rect.centerx > self.rect.right:
                    self.handel.rect.centerx = self.rect.right
                elif self.handel.rect.centerx < self.rect.left:
                    self.handel.rect.centerx = self.rect.left
                    
            else:
                
                if self.handel.rect.right > self.rect.right:
                    self.handel.rect.right = self.rect.right
                elif self.handel.rect.left < self.rect.left:
                    self.handel.rect.left = self.rect.left
      
        elif self.dir == 'y':
            self.handel.rect.centerx = self.rect.centerx
            if not self.contained:
            
                if self.handel.rect.centery > self.rect.bottom:
                    self.handel.rect.centery = self.rect.bottom
                elif self.handel.rect.centery < self.rect.top:
                    self.handel.rect.centery = self.rect.top
                    
            else:
                
                if self.handel.rect.bottom > self.rect.bottom:
                    self.handel.rect.bottom = self.rect.bottom
                elif self.handel.rect.top < self.rect.top:
                    self.handel.rect.top = self.rect.top
                    
        self.handel.set_current_offset()

    def get_state(self):
        ratio = self.get_state_as_ratio()
        full = len(self.range)
        shift = self.range[0]
        state = (full * ratio) + shift
        return round(state)
        
    def get_state_as_ratio(self):
        self.adjust_handel()
        
        if self.dir == 'x':
            dx = self.handel.rect.centerx - self.rect.x
            ratio = dx / self.rect.width 
        elif self.dir == 'y':
            dy = self.handel.rect.centery - self.rect.y
            ratio = dy / self.rect.height
            
        if self.flipped:
            ratio = 1 - ratio
            
        return ratio
            
    def set_state(self, value):
        state = round(value)
        full = len(self.range)
        shift = self.range[0]
        ratio = (state - shift) / full
        self.set_state_as_ratio(ratio)
        
    def set_state_as_ratio(self, ratio):
        if self.flipped:
            ratio = 1 - ratio
            
        if self.dir == 'x':   
            dx = ratio * self.rect.width
            self.handel.rect.centerx = dx + self.rect.x
        elif self.dir == 'y':
            dy = ratio * self.rect.height
            self.handel.rect.centery = dy + self.rect.y
        self.adjust_handel()
  
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
        super().update()
        if self.held:
            p = pg.mouse.get_pos()
            self.handel.rect.center = p
            self.adjust_handel()
            self.run_func()

    def draw(self, surf):
        pg.draw.rect(surf, self.color, self.rect)
        pg.draw.rect(surf, self.handel_color, self.handel.rect)
        super().draw(surf)

class Check_Box(Compound_Object):
    def __init__(self, size=15, state=True, **kwargs):
        super().__init__(**kwargs)
        self.rect = pg.Rect(0, 0, size, size)
        self.state = state
        self.icon = Textbox.static_textbox(icons['check'], font='icons', tsize=size - 2, fgcolor=(0, 0, 0))
        self.add_child(self.icon, anchor_point='center')
        
    def set_cursor(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True
        
    def set_state(self, state):
        self.state = state
        self.icon.set_visible(state)
        
    def get_state(self):
        return self.state
        
    def flip_state(self):
        self.set_state(not self.state)
        
    def events(self, events):
        p = events['p']
        mbd = events.get('mbd')
        
        if mbd:
            if self.rect.collidepoint(p):
                self.flip_state()
                self.run_func()
                
        super().events(events)
        
    def draw(self, surf):
        pg.draw.rect(surf, (0, 0, 0), self.rect.inflate(2, 2))
        pg.draw.rect(surf, (255, 255, 255), self.rect)
            
        super().draw(surf)
        
        
        
        
        
        