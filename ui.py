import pygame as pg
from pygame.math import Vector2 as vec
from tkinter import Tk

def copy_to_clipboard(text):
    Tk().clipboard_append(text)
    
def get_clip():
    try:
        text = Tk().clipboard_get()    
    except:
        text = ''
        
    return text

def outline_points(r):
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
    
    return points

def create_text(message, size=10, color=(255, 255, 255), bgcolor=None, olcolor=None, r=2):
    font = 'freesansbold.ttf'

    text_font = pg.font.Font(font, size)
    text = text_font.render(message, size, color).convert_alpha()
    
    if olcolor is not None:
        
        w, h = text.get_size()
        w = w + 2 * r
        
        osurf = pg.Surface((w, h + 2 * r)).convert_alpha()
        osurf.fill((0, 0, 0, 0))
        surf = osurf.copy()
        outline = create_text(message, size, color=olcolor)
        osurf.blit(outline, (0, 0))
        
        for dx, dy in outline_points(r):
            
            surf.blit(osurf, (dx + r, dy + r))
            
        surf.blit(text, (r, r))
        text = surf
    
    if bgcolor is not None:
        
        bg = pg.Surface(text.get_size()).convert()
        bg.fill(bgcolor)
        bg.blit(text, (0, 0))
        
        text = bg

    return text

def fit_text(rect, text, tcolor=(255, 255, 255), bgcolor=(0, 0, 0, 0), olcolor=None):
    surf = pg.Surface(rect.size).convert_alpha()
    surf.fill(bgcolor)
    
    rect = surf.get_rect()
    
    if text.strip():
    
        text = text.split()
        
        if len(text) > 1:
            
            for i in range(1, len(text)):
                
                text[i] = ' ' + text[i]

        tsize = rect.height
        i = 0
        
        while i < len(text):

            i = 0
            x = 0
            y = 0 
            lines = []
            line = []

            for word in text:
                
                textbox = create_text(word, size=tsize, color=tcolor, olcolor=olcolor)
                r = textbox.get_rect()
                r.topleft = (x, y)
                
                if r.right > rect.right:
                    
                    lines.append(line.copy())
                    line.clear()
                    
                    x = 0
                    y += r.height
                    
                    textbox = create_text(word.replace(' ', ''), size=tsize, color=tcolor, olcolor=olcolor)
                    r = textbox.get_rect()
                    r.topleft = (x, y)

                if not rect.contains(r):
                    
                    tsize -= 1

                    break
                    
                else:
                    
                    line.append((word, textbox, r))
                    
                    x += r.width
                    i += 1
                    
        lines.append(line.copy())
        
        total_height = sum(line[0][2].height for line in lines)
        r = pg.Rect(0, 0, 1, total_height)
        r.centery = rect.centery
        dy = r.y - lines[0][0][2].y
                    
        for line in lines:
            
            total_width = sum(l[2].width for l in line)
            r = pg.Rect(0, 0, total_width, 1)
            r.centerx = rect.centerx
            dx = r.x - line[0][2].x
            
            for word, textbox, trect in line:
                
                x, y = trect.topleft
                surf.blit(textbox, (x + dx, y + dy))

    return surf

def rect_outline(img, color=(0, 0, 0), ol_size=2):
    ol = img.copy()
    ol.fill(color)

    w, h = img.get_size()
    img = pg.transform.scale(img, (w - (ol_size * 2), h - (ol_size * 2)))
    ol.blit(img, (ol_size, ol_size))
    
    return ol
    
def get_rate(p0, p1, rate):
    x0, y0 = p0
    x1, y1 = p1
    
    dx = x1 - x0
    dy = y1 - y0
    d = pow(pow(dx, 2) + pow(dy, 2), 0.5)
    
    if dx != 0:
        rx = d / dx
        vx = rate / rx
    else:
        rx = 0
        vx = 0
        
    if dy != 0:
        ry = d / dy
        vy = rate / ry
    else:
        ry = 0
        vy = 0
        
    steps = 1 / (rate * d)
  
    return (steps, [vx, vy])

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
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        
    def events(self, input):
        pass
        
    def update(self):
        pass
        
    def draw(self, win):
        win.blit(self.image, self.rect)

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

