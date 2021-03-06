import json

import pygame as pg

from data.save import SAVE, CONSTANTS

from ui.geometry import position
from ui.element.standard import Image, Textbox, Button, Input, Text_Flipper
from ui.element.background import Draw_Lines
from ui.menu import Menu

WIDTH, HEIGHT = CONSTANTS['screen_size']
CENTER = CONSTANTS['center']

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
    i = Image(s)
    i.rect.center = CENTER
    objects.append(i)
    
    body.center = CENTER
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
        
        t = Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25, allignment='l')
        t.rect.topleft = upper.topleft
        t.rect.x += 10
        t.rect.y += 10
        objects.append(t)
        
        x = t.rect.left
        y = t.rect.bottom + 10
        text_rect = pg.Rect(0, 0, body.width, 30)
        
        for err in errors[:5]:
            t = Textbox(err, olcolor=(0, 0, 0))
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
        t = Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25)
        t.rect.center = text_rect.center
        objects.append(t)
    
    b = Button.text_button('ok', color2=(0, 200, 0), tag='break')
    b.rect.center = lower.center
    objects.append(b)

    return objects
    
def info_menu(n):
    objects = []
    n = type(n)(-1)
    n.set_enabled(False)

    with open('data/node/node_info.json', 'r') as f:
        data = json.load(f)    
    data = data.get(n.name, {})

    title = Textbox(n.get_name(), tsize=35)
    title.rect.topleft = (30, 20)
    objects.append(title)
    
    info_rect = pg.Rect(0, 0, 400, 200)
    info_surf = pg.Surface(info_rect.size).convert()
    pg.draw.rect(info_surf, (255, 255, 255), info_rect, width=3, border_radius=10)
    info_rect.topleft = (30, 150)
    i = Image(info_surf)
    i.rect = info_rect.copy()
    objects.append(i)
    
    label = Textbox('info:', tsize=20)
    label.rect.bottomleft = info_rect.topleft
    label.rect.x += 10
    label.rect.y -= 5
    objects.append(label)
    
    node_info = Textbox(data.get('info', ''))
    node_info.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
    node_info.rect.center = info_rect.center
    
    if data.get('tips'):
    
        node_tips = Textbox(data['tips'])
        node_tips.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
        node_tips.rect.center = info_rect.center
        
        node_text = Image(node_info.image)
        node_text.rect.center = info_rect.center
        objects.append(node_text)
        
        def update_info():
            if label.get_message() == 'info:':
                label.set_message('tips:')
                node_text.image = node_tips.image
            else:
                label.set_message('info:')
                node_text.image = node_info.image
                
        b = Button.text_button('>', padding=(15, 15), func=update_info, border_radius=20)
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
    port_box = Image(port_surf, bgcolor=(100, 100, 100))
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
        d = {'port': p, 'color': p.color}
        p_label = Textbox(f'Port {p.port}', fgcolor=(0, 0, 0))
        p_label.fit_text(port_label_rect, tsize=20, allignment='l')
        d['label'] = p_label.image
        p_info = Textbox(info_text)
        p_info.fit_text(port_info_rect, tsize=15, allignment='l')
        d['info'] = p_info.image
        port_data.append(d)

    n.rect.midtop = port_box.rect.midbottom
    n.rect.y += 100
    n.set_port_pos()
    objects.append(n)
        
    if port_data:
        
        port_label = Image(port_data[0]['label'])
        port_label.rect.center = port_label_rect.center
        port_label.rect.x += 5
        objects.append(port_label)
        port_info = Image(port_data[0]['info'])
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
                
            b = Button.text_button('>', padding=(15, 15), func=update_port_info, args=[port_index], kwargs={'dir': 1}, border_radius=20)
            b.rect.midleft = port_box.rect.midright
            objects.append(b)
            b = Button.text_button('<', padding=(15, 15), func=update_port_info, args=[port_index], kwargs={'dir': -1}, border_radius=20)
            b.rect.midright = port_box.rect.midleft
            objects.append(b)
            
            for i, pd in enumerate(port_data):
                r = pd['port'].rect
                b = Button(r.size, func=update_port_info, args=[port_index], kwargs={'i': i})
                b.rect.center = r.center
                objects.insert(0, b)
                
    else:
        objects.pop(-2)

    b = Button.text_button('back', color2=(0, 200, 0), tag='break')
    b.rect.centerx = WIDTH // 2
    b.rect.bottom = HEIGHT - 10
    objects.append(b)
    
    return objects
    
