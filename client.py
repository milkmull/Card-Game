import pygame as pg
import time
import sys
import os
import subprocess
import random
from requests import get as getreq
from network import Network, InvalidIP
from spritesheet import Spritesheet, Textbox, create_text, Counter, Input
from settings import settings as defult_settings

operating_system = sys.platform

info = ['log', 'is_turn', 'coin', 'dice', 'flipping', 'rolling', 'score', 'selection', 'unplayed', 'played', 'equipped', 'items', 'spells', 'ongoing', 'treasure', 'active_card', 'landscape']

light_info = ['log', 'flipping', 'rolling', 'is_turn', 'coin', 'dice', 'score', 'played', 'ongoing', 'active_card', 'landscape', 'treasure']

colors = ((0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 128, 0), (210, 105, 30), (255, 192, 203), (255, 127, 0))

pg.init()

clock = pg.time.Clock()

width = 1024
height = 576

cw = 375 // 10
ch = 525 // 10
ph = ch * 7

fps = 30

win = pg.display.set_mode((width, height)) #initiate window

spritesheet = Spritesheet() #load spritesheet info

def get_ips(): #returns dictionary of any saved ip addresses (used for connecting via port forwarding)
    with open('ips.txt', 'r') as f:
    
        ips = {name: ip for name, ip in [tup.strip().split(' ') for tup in f]}
        
    return ips
    
def update_ips(name, ip):
    with open('ips.txt', 'r+') as f:
        
        ips = {name: ip for name, ip in [tup.strip().split(' ') for tup in f]}
        
        if name not in ips.keys() and ip not in ips.values():
    
            f.write('{} {}\n'.format(name, ip))
            
def del_ips(name):
    ips = get_ips()
    
    del ips[name]
    
    with open('ips.txt', 'w+') as f:
        
        for name, ip in ips.items():
        
            f.write('{} {}\n'.format(name, ip))
            
def flatten(lst):
    return [c for L in lst for c in L]

def copy_to_clipboard(text):
    if operating_system.startswith('linux'):
        
        command = 'echo ' + text.strip() + '| xclip'
        
    elif operating_system.startswith('win'):
    
        command = 'echo ' + text.strip() + '| clip'
    
    elif operating_system.startswith('darwin'):

        command = 'echo ' + text.strip() + '| pbcopy'
        
    else:
        
        return
        
    os.system(command)

def pack_log(log):
    if log['type'] == 'gp':
        
        return ('gp', log['gp'], log['card'][1])
        
    elif log['type'] == 'lp':
        
        return ('lp', log['lp'], log['card'][1])
        
    elif log['type'] == 'sp':   
        
        return ('sp', log['sp'], log['target'], log['card'][1])
        
    elif log['type'] == 'rp':
        
        return ('rp', log['rp'], log['robber'], log['card'][1])
        
    elif log['type'] == 'give':
        
        return ('give', log['gp'], log['target'], log['card'][1])

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

#main------------------------------------------------------------------------------

def main():
    running = True
    
    while running:
        
        mode = main_menu()
        
        if mode == 'search online':
            
            ip = client_menu()
            
            if ip:
                
                connect(ip)
                
        elif mode == 'search local':
            
            connect()
                
        elif mode == 'host':
            
            subprocess.Popen('server.exe')
            
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
        
        for name, ip in get_ips().items():
        
            text = Textbox(name + ': ' + ip, 20)
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
        text.rect.y += 5
        screen.append(text)
        
        text = Textbox(' [join game]', 20, tcolor=(0, 255, 0))
        text.rect.bottomright = (0, 0)
        screen.append(text)
        
        text = Textbox(' [delete]', 20, tcolor=(255, 0, 0))
        text.rect.bottomright = (0, 0)
        screen.append(text)
        
    elif mode == 'new entry':
        
        text = Textbox('entry name: ', 20)
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
        
        text = Textbox('entry IP: ', 20)
        text.rect.topright = screen[-2].rect.bottomright
        text.rect.y += 20
        screen.append(text)
        
        text = Input('012.345.6789', 20)
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
        
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        screen.append(text)
        
    elif mode == 'name':
        
        text = Textbox('enter your name:', 30)
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

        text = Textbox('your public IP:  {}'.format(getreq('http://ip.42.pl/raw').text), 20)
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
    btns = set_screen('main')
    
    mode = None

    while mode is None: #once player chooses a mode, go to next screen
        
        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                mode = 'quit'
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    mode = 'quit'
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for t in btns:
                    
                    if t.rect.colliderect(r):
                        
                        if t.message == 'find online game':
                            
                            mode = 'search online'
                            
                        elif t.message == 'host game':
                            
                            mode = 'host'
                            
                        elif t.message == 'find local game':
                            
                            mode = 'search local'
                            
                        elif t.message == 'single player':
                            
                            mode = 'single'
        
    return mode
    
