import pygame as pg
import time
import sys
import subprocess
from network import Network
from spritesheet import Spritesheet, Textbox, create_text
from settings import settings as defult_settings

def get_ips(): #returns dictionary of any saved ip addresses (used for connecting via port forwarding)
    with open('ips.txt', 'r') as f:
    
        ips = {name: ip for name, ip in [tup.strip().split(' ') for tup in f]}
        
    return ips

pg.init()

clock = pg.time.Clock()

width = 1024
height = 576

cw = 375 // 10
ch = 525 // 10

fps = 30

win = pg.display.set_mode((width, height)) #initiate window

spritesheet = Spritesheet() #load spritesheet info

def get_btn(btns, text): #find button in list of buttons based on text
    return next((b for b in btns if b.message == text), None)
    
def show_winner(players): #shows winner of the round
    players.sort(key=lambda p: p.score, reverse=True)
    
    for i, p in enumerate(players):
        
        new_message('1: {}: {} points'.format(p.pid, p.score))

def set_screen(mode, wait=0): #sets starting screen based on given mode
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
        
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += text.rect.height
        screen.append(text)
        
    elif mode == 'choose host':
        
        for name in get_ips().keys():
        
            text = Textbox(name, 20)
            screen.append(text)
            
        y = (height - sum(t.rect.height for t in screen)) / 2
        
        for t in screen:
            
            t.rect.midtop = (width / 2, y)
            
            y += t.rect.height
            
        text = Textbox('back', 20)
        text.rect.midtop = screen[-1].rect.midbottom
        text.rect.y += 20
        screen.append(text)

    new_screen(screen, wait)
        
    return screen #returns list of objects on screen
    
def settings_screen(settings): #special function to set up the settings screen
    screen = []
    
    text = Textbox('rounds: ', 20, counter=settings['rounds'], r=range(1, 26))
    screen.append(text)
    
    text = Textbox('free play: {}'.format(settings['fp']), 20)
    screen.append(text)
    
    text = Textbox('starting score: ', 20, counter=settings['ss'], r=range(5, 51))
    screen.append(text)

    text = Textbox('starting cards: ', 20, counter=settings['cards'], r=range(1, 11))
    screen.append(text)
    
    text = Textbox('starting items: ', 20, counter=settings['items'], r=range(0, 6))
    screen.append(text)
    
    text = Textbox('starting spells: ', 20, counter=settings['spells'], r=range(0, 6))
    screen.append(text)
    
    text = Textbox('score wrap: {}'.format(settings['score wrap']), 20)
    screen.append(text)
    
    text = Textbox('number of cpus: ', 20, counter=settings['cpus'], r=range(1, 10))
    screen.append(text)
    
    y = (height - sum(t.rect.height for t in screen)) / 2
    
    for t in screen:
        
        t.rect.y = y
        t.rect.centerx = width / 2
        
        if hasattr(t, 'counter'):
        
            t.move_counter()
        
        y += t.rect.height
    
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
    
    new_screen(screen)
    
    return screen

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

def connect(ip=None): #try connecting to game
    new_message('searching for game...')
    
    try:
                
        c = Client(win, ip) #attempt to find running game
        
    except EOFError: #triggers if host or client leaves game
        
        new_message('disconnecting...', 1000)
        
    except TypeError as e: #triggers if client tries to search for a game and is unable to find one
        
        print(e)
        
        new_message('no games were found', 2000)
        
    except Exception as e: #catch all other exceptions while playing
        
        print(e)
        
        new_message('an error occurred', 2000)
        
def start_game(): #start a new game
    new_message('starting game...', 500)
    
    try:
                
        c = Client(win) #try to host a game
        
    except EOFError: #triggers if host leaves game

        new_message('diconnected', 1000)
        
    except Exception as e: #catch any other exceptions
    
        print(e)
        
        new_message('an error occurred', 2000)
        
def single_player(): #start a single player game
    new_message('starting game...', 500)
    
    from game import Game #import game class
    
    Client(win, 0, Game('single'))
    
    new_message('returning to main menu...', 1000) #if any errors occur or player leaves game, retrun to main menu

def menu():
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
    
    running = True
    
    while running:
        
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
                            
                        else:
                            
                            return get_ips()[t.message]
        