def log_menu(name, data):
    objects = []
    
    title = Textbox.static_textbox(name, tsize=35)
    title.rect.topleft = (30, 20)
    objects.append(title)
    
    info_rect = pg.Rect(0, 0, 400, 200)
    info_surf = pg.Surface(info_rect.size).convert()
    pg.draw.rect(info_surf, (255, 255, 255), info_rect, width=3, border_radius=10)
    info_rect.topleft = (30, 150)
    i = Image(info_surf)
    i.rect = info_rect.copy()
    objects.append(i)
    
    label = Textbox.static_textbox('info:', tsize=20)
    label.rect.bottomleft = info_rect.topleft
    label.rect.x += 10
    label.rect.y -= 5
    objects.append(label)
    
    node_info = Textbox(data['info'])
    node_info.fit_text(info_rect.inflate(-10, -10), tsize=20, allignment='l')
    node_info.rect.center = info_rect.center
    objects.append(node_info)
    
    key_tb = Textbox.static_textbox('key')
    key_tb.rect.topleft = (WIDTH // 2, 40)
    objects.append(key_tb)
    
    value_tb = Textbox.static_textbox('return value')
    value_tb.rect.x = key_tb.rect.right + 30
    value_tb.rect.y = key_tb.rect.y
    objects.append(value_tb)
    
    value_rect = value_tb.rect.inflate(150, 50)
    
    y = value_tb.rect.bottom + 20
    
    for key, value in data['data'].items():
        k = Textbox.static_textbox(key)
        k.rect.right = key_tb.rect.right
        k.rect.y = y
        objects.append(k)
        
        v = Textbox(value)
        v.fit_text(value_rect, allignment='l')
        v.crop_fitted()
        v.rect.left = value_tb.rect.left
        v.rect.y = y
        objects.append(v)
        
        y = v.rect.bottom + 5
        
    b = Button.text_button('back', color2=(0, 200, 0), tag='break')
    b.rect.centerx = WIDTH // 2
    b.rect.bottom = HEIGHT - 10
    objects.append(b)
        
    return objects

def game_options_menu(client):
    objects = []

    b = Button.text_button('disconnect', tag='break', func=client.disconnect)
    b.rect.midtop = CENTER
    objects.append(b)
    
    b = Button.text_button('game settings', func=Menu.build_and_run, args=[game_settings_menu, client])
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    if client.is_host():
        b = Button.text_button('new game', tag='break', func=client.send, args=['reset'])
        b.rect.midtop = objects[-1].rect.midbottom
        objects.append(b)
        
    b = Button.text_button('back', tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    position.center_objects_y(objects)

    return objects

def game_settings_menu(client):
    objects = []

    settings = client.get_settings()

    space = 70
    x0 = (WIDTH // 2) - space
    x1 = x0 + (2 * space)
    
    t = Textbox.static_textbox('rounds: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting score: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting cards: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting items: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting spells: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('number of cpus: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('cpu difficulty: ')
    t.rect.centerx = x0
    objects.append(t)
    
    position.center_objects_y(objects)
    row_sep = len(objects)
    
    c = Text_Flipper.counter(range(1, 6), index=settings['rounds'] - 1, size=(50, 25))
    c.set_tag('rounds')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(5, 51), index=settings['ss'] - 5, size=(50, 25))
    c.set_tag('ss')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(1, 11), index=settings['cards'] - 1, size=(50, 25))
    c.set_tag('cards')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 6), index=settings['items'], size=(50, 25))
    c.set_tag('items')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 4), index=settings['spells'], size=(50, 25))
    c.set_tag('spells')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(1, 15), index=settings['cpus'] - 1, size=(50, 25))
    c.set_tag('cpus')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 5), index=settings['diff'], size=(50, 25))
    c.set_tag('diff')
    c.rect.centerx = x1
    objects.append(c)
    
    position.center_objects_y(objects[row_sep:])

    counters = [c for c in objects if isinstance(c, Text_Flipper)]
    if not client.is_host():
        for c in counters:
            c.set_enabled(False)
    else:
    
        def save_game_settings(client, counters):
            settings = {c.tag: int(c.current_value) for c in counters}  
            SAVE.set_data('settings', settings)
            client.update_settings(settings)
            
        b = Button.text_button('save', size=(100, 25), func=save_game_settings, args=[client, counters])
        b.set_tag('break')
        b.rect.midtop = objects[-1].rect.midbottom
        b.rect.y += b.rect.height
        b.rect.centerx = WIDTH // 2
        objects.append(b)
        
    b = Button.text_button('back', size=(100, 25))
    b.set_tag('break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.centerx = WIDTH // 2
    objects.append(b)

    return objects
