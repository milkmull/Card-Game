import json

import pygame as pg

import ui
from constants import *

class Draw_Lines(ui.Base_Object):
    def __init__(self, points, color=(0, 0, 0), width=3):
        super().__init__()
        
        self.points = points
        self.color = color
        self.width = width
        
    def set_color(self, color):
        self.color = color
        
    def set_points(self, points):
        self.points = points
    
    def draw(self, surf):
        pg.draw.lines(surf, self.color, False, self.points, width=self.width)

def error_screen(errors):
    objects = []
    
    body = pg.Rect(0, 0, 500, 300)
    upper = pg.Rect(0, 0, 500, 250)
    lower = pg.Rect(0, 100, 500, 50)
    outline = pg.Rect(0, 0, body.width + 10, body.height + 10)
    
    s = pg.Surface(outline.size).convert()
    pg.draw.rect(s, (255, 255, 255), outline, border_radius=10)
    body.center = outline.center
    pg.draw.rect(s, (100, 100, 100), body, border_radius=10)
    lower.bottomleft = body.bottomleft
    pg.draw.rect(s, (50, 50, 50), lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
    i = ui.Image(s)
    i.rect.center = (width // 2, height // 2)
    objects.append(i)
    
    body.center = (width // 2, height // 2)
    upper.topleft = body.topleft
    lower.bottomleft = body.bottomleft
    
    num = len(errors)
    if num:
        text_rect = pg.Rect(0, 0, 200, 25)
        text_rect.center = upper.center
        
        if len(errors) < 6:
            message = f"{num} error{'s' if num > 1 else ''} found:"
        else:
            message = '5+ errors found:'
        
        t = ui.Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25, allignment='l')
        t.rect.topleft = upper.topleft
        t.rect.x += 10
        t.rect.y += 10
        objects.append(t)
        
        x = t.rect.left
        y = t.rect.bottom + 10
        text_rect = pg.Rect(0, 0, body.width, 30)
        
        for err in errors[:5]:
            t = ui.Textbox(err, olcolor=(0, 0, 0))
            t.fit_text(text_rect, tsize=25, allignment='l')
            t.rect.topleft = (x, y)
            objects.append(t)
            
            y += text_rect.height + 10
            rx = t.rect.left - i.rect.left
            ry = t.rect.top - i.rect.top
            pg.draw.line(i.image, (0, 0, 0), (rx, ry + t.rect.height + 5), (i.rect.width - rx, ry + t.rect.height + 5), width=2)

    else:
        text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
        text_rect.center = upper.center
        message = 'all tests passed, no errors found!'
        t = ui.Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25)
        t.rect.center = text_rect.center
        objects.append(t)
    
    b = ui.Button.text_button('ok', color2=(0, 200, 0), tag='break')
    b.rect.center = lower.center
    objects.append(b)

    return objects
    
def info_menu(n):
    objects = []
    n = type(n)(None, -1)
    n.set_enabled(False)

    with open('data/node_info.json', 'r') as f:
        data = json.load(f)    
    data = data.get(n.name, {})

    title = ui.Textbox(n.get_name(), tsize=35)
    title.rect.topleft = (30, 20)
    objects.append(title)
    
    info_rect = pg.Rect(0, 0, 400, 200)
    info_surf = pg.Surface(info_rect.size).convert()
    pg.draw.rect(info_surf, (255, 255, 255), info_rect, width=3, border_radius=10)
    info_rect.topleft = (30, 150)
    i = ui.Image(info_surf)
    i.rect = info_rect.copy()
    objects.append(i)
    
    label = ui.Textbox('info:', tsize=20)
    label.rect.bottomleft = info_rect.topleft
    label.rect.x += 10
    label.rect.y -= 5
    objects.append(label)
    
    node_info = ui.Textbox(data.get('info', ''))
    node_info.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
    node_info.rect.center = info_rect.center
    
    if data.get('tips'):
    
        node_tips = ui.Textbox(data['tips'])
        node_tips.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
        node_tips.rect.center = info_rect.center
        
        node_text = ui.Image(node_info.image)
        node_text.rect.center = info_rect.center
        objects.append(node_text)
        
        def update_info():
            if label.get_message() == 'info:':
                label.set_message('tips:')
                node_text.image = node_tips.image
            else:
                label.set_message('info:')
                node_text.image = node_info.image
                
        b = ui.Button.text_button('>', padding=(15, 15), func=update_info, border_radius=20)
        b.rect.midleft = info_rect.midright
        objects.append(b)
    
    else:
        objects.append(node_info)

    port_rect = pg.Rect(0, 0, 300, 200)
    w, h = port_rect.size
    port_surf = pg.Surface(port_rect.size).convert()
    port_surf.fill((1, 1, 1))
    port_info_rect = pg.Rect(5, 20, w - 10, h - 25)
    pg.draw.rect(port_surf, (0, 0, 0), port_info_rect)
    port_surf.set_colorkey((1, 1, 1))
    port_box = ui.Image(port_surf, bgcolor=(100, 100, 100))
    port_box.rect = port_rect.copy()
    port_box.rect.topleft = (650, 100)
    objects.append(port_box)
    
    port_label_rect = pg.Rect(0, 0, w, 20)
    port_label_rect.midtop = port_box.rect.midtop
    port_info_rect.midtop = port_label_rect.midbottom
    port_info_rect.inflate_ip(-10, -5)

    port_data = []
    port_index = [0]
    for p in n.ports:
        info_text = data.get('ports', {}).get(str(p.port))
        if info_text is None:
            continue
        d = {'port': p, 'color': p.get_color(p.types)}
        p_label = ui.Textbox(f'Port {p.port}', fgcolor=(0, 0, 0))
        p_label.fit_text(port_label_rect, tsize=20, allignment='l')
        d['label'] = p_label.image
        p_info = ui.Textbox(info_text)
        p_info.fit_text(port_info_rect, tsize=15, allignment='l')
        d['info'] = p_info.image
        port_data.append(d)

    n.rect.midtop = port_box.rect.midbottom
    n.rect.y += 100
    n.set_port_pos()
    objects.append(n)
        
    if port_data:
        
        port_label = ui.Image(port_data[0]['label'])
        port_label.rect.center = port_label_rect.center
        port_label.rect.x += 5
        objects.append(port_label)
        port_info = ui.Image(port_data[0]['info'])
        port_info.rect.center = port_info_rect.center
        objects.append(port_info)
        port_box.set_background(port_data[0]['color'])

        def update_points(port):
            start = port.rect.center
            end = port_box.rect.midbottom
            
            xs, ys = start
            xe, ye = end
            
            if port.port > 0:
                return (start, (xs - 20, ys), (xs - 20, n.rect.top - 50), (port_box.rect.centerx, n.rect.top - 50), end)
            else:
                return (start, (xs + 20, ys), (xs + 20, n.rect.top - 50), (port_box.rect.centerx, n.rect.top - 50), end)
                
        points = update_points(port_data[0]['port'])
        o = Draw_Lines(points, color=port_data[0]['color'])
        objects.append(o)
        
        if len(port_data) > 1:
        
            def update_port_info(port_index, dir=None, i=None):
                if i is None:
                    port_index[0] = (port_index[0] + dir) % len(port_data)
                else:
                    port_index[0] = i
                d = port_data[port_index[0]]
                port_label.image = d['label']
                port_info.image = d['info']
                port_box.set_background(d['color'])
                o.set_color(d['color'])
                o.set_points(update_points(d['port']))
                
            b = ui.Button.text_button('>', padding=(15, 15), func=update_port_info, args=[port_index], kwargs={'dir': 1}, border_radius=20)
            b.rect.midleft = port_box.rect.midright
            objects.append(b)
            b = ui.Button.text_button('<', padding=(15, 15), func=update_port_info, args=[port_index], kwargs={'dir': -1}, border_radius=20)
            b.rect.midright = port_box.rect.midleft
            objects.append(b)
            
            for i, pd in enumerate(port_data):
                r = pd['port'].rect
                b = ui.Button(r.size, func=update_port_info, args=[port_index], kwargs={'i': i})
                b.rect.center = r.center
                objects.insert(0, b)
                
    else:
        objects.pop(-2)

    b = ui.Button.text_button('back', color2=(0, 200, 0), tag='break')
    b.rect.centerx = width // 2
    b.rect.bottom = height - 10
    objects.append(b)
    
    return objects
    
def log_menu(name, data):
    objects = []
    
    title = ui.Textbox.static_textbox(name, tsize=35)
    title.rect.topleft = (30, 20)
    objects.append(title)
    
    info_rect = pg.Rect(0, 0, 400, 200)
    info_surf = pg.Surface(info_rect.size).convert()
    pg.draw.rect(info_surf, (255, 255, 255), info_rect, width=3, border_radius=10)
    info_rect.topleft = (30, 150)
    i = ui.Image(info_surf)
    i.rect = info_rect.copy()
    objects.append(i)
    
    label = ui.Textbox.static_textbox('info:', tsize=20)
    label.rect.bottomleft = info_rect.topleft
    label.rect.x += 10
    label.rect.y -= 5
    objects.append(label)
    
    node_info = ui.Textbox(data['info'])
    node_info.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
    node_info.rect.center = info_rect.center
    objects.append(node_info)
    
    key_tb = ui.Textbox.static_textbox('key')
    key_tb.rect.topleft = (width // 2, 40)
    objects.append(key_tb)
    
    value_tb = ui.Textbox.static_textbox('return value')
    value_tb.rect.x = key_tb.rect.right + 30
    value_tb.rect.y = key_tb.rect.y
    objects.append(value_tb)
    
    value_rect = value_tb.rect.inflate(150, 50)
    
    y = value_tb.rect.bottom + 20
    
    for key, value in data['data'].items():
        k = ui.Textbox.static_textbox(key)
        k.rect.right = key_tb.rect.right
        k.rect.y = y
        objects.append(k)
        
        v = ui.Textbox(value)
        v.fit_text(value_rect, allignment='l')
        v.crop_fitted()
        v.rect.left = value_tb.rect.left
        v.rect.y = y
        objects.append(v)
        
        y = v.rect.bottom + 5
        
    b = ui.Button.text_button('back', color2=(0, 200, 0), tag='break')
    b.rect.centerx = width // 2
    b.rect.bottom = height - 10
    objects.append(b)
        
    return objects
    

