import sys
import random
import time
from settings import settings
from cards import *
from player import Player

def check_int(string): #checks to see if string can be represented as an integer
    try:
        
        int(string)
        
        return True
        
    except ValueError:
        
        return False
    
def count_cards(card, deck): #returns number of specific card in given deck
    return len([c for c in deck if type(c) == card])
        
class Game:
    def __init__(self, mode='online'):
        self.running = True
        
        self.done = False #true when game is over
        
        self.wait = True #true while waiting for players to join
        
        self.settings = settings.copy()
        
        self.uid = 0
        self.pid = 0
        
        self.deck = []
        self.items = []
        self.spells = []
        self.treasure = []
        self.event_cards = []
        self.landscapes = []

        self.discard = []
        
        self.turn = 0 #turn of game

        self.event = None #impliment multiple
        
        self.players = []

        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = None #main player

        self.phase = ''
        
        self.mode = mode #single vs online
        
        if self.mode == 'single':
            
            self.new_player(0)
        
#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        self.players.sort(key=lambda p: p.pid)
    
        if self.mode == 'single':
            
            self.add_cpus()

        self.done = False
        self.phase = 'draft'
        self.uid = len(self.players)
        
        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = self.players[0] #main player
        
        self.deck = self.fill_deck(cards)
        self.items = self.fill_deck(items)
        self.spells = self.fill_deck(spells)
        self.treasure = self.fill_deck(treasure)
        self.event_cards = self.fill_deck(events)
        self.landscapes = self.fill_deck(landscapes)

        self.discard = []
        
        for p in self.players:
        
            p.start()
        
        self.turn = 0 #turn of game
        self.round = 1

        self.deal('items', 'items', self.get_setting('items'))
        self.deal('spells', 'spells', self.get_setting('spells'))

        self.deal('deck', 'selection', self.get_setting('cards'))
        
        if self.get_setting('event'):

            self.event = self.event_cards.pop(random.randrange(len(self.event_cards)))
            
    def add_cpus(self):
        self.pid = 1
        
        self.players = [self.get_player(0)]
            
        for _ in range(self.get_setting('cpus')):

            self.players.append(Player(self, self.pid, self.settings['ss'], auto=True))
        
            self.pid += 1
            
    def reset(self):
        self.done = False
        self.wait = True
        
        self.phase = ''
        
        for p in self.players:
            
            p.reset()
            
        self.players.sort(key=lambda p: p.pid)
        
        return True

    def new_round(self):
        self.phase = 'draft'
        self.done = False
        self.turn = 0
        
        for p in self.players:
            
            p.new_round()

        self.current_player = 0
        self.main_p = self.players[0]

        self.deal('deck', 'selection', self.get_setting('cards'))
        
        if self.get_setting('event'):

            self.event = self.event_cards.pop(random.randrange(len(self.event_cards)))
            
    def fill_deck(self, cards):
        deck = []
        
        for card in cards:
            
            m = cards[card]
            
            if m:
            
                for _ in range(m):
                    
                    deck.append(card(self, self.uid))
                    
                    self.uid += 1
                    
        random.shuffle(deck)

        return deck
        
    def deal(self, deck, destination, num=5):
        for p in self.players:
            
            dest = getattr(p, destination)
            
            dest += self.draw_cards(deck, num)
        
#server communication functions-----------------------------------------------------------------------------

    def new_player(self, pid): #add player to game
        if self.wait:

            p = Player(self, pid, self.settings['ss'])

            self.players.append(p)
                
            self.pid += 1

            return True
            
        else:
            
            return False
            
    def remove_player(self, pid): #remove player from game
        p = next(p for p in self.players if p.pid == pid)
        
        self.players.remove(p)
        
    def start(self, pid):
        if (pid == 0 and len(self.players) > 1) or self.mode == 'single':
            
            self.wait = False
            
            self.new_game()
            
            return True
            
        else:
            
            return False
            
    def get_info(self, player):
        if not self.get_player(0):
            
            return 'close'

        info = {}
        
        for p in self.players:
            
            if p == player:
                
                info[p.pid] = p.get_info()
                
            else:
                
                info[p.pid] = p.get_light_info()
                
        if self.event is not None:
                
            info['e'] = (self.event.name, self.event.uid)
                
        return info
        
    def select(self, pid, uid):
        p = self.get_player(pid)
        
        card = self.find_card(uid, pid)
        
        if self.phase == 'draft':
            
            p.draft(card)
            
            self.check_rotate()
            
        else:
            
            p.update('select', card)
        
        return True
        
    def cancel(self, pid):
        p = self.get_player(pid)
        
        cmd = 'cancel'
        
        p.update(cmd)
        
        return True
        
    def play(self, pid):
        p = self.get_player(pid)

        cmd = 'play'
        
        p.update(cmd)
        
        return True
        
    def info(self, pid):
        return self.get_info(self.get_player(pid))
        
    def get_settings(self):
        return self.settings.copy()
        
    def update_settings(self, setting):
        key, val = setting[1:].split(',')

        if val in (str(True), str(False)):
            
            self.settings[key] = True if val == 'True' else False
            
        else:
            
            self.settings[key] = int(val)
            
        return True
        
    def send(self, data):
        reply = ''
        
        if data == 'info':
                    
            reply = self.info(0)
        
        elif data == 'start':
            
            reply = self.start(0)
            
        elif data == 'reset':
            
            reply = self.reset()
            
        elif data == 'settings':
            
            reply = self.get_settings()
            
        elif '-' == data[0]:
            
            if self.wait:
            
                reply = self.update_settings(data)
                
            else:
                
                reply = False
                
        elif data == 'disconnect':
            
            self.running = False
            
        elif self.wait: #won't go past here if client is waiting to start game
            
            reply = 1

        elif check_int(data):

            reply = self.select(0, int(data))
            
        elif data == 'click':
            
            reply = self.select(0)
            
        elif data == 'play':
            
            reply = self.play(0)
            
        elif data == 'cancel':
            
            reply = self.cancel(0)

        if reply == 'close':
            
            self.running = False
            
        self.main()
            
        return reply
        
    def get_pid(self):
        return 0
        
    def close(self):
        self.running = False
            