def client_menu():
    btns = set_screen('choose host')
    options = btns[-2:]

    def move_options(p):
        options[0].rect.topleft = p
        options[1].rect.topleft = options[0].rect.topright
        
    def reset_options():
        for t in options:
        
            t.rect.bottomright = (0, 0)
            
    name = ''
    ip = ''
    
    running = True
    
    while running:
        
        clock.tick(60)
        
        new_screen(btns)

        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for t in btns:
                    
                    if t.rect.colliderect(r):
                        
                        if t.message == 'back':
                            
                            return
                            
                        elif t.message == 'new entry':
                        
                            tup = new_entry()
                            
                            if tup is not None:
                            
                                name, ip = tup
                                
                                update_ips(name, ip)
                                
                                btns = set_screen('choose host')
                                options = btns[-2:]
                                
                            break
                            
                        elif t.message == 'view my ip':
                            
                            view_ip()
                            
                            break
                            
                        elif ip and 'join game' in t.message:
                            
                            return ip
                            
                        elif ip and 'delete' in t.message:
                            
                            del_ips(name)
                            
                            btns = set_screen('choose host')
                            options = btns[-2:]
                            
                            break
                            
                        elif isinstance(t, Textbox):
                            
                            name, ip = t.message.split(': ')

                            move_options(t.rect.topright)
                            
                            break
                            
                else:
                
                    name = ''
                    ip = ''
                    
                    reset_options()
        
def new_entry(info=None):
    btns = set_screen('new entry')
    
    if info:
        
        name, ip = info
        
        btns[1].update_text(name)
        btns[3].update_text(ip)

    field = None
    
    running = True
    
    while running:
        
        clock.tick(60)
        
        new_screen(btns)
        
        if field is not None:

            field.update()

        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
                elif field is not None and e.key == pg.K_BACKSPACE:
                    
                    field.send_keys()
                    
                elif field is not None and e.key == pg.K_RETURN:
                    
                    field.close()
                    field = None
                    
                elif field is not None and hasattr(e, 'unicode'):
                    
                    if e.unicode.strip():
                    
                        field.send_keys(e.unicode)

            elif e.type == pg.MOUSEBUTTONDOWN:

                for btn in btns:
                    
                    if r.colliderect(btn.rect):
                    
                        if isinstance(btn, Input):
                            
                            if field is not None:
                                
                                field.close()
                            
                            field = btn
                            
                        elif btn.message == 'back':
                        
                            return
                            
                        elif btn.message == 'save':
                            
                            return (btns[1].get_message(), btns[3].get_message())
                            
                        break
                        
                        
                        
                else:
                    
                    if field is not None:
                    
                        field.close()
                        field = None
  
def view_ip(info=None):
    btns = set_screen('view ip')

    running = True
    
    while running:
        
        clock.tick(60)
        
        new_screen(btns)

        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
               
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return

            elif e.type == pg.MOUSEBUTTONDOWN:

                for btn in btns:
                    
                    if r.colliderect(btn.rect):
                    
                        if btn.message == 'back':
                            
                            return
                            
                        elif 'copy' in btn.message:
                            
                            copy_to_clipboard(getreq('http://ip.42.pl/raw').text)
  
#in game menues------------------------------------------------------------------------------
 
def settings_screen(pid, settings): #special function to set up the settings screen
    screen = []
    
    text = Counter('rounds', settings['rounds'], range(1, 26), 20)
    screen.append(text)
    
    text = Textbox('free play: {}'.format(settings['fp']), tsize=20)
    screen.append(text)
    
    text = Counter('starting score: ', settings['ss'], range(5, 51), 20)
    screen.append(text)

    text = Counter('starting cards: ', settings['cards'], range(1, 11), 20)
    screen.append(text)
    
    text = Counter('starting items: ', settings['items'], range(0, 6), 20)
    screen.append(text)
    
    text = Counter('starting spells: ', settings['spells'], range(0, 6), 20)
    screen.append(text)
    
    text = Textbox('score wrap: {}'.format(settings['score wrap']), tsize=20)
    screen.append(text)
    
    text = Counter('number of cpus: ', settings['cpus'], range(1, 10), 20)
    screen.append(text)
    
    y = (height - sum(t.rect.height for t in screen)) / 2
    
    for t in screen:
        
        t.rect.y = y
        t.rect.centerx = width / 2
        
        if isinstance(t, Counter):
        
            t.move_counter()
        
        y += t.rect.height
    
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

    running = True
    
    while running:
        
        client.clock.tick(30)
        
        btns = set_screen(mode)
        
        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                client.quit()
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for t in btns:
                    
                    if t.rect.colliderect(r):
                        
                        if t.message == 'new game':
                            
                            client.send('reset')
                            
                            return
                            
                        elif t.message == 'disconnect':
                            
                            client.exit()
                            
                            pg.time.wait(1000)
                            
                            return
                            
                        elif t.message == 'back':
                            
                            return
                            
                        elif t.message == 'game settings':
                            
                            settings_menu(client, client.send('settings'))
                            