def main():
    running = True
    
    while running:
        
        mode = menu()
        
        if mode == 'search online':
            
            ip = client_menu()
            
            if ip:
                
                connect(ip)
                
        elif mode == 'search local':
            
            connect()
                
        elif mode == 'host':
            
            subprocess.Popen([sys.executable, 'server.py'])
            
            start_game()
            
        elif mode == 'single':
            
            single_player()
                
        elif mode == 'quit':
            
            running = False
            
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
                            
                            client.n.send('reset')
                            
                            return
                            
                        elif t.message == 'disconnect':
                            
                            client.exit()
                            
                            pg.time.wait(1000)
                            
                            return
                            
                        elif t.message == 'back':
                            
                            return
                            
                        elif t.message == 'game settings':
                            
                            settings_menu(client, client.n.send('settings'))
                            
def settings_menu(client, settings):
    running = True
    
    while running:
    
        client.clock.tick(30)

        btns = settings_screen(settings)

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

                    elif hasattr(t, 'counter'):
                        
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
                            
                            

class Coin:
    def __init__(self, game, tsize=20):
        self.game = game
        
        self.text = (Textbox('tails', tsize), Textbox('heads', tsize), Textbox('flip', tsize))
        
    def move_text(self, pos):
        for t in self.text:
            
            t.rect.topleft = pos
            
class Dice:
    def __init__(self, game, tsize=20):
        self.game = game
        
        self.text = [Textbox(str(i + 1), tsize) for i in range(6)]
        self.text.append(Textbox('roll', tsize))
            
    def move_text(self, pos):
        for t in self.text:
            
            t.rect.topleft = pos
    
class Pane:
    def __init__(self, rect, message, color=(0, 0, 0), layer=0, tsize=10, tcolor=(255, 255, 255), tab=False, single=False):
        self.rect = rect
        
        self.text_box = Textbox(message, tsize, tcolor)
        
        self.move_text()
        
        self.color = color
        
        self.single = single
        
        self.tab = tab
        
        self.cards = []
        
        self.layer = layer
        
        if tab:

            self.pos = [self.rect.x, height]
            self.adjust_pos()
        
            self.vel = [0, 5 * self.rect.height / 50]
        
            self.mode = None
        
            self._open = False
            self.closed = True
            
            self.locked = False
            
            self.timer = 0
            
            self.auto = False
            
    def is_tab(self):
        return self.tab
        
    def check_cards(self, c):
        return c in self.cards
        
    def click(self):
        if self.timer > 10:
            
            self.timer = 0
            
        else:
            
            self.locked = not self.locked
        
    def hit(self, r):
        detect = pg.Rect(self.rect.x, height - self.text_box.rect.height, self.rect.width, self.text_box.rect.height)
        
        if detect.colliderect(r) or self.rect.colliderect(r):
            
            self.mode = 'opening'
            
        elif not self.closed and not self.locked:
            
            self.mode = 'closing'
        
    def open(self):
        self.rect.bottom = height
        self.pos = [self.rect.x, self.rect.y]
        self.move_text()
        
        self._open = True
        self.closed = False
        
        self.mode = None
        
    def close(self):
        self.rect.top = height
        self.pos = [self.rect.x, height]
        self.move_text()
        
        self.closed = True
        self._open = False
        
        self.mode = None
        
    def adjust_pos(self):
        self.rect.topleft = self.pos
        
        self.move_text()
        
    def start_auto(self, t=60):
        self.auto = True
        self.timer = t
        
    def update(self):
        if self.auto:
            
            self.mode = 'opening'
            
        if self.mode is not None:
            
            self._open = self.closed = False
            
        if self.mode == 'opening':
        
            self.pos[1] -= self.vel[1]
            
            self.adjust_pos()
            
            if self.rect.bottom < height:
                
                self.open()
                
        elif self.mode == 'closing':
            
            self.pos[1] += self.vel[1]
            
            self.adjust_pos()
            
            if self.rect.top > height: 
                
                self.close()
                
        self.mode = None
        
        if self.auto:
            
            self.timer -= 1
            
            if not self.timer:
                
                self.auto = False
                
        else:
        
            self.timer += 1

    def draw(self, win):
        pg.draw.rect(win, self.color, self.rect)
        
        for c in self.cards:
            
            win.blit(c.get_image(), c.rect)
        
        win.blit(self.text_box.text, self.text_box.rect)
        
    def move_text(self):
        self.text_box.rect.midbottom = self.rect.midtop
        
    def move_body(self):
        self.rect.midtop = self.text_box.rect.midbottom
        
    def new_x(self, x):
        self.pos[0] = x
        
        self.adjust_pos()
        
    def update_text(self, message, tcolor=None):
        self.text_box.update_text(message, tcolor)
        
        self.move_text()
        
    def add_cards(self, cards, ypad=5, xpad=5, dir='y'):
        if self.single:
            
            xpad = ypad = 0
    
        if dir == 'y':
        
            y = 0
            x = 0

            for c in cards:
                
                if self.rect.y + y + ypad + c.rect.height > height:
                    
                    y = 0
                    x = c.rect.width + xpad
            
                c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                
                y += c.rect.height + ypad

        elif dir == 'x':
            
            x = 0
            
            for c in cards:
                
                c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                
                x += c.rect.width + xpad
                
        if any(c not in self.cards for c in cards):
            
            self.start_auto(60)
                
        self.cards = cards.copy()
        
