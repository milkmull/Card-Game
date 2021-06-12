import pygame as pg
import time
import sys
import os
import subprocess
import random
import urllib.request
import json
from colorsys import hsv_to_rgb
from tkinter import Tk
from constants import *
from network import Network, InvalidIP, PortInUse
from spritesheet import Spritesheet, Textbox, Counter, Input
from settings import settings as defult_settings

#save data stuff -----------------------------------------------------------------------------------------------------

def new_save():
    save_data = {'username': 'Player 0', 'port': 5555, 'ips': []}
    
    with open('save.json', 'w') as f:
        
        json.dump(save_data, f, indent=4)
        
    return save_data

def read_save():
    try:
    
        with open('save.json', 'r') as f:

            save_data = json.load(f)
            
    except:
    
        new_message('an error occurred, save data has been cleared', 2000)
        
        save_data = new_save()

    return save_data
    
def get_data(key):
    global save_data
    
    return save_data[key]
    
def set_data(key, val):
    global save_data

    if save_data[key] != val:
        
        save_data[key] = val

        with open('save.json', 'w') as f:
        
            json.dump(save_data, f, indent=4)
    
def update_ips(entry):
    ips = get_data('ips').copy()

    if entry not in ips:
    
        ips.append(entry)
        set_data('ips', ips)

def del_ips(name, ip):
    ips = get_data('ips').copy()
    
    for data in ips.copy():
        
        if data['name'] == name and data['ip'] == ip:
            
            ips.remove(data)
            set_data('ips', ips)
            
            break
            
def set_port(new_port):
    new_port = int(new_port)
    old_port = get_data('port')
    
    if new_port != old_port:
        
        set_data('port', new_port)
        
def set_username(new_name):
    old_name = get_data('username')
    
    if new_name != old_name:
    
        set_data('username', new_name)
            
#---------------------------------------------------------------------------------------------------------------

def get_pub_ip():
    return urllib.request.urlopen('https://api.ipify.org').read().decode()
            
def flatten(lst):
    return [c for L in lst for c in L]

def copy_to_clipboard(text):
    Tk().clipboard_append(text)
    
def get_clip():
    try:
    
        text =  Tk().clipboard_get()
        
    except:
        
        text = None
        
    return text
    
def gen_colors(num):
    golden = (1 + 5 ** 0.5) / 2
    colors = []
    
    for i in range(num):
        
        h = (i * (golden - 1)) % 1
        r, g, b = hsv_to_rgb(h, 0.8, 1)
        rgb = (r * 255, g * 255, b * 255)
        colors.append(rgb)

    return colors

def get_outline(rect, color=(255, 0, 0), r=2):
    ol = pg.Surface((rect.width + (2 * r), rect.height + (2 * r))).convert()
    ol.fill(color)
    
    mid = pg.Surface(rect.size).convert()
    mid.fill((0, 0, 0))
    
    ol.blit(mid, (r, r))
    ol.set_colorkey((0, 0, 0))
    
    return ol

#screen stuff----------------------------------------------------------------------

def new_screen(text, wait=0): #renders all new images to the screen
    global win
    
    win.fill((0, 0, 0))

    for t in text:
        
        win.blit(t.get_image(), t.rect)
        
    pg.display.update()
    
    if wait:
    
        pg.time.wait(wait)
        
def new_message(message, wait=0): #renders a given message to the screen for a given ammount of time
    global win
    
    win.fill((0, 0, 0))
    m = Textbox(message, 20)
    m.rect.center = (width / 2, height / 2)
        
    win.blit(m.get_image(), m.rect)
    pg.display.update()
    
    if wait:
    
        pg.time.wait(wait)
        
    pg.event.clear()
    