def settings_menu(client, settings):
    pid = client.pid
    
    running = True
    
    while running:
    
        client.clock.tick(30)

        btns = settings_screen(pid, settings)

        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
        for e in pg.event.get():
                
            if e.type == pg.QUIT:
            
                return
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                
                    return
                    
            elif e.type == pg.MOUSEBUTTONDOWN:

                for t in btns:
                    
                    if t.rect.colliderect(r):
                        
                        if pid == 0:
                        
                            if 'free play' in t.message:

                                settings['fp'] = not settings['fp']
                                
                            elif 'score wrap' in t.message:
                            
                                settings['score wrap'] = not settings['score wrap']
                                
                            elif t.message == 'save changes':
                                
                                new_message('saving...', 500)
                                
                                reply = client.update_settings(settings)
                                    
                                if reply:

                                    new_message('changes saved!', 1500)
                                    
                                else:
                                    
                                    new_message('cannot change rules while playing', 2000)
                                
                                return
                                
                            elif t.message == 'reset':
                                
                                settings = defult_settings.copy()
                            
                            elif t.message == 'cancel':
                                
                                return
                                
                        elif t.message == 'cancel':
                            
                            return

                    elif pid == 0 and isinstance(t, Counter):
                        
                        if t.click_counter(r):
                        
                            if 'starting score' in t.message:

                                settings['ss'] = t.get_count()
                                
                            elif 'rounds' in t.message:
                                
                                settings['rounds'] = t.get_count()
                                
                            elif 'cards' in t.message:
                                
                                settings['cards'] = t.get_count()
                        
                            elif 'items' in t.message:
                                
                                settings['items'] = t.get_count()
                                
                            elif 'spells' in t.message:
                                
                                settings['spells'] = t.get_count()
                                
                            elif 'cpus' in t.message:
                                
                                settings['cpus'] = t.get_count()
                                
def name_entry(id):
    btns = set_screen('name')

    field = btns[1]
    field.update_text('player {}'.format(id), tcolor=colors[id])
    
    running = True
    
    while running:
        
        clock.tick(60)
        
        new_screen(btns)

        field.update()
        
        name = field.get_message()

        x, y = pg.mouse.get_pos()
    
        r = pg.Rect(x, y, 1, 1)
        
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

                for t in btns:
                    
                    if t.rect.colliderect(r):
                        
                        m = field.get_message()
                        
                        if t.message == 'OK' and name:
                            
                            return name
                            
                        elif t.message == 'back':
                            
                            return

#new game stuff-------------------------------------------------------------------------

def connect(ip=None): #try connecting to game
    new_message('searching for game...')
    
    try:
                
        c = Client(win, Network(ip)) #attempt to find running game
        
        c.n.close()
        
    except InvalidIP:
        
        new_message('invalid IP address', 1500)
        
    except EOFError as e: #triggers if host or client leaves game
    
        print(e)
        
        new_message('disconnecting...', 1000)
        
    except Exception as e: #catch all other exceptions while playing
        
        print(e, 'c1')
        
        new_message('no games could be found', 2000)
        
def start_game(): #start a new game
    new_message('starting game...', 500)
    
    try:
                
        c = Client(win, Network()) #try to host a game
        
        c.n.close()
        
    except EOFError as e: #triggers if host leaves game
        
        print(e)

        new_message('diconnected', 1000)
        
    except Exception as e: #catch any other exceptions
    
        print(e, 'c2')
        
        new_message('an error occurred', 2000)
        
def single_player(): #start a single player game
    new_message('starting game...', 500)
    
    from game import Game #import game class
    
    Client(win, Game('single'))
    
    new_message('returning to main menu...', 1000) #if any errors occur or player leaves game, retrun to main menu

#-----------------------------------------------------------------------------------

def get_btn(btns, text): #find button in list of buttons based on text
    return next((b for b in btns if b.message == text), None)
    
def show_winner(players): #shows winner of the round
    players.sort(key=lambda p: p.score, reverse=True)
    
    for i, p in enumerate(players):
        
        new_message('1: {}: {} points'.format(p.pid, p.score))
        
class Particle:
    def __init__(self, rect, color):
        self.pos = [random.randrange(rect.left, rect.right), random.randrange(rect.top, rect.bottom)]
        
        self.vel = [random.randrange(-5, 5), random.randrange(-5, 5)]
        
        self.timer = random.randrange(10)
        
        self.r = random.randrange(3)
        
        self.color = color

    def update(self):
        self.vel[1] += 0.5
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.timer -= 1
        
        return self.timer