class Slider:
    def __init__(self, rect, message, color=(0, 0, 0), layer=0, tsize=10, tcolor=(255, 255, 255), dir='+', sensor=None):
        self.rect = rect
        
        self.text_box = Textbox(message, tsize, tcolor)
        
        self.move_text()
        
        self.color = color

        self.cards = []
        
        self.layer = layer

        self.pos = [self.rect.x, self.rect.y]
        self.adjust_pos()
        
        self.ref = self.rect.copy()
        
        if sensor is None:
        
            self.sensor = self.ref.copy()
            self.sensor.height = 50
            
        else:
            
            self.sensor = sensor
    
        self.vel = [5 * self.rect.height / 50, 0]
        
        self.dir = dir
        
        if dir == '-':
            
            self.vel[0] *= -1
    
        self.mode = None
    
        self._open = False
        self.closed = True
        
        self.locked = False
        
        self.timer = 0
        
        self.auto = False
            
    def is_tab(self):
        return True
        
    def set_origin(self, pos):
        self.ref.topleft = pos
        
    def click(self):
        if self.timer > 10:
            
            self.timer = 0
            
        else:
            
            self.locked = not self.locked
        
    def hit(self, r):
        if (self._open and (self.ref.colliderect(r) or self.rect.colliderect(r))) or self.sensor.colliderect(r):
            
            self.mode = 'opening'
            
        elif not self.closed and not self.locked:
            
            self.mode = 'closing'
        
    def open(self):
        if self.dir == '+':
            
            self.rect.left = self.ref.right
            self.pos = [self.ref.right, self.ref.y]
            self.move_text()
            
            self._open = True
            self.closed = False
            
            self.mode = None
            
        elif self.dir == '-':
            
            self.rect.right = self.ref.left
            self.pos = [self.ref.x - self.rect.width, self.ref.y]
            self.move_text()
            
            self._open = True
            self.closed = False
            
            self.mode = None
        
    def close(self):
        self.rect.topleft = self.ref.topleft
        self.pos = [self.rect.x, self.rect.y]
        self.move_text()
        
        self.closed = True
        self._open = False
        
        self.mode = None

    def adjust_pos(self):
        self.rect.topleft = self.pos
        
        self.move_text()
        
    def update(self):
        if self.auto:
            
            self.mode = 'opening'
            
        if self.mode is not None:
            
            self._open = self.closed = False
            
        if self.mode == 'opening':
        
            self.pos[0] += self.vel[0]
            
            self.adjust_pos()
            
            if (self.dir == '+' and self.rect.left > self.ref.right) or (self.dir == '-' and self.rect.right < self.ref.left):
                
                self.open()
                
        elif self.mode == 'closing':
            
            self.pos[0] -= self.vel[0]
            
            self.adjust_pos()
            
            if (self.dir == '+' and self.rect.right < self.ref.right) or (self.dir == '-' and self.rect.left > self.ref.left):
                
                self.close()
                
        self.mode = None
        
        if self.auto:
            
            self.timer -= 1
            
            if not self.timer:
                
                self.auto = False
                
        else:
        
            self.timer += 1

    def draw(self, win):
        if self.color != (0, 0, 0):
        
            pg.draw.rect(win, self.color, self.rect)
        
        for c in self.cards:
            
            win.blit(c.get_image(), c.rect)
        
        win.blit(self.text_box.text, self.text_box.rect)
        
    def move_text(self):
        self.text_box.rect.midbottom = self.rect.midtop
        
    def move_body(self):
        self.rect.midtop = self.text_box.rect.midbottom
        
    def update_text(self, message, tcolor=None):
        self.text_box.update_text(message, tcolor)
        
        self.move_text()
        
    def start_auto(self, t=60):
        self.auto = True
        self.timer = t
        
    def add_cards(self, cards, ypad=5, xpad=5, dir='y'):
        if dir == 'y':
        
            y = 0
            x = 0

            for c in cards:
                
                if y + ypad + c.rect.height > height:
                    
                    y = 0
                    x = c.rect.width + xpad
            
                c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                
                y += c.rect.height + ypad

        elif dir == 'x':
            
            x = 0
            
            for c in cards:
                
                c.rect.topleft = (self.rect.x + x + xpad, self.rect.y + y + ypad)
                
                x += c.rect.width + xpad
                
        if any(c not in self.cards for c in cards):
            
            self.start_auto(60)
                
        self.cards = cards.copy()

