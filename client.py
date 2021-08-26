import pygame as pg
import time, sys, subprocess, random, socket
import urllib.request
from colorsys import hsv_to_rgb
from ui import *
from constants import *
from particles import *
from builder import *
from network import Network, InvalidIP, NoGamesFound
from spritesheet import Spritesheet
from game import Game
from save import *

#---------------------------------------------------------------------------------------------------------------

def exit():
    pg.quit()
    sys.exit()

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())
    
def get_public_ip():
    ip = 'no internet connection'
    
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode()
    except urllib.error.URLError:
        pass
        
    return ip

def gen_colors(num):
    golden = (1 + 5 ** 0.5) / 2
    colors = []
    
    for i in range(num):
        
        h = (i * (golden - 1)) % 1
        r, g, b = hsv_to_rgb(h, 0.8, 1)
        rgb = (r * 255, g * 255, b * 255)
        colors.append(rgb)

    return colors

#screen stuff----------------------------------------------------------------------

def new_screen(text, wait=0):
    global win
    
    win.fill((0, 0, 0))

    for t in text:
        
        win.blit(t.get_image(), t.rect)
        
    pg.display.update()
    
    if wait:
    
        pg.time.wait(wait)
        
def new_message(message, wait=0):
    global win
    
    win.fill((0, 0, 0))
    m = Textbox(message, 20)
    m.rect.center = (width / 2, height / 2)
        
    win.blit(m.get_image(), m.rect)
    pg.display.update()
    
    if wait:
    
        pg.time.wait(wait)
        
    pg.event.clear()

def outline_buttons(mouse, btns, olc=(255, 0, 0)):
    hit = False
    
    for b in btns:
        
        if hasattr(b, 'add_outline'):
        
            if mouse.colliderect(b.rect) and not hit:
                
                b.add_outline(olc)
                hit = True
                
            else:
                
                b.add_outline()

def center_buttons_y(btns):
    h = max(b.rect.bottom for b in btns) - min(b.rect.top for b in btns)
    r = pg.Rect(0, 0, 2, h)
    r.centery = height // 2

    dy = r.y - min(b.rect.top for b in btns)
    
    for b in btns:
        
        b.rect = b.rect.move(0, dy)
        
def center_buttons_x(btns):
    w = max(b.rect.right for b in btns) - min(b.rect.left for b in btns)
    r = pg.Rect(0, 0, w, 2)
    r.centerx = width // 2

    dx = r.x - min(b.rect.left for b in btns)
    
    for b in btns:
        
        b.rect = b.rect.move(dx, 0)
        
    return r

#menu mechanics------------------------------------------------------------------------

def mini_loop(elements, input=[]):
    global win

    for e in elements:

        is_button = isinstance(e, Button)
    
        if hasattr(e, 'events'):
            e.events(input)
                
        if isinstance(e, Button):
            if e.get_state():
                break
                
    for e in elements:
            
        if hasattr(e, 'update'):
            e.update()
            
    win.fill((0, 0, 0))
            
    for e in elements:
        
        if hasattr(e, 'draw'):
            e.draw(win)

    pg.display.flip()
    
def check_break(elements):
    for e in elements:
        
        if isinstance(e, Button):
            
            if e.get_tag() == 'break':
                
                if e.get_state():
                    
                    return True
                
    return False

def get_return(elements):
    for e in elements:
    
        if isinstance(e, Button):
            
            if e.get_tag() == 'return':
                
                return e.get_return()

def check_refresh(elements, mode, args):
    for e in elements:
    
        if isinstance(e, Button):
            
            if e.get_tag() == 'refresh':
                
                if e.get_state():

                    return (set_screen(mode, args=args), True)
                
    return (elements, False)

def menu(mode='', args=[]):
    global win
    
    elements = set_screen(mode, args=args)
    skip = False
    input = []
    
    while True:
        clock.tick(30)
        p = pg.mouse.get_pos()
        
        input = pg.event.get()
        
        for e in input:
               
            if e.type == pg.QUIT:
                exit()
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                    exit()
                    
        for e in elements:
            
            is_button = isinstance(e, Button)
            if is_button:
                if e.get_state():
                    e.reset()
                    
            if hasattr(e, 'events'):
                e.events(input)
                
            if is_button:
                if e.get_state():
                    break
                    
        elements, skip = check_refresh(elements, mode, args)
        
        if not skip:
            if check_break(elements):
                break
            skip = False

        r = get_return(elements)
        if r is not None:
            return r
                    
        for e in elements:
            if hasattr(e, 'update'):
                e.update()
                
        win.fill((0, 0, 0))
                
        for e in elements:
            if hasattr(e, 'draw'):
                e.draw(win)
                
        pg.display.flip()

#button functions------------------------------------------------------------------

def run_builder():
    b = Builder(win)  
    b.run()
    b.close()

def save_game_settings(client, counters):
    settings = {c.tag: c.get_current_option() for c in counters}  
    set_data('settings', settings)
    client.update_settings()

def save_user_settings(username_field, port_field):
    username = username_field.get_message()
    port = int(port_field.get_message())
    
    set_username(username)
    
    if port > 1023:

        if port <= 65535:
        
            set_port(port)
            new_message('changes saved', 1500)
            
            return
            
        else:
            
            new_message('port value is too high', 2000)
            
    else:
        
        new_message('port value too small', 2000)
 
def join_game(ip, field):
    port = int(field.get_message())
    connect(ip, port)

def new_entry(name_field, ip_field):
    name = name_field.get_message()
    ip = ip_field.get_message()

    update_ips({'name': name, 'ip': ip})

#menu stuff------------------------------------------------------------------------