class Coin:
    def __init__(self, game, tsize=20):
        self.game = game
        
        self.text = [Textbox('tails', tsize), Textbox('heads', tsize), Textbox('flip', tsize)]
        
    def move_text(self, pos):
        for t in self.text:
            
            t.rect.topleft = pos
            
    def adjust_x(self, dx):
        for t in self.text:
            
            t.rect.x += dx
            
    def adjust_y(self, dy):
        for t in self.text:
            
            t.rect.y += dy
            
class Dice:
    def __init__(self, game, tsize=20):
        self.game = game
        
        self.text = [Textbox(str(i + 1), tsize) for i in range(6)]
        self.text.append(Textbox('roll', tsize))
            
    def move_text(self, pos):
        for t in self.text:
            
            t.rect.topleft = pos
            
    def adjust_x(self, dx):
        for t in self.text:
            
            t.rect.x += dx
            
    def adjust_y(self, dy):
        for t in self.text:
            
            t.rect.y += dy
            
class TurnIndicator:
    def __init__(self, game, textbox):
        self.game = game
        
        self.text = textbox
        
        self.rect = self.text.rect.copy()
        
    def change_color(self, tcolor):
        self.text.tcolor = tcolor
        
    def get_image(self):
        return self.text.get_image()
        
    def set_pos(self, rect):
        self.rect.topright = rect.topleft
        
    def reset(self):
        self.rect.bottomright = (0, 0)
 
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
        
        self.textbox.update_text('')
        
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
            
            text = '+{}'.format(self.counter)
            
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
        
            self.text = Textbox('+{}'.format(points), 30, (0, 255, 0))
            
        else:
            
            self.text = Textbox('{}'.format(points), 30, (255, 0, 0))
        
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
        return spritesheet.get_image(self.name, mini)
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.rect.topleft = self.pos
 
class Pane:
    def __init__(self, rect, message, color=(0, 0, 0, 0), layer=0, tsize=10, tcolor=(255, 255, 255)):
        self.rect = rect
        self.textbox = Textbox(message, tsize, tcolor)
        
        self.move_text()
        
        self.color = color
        self.layer = layer
        
        self.cards = []
        self.uids = {}
        
        self.image = self.get_image()
        self.bg = pg.Surface((cw, ch)).convert()
        
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
        
    def move_body(self):
        self.rect.midtop = self.textbox.rect.midbottom
        
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

        
    def update_text(self, message, tcolor=None):
        self.textbox.update_text(message, tcolor)
        
        self.move_text()
        
    def add_cards(self, cards, ypad=5, xpad=5, dir='y', color=None):
        if cards != self.cards:

            if self.rect.size == (cw, ch):
                
                ypad = xpad = 0

            if self.color:
                
                self.image.fill(self.color)
            
            if dir == 'y':
            
                y = 0
                x = 0

                for c in cards:

                    if self.rect.y + y + ypad + c.rect.height > self.rect.bottom:
                        
                        y = 0
                        x = c.rect.width + xpad
                
                    c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                    
                    rel_pos = (x + xpad, y + ypad)
                    
                    color = self.uids.get(c.uid) if color is None else color
                    
                    if color:

                        self.bg.fill(color)
                        self.image.blit(self.bg, (rel_pos[0] - 2, rel_pos[1] - 2))
                        
                        c.color = color
                        
                    self.image.blit(c.get_image(), rel_pos)
                    
                    c.set_rel_pos(rel_pos)
                    
                    y += c.rect.height + ypad

            elif dir == 'x':
                
                y = 0
                x = 0
                
                for c in cards:
                    
                    if self.rect.x + x + xpad + c.rect.width > self.rect.right:
                        
                        x = 0
                        y = c.rect.height + ypad
                    
                    c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                    
                    rel_pos = (x + xpad, y + ypad)
                    
                    color = self.uids.get(c.uid) if color is None else color
                    
                    if color:

                        self.bg.fill(color)
                        self.image.blit(self.bg, (rel_pos[0] - 2, rel_pos[1] - 2))
                        
                        c.color = color
                    
                    self.image.blit(c.get_image(), rel_pos)
                    
                    c.set_rel_pos(rel_pos)
                    
                    x += c.rect.width + xpad

            if hasattr(self, 'start_auto'):
                
                self.start_auto(60)
                
            self.cards = cards.copy()
            
        return self.cards
        
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
            
        return self.cards

    def draw(self, win):
        win.blit(self.image, self.rect)
        
        win.blit(self.textbox.text, self.textbox.rect)
        
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
        self.name = name
        self.color = colors[pid]
        
        self.i = 0
        
        self.host = True if pid == 0 else False

        self.score = 0
        
        self.coin = None
        self.dice = None
        
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
        
    def get_image(self, mini=False):
        return self.card.text
        
    def get_info(self, info):
        step = 1
        
        for i in range(0, len(info), step):
        
            cmd = 'info-' + str(self.pid) + '-' + ','.join(info[i:i + step])
            
            attrs = info[i:i + step]
        
            vals = self.client.send(cmd)
        
            if vals != 'w':
                
                for attr, val in zip(attrs, vals):
            
                    self.update_info(attr, val)

    def update_info(self, attr, val):        
        if attr in ('coin', 'dice', 'flipping', 'rolling', 'is_turn', 'score'):
        
            setattr(self, attr, val)
                
        elif attr in ('landscape', 'active_card', 'used_item'):
            
            if val:
            
                name, uid = val
            
                setattr(self, attr, Card(name, uid))
                
            else:
                
                setattr(self, attr, None)
  
        elif attr == 'log':
            
            self.parse_log(val)
                    
        elif type(val) == list:

            setattr(self, attr, [Card(name, uid) for name, uid in val])
            
    def parse_log(self, val):
        types = ('rp', 'sp', 'lp', 'gp', 'give')
            
        points = [pack_log(log) for log in val if log.get('type') in types]
                    
        self.client.unpack_points(self.pid, points)
        
        ui = next((log['card'] for log in val if log['type'] == 'ui'), None)
        
        if ui:
            
            ui = Card(ui[0], ui[1])
            
            self.client.panes['last used item'].uids[ui.uid] = self.color
            
            if self != self.client.main_p:
                
                self.client.panes['active card'].uids[ui.uid] = self.color
        
        setattr(self, 'used_item', ui)
        
        if any(log['type'] == 'dt' for log in val):
            
            r = self.client.get_spot(self.pid).rect
            self.client.add_particles(r, 100)
            
        buy = next((log['card'] for log in val if log['type'] == 'buy'), None)
        
        if buy:
        
            target = self.client.get_target(self.pid)
            target.add_cards(buy[0], self.client.panes['shop'].rect.topleft)

        log = next((log for log in val if log['type'] == 'cast'), None)
        
        if log:
            
            for p in self.client.get_panes('landscape'):

                p.uids[log['card'][1]] = self.color
            
        log = next((log for log in val if log['type'] == 'play'), None)
        
        if log and self != self.client.main_p:
            
            self.client.panes['active card'].uids[log['card'][1]] = self.color
            
    def get_target(self):
        return client.targets.get(self.pid)
     