class Textbox(Mover):
    def __init__(self, message, tsize=10, tcolor=(255, 255, 255), bgcolor=None, olcolor=None, r=2, anchor='center', font='freesansbold.ttf'):
        self.message = message
        self.original_message = message
        
        self.font = font
        self.text_font = pg.font.Font(font, tsize)

        self.tsize = tsize
        self.tcolor = tcolor
        self.olcolor = olcolor
        self.olrad = r
        self.bgcolor = bgcolor
        
        self.olcache = {}
        
        self.image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.rect = self.image.get_rect()
        self.anchor = anchor
        
        self.timer = 0
        
        super().__init__()
        
    def __str__(self):
        return self.get_message()
        
    def __repr__(self):
        return self.get_message()
        
    def __eq__(self, other):
        return self.message == other.message and self.tcolor == other.tcolor

    def set_message_timer(self, message, timer):
        self.update_message(message)
        self.timer = timer

    def outline_points(self, r):
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
            
        return points
        
    def new_image(self, image):
        a = getattr(self.rect, self.anchor, self.rect.topleft)
        self.image = image
        self.rect = self.image.get_rect()
        setattr(self.rect, self.anchor, a)
        
    def update_font(self, tsize=None, font=None):
        if tsize is None:
            tsize = self.tsize
        if font is None:
            font = self.font
            
        self.text_font = pg.font.Font(font, tsize)
        self.tsize = tsize
        self.font = font

    def create_text(self, message, tsize=10, tcolor=(255, 255, 255), bgcolor=None, olcolor=None, r=2):
        text = self.text_font.render(message, tsize, tcolor).convert_alpha()
        
        if olcolor is not None:
            
            w, h = text.get_size()
            w = w + 2 * r
            
            osurf = pg.Surface((w, h + 2 * r)).convert_alpha()
            osurf.fill((0, 0, 0, 0))
            surf = osurf.copy()
            outline = self.create_text(message, tsize=tsize, tcolor=olcolor)
            osurf.blit(outline, (0, 0))
            
            for dx, dy in outline_points(r):
                
                surf.blit(osurf, (dx + r, dy + r))
                
            surf.blit(text, (r, r))
            text = surf
        
        if bgcolor is not None:
            
            bg = pg.Surface(text.get_size()).convert()
            bg.fill(bgcolor)
            bg.blit(text, (0, 0))
            
            text = bg

        return text
        
    def multicolor(self, colors):
        chars = []
        message = self.get_message()
        
        width = 0
        j = 0
        
        for i in range(len(message)):
            
            char = message[i]
            color = colors[j % len(colors)]
            
            img = self.create_text(char, tsize=self.tsize, tcolor=color, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
            r = img.get_rect()
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
        
    def get_char_rect(self, char):
        return self.text_font.size(char)

    def set_anchor(self, anchor):
        self.anchor = anchor

    def fit_text(self, rect):
        if self.rect.size == rect.size:
            return 
            
        surf = pg.Surface(rect.size).convert_alpha()
        
        if self.bgcolor is not None:
            surf.fill(self.bgcolor)
        else:
            surf.fill((0, 0, 0, 0))

        rect = surf.get_rect()
        text = self.message
        tsize = rect.height
        
        if text.strip():
        
            text = text.split()
            
            if len(text) > 1:
                for i in range(1, len(text)):  
                    text[i] = ' ' + text[i]

            tsize = rect.height
            self.update_font(tsize=tsize)
            i = 0
            
            while i < len(text):

                i = 0
                x = 0
                y = 0 
                lines = []
                line = []

                for word in text:
                    
                    r = pg.Rect(0, 0, 0, 0)
                    r.size = self.text_font.size(word)
                    r.topleft = (x, y)
                    
                    if r.right > rect.right:
                        
                        lines.append(line.copy())
                        line.clear()
                        
                        x = 0
                        y += r.height
                        
                        r = pg.Rect(0, 0, 0, 0)
                        r.size = self.text_font.size(word)
                        r.topleft = (x, y)

                    if not rect.contains(r):
                        
                        tsize -= 1
                        self.update_font(tsize=tsize)

                        break
                        
                    else:
                        
                        line.append((word, r))
                        
                        x += r.width
                        i += 1
                        
            lines.append(line.copy())
            
            total_height = sum(line[0][1].height for line in lines)
            r = pg.Rect(0, 0, 1, total_height)
            r.centery = rect.centery
            dy = r.y - lines[0][0][1].y
                        
            for line in lines:
                
                total_width = sum(l[1].width for l in line)
                r = pg.Rect(0, 0, total_width, 1)
                r.centerx = rect.centerx
                dx = r.x - line[0][1].x
                
                for word, r in line:
                    
                    img = self.create_text(word, tsize=tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
                    
                    x, y = r.topleft
                    surf.blit(img, (x + dx, y + dy))

        self.new_image(surf)
        self.tsize = tsize
        
    def resize(self, tsize):
        self.tsize = tsize
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
        
    def scale(self, width=None, height=None):
        if width is None:
            width = self.rect.width
        if height is None:
            height = self.rect.height
            
        img = pg.transform.scale(self.image, (int(width), int(height)))
        self.new_image(img)
        
    def update_all(self, message=None, tsize=None, tcolor=None, bgcolor=None, olcolor=None, r=None):
        p = getattr(self.rect, self.anchor)
        
        if message is not None:
            self.message = message
        
        if tsize is not None:
            self.tsize = tsize
            
        if tcolor is not None:
            self.tcolor = tcolor
            
        if bgcolor is not None:
            self.bgcolor = bgcolor
            
        if olcolor is not None:
            self.olcolor = olcolor
            
        if r is not None:
            self.olrad = r

        self.image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.rect = self.image.get_rect()
        
        setattr(self.rect, self.anchor, p)
        
    def add_background(self, bgcolor):
        self.bgcolor = bgcolor
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
        
    def remove_background(self):
        self.bgcolor = (0, 0, 0, 0)
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
        
    def add_outline(self, olcolor, r=2):
        self.olcolor = olcolor
        self.olrad = r
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
        
    def remove_outline(self):
        self.olcolor = None
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
       
    def set_color(self, tcolor):
        self.tcolor = tcolor
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
       
    def update_message(self, message):
        self.message = message
        image = self.create_text(self.message, tsize=self.tsize, tcolor=self.tcolor, bgcolor=self.bgcolor, olcolor=self.olcolor, r=self.olrad)
        self.new_image(image)
        
    def clear(self):
        self.update_message('')
        
    def reset(self):
        self.self.bgcolor = None
        self.olcolor = None
        
        image = self.create_text(self.message, tsize=self.size, tcolor=self.tcolor)
        self.new_image(image)
        
    def get_message(self):
        return self.message
        
    def get_image(self):
        return self.image
        
    def is_outlined(self):
        return self.olcolor is not None
        
    def is_color(self, color):
        return self.tcolor == color
        
    def events(self, input):
        pass
        
    def update(self):
        self.move()
        
        if self.timer != 0:
            self.timer -= 1
            if self.timer == 0:
                self.clear()
        
    def draw(self, win):
        win.blit(self.get_image(), self.rect)
       
class Button:
    def __init__(self, size, message, color1=(0, 0, 0), color2=(100, 100, 100), tcolor=(255, 255, 255), border_radius=10, tag='', func=lambda: None, args=[], kwargs={}):
        self.rect = pg.Rect(0, 0, size[0], size[1])
        r = self.rect.copy()
        r.width -= 5
        r.height -= 5
        self.text_rect = r
        self.textbox = Textbox(message, tsize=r.height, tcolor=tcolor)
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
        
    def reset(self):
        self.pressed = False
        
    def events(self, input):
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
        pg.draw.rect(win, self.current_color, self.rect, border_radius=self.border_radius)
        self.textbox.draw(win)
        
    def get_message(self):
        return self.textbox.get_message()
        
    def update_message(self, message, tcolor=None):    
        self.textbox.update_message(message)
        if tcolor is not None:
            self.textbox.set_color(tcolor)
            
        self.textbox.fit_text(self.text_rect)

class Input(Textbox):
    def __init__(self, size, message='', color=(0, 0, 0), tsize=None, tcolor=(255, 255, 255), length=99, check=lambda char: True, fitted=False):
        self.size = size
        self.tsize = self.size[1] if tsize is None else tsize

        self.default_message = message
        self.message = message
        
        self.textbox = Textbox(self.message, tsize=self.tsize, tcolor=tcolor)

        self.image = pg.Surface(self.size).convert_alpha()
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        
        self.active = False
        
        self.timer = 25
        
        self.btimer = 0
        self.backspace = False
        
        self.length = length
        self.check = check
        self.paste = [0, 0]
        
        self.fitted = fitted
        
        self.update_message(self.get_message())
        
    def clear(self):
        self.update_message('')
        
    def update_message(self, message, tcolor=None):
        if tcolor:
            
            self.tcolor = tcolor
    
        self.message = message
        self.textbox.update_message(self.message)
        
        if self.fitted:
        
            self.textbox.fit_text(self.rect)
        
    def reset(self):
        self.update_message(self.default_message)
        
    def get_message(self):
        return self.message.replace('|', '')
        
    def close(self):
        m = self.get_message()
        
        if not m.strip():
            
            m = self.default_message
        
        self.update_message(m)
        
    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input:
        
            if e.type == pg.MOUSEBUTTONDOWN:
                
                if self.rect.collidepoint(p) or self.textbox.rect.collidepoint(p):
                    
                    self.active = True
                    
                else:

                    self.active = False
                    self.close()
                    
            elif self.active:

                if e.type == pg.KEYDOWN:
                    
                    if e.key == pg.K_BACKSPACE:
                        
                        self.backspace = True
                        
                    elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                        
                        self.paste[0] = 1
                            
                    elif e.key == pg.K_v:
                        
                        self.paste[1] = 1
                        
                    elif e.key == pg.K_SPACE:
                        
                        self.send_keys(' ')
                    
                    elif hasattr(e, 'unicode'):
                        
                        char = e.unicode.strip()
                        
                        self.send_keys(char)
                            
                elif e.type == pg.KEYUP:
                    
                    if e.key == pg.K_BACKSPACE:
                        
                        self.backspace = False
                    
                    elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    
                        self.paste[0] = 0
                            
                    elif e.key == pg.K_v:
                        
                        self.paste[1] = 0
                        
        if all(self.paste):
            
            text = self.get_clip()
            self.send_keys(text)
            
        elif self.backspace:
            
            self.delete()
            
    def get_clip(self):
        try:
        
            text = Tk().clipboard_get()
            
        except:
            
            text = None
            
        return text
                            
    def send_keys(self, text):
        if text and all(self.check(char) for char in text):

            if len(self.get_message()) < self.length or len(text) == 0:

                self.update_message(self.get_message() + text)
            
    def delete(self):
        if self.btimer <= 0:
        
            self.update_message(self.get_message()[:-1])
            self.btimer = 3
            
    def update(self):
        self.timer -= 1
        self.btimer -= 1
    
        if self.active and self.timer <= 0:

            if '|' in self.message:
                
                self.update_message(self.message[:-1])
                
            else:
                
                self.update_message(self.message + '|') 
    
            self.timer = 25
            
        self.textbox.rect.topleft = self.rect.topleft
        
    def draw(self, win):
        win.blit(self.image, self.rect)
        self.textbox.draw(win)

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
    def __init__(self, size, label='', color=(0, 0, 0, 0), tsize=25, tcolor=(255, 255, 255)):
        self.size = size
        
        self.image = pg.Surface(self.size).convert_alpha()
        self.color = color
        self.image.fill(self.color)

        self.message = label
        self.label = fit_text(pg.Rect(0, 0, self.size[0], tsize), self.message, tcolor=tcolor)
        self.tab = self.label.get_rect()
        
        self.rect = self.image.get_rect()
        
        self.ctimer = 0
        
        self.scroll_buttons = (Button((self.rect.width, 20), '^', color1=(0, 0, 0), color2=(0, 0, 0),
                                       func=self.scroll, args=['u'], border_radius=0), 
                               Button((self.rect.width, 20), 'v', color1=(0, 0, 0), color2=(0, 0, 0),
                                       func=self.scroll, args=['d'], border_radius=0))

        self.objects = []
        
        self.orientation_cache = {'xpad': 5, 'ypad': 5, 'dir': 'y', 'pack': False}
                
    def is_same(self, objects):
        if len(objects) == len(self.objects):
            return all(objects[i] == self.objects[i] for i in range(len(objects)))
        else:
            return False
  
    def join_objects(self, objects, xpad=5, ypad=5, dir='y', pack=False, force=False, scroll=False, move=False, key=None):
        if key is None:
            same = self.is_same(objects)
        else:
            same = key(objects, self.objects)

        if not same or force:

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
        
    def add_waits(self, object):
        self.waits.append(object)
        
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
                    
                self.redraw()

            elif dir == 'u' and self.can_scroll_up():
            
                for o in self.objects:
                    
                    o.rect.y += 25
                
                self.redraw()
                
    def redraw(self):
        if self.color:
            
            self.image.fill(self.color)
            
        for o in self.objects:
            
            dx = o.rect.x - self.rect.x
            dy = o.rect.y - self.rect.y

            tl = o.rect.topleft 
            o.rect.topleft = (dx, dy)
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
                        
    def update(self):
        self.scroll_buttons[0].rect.midtop = self.rect.midtop
        self.scroll_buttons[1].rect.midbottom = self.rect.midbottom
        self.tab.midbottom = self.rect.midtop
        
        for b in self.scroll_buttons:
            b.update()
        
    def draw(self, win):
        if self.color != (0, 0, 0, 0) or self.objects:
            win.blit(self.image, self.rect)
            
        win.blit(self.label, self.tab)
        
        if self.can_scroll_up():
            self.scroll_buttons[0].draw(win)
        if self.can_scroll_down():
            self.scroll_buttons[1].draw(win)
        
class Popup(Pane):
    def __init__(self, size, slide_dir='u', label='', color=(0, 0, 0, 0), tsize=15, tcolor=(255, 255, 255)):
        super().__init__(size, label, color, tsize, tcolor)
        
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
    def __init__(self, ran, size, bcolor=(255, 255, 255), hcolor=(0, 0, 0)):
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
            
            if self.flipped:
                ratio = 1 - ratio

            full = len(self.range)
            shift = self.range[0]

            state = (full * ratio) + shift

            return round(state)
            
        elif self.orientation == 'y':

            dy = self.handel.centery - self.rect.y
            ratio = dy / self.rect.height
            
            if self.flipped:
                ratio = 1 - ratio

            full = len(self.range)
            shift = self.range[0]

            state = (full * ratio) + shift

            return round(state)

    def flip(self):
        self.flipped = True

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
            
        self.collision()
            
    def draw(self, win):
        pg.draw.rect(win, self.bcolor, self.rect)
        pg.draw.rect(win, self.hcolor, self.handel)
        
class RGBSlider(Slider):
    def __init__(self, size, rgb, hcolor=None, flipped=True):
        super().__init__(range(255), size)
        
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