def set_screen(mode, args=[], wait=0):
    screen = []
    
    if mode == 'main':
    
        btn = Button((200, 30), 'single player', (0, 0, 0), (100, 100, 100), func=single_player)
        btn.rect.center = (width // 2, height // 2)
        btn.rect.midbottom = btn.rect.midtop
        screen.append(btn)
        
        btn = Button((200, 30), 'host game', (0, 0, 0), (100, 100, 100), func=start_game)
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'find online game', (0, 0, 0), (100, 100, 100), func=menu, kwargs={'mode': 'choose host'})
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'find local game', (0, 0, 0), (100, 100, 100), func=connect, args=['', get_data('port')])
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'card builder', (0, 0, 0), (100, 100, 100), func=run_builder)
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'settings', (0, 0, 0), (100, 100, 100), func=menu, kwargs={'mode': 'user settings'})
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        center_buttons_y(screen)
        
    elif mode == 'user settings':
        
        text = Textbox('display name:  ', 20, tcolor=gen_colors(1)[0])
        text.rect.right = width // 2
        text.rect.bottom = height // 2
        text.rect.midbottom = text.rect.midtop
        screen.append(text)
        
        text = Input((200, 30), get_data('username'), color=(0, 0, 0), tcolor=(255, 255, 255), length=12)
        text.rect.midleft = screen[-1].rect.midright
        screen.append(text)
        
        text = Textbox('default port:  ', 20)
        text.rect.right = width // 2
        text.rect.y = screen[-1].rect.bottom + 5
        screen.append(text)
        
        text = Input((200, 30), str(get_data('port')), color=(0, 0, 0), tcolor=(255, 255, 255), 
                                                       check=lambda char: char.isnumeric())
        text.rect.midleft = screen[-1].rect.midright
        screen.append(text)

        btn = Button((200, 30), 'edit profile card', func=run_builder)
        btn.rect.centerx = width // 2
        btn.rect.y = screen[-1].rect.bottom + btn.rect.height
        screen.append(btn)
        
        b = Button((200, 30), 'reset save data', func=refresh_save, tag='refresh')
        b.rect.midtop = screen[-1].rect.midbottom
        b.rect.y += 5
        screen.append(b)
        
        btn = Button((200, 30), 'save', (0, 0, 0), (100, 100, 100), func=save_user_settings, 
                                                   args=[screen[1], screen[3]], tag='break')
        btn.rect.centerx = width // 2
        btn.rect.y = screen[-1].rect.bottom + btn.rect.height
        screen.append(btn)
        
        btn = Button((200, 30), 'cancel', (0, 0, 0), (100, 100, 100), tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        screen.append(btn)

    elif mode == 'choose host':
    
        y = 0

        for entry in get_data('ips'):

            btn = Button((200, 30), entry['name'] + ': ' + entry['ip'], (0, 0, 0), (100, 100, 100), func=menu,
                            kwargs={'mode': 'join game', 'args': [entry['name'], entry['ip']]}, tag='refresh')
            btn.rect.centerx = width // 2
            btn.rect.y = y
            screen.append(btn)
            
            y += btn.rect.height + 5
            
        if screen:  
            center_buttons_y(screen)

        btn = Button((200, 30), 'new entry', (0, 0, 0), (100, 100, 100), func=menu,
                                       kwargs={'mode': 'new entry'}, tag='refresh')
        if screen:
            btn.rect.midtop = screen[-1].rect.midbottom   
        else:
            btn.rect.midbottom = (width // 2, height // 2) 
        btn.rect.y += 20
        screen.append(btn)
        
        btn = Button((200, 30), 'view my ip', (0, 0, 0), (100, 100, 100), func=menu, kwargs={'mode': 'view ip'})
        btn.rect.midtop = screen[-1].rect.midbottom
        screen.append(btn)
            
        btn = Button((200, 30), 'back', (0, 0, 0), (100, 100, 100), tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += btn.rect.height
        screen.append(btn)

        center_buttons_y(screen)
  
    elif mode == 'view ip':
        
        public_ip = get_public_ip()
        local_ip = get_local_ip()

        text = Textbox(f'your online IP:  {public_ip}', 20)
        text.rect.midbottom = (width // 2, height // 2)
        screen.append(text)
        
        btn = Button((200, 30), 'copy online IP to clipboard', tcolor=(255, 255, 0))
        btn.set_func(copy_to_clipboard, args=[public_ip])
        btn.set_timer_rule(125, 'coppied')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        text = Textbox(f'your local IP: {local_ip}', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 5
        screen.append(text)
        
        btn = Button((200, 30), 'copy local IP to clipboard', tcolor=(255, 255, 0))
        btn.set_func(copy_to_clipboard, args=[local_ip])
        btn.set_timer_rule(125, 'coppied')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'back', tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += btn.rect.height
        screen.append(btn)
        
        center_buttons_y(screen)

    elif mode == 'new entry':
        
        text = Textbox('entry name: ', 20)
        text.rect.midright = (width // 2, height // 2)
        text.rect.midbottom = text.rect.midtop
        screen.append(text)
        
        input = Input((100, 20), 'name')
        input.rect.midleft = screen[-1].rect.midright 
        screen.append(input)
        
        center_buttons_x(screen[-2:])
        
        text = Textbox('entry IP: ', 20)
        text.rect.topright = screen[-2].rect.bottomright
        text.rect.y += 20
        screen.append(text)
        
        input = Input((100, 20), '255.255.255.255', check=lambda txt: txt.isnumeric() or txt == '.')
        input.rect.midleft = screen[-1].rect.midright      
        screen.append(input)
        
        center_buttons_x(screen[-2:])
        
        btn = Button((200, 30), 'save', (0, 0, 0), (100, 100, 100), func=new_entry,
                                              args=[screen[1], screen[3]], tag='break')
        btn.rect.centerx = width // 2
        btn.rect.y = screen[-1].rect.bottom + (btn.rect.height * 2)
        screen.append(btn)
        
        btn = Button((200, 30), 'cancel', (0, 0, 0), (100, 100, 100), tag='break')
        btn.rect.centerx = width // 2
        btn.rect.y = screen[-1].rect.bottom + 5
        screen.append(btn)

    elif mode == 'join game':
        
        name, ip = args
        
        text = Textbox('name: ' + name, 20)
        text.rect.center = (width // 2, height // 2)
        screen.append(text)

        text = Textbox('ip: ' + ip, 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 5
        screen.append(text)
        
        text = Textbox('port: ', 20)
        text.rect.top = screen[-1].rect.bottom
        text.rect.y += 5
        text.rect.right = width // 2
        screen.append(text)
        
        input = Input((100, 20), str(get_data('port')))
        input.rect.midleft = screen[-1].rect.midright
        screen.append(input)
        
        center_buttons_x(screen[-2:])

        btn = Button((200, 30), 'join game', (0, 0, 0), (0, 255, 0), func=join_game, args=[ip, screen[-1]])
        btn.rect.top = screen[-1].rect.bottom
        btn.rect.y += btn.rect.height
        btn.rect.centerx = width // 2
        screen.append(btn)
        
        btn = Button((200, 30), 'delete', (0, 0, 0), (255, 0, 0), func=del_ips, args=[name, ip], tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        btn = Button((200, 30), 'back', (0, 0, 0), (255, 0, 0), tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        btn.rect.y += 5
        screen.append(btn)
        
        center_buttons_y(screen)
     
    elif mode == 'game options':
        
        client = args[0]
        
        btn = Button((200, 30), 'disconnect', tag='break', func=client.disconnect)
        btn.rect.midtop = (width // 2, height // 2)
        screen.append(btn)
        
        btn = Button((200, 30), 'game settings', func=menu, kwargs={'mode': 'game settings', 
                                                                    'args': [client]})
        btn.rect.midtop = screen[-1].rect.midbottom
        screen.append(btn)
        
        if client.is_host():

            btn = Button((200, 30), 'new game', tag='break', func=client.send, args=['reset'])
            btn.rect.midtop = screen[-1].rect.midbottom
            screen.append(btn)
            
        btn = Button((200, 30), 'back', tag='break')
        btn.rect.midtop = screen[-1].rect.midbottom
        screen.append(btn)
        
        center_buttons_y(screen)
        
    elif mode == 'game settings':
        
        client = args[0]
        settings = client.get_settings()
        
        if client.is_host():
        
            sep = 15
            off = 3
            
            t = Textbox('rounds: ', tsize=20)
            t.rect.centerx = width // 2
            screen.append(t)
            
            c = Counter(range(1, 6), option=settings['rounds'], tsize=30, tag='rounds')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('starting score: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(5, 51), option=settings['ss'], tsize=30, tag='ss')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('starting cards: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(1, 11), option=settings['cards'], tsize=30, tag='cards')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('starting items: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(0, 6), option=settings['items'], tsize=30, tag='items')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('starting spells: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(0, 4), option=settings['spells'], tsize=30, tag='spells')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('number of cpus: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(1, 15), option=settings['cpus'], tsize=30, tag='cpus')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])

            t = Textbox('cpu difficulty: ', tsize=20)
            t.rect.centerx = width // 2
            t.rect.y = screen[-1].rect.bottom + sep
            screen.append(t)
            
            c = Counter(range(0, 5), option=settings['diff'], tsize=30, tag='diff')
            c.rect.bottomleft = screen[-1].rect.bottomright
            c.rect.y += off
            screen.append(c)
            
            center_buttons_x(screen[-2:])
            
            counters = [c for c in screen if isinstance(c, Counter)]
            
            b = Button((200, 30), 'save', func=save_game_settings, args=[client, counters], tag='break')
            b.rect.midtop = screen[-1].rect.midbottom
            b.rect.y += b.rect.height
            b.rect.centerx = width // 2
            screen.append(b)
                
            b = Button((200, 30), 'back', tag='break')
            b.rect.midtop = screen[-1].rect.midbottom
            b.rect.centerx = width // 2
            screen.append(b)
            
            center_buttons_y(screen)
            
        else:
            
            t = Textbox(f"rounds: {settings['rounds']}", tsize=20)
            t.rect.centerx = width // 2
            screen.append(t)
            
            t = Textbox(f"starting score: {settings['ss']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            t = Textbox(f"starting cards: {settings['cards']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            t = Textbox(f"starting items: {settings['items']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            t = Textbox(f"starting spells: {settings['spells']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            t = Textbox(f"number of cpus: {settings['cpus']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            t = Textbox(f"cpu difficulty: {settings['diff']}", tsize=20)
            t.rect.midtop = screen[-1].rect.midbottom
            t.rect.y += 5
            screen.append(t)
            
            b = Button((200, 30), 'cancel', tag='break')
            b.rect.midtop = screen[-1].rect.midbottom
            b.rect.y += b.rect.height
            b.rect.centerx = width // 2
            screen.append(b)
            
            center_buttons_y(screen)

    return screen

#new game stuff-------------------------------------------------------------------------

def connect(ip, port):
    new_message('searching for game...', 500)

    try:       
        net = Network(ip, port)
        c = Client(win, net, 'online') 
        c.run()
        
    except InvalidIP:
        new_message('invalid IP address', 2000) 
        
    except NoGamesFound:  
        new_message('no games could be found', 2000)
        
    except EOFError as e:
        print(e)
        new_message('disconnecting...', 1000)  
        
    except Exception as e: 
        print(e, 'c1')
        new_message('an error occurred', 2000)
        
    finally:
        if 'c' in locals():
            c.exit()
        
def start_game():
    new_message('starting game...', 500)

    try:
        subprocess.Popen([sys.executable, 'server.py'])
        net = Network(get_local_ip(), get_data('port'))
        c = Client(win, net, 'online')
        c.run()
        
    except EOFError as e:
        print(e)
        new_message('diconnected', 1000)
        
    except NoGamesFound:
        new_message('game could not be started', 2000)
        
    #except Exception as e:
    #    print(e, 'c2')
    #    new_message('an error occurred', 2000)
        
    finally:
        if 'c' in locals():
            c.exit()
        
def single_player():
    new_message('starting game...', 500)

    g = Game('single')
    c = Client(win, g, 'single')
    c.run()
    
    new_message('returning to main menu...', 1000)

#-----------------------------------------------------------------------------------

def sort_logs(log):
    u = log.get('u')
    
    if u == 'g':
        return -1
    else:
        return u

class Player:
    def __init__(self, client, pid, name=None):
        self.client = client
        
        self.pid = pid
        self.name = name if name is not None else f'Player {pid}'
        self.color = self.client.colors[pid]
        
        self.target = pg.Rect(0, 0, 20, 20)
        self.view_card_rect = pg.Rect(0, 0, card_width // 2, card_height // 2)
        self.card_rect = pg.Rect(0, 0, cw, ch)

        self.score = -1
        self.score_card = Textbox('', tsize=20, tcolor=self.color)
        self.update_score(0)
        
        self.coin = None
        self.dice = None
        self.timer = 0
        self.frt = 0
        
        self.flipping = False
        self.rolling = False
        self.is_turn = False
        self.can_cancel = False

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
        self.landscapes = []
        self.used_item = None
        
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    def is_host(self):
        return self.pid == 0
        
    def update_score(self, score):
        if self.score != score:
            self.score = score
            self.score_card.update_message(f'{self.name}: {self.score}')
            self.score_card.fit_text(pg.Rect(0, 0, self.client.elements['scores'].rect.width, self.score_card.rect.height))
            return True
            
        return False
 
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
        self.update_score(0)

        self.coin = None
        self.dice = None
        
        self.flipping = False
        self.rolling = False
        self.is_turn = False
        self.can_cancel = False
        
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
        self.landscapes.clear()
        self.used_item = None
        
    def new_round(self):
        self.played.clear()
        self.unplayed.clear()
        self.selection.clear()
        self.ongoing.clear()
        self.landscapes.clear()
        self.active_card = None
        
    def get_cards(self):
        return [self.played, self.unplayed, self.items, self.selection, self.selected, self.equipped, self.ongoing, self.treasure, self.spells, self.landscapes]

    def get_spot(self):
        return self.client.get_spot(self.pid)

    def play(self, uid):
        for c in self.unplayed:

            if c.uid == uid:
                
                self.unplayed.remove(c)
                self.client.add_moving_card(self, original=c)
                self.played.append(c)
                
                break
         
    def new_deck(self, deck, cards):
        cards = [Card(name, uid) for name, uid in cards]
        
        #if deck == 'treasure':
        #    
        #    if len(cards) > len(self.treasure):
        #        
        #        r = self.get_spot().rect
        #        self.client.add_particles(r, 100)

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
         
    def use_item(self, uid, name):
        for c in self.items:
            
            if c.uid == uid:
                
                self.items.remove(c)

                break
 
        c = Card(name, uid)
        c.color = self.color
        self.client.last_item = c
        
        self.client.add_moving_card(self, c)
 
    def cast(self, card, target):
        for c in self.spells:
            
            if c == card:

                self.spells.remove(c)

                break
                
        self.client.add_moving_card(self, card)
                
        card.color = self.color        
        target.ongoing.append(card)
          
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

    def update_name(self, name):
        self.name = name

    def new_ac(self, c, wait, cancel):
        self.active_card = c
        
        if wait == 'flip':
            self.coin = -1 
        elif wait == 'roll':
            self.dice = -1
            
        self.can_cancel = cancel
        
    def remove_ac(self):
        self.active_card = None
        self.coin = None
        self.dice = None
        self.can_cancel = False
 
    def start_flip(self):
        self.flipping = True
        
    def end_flip(self, coin, timer):
        self.flipping = False
        
        self.coin = coin
        
        self.timer = timer
    
    def start_roll(self):
        self.rolling = True
        
    def end_roll(self, dice, timer):
        self.rolling = False
        
        self.dice = dice - 1
        
        self.timer = timer

    def draw(self, deck, num):
        #for _ in range(num):
        #    
        #    self.client.add_moving_card(self, type='back')
        pass

class Card(Mover):
    def __init__(self, name, uid=None, color=None):
        self.name = name
        self.uid = uid if uid is not None else id(self)
        self.color = color
        self.rect = pg.Rect(0, 0, cw, ch)
        
        super().__init__()
 
    def __eq__(self, other):
        return self.uid == other.uid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def copy(self):
        c = Card(self.name, uid=self.uid, color=self.color)
        c.rect = self.rect.copy()
        return c
        
    def get_image(self, outline=False, scale=(cw, ch)):
        return spritesheet.get_image(self, outline, scale=scale)
        
    def update_info(self, name, uid):
        self.name = name
        self.uid = uid
        
    def update(self):
        self.move()

    def draw(self, win): 
        win.blit(self.get_image(), self.rect)

class PlayerSpot:
    def __init__(self, height, attrs):  
        self.player = None
        
        self.elements = []
        
        self.label = Textbox('', 20)
        self.elements.append(self.label)
        self.ongoing = Pane((cw, height))
        self.elements.append(self.ongoing)
        self.played = Pane((cw, height))
        self.elements.append(self.played)
        self.active_card = Pane((cw, ch + 5))
        self.elements.append(self.active_card)
        self.target = None
        self.view_card_rect = None
        self.card_rect = None
        
        w = self.ongoing.rect.width + 5 + self.played.rect.width + 5 + self.active_card.rect.width
        h = height
        
        self.rect = pg.Rect(0, 0, w, h)
        
        self.panes = (self.ongoing, self.played, self.active_card)
        
        for attr in attrs:
            setattr(self, attr, attrs[attr])
        
    def __str__(self):
        return self.player.name + ' spot'
        
    def __repr__(self):
        return self.player.name + ' spot'
        
    def get_target(self):
        return self.target
        
    def update_info(self, player):
        self.player = player
        self.label.update_all(message=self.player.name, tcolor=self.player.color)
        self.target = player.target
        self.view_card_rect = player.view_card_rect
        self.card_rect = player.card_rect
        
    def clear(self):
        for p in self.panes: 
            p.clear()
            
    def get_cards(self):
        cards = []
        
        for p in self.panes:
            
            cards += p.get_visible()
            
        return cards

    def add_cards(self, pane, cards):
        p = getattr(self, pane)
        p.join_objects(cards, scroll=True)

        return p.get_visible()
        
    def update_label(self, name):
        self.label.update_message(name)
        self.adjust_pos()
        
    def events(self, input):
        for e in self.elements:
            e.events(input)
            
    def update(self):
        if self.player.name != self.label.get_message():
            self.update_info(self.player)
            
        self.ongoing.rect.topleft = self.rect.topleft
        self.played.rect.topleft = self.ongoing.rect.topright
        self.played.rect.x += 5
        self.active_card.rect.topleft = self.played.rect.topright
        self.active_card.rect.x += 5
        self.label.rect.midbottom = self.played.rect.midtop
        self.target.midleft = self.label.rect.midright
        self.view_card_rect.midtop = self.label.rect.midbottom
        self.card_rect.midtop = self.view_card_rect.midtop
        
        for e in self.elements:
            e.update()
            
    def draw(self, win):
        for e in self.elements:
            e.draw(win)
            
        c = self.active_card.rect.center
            
        if self.player.coin is not None:
            
            img = self.coin[self.player.coin].get_image()
            r = img.get_rect()
            r.center = c
            win.blit(img, r)
            
        elif self.player.dice is not None:
        
            img = self.dice[self.player.dice].get_image()
            r = img.get_rect()
            r.center = c
            win.blit(img, r)
            
        elif self.player.selection:
            
            img = self.select.get_image()
            r = img.get_rect()
            r.center = c
            win.blit(img, r)
    
class Client:
    def __init__(self, screen, connection, mode):
        self.screen = screen
        self.mode = mode
        self.status = ''
        self.round = 1
        
        self.spritesheet = spritesheet

        self.frame = pg.Surface((width, height)).convert()
        self.camera = self.frame.get_rect()
        
        self.clock = pg.time.Clock()

        self.n = connection
        self.playing = True
        self.logs = {}
        self.log_queue = []

        self.pid = self.send('pid', threaded=False)
        self.colors = gen_colors(20)
        self.players = []
        
        self.settings = {}
        
        self.event = None
        self.view_card = None
        self.last_item = None

        self.outlined_card = None
        
        self.cards = []
        self.lines = []
        self.moving_cards = []
        self.effects = []
        self.particles = []
        self.shop = []

        self.loop_times = []

        self.targets = {}
        self.elements = {}
        self.player_spots = []
        self.points_queue = []
        self.points = []
        self.set_screen()
        self.panes = [p for p in self.elements if isinstance(p, Pane)]
        
        for pid in range(self.pid, -1, -1):
            self.add_player(pid)    
        self.main_p = self.get_main_p()
        
        self.set_name()
        
    def is_host(self):
        return self.pid == 0
   
    def get_main_p(self):
        for p in self.players:
            if p.pid == self.pid:
                return p

#screen stuff-----------------------------------------------------------------------------------
        
    def set_screen(self):
        ph = ch * 6

        pane = Pane((cw * 1.5, ph), label='your sequence', color=(255, 0, 0))
        pane.rect.bottomleft = (20, height - 20)
        self.elements['sequence'] = pane

        pane = Pane((cw * 1.5, (ch * 5) + 30), label='selection', color=(0, 0, 255))
        pane.rect.bottomright = (width - 20, height - 20)
        self.elements['selection'] = pane
        
        b = Button((20, 20), 'x', tcolor=(255, 0, 0), func=self.send, args=['cancel'], color2=(0, 0, 0))
        b.rect.center = (-50, -50)
        self.elements['cancel'] = b
        
        pane = Pane((cw * 1.5, ch * 1.5), label='active card', color=(255, 255, 255))
        pane.rect.bottomright = self.elements['selection'].rect.bottomleft
        pane.rect.x -= 10
        self.elements['active card'] = pane
        
        pane = Popup((cw * 10, ch * 4), label='extra cards', color=(0, 0, 0))
        pane.rect.x = self.elements['sequence'].rect.right + 10
        pane.rect.y = height
        pane.set_pos()
        self.elements['extra cards'] = pane
        
        b = Button((100, 50), '', tcolor=(0, 255, 0), func=self.main_button)
        b.disable()
        b.rect.midbottom = (width // 2, height)
        b.rect.y -= 10
        self.elements['main'] = b
        
        pane = Pane(((cw * 3) + 20, ch + 10), label='shop', color=(255, 255, 0))
        pane.rect.bottomright = self.elements['active card'].rect.bottomleft
        pane.rect.x -= 10
        self.elements['shop'] = pane

        self.view_card_rect = pg.Rect(0, 0, 375, 525)
        self.view_card_rect.center = (width // 2, height // 2)
        
        btn = Button((100, 30), 'options', func=menu, kwargs={'mode': 'game options', 'args': [self]})
        btn.rect.topright = (width, 0)
        btn.rect.y += 30
        btn.rect.x -= 30
        self.elements['options'] = btn
        
        text = Textbox('', 20, tcolor=(255, 255, 0))
        text.rect.midtop = self.elements['options'].rect.midbottom
        text.rect.y += 10
        self.elements['round'] = text
        #self.update_round()
        
        text = Textbox('', tsize=100, olcolor=(0, 0, 0), r=4)
        text.rect.center = (width // 2, height // 2)
        self.elements['winner'] = text

        pane = Pane((cw, ch * 1.5), label='item discard')
        pane.rect.midbottom = self.elements['selection'].rect.midtop
        pane.rect.y -= 30
        self.elements['last used item'] = pane
        
        pane = Pane((cw, ch * 1.5), label='event')
        pane.rect.centerx = self.elements['active card'].rect.centerx
        pane.rect.y = self.elements['last used item'].rect.y
        self.elements['event'] = pane
        
        pane = Pane((cw * 2, ch * 3), label='scores')
        pane.rect.topleft = (20, 40)
        self.elements['scores'] = pane
        
        self.coin = [Textbox('tails', 20, (255, 0, 0)), Textbox('heads', 20, (0, 255, 0)), Textbox('flip', 20, (255, 255, 0))]
        self.dice = [Textbox(str(i + 1), 20, tcolor) for i, tcolor in enumerate(gen_colors(6))] + [Textbox('roll', 20, (255, 255, 0))]
        self.select = Textbox('selecting', 15, (255, 255, 0))

        for t in self.coin + self.dice + [self.select]:
            t.add_outline((0, 0, 0))
            
        t = Textbox('', 40, tcolor=(255, 255, 0))
        t.rect.center = (width // 2, height // 2)
        self.elements['message'] = t
        
    def new_message(self, message, timer=60):
        self.elements['message'].set_message_timer(message, timer)
            
#pane stuff --------------------------------------------------------------------------------------------------------------

    def add_panes(self):
        self.player_spots.clear()
        
        num = len(self.players)
        
        w = (self.elements['selection'].rect.left - self.elements['sequence'].rect.right) - 50
        h = height
        r = pg.Rect(0, 0, w, h)
        r.top = 50
        r.left = self.elements['sequence'].rect.right
        
        rows = (num // 5) + 1
        
        if rows == 1:
            ph = ch * 6
        elif rows == 2:
            ph = ch * 4 
        elif rows == 3: 
            ph = ch * 2   
        else:
            ph = ch * 2
            
        x = r.left + 50
        y = r.top

        row_rect = pg.Rect(x, y, 0, 0)
        row = []
        
        attrs = {'coin': self.coin, 'dice': self.dice, 'select': self.select}

        for i, p in enumerate(self.players):

            ps = PlayerSpot(ph, attrs.copy())
            ps.update_info(p)
            ps.rect.topleft = (x, y)
            
            if ps.rect.right > r.right:
                
                x0 = row_rect.x
                row_rect.centerx = r.centerx
                dx = row_rect.x - x0

                for s in row:
                    s.rect.x += dx

                y += ps.rect.height + 20
                x = r.left + 50
                
                ps.rect.topleft = (x, y)
                
                row.clear()
                
                row_rect.width = 0
                row_rect.topleft = (x, y)
                
            row_rect.width = ps.rect.right - row_rect.x
            
            self.player_spots.append(ps)
            row.append(ps)
            
            x += ps.rect.width + 25
            
        x0 = row_rect.x
        row_rect.centerx = r.centerx
        dx = row_rect.x - x0
            
        for s in row:
                    
            s.rect.x += dx

    def relable_panes(self):
        for p, ps in zip(self.players, self.player_spots):

            ps.update_info(p)
      
    def update_player_scores(self, scores):
        checks = []
        pids = []
        
        for pid, score in scores.items():
            
            p = self.get_player_by_pid(pid)
            if p is not None:
                check = p.update_score(score)
            else:
                check = True
            checks.append(check)
            pids.append(int(pid))
            
        if any(checks) or len(pids) != len(self.players):

            players = sorted([p for p in self.players if p.pid in pids], key=lambda p: p.score, reverse=True)
            objects = [p.score_card for p in players]
            self.elements['scores'].join_objects(objects, force=True)

    def update_panes(self):
        self.cards.clear()

        self.elements['last used item'].join_objects([self.last_item] if self.last_item is not None else [])
        self.cards += self.elements['last used item'].get_visible()
        
        self.elements['event'].join_objects([self.event] if self.event is not None else [])
        self.cards += self.elements['event'].get_visible()
        
        self.elements['shop'].join_objects(self.shop, dir='x')
        self.cards += self.elements['shop'].get_visible()

        for i, p in enumerate(self.players):
            
            ps = self.get_spot(p)

            self.cards += ps.add_cards('played', p.played)
            self.cards += ps.add_cards('active_card', [p.active_card] if p.active_card is not None else [])
            
            cards = p.landscapes.copy() + p.ongoing.copy()
            if self.status not in ('waiting', 'playing', 'draft'):         
                cards += [c.copy() for c in p.treasure] 
            self.cards += ps.add_cards('ongoing', cards)

            if p == self.main_p:
                
                self.elements['sequence'].join_objects(p.unplayed.copy())
                self.cards += self.elements['sequence'].get_visible()
                
                self.elements['extra cards'].join_objects(p.items + p.equipped + p.spells + p.treasure, dir='x', pack=True, move=True)
                self.cards += self.elements['extra cards'].get_visible()

                self.elements['selection'].join_objects(p.selection.copy(), dir='y')
                self.cards += self.elements['selection'].get_visible()
                
                self.elements['active card'].join_objects([p.active_card.copy()] if p.active_card is not None else [])
                self.cards += self.elements['active card'].get_visible()
                
        self.cards += self.moving_cards
      
    def get_pane(self, key):
        return self.panes.get(key)
        
    def get_pane_by_player(self, name, player):
        key = name + ' ' + str(self.players.index(player))
        
        return self.panes.get(key)

    def get_spot(self, player):
        for ps in self.player_spots:
            
            if ps.player == player:
                
                return ps

    def add_moving_card(self, player, original=None, type='zoom'):
        if type == 'zoom':
            
            c = original.copy()

            sequence = [{'target': self.get_spot(player).view_card_rect, 'v': 100, 'timer2': 30, 'scale': True},
                        {'target': original.rect, 'v': 50, 'scale': True}]
                       
            c.set_sequence(sequence, start=True)
            c.color = player.color
            
        elif type == 'back':
            
            c = Card('back')
            c.rect.bottomright = (width, height)
            c.set_target(player.card_rect, v=30)

        self.moving_cards.append(c)

#option stuff------------------------------------------------------------------------------
              
    def set_option(self):
        mp = self.main_p
        option = ''
        stat = self.get_status()
        tcolor = (0, 255, 0)
        b = self.elements['main']

        if stat == 'playing':
        
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
            
        else:
            option = stat
            
        if b.get_message() != option:
        
            b.update_message(option, tcolor=tcolor)
        
            if option in ('play', 'flip', 'roll', 'next round', 'new game', 'start'):
                b.enable()        
            else:   
                b.disable()
                
            c = self.elements['cancel']
                
            if option == 'select' and mp.can_cancel:
                c.rect.topleft = b.rect.topright
            else:
                c.rect.center = (-50, -50)
        
    def is_option(self, option):
        return self.get_option() == option
        
    def get_option(self):
        return self.elements['main'].get_message()
        
    def main_button(self):
        option = self.get_option()
        mp = self.main_p
        
        if option == 'play':
            self.send('play')  
            
        elif option == 'flip':
            self.send('flip')

        elif option == 'roll':
            self.send('roll')
            
        elif option == 'start':
            self.send('start')
            
        elif option in ('next round', 'new game'):
            self.send('continue')
        
#status stuff----------------------------------------------------------------------------------
        
    def set_status(self, stat):
        if stat == 'start':
            if not self.is_host():
                stat = 'waiting'
                
        elif stat == 'next round':
            if not self.is_host():
                stat = 'round over'
                
        elif stat == 'new game':
            if not self.is_host():
                stat = 'game over'
                
        elif stat == 'waiting':
            if self.mode == 'single' or (self.is_host() and len(self.players) > 1):
                stat = 'start'

        self.status = stat
            
    def get_status(self):
        return self.status
        
    def is_status(self, stat):
        return self.get_status() == stat
                
#start up stuff-----------------------------------------------------------------------------------------

    def add_player(self, pid):
        if not any(p.pid == pid for p in self.players):
        
            p = Player(self, pid)
            
            self.players.append(p)
            self.players.sort(key=lambda p: p.pid)
            self.add_panes()

            return p
        
    def remove_player(self, pid):
        if any(p.pid == pid for p in self.players):
            
            p = self.get_player_by_pid(pid)

            self.players.remove(p)
            self.add_panes()
            
            self.spritesheet.remove_player_card(p.name)
            
            if pid == 0:
                
                self.exit()
                new_message('the host closed the game', 2000)
                
            else:
                
                self.new_message(f'{p.name} has left the game')

    def reset(self):
        for p in self.panes:
            p.clear()
            
        for ps in self.player_spots:
            ps.clear()
            
        for p in self.players:
            p.reset()

        self.cards.clear()
        self.shop.clear()
        self.points.clear()
        self.moving_cards.clear()
        self.event = None
        self.last_item = None
        
        self.elements['winner'].clear()

        self.round = 1
        self.update_round()
        
    def new_round(self):
        for p in self.players:
            p.new_round()
            
        self.shop.clear()
        self.elements['winner'].clear()
        
        self.round += 1
        self.update_round()
        
    def update_round(self):
        self.elements['round'].update_message(f"round {self.round}/{self.get_settings()['rounds']}")

    def quit(self):
        self.n.close()
        self.playing = False
        pg.quit()
        sys.exit()
        
    def exit(self):
        self.n.close()
        self.playing = False   
  
    def set_name(self):
        name = get_data('username')
        self.main_p.update_name(name)
        self.send(f'name,{name}')
            
#main loop-----------------------------------------------------------------------------
            
    def run(self):
        while self.playing:
        
            self.clock.tick(30)

            self.get_info()
            self.update_info()
            
            self.events()
            self.update()
            self.draw()
 
    def events(self):   
        p = pg.mouse.get_pos()
        self.input = pg.event.get()

        for e in self.input:
            
            if e.type == pg.QUIT:
            
                self.quit() 
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                    self.quit()
                    
                elif e.key == pg.K_s and self.is_host():
                    self.send('start')
                    
                elif e.key == pg.K_p:
                    self.send('play')
                        
                elif e.key == pg.K_x:
                    self.send('cancel')

                elif e.key == pg.K_LALT or e.key == pg.K_RALT:

                    for c in self.cards:
                        
                        if c.rect.collidepoint(p):
                            
                            self.view_card = c
                            
                            break

            elif e.type == pg.KEYUP:
                    
                if e.key == pg.K_LALT or e.key == pg.K_RALT:
                
                    self.view_card = None
                    
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                if e.button == 1:

                    for c in self.cards:
                        
                        if c.rect.collidepoint(p):

                            self.send(str(c.uid))
                            
                            break
                            
                    if self.moving_cards:
                        self.moving_cards.pop(0)
                                
                elif e.button == 3:
                    
                    for c in self.cards:
                        
                        if c.rect.collidepoint(p):
                            
                            self.view_card = c
                            
                            break
                            
            elif e.type == pg.MOUSEBUTTONUP:
                
                if e.button == 3:
                
                    self.view_card = None
                            
        for e in self.elements.values():
            
            e.events(self.input)
            
        for e in self.player_spots:
            
            e.events(self.input)
          
        self.lines.clear()

        for c in self.cards:
            
            if c.rect.collidepoint(p):
                
                self.outlined_card = c
                s = c.rect.center
                others = self.find_card(c)
                
                for o in others:
                
                    self.lines.append((s, o.rect.center))
                    
                break
                
        else:
            
            self.outlined_card = None
                        
    def update(self):  
        self.main_p = self.get_main_p()
        
        self.set_option()
        
        for e in self.elements.values(): 
            e.update()
            
        for e in self.player_spots:
            e.update()

        for p in self.players: 
            p.update()
            
        self.update_panes()
        self.unpack_points()
            
        for p in self.points.copy():
            p.update()
            if p.finished():
                self.points.remove(p)
        self.collide_points()
    
        for c in self.main_p.equipped:
            if c.rect.colliderect(self.camera) and c in self.cards:
                self.add_particles(2, 1, self.main_p.color, rect=c.rect)
                
        if self.moving_cards:
            for c in self.moving_cards[:5]:
                c.update()
                if c.finished():
                    self.moving_cards.remove(c)
    
        for p in self.players:
            if p.is_turn:
                self.add_particles(2, 1, p.color, self.get_spot(p).rect)
                break
                
        for e in self.effects.copy():
            e.update()
            if e.is_finished():
                self.effects.remove(e)

        update_particles(self.particles)    

    def draw(self):
        self.frame.fill((0, 0, 0))

        for t in self.targets.values():
            self.frame.blit(t.textbox.get_image(), t.rect)
            
            for p in t.points:
                self.frame.blit(p.image, p.rect)
                
            for c in t.cards:
                self.frame.blit(c.get_image(), c.rect)
   
        for e in self.player_spots:
            e.draw(self.frame)
            
        for e in self.elements.values():
            e.draw(self.frame)
           
        if self.outlined_card:
            self.frame.blit(self.outlined_card.get_image(outline=True), self.outlined_card.rect)
              
        for s, e in self.lines:
            pg.draw.line(self.frame, (255, 0, 0), s, e, 5)
            
        for p in self.points:
            p.draw(self.frame)
  
        if self.moving_cards:
            for c in self.moving_cards[:5]:
                self.frame.blit(c.get_image(scale=c.get_scale()), c.rect)
            
        for e in self.effects:
            e.draw(self.frame)
            
        draw_particles(self.frame, self.particles)
        
        if self.view_card:
            self.frame.blit(self.view_card.get_image(scale=(card_width, card_height)), self.view_card_rect)

        self.screen.blit(self.frame, (0, 0))
        pg.display.flip()
       
#server stuff-----------------------------------------------------------------------------
  
    def send(self, data, threaded=True):
        if self.playing:
            
            if threaded and self.mode == 'online':
                reply = self.n.threaded_send(data)  
            else:
                reply = self.n.send(data)
            
            if reply is None:
                self.playing = False 
            else:
                return reply

    def get_settings(self):
        return self.send('settings', threaded=False)
        
    def update_settings(self):
        if self.get_status() in ('waiting', 'start', 'new game'):
            print(self.get_status())
            self.send('us')
            new_message('settings saved!', 1000)
        else:
            new_message('cannot change settings while playing', 1000)
            
    def new_settings(self, settings):
        self.settings = settings
        
    def disconnect(self):
        new_message('disconnecting...', 1000)
        self.exit()
        
    def get_info(self):
        info = self.send('info')
        
        if info:

            scores, logs = info
        
            self.update_player_scores(scores)
            
            if logs:

                self.log_queue += logs
                self.log_queue.sort(key=sort_logs)

    def update_info(self):
        self.parse_logs(self.log_queue[:15])
        self.log_queue = self.log_queue[15:]
            
    def parse_logs(self, logs):
        points = []
            
        for log in logs:
            
            pid = log.get('u')
        
            type = log.get('t')
            if 'c' in log:
                name, uid = log.get('c')
            
            if pid == 'g':
                    
                if type == 'tf': 
                    self.transform(uid, log.get('name'))
                    
                elif type == 'add':
                    self.add_player(log.get('pid'))

                elif type == 'del':
                    self.remove_player(log.get('pid'))
                    
                elif type == 'ord':
                    self.reorder(log.get('ord'))
                    
                elif type == 'fin':
                    self.win_screen(log.get('w'))
                    
                elif type == 'res':
                    self.reset()
                    
                elif type == 'nt':
                    self.switch_turn(log.get('pid'))
                    
                elif type == 'ns':
                    self.set_status(log.get('stat'))
                    
                elif type == 'se':
                    self.set_events(name, uid)
                    
                elif type == 'nr':
                    self.new_round()
                    
                elif type == 'fill':
                    self.fill_shop(log.get('cards'))
                    
                #elif type == 'set':
                #    self.new_settings(log.get('settings'))
                    
            else:
                
                p = self.get_player_by_pid(pid)
                
                if type == 'play' and not log.get('d'):
                    p.play(uid)
                    
                elif type in ('gp', 'lp', 'give', 'sp'):
                    self.points_queue.append((p, log))
                    
                elif type == 'nd':
                    p.new_deck(log.get('deck'), log.get('cards'))
                    
                elif type == 'ui':
                    p.use_item(uid, name)
                    
                elif type == 'cast':
                    p.cast(Card(name, uid), self.get_player_by_pid(log.get('target')))
                    
                elif type == 'rs':
                    p.discard(uid)
                    
                elif type == 'cn':
                    p.update_name(log.get('name'))
                    
                elif type == 'aac':
                    p.new_ac(Card(name, uid), log.get('w'), log.get('cancel'))
                    
                elif type == 'rac':
                    p.remove_ac()
                    
                elif type == 'cfs':
                    p.start_flip()
                    
                elif type == 'cfe':
                    p.end_flip(log.get('coin'), log.get('ft'))
                    
                elif type == 'drs':
                    p.start_roll()
                    
                elif type == 'dre':
                    p.end_roll(log.get('dice'), log.get('rt'))
                    
                elif type == 'draw':
                    p.draw(log.get('deck'), log.get('num'))
                      
    def unpack_points(self):
        for info in self.points_queue.copy():
            
            player, pack = info
        
            uid = pack.get('c')[1]
            type = pack.get('t')
            target = self.get_player_by_pid(pack.get('target'))
            
            timer1 = 30
            
            if pack.get('d'):
                self.points_queue.remove(info)
                continue
                
            if any(c.uid == uid for c in self.moving_cards):
                continue
            
            if type == 'gp':
                points = pack.get('gp')
            elif type == 'lp':
                points = -pack.get('lp')
            elif type == 'sp':
                points = pack.get('sp')
            elif type == 'give':
                points = -pack.get('gp')
                
            if points < 0:
                color = (255, 0, 0)
                message = str(points)
            elif points > 0:
                color = (0, 255, 0)
                message = f'+{points}'
            else:
                self.points_queue.remove(info)
                continue
                
            textbox = Textbox(message, tsize=30, tcolor=color, olcolor=(0, 0, 0)) 

            if type == 'sp':

                s = target.target.center
                t = player.target
                
                timer1 = 0
                
            elif type == 'give':

                s = player.target.center
                t = target.target
                
                timer1 = 0
                
            elif type == 'gp' or type == 'lp':
                
                card = self.find_uid(uid)
                
                if card:
                    s = card.rect.center 
                else: 
                    s = player.target.center
                
                t = player.target
           
            else:
                self.points_queue.remove(info)
                continue

            textbox.set_target(t, v=10, timer1=timer1, timer2=100, p=s)
            self.points.append(textbox)
            
            self.points_queue.remove(info)
            
    def collide_points(self):
        removed = []
        
        for p0 in self.points.copy():
            
            if p0 in removed:
                continue
                
            for p1 in self.points.copy():
                
                if p1 in removed:
                    continue
                    
                if p0 is not p1:
                
                    if p0.rect.colliderect(p1.rect):
                        
                        n0 = int(p0.get_message())
                        n1 = int(p1.get_message())
                        
                        n = n0 + n1
                        
                        if n < 0:
                            message = str(n)
                            tcolor = (255, 0, 0)
                        elif n > 0:
                            message = f'+{n}'
                            tcolor = (0, 255, 0)
                        else:
                            self.points.remove(p0)
                            self.points.remove(p1)
                            removed.append(p0)
                            removed.append(p1)
                            continue
                            
                        p0.update_message(message)
                        p0.set_color(tcolor)
                        p0.reset_timer()
                        
                        self.points.remove(p1)
                        removed.append(p1)
    
    def fill_shop(self, cards):
        self.shop.clear()
        
        for name, uid in cards:           
            self.shop.append(Card(name, uid))
       
#helper stuff-------------------------------------------------------------------------------
 
    def reorder(self, pids):
        players = []
        
        for pid in pids:
            
            p = self.get_player_by_pid(pid)
            
            if p:
                
                players.append(p)
                
        self.players = players
        self.relable_panes()
        
    def win_screen(self, pids):
        winners = []
        
        for pid in pids:
            
            p = self.get_player_by_pid(pid)
            if p is not None: 
                winners.append(p)
                
        text = self.elements['winner']
                
        if len(winners) == 1:
            
            w = winners[0]
            text.update_message(f'{w.name} wins!')
            text.set_color(w.color)
            self.add_particles(2000, 0, w.color, text.rect)
            
        else:
            
            colors = [w.color for w in winners]
            
            message = f'{len(winners)} way tie!'
            while len(message.replace(' ', '')) < len(winners):
                message += '!'
            
            text.update_message(message)
            text.multicolor(colors)

            for c in colors:
                self.add_particles(2000 // len(colors), 0, c, text.rect)
        
    def switch_turn(self, pid):
        for p in self.players:
            
            if p.pid == pid:
                
                p.is_turn = True
                
            else:
                
                p.is_turn = False
  
    def set_events(self, name, uid):
        self.event = Card(name, uid)
                 
    def transform(self, uid, name):
        for p in self.players:
            
            for deck in p.get_cards():
                
                for i, c in enumerate(deck):

                    if c.uid == uid:
                        
                        deck[i] = Card(name, uid)

#-------------------------------------------------------------------------------------------

    def get_scores(self):
        return {p.pid: p.score for p in self.players}

    def get_player_by_pid(self, pid):
        if type(pid) == str:
            if pid.isnumeric():
                pid = int(pid)
        return next((p for p in self.players if p.pid == pid), None)

    def find_local_card(self, card):
        for c in self.panes['extra cards'].cards:
            
            if c == card:
                
                return c
        
    def find_card(self, other):
        cards = []
        
        for c in self.cards:
            
            if c == other and c is not other:
                
                cards.append(c)
                
        return cards
                
    def find_uid(self, uid):
        for c in self.cards:
            
            if uid == c.uid and spritesheet.check_name(c.name):
                
                return c
                
    def uid_exists(self, upd):
        return any(c.uid == uid for c in self.cards)
        
    def get_target(self, pid):
        return self.targets[pid]
        
    def get_panes(self, name):
        panes = []
        
        for key in self.panes:
            
            if name in key:
                
                panes.append(self.panes[key])
                
        return panes
    
    def add_particles(self, num, type, color, rect=None, pos=None):
        self.particles += get_particles(num, type, color, rect, pos)
   
if __name__ == '__main__':

    pg.init()

    clock = pg.time.Clock()

    win = pg.display.set_mode((width, height))
    pg.display.set_caption('card game')

    spritesheet = Spritesheet()
  
    menu(mode='main')
        
    pg.quit()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        