class Player:
    def __init__(self, client, pid):
        self.client = client
        
        self.pid = pid
        
        self.host = True if pid == 0 else False

        self.score = 0
        
        self.coin = None
        self.dice = None
        
        self._coin = Coin(client)
        
        self.flipping = False
        self.rolling = False
        
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
        self.used_items = []
        
        self.card = Textbox('')
        
    def get_image(self, mini=False):
        return self.card.text
        
    def update_info(self, info):
        if not info.get('points') and self is not self.client.main_p:
            
            if info['score'] - self.score:
            
                try:
            
                    self.client.points.append(Points(info['score'] - self.score, list(self.client.panes['spot {}'.format(self.pid)].rect.topleft)))
        
                except KeyError:
                    
                    return
        
        for attr in info:
            
            if attr in ('score', 'coin', 'dice', 'flipping', 'rolling'):
        
                setattr(self, attr, info[attr])
                
            elif attr in ('landscape', 'active_card'):
                
                name, uid = info[attr]
                
                setattr(self, attr, Card(name, uid))
                
            elif attr == 'points':
                
                continue
                
            elif attr == 'treasure':
                
                dt = len(info[attr]) - len(self.treasure)
                
                if dt > 0:
                    
                    self.client.points.append(Points(dt, list(self.client.panes['spot {}'.format(self.pid)].rect.topleft), dt=True))
                    
                setattr(self, attr, [Card(name, uid) for name, uid in info[attr]])
                
            elif type(info[attr]) == list:

                setattr(self, attr, [Card(name, uid) for name, uid in info[attr]])
                
            else:
                
                setattr(self, attr, info[attr])
                
        if 'active_card' not in info:
            
            self.active_card = None

class Points:
    def __init__(self, points, pos, dt=False):
        self.pos = pos
        
        if dt:
            
            self.text = Textbox('+{}'.format(points), 30, (255, 255, 0))
        
        elif points > 0:
        
            self.text = Textbox('+{}'.format(points), 30, (0, 255, 0))
            
        else:
            
            self.text = Textbox('{}'.format(points), 30, (255, 0, 0))
        
        self.rect = self.text.rect
        self.rect.topleft = self.pos
        
        self.image = self.text.get_image()
        
        self.vel = [0, -3]
        
        self.timer = 30
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        self.rect.topleft = self.pos
        
        self.timer -= 1
        
        return self.timer
        
class Card:
    def __init__(self, name, uid=id('')):
        self.name = name
        
        self.uid = uid
        
        self.rect = pg.Rect(0, 0, cw, ch)
        
    def copy(self):
        return type(self)(self.name, self.uid)
        
    def __eq__(self, other):
        return self.uid == other.uid
        
    def get_image(self, mini=True):
        return spritesheet.get_image(self.name, mini)
        
    def update(self, name, uid):
        self.name = name
        
        self.uid = uid
        