class Card:
    def __init__(self, name, uid=None):
        self.name = name
        
        self.uid = uid if uid is not None else id(self)
        
        self.rect = pg.Rect(0, 0, cw, ch)
        
        self.rel_pos = [0, 0]
        
        self.color = None
        
        if not spritesheet.check_name(self.name):
            
            w, h = self.get_image().get_size()
            
            self.rect = pg.Rect(0, 0, w, h)
        
    def set_rel_pos(self, pos):
        self.rel_pos = pos
        
    def copy(self):
        return type(self)(self.name, self.uid)
        
    def __eq__(self, other):
        return self.uid == other.uid
        
    def __repr__(self):
        return self.name
        
    def get_image(self, mini=True):
        return spritesheet.get_image(self.name, mini)
        
    def update(self, name, uid):
        self.name = name
        self.uid = uid
        
    def adjust_pos(self, rect):
        self.rect.x = rect.x + self.rel_pos[0]
        self.rect.y = rect.y + self.rel_pos[1]
        
class Client:
    def __init__(self, screen, connection):
        self.screen = screen
        pg.display.set_caption('test')
        
        self.frame = pg.Surface((width, height)).convert()
        
        self.clock = pg.time.Clock()
        self.mouse = pg.Rect(0, 0, 1, 1)
        
        self.n = connection #if no game is sent, we need network to connect to game, otherwise use game as network
        self.playing = True
        
        self.pid = int(self.n.get_pid())
        self.name = 'player {}'.format(self.pid)
        self.players = [Player(self, self.pid)]
        
        self.main_p = self.players[0]
        
        self.event = None
        self.view_card = None
        
        self.status = self.send('status')

        self.flipping = False
        self.rolling = False
        
        self.cards = [] #visible cards
        self.lines = [] #visible lines (used to show 
        self.moving_cards = []
        self.particles = []

        self.loop_times = []
        
        self.turnid = TurnIndicator(self, Textbox('->', 20))
        self.turnid.reset()
        self.coin = Coin(self, 50)
        self.dice = Dice(self, 50)

        self.new_game()
        
        self.run()
        
    def set_screen(self):
        self.panes = {}
        self.text = {}
        self.coins = {}
        self.dices = {}
        self.targets = {}

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
        
        text = Textbox('play', 50)
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
        
        text = Textbox('', 20, tcolor=(0, 255, 0))
        text.rect.centerx = self.text['options'].rect.centerx
        text.rect.y += 60
        self.text['status'] = text
        
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

        for t in self.coin.text + self.dice.text:
        
            t.rect.bottomright = self.panes['active card'].rect.bottomleft
            t.rect.x -= 20

    def add_panes(self):
        left = self.panes['card area'].rect.right
        right = self.panes['selection area'].rect.left
        step = (right - left) // len(self.players) 

        for i, x in zip(range(len(self.players)), range(left + step // 2, right + step, step)):    
            
            p = self.players[i]

            pane = Pane(pg.Rect(x, 40, cw * 1.5, ph * 1.5), '', tsize=20, layer=len(self.players) - i, color=(0, 0, 0), tcolor=p.color)
            self.panes['spot {}'.format(i)] = pane

            pane = Slider(pg.Rect(x, 40, cw * 1.5, ph), '', tsize=20, layer=(len(self.players) - i) + 1, dir='x', tcolor=p.color)
            self.panes['items {}'.format(i)] = pane
            
            pane = Slider(pg.Rect(x, 40, cw * 1.5, ph), '', tsize=20, layer=(len(self.players) - i) + 1, dir='-x', tcolor=p.color)
            self.panes['landscape {}'.format(i)] = pane
            
            tr = self.panes['spot {}'.format(i)].rect.topright
            
            coin = Coin(self)
            coin.move_text((tr[0], tr[1] - coin.text[0].rect.height))
            coin.adjust_x(15)
            self.coins[i] = coin
            
            dice = Dice(self)
            dice.move_text((tr[0], tr[1] - dice.text[0].rect.height))
            dice.adjust_x(15)
            self.dices[i] = dice
            
            target = Target(self)
            target.rect.bottomleft = self.panes['spot {}'.format(i)].rect.topright
            target.rect.x += 5
            self.targets[i] = target
            
        y = 0
        
        for i, p in enumerate(self.players):

            text = Textbox('{}: {}'.format(p.name, p.score))
            text.rect.topleft = (0, y)
            self.text['score {}'.format(i)] = text
            
            y += text.rect.height
            
    def update_panes(self):
        self.cards.clear()
        
        for i, p in enumerate(self.players):

            pane = self.panes['spot {}'.format(i)]  
            pane.update_text(p.name, p.color)
            cards = [c.copy() for c in p.played]
            self.cards += pane.add_cards(cards)
            
            target = self.targets[p.pid]
            tl = target.rect.topleft
            target.rect.topleft = pane.textbox.rect.topright
            target.rect.x += 5
            if target.rect.topleft != tl:
                target.adjust_course()
            
            if p.is_turn:
                
                self.turnid.set_pos(pane.textbox.rect)
            
            pane = self.panes['last used item'] 
            if p.used_item:
                cards = [p.used_item]
                self.cards += pane.add_cards(cards)
            else:
                self.cards += pane.cards
            
            pane = self.panes['items {}'.format(i)]
            cards = []
            if p.active_card:
                cards.append(p.active_card.copy())
            #if p.used_items:
            #    cards.append(p.used_items[-1].copy())
            self.cards += pane.add_cards(cards)
            
            if p.landscape is not None:
            
                pane = self.panes['landscape {}'.format(i)]
                cards = [p.landscape] + [c.copy() for c in p.ongoing]
                if self.status not in ('waiting', 'playing'):
                    cards += p.treasure
                self.cards += pane.add_cards(cards)
                
            else:
                
                self.panes['landscape {}'.format(i)].cards.clear()

            if p == self.main_p:
                
                self.cards += self.panes['card area'].add_cards(p.unplayed)
                self.cards += self.panes['extra cards'].add_rows({(255, 0, 0): p.items + p.equipped, (255, 0, 255): p.spells, (255, 255, 0): p.treasure})
                self.cards += self.panes['selection area'].add_cards(p.selection)

                self.cards += self.panes['active card'].add_cards([p.active_card] if p.active_card is not None else [])
 
        y = 0
                
        players = sorted(self.players, key=lambda p: p.score, reverse=True)
        
        for i, p in enumerate(players):
        
            text = self.text['score {}'.format(i)]
            text.update_text('{}: {}'.format(p.name, p.score))
            text.rect.topleft = (0, y)
            y += text.rect.height
            
        pane = self.panes['event']
        pane.cards.clear()
        self.cards += pane.add_cards([self.event] if self.event is not None else [])
        
        pane = self.panes['shop']
        info = self.send('shop')
        if info != 'w':
            cards = [Card(name, uid) for name, uid in info]
            if cards:
                self.cards += pane.add_cards(cards, dir='x')
            else:
                self.cards += pane.cards

    def new_game(self):
        self.cards.clear()

        self.turnid.reset()
        
        self.set_screen()
        
        for p in self.panes.values():
            
            p.reset()

    def quit(self):
        self.n.close()
        self.playing = False
        pg.quit()
        sys.exit()
        
    def exit(self):
        self.n.close()
        
        self.playing = False       
     
#main loop-----------------------------------------------------------------------------
            
    def run(self):
        self.set_name()
        
        while self.playing:
        
            self.clock.tick(30)
            
            self.events()
            
            self.update()

            self.draw()
            
    def events(self):
        self.mouse.topleft = pg.mouse.get_pos()

        for e in pg.event.get():
            
            if e.type == pg.QUIT:
                self.quit() 
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                    self.quit()
                    
                elif e.key == pg.K_p:
                    
                    self.send('play')
                        
                elif e.key == pg.K_x:
                    
                    self.send('cancel')
                    
                elif e.key == pg.K_s and self.pid == 0:
                    
                    self.send('start')
                    
                    self.new_game()
                    
                elif e.key == pg.K_LALT:

                    for c in self.cards:
                        
                        if c.rect.colliderect(self.mouse):
                            
                            self.view_card = c
                            
                            break

            elif e.type == pg.KEYUP:
                    
                if e.key == pg.K_LALT:
                
                    self.view_card = None
                    
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                if self.mouse.colliderect(self.text['options'].rect):
                    
                    game_menu(self)
                    
                elif self.mouse.colliderect(self.text['status'].rect) and self.pid == 0:
                    
                    self.send('continue')

                if self.mouse.colliderect(self.text['play'].rect):
                    
                    self.send('play')
                    
                elif self.mouse.colliderect(self.coin.text[-1].rect) and self.main_p.flipping:
                    
                    self.send('flip')
                    
                elif self.mouse.colliderect(self.dice.text[-1].rect) and self.main_p.rolling:
                    
                    self.send('roll')
                    
                else:
                    
                    for c in self.cards:
                        
                        if self.mouse.colliderect(c.rect):

                            self.send(str(c.uid))
                            
                            break
                            
                    else:
                        
                        self.send('select')
                        
                for p in self.panes.values():
                    
                    if hasattr(p, 'click'):
                        
                        if p.rect.colliderect(self.mouse):
                            
                            p.click()
                            
                            break
                        
        for pane in self.panes.values():
            
            if hasattr(pane, 'hit'):
                
                pane.hit(self.mouse)
                        
    def update(self):  
        self.status = self.send('status')
        
        self.update_players()
        
        e = self.send('event')
        
        if e and e != 'w':
            
            self.event = Card(e)
        
        if self.pid == 0:
            
            self.check_status()
            
        if self.status not in ('playing', 'waiting'):
            
            w = self.send('winner')
            
            if w != 'w' and w is not False:

                self.win_screen(w)
                
        else:
            
            self.text['winner'].update_text('')
        
        for pane in self.panes.values():
            
            if hasattr(pane, 'update'):
                
                if pane.check_mode():
                
                    pane.update()

        for c in self.cards:
            
            if c.rect.colliderect(self.mouse):
            
                s = c.rect.center
                
                other = self.find_card(c)
                
                if other:
                
                    e = other.rect.center
                    self.lines.append((s, e))
                    
                break
                
        for c in self.main_p.equipped:
        
            c = self.find_local_card(c)
            
            if c is not None:
                
                self.add_particles(c.rect, 2, (255, 0, 0))

        for p in self.particles.copy():
            
            if not p.update():
                
                self.particles.remove(p)
                        
        self.update_panes()

        for target in self.targets.values():
            
            target.update()
        
    def draw(self):
        self.frame.fill((0, 0, 0))

        self.draw_panes(self.frame)

        self.frame.blit(self.turnid.get_image(), self.turnid.rect)
 
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

        for i, p in enumerate(self.players):
            
            if p == self.main_p:
                
                if p.coin is not None and p.flipping:
                    
                    text = self.coin.text[p.coin]
        
                    self.frame.blit(text.get_image(), text.rect)
                    
                elif p.dice is not None and p.rolling:
                    
                    text = self.dice.text[-1] if p.dice == -1 else self.dice.text[p.dice - 1]
                    
                    self.frame.blit(text.get_image(), text.rect)
                    
            else:
                
                if p.coin is not None and p.flipping:
                    
                    text = self.coins[i].text[p.coin]
                    
                    self.frame.blit(text.get_image(), text.rect)
                    
                elif p.dice is not None and p.rolling:
                    
                    text = self.dices[i].text[-1] if p.dice == -1 else self.dices[i].text[p.dice - 1]
                    
                    self.frame.blit(text.get_image(), text.rect)
                    
        for c in self.moving_cards:
            
            self.frame.blit(c.get_image(), c.rect)
            
        if self.view_card:
        
            self.frame.blit(self.view_card.get_image(False), self.view_card_rect)

        for p in self.particles:
            
            pg.draw.circle(self.frame, p.color, p.pos, p.r)

        self.screen.blit(self.frame, (0, 0))

        pg.display.flip()
        
#-------------------------------------------------------------------------------------------
        
    def draw_panes(self, frame):
        for i in range(len(self.players)):   

            self.panes['landscape {}'.format(i)].draw(frame)
            self.panes['items {}'.format(i)].draw(frame)
            self.panes['spot {}'.format(i)].draw(frame)

        self.panes['card area'].draw(frame)
        self.panes['selection area'].draw(frame)
        self.panes['active card'].draw(frame)
        self.panes['extra cards'].draw(frame)
        self.panes['event'].draw(frame)
        self.panes['active card'].draw(frame)
        self.panes['last used item'].draw(frame)
        self.panes['shop'].draw(frame)
        
    def update_players(self):
        global info
        global light_info
        
        self.send('update')
        
        pids, names = self.send('players')
        
        for pid, name in zip(pids, names):

            if not any(p.pid == pid for p in self.players):
                
                self.add_player(pid, name)
                
            else:
                
                p = self.get_player_by_pid(pid)
                
                if p.name != name:
                    
                    p.name = name

        for p in self.players.copy():
            
            if p.pid not in pids:
                
                self.remove_player(p)
                
        self.players.sort(key=lambda p: pids.index(p.pid))
        
        for p in self.players:
            
            if p.pid == self.pid:
                
                p.get_info(info)
                
            else:
            
                p.get_info(light_info)
                
            p.card.update_text('player {}: {}'.format(p.pid, p.score))

    def add_player(self, pid, name):
        p = Player(self, pid)
        p.name = name
        
        self.players.append(p)
        
        self.players.sort(key=lambda p: p.pid)
        
        self.add_panes()
        
        return p
        
    def get_player_by_pid(self, pid):
        return next((p for p in self.players if p.pid == pid), None)
        
    def remove_player(self, p):
        self.players.remove(p)
        
        self.set_screen()
   
    def update_settings(self, settings):
        for key, val in settings.items():
            
            reply = self.send('~{},{}'.format(key, val))
            
        return reply
        
    def find_local_card(self, card):
        for c in self.panes['extra cards'].cards:
            
            if c == card:
                
                return c
        
    def find_card(self, other):
        cards = []
        
        pos = (0, 0)
        
        for p in self.players:
            
            cards += self.panes['spot {}'.format(p.pid)].cards
            cards += self.panes['landscape {}'.format(p.pid)].cards
            
        c = next((c for c in cards if c.uid == other.uid and c is not other and spritesheet.check_name(c.name) and c.rect.topleft != pos), None)
            
        return c
                
    def find_uid(self, uid):
        for c in self.cards:
            
            if uid == c.uid and spritesheet.check_name(c.name):
                
                return c
                
    def unpack_points(self, pid, points):
        for pack in points:

            uid = pack[-1]
            type = pack[0]
            points = pack[1] if type in ('gp', 'sp') else -pack[1]
            
            if type == 'sp':
                
                target = pack[2]
                
                s = self.get_spot(target).rect.topleft
                
                self.targets[pid].add_points(points, s)
                
            elif type == 'give':
                
                target = pack[2]
                
                s = self.get_spot(pid).rect.topleft
                
                self.targets[target].add_points(points, s)
                
            elif type == 'gp' or type == 'lp':
                
                card = self.find_uid(uid)
                
                if card:
                    
                    s = card.rect.center
                    
                else:
                    
                    s = self.targets[pid].rect.center
                    
                self.targets[pid].add_points(points, s)
            
    def get_spot(self, pid):
        return self.panes['spot {}'.format(self.players.index(next((p for p in self.players if pid == p.pid))))]
        
    def get_target(self, pid):
        return self.targets[pid]
  
    def check_status(self):
        text = self.text['status']
        text.update_text(self.status)
        
    def win_screen(self, pid):
        p = self.get_player_by_pid(pid)
        text = self.text['winner']
        text.update_text('{} wins!'.format(p.name), tcolor=p.color)
        
        self.add_particles(text.rect, 50, self.get_player_by_pid(pid).color)
        
    def set_name(self):
        name = name_entry(self.pid)
        
        if not name:
            
            self.exit()
            
            return
            
        else:
            
            self.name = name
            self.main_p.name = name
            self.send('name,{}'.format(name))
        
    def get_panes(self, name):
        panes = []
        
        for key in self.panes:
            
            if name in key:
                
                panes.append(self.panes[key])
                
        return panes
        
    def send(self, data):
        if self.playing:
        
            reply = self.n.send(data)
            
            if reply is None:
                
                self.playing = False
                
            else:
                
                return reply
            
    def add_particles(self, rect, num, color=(255, 255, 0)):
        for _ in range(num):
            
            self.particles.append(Particle(rect, color))
        
main()


















     
#try:
#        
#    c = Client(win)
#    
#except Exception as e:
#    
#    print(e)
#    
#    print('could not find server')
    
pg.quit()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        