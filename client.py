import random, colorsys

import pygame as pg

import save
import ui
import ui_extended as uie
import spritesheet

from constants import *
from particles import *

def init():
    globals()['SAVE'] = save.get_save()
    globals()['SPRITESHEET'] = spritesheet.get_sheet()
    Visuals.class_init()
    
Moving_Textbox = ui.Textbox.get_moving()

#menus-----------------------------------------------------------------

class Visuals:
    COIN = None
    DICE = None
    SELECT = None
    VOTE = None
    
    PLAYER_SPOTS = None
    
    GAME_START = None
    
    @classmethod
    def class_init(cls):
        cls.COIN = [ui.Textbox('tails', fgcolor=(255, 0, 0), olcolor=(0, 0, 0)), 
                    ui.Textbox('heads', 20, fgcolor=(0, 255, 0), olcolor=(0, 0, 0)), 
                    ui.Textbox('flip', fgcolor=(255, 255, 0), olcolor=(0, 0, 0))]
        cls.DICE = [ui.Textbox(str(i + 1), fgcolor=fgcolor, olcolor=(0, 0, 0)) for i, fgcolor in enumerate(gen_colors(6))] + [ui.Textbox('roll', fgcolor=(255, 255, 0), olcolor=(0, 0, 0))]
        cls.SELECT = ui.Textbox('selecting', tsize=15, fgcolor=(255, 255, 0), olcolor=(0, 0, 0))
        cls.VOTE = {'rotate':  ui.Textbox('rotate', tsize=15, fgcolor=(255, 255, 0), olcolor=(0, 0, 0)), 
                    'keep':  ui.Textbox('keep', tsize=15, fgcolor=(255, 255, 0), olcolor=(0, 0, 0))}
        
        cls.PLAYER_SPOTS = [Player_Spot() for _ in range(16)]
        
        cls.GAME_START = {'game': Moving_Textbox('game ', tsize=70), 'start': Moving_Textbox('start!', tsize=70)}
        
    @classmethod
    def get_player_spot(cls, pid):
        return cls.PLAYER_SPOTS[pid]
        
    @classmethod
    def reset_spots(cls):
        for w in cls.PLAYER_SPOTS:
            w.reset()