class Client:
    def __init__(self, screen, ip=None, n=None):
        self.screen = screen
        pg.display.set_caption('test')
        
        self.clock = pg.time.Clock()
        
        self.mouse = pg.Rect(0, 0, 1, 1)
        
        self.n = Network(ip) if n is None else n #if no game is sent, we need network to connect to game, otherwise use game as network
        
        self.pid = int(self.n.get_pid())

        self.players = [Player(self, self.pid)]
        
        self.main_p = next(p for p in self.players if p.pid == self.pid)
        
        self.event = Card('', id(self))

        self.flipping = False
        self.rolling = False
        
        self.cards = []
        self.lines = []
        self.points = []

        self.view_card = None

        self.loop_times = []
        
        self.panes = {}
        self.text = {}
        
        self.new_game()
        
    def new_game(self):
        self.cards.clear()

        self.set_screen()
        
        self.coin = Coin(self, 50)
        self.dice = Dice(self)
        
        self.run()
        
    def add_player(self, pid):
        p = Player(self, pid)
        
        self.players.append(p)
        
        self.set_screen()
        
        return p
        
    def remove_player(self, p):
        self.players.remove(p)
        
        self.set_screen()
        
    def new_info(self, info): #unpack new info recieved from game or network
        if type(info) == dict:
        
            if 'e' in info:
            
                name, uid = info['e']
                
                self.event.update(name, uid)
            
                del info['e']
            
            for pid in info:

                p = next((p for p in self.players if p.pid == pid), None)
                
                if p is None:
                    
                    p = self.add_player(pid)
                
                p.update_info(info[pid])
      
            players = list(info.keys())
            
            for p in self.players.copy():
                
                if p.pid not in players:
                    
                    self.remove_player(p)
                
            self.players.sort(key=lambda p: players.index(p.pid))
            
            if info[self.pid].get('points'):
        
                self.unpack_points(info[self.pid]['points'])

    def set_screen(self):
        self.panes = {}
        self.text = {}
        self.coins = []
        self.dices = []
        
        ph = ch * 7
        
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
        
        pane = Pane(pg.Rect(0, 0, cw * 2.5, ph), 'your items', (255, 0, 0), tab=True)
        pane.new_x(self.panes['card area'].rect.right + 10)
        self.panes['items'] = pane
        
        pane = Pane(pg.Rect(0, 0, cw * 2.5, ph), 'equipped', (0, 255, 0), tab=True)
        pane.new_x(max(self.panes['items'].rect.right, self.panes['items'].text_box.rect.right) + 10)
        self.panes['equipped'] = pane
        
        pane = Pane(pg.Rect(0, 0, cw * 1.5, ph), 'spells on you', (0, 255, 255), tab=True)
        pane.new_x(max(self.panes['equipped'].rect.right, self.panes['equipped'].text_box.rect.right) + 20)
        self.panes['spells'] = pane
        
        pane = Pane(pg.Rect(0, 0, cw * 1.5, ph), 'your treasure', (255, 255, 0), tab=True)
        pane.new_x(max(self.panes['spells'].rect.right, self.panes['spells'].text_box.rect.right) + 20)
        self.panes['treasure'] = pane
        
        text = Textbox('player {}'.format(self.main_p.pid), 50)
        text.rect.bottomleft = self.panes['card area'].text_box.rect.topleft
        text.rect.y -= 20
        self.text['player'] = text
        
        text = Textbox('play', 50)
        text.rect.midbottom = (width // 2, height)
        text.rect.y -= 10
        self.text['play'] = text

        left = self.text['player'].rect.right + 20
        right = self.panes['selection area'].rect.left
        step = (right - left) // len(self.players)

        for i, x in zip(range(len(self.players)), range(left, right, step)):    
            
            p = self.players[i]
            
            pane = Pane(pg.Rect(x, 40, cw * 1.5, ph), '', tsize=20, layer=len(self.players) - i)
            self.panes['spot {}'.format(i)] = pane
        
            pane = Slider(pg.Rect(x, 40, cw * 1.5, ph), '', tsize=20, layer=(len(self.players) - i) + 1, dir='-')
            self.panes['spells {}'.format(i)] = pane

            pane = Slider(pg.Rect(x, 40, cw * 1.5, ph), '', tsize=20, layer=(len(self.players) - i) + 1)
            self.panes['items {}'.format(i)] = pane
            
            pane = Slider(pg.Rect(x, 40, cw * 1.5 * 2, ph), '', tsize=20, layer=(len(self.players) - i) + 1, sensor=pg.Rect(x, 40, cw * 1.5 * 2, ch), dir='-')
            self.panes['landscape {}'.format(i)] = pane
            
            coin = Coin(self)
            coin.move_text(self.panes['spot {}'.format(i)].rect.topright)
            self.coins.append(coin)
            
            dice = Dice(self)
            dice.move_text(self.panes['spot {}'.format(i)].rect.topright)
            self.dices.append(dice)

        y = 0
        
        for i, p in enumerate(self.players):

            text = Textbox('player {}: {}'.format(p.pid, p.score))
            text.rect.topleft = (0, y)
            self.text['score {}'.format(i)] = text
            
            y += text.rect.height
            
        self.view_card_rect = pg.Rect(0, 0, 375, 525)
        self.view_card_rect.center = (width // 2, height // 2)

        self.event.rect.midtop = self.panes['selection area'].rect.midtop
        self.event.rect.y -= 200
        
        text = Textbox('options', 20)
        text.rect.topright = (width, 0)
        text.rect.y += 30
        text.rect.x -= 30
        self.text['options'] = text
        
        pane = Pane(pg.Rect(0, 0, cw, ch), 'event', (0, 0, 0))
        pane.rect.midbottom = self.panes['selection area'].rect.midtop
        pane.rect.y -= 30
        pane.move_text()
        self.panes['event'] = pane
        
    def update_panes(self):
        self.cards.clear()
        
        for i, p in enumerate(self.players):
            
            pane = self.panes['spot {}'.format(i)]  
            pane.update_text('player {}'.format(p.pid))
            cards = [c.copy() for c in p.played]
            pane.add_cards(cards)
            self.cards += cards
            
            pane = self.panes['spells {}'.format(i)]
            cards = [c.copy() for c in p.ongoing]
            pane.add_cards(cards)
            self.cards += cards
            
            pane = self.panes['items {}'.format(i)]
            cards = [c.copy() for c in p.used_items]
            pane.add_cards(cards)
            self.cards += cards
            
            if p.landscape is not None:
            
                pane = self.panes['landscape {}'.format(i)]
                pane.add_cards([p.landscape])
                self.cards.append(p.landscape)
                
            else:
                
                self.panes['landscape {}'.format(i)].cards.clear()

            if p == self.main_p:
                
                self.panes['card area'].add_cards(p.unplayed)
                self.panes['items'].add_cards(p.items + p.spells)
                self.panes['selection area'].add_cards(p.selection)
                self.panes['treasure'].add_cards(p.treasure)
                self.panes['spells'].add_cards(p.ongoing)
                self.panes['equipped'].add_cards(p.equipped)
                
                if p.active_card is not None:
                
                    self.panes['active card'].add_cards([p.active_card])
                    self.cards.append(p.active_card)
                    
                else:
                    
                    self.panes['active card'].cards.clear()

                self.cards += p.unplayed
                self.cards += p.items + p.spells
                self.cards += p.selection
                self.cards += p.treasure
                self.cards += p.equipped
                self.cards += p.ongoing

                self.text['player'].update_text('player {}'.format(p.pid))
 
        y = 0
                
        players = sorted(self.players, key=lambda p: p.score, reverse=True)
        
        for i, p in enumerate(players):
        
            text = self.text['score {}'.format(i)]
            text.update_text('player {}: {}'.format(p.pid, p.score))
            text.rect.topleft = (0, y)
            y += text.rect.height

        if self.event is not None:
            
            self.panes['event'].add_cards([self.event], xpad=0, ypad=0)

            self.cards.append(self.event)
        
    def update_settings(self, settings):
        for key, val in settings.items():
            
            reply = self.n.send('-{},{}'.format(key, val))
            
        return reply

    def find_card(self, other):   
        for c in self.cards:
            
            if c.uid == other.uid and c is not other and 'player' not in c.name and c.rect.topleft != (0, 0):
                
                return c
                
    def find_uid(self, uid):
        for c in self.cards:
            
            if uid == c.uid and 'player' not in c.name:
                
                return c
                
    def unpack_points(self, points):
        for pack in points:

            uid = pack[-1]
            type = pack[0]
            points = pack[1] if type in ('gp', 'sp') else -pack[1]
            
            c = self.find_uid(pack[-1])
            
            if c:
                
                pos = [c.rect.x, c.rect.y]
                
            else:
                
                r = self.text['player'].rect
                
                pos = [r.x, r.y]
   
            self.points.append(Points(points, pos))
                
            
     
    def quit(self):
        self.n.close()
        self.playing = False
        pg.quit()
        sys.exit()
        
    def exit(self):
        self.n.close()
        
        self.playing = False
            
    def events(self):
        self.mouse.topleft = pg.mouse.get_pos()

        for e in pg.event.get():
            
            if e.type == pg.QUIT:
                self.quit() 
                
            elif e.type == pg.KEYDOWN:
            
                if e.key == pg.K_ESCAPE:
                    self.quit()
                    
                elif e.key == pg.K_p:
                    
                    self.n.send('play')
                        
                elif e.key == pg.K_x:
                    
                    self.n.send('cancel')
                    
                elif e.key == pg.K_s and self.pid == 0:
                    
                    self.n.send('start')
                    
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

                if self.mouse.colliderect(self.text['play'].rect):
                    
                    self.n.send('play')
                    
                else:
                    
                    c = next((c for c in self.cards if self.mouse.colliderect(c.rect)), None)
                    
                    if c:

                        self.n.send(str(c.uid))
                        
                    else:
                    
                        self.n.send('select')
                        
                for p in self.panes.values():
                    
                    if p.is_tab():
                        
                        if p.rect.colliderect(self.mouse):
                            
                            p.click()
                            
                            break
                        
        for pane in self.panes.values():
            
            if pane.is_tab():
                
                pane.hit(self.mouse)
                        
    def update(self):
        self.new_info(self.n.send('info'))
        
        for pane in self.panes.values():
            
            if pane.is_tab():
                
                pane.update()
        
        for p in self.players:
            
            p.card.update_text('player {}: {}'.format(p.pid, p.score))
        
        for c in self.cards:
            
            if c.rect.colliderect(self.mouse):
            
                s = c.rect.center
                
                other = self.find_card(c)
                
                if other:
                
                    e = other.rect.center
                    self.lines.append((s, e))
                        
        self.update_panes()

        for p in self.points.copy():
            
            if not p.update():
            
                self.points.remove(p)
        
    def draw(self):
        frame = pg.Surface((width, height)).convert()
        
        #for p in self.players:
        #    
        #    if p.is_turn:
        #        
        #        self.text

        for pane in sorted(self.panes.values(), key=lambda pane: pane.layer, reverse=True):
            
            pane.draw(frame)
  
        for key in self.text:
            text = self.text[key]
            frame.blit(text.text, text.rect)
                
        if self.view_card:
            frame.blit(self.view_card.get_image(False), self.view_card_rect)
            
        img = None
        
        if self.main_p.flipping:
        
            if self.main_p.coin is None:
            
                img = self.coin.text[-1]
                
            else:    
            
                img = self.coin.text[self.main_p.coin]

            img.rect.bottomright = self.panes['active card'].rect.bottomleft
            img.rect.x -= 20

            frame.blit(img.text, img.rect)

        elif self.main_p.rolling:
        
            if self.main_p.dice is not None:
            
                img = self.dice.text[self.main_p.dice - 1]
                img.rect.bottomright = self.panes['active card'].rect.bottomleft
                img.rect.x -= 20

                frame.blit(img.text, img.rect)
                
        for i, p in enumerate(self.players):
            
            if p.flipping and p.coin is not None:
                
                text = self.coins[i].text[p.coin]
                
                frame.blit(text.get_image(), text.rect)
                
            elif p.rolling and p.dice is not None:
                
                text = self.dices[i].text[p.dice - 1]
                
                frame.blit(text.get_image(), text.rect)
                
        for s, e in self.lines:
            pg.draw.line(frame, (255, 0, 0), s, e, 5)
        self.lines.clear()

        for p in self.points:
            
            frame.blit(p.image, p.rect)
        
        self.screen.blit(frame, (0, 0))

        pg.display.flip()
        
    def run(self):
        self.playing = True
        
        while self.playing:
        
            self.clock.tick(30)
            
            self.events()
            
            self.update()

            self.draw()
     

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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        