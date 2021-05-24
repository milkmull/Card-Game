import sys
import random
import time
import copy
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
    
def pack_log(logs):
    new_log = []
    
    for log in logs:

        new_entry = {}
        
        for key in log:
            
            val = log[key]
            
            if isinstance(val, Player):
                
                new_entry[key] = val.pid
                
            elif hasattr(val, 'uid'):
                
                new_entry[key] = (val.name, val.uid)
                
            else:
                
                new_entry[key] = val
                
        new_log.append(new_entry)
                
    return new_log
        
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
        self.shop = []

        self.discard = []
        
        self.logs = {}
        
        self.turn = 0 #turn of game
        self.current_turn = 0

        self.event = None #impliment multiple
        
        self.players = []

        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = None #main player

        self.phase = ''
        
        self.mode = mode #single vs online
        
        if self.mode == 'single':
            
            self.new_player(0)
            
#copy stuff---------------------------------------------------------------------------------------------------

    def copy(self):
        g = Game('turbo')
        
        g.settings = self.settings.copy()
        
        g.done = self.done
        g.wait = self.wait
        
        g.turn = self.turn
        g.round = self.round
        g.current_turn = 0

        g.current_player = self.current_player

        g.phase = self.phase
        
        g.players = [Player(g, p.pid, p.score, True) for p in self.players]
        g.main_p = g.players[g.current_player]
            
        for i in range(len(self.players)):
            
            g.players[i].start_copy(g, self.players[i])
        
        g.deck = [c.light_sim_copy(g) for c in self.deck[:8]]
        g.items = [c.light_sim_copy(g) for c in self.items[:10]]
        g.spells = [c.light_sim_copy(g) for c in self.spells[:5]]
        g.treasure = [c.light_sim_copy(g) for c in self.treasure[:10]]
        g.shop = [c.light_sim_copy(g) for c in self.shop]
        g.landscapes = [c.light_sim_copy(g) for c in self.landscapes]

        g.discard = [c.light_sim_copy(g) for c in self.discard[:3]]
        
        g.event = self.event.light_sim_copy(g) if self.event is not None else None
            
        return g
        
#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        if self.mode == 'single':
            
            self.players = [self.get_player(0)]
            self.players[0].reset()
            
            self.add_cpus()
            
        for p in self.players:
            
            p.reset()

        self.done = False
        self.phase = 'draft'
        self.uid = len(self.players)
        
        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = self.players[0] #main player
        random.shuffle(self.players)
        
        self.deck = self.fill_deck(cards)
        self.items = self.fill_deck(items)
        self.spells = self.fill_deck(spells)
        self.treasure = self.fill_deck(treasure)
        self.event_cards = self.fill_deck(events)
        self.landscapes = self.fill_deck(landscapes)
        
        self.shop.clear()
        self.discard.clear()
        
        for p in self.players:
        
            p.start()
        
        self.turn = 0 #turn of game
        self.round = 1
        self.current_turn = 0

        self.deal('items', 'items', self.get_setting('items'))
        self.deal('spells', 'spells', self.get_setting('spells'))

        self.deal('deck', 'selection', self.get_setting('cards'))
        
        for p in self.players:
            
            p.treasure.append(GoldCoins(self, self.uid))
            
            self.uid += 1
        
        if self.get_setting('event'):

            self.event = self.event_cards.pop(random.randrange(len(self.event_cards)))
            
    def add_cpus(self):
        self.pid = 1

        for _ in range(self.get_setting('cpus')):

            self.players.append(Player(self, self.pid, self.get_setting('ss'), auto=True))
        
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
        self.round += 1
        
        self.phase = 'draft'
        self.done = False
        self.turn = 0
        self.current_turn = 0
        
        for p in self.players:
            
            p.new_round()

        self.current_player = 0
        self.main_p = self.players[0]
        
        self.shop.clear()

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
            
    def fill_shop(self, num=3):
        for _ in range(num):
        
            card = random.choice(self.deck + self.items + self.spells)#, self.landscapes])
            
            deck = next((deck for deck in [self.deck, self.items, self.spells] if card in deck))

            deck.remove(card)
            
            self.shop.append(card)
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            
            if c.uid == uid:
                
                self.shop.remove(c)
                
                self.fill_shop(1)
                
                return c