#turn stuff-----------------------------------------------------------------------------------------------

    def check_rotate(self):
        if not any(p.selecting for p in self.players) and not self.wait:
            
            self.rotate_selection()

    def rotate_selection(self, dir='cc'):
        if not any(p.selection for p in self.players):
                                    
            self.end_draft()
    
        else:
    
            selections = []
            
            for p in self.players:
            
                selections.append(p.selection)
                
            if dir == 'cc':
            
                selections = selections[1:] + [selections[0]]
                
            else:
                selections = [selections[-1]] + selections[:-1]
                
            for p, s in zip(self.players, selections):
            
                p.new_draft(s)
                
    def end_draft(self):
        self.phase = 'play'
        
        self.event.start(self)

        self.advance_turn()
  
    def check_advance(self):
        if self.main_p.finished:
            
            self.advance_turn()
            
    def finished_game(self):
        return self.round + 1 > self.get_setting('rounds')

    def advance_turn(self):
        self.main_p.end_turn()
        
        if len(self.players) == 1:
            
            return
        
        players = [p for p in self.players if p.unplayed]
        
        if all(p.game_over for p in self.players):
            
            self.round += 1
            
            if self.round <= self.get_setting('rounds'):
            
                self.new_round()
            
            return

        elif not players:
        
            return

        if any(len(p.played) == self.turn for p in players):

            for p in players:
                
                if len(p.played) == self.turn:
        
                    self.current_player = self.players.index(p)

                    break
   
        else:
            
            self.turn += 1
            
            self.current_player = 0
            
            self.advance_turn()
            
        self.main_p = self.players[self.current_player]

        self.main_p.start_turn()
        
    def main(self):
        auto = [p for p in self.players if p.auto]

        for p in auto:
            
            p.auto_update()
        
#player stuff-----------------------------------------------------------------------------------------------
        
    def draw_cards(self, deck='deck', num=1):
        cards = []
        
        deck = getattr(self, deck)
        
        while deck:
        
            for _ in range(num):
                
                card = random.choice(deck)
                
                cards.append(card)
                
                deck.remove(card)
                
            break

        return cards
        
    def check_last(self, player):
        return all(len(p.played) > len(player.played) for p in [x for x in self.players if x.pid != player.pid]) or (self.players[-1] == player)
        
    def check_first(self, player):
        return player.pid == self.players[0].pid and all(len(p.played) == self.turn for p in [x for x in self.players if x.pid != player.pid])
               
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if c.type in ('item', 'equipment')]
        
    def restore(self, c):
        self.discard.remove(c)
        
#card stuff---------------------------------------------------------------------------------------

    def get_event(self):
        return self.event.name if hasattr(self, 'event') else None

    def get_player(self, pid):
        return next((p for p in self.players if p.pid == pid), None)
        
    def get_setting(self, setting):
        return self.settings[setting]
     
    def find_card_deep(self, uid):
        for p in self.players:
        
            for i, c in enumerate(p.unplayed):
                if c.uid == uid:
                    return (p, 'unplayed', i)
                    
            for i, c in enumerate(p.played):
                if c.uid == uid:
                    return (p, 'played', i)
                    
            for i, c in enumerate(p.items):
                if c.uid == uid:
                    return (p, 'items', i)
                    
            for i, c in enumerate(p.equipped):
                if c.uid == uid:
                    return (p, 'equipped', i)
                    
            for i, c in enumerate(p.spells):
                if c.uid == uid:
                    return (p, 'spells', i)
                    
            for i, c in enumerate(p.get_spells()):
                if c.uid == uid:
                    return (p, 'ongoing', i)
                    
    def swap(self, c1, c2):
        i1 = self.find_card_deep(c1.uid)
        i2 = self.find_card_deep(c2.uid)
            
        getattr(i1[0], i1[1])[i1[2]], getattr(i2[0], i2[1])[i2[2]] = getattr(i2[0], i2[1])[i2[2]], getattr(i1[0], i1[1])[i1[2]]
                 
    def find_card(self, uid, pid=None):
        if pid is None:
        
            mp = self.main_p
            
        else:
            
            mp = self.get_player(pid)
            
        for p in self.players:
        
            if p.pid == mp.pid:
            
                for c in p.unplayed + p.played + p.items + p.treasure + p.spells + p.get_spells() + p.selection + p.equipped:
                    if c.get_id() == uid:
                        return c
                        
            else:
                
                for c in p.played:
                    if c.get_id() == uid:
                        return c

    def find_owner(self, c):
        return next((p for p in self.players if c in p.played), None)

    
            
    
                