def game_options_menu(client):
    objects = []

    b = ui.Button.text_button('disconnect', tag='break', func=client.disconnect)
    b.rect.midtop = (width // 2, height // 2)
    objects.append(b)
    
    b = ui.Button.text_button('game settings', func=ui.Menu.build_and_run, args=[game_settings_menu, client])
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    if client.is_host():

        b = ui.Button.text_button('new game', tag='break', func=client.send, args=['reset'])
        b.rect.midtop = objects[-1].rect.midbottom
        objects.append(b)
        
    b = ui.Button.text_button('back', tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    ui.Position.center_objects_y(objects)

    return objects

def game_settings_menu(client):
    objects = []

    settings = client.get_settings()

    space = 70
    x0 = (width // 2) - space
    x1 = x0 + (2 * space)
    
    t = ui.Textbox.static_textbox('rounds: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('starting score: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('starting cards: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('starting items: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('starting spells: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('number of cpus: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = ui.Textbox.static_textbox('cpu difficulty: ')
    t.rect.centerx = x0
    objects.append(t)
    
    ui.Position.center_objects_y(objects)
    row_sep = len(objects)
    
    c = ui.Flipper.counter(range(1, 6), index=settings['rounds'] - 1, size=(50, 25))
    c.set_tag('rounds')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(5, 51), index=settings['ss'] - 5, size=(50, 25))
    c.set_tag('ss')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(1, 11), index=settings['cards'] - 1, size=(50, 25))
    c.set_tag('cards')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(0, 6), index=settings['items'], size=(50, 25))
    c.set_tag('items')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(0, 4), index=settings['spells'], size=(50, 25))
    c.set_tag('spells')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(1, 15), index=settings['cpus'] - 1, size=(50, 25))
    c.set_tag('cpus')
    c.rect.centerx = x1
    objects.append(c)

    c = ui.Flipper.counter(range(0, 5), index=settings['diff'], size=(50, 25))
    c.set_tag('diff')
    c.rect.centerx = x1
    objects.append(c)
    
    ui.Position.center_objects_y(objects[row_sep:])

    counters = [c for c in objects if isinstance(c, ui.Flipper)]
    
    if not client.is_host():
        for c in counters:
            c.set_enabled(False)
    else:
        b = ui.Button.text_button('save', size=(100, 25), func=save_game_settings, args=[client, counters])
        b.set_tag('break')
        b.rect.midtop = objects[-1].rect.midbottom
        b.rect.y += b.rect.height
        b.rect.centerx = width // 2
        objects.append(b)
        
    b = ui.Button.text_button('back', size=(100, 25))
    b.set_tag('break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.centerx = width // 2
    objects.append(b)

    return objects

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
    settings = {c.tag: c.get_current_tag() for c in counters}  
    SAVE.set_data('settings', settings)
    client.update_settings(settings)
    
#-----------------------------------------------------------------------------------

class Player_Spot(ui.Live_Window.get_moving()):
    SIZE = ((cw * 3) + 18, ch * 6)
    def __init__(self):
        self.player = None

        super().__init__(Player_Spot.SIZE, label='', text_kwargs={'olcolor': (0, 0, 0), 'width': 1})

        self.target = ui.Position(rect=pg.Rect(0, 0, 20, 20), parent_rect=self.label_rect.rect, anchor_point='topright', offset=[5, 5])
        self.view_card_rect = ui.Position(rect=pg.Rect(0, 0, card_width // 5, card_height // 5), parent_rect=self.rect, anchor_point='midtop')
        self.card_rect = ui.Position(rect=pg.Rect(0, 0, cw, ch), parent_rect=self.rect, anchor_point='midtop')
        self.original_rect = self.rect.copy()
        self.set_children([self.target, self.view_card_rect, self.card_rect])

        ongoing = uie.Alt_Static_Window((cw + 6, Player_Spot.SIZE[1]), color=(0, 0, 0, 0), hide_label=True)
        played = uie.Alt_Static_Window((cw + 6, Player_Spot.SIZE[1]), color=(0, 0, 0, 0), hide_label=True)
        active_card = uie.Alt_Static_Window((cw + 6, ch + 10), color=(0, 0, 0, 0), hide_label=True)
        self.sub_windows = {'ongoing': ongoing, 'played': played, 'active_card': active_card}
        self.join_objects([ongoing, played, active_card], xpad=0, ypad=0, dir='x', pack=True)
        
    def __str__(self):
        return f'{self.player.name} spot'
        
    def __repr__(self):
        return f'{self.player.name} spot'
        
    def set_player(self, player):
        self.player = player
        self.label.set_message(player.name)
        self.label_color = player.color
        for _, win in self.sub_windows.items():
            win.image.fill((0, 0, 0))
            win.image = ui.Image_Manager.rect_outline(win.image, player.color, width=3)
        
    def set_original_rect(self):
        if self.target_rect:
            self.original_rect = self.target_rect.copy()
        else:
            self.original_rect = self.rect.copy()
    
    def reset(self):
        self.clear()
        self.resize(Player_Spot.SIZE[1])
        
    def clear(self):
        for w in self.objects:
            w.clear()
            
    def resize(self, h):
        for w in self.objects[:2]:
            w.resize(h=h)
        super().resize(h=h)
        
    def get_target(self):
        return self.target

    def get_cards(self):
        return [c for w in self.objects for c in w.objects]
        
    def get_visible(self):
        return [c for c in self.objects if self.rect.clip(c.rect).height // 2 > c.rect.height // 3]

    def add_cards(self, win, cards):
        win = self.sub_windows[win]
        win.join_objects(cards)
        return win.get_visible()
        
    def update(self):
        super().update()
        self.update_children()

    def draw(self, surf):
        super().draw(surf)
            
        c = self.objects[2].rect.center
            
        if self.player.coin is not None:
            img = Visuals.COIN[self.player.coin].get_image()
            r = img.get_rect()
            r.center = c
            surf.blit(img, r)
            
        elif self.player.dice is not None:
            img = Visuals.DICE[self.player.dice].get_image()
            r = img.get_rect()
            r.center = c
            surf.blit(img, r)
            
        elif self.player.selection:
            img = Visuals.SELECT.get_image()
            r = img.get_rect()
            r.center = c
            surf.blit(img, r)
            
        elif self.player.vote is not None:
            img = Visuals.VOTE[self.player.vote].get_image()
            r = img.get_rect()
            r.center = c
            surf.blit(img, r)

class Player:
    def __init__(self, client, pid, color, info, spot):
        self.client = client
        
        self.pid = pid
        self.name = info['name']
        self.color = color
        info['color'] = self.color
        self.info = info
        SPRITESHEET.add_extra(self.info)
        self.spot = spot
        spot.set_player(self)

        self.target = pg.Rect(0, 0, 20, 20)

        self.score = -1
        self.score_card = ui.Textbox('', fgcolor=self.color)
        self.update_score(0)
        
        self.coin = None
        self.dice = None
        self.timer = 0
        self.frt = 0
        
        self.vote = None
        
        self.flipping = False
        self.rolling = False
        self.gone = True
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
        
    def set_spot(self, spot):
        self.spot = spot
        
    def update_score(self, score):
        if self.score != score:
            self.score = score
            self.score_card.set_message(f'{self.name}: {self.score}')
            self.score_card.fit_text(pg.Rect(0, 0, self.client.objects_dict['scores_window'].rect.width, self.score_card.rect.height))
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
        self.vote = None
        
        self.flipping = False
        self.rolling = False
        self.gone = False
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
        
    def get_cards(self):
        return [self.played, self.unplayed, self.items, self.selection, self.selected, self.equipped, self.ongoing, self.treasure, self.spells, self.landscapes]

    def get_extra_cards(self):
        return sorted(self.items + self.equipped, key=lambda c: c.uid) + self.spells + self.treasure

    def get_spot(self):
        return self.spot

    def play(self, c):  
        self.gone = True
        self.client.add_moving_card(self, original=c)
        sound = SPRITESHEET.get_sound(c.name)
        if sound:
            sound.play()
         
    def new_deck(self, deck_name, cards):
        deck = getattr(self, deck_name)
        new_deck = []
        for name, uid in cards:
            for c in deck:
                if c.uid == uid:
                    break
            else:
                c = Card(name, uid)
            new_deck.append(c)
        setattr(self, deck_name, new_deck)

        if deck_name == 'selection' and self is self.client.main_p:
            
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
        self.rolling = False
        self.dice = dice - 1
        self.timer = timer

    def draw(self, deck, num):
        #for _ in range(num):
        #    
        #    self.client.add_moving_card(self, type='back')
        pass
        
    def set_vote(self, v):
        self.vote = v
        
    def start_turn(self):
        self.gone = False
        self.vote = None

class Card(ui.Position, ui.Mover):
    def __init__(self, name, uid, color=None, olcolor=None):
        self.name = name
        self.uid = uid
        self.color = color
        self.olcolor = olcolor

        ui.Position.__init__(self, rect=pg.Rect(0, 0, cw, ch))
        ui.Mover.__init__(self)
 
    def __eq__(self, other):
        return self.uid == other.uid and self.name == other.name
        
    def __repr__(self):
        return self.name
        
    def set_visible(self, _):
        pass
        
    def set_enabled(self, _):
        pass
        
    def copy(self):
        c = Card(self.name, self.uid, color=self.color, olcolor=self.olcolor)
        c.rect = self.rect.copy()
        return c
        
    def set_color(self, color):
        self.color = color
        
    def set_olcolor(self, olcolor):
        self.olcolor = olcolor
        
    def get_image(self, scale=(cw, ch)):
        return SPRITESHEET.get_image(self.name, scale=scale, olcolor=self.olcolor)
        
    def get_med_image(self):
        img = self.get_image(scale=(cw * 1.4, ch * 1.4))
        i = ui.Image(img)
        i.rect.center = self.rect.center
        return i
        
    def update_info(self, name, uid):
        self.name = name
        self.uid = uid
        
    def update(self):
        self.move()

    def draw(self, surf): 
        surf.blit(self.get_image(), self.rect)
    
class Client(ui.Menu):        
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

        self.pid = self.send('pid')
        print(self.pid)
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
        self.moving_objects = []
        self.effects = []
        self.particles = []
        self.shop = []

        self.loop_times = []
        
        Visuals.reset_spots()
        self.objects_dict = {}
        self.player_spots = []
        super().__init__(get_objects=self.client_objects)

        self.targets = {}
        self.points_queue = []
        self.points = []
        
        self.view_card_rect = pg.Rect(0, 0, 375, 525)
        self.view_card_rect.center = (width // 2, height // 2)

        for pid in range(self.pid, -1, -1):
            p = self.add_player(pid)    
            if pid == self.pid:
                self.main_p = p

    def client_objects(self):
        objects = []
        ph = ch * 6

        sequence_window = ui.Static_Window((cw * 1.5, ph), label='your sequence', color=(255, 0, 0))
        sequence_window.rect.bottomleft = (20, height - 20)
        objects.append(sequence_window)
        self.objects_dict['sequence_window'] = sequence_window

        selection_window = ui.Static_Window((cw * 1.5, (ch * 5) + 30), label='selection', color=(0, 0, 255))
        selection_window.rect.bottomright = (width - 20, height - 20)
        objects.append(selection_window)
        self.objects_dict['selection_window'] = selection_window
        
        cancel_button = ui.Button.text_button('x', fgcolor=(255, 0, 0), func=self.send, args=['cancel'], color2=(0, 0, 0))
        cancel_button.rect.center = (-50, -50)
        objects.append(cancel_button)
        self.objects_dict['cancel_button'] = cancel_button
        
        active_card_window = ui.Static_Window((cw * 1.5, ch * 1.5), label='active card', color=(255, 255, 255))
        active_card_window.rect.bottomright = selection_window.rect.bottomleft
        active_card_window.rect.x -= 10
        objects.append(active_card_window)
        self.objects_dict['active_card_window'] = active_card_window
        
        extra_cards_window = ui.Popup_Base((cw * 10, ch * 4), label='extra cards', color=(0, 0, 0))
        extra_cards_window.rect.x = sequence_window.rect.right + 10
        extra_cards_window.rect.y = height
        objects.append(extra_cards_window)
        self.objects_dict['extra_cards_window'] = extra_cards_window
        
        main_button = ui.Button.text_button('', size=(100, 35), tsize=30, fgcolor=(0, 255, 0), func=self.main_button)
        main_button.set_enabled(False)
        main_button.rect.midbottom = (width // 2, height)
        main_button.rect.y -= 10
        objects.append(main_button)
        self.objects_dict['main_button'] = main_button
        
        shop_window = ui.Static_Window(((cw * 3) + 20, ch + 10), label='shop', color=(255, 255, 0))
        shop_window.rect.bottomright = active_card_window.rect.bottomleft
        shop_window.rect.x -= 10
        objects.append(shop_window)
        self.objects_dict['shop_window'] = shop_window

        options_button = ui.Button.text_button('options', func=ui.Menu.build_and_run, args=[game_options_menu, self])
        options_button.rect.topright = (width, 0)
        options_button.rect.y += 30
        options_button.rect.x -= 30
        objects.append(options_button)
        self.objects_dict['options_button'] = options_button
        
        round_text = ui.Textbox('', fgcolor=(255, 255, 0))
        round_text.rect.midtop = options_button.rect.midbottom
        round_text.rect.y += 10
        objects.append(round_text)
        self.objects_dict['round_text'] = round_text
        
        winner_text = ui.Textbox('', tsize=100, olcolor=(0, 0, 0), width=4)
        winner_text.rect.center = (width // 2, height // 2)
        objects.append(winner_text)
        self.objects_dict['winner_text'] = winner_text

        discard_window = ui.Static_Window((cw, ch * 1.5), label='item discard')
        discard_window.rect.midbottom = selection_window.rect.midtop
        discard_window.rect.y -= 30
        objects.append(discard_window)
        self.objects_dict['discard_window'] = discard_window
        
        event_window = ui.Static_Window((cw, ch * 1.5), label='event')
        event_window.rect.centerx = active_card_window.rect.centerx
        event_window.rect.y = discard_window.rect.y
        objects.append(event_window)
        self.objects_dict['event_window'] = event_window
        
        scores_window = uie.Alt_Static_Window((cw * 2, ch * 3), label='scores')
        scores_window.rect.topleft = (20, 40)
        objects.append(scores_window)
        self.objects_dict['scores_window'] = scores_window

        message_box = ui.Textbox('', tsize=40, fgcolor=(255, 255, 0))
        message_box.rect.center = (width // 2, height // 2)
        objects.append(message_box)
        self.objects_dict['message_box'] = message_box
        
        game_text = Moving_Textbox('Game ', tsize=100)
        game_text.rect.midright = (0, height // 2)
        r = game_text.rect.copy()
        r.midright = (width // 2, height // 2)
        start = {'target_rect': r, 'p': (0, height // 2), 'v': 70, 'end_timer': 30}
        end = {'target_rect': game_text.rect.copy(), 'v': 50}
        game_text.set_animation([start, end])
        objects.append(game_text)
        
        start_text = Moving_Textbox('Start!', tsize=100)
        start_text.rect.midleft = (width, height // 2)
        r = start_text.rect.copy()
        r.midleft = (width // 2, height // 2)
        start = {'target_rect': r, 'p': (width, height // 2), 'v': 70, 'end_timer': 30}
        end = {'target_rect': start_text.rect.copy(), 'v': 50}
        start_text.set_animation([start, end])
        objects.append(start_text)
        
        self.objects_dict['game_start_text'] = (game_text, start_text)
        
        rotate_text = Moving_Textbox('Rotate!', tsize=100)
        rotate_text.rect.midbottom = (width // 2, 0)
        r = rotate_text.rect.copy()
        r.center = (width // 2, height // 2)
        start = {'target_rect': r, 'p': rotate_text.rect.center, 'v': 70, 'end_timer': 30}
        r = r.move(0, height // 2 + r.height)
        end = {'target_rect': r, 'v': 70}
        rotate_text.set_animation([start, end])
        objects.append(rotate_text)
        self.objects_dict['rotate_text'] = rotate_text
        
        return objects
      
    def is_host(self):
        return self.pid == 0
                
    def get_event_objects(self):
        objects = self.objects.copy()
        for ps in self.player_spots:
            objects += [ps] + ps.objects
        return objects

#startup stuff-----------------------------------------------------------------------------                
 
    def organize_screen(self):
        num = len(self.players)
        
        w = (self.objects_dict['selection_window'].rect.left - self.objects_dict['sequence_window'].rect.right) - 50
        h = height
        r = pg.Rect(0, 0, w, h)
        r.top = 50
        r.left = self.objects_dict['sequence_window'].rect.right
        
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

        for i, p in enumerate(self.players):

            ps = p.spot
            ps.resize(ph)
            ps.rect.topleft = (x, y)

            if ps.rect.right > r.right:
                
                x0 = row_rect.x
                row_rect.centerx = r.centerx
                dx = row_rect.x - x0

                for s in row:
                    s.rect.x += dx

                y += ps.rect.height + ps.label_rect.rect.height + 20
                x = r.left + 50
                
                ps.rect.topleft = (x, y)
                
                row.clear()
                
                row_rect.width = 0
                row_rect.topleft = (x, y)
    
            row_rect.width = ps.rect.right - row_rect.x

            row.append(ps)
            
            x += ps.rect.width + 25
            
        x0 = row_rect.x
        row_rect.centerx = r.centerx
        dx = row_rect.x - x0
            
        for ps in row:      
            ps.rect.x += dx
            ps.set_original_rect()

    def add_player(self, pid):
        if not any({p.pid == pid for p in self.players}):
            
            ps = Visuals.get_player_spot(pid)
            self.player_spots.append(ps)
            
            info = self.n.recieve_player_info(pid)
            p = Player(self, pid, self.colors[pid], info, ps)
            self.players.append(p)
            self.players.sort(key=lambda p: p.pid)

            self.organize_screen()

            return p
            
    def remove_player(self, pid):
        if any({p.pid == pid for p in self.players}):
            p = self.get_player(pid)
            
            ps = p.spot
            self.player_spots.remove(ps)

            self.players.remove(p)
            SPRITESHEET.remove_extra(p.name)
            
            self.organize_screen()
            
            if pid == 0: 
                self.exit()
                menu = ui.Menu.notice('The host has closed the game.', overlay=True)   
                menu.run()
            elif self.mode != 'single':
                menu = ui.Menu.timed_message(f'{p.name} has left the game', 60, overlay=True)   
                menu.run()

    def reset(self):
        for o in self.objects:
            if isinstance(o, ui.Static_Window):
                o.clear()
            
        for ps in self.player_spots:
            ps.clear()
            #ps.cancel_move()
            ps.set_original_rect()
            
        for p in self.players:
            p.reset()

        self.cards.clear()
        self.shop.clear()
        self.points.clear()
        self.moving_cards.clear()
        self.moving_objects.clear()
        self.event = None
        self.last_item = None

        self.objects_dict['winner_text'].clear()

        self.round = 1
        r = self.objects_dict['round_text']
        if r.get_message():
            r.clear()
        else: 
            self.update_round()
        
    def new_round(self):
        for p in self.players:
            p.reset()
            
        self.shop.clear()
        self.objects_dict['round_text'].clear()
        self.objects_dict['winner_text'].clear()
        
        self.round += 1
        self.update_round()
        
    def update_round(self):
        self.objects_dict['round_text'].set_message(f"round {self.round}/{self.get_settings()['rounds']}")

    def quit(self):
        self.n.close()
        self.playing = False
        super().quit()
        
    def exit(self):
        self.n.close()
        self.playing = False   

#main loop-----------------------------------------------------------------------------

    def run(self):
        while self.playing:
        
            self.clock.tick(30)
            #print(self.clock.get_fps())

            self.get_info()
            self.update_info()
            if self.playing:
                self.events()
            if self.playing:
                self.update()
                self.draw()

    def events(self):   
        events = self.get_events()
        
        p = events['p']
        q = events.get('q')
        kd = events.get('kd')
        ku = events.get('ku')
        mbd = events.get('mbd')
        mbu = events.get('mbu')

        if q:
            self.quit()
            
        elif kd:
            if kd.key == pg.K_ESCAPE:
                self.quit()
            elif kd.key == pg.K_s and self.is_host():
                self.send('start') 
            elif kd.key == pg.K_p:
                self.send('play')        
            elif kd.key == pg.K_x:
                self.send('cancel')
            elif kd.key == pg.K_LALT or kd.key == pg.K_RALT:
                for c in self.cards:
                    if c.rect.collidepoint(p):
                        self.view_card = c
                        break

        elif ku:
            if ku.key == pg.K_LALT or ku.key == pg.K_RALT:
                self.view_card = None
                
        elif mbd:
            if mbd.button == 1:
                for c in self.cards:
                    if c.rect.collidepoint(p):
                        self.send(str(c.uid))
                        break
                if self.moving_cards:
                    self.moving_cards.pop(0)
            elif mbd.button == 3:
                for c in self.cards:
                    if c.rect.collidepoint(p):
                        self.view_card = c
                        break
                        
        elif mbu:
            if mbu.button == 3:
                self.view_card = None
               
        super().sub_events(events)
          
        self.lines.clear()

        for c in self.cards:
            if c.rect.collidepoint(p):     
                self.outlined_card = c.get_med_image()
                #s = c.rect.center
                #others = Card.ALL_CARDS
                #for o in others:
                #    if c == o and c is not o:
                #        self.lines.append((s, o.rect.center)) 
                break
                
        else:
            if self.outlined_card:
                self.outlined_card = None
                        
    def update(self):  
        self.set_option()
        
        for o in self.objects: 
            o.update()
        for ps in self.player_spots:
            ps.update()
        for o in self.moving_objects.copy():
            o.update()
            if o.finished_move():
                self.moving_objects.remove(o)

        for p in self.players: 
            p.update()
            
        self.update_windows()
        self.unpack_points()
        self.update_scores()
            
        for p in self.points.copy():
            p.update()
            if p.finished_move():
                self.points.remove(p)
        self.collide_points()
    
        for c in self.main_p.equipped:
            if c.rect.colliderect(self.camera) and c in self.cards:
                self.add_particles(2, 1, self.main_p.color, rect=c.rect)

        for c in self.moving_cards:
            c.update()
            if c.finished_move():
                self.moving_cards.remove(c)
    
        #for p in self.players:
        #    if not p.vote:
        #        self.add_particles(2, 1, p.color, p.spot.rect)
                
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

        for ps in self.player_spots:
            ps.draw(self.screen)
        for o in self.objects:
            o.draw(self.screen)
        for o in self.moving_objects:
            o.draw(self.screen)
           
        if self.outlined_card:
            self.outlined_card.draw(self.screen)
              
        for s, e in self.lines:
            pg.draw.line(self.screen, (255, 0, 0), s, e, 5)
            
        for p in self.points:
            p.draw(self.screen)
  
        if self.moving_cards:
            for c in self.moving_cards:
                self.screen.blit(c.get_image(scale=c.get_scale()), c.rect)
            
        for e in self.effects:
            e.draw(self.screen)
            
        draw_particles(self.screen, self.particles)
        
        if self.view_card:
            self.screen.blit(self.view_card.get_image(scale=(card_width, card_height)), self.view_card_rect)

        pg.display.flip()
   
#server stuff-----------------------------------------------------------------------------
  
    def send(self, data, thread=False, func=None):
        if self.playing:
            
            if thread:
                reply = self.n.queue_data(data, func=func)
            else:
                reply = self.n.send(data)
                
            if reply is None:
                self.playing = False 
            else:
                return reply

    def get_settings(self):
        return self.send('settings')
        
    def update_settings(self, settings):
        if self.get_status() in ('waiting', 'start', 'new game'):
            self.send('us')
            menu = ui.Menu.timed_message('Settings saved!', 30, overlay=True)
        else:
            menu = ui.Menu.notice('Cannot change settings during a game.', overlay=True)
        menu.run()
            
    def new_settings(self, settings):
        self.settings = settings
        
    def disconnect(self):
        menu = ui.Menu.timed_message('disconnecting...', 20)
        menu.run()
        self.exit()
        
    def get_info(self):
        logs = self.send('info')
        if logs:
            self.log_queue += logs

    def update_info(self):
        self.parse_logs(self.log_queue[:5])
        self.log_queue = self.log_queue[5:]
            
    def parse_logs(self, logs):
        points = []

        for log in logs:
            
            pid = log.get('u')
        
            type = log.get('t')
            if 'c' in log:
                name, uid = log.get('c')
            
            if pid == 'g':
                    
                if type == 'add':
                    self.add_player(log.get('pid'))

                elif type == 'del':
                    self.remove_player(log.get('pid'))
                    
                elif type == 'ord':
                    self.reorder(log.get('ord'))
                    
                elif type == 'fin':
                    self.win_objects(log.get('w'))
                    
                elif type == 'res':
                    self.reset()
                    
                elif type == 'nt':
                    self.new_turn()
                    
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
                    
                elif type == 'v':
                    self.new_vote(log['v'])
                    
            else:
                p = self.get_player(pid)
                
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
                    p.cast(Card(name, uid), self.get_player(log.get('target')))
                    
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
                    
                elif type == 'v':
                    p.set_vote(log['v'])
                      
    def unpack_points(self):
        for info in self.points_queue.copy():
            
            player, pack = info
        
            uid = pack.get('c')[1]
            type = pack.get('t')
            target = self.get_player(pack.get('target'))
            
            startup_timer = 30
            
            if pack.get('d'):
                self.points_queue.remove(info)
                continue
                
            if any({c.uid == uid for c in self.moving_cards}):
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
                
            textbox = Moving_Textbox(message, tsize=30, fgcolor=color, olcolor=(0, 0, 0)) 

            if type == 'sp':
                s = target.spot.target.rect.center
                t = player.spot.target.rect
                startup_timer = 0
                
            elif type == 'give':
                s = player.spot.target.rect.center
                t = target.spot.target.rect
                startup_timer = 0
                
            elif type == 'gp' or type == 'lp':
                card = self.find_uid(uid)
                if card:
                    s = card.rect.center 
                else: 
                    s = player.spot.target.rect.center
                t = player.spot.target.rect
           
            else:
                self.points_queue.remove(info)
                continue

            textbox.set_target_rect(t, v=10, startup_timer=startup_timer, end_timer=100, p=s)
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
                
                    if p0.rect.colliderect(p1.rect) and p0.target_rect == p1.target_rect:
                        
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
                            
                        p0.set_message(message)
                        p0.set_fgcolor(tcolor)
                        p0.reset_timer()
                        
                        self.points.remove(p1)
                        removed.append(p1)
    
    def fill_shop(self, cards):
        self.shop.clear()
        for name, uid in cards:           
            self.shop.append(Card(name, uid))
       
#objects stuff-----------------------------------------------------------------------------------

    def new_message(self, message, timer=60):
        self.objects_dict['message_box'].set_message_timer(message, timer)
            
#pane stuff --------------------------------------------------------------------------------------------------------------

    def update_scores(self):
        players = sorted(self.players, key=lambda p: p.score, reverse=True)
        objects = [p.score_card for p in players]
        self.objects_dict['scores_window'].join_objects(objects, force=True)

    def update_windows(self):
        self.cards.clear()
        
        if self.last_item:
            self.objects_dict['discard_window'].join_objects([self.last_item])
            self.cards.append(self.last_item)
        elif self.objects_dict['discard_window']:
            self.objects_dict['discard_window'].clear()

        if self.event:
            self.objects_dict['event_window'].join_objects([self.event])
            self.cards.append(self.event)
        elif self.objects_dict['event_window']:
            self.objects_dict['event_window'].clear()
        
        if self.shop:
            self.objects_dict['shop_window'].join_objects(self.shop, dir='x')
            self.cards += self.objects_dict['shop_window'].get_visible()
        elif self.objects_dict['shop_window']:
            self.objects_dict['shop_window'].clear()

        for p in self.players:
            ps = p.spot
            
            if p.played:
                ps.sub_windows['played'].join_objects(p.played)
                self.cards += ps.sub_windows['played'].get_visible()
            elif ps.sub_windows['played']:
                ps.sub_windows['played'].clear()
                
            if p.active_card:
                ps.sub_windows['active_card'].join_objects([p.active_card])
                self.cards.append(p.active_card)
            elif ps.sub_windows['active_card']:
                ps.sub_windows['active_card'].clear()

            ongoing = p.landscapes + p.active_spells
            if self.status in ('game over', 'new game'):         
                ongoing += [c.copy() for c in p.treasure] 
            if ongoing:
                ps.sub_windows['ongoing'].join_objects(ongoing)
                self.cards += ps.sub_windows['ongoing'].get_visible()
            elif ps.sub_windows['ongoing']:
                ps.sub_windows['ongoing'].clear()

            if p == self.main_p:
                
                if p.unplayed:
                    self.objects_dict['sequence_window'].join_objects(p.unplayed)
                    self.cards += self.objects_dict['sequence_window'].get_visible()
                elif self.objects_dict['sequence_window']:
                    self.objects_dict['sequence_window'].clear()
                    
                extra_cards = p.get_extra_cards()
                if extra_cards:
                    self.objects_dict['extra_cards_window'].join_objects(extra_cards, dir='x', pack=True, move=True)
                    self.cards += self.objects_dict['extra_cards_window'].get_visible()
                elif self.objects_dict['extra_cards_window']:
                    self.objects_dict['extra_cards_window'].clear()

                if p.selection:
                    self.objects_dict['selection_window'].join_objects(p.selection)
                    self.cards += self.objects_dict['selection_window'].get_visible()
                elif self.objects_dict['selection_window']:
                    self.objects_dict['selection_window'].clear()
                    
                if p.active_card:
                    self.objects_dict['active_card_window'].join_objects([p.active_card])
                    self.cards.append(p.active_card)
                elif self.objects_dict['active_card_window']:
                    self.objects_dict['active_card_window'].clear()
                
        self.cards += self.moving_cards

    def add_moving_card(self, player, original=None, type='zoom'):
        if type == 'zoom':
            
            c = original.copy()

            sequence = [{'target_rect': player.spot.view_card_rect.rect, 'v': 100, 'end_timer': 30, 'scale': True},
                        {'target_rect': original.rect, 'v': 50, 'scale': True}]
                       
            c.set_animation(sequence, start=True)
            c.color = player.color
            self.moving_cards.append(c)
     
        elif type == 'back':
            
            c = Card('back', -1)
            c.rect.bottomright = (width, height)
            c.set_target_rect(player.card_rect, v=30)
            self.moving_cards.append(c)
   
        elif type == 'shuffle':
            
            r = pg.Rect(0, 0, cw * 2, ch * 2)
            r.center = (width // 2, height // 2)
            targets = [ps.target.rect for ps in self.player_spots]
            for c in self.cards[:10]:
                c = c.copy()
                sequence = [{'target_rect': r, 'p': random.choice(targets).center, 'v': 40, 'end_timer': 20, 'scale': True},
                           {'target_rect': random.choice(self.player_spots).rect, 'v': 40}]
                c.set_animation(sequence, start=True)
                self.moving_cards.append(c)
            
        elif type == 'rotate':

            r = pg.Rect(0, 0, cw * 2, ch * 2)
            r.center = (width // 2, height // 2)
            
            for i, ps in enumerate(self.player_spots):
                y = ps.rect.top
                for c in ps.player.unplayed[:4]:
                    c = c.copy()
                    sequence = [{'target_rect': self.player_spots[(i + 1) % len(self.player_spots)].rect, 'p': (ps.rect.centerx, y), 'v': 10}]
                    c.set_animation(sequence, start=True)
                    self.moving_cards.append(c)
                    y += ch

        
#option stuff------------------------------------------------------------------------------
              
    def set_option(self):
        mp = self.main_p
        option = ''
        stat = self.get_status()
        tcolor = (0, 255, 0)
        b = self.objects_dict['main_button']

        if stat == 'playing':
        
            if mp.coin is not None:
                option = Visuals.COIN[mp.coin].message
                tcolor = Visuals.COIN[mp.coin].fgcolor
                
            elif mp.dice is not None:
                option = Visuals.DICE[mp.dice].message
                tcolor = Visuals.DICE[mp.dice].fgcolor
                
            elif mp.selection:
                option = 'select'
                tcolor = (255, 255, 0)
                
            elif not mp.gone and mp.unplayed:
                option = 'play'
            
        else:
            option = stat
            
        if b.object.get_message() != option:
        
            b.object.set_fgcolor(tcolor)
            b.object.set_message(option)
        
            if option in ('play', 'flip', 'roll', 'next round', 'new game', 'start'):
                b.set_enabled(True)               
            else:   
                b.set_enabled(False)
                
            c = self.objects_dict['cancel_button']
                
            if option == 'select' and mp.can_cancel:
                c.rect.topleft = b.rect.topright
            else:
                c.rect.center = (-50, -50)
        
    def is_option(self, option):
        return self.get_option() == option
        
    def get_option(self):
        return self.objects_dict['main_button'].object.get_message()
        
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
        if stat == 'next round':
            if not self.is_host():
                stat = 'round over'
                
        elif stat == 'new game':
            if not self.is_host():
                stat = 'game over'
                
        elif stat == 'waiting':
            if self.mode == 'single' or (self.is_host() and len(self.players) > 1):
                stat = 'start'
                
        else:
            self.objects_dict['game_start_text'][0].start_animation()
            self.objects_dict['game_start_text'][1].start_animation()

        self.status = stat
            
    def get_status(self):
        return self.status
        
    def is_status(self, stat):
        return self.get_status() == stat
        
    def new_vote(self, vote):
        if vote == 'rotate':
            self.objects_dict['rotate_text'].start_animation()
            self.add_moving_card(self.main_p, type='rotate')
            
        elif vote == 'shuffle':
            self.add_moving_card(self.main_p, type='shuffle')

#helper stuff-------------------------------------------------------------------------------
 
    def reorder(self, pids):
        players = []
        
        for pid in pids: 
            p = self.get_player(pid) 
            if p:
                players.append(p)
                
        for p0 in self.players:
            i = players.index(p0)
            p1 = self.players[i]
            p0.spot.set_target_rect(p1.spot.original_rect.copy(), v=50)
        for ps in self.player_spots:
            ps.set_original_rect()

        self.players = players
        
    def win_objects(self, pids):
        winners = []
        
        for pid in pids:
            
            p = self.get_player(pid)
            if p is not None: 
                winners.append(p)
                
        text = self.objects_dict['winner_text']
                
        if len(winners) == 1:
            
            w = winners[0]
            text.set_fgcolor(w.color)
            text.set_message(f'{w.name} wins!')
            self.add_particles(2000, 0, w.color, text.rect)
            
        else:
            
            colors = [w.color for w in winners]
            
            message = f'{len(winners)} way tie!'
            while len(message.replace(' ', '')) < len(winners):
                message += '!'
            
            text.set_message(message)
            text.render_multicolor(colors)

            for c in colors:
                self.add_particles(2000 // len(colors), 0, c, text.rect)
        
    def new_turn(self):
        for p in self.players: 
            p.start_turn()
  
    def set_events(self, name, uid):
        self.event = Card(name, uid)

#-------------------------------------------------------------------------------------------

    def get_scores(self):
        return {p.pid: p.score for p in self.players}

    def get_player(self, pid):
        if type(pid) == str:
            if pid.isnumeric():
                pid = int(pid)
        return next((p for p in self.players if p.pid == pid), None)

    def find_local_card(self, card):
        for c in self.objects_dict['extra_cards_window'].cards:
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
        return any({c.uid == uid for c in self.cards})
        
    def get_target(self, pid):
        return self.targets[pid]
    
    def add_particles(self, num, type, color, rect=None, pos=None):
        self.particles += get_particles(num, type, color, rect, pos)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        