def get_dx(r1, r2):
    x0 = min([r1, r2], key=lambda r: r.x).x
    wt = r1.width + r2.width
    xc = r1.x + (wt // 2)
    dx = (width // 2) - xc
    
    return dx
    
def outline_buttons(mouse, btns, olc=(255, 0, 0)):
    hit = False
    
    for b in btns:
        
        if hasattr(b, 'add_outline'):
        
            if mouse.colliderect(b.rect) and not hit:
                
                b.add_outline(olc)
                hit = True
                
            else:
                
                b.add_outline()

#main------------------------------------------------------------------------------

def main():
    running = True
    
    while running:
        
        mode = main_menu()
        
        if mode == 'settings':
            
            user_settings()
        
        elif mode == 'search online':
            
            addr = choose_host()
            
            if addr:
                
                ip, port = addr
                connect(ip, port)
                
        elif mode == 'search local':
            
            connect('', get_data('port'))
                
        elif mode == 'host':

            start_game()
            
        elif mode == 'single':
            
            single_player()
                
        elif mode == 'quit':
            
            running = False

#menu stuff------------------------------------------------------------------------

def set_screen(mode, wait=0): #returns all screen objects for given menu
    screen = []
    
    if mode == 'main':
    
        text = Textbox('single player', 20)
        text.rect.center = (width / 2, height / 2)
        text.rect.midbottom = text.rect.midtop
        screen.append(text)
        
        text = Textbox('host game', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
        text = Textbox('find online game', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
        text = Textbox('find local game', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
        text = Textbox('settings', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += text.rect.height
        screen.append(text)
        
    elif mode == 'user settings':
        
        text = Textbox('display name:  ', 20, tcolor=gen_colors(1)[0])
        text.rect.right = width // 2
        text.rect.bottom = height // 2
        text.rect.midbottom = text.rect.midtop
        screen.append(text)
        
        text = Input(get_data('username'), 20)
        text.rect.midleft = screen[-1].rect.midright
        text.set_lock()
        screen.append(text)
        
        text = Textbox('default port:  ', 20)
        text.rect.right = width // 2
        text.rect.y = screen[-1].rect.bottom
        screen.append(text)
        
        text = Input(str(get_data('port')), 20, type=2)
        text.rect.midleft = screen[-1].rect.midright
        text.set_lock()
        screen.append(text)
        
        text = Textbox('save', 20, (255, 255, 0))
        text.rect.centerx = width // 2
        text.rect.y = screen[-1].rect.bottom + text.rect.height
        screen.append(text)
        
        text = Textbox('cancel', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
    elif mode == 'host options':

        text = Textbox('disconnect', 20)
        text.rect.center = (width / 2, height / 2)
        screen.append(text)
        
        text = Textbox('game settings', 20)
        text.rect.midbottom = screen[-1].rect.midtop
        screen.append(text)
        
        text = Textbox('new game', 20)
        text.rect.midtop = screen[-2].rect.midbottom
        screen.append(text)
        
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += text.rect.height
        screen.append(text)
    
    elif mode == 'client options':

        text = Textbox('disconnect', 20)
        text.rect.center = (width / 2, height / 2)
        screen.append(text)
        
        text = Textbox('game settings', 20)
        text.rect.midbottom = screen[-1].rect.midtop
        screen.append(text)
        
        text = Textbox('back', 20)
        text.rect.midtop = screen[-2].rect.midbottom
        text.rect.y += text.rect.height
        screen.append(text)
        
    elif mode == 'choose host':
        
        for entry in get_data('ips'):
        
            text = Textbox(entry['name'] + ': ' + entry['ip'], 20)
            screen.append(text)
            
        y = (height - sum(t.rect.height for t in screen)) / 2
        
        for t in screen:
            
            t.rect.midtop = (width / 2, y)
            y += t.rect.height
            
        text = Textbox('new entry', 20)
        if screen:
            text.rect.midtop = screen[-1].rect.midbottom
        else:
            text.rect.midbottom = (width // 2, height // 2)
        text.rect.y += 20
        screen.append(text)
        
        text = Textbox('view my ip', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
            
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += text.rect.height
        screen.append(text)
        
        text = Textbox(' Port: ', 20, (255, 255, 0), is_button=False)
        text.rect.bottomright = (0, 0)
        screen.append(text)

        text = Textbox(' [join game]', 20, tcolor=(0, 255, 0), is_button=False)
        text.rect.bottomright = (0, 0)
        screen.append(text)
        
        text = Input(' [specify port]', 20, tcolor=(255, 255, 0), type=2)
        text.rect.bottomright = (0, 0)
        text.set_lock()
        screen.append(text)
        
        text = Textbox(' [delete]', 20, tcolor=(255, 0, 0), is_button=False)
        text.rect.bottomright = (0, 0)
        screen.append(text)

    elif mode == 'new entry':
        
        text = Textbox('entry name: ', 20, is_button=False)
        text.rect.midright = (width / 2, height / 2)
        text.rect.midbottom = text.rect.midtop
        screen.append(text)
        
        text = Input('name', 20)
        text.rect.topleft = screen[-1].rect.topright
        text.set_lock()
        screen.append(text)
        
        dx = get_dx(screen[0].rect, screen[1].rect)
        screen[0].rect.x += dx
        screen[1].rect.x += dx
        
        text = Textbox('entry IP: ', 20, is_button=False)
        text.rect.topright = screen[-2].rect.bottomright
        text.rect.y += 20
        screen.append(text)
        
        text = Input('012.345.6789', 20, type=3)
        text.rect.midleft = screen[-1].rect.midright
        text.set_lock()        
        screen.append(text)
        
        dx = get_dx(screen[2].rect, screen[3].rect)
        screen[2].rect.x += dx
        screen[3].rect.x += dx
        
        text = Textbox('save', 20)
        text.rect.centerx = width // 2
        text.rect.y = screen[-1].rect.bottom + (text.rect.height * 2)
        screen.append(text)
        
        text = Textbox('cancel', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
    elif mode == 'name':
        
        text = Textbox('enter your name:', 30, is_button=False)
        text.rect.midbottom = (width // 2, height // 2)
        screen.append(text)
        
        text = Input('player', 30)
        text.rect.midtop = screen[0].rect.midbottom
        text.rect.y += 10
        screen.append(text)
        
        text = Textbox('OK', 30, tcolor=(0, 255, 0))
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 50
        screen.append(text)
        
        text = Textbox('back', 20)
        text.rect.bottomleft = (0, height)
        text.rect.y -= 5
        text.rect.x += 5
        screen.append(text)
        
    elif mode == 'view ip':

        text = Textbox(f'your public IP:  {get_pub_ip()}', 20, is_button=False)
        text.rect.midbottom = (width // 2, height // 2)
        screen.append(text)
        
        text = Textbox('[copy to clipboard]', 15, tcolor=(255, 255, 0))
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 5
        screen.append(text)
        
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += text.rect.width
        screen.append(text)

    new_screen(screen, wait)
        
    return screen

def main_menu():
    mouse = pg.Rect(0, 0, 1, 1)
    btns = set_screen('main')
    
    mode = None

    while mode is None: #once player chooses a mode, go to next screen
        
        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        outline_buttons(mouse, btns)
        new_screen(btns)

        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                mode = 'quit'
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    mode = 'quit'
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if b.rect.colliderect(mouse):
                        
                        if b.message == 'find online game':
                            
                            mode = 'search online'
                            
                        elif b.message == 'host game':
                            
                            mode = 'host'
                            
                        elif b.message == 'find local game':
                            
                            mode = 'search local'
                            
                        elif b.message == 'single player':
                            
                            mode = 'single'
                            
                        elif b.message == 'settings':
                            
                            mode = 'settings'
                            
                        break
        
    return mode
    
def user_settings():
    mouse = pg.Rect(0, 0, 1, 1)
    btns = set_screen('user settings')
    field = None
    
    username_field = btns[1]
    port_field = btns[3]
    
    backspace = False
    checks = [0, 0]
    
    running = True
    
    while running:
        
        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        outline_buttons(mouse, btns)
        new_screen(btns)
        
        if field is not None:

            field.update()

        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
                if field is not None and e.key == pg.K_BACKSPACE:
                    
                    backspace = True
                    
                elif field is not None and e.key == pg.K_RETURN:
                    
                    field.close()
                    field = None
                    
                elif field is not None and hasattr(e, 'unicode'):
                    
                    char = e.unicode.strip()
                    
                    if char and char in chars:

                        field.send_keys(char)
                        
                if (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    
                    checks[0] = 1
                        
                elif e.key == pg.K_v:
                    
                    checks[1] = 1
                    
            elif e.type == pg.KEYUP:
                
                if e.key == pg.K_BACKSPACE:
                    
                    backspace = False
                
                elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    
                    checks[0] = 0
                        
                elif e.key == pg.K_v:
                    
                    checks[1] = 0

            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if mouse.colliderect(b.rect):
                    
                        if isinstance(b, Input):
                            
                            if field is not None:
                                
                                field.close()
                            
                            field = b
                            
                        elif b.message == 'save':
                            
                            username = username_field.get_message()
                            port = port_field.get_message()
                            
                            set_username(username)
                            set_port(port)
                            
                            new_message('changes saved', 1500)
                            
                            return
                            
                        elif b.message == 'cancel':
                        
                            return
                            
                        break

                else:
                    
                    if field is not None:
                    
                        field.close()
                        field = None
                        
        if field is not None:
                        
            if backspace:
                
                field.send_keys()
                        
            elif checks[0] and checks[1]:
                
                text = get_clip()
                
                if text:
                
                    field.send_keys(text)
                
                checks = [0, 0]

def choose_host():
    btns = set_screen('choose host')
    mouse = pg.Rect(0, 0, 1, 1)

    def get_options():
        return btns[-3:]

    def move_options(p):
        options[0].rect.topleft = p
        options[1].rect.topleft = options[0].rect.topright
        options[2].rect.topleft = options[1].rect.topright
        
        btns[-4].rect.bottomright = (0, 0)
        
    def reset_options():
        for t in options:
        
            t.rect.bottomright = (0, 0)
            
        options[-2].reset()
        btns[-4].rect.bottomright = (0, 0)
        
    def move_port_text():
        options[-1].rect.bottomright = (0, 0)
        btns[-4].rect.topleft = options[0].rect.topright
        options[1].rect.topleft = btns[-4].rect.topright
        
    def get_port():
        port = -1
        
        try:
    
            port = int(options[-2].get_message())
            
        except ValueError:
            
            port = get_data('port')

        return port
            
    options = get_options()
    field = None
            
    name = ''
    ip = ''
    
    backspace = False
    
    running = True
    
    while running:

        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        outline_buttons(mouse, btns)
        new_screen(btns)
        
        if field is not None:

            field.update()
        
        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:

                if e.key == pg.K_ESCAPE:
                
                    return
                    
                elif field is not None:
                    
                    if e.key == pg.K_BACKSPACE:
                        
                        backspace = True
                        
                    elif e.key == pg.K_RETURN:
                        
                        field.close()
                        field = None

                    elif hasattr(e, 'unicode'):
                        
                        char = e.unicode.strip()
                        
                        if char and char in chars:

                            field.send_keys(char)
                        
            elif e.type == pg.KEYUP:
                
                if e.key == pg.K_BACKSPACE:
                    
                    backspace = False
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if b.rect.colliderect(mouse):
                        
                        if isinstance(b, Input):
                            
                            b.clear()
                            field = b
                            move_port_text()
                            
                            break
                            
                        else:
                            
                            if field is not None:
                                
                                field.close()
                                field = None
                        
                            if b.message == 'back':
                                
                                return
                                
                            elif b.message == 'new entry':
                            
                                tup = new_entry()
                                
                                if tup is not None:
                                
                                    name, ip = tup
                                    update_ips({'name': name, 'ip': ip})
                                    
                                    btns = set_screen('choose host')
                                    options = get_options()
                                    
                                break
                                
                            elif b.message == 'view my ip':
                                
                                try:
                                
                                    view_ip()
                                    
                                except urllib.error.URLError:
                                    
                                    new_message('connection could not be found', 2000)
                                
                                break
                                
                            elif ip and 'join game' in b.message:
                                
                                return (ip, get_port())
                                
                            elif ip and 'delete' in b.message:
                                
                                del_ips(name, ip)
                                
                                btns = set_screen('choose host')
                                options = get_options()
                                
                                break
                                
                            elif isinstance(b, Textbox) and ':' in b.message and getattr(b, 'is_button', False):
                                
                                name, ip = b.message.split(': ')
                                move_options(b.rect.topright)
                                
                                break
                            
                else:
                
                    name = ''
                    ip = ''
                    
                    if field is not None:
                    
                        field.close()
                        field = None
                    
                    reset_options()
                    
        if field is not None:
                            
            if backspace:
                
                field.send_keys()
        
def new_entry(info=None):
    btns = set_screen('new entry')
    mouse = pg.Rect(0, 0, 1, 1)
    
    if info:
        
        name, ip = info
        
        btns[1].update_text(name)
        btns[3].update_text(ip)

    field = btns[1]
    
    backspace = False
    
    running = True
    
    checks = [0, 0]
    
    while running:
        
        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        outline_buttons(mouse, btns)
        new_screen(btns)
        
        if field is not None:

            field.update()

        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
                if field is not None and e.key == pg.K_BACKSPACE:
                    
                    backspace = True
                    
                elif field is not None and e.key == pg.K_RETURN:
                    
                    field.close()
                    field = None
                    
                elif field is not None and hasattr(e, 'unicode'):
                    
                    char = e.unicode.strip()
                    
                    if char and char in chars:

                        field.send_keys(char)
                        
                if (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    
                    checks[0] = 1
                        
                elif e.key == pg.K_v:
                    
                    checks[1] = 1
                    
            elif e.type == pg.KEYUP:
                
                if e.key == pg.K_BACKSPACE:
                    
                    backspace = False
                
                elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    
                    checks[0] = 0
                        
                elif e.key == pg.K_v:
                    
                    checks[1] = 0

            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if mouse.colliderect(b.rect):
                    
                        if isinstance(b, Input):
                            
                            if field is not None:
                                
                                field.close()
                            
                            field = b
                            
                        elif b.message == 'cancel':
                        
                            return
                            
                        elif b.message == 'save':
                            
                            return (btns[1].get_message(), btns[3].get_message())
                            
                        break
    
                else:
                    
                    if field is not None:
                    
                        field.close()
                        field = None
                        
        if field is not None:
                        
            if backspace:
                
                field.send_keys()
                        
            elif checks[0] and checks[1]:
                
                text = get_clip()
                
                if text:
                
                    field.send_keys(text)
                
                checks = [0, 0]

def view_ip(info=None):
    btns = set_screen('view ip')
    mouse = pg.Rect(0, 0, 1, 1)
    
    timer = 0

    running = True
    
    while running:
        
        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        outline_buttons(mouse, btns)
        new_screen(btns)

        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return

            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if mouse.colliderect(b.rect):
                    
                        if b.message == 'back':
                            
                            return
                            
                        elif 'cop' in b.message:
                            
                            copy_to_clipboard(get_pub_ip())
                            
                            btns[1].update_text('[coppied]')
                            
                            timer = 125
                            
        timer -= 1
        
        if timer == 0:
            
            btns[1].update_text('[copy to clipboard]')
  
#in game menues------------------------------------------------------------------------------
 
def settings_screen(pid, settings): #special function to set up the settings screen
    screen = []
    
    text = Counter('rounds: ', settings['rounds'], range(1, 26), 20)
    screen.append(text)
    
    text = Textbox(f"free play: {settings['fp']}", tsize=20, is_button=False)
    screen.append(text)
    
    text = Counter('starting score: ', settings['ss'], range(5, 51), 20)
    screen.append(text)

    text = Counter('starting cards: ', settings['cards'], range(1, 11), 20)
    screen.append(text)
    
    text = Counter('starting items: ', settings['items'], range(0, 6), 20)
    screen.append(text)
    
    text = Counter('starting spells: ', settings['spells'], range(0, 6), 20)
    screen.append(text)
    
    text = Textbox(f"score wrap: {settings['score wrap']}", tsize=20, is_button=False)
    screen.append(text)
    
    text = Counter('number of cpus: ', settings['cpus'], range(1, 15), 20)
    screen.append(text)
    
    text = Counter('cpu difficulty: ', settings['diff'], range(0, 5), 20)
    screen.append(text)
    
    y = (height - sum(t.rect.height for t in screen)) / 2
    
    for b in screen:
        
        b.rect.y = y
        b.rect.centerx = width / 2
        
        if isinstance(b, Counter):
        
            b.move_counter()
        
        y += b.rect.height
    
    if pid == 0:
    
        text = Textbox('save changes', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 20
        screen.append(text)
        
        text = Textbox('reset', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
    
    text = Textbox('cancel', 20)
    text.rect.midtop = screen[-1].rect.midbottom
    screen.append(text)
    
    if pid != 0:
        
        text.rect.y += 20
    
    new_screen(screen)
    
    return screen
 
def game_menu(client):
    if client.pid == 0:
    
        mode = 'host options'
        
    else:
        
        mode = 'client options'
        
    btns = set_screen(mode)
    mouse = pg.Rect(0, 0, 1, 1)

    running = True
    
    while running:
        
        client.clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        new_screen(btns)
        outline_buttons(mouse, btns)

        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                client.quit()
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if b.rect.colliderect(mouse):
                        
                        if b.message == 'new game':
                            
                            client.send('reset')
                            
                            return
                            
                        elif b.message == 'disconnect':
                            
                            client.exit()
                            pg.time.wait(1000)
                            
                            return
                            
                        elif b.message == 'back':
                            
                            return
                            
                        elif b.message == 'game settings':
                            
                            settings_menu(client, client.send('settings'))
                            
def settings_menu(client, settings):
    pid = client.pid
    
    btns = settings_screen(pid, settings)
    mouse = pg.Rect(0, 0, 1, 1)
    
    running = True
    
    while running:
    
        client.clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        new_screen(btns)
        outline_buttons(mouse, btns)

        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if b.rect.colliderect(mouse):
                        
                        if pid == 0:
                        
                            if 'free play' in b.message:

                                settings['fp'] = not settings['fp']
                                
                            elif 'score wrap' in b.message:
                            
                                settings['score wrap'] = not settings['score wrap']
                                
                            elif b.message == 'save changes':
                                
                                new_message('saving...', 500)
                                
                                reply = client.update_settings(settings)
                                    
                                if reply:

                                    new_message('changes saved!', 1500)
                                    
                                else:
                                    
                                    new_message('cannot change rules while playing', 2000)
                                
                                return
                                
                            elif b.message == 'reset':
                                
                                settings = defult_settings.copy()
                                btns = settings_screen(pid, settings)
                                new_screen(btns)
                            
                            elif b.message == 'cancel':
                                
                                return
                                
                        elif b.message == 'cancel':
                            
                            return

                    elif pid == 0 and isinstance(b, Counter):
                        
                        if b.click_counter(mouse):
                        
                            if 'starting score' in b.message:

                                settings['ss'] = b.get_count()
                                
                            elif 'rounds' in b.message:
                                
                                settings['rounds'] = b.get_count()
                                
                            elif 'cards' in b.message:
                                
                                settings['cards'] = b.get_count()
                        
                            elif 'items' in b.message:
                                
                                settings['items'] = b.get_count()
                                
                            elif 'spells' in b.message:
                                
                                settings['spells'] = b.get_count()
                                
                            elif 'cpus' in b.message:
                                
                                settings['cpus'] = b.get_count()
                                
                            elif 'diff' in b.message:
                                
                                settings['diff'] = b.get_count()
                                
def name_entry(id, color):
    btns = set_screen('name')
    mouse = pg.Rect(0, 0, 1, 1)

    field = btns[1]
    field.update_text(f'Player {id}', tcolor=color)
    
    running = True
    
    while running:
        
        clock.tick(30)
        mouse.center = pg.mouse.get_pos()
        new_screen(btns)
        field.update()
        outline_buttons(mouse, btns)
        
        name = field.get_message()

        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
                elif e.key == pg.K_BACKSPACE:
                    
                    field.send_keys()
                    
                elif e.key == pg.K_RETURN and name:
                    
                    return name
                    
                elif hasattr(e, 'unicode'):
                    
                    if e.unicode.strip():
                    
                        field.send_keys(e.unicode)

            elif e.type == pg.MOUSEBUTTONDOWN:

                for b in btns:
                    
                    if b.rect.colliderect(mouse):
                        
                        m = field.get_message()
                        
                        if b.message == 'OK' and name:
                            
                            return name
                            
                        elif b.message == 'back':
                            
                            return

#new game stuff-------------------------------------------------------------------------

def connect(ip, port):
    new_message('searching for game...', 500)

    try:
             
        net = Network(ip, port)
        c = Client(win, net, 'online')
        
    except InvalidIP:
        
        new_message('invalid IP address', 2000)
        
    except PortInUse:
        
        new_message('the specified port is currently in use', 2000)
        
    except EOFError as e:
    
        print(e)
        new_message('disconnecting...', 1000)
        
    except Exception as e:
        
        print(e, 'c1')
        new_message('no games could be found', 2000)
        
def start_game():
    new_message('starting game...', 500)

    try:
        
        subprocess.Popen([sys.executable, 'server.py'])
        net = Network('', get_data('port'))
        c = Client(win, net, 'online')
        
    except EOFError as e:
        
        print(e)
        new_message('diconnected', 1000)
        
    except Exception as e:
    
        print(e, 'c2')
        new_message('an error occurred', 2000)
        
def single_player(): #start a single player game
    new_message('starting game...', 500)
    
    from game import Game #import game class
    
    g = Game('single')
    
    Client(win, g, 'single')
    
    new_message('returning to main menu...', 1000) #if any errors occur or player leaves game, retrun to main menu

#-----------------------------------------------------------------------------------

def get_btn(btns, text): #find button in list of buttons based on text
    return next((b for b in btns if b.message == text), None)
        
class Particle1:
    def __init__(self, rect, color, radius=None):
        self.pos = [random.randrange(rect.left, rect.right), random.randrange(rect.top, rect.bottom)]
        
        self.vel = [random.randrange(-5, 5), random.randrange(-5, 5)]
        
        self.timer = random.randrange(1, 50)
        
        self.r = random.randrange(3) if radius is None else radius
        
        self.color = color

    def update(self):
        self.vel[1] += 0.5
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.timer -= 1
        
        return self.timer
        
class Particle2:
    def __init__(self, rect, color, radius=None):
        self.pos = [random.randrange(rect.left, rect.right), random.randrange(rect.top, rect.bottom)]
        
        self.vel = [0, random.randrange(1, 5)]

        self.r = random.randrange(1, 10)
        
        self.color = color

    def update(self):
        self.pos[1] -= 2

        self.r -= 1

        return self.r
 
class Target:
    def __init__(self, client):
        self.client = client
        
        self.textbox = Textbox('', 20)
        self.rect = self.textbox.rect

        self.timer = 0
        self.counter = 0
        
        self.points = []
        self.cards = []
        
    def adjust_course(self):
        for p in self.points.copy():
            
            self.points.remove(p)
            
            self.add_points(p.num, p.rect.topleft)

    def reset(self):
        self.counter = 0
        self.timer = 0
        
        self.textbox.clear()
        
    def add_points(self, num, s):
        self.points.append(Points(num, s, self.rect.center))
        
    def add_cards(self, name, s):
        self.cards.append(MovingCard(name, s, self.rect.center))
        
    def get_color(self):
        if self.counter < 0:
            
            return (255, 0, 0)
            
        elif self.counter > 0:
            
            return (0, 255, 0)
            
    def update_text(self):
        if self.counter > 0:
            
            text = f'+{self.counter}'
            
        else:
            
            text = str(self.counter)
            
        self.textbox.update_text(text, self.get_color())
        
    def update(self):
        for p in self.points.copy():
            
            p.update()

            if p.rect.collidepoint(self.rect.center):

                self.points.remove(p)
                
                self.timer = 100
                
                self.counter += p.num
                
                self.update_text()
                
        for c in self.cards.copy():
            
            c.update()
            
            if c.rect.collidepoint(self.rect.center):
                
                self.cards.remove(c)
        
        if self.timer == 0:
            
            self.reset()
            
        else:
            
            self.timer -= 1
            
class Points:
    def __init__(self, points, s, e, color=None):
        self.pos = list(s)
        self.target = e
        
        self.num = points

        if points > 0:
        
            self.text = Textbox(f'+{points}', 30, (0, 255, 0))
            
        else:
            
            self.text = Textbox(f'{points}', 30, (255, 0, 0))
            
        self.text.add_outline((0, 0, 0))
        
        self.rect = self.text.rect
        self.rect.topleft = self.pos
        
        self.image = self.text.get_image()
        
        self.vel = [(self.target[0] - self.pos[0]) // 30, (self.target[1] - self.pos[1]) // 30]
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.rect.topleft = self.pos
        
class MovingCard:
    def __init__(self, name, s, e):
        self.pos = list(s)
        self.target = e
        
        self.name = name
        
        self.rect = pg.Rect(0, 0, cw, ch)
        self.rect.topleft = self.pos
        
        self.image = self.get_image()
        self.vel = [(self.target[0] - self.pos[0]) // 30, (self.target[1] - self.pos[1]) // 30]
        
    def get_image(self, mini=True):
        return spritesheet.get_image(self, mini)
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.rect.topleft = self.pos
 
class Pane:
    def __init__(self, rect, message, color=(0, 0, 0, 0), layer=0, tsize=10, tcolor=(255, 255, 255)):
        self.rect = rect
        self.textbox = Textbox(message, tsize, tcolor)

        self.scroll_buttons = [Textbox('       v       ', 20), Textbox('       ^       ', 20)]
        
        for b in self.scroll_buttons:
            
            b.add_background((0, 0, 0))
            
        self.lock = 1

        self.move_text()
        
        self.color = color
        self.layer = layer
        
        self.cards = []
        self.uids = {}
        
        self.image = self.get_image()
        self.bg = pg.Surface((cw, ch)).convert()
        
    def resize(self, w, h):
        tl = self.rect.topleft
        self.rect.size = (w, h)
        self.rect.topleft = tl
        
        self.image = self.get_image()
        self.redraw()

    def get_image(self):
        s = pg.Surface(self.rect.size).convert_alpha()
        
        if self.color:
            
            s.fill(self.color)
            
        return s
        
    def reset(self):
        self.cards.clear()
        
        self.image.fill(self.color)
        
    def get_cards(self):
        return self.cards.copy()

    def move_text(self):
        self.textbox.rect.midbottom = self.rect.midtop
        
        self.scroll_buttons[0].rect.midbottom = self.rect.midbottom
        self.scroll_buttons[1].rect.midtop = self.rect.midtop
        
    def move_body(self):
        self.rect.midtop = self.textbox.rect.midbottom

    def update_text(self, message, tcolor=None):
        self.textbox.update_text(message, tcolor)
        
        self.move_text()
        
    def add_cards(self, cards, ypad=5, xpad=5, dir='y', color=None):
        if cards != self.cards:

            if self.rect.width == cw:
                
                xpad = 0
            
            if self.rect.height == ch:
                
                ypad = 0
            
            if dir == 'y':
            
                y = 0
                x = 0

                for c in cards:
                
                    c.rect.midtop = (self.rect.centerx, self.rect.y + y + ypad)
                    y += c.rect.height + ypad

            elif dir == 'x':
                
                y = 0
                x = 0
                
                for c in cards:
                    
                    if self.rect.x + x + xpad + c.rect.width > self.rect.right:
                        
                        x = 0
                        y = c.rect.height + ypad
                    
                    c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                    x += c.rect.width + xpad

            if hasattr(self, 'start_auto'):

                self.start_auto(60)

            self.cards = cards.copy()
            
            if self.lock == 0:
                
                self.go_to_bottom()
                
            self.redraw()
            
        if getattr(self, 'opened', True):
            
            cards = [c for c in self.cards if self.rect.bottom >= c.rect.bottom and self.rect.top <= c.rect.top]
            
        else:
            
            cards = []
            
        return cards
        
    def add_rows(self, cards, ypad=5, xpad=5):
        if self.cards != flatten(cards.values()):
            
            self.image.fill((0, 0, 0, 0))
            
            y = 0
            
            for color, lst in cards.items():
                
                if lst:
                
                    x = 0
                    
                    for c in lst:
                        
                        if self.rect.x + x + xpad + c.rect.width > self.rect.right:
                            
                            x = 0
                            y = c.rect.height + ypad
                        
                        c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                        
                        rel_pos = (x + xpad, y + ypad)
                        
                        pg.draw.rect(self.image, color, pg.Rect(x + (xpad // 2), y + (ypad // 2), cw + xpad, ch + ypad))
                        self.image.blit(c.get_image(), rel_pos)
                        
                        c.set_rel_pos(rel_pos)
                        
                        x += c.rect.width + xpad
                        
                    y += c.rect.height + ypad

            if hasattr(self, 'start_auto'):
                
                self.start_auto(60)
                
            self.cards = flatten(cards.values())
            
        return [c for c in self.cards if self.rect.contains(c.rect)]

    def draw(self, win):  
        win.blit(self.image, self.rect)
        
        win.blit(self.textbox.text, self.textbox.rect)
        
    def redraw(self):
        if self.color:
            
            self.image.fill(self.color)
            
        for c in self.cards:
            
            rel_pos = (c.rect.x - self.rect.x, c.rect.y - self.rect.y)
            c.set_rel_pos(rel_pos)
            
            if c.color and spritesheet.check_name(c.name):

                self.bg.fill(c.color)
                self.image.blit(self.bg, (rel_pos[0] - 2, rel_pos[1] - 2))
                
            self.image.blit(c.get_image(), rel_pos)

        if self.can_scroll_down(): 
            
            b = self.scroll_buttons[0]
            rel_pos = (b.rect.x - self.rect.x, b.rect.y - self.rect.y)
            self.image.blit(b.get_image(), rel_pos)
            
        if self.can_scroll_up():
            
            b = self.scroll_buttons[1]
            rel_pos = (b.rect.x - self.rect.x, b.rect.y - self.rect.y)
            self.image.blit(b.get_image(), rel_pos)
        
    def can_scroll_up(self):
        return any(c.rect.top < self.rect.top for c in self.cards)
        
    def can_scroll_down(self):
        return any(c.rect.bottom > self.rect.bottom for c in self.cards) and self.rect.size != (cw, ch)
            
    def scroll(self, mouse, dir):
        if self.cards:
        
            if mouse.colliderect(self.rect) and dir == 5:
                
                if self.can_scroll_down():

                    for c in self.cards:
                        
                        c.rect.y -= 25
                        
                    self.redraw()
                    
            elif mouse.colliderect(self.rect) and dir == 4:

                if self.can_scroll_up():
                
                    for c in self.cards:
                        
                        c.rect.y += 25
                    
                    self.redraw()
                    
    def go_to_bottom(self):
        while self.can_scroll_down():
            
            self.scroll(self.rect, 5)
        
class Slider(Pane):
    def __init__(self, rect, message, color=(0, 0, 0, 0), layer=0, tsize=10, tcolor=(255, 255, 255), type=0, dir='y', sensor=None):
        super().__init__(rect, message, color, layer, tsize, tcolor)
        
        self.type = type
        self.dir = dir
        
        self.pos = [self.rect.x, self.rect.y]
        self.adjust_pos()
        
        self.ref = self.rect.copy()
        
        if sensor is None:
        
            self.apply_sensor()
            
        else:
            
            self.sensor = sensor
    
        self.vel = 5 * self.rect.height / 50
    
        self.mode = None
    
        self.opened = False
        self.closed = True
        
        self.locked = False
        
        self.timer = 0
        
        self.auto = False
        
    def check_mode(self):
        return self.auto or self.mode is not None
        
    def new_x(self, x):
        dx = x - self.pos[0]
        self.pos[0] = x
        
        self.adjust_pos()
        
        if hasattr(self, 'ref'):
            
            self.ref.x += dx
            
        if hasattr(self, 'sensor'):
            
            self.sensor.x += dx
            
    def new_y(self, y):
        dy = y - self.pos[1]
        self.pos[1] = y
        
        self.adjust_pos()
        
        if hasattr(self, 'ref'):
            
            self.ref.y += dy
            
        if hasattr(self, 'sensor'):
            
            self.sensor.y += dy
        
    def adjust_pos(self):
        self.rect.topleft = self.pos
        self.move_text()
        
    def adjust_cards(self):
        for c in self.cards:
            
            c.adjust_pos(self.rect)

    def hit(self, r):
        if self.rect.colliderect(r) or self.sensor.colliderect(r) or self.ref.colliderect(r):
            
            self.mode = 'opening'
            
        elif not self.closed and not self.locked:
            
            self.mode = 'closing'
            
    def update(self):
        if self.auto:
            
            self.mode = 'opening'
            
        if self.mode == 'opening':# and not self.opened:
        
            if self.dir == 'x':
        
                self.pos[0] += self.vel
            
            elif self.dir == '-x':
                
                self.pos[0] -= self.vel
                
            elif self.dir == 'y':
                
                self.pos[1] += self.vel
                
            elif self.dir == '-y':
                
                self.pos[1] -= self.vel
            
            self.adjust_pos()
            
            if (self.dir == 'x' and self.rect.left > self.ref.right) or (self.dir == '-x' and self.rect.right < self.ref.left) or (self.dir == 'y' and self.rect.top > self.ref.bottom) or (self.dir == '-y' and self.rect.bottom < self.ref.top):
                
                self.open()
                
            self.adjust_cards()
                
        elif self.mode == 'closing' and not self.closed:
            
            if self.dir == 'x':
        
                self.pos[0] -= self.vel
            
            elif self.dir == '-x':
                
                self.pos[0] += self.vel
                
            elif self.dir == 'y':
                
                self.pos[1] -= self.vel
                
            elif self.dir == '-y':
                
                self.pos[1] += self.vel
            
            self.adjust_pos()
            
            if (self.dir == 'x' and self.rect.left < self.ref.left) or (self.dir == '-x' and self.rect.right > self.ref.right) or (self.dir == 'y' and self.rect.top < self.ref.top) or (self.dir == '-y' and self.rect.bottom > self.ref.bottom):
                
                self.close()
                
            self.adjust_cards()
        
        if self.auto:
            
            self.timer -= 1
            
            if not self.timer:
                
                self.auto = False
                
        else:
        
            self.timer += 1
    
    def click(self):
        if self.timer > 10:
            
            self.timer = 0
            
        else:
            
            self.locked = not self.locked

    def open(self):
        if self.dir == 'x':
            
            self.rect.left = self.ref.right
            self.pos = [self.ref.right, self.ref.y]
            
        elif self.dir == '-x':
            
            self.rect.right = self.ref.left
            self.pos = [self.ref.left - self.rect.width, self.ref.y]
            
        elif self.dir == 'y':
            
            self.rect.top = self.ref.bottom
            self.pos = [self.ref.x, self.ref.bottom]
            
        elif self.dir == '-y':
        
            self.rect.bottom = self.ref.top
            self.pos = [self.ref.x, self.ref.top - self.rect.height]
        
        self.move_text()
            
        self.opened = True
        self.closed = False
        
        self.mode = None
        
    def close(self):
        self.rect.topleft = self.ref.topleft
        self.pos = [self.rect.x, self.rect.y]
        self.move_text()
        
        self.closed = True
        self.opened = False
        
        self.mode = None

    def start_auto(self, t=60):
        self.auto = True
        self.timer = t
        
    def is_tab(self):
        return True
        
    def apply_sensor(self):
        self.sensor = self.ref.copy()
        
        if self.dir == 'x':
            
            self.sensor.width = 10
            self.sensor.x -= 10
            
        elif self.dir == '-x':
            
            self.sensor.width = 10
            self.sensor.x += 10
            
        elif self.dir == 'y':
            
            self.sensor.height = 10
            self.sensor.y += 10
            
        elif self.dir == '-y':
            
            self.sensor.height = 10
            self.sensor.y -= 10

class Player:
    def __init__(self, client, pid, name=None):
        self.client = client
        
        self.pid = pid
        self.name = name if name is not None else f'Player {pid}'
        self.color = self.client.colors[pid]

        self.score = self.client.send('-s:ss')
        
        self.coin = None
        self.dice = None
        self.timer = 0
        self.frt = 0
        
        self.flipping = False
        self.rolling = False
        self.is_turn = False
        
        self.landscape = None
        self.active_card = None
        
        self.played = []
        self.unplayed = []
        self.items = []
        self.selection = []
        self.selected = []
        self.equipped = []
        self.ongoing = []
        self.treasure = []
        self.spells = []
        self.used_item = None
        
        self.card = Textbox('')
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    def update(self):
        if self.flipping and not self.frt % 2:
                
            self.coin = random.choice((0, 1))
            
        elif self.rolling and not self.frt % 2:
            
            self.dice = random.choice(range(0, 6))
            
        if self.timer:
            
            self.timer -= 1

            if self.timer <= 0:
                
                if self.coin != -1:
                
                    self.coin = None
                    
                if self.dice != -1:
                
                    self.dice = None
                    
                self.timer = 0
                    
        self.frt = (self.frt + 1) % 500
        
        if self.active_card is None:

            self.coin = None
            self.dice = None
        
    def reset(self):
        self.score = self.client.send('-s:ss')

        self.coin = None
        self.dice = None
        
        self.flipping = False
        self.rolling = False
        self.is_turn = False
        
        self.landscape = None
        self.active_card = None
        
        self.played.clear()
        self.unplayed.clear()
        self.items.clear()
        self.selection.clear()
        self.selected.clear()
        self.equipped.clear()
        self.ongoing.clear()
        self.treasure.clear()
        self.spells.clear()
        self.used_item = None
        
    def new_round(self):
        self.played.clear()
        self.unplayed.clear()
        self.selection.clear()
        self.ongoing.clear()
        self.active_card = None
        
    def get_cards(self):
        return [self.played, self.unplayed, self.items, self.selection, self.selected, self.equipped, self.ongoing, self.treasure, self.spells]
        
    def get_image(self, mini=False):
        return self.card.text
            
    def get_target(self):
        return self.client.targets.get(self.pid)
        
    def get_spot(self):
        return self.client.get_spot(self.pid)
        
    def get_starting_point(self):
        return self.get_spot().rect.topleft
        
    def play(self, uid):
        for c in self.unplayed:
            
            if c.uid == uid:
                
                self.unplayed.remove(c)
                self.played.append(c)
                
                break
        
    def new_lead(self, uid):
        for i in range(len(self.unplayed)):
            
            c = self.unplayed[i]
            
            if c.uid == uid:
                
                self.unplayed.insert(0, self.unplayed.pop(i))
                
                break
                
    def new_deck(self, deck, cards):
        cards = [Card(name, uid) for name, uid in cards]
        
        setattr(self, deck, cards)
        
        if deck == 'selection' and self is self.client.main_p:
            
            for c in self.selection:

                for p in self.client.players:

                    if p.name == c.name:
 
                        c.color = p.color
                        
                        break
            
            if self.coin == -1:
                
                self.coin = None
                
            if self.dice == -1:
                
                self.dice = None
        
    def clear_deck(self, deck):
        getattr(p, log.get('d')).clear()
        
    def equip(self, uid):
        for c in self.items:
            
            if c.uid == uid:
                
                self.items.remove(c)
                self.equipped.append(c)

                break
                
    def unequip(self, uid):
        for c in self.equipped:
            
            if c.uid == uid:
                
                self.equipped.remove(c)
                self.items.append(c)
                
                break
                
    def steal_treasure(self, target, uid):
        for c in target.treasure:
            
            if c.uid == uid:
                
                target.treasure.remove(c)
                self.treasure.append(c)
                
                r = self.client.get_spot(self.pid).rect
                self.client.add_particles(r, 100)

                break
                
    def steal_item(self, target, uid):
        for c in target.items:
            
            if c.uid == uid:
                
                target.items.remove(c)
                self.items.append(c)
                
                break
                
    def steal_spell(self, target, uid):
        for c in target.spells:
            
            if c.uid == uid:
                
                target.spells.remove(c)
                self.spells.append(c)
                
                break
                
    def give_treasure(self, target, uid):
        for c in self.treasure:
            
            if c.uid == uid:
                
                self.treasure.remove(c)
                target.treasure.append(c)
                
                break
                
    def give_item(self, target, uid):
        for c in self.items:
            
            if c.uid == uid:
                
                self.items.remove(c)
                target.items.append(c)
                
                break
                
    def give_spell(self, target, uid):
        for c in self.spells:
            
            if c.uid == uid:
                
                self.spells.remove(c)
                target.spells.append(c)
                
                break
                
    def use_treasure(self, uid):
        for c in self.treasure:
            
            if c.uid == uid:
                
                self.treasure.remove(c)
                
                break
                
    def use_item(self, uid, name):
        for c in self.items:
            
            if c.uid == uid:
                
                self.items.remove(c)

                break
                
        c = Card(name, uid)
        c.color = self.color
        self.client.last_item = c
                
    def draw_treasure(self, name, uid):
        self.treasure.append(Card(name, uid))
        
        r = self.get_spot().rect
        self.client.add_particles(r, 100)
        
    def draw_item(self, name, uid):
        self.items.append(Card(name, uid))
        
        r = self.get_spot().rect
        self.client.add_particles(r, 100, (255, 0, 0))
        
    def draw_spell(self, name, uid):
        self.spells.append(Card(name, uid))
        
        r = self.get_spot().rect
        self.client.add_particles(r, 100, (255, 0, 255))
        
    def cast(self, uid, target):
        for c in self.spells:
            
            if c.uid == uid:
                
                self.spells.remove(c)
                target.ongoing.append(c)
                
                c.color = self.color
                
                break
                
    def add_spell(self, name, uid):
        self.ongoing.append(Card(name, uid))
                
    def discard(self, uid):
        for c in self.equipped:
            
            if c.uid == uid:
                
                self.equipped.remove(c)
                
                break
                
        for c in self.ongoing:
            
            if c.uid == uid:
                
                self.ongoing.remove(c)
                
                break
                
        for c in self.items:
            
            if c.uid == uid:
                
                self.items.remove(c)
                
                break
                
        for c in self.spells:
            
            if c.uid == uid:
                
                self.spells.remove(c)
                
                break
                
    def buy(self, uid, type):
        card = None 
        
        for c in self.client.shop:
            
            if c.uid == uid:
                
                self.client.shop.remove(c)
                card = c

                break
                
        c = card
                
        if type in ('item', 'equipment'):
            
            self.items.append(c)
            
        elif type == 'spell':
            
            self.spells.append(c)
            
        elif type == 'treasure':
            
            self.treasure.append(c)
            
        else:
            
            self.unplayed.append(c)
            
    def add_unplayed(self, name, uid):
        self.unplayed.append(Card(name, uid))
        
    def draft(self, uid):
        for c in self.selection:
            
            if c.uid == uid:
                
                self.selection.remove(c)
                self.unplayed.append(c)
                
                break

    def update_name(self, name):
        self.name = name
    
    def new_ac(self, c, wait):
        self.active_card = c
        
        if wait == 'coin':
            
            self.coin = -1
            
        elif wait == 'dice':
            
            self.dice = -1
        
    def remove_ac(self):
        self.active_card = None
        
    def cancel_select(self):
        self.selection.clear()
        
    def set_landscape(self, c):
        self.landscape = c
        
    def remove_landscape(self):
        self.landscape = None
        
    def flip_request(self):
        self.coin = -1
        
    def start_flip(self):
        self.flipping = True
        
    def end_flip(self, coin, timer):
        self.flipping = False
        
        self.coin = coin
        
        self.timer = timer
        
    def roll_request(self):
        self.dice = -1
        
    def start_roll(self):
        self.rolling = True
        
    def end_roll(self, dice, timer):
        self.rolling = False
        
        self.dice = dice - 1
        
        self.timer = timer
        
    def remove_coins(self, uid):
        for c in self.treasure:
            
            if c.uid == uid:
                
                self.treasure.remove(c)
                
                break

class Card:
    def __init__(self, name, uid=None, color=None):
        self.name = name
        self.uid = uid if uid is not None else id(self)

        self.rel_pos = [0, 0]
        
        self.color = color
        
        self.rect = self.get_image().get_rect()
            
        self.on = False
        
    def set_rel_pos(self, pos):
        self.rel_pos = pos
        
    def copy(self):
        return type(self)(self.name, self.uid, self.color)
        
    def __eq__(self, other):
        return self.uid == other.uid
        
    def __repr__(self):
        return self.name
        
    def get_image(self, mini=True):
        return spritesheet.get_image(self, mini)
        
    def get_outline(self):
        return get_outline(self.rect, r=3)
        
    def update(self, name, uid):
        self.name = name
        self.uid = uid
        
    def adjust_pos(self, rect):
        self.rect.x = rect.x + self.rel_pos[0]
        self.rect.y = rect.y + self.rel_pos[1]
        
class Client:
    def __init__(self, screen, connection, mode):
        self.screen = screen
        self.mode = mode
        self.status = 'waiting' if self.mode == 'online' else 'start'

        self.frame = pg.Surface((width, height)).convert()
        self.camera = self.frame.get_rect()
        
        self.clock = pg.time.Clock()

        self.n = connection
        self.playing = True
        self.logs = {}

        self.pid = self.n.get_pid()
        self.colors = gen_colors(self.pid + 1)
        self.players = [Player(self, self.pid)]
        
        self.main_p = self.players[0]
        
        self.event = None
        self.view_card = None
        self.last_item = None
        
        self.card_outline = get_outline(pg.Rect(0, 0, cw, ch), r=4)
        self.outlined_card = None
        
        self.cards = []
        self.lines = []
        self.moving_cards = []
        self.particles = []
        self.shop = []

        self.loop_times = []

        self.set_screen()
        self.add_panes()
        
        self.run()
        
#screen stuff-----------------------------------------------------------------------------------
        
    def set_screen(self):
        ph = ch * 6
        
        self.panes = {}
        self.text = {}
        self.targets = {}
        self.btns = []

        pane = Pane(pg.Rect(0, 0, cw * 1.5, ph), 'your sequence', (255, 0, 0))
        pane.rect.bottomleft = (20, height - 20)
        pane.move_text()
        self.panes['card area'] = pane

        pane = Pane(pg.Rect(0, 0, cw * 2.5, ph), 'selection', (0, 0, 255))
        pane.rect.bottomright = (width - 20, height - 20)
        pane.move_text()
        self.panes['selection area'] = pane
        
        pane = Pane(pg.Rect(0, 0, cw * 1.5, ch * 1.5), 'active card', (255, 255, 255))
        pane.rect.bottomright = self.panes['selection area'].rect.bottomleft
        pane.rect.x -= 10
        pane.move_text()
        self.panes['active card'] = pane
        
        pane = Slider(pg.Rect(0, 0, cw * 10, ch * 4), 'extra cards', (0, 0, 0), dir='-y')
        pane.new_x(self.panes['card area'].rect.right + 10)
        pane.new_y(height)
        self.panes['extra cards'] = pane
        
        text = Textbox('', 50, (0, 255, 0))
        text.rect.midbottom = (width // 2, height)
        text.rect.y -= 10
        self.text['play'] = text
        
        pane = Slider(pg.Rect(0, 0, cw * 4, ch * 1.5), 'shop', (255, 255, 0), dir='-y')
        pane.new_x(self.text['play'].rect.right + pane.rect.width // 2)
        pane.new_y(height)
        self.panes['shop'] = pane

        self.add_panes()

        self.view_card_rect = pg.Rect(0, 0, 375, 525)
        self.view_card_rect.center = (width // 2, height // 2)
        
        text = Textbox('options', 20)
        text.rect.topright = (width, 0)
        text.rect.y += 30
        text.rect.x -= 30
        self.text['options'] = text
        self.btns.append(text)
        
        text = Textbox(self.status, 20, tcolor=(0, 255, 0))
        text.rect.centerx = self.text['options'].rect.centerx
        text.rect.y += 60
        self.text['status'] = text
        
        text = Textbox('', 20, (255, 255, 0))
        text.rect.midtop = self.text['status'].rect.midbottom
        text.rect.y += 10
        self.text['round'] = text
        
        text = Textbox('', 100, tcolor=(255, 255, 0))
        text.rect.center = (width // 2, height // 2)
        self.text['winner'] = text
        
        pane = Pane(pg.Rect(0, 0, cw, ch), 'event')
        pane.rect.midbottom = self.panes['selection area'].rect.midtop
        pane.rect.y -= 30
        pane.rect.right = self.panes['selection area'].rect.right
        pane.move_text()
        self.panes['event'] = pane
        
        pane = Pane(pg.Rect(0, 0, cw * 1.5, ch * 1.5), 'item discard')
        pane.rect.midbottom = self.panes['selection area'].rect.midtop
        pane.rect.y = self.panes['event'].rect.y
        pane.rect.left = self.panes['selection area'].rect.left
        pane.rect.x -= 10
        pane.move_text()
        self.panes['last used item'] = pane
        
        self.coin = [Textbox('tails', 20, (255, 0, 0)), Textbox('heads', 20, (0, 255, 0)), Textbox('flip', 20, (255, 255, 0))]
        self.dice = [Textbox(str(i + 1), 20, tcolor) for i, tcolor in enumerate(gen_colors(6))] + [Textbox('roll', 20, (255, 255, 0))]
        self.select = Textbox('selecting', 15, (255, 255, 0))

        for t in self.coin + self.dice + [self.select]:

            t.add_outline((0, 0, 0))
            
#pane stuff --------------------------------------------------------------------------------------------------------------

    def add_panes(self):
        col = 5
        rows = len(self.players) // col
        ph = (height // (rows + 1)) * 0.6

        y = 40

        for row in range(rows + 1):
            
            players = self.players[row * col:(row + 1) * col]

            if not players:
                
                break
            
            left = self.panes['card area'].rect.right
            right = self.panes['selection area'].rect.left - 50
            step = (right - left) // len(players) 

            for i, x in zip(range(len(players)), range(left + step // 2, right + step, step)):
                
                p = players[i]
                
                i += (col * row)
        
                pane = Pane(pg.Rect(x, y, cw * 1.5, ph), p.name, tsize=20, color=(0, 0, 0), tcolor=p.color)
                pane.lock = 0
                self.panes[f'spot {i}'] = pane

                pane = Pane(pg.Rect(x, y, cw * 1.5, ch), '', tsize=20, tcolor=p.color)
                pane.rect.x = pane.rect.right
                pane.rect.y += 5
                pane.move_text()
                self.panes[f'ac {i}'] = pane
                
                pane = Slider(pg.Rect(x, y, cw * 1.5, ph), '', tsize=20, dir='-x', tcolor=p.color)
                self.panes[f'landscape {i}'] = pane
                
                tr = self.panes[f'spot {i}'].rect.topright
                
                target = Target(self)
                target.rect.bottomleft = self.panes[f'spot {i}'].rect.topright
                target.rect.x += 5
                self.targets[p.pid] = target
                
            y += 40 + ph
            
        for t in list(self.text.keys()):
            
            if 'score' in t:
                
                del self.text[t]
            
        y = 5
        
        for i, p in enumerate(self.players):

            text = Textbox(f'{p.name}: {p.score}', tsize=12, tcolor=p.color)
            text.rect.topleft = (5, y)
            self.text[f'score {i}'] = text
            
            y += text.rect.height

    def relable_panes(self):
        for i, p in enumerate(self.players):
            
            pane = self.panes[f'spot {i}']
            pane.update_text(p.name, p.color)
            
            target = self.targets[p.pid]
            target.rect.topleft = pane.textbox.rect.topright
            target.rect.x += 5
            target.adjust_course()
            
            text = self.text[f'score {i}']
            tl = text.rect.topleft
            text.update_text(f'{p.name}: {p.score}', tcolor=p.color)
            text.rect.topleft = tl
            
    def update_scores(self, scores):
        counter = 0
        
        for pid, score in scores.items():
            
            p = self.get_player_by_pid(int(pid))
                
            if p:
                
                if p.score == score:
                    
                    counter += 1
                    
                else:
                
                    p.score = score
                    
        if counter != len(self.players):
                
            y = 5
            players = sorted(self.players, key=lambda p: p.score, reverse=True)
            
            for i, p in enumerate(players):
            
                text = self.text[f'score {i}']
                text.update_text(f'{p.name}: {p.score}', tcolor=p.color)
                text.rect.topleft = (5, y)
                y += text.rect.height

    def update_panes(self):
        self.cards.clear()

        self.cards += self.panes['last used item'].add_cards([self.last_item] if self.last_item is not None else [])
        self.cards += self.panes['event'].add_cards([self.event] if self.event is not None else [])
        self.cards += self.panes['shop'].add_cards(self.shop, dir='x')

        for i, p in enumerate(self.players):

            self.cards += self.panes[f'spot {i}'].add_cards(p.played)
            self.cards += self.panes[f'ac {i}'].add_cards([p.active_card] if p.active_card is not None else [])
            
            cards = p.ongoing.copy()
            
            if self.status not in ('waiting', 'playing', 'draft'):
                
                cards += [c.copy() for c in p.treasure]
            
            if p.landscape is not None:
                
                cards.insert(0, p.landscape)
                
            self.cards += self.panes[f'landscape {i}'].add_cards(cards)

            if p == self.main_p:
                
                self.cards += self.panes['card area'].add_cards(p.unplayed.copy())
                self.cards += self.panes['extra cards'].add_rows({(255, 0, 0): p.items + p.equipped, (255, 0, 255): p.spells, (255, 255, 0): p.treasure})
                self.cards += self.panes['selection area'].add_cards(p.selection.copy())
                self.cards += self.panes['active card'].add_cards([p.active_card.copy()] if p.active_card is not None else [])
      
    def get_pane(self, key):
        return self.panes.get(key)
        
    def get_pane_by_player(self, name, player):
        key = name + ' ' + str(self.players.index(player))
        
        return self.panes.get(key)

#option stuff------------------------------------------------------------------------------
              
    def set_option(self):
        mp = self.main_p
        option = ''
        tcolor = (0, 0, 0)
        text = self.text['play']
        
        if mp.coin is not None:
            
            option = self.coin[mp.coin].message
            tcolor = self.coin[mp.coin].tcolor
            
        elif mp.dice is not None:
            
            option = self.dice[mp.dice].message
            tcolor = self.dice[mp.dice].tcolor
            
        elif mp.selection:
            
            option = 'select'
            tcolor = (255, 255, 0)
            
        elif mp.is_turn:
            
            option = 'play'
            tcolor = (0, 255, 0)
            
        if text.message != option:
            
            text.update_text(option, tcolor)
        
            if option in ('play', 'flip', 'roll'):
                
                if text not in self.btns:
                    
                    self.btns.append(text)
                    
            else:
                
                if text in self.btns:
                    
                    self.btns.remove(text)
        
    def is_option(self, option):
        return self.get_option() == option
        
    def get_option(self):
        return self.text['play'].message
        
#status stuff----------------------------------------------------------------------------------

    def change_round(self, text):
        self.text['round'].update_text(text)
        
    def set_status(self, stat):
        btn = self.text['status']
        
        if stat == 'waiting':
        
            if (self.mode == 'online' and self.pid == 0 and len(self.players) > 1) or self.mode == 'single':
        
                stat = 'start'
                
        elif stat == 'new round':
            
            if self.pid != 0:
                
                stat = 'round over'
                
        elif stat == 'new game':
            
            if self.pid != 0:
                
                stat = 'game over'

        self.status = stat
        btn.update_text(stat)
        
        if stat in ('new round', 'new game', 'start'):
            
            if btn not in self.btns:
            
                self.btns.append(btn)
            
        elif btn in self.btns:
            
            self.btns.remove(btn)
            
    def get_status(self):
        return self.text['status'].message
        
    def is_status(self, stat):
        return self.get_status() == stat
                
#start up stuff-----------------------------------------------------------------------------------------

    def reset(self):
        for p in list(self.panes.values()):
            
            p.reset()
            
        for p in self.players:
            
            p.reset()

        self.cards.clear()
        self.shop.clear()
        self.event = None
        self.last_item = None
        
        self.status = 'waiting' if self.mode == 'online' else 'start'
        self.change_round('')

        self.reset_win_screen()
        
    def new_round(self):
        for p in self.players:
            
            p.new_round()
            
        self.shop.clear()

    def quit(self):
        self.n.close()
        
        self.playing = False
        
        pg.quit()
        sys.exit()
        
    def exit(self):
        self.n.close()
        
        self.playing = False   

    def send(self, data):
        if self.playing:
        
            reply = self.n.send(data)
            
            if reply is None:
                
                self.playing = False
                
            else:

                return reply
                
    def set_name(self):
        name = name_entry(self.pid, self.colors[self.pid])
        
        if not name:
            
            self.exit()
            
        else:

            self.main_p.name = name
            self.send(f'name,{name}')
            
#server stuff-----------------------------------------------------------------------------
        
    def get_info(self):
        u, scores = self.send('u')
        self.update_scores(scores)
        
        if u:
            
            info = self.send('info')

            for key in info:
                
                if key in self.logs:
                    
                    self.logs[key] += info[key]
                    
                else:
                    
                    self.logs[key] = info[key]

    def update_info(self):
        glogs = self.logs.get('g')
        
        if glogs:

            self.parse_logs('g', glogs[:5])
            self.logs['g'] = self.logs['g'][5:]
            
        else:
            
            for key, logs in self.logs.items():
                
                if key != 'g' and logs:
                    
                    pid = int(key)
                    
                    if not self.get_player_by_pid(pid):
                        
                        self.add_player(pid)
                        
                    self.parse_logs(pid, logs[:5])
                    self.logs[key] = self.logs[key][5:]
                    
                    break
            
    def parse_logs(self, pid, logs):
        for log in logs:
        
            type = log.get('t')
            
            if 'c' in log:
            
                name, uid = log.get('c')
            
            if pid == 'g':
                
                if type == 'fill':
                    
                    self.shop.append(Card(name, uid))
                    
                elif type == 'sw':
                    
                    self.swap(log.get('c1'), log.get('c2'))
                    
                elif type == 'add':
                    
                    self.add_player(log.get('pid'))
                    
                    if self.mode == 'online':
                
                        if self.pid == 0 and len(self.players) > 1:
                        
                            self.set_status('start')

                elif type == 'del':
                    
                    self.remove_player(log.get('pid'))
                    
                    if self.pid == 0:
                    
                        if self.mode == 'online':

                            if len(self.players) == 1 and self.is_status('start'):
                            
                                self.set_status('waiting')
                            
                            if self.get_status() not in ('waiting', 'start'):
                                
                                self.send('reset')
                    
                elif type == 'ord':
                    
                    self.reorder(log.get('ord'))
                    
                elif type == 'sd':
                    
                    self.shift_down(log.get('pid'))
                    
                elif type == 'su':
                    
                    self.shift_up(log.get('pid'))
                    
                elif type == 'fin':
                    
                    self.win_screen(log.get('w'))
                    
                elif type == 'res':
                    
                    self.reset()
                    
                elif type == 'nt':
                
                    self.switch_turn(log.get('pid'))
                    
                elif type == 'ns':
                    
                    self.set_status(log.get('stat'))
                    
                elif type == 'se':
                    
                    self.set_event(name, uid)
                    
                elif type == 'nr':
                    
                    self.new_round()
                    
                elif type == 'ur':

                    self.change_round(log.get('s'))
                    
            else:
                
                p = self.get_player_by_pid(pid)
                
                if type == 'play' and not log.get('d'):
                    
                    p.play(uid)
                    
                elif type in ('gp', 'lp', 'give', 'sp'):
                    
                    self.unpack_points(pid, log)
                    
                elif type == 'nl':
                    
                    p.new_lead(uid)
                    
                elif type == 'nd':
                    
                    p.new_deck(log.get('deck'), log.get('cards'))
                    
                elif type == 'cd':
                
                    p.clear_deck(log.get('d'))
                    
                elif type == 'eq':
                    
                    p.equip(uid)
                    
                elif type == 'ueq':
                    
                    p.unequip(uid)
                    
                elif type == 'st':
                    
                    p.steal_treasure(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'si':
                    
                    p.steal_item(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'ss':
                
                    p.steal_spell(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'gt':
                    
                    p.give_treasure(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'gi':
                    
                    p.give_item(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'gs':
                
                    p.give_spell(self.get_player_by_pid(log.get('target')), uid)
                    
                elif type == 'ut':
                    
                    p.use_treasure(uid)
                    
                elif type == 'ui':
                    
                    p.use_item(uid, name)
                    
                elif type in ('dt', 'at'):
                    
                    p.draw_treasure(name, uid)
                    
                elif type in ('di', 'ai'):
                    
                    p.draw_item(name, uid)
                    
                elif type == 'ds':
                    
                    p.draw_spell(name, uid)
                    
                elif type == 'as':
                    
                    p.add_spell(name, uid)
                    
                elif type == 'cast':
                    
                    p.cast(uid, self.get_player_by_pid(log.get('target')))
                    
                elif type in ('rs', 'disc'):
                    
                    p.discard(uid)
                    
                elif type == 'buy':
                    
                    p.buy(uid, log.get('ctype'))
                    
                elif type == 'au':
                    
                    p.add_unplayed(name, uid)
                    
                elif type == 'd':
                    
                    p.draft(uid)
                    
                elif type == 'cn':
                    
                    p.update_name(log.get('name'))
                    self.relable_panes()
                    
                elif type == 'aac':
                    
                    p.new_ac(Card(name, uid), log.get('w'))
                    
                elif type == 'rac':
                    
                    p.remove_ac()
                    
                elif type == 'sl':
                    
                    p.set_landscape(Card(name, uid))
                    
                elif type == 'sels':
                    
                    p.new_deck('selection', log.get('cards'))
                    
                elif type == 'sele':
                    
                    p.cancel_select()
                    
                elif type == 'cfr':
                    
                    p.flip_request()
                    
                elif type == 'cfs':
                    
                    p.start_flip()
                    
                elif type == 'cfe':
                    
                    p.end_flip(log.get('coin'), log.get('ft'))

                elif type == 'drr':
                    
                    p.roll_request()
                    
                elif type == 'drs':
                    
                    p.start_roll()
                    
                elif type == 'dre':
                    
                    p.end_roll(log.get('dice'), log.get('rt'))
                    
                elif type == 'rc':
                
                    p.remove_coins(uid)
     
#main loop-----------------------------------------------------------------------------
            
    def run(self):
        self.set_name()

        while self.playing:
        
            self.clock.tick(30)
            
            #print(self.clock.get_fps())

            self.get_info()
            self.update_info()
            
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        mouse = pg.Rect(0, 0, 1, 1)
        mouse.center = pg.mouse.get_pos()
        
        outline_buttons(mouse, self.btns)

        for e in pg.event.get():
            
            if e.type == pg.QUIT:
            
                self.quit() 
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    self.quit()
                    
                elif e.key == pg.K_s and self.pid == 0:
                    
                    self.send('start')
                    
                elif e.key == pg.K_p:
                    
                    self.send('play')
                        
                elif e.key == pg.K_x:
                    
                    self.send('cancel')

                elif e.key == pg.K_LALT or e.key == pg.K_RALT:

                    for c in self.cards:
                        
                        if c.rect.colliderect(mouse):
                            
                            self.view_card = c
                            
                            break

            elif e.type == pg.KEYUP:
                    
                if e.key == pg.K_LALT or e.key == pg.K_RALT:
                
                    self.view_card = None
                    
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                if e.button == 1:
                
                    if mouse.colliderect(self.text['options'].rect):
                        
                        game_menu(self)
                        
                        return
                        
                    elif mouse.colliderect(self.text['status'].rect) and self.pid == 0:
                        
                        stat = self.get_status()
                        
                        if stat == 'start':
                            
                            self.send('start')
                            
                        else:
                            
                            self.send('continue')

                    elif mouse.colliderect(self.text['play'].rect):
                        
                        option = self.get_option()
                        mp = self.main_p
                        
                        if option == 'play' and mp.is_turn:
                        
                            self.send('play')
                            
                        elif option == 'flip' and mp.coin is not None:
                            
                            self.send('flip')
                            
                        elif option == 'roll' and mp.dice is not None:
                            
                            self.send('roll')
                        
                    else:
                        
                        for c in self.cards:
                            
                            if mouse.colliderect(c.rect):

                                self.send(str(c.uid))
                                
                                break
                            
                    for p in self.panes.values():
                        
                        if hasattr(p, 'click'):
                            
                            if p.rect.colliderect(mouse):
                                
                                p.click()
                                
                                break
                                
                elif e.button in (4, 5):

                    for pane in self.panes.values():
                        
                        if pane.rect.colliderect(mouse):
                        
                            pane.scroll(mouse, e.button)
                            
                            break
                        
    def update(self):  
        mouse = pg.Rect(0, 0, 1, 1)
        mouse.center = pg.mouse.get_pos()
        
        self.set_option()

        for p in self.players:
            
            p.update()

        for pane in self.panes.values():
            
            if hasattr(pane, 'hit'):
                
                pane.hit(mouse)
            
            if hasattr(pane, 'update'):
                
                if pane.check_mode():
                
                    pane.update()

        for c in self.cards:
            
            if c.rect.colliderect(mouse):
                
                self.outlined_card = c
                self.card_outline = c.get_outline()
            
                s = c.rect.center
                
                other = self.find_card(c)
                
                if other:
                
                    e = other.rect.center
                    self.lines.append((s, e))
                    
                break
                
        else:
            
            self.outlined_card = None
    
        for c in self.main_p.equipped:

            if c.rect.colliderect(self.camera):
            
                self.add_particles(c.rect, 1, (255, 0, 0), type=2)
    
        for p in self.players:
            
            if p.is_turn:
                
                self.add_particles(p.get_spot().rect, 2, p.color, type=2)
                
                break

        for p in self.particles.copy():
            
            if not p.update():
                
                self.particles.remove(p)
                
        self.update_panes()

        for target in self.targets.values():
            
            target.update()
        
    def draw(self):
        self.frame.fill((0, 0, 0))

        for i in range(len(self.players)):
            
            self.panes[f'landscape {i}'].draw(self.frame)
            self.panes[f'ac {i}'].draw(self.frame)
            self.panes[f'spot {i}'].draw(self.frame)
            
        self.panes['card area'].draw(self.frame)
        self.panes['selection area'].draw(self.frame)
        self.panes['active card'].draw(self.frame)
        self.panes['extra cards'].draw(self.frame)
        self.panes['event'].draw(self.frame)
        self.panes['active card'].draw(self.frame)
        self.panes['last used item'].draw(self.frame)
        self.panes['shop'].draw(self.frame)

        for key in self.text:
        
            text = self.text[key]
            self.frame.blit(text.text, text.rect)

        for t in self.targets.values():
            
            self.frame.blit(t.textbox.get_image(), t.rect)
            
            for p in t.points:
                
                self.frame.blit(p.image, p.rect)
                
            for c in t.cards:
                
                self.frame.blit(c.get_image(), c.rect)
                
        for s, e in self.lines:
        
            pg.draw.line(self.frame, (255, 0, 0), s, e, 5)
            
        self.lines.clear()

        for p in self.players:

            c = self.get_pane_by_player('ac', p).rect.center
            
            if p.coin is not None:
                
                img = self.coin[p.coin].get_image()
                r = img.get_rect()
                r.center = c
                self.frame.blit(img, r)
                
            elif p.dice is not None:
            
                img = self.dice[p.dice].get_image()
                r = img.get_rect()
                r.center = c
                self.frame.blit(img, r)
                
            elif p.selection:
                
                img = self.select.get_image()
                r = img.get_rect()
                r.center = c
                self.frame.blit(img, r)
                    
        for c in self.moving_cards:
            
            self.frame.blit(c.get_image(), c.rect)
            
        if self.view_card:
        
            self.frame.blit(self.view_card.get_image(False), self.view_card_rect)

        for p in self.particles:
            
            pg.draw.circle(self.frame, p.color, p.pos, p.r)
            
        if self.outlined_card:
            
            wo, ho = self.card_outline.get_size()
            wc, hc = self.outlined_card.rect.size
            xc, yc = self.outlined_card.rect.topleft
            
            self.frame.blit(self.card_outline, (xc - ((wo - wc) // 2), yc - ((ho - hc) // 2)))

        self.screen.blit(self.frame, (0, 0))
        pg.display.flip()
        
#helper stuff-------------------------------------------------------------------------------

    def update_colors(self):
        self.colors = gen_colors(len(self.colors) + 1)
        
        for p in self.players:
            
            p.color = self.colors[p.pid]

    def add_player(self, pid):
        if not any(p.pid == pid for p in self.players):
            
            self.update_colors()
        
            p = Player(self, pid)
            
            self.players.append(p)
            self.players.sort(key=lambda p: p.pid)
            self.add_panes()

            return p
        
    def remove_player(self, pid):
        if any(p.pid == pid for p in self.players):
            
            p = self.get_player_by_pid(pid)
            i = self.players.index(p)
            
            del self.targets[p.pid]
            del self.panes[f'spot {i}']
            del self.panes[f'ac {i}']
            del self.panes[f'landscape {i}']
            
            if p.pid in self.logs:
                
                del self.logs[p.pid]

            self.players.remove(p)
            self.update_colors()
            self.add_panes()
            
            if pid == 0:
                
                self.exit()
                
                new_message('the host closed the game', 2000)
        
    def reorder(self, pids):
        players = []
        
        for pid in pids:
            
            p = self.get_player_by_pid(pid)
            
            if p:
                
                players.append(p)
                
        self.players = players

        self.relable_panes()
        
    def shift_down(self, pid):
        p = self.get_player_by_pid(pid)
        
        self.players.append(self.players.pop(self.players.index(p)))
        
        self.relable_panes()
        
    def shift_up(self, pid):
        p = self.get_player_by_pid(pid)
        
        self.players.insert(0, self.players.pop(self.players.index(p)))
        
        self.relable_panes()
        
    def win_screen(self, pids):
        winners = []
        
        for pid in pids:
            
            p = self.get_player_by_pid(pid)
            
            if p is not None:
                
                winners.append(p)
                
        text = self.text['winner']
                
        if len(winners) == 1:
            
            w = winners[0]
            text.update_text(f'{w.name} wins!', tcolor=w.color)
            text.add_outline((0, 0, 0))
            self.add_particles(text.rect, 5000, w.color)
            
        else:
            
            colors = [w.color for w in winners]
            
            message = f'{len(winners)} way tie!'
            
            while len(message.replace(' ', '')) < len(winners):
                
                message += '!'
            
            text.update_text_multicolor(message, colors)
            text.add_outline((0, 0, 0))

            for c in colors:
                
                self.add_particles(text.rect, 5000 // len(colors), c)
        
    def reset_win_screen(self):
        text = self.text['winner']
        text.clear()
        
    def switch_turn(self, pid):
        for p in self.players:
            
            if p.pid == pid:
                
                p.is_turn = True
                
            else:
                
                p.is_turn = False
  
    def set_event(self, name, uid):
        self.event = Card(name, uid)

    def swap(self, c1, c2):
        name1, uid1 = c1
        name2, uid2 = c2
        
        check1 = False
        check2 = False
       
        for p in self.players:
            
            for deck in p.get_cards():
                
                for i in range(len(deck)):
                
                    c = deck[i]

                    if c.uid == uid1 and not check1:
                        
                        deck.pop(i)
                        deck.insert(i, Card(name2, uid2))
                        check1 = True
                        
                    elif c.uid == uid2 and not check2:
                        
                        deck.pop(i)
                        deck.insert(i, Card(name1, uid1))
                        check2 = True
                        
                if check1 or check2:
                    
                    break
                        
    def unpack_points(self, pid, pack):
        uid = pack.get('c')[1]
        type = pack.get('t')
        
        if pack.get('d'):
            
            return
        
        if type == 'gp':
            
            points = pack.get('gp')
            
        elif type == 'lp':
            
            points = -pack.get('lp')
            
        elif type == 'sp':
        
            points = pack.get('sp')
            
        elif type == 'give':
            
            points = -pack.get('gp')

        if type == 'sp':
            
            target = pack.get('target')
            s = self.get_spot(target).rect.topleft
            self.targets[pid].add_points(points, s)
            
        elif type == 'give':
            
            target = pack.get('target')
            s = self.get_spot(pid).rect.topleft
            self.targets[target].add_points(points, s)
            
        elif type == 'gp' or type == 'lp':
            
            card = self.find_uid(uid)
            
            if card:
                
                s = card.rect.center
                
            else:
                
                s = self.targets[pid].rect.center
                
            self.targets[pid].add_points(points, s)

#-------------------------------------------------------------------------------------------

    def get_player_by_pid(self, pid):
        return next((p for p in self.players if p.pid == pid), None)
   
    def update_settings(self, settings):
        for key, val in settings.items():
            
            reply = self.send(f'~{key},{val}')
            
        return reply

    def find_local_card(self, card):
        for c in self.panes['extra cards'].cards:
            
            if c == card:
                
                return c
        
    def find_card(self, other):
        cards = []
        
        pos = (0, 0)
        
        for p in self.players:
            
            cards += self.panes[f'spot {p.pid}'].cards
            cards += self.panes[f'landscape {p.pid}'].cards
            
        c = next((c for c in cards if c.uid == other.uid and c is not other and spritesheet.check_name(c.name) and c.rect.topleft != pos), None)
            
        return c
                
    def find_uid(self, uid):
        for c in self.cards:
            
            if uid == c.uid and spritesheet.check_name(c.name):
                
                return c
    
    def get_spot(self, pid):
        return self.panes[f'spot {self.players.index(next((p for p in self.players if pid == p.pid)))}']
        
    def get_target(self, pid):
        return self.targets[pid]
        
    def get_panes(self, name):
        panes = []
        
        for key in self.panes:
            
            if name in key:
                
                panes.append(self.panes[key])
                
        return panes
    
    def add_particles(self, rect, num, color=(255, 255, 0), radius=None, type=1):
        if len(self.particles) < 1500:
        
            for _ in range(num):
                
                if type == 1:
                
                    self.particles.append(Particle1(rect, color, radius))
                
                else:
                    
                    self.particles.append(Particle2(rect, color, radius))
   
pg.init()

clock = pg.time.Clock()

win = pg.display.set_mode((width, height))
pg.display.set_caption('card game')

spritesheet = Spritesheet()

if not os.path.exists('save.json'):
    
    save_data = new_save()
    
else:
    
    save_data = read_save()
   
main()
    
pg.quit()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        