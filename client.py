import pygame as pg
import random, colorsys

import save

import spritesheet

from constants import *
from ui import *
from particles import *

def init():
    globals()['SAVE'] = save.get_save()
    globals()['SPRITESHEET'] = spritesheet.get_sheet()

#menus-----------------------------------------------------------------

def game_options_menu(client):
    screen = []

    btn = Button((200, 30), 'disconnect', tag='break', func=client.disconnect)
    btn.rect.midtop = (width // 2, height // 2)
    screen.append(btn)
    
    btn = Button((200, 30), 'game settings', func=menu, args=[game_settings_menu], kwargs={'args': [client]})
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

    return screen

def game_settings_menu(client):
    screen = []

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

#other--------------------------------------------------------------

def gen_colors(num):
    golden = (1 + 5 ** 0.5) / 2
    colors = []
    
    for i in range(num):
        
        h = (i * (golden - 1)) % 1
        r, g, b = colorsys.hsv_to_rgb(h, 0.8, 1)
        rgb = (r * 255, g * 255, b * 255)
        colors.append(rgb)

    return colors

#button functions------------------------------------------------------------------

def save_game_settings(client, counters):
    settings = {c.tag: c.get_current_option() for c in counters}  
    SAVE.set_data('settings', settings)
    client.update_settings(settings)
    
#-----------------------------------------------------------------------------------

class Player:
    def __init__(self, client, pid, info, name=None):
        self.client = client
        
        self.pid = pid
        self.name = info['name']
        self.color = self.client.colors[pid]
        self.info = info
        SPRITESHEET.add_player_card(self.info, self.color)

        self.target = pg.Rect(0, 0, 20, 20)
        self.view_card_rect = pg.Rect(0, 0, card_width // 2, card_height // 2)
        self.card_rect = pg.Rect(0, 0, cw, ch)

        self.score = -1
        self.score_card = Textbox('', tsize=20, fgcolor=self.color)
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
        self.active_spells = []
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
        self.active_spells.clear()
        self.used_item = None
        
    def new_round(self):
        self.played.clear()
        self.unplayed.clear()
        self.selection.clear()
        self.ongoing.clear()
        self.landscapes.clear()
        self.active_spells.clear()
        self.active_card = None
        
    def get_cards(self):
        return [self.played, self.unplayed, self.items, self.selection, self.selected, self.equipped, self.ongoing, self.treasure, self.spells, self.landscapes]

    def get_spot(self):
        return self.client.get_spot(self.pid)

    def play(self, c):  
        self.client.add_moving_card(self, original=c)
        sound = SPRITESHEET.get_sound(c.name)
        if sound:
            sound.play()
         
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
                
    def discard(self, name, uid, tags):
        c = Card(name, uid)
        c.set_olcolor(self.color)
        self.client.last_item = c
        
        self.client.add_moving_card(self, c)
 
    def cast(self, card, target):
        for c in self.spells:
            
            if c == card:

                self.spells.remove(c)

                break
                
        self.client.add_moving_card(self, card)
                
        card.set_olcolor(self.color)     
        target.ongoing.append(card)
        
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
        if self.pid == 1:
            print(True)
        self.rolling = False
        self.dice = dice - 1
        self.timer = timer

    def draw(self, deck, num):
        #for _ in range(num):
        #    
        #    self.client.add_moving_card(self, type='back')
        pass

class Card(Mover):
    def __init__(self, name, uid=None, color=None, olcolor=None):
        self.name = name
        self.uid = uid if uid is not None else id(self)
        self.color = color
        self.olcolor = olcolor
        self.rect = pg.Rect(0, 0, cw, ch)
        
        super().__init__()
 
    def __eq__(self, other):
        return self.uid == other.uid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def copy(self):
        c = Card(self.name, uid=self.uid, color=self.color, olcolor=self.olcolor)
        c.rect = self.rect.copy()
        return c
        
    def set_color(self, color):
        self.color = color
        
    def set_olcolor(self, olcolor):
        self.olcolor = olcolor
        
    def get_image(self, scale=(cw, ch)):
        return SPRITESHEET.get_image(self.name, scale=scale, olcolor=self.olcolor)
        
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
        self.label.set_fgcolor(player.color)
        self.label.update_message(self.player.name)
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
    def __init__(self, connection, mode):
        self.screen = pg.display.get_surface()
        self.mode = mode
        self.status = ''
        self.round = 1

        self.camera = self.screen.get_rect()
        
        self.clock = pg.time.Clock()

        self.n = connection
        self.playing = True
        self.logs = {}
        self.log_queue = []
        self.frame = 0

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
        
        btn = Button((100, 30), 'options', func=menu, args=[game_options_menu], kwargs={'args': [self]})
        btn.rect.topright = (width, 0)
        btn.rect.y += 30
        btn.rect.x -= 30
        self.elements['options'] = btn
        
        text = Textbox('', 20, fgcolor=(255, 255, 0))
        text.rect.midtop = self.elements['options'].rect.midbottom
        text.rect.y += 10
        self.elements['round'] = text
        #self.update_round()
        
        text = Textbox('', tsize=100, olcolor=(0, 0, 0), olrad=4)
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
        
        self.coin = [Textbox('tails', 20, fgcolor=(255, 0, 0), olcolor=(0, 0, 0)), Textbox('heads', 20, fgcolor=(0, 255, 0), olcolor=(0, 0, 0)), 
                     Textbox('flip', 20, fgcolor=(255, 255, 0), olcolor=(0, 0, 0))]
        self.dice = [Textbox(str(i + 1), 20, fgcolor=fgcolor, olcolor=(0, 0, 0)) for i, fgcolor in enumerate(gen_colors(6))] + [Textbox('roll', 20, fgcolor=(255, 255, 0), olcolor=(0, 0, 0))]
        self.select = Textbox('selecting', 15, fgcolor=(255, 255, 0), olcolor=(0, 0, 0))

        #for t in self.coin + self.dice + [self.select]:
        #    t.add_outline((0, 0, 0))
            
        t = Textbox('', 40, fgcolor=(255, 255, 0))
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

    def update_scores(self):
        players = sorted(self.players, key=lambda p: p.score, reverse=True)
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
            
            cards = p.landscapes.copy() + p.active_spells.copy()
            if self.status in ('game over', 'new game'):         
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
                tcolor = self.coin[mp.coin].fgcolor
                
            elif mp.dice is not None:
                option = self.dice[mp.dice].message
                tcolor = self.dice[mp.dice].fgcolor
                
            elif mp.selection:
                option = 'select'
                tcolor = (255, 255, 0)
                
            elif mp.is_turn:
                option = 'play'
            
        else:
            option = stat
            
        if b.get_message() != option:
        
            b.textbox.set_fgcolor(tcolor)
            b.update_message(option)
        
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

            info = self.n.recieve_player_info(pid)
            
            p = Player(self, pid, info)
            
            self.players.append(p)
            self.players.sort(key=lambda p: p.pid)
            self.add_panes()

            return p
        
    def remove_player(self, pid):
        if any(p.pid == pid for p in self.players):
            
            p = self.get_player_by_pid(pid)

            self.players.remove(p)
            self.add_panes()
            
            SPRITESHEET.remove_player_card(p.name)
            
            if pid == 0: 
                self.exit()
                menu(notice, args=['The host has closed the game.'], overlay=True)   
            elif self.mode != 'single':
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
        r = self.elements['round']
        if r.get_message():
            r.clear()
        else: 
            self.update_round()
        
    def new_round(self):
        for p in self.players:
            p.new_round()
            
        self.shop.clear()
        self.elements['round'].clear()
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
        name = SAVE.get_data('username')
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
            
            if self.status == 'playing':
                self.frame += 1

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
                c.set_olcolor((255, 0, 0))
                s = c.rect.center
                others = self.find_card(c)
                
                for o in others:
                
                    self.lines.append((s, o.rect.center))
                    
                break
                
        else:
        
            if self.outlined_card:
                self.outlined_card.set_olcolor(None)
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
        self.update_scores()
            
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
        self.screen.fill((0, 0, 0))

        for t in self.targets.values():
            self.screen.blit(t.textbox.get_image(), t.rect)
            
            for p in t.points:
                self.screen.blit(p.image, p.rect)
                
            for c in t.cards:
                self.screen.blit(c.get_image(), c.rect)
   
        for e in self.player_spots:
            e.draw(self.screen)
            
        for e in self.elements.values():
            e.draw(self.screen)
           
        if self.outlined_card:
            self.screen.blit(self.outlined_card.get_image(), self.outlined_card.rect)
              
        for s, e in self.lines:
            pg.draw.line(self.screen, (255, 0, 0), s, e, 5)
            
        for p in self.points:
            p.draw(self.screen)
  
        if self.moving_cards:
            for c in self.moving_cards[:5]:
                self.screen.blit(c.get_image(scale=c.get_scale()), c.rect)
            
        for e in self.effects:
            e.draw(self.screen)
            
        draw_particles(self.screen, self.particles)
        
        if self.view_card:
            self.screen.blit(self.view_card.get_image(scale=(card_width, card_height)), self.view_card_rect)

        pg.display.flip()
       
#server stuff-----------------------------------------------------------------------------
  
    def send(self, data, threaded=True, return_val=False):
        if self.playing:
            
            #if threaded and self.r'online':
            #    reply = self.n.threaded_send(data, return_val=return_val)  
            #else:
            reply = self.n.send(data)
            
            if reply is None:
                self.playing = False 
            else:
                return reply

    def get_settings(self):
        return self.send('settings', threaded=False)
        
    def update_settings(self, settings):
        if self.get_status() in ('waiting', 'start', 'new game'):
            self.send('us')
            menu(notice, args=['Settings saved!'], overlay=True)
        else:
            menu(notice, args=['Cannot change settings in the middle of a game.'], overlay=True)
            
    def new_settings(self, settings):
        self.settings = settings
        
    def disconnect(self):
        new_message('disconnecting...', 1000)
        self.exit()
        
    def get_info(self):
        logs = self.send('info', return_val=True)
        if logs:
            self.log_queue += logs

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
                    
                elif type == 'set':
                    self.new_settings(log.get('settings'))
                    
            else:
                p = self.get_player_by_pid(pid)
                
                if type == 'play':
                    p.play(Card(name, uid))
                    
                elif type == 'score':
                    p.update_score(log['score'])
                    
                elif type in ('gp', 'lp', 'give', 'sp'):
                    self.points_queue.append((p, log))
                    
                elif type == 'nd':
                    p.new_deck(log.get('deck'), log.get('cards'))
                    
                elif type == 'disc':
                    p.discard(name, uid, log.get('tags'))
                    
                elif type == 'cast':
                    p.cast(Card(name, uid), self.get_player_by_pid(log.get('target')))
                    
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
                
            textbox = Textbox(message, tsize=30, fgcolor=color, olcolor=(0, 0, 0)) 

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
                
                    if p0.rect.colliderect(p1.rect) and p0.target == p1.target:
                        
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
                        p0.set_fgcolor(tcolor)
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
            text.set_fgcolor(w.color)
            text.update_message(f'{w.name} wins!')
            self.add_particles(2000, 0, w.color, text.rect)
            
        else:
            
            colors = [w.color for w in winners]
            
            message = f'{len(winners)} way tie!'
            while len(message.replace(' ', '')) < len(winners):
                message += '!'
            
            text.update_message(message)
            text.render_multicolor(colors)

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
            
            if uid == c.uid and SPRITESHEET.check_name(c.name):
                
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        