#server communication functions-----------------------------------------------------------------------------

    def new_player(self, pid): #add player to game
        if self.wait:

            p = Player(self, pid, self.settings['ss'])

            self.players.append(p)
                
            self.pid += 1
            
            self.logs[pid] = {p.pid: [] for p in self.players}
            
            return True
            
        else:
            
            return False
            
    def remove_player(self, pid): #remove player from game
        p = self.get_player(pid)
        
        if p:
        
            for key in self.logs:
                
                del self.logs[key][p.pid]
                
            del self.logs[p.pid]
            
            self.players.remove(p)

    def check_order(self):
        pids = []
        names = []
        
        for p in self.players:
            
            pids.append(p.pid)
            names.append(p.name)
            
        return [pids, names]
        
    def start(self, pid):
        if (pid == 0 and len(self.players) > 1) or self.mode == 'single':
            
            self.wait = False
            
            self.new_game()
            
            return True
            
        else:
            
            return False
            
    def get_info(self, player, other, attrs):
        if not self.get_player(0):
            
            return 'close'
            
        p = self.get_player(other)
        
        info = [p.get_info(attr) for attr in attrs]
        
        if 'log' in attrs:
            
            info[attrs.index('log')] = self.get_log(player, other)

        return info
        
    def update_logs(self, pid, new_entry):
        for key in self.logs:
            
            sublog = self.logs[key]
            
            log = sublog.get(pid)
            
            if log is None:
                
                sublog[pid] = new_entry
                
            else:
                
                sublog[pid] += new_entry

    def get_log(self, id, oid):
        logs = self.logs.get(id)
        
        log = logs.get(oid)
        
        if log is None:
            
            logs[oid] = []
            
            log = logs[oid]
            
        pack = pack_log(log)
        
        log.clear()
        
        return pack
        
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
        
    def flip(self, pid):
        p = self.get_player(pid)
        
        cmd = 'flip'
        
        p.update(cmd)
        
        return True
        
    def roll(self, pid):
        p = self.get_player(pid)
        
        cmd = 'roll'
        
        p.update(cmd)
        
        return True
        
    def event_info(self):
        return self.event.name if hasattr(self, 'event') else False
        
    def get_settings(self):
        return self.settings.copy()
        
    def update_settings(self, setting):
        key, val = setting[1:].split(',')

        if val in (str(True), str(False)):
            
            self.settings[key] = True if val == 'True' else False
            
        else:
            
            self.settings[key] = int(val)
            
        return True
        
    def update_player(self, pid):
        p = self.get_player(pid)
        
        if p:
            
            p.update()
            
            return True
            
    def check_status(self):
        if self.wait:
            
            return 'waiting'
    
        if self.done:
        
            if self.round <= self.get_setting('rounds') - 1:
                
                return 'next round'
                
            else:
                
                return 'new game'
                
        else:
            
            return 'playing'
            
    def get_shop(self):
        return [(c.name, c.uid) for c in self.shop]
        
    def get_winner(self):
        if self.done and self.check_status() == 'new game' and not self.wait:

            reply = max(self.players, key=lambda p: p.score).pid
            
            return reply
            
        else:
            
            return False
        
    def send(self, data):
        reply = ''
        
        if data.startswith('info'):
                    
            data = data.split('-')
            
            reply = self.get_info(0, int(data[1]), data[2].split(',')) #get info for each player (points, visible cards)
            
        elif data.startswith('name'):
            
            reply = self.get_player(0).set_name(data.split(',')[-1])
            
        elif data == 'players':
                    
            reply = self.check_order()
        
        elif data == 'start':
            
            reply = self.start(0)
            
        elif data == 'reset':
            
            reply = self.reset()
            
        elif data == 'settings':
            
            reply = self.get_settings()
            
        elif '~' == data[0]:
            
            if self.wait:
            
                reply = self.update_settings(data)
                
            else:
                
                reply = False
                
        elif data == 'disconnect':
            
            self.running = False
            
        elif data == 'wait':
                    
            reply = self.wait
            
        elif self.wait: #won't go past here if client is waiting to start game
            
            reply = 'w'
        
        elif data == 'status':
                    
            reply = self.check_status()
            
        elif data == 'continue':
            
            text = self.check_status()
            
            if text == 'next round':
                
                self.new_round()
                
            elif text == 'new game':
                
                self.new_game()
                
            reply = True
            
        elif data == 'winner':
            
            return self.get_winner()
            
        elif data == 'update':
            
            self.update_player(0)
            
            self.main()

        elif check_int(data):

            reply = self.select(0, int(data))
            
        elif data == 'event':
            
            reply = self.event_info()
            
        elif data == 'shop':
            
            reply = self.get_shop()
            
        elif data == 'click':
            
            reply = self.select(0)
            
        elif data == 'play':
            
            reply = self.play(0)
            
        elif data == 'flip':
            
            reply = self.flip(0)
            
        elif data == 'roll':
            
            reply = self.roll(0)
            
        elif data == 'cancel':
            
            reply = self.cancel(0)

        if reply == 'close':
            
            self.running = False

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
        self.fill_shop()

        self.advance_turn()
  
    def end_round(self):
        for p in self.players:
            
            if not p.round_over:
            
                p.end_round()
        
    def end_game(self):
        for p in self.players:
            
            if not p.round_over:
            
                p.end_round()
                
            if not p.game_over:
            
                p.end_game()

    def check_advance(self):
        if not self.done and self.main_p.finished:
            
            self.advance_turn()
            
    def finished_game(self):
        return self.round + 1 > self.get_setting('rounds')
        
    def advance_turn(self):
        if all(p.check_end_game() for p in self.players) or (all(p.check_end_round() for p in self.players) and self.mode == 'turbo'):
            
            self.done = True
            
        elif all(p.check_end_round() for p in self.players):
            
            self.new_round()
            
            return
            
        if len(self.players) == 1 or self.done:

            return
            
        if all(not (p.unplayed or p.requests) for p in self.players):

            for p in self.players:
                
                p.end_round()
                
                if self.round == self.get_setting('rounds'):
                
                    p.end_game()
                
            self.current_turn += 1
                
            return
            
        if not self.main_p.requests and any(p.unplayed for p in self.players):
            
            self.main_p.end_turn()
            
            while True:

                for p in self.players:
                    
                    if len(p.played) <= self.turn and p.unplayed:
            
                        self.current_player = self.players.index(p)

                        break
           
                else:
                    
                    self.turn += 1
                    
                    self.current_player = 0
                    
                    continue
                    
                break
                
            self.main_p = self.players[self.current_player]

            self.main_p.start_turn()
            
            self.current_turn += 1

    #def advance_turn(self):
    #    if all(p.check_end_game() for p in self.players):
    #        
    #        self.done = True
    #        
    #    if len(self.players) == 1 or self.done:
    #
    #        return
    #        
    #    if all(not (p.unplayed or p.requests) for p in self.players):
    #        
    #        if self.round == self.get_setting('rounds'):
    #            
    #            self.end_game()
    #            
    #        else:
    #            
    #            self.end_round()
    #            
    #        self.current_turn += 1
    #            
    #        return
    #        
    #    self.main_p.end_turn()
    #    
    #    for p in self.players:
    #        
    #        print(self.turn, p.pid, p.played, p.unplayed, p.requests)
    #
    #    if any(len(p.played) == self.turn and p.unplayed for p in self.players):
    #
    #        for p in self.players:
    #            
    #            if len(p.played) == self.turn and p.unplayed:
    #    
    #                self.current_player = self.players.index(p)
    #
    #                break
    #
    #    else:
    #        
    #        if self.turn > 10:
    #            
    #            for p in self.players:
    #                
    #                print(p.pid, p.played, p.unplayed)
    #                print(self.players[5])
    #        
    #        self.turn += 1
    #        
    #        self.current_player = 0
    #        
    #        self.advance_turn()
    #        
    #    self.main_p = self.players[self.current_player]
    #
    #    self.main_p.start_turn()
    #    
    #    self.current_turn += 1
        
    def main(self):
        for p in self.players:
        
            if p.auto:
                
                p.auto_update()
        
#player stuff-----------------------------------------------------------------------------------------------
        
    def draw_cards(self, deck='deck', num=1):
        cards = []
        
        deck = getattr(self, deck)

        for _ in range(num):
            
            if deck:
            
                card = random.choice(deck)
                
                cards.append(card)
                
                deck.remove(card)
                
            else:
            
                break

        return cards
        
    def check_last(self, player):
        return all(len(p.played) > len(player.played) for p in [x for x in self.players if x.pid != player.pid]) or (self.players[-1] == player)
        
    def check_first(self, player):
        return player.pid == self.players[0].pid and all(len(p.played) == self.turn for p in [x for x in self.players if x.pid != player.pid])
               
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if c.type in ('item', 'equipment')]
        
    def restore(self, c):
        if c in self.discard:
        
            self.discard.remove(c)
            
    def get_last_item(self):
        i = self.get_discarded_items()
        
        if not i:
            
            i = self.draw_cards('items')[0]
            
        else:
            
            i = i[0]
            
        return i.copy()
        
#card stuff---------------------------------------------------------------------------------------

    def get_event(self):
        return self.event.name if hasattr(self, 'event') else None

    def get_player(self, pid):
        return next((p for p in self.players if p.pid == pid), None)
        
    def get_current_turn(self):
        return self.main_p
        
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
        
        if i1 and i2:
            
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
                        
            for c in self.shop:
                
                if c.uid == uid:
                    
                    return c

    def find_owner(self, c):
        return next((p for p in self.players if c in p.played), None)

    
            
    
                

