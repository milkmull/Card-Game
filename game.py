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
                
            elif isinstance(val, list):
                
                new_list = []
                
                for i in val:
                    
                    if hasattr(i, 'get_id'):
                        
                        new_list.append([i.name, i.get_id()])
                        
                    else:
                        
                        new_list.append(i)
                        
                new_entry[key] = new_list

            else:
                
                new_entry[key] = val
                
        new_log.append(new_entry)
                
    return new_log
        
class Game:
    def __init__(self, mode='online'):
        self.running = True
        self.wait = True
        self.done = False #true when game is over
        
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
        
        self.log = []
        self.master_log = []
        
        self.logs = {}
        
        self.turn = 0 #turn of game
        self.current_turn = 0

        self.event = None #impliment multiple
        
        self.players = []

        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = None #main player

        self.phase = ''
        
        self.mode = mode #single vs online
        
        self.status = ''
        self.new_status('waiting')
        
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
        self.log.clear()
        self.master_log.clear()
        
        if self.mode == 'single':
            
            self.players = [self.get_player(0)]
            self.players[0].reset()
            
            self.add_cpus()
            
        for p in self.players:
            
            p.reset()
            
        self.log.append({'t': 'res'})

        self.done = False
        self.wait = False
        self.phase = 'draft'
        self.new_status('draft')
        self.uid = len(self.players)
        
        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = self.players[0] #main player
        self.shuffle_players()
        
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
            
            p.add_treasure(GoldCoins(self, self.uid))
            self.uid += 1
        
        if self.get_setting('event'):

            self.event = self.event_cards.pop(random.randrange(len(self.event_cards)))
            self.log.append({'t': 'se', 'c': self.event.copy()})

    def new_round(self):
        self.clear_logs()
        self.log.append({'t': 'nr'})
        
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
            
    def add_cpus(self):
        self.pid = 1

        for _ in range(self.get_setting('cpus')):

            self.players.append(Player(self, self.pid, self.get_setting('ss'), auto=True))
            
            self.logs[0][self.pid] = []
            
            self.log.append({'t': 'add', 'pid': self.pid})

            self.pid += 1
            
    def new_player(self, pid): #add player to game
        if self.status == 'waiting':

            p = Player(self, pid, self.settings['ss'])
            self.players.append(p)  
            
            if pid == 0:
            
                self.main_p = p
                
            self.pid += 1
            
            self.logs[pid] = {p.pid: p.master_log.copy() for p in self.players}
            self.logs[pid]['g'] = self.master_log.copy()
            
            for p in self.players:
                
                if p.pid != pid:
            
                    self.logs[p.pid][pid] = []

            self.log.append({'t': 'add', 'pid': pid})
            
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
            
            self.log.append({'t': 'del', 'pid': p.pid})
            
    def start(self, pid):
        if (pid == 0 and len(self.players) > 1) or self.mode == 'single':

            self.new_game()
            
    def reset(self):
        self.done = False
        self.wait = True
        
        self.new_status('waiting')
        
        self.phase = ''
        
        for p in self.players:
            
            p.reset()
            
        self.log.append({'t': 'res'})
     
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
            
            cards = self.draw_cards(deck, num)

            p.new_deck(destination, cards)
            
    def fill_shop(self, num=3): #will cause problems with empty decks
        for _ in range(num):
        
            card = random.choice(self.deck + self.items + self.spells)#, self.landscapes])
            deck = next((deck for deck in [self.deck, self.items, self.spells] if card in deck))
            deck.remove(card)
            self.shop.append(card)
            
            self.log.append({'t': 'fill', 'c': card})
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            
            if c.uid == uid:
                
                self.shop.remove(c)
                
                self.fill_shop(1)
                
                return c
                
#log stuff--------------------------------------------------------------------------------------------------

    def get_info(self, pid):
        p = self.get_player(pid)

        info = {}
        
        sublog = self.logs[pid]
        
        for key in sublog:
            
            log = sublog[key]
            
            if log:
            
                info[key] = pack_log(log)
                sublog[key].clear()
                
        for pid in info:
            
            if pid != 'g':
                
                info[pid].append({'t': 'score', 's': self.get_player(pid).score})

        return info
                
    def update_game_logs(self):
        for key in self.logs:
            
            sublog = self.logs[key]           
            log = sublog.get('g')
            log += self.log
            
        self.master_log += self.log
        self.log.clear()
        
    def update_player_logs(self, pid):
        p = self.get_player(pid)
        
        for key in self.logs:
            
            sublog = self.logs[key]
            log = sublog.get(pid)
            log += p.log
            
        p.log.clear()

    def check_logs(self, pid):
        sublog = self.logs[pid]
        
        return any(log for log in sublog.values())

    def get_log(self, id, oid):
        logs = self.logs.get(id)
        
        log = logs.get(oid)
        
        if log is None:
            
            logs[oid] = []
            
            log = logs[oid]
            
        pack = pack_log(log)
        
        log.clear()
        
        return pack
        
    def clear_logs(self):
        for key in self.logs:
            
            for sublog in self.logs[key].values():
                
                sublog.clear()

#server communication functions-----------------------------------------------------------------------------

    def play(self, pid):
        p = self.get_player(pid)

        cmd = 'play'
        
        p.update(cmd)
        
    def cancel(self, pid):
        p = self.get_player(pid)
        
        cmd = 'cancel'
        
        p.update(cmd)
        
    def select(self, pid, uid):
        p = self.get_player(pid)
        
        card = self.find_card(uid, pid)
        
        if self.phase == 'draft':
            
            p.draft(card)

            self.check_rotate()
            
        else:
            
            p.update('select', card)
        
    def update_player(self, pid):
        p = self.get_player(pid)
        
        if p:
            
            p.update()

    def flip(self, pid):
        p = self.get_player(pid)
        
        cmd = 'flip'
        
        p.update(cmd)
        
    def roll(self, pid):
        p = self.get_player(pid)
        
        cmd = 'roll'
        
        p.update(cmd)
        
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
        
    def get_winners(self):
        hs = max(self.players, key=lambda p: p.score).score
            
        return [p.pid for p in self.players if p.score == hs]
        
    def send(self, data):
        reply = ''
        
        if not data:
                    
            return
            
        else:
            
            if data == 'disconnect': #disconnect
                
                return

            elif data == 'u': #check if there are any updates

                self.update_player(0)
                self.main()
                
                reply = self.check_logs(0)
                
            elif data == 'info': #get update info
            
                reply = self.get_info(0)
                
            elif data.startswith('name'): #set player name
                
                reply = self.get_player(0).set_name(data.split(',')[-1])
            
            elif data == 'start': #start game
                
                self.start(0)
                
                reply = 1
                
            elif data == 'reset': #reset game
                
                self.reset()
                
                reply = 1
                
            elif data == 'continue': #continue to next game/round
                
                status = self.status
                
                if status == 'next round':
                    
                    self.new_round()
                    
                elif status == 'new game':
                    
                    self.new_game()
                    
                reply = 1
                
            elif data == 'play': #play card
                
                if self.phase == 'play':
                
                    self.play(0)
                    
                reply = 1
                
            elif data == 'cancel': #cancel selection
                
                if self.phase == 'play':
                
                    self.cancel(0)
                    
                reply = 1
                
            elif check_int(data):
            
                self.select(0, int(data))
                    
                reply = 1
                
            elif data == 'update':

                self.update_player(0)
                self.main()
                    
                reply = 1
                
            elif data == 'flip':
                
                if self.phase == 'play':
                
                    self.flip(0)
                    
                reply = 1
                
            elif data == 'roll':
                
                if self.phase == 'play':
                
                    self.roll(0)
                    
                reply = 1

            elif data == 'settings': #get settings
                
                reply = self.get_settings()
                
            elif data.startswith('-s:'):
            
                reply = self.get_setting(data[3:])
                
            elif '~' == data[0]: #update settings
                
                if self.status == 'waiting':
                
                    self.update_settings(data)
                    
                    reply = 1
                    
                else:
                    
                    reply = 0

        return reply
        
    def get_pid(self):
        return 0
        
    def close(self):
        self.running = False
            
#turn stuff-----------------------------------------------------------------------------------------------

    def new_status(self, stat):
        self.status = stat
        
        self.log.append({'t': 'ns', 'stat': stat})

    def check_rotate(self):
        if not any(p.selecting for p in self.players):
            
            self.rotate_selection()

    def rotate_selection(self):
        if not any(p.selection for p in self.players):
                                    
            self.end_draft()
            
        else:
    
            selections = []
            
            for p in self.players:
            
                selections.append(p.selection)
                
            selections.append(selections.pop(0))
                
            for p, s in zip(self.players, selections):
            
                p.new_draft(s)
                
    def end_draft(self):
        self.phase = 'play'
        
        self.new_status('playing')
        
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
        if self.phase == 'play':
        
            if not self.done and self.main_p.finished:
                
                self.advance_turn()
            
    def finished_game(self):
        return self.round + 1 > self.get_setting('rounds')
        
    def advance_turn(self):   
        if all(p.check_end_game() for p in self.players) or (all(p.check_end_round() for p in self.players) and self.mode == 'turbo'):
            
            if not self.done:
            
                self.done = True

                if self.round <= self.get_setting('rounds') - 1:
                    
                    self.new_status('next round')
                    
                else:
                    
                    self.new_status('new game')
            
                self.log.append({'t': 'fin', 'w': self.get_winners()})
            
        elif all(p.check_end_round() for p in self.players):
            
            #self.new_round()
            self.new_status('next round')
            
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
            
            self.log.append({'t': 'nt', 'pid': self.main_p.pid})
        
    def main(self):
        if not self.wait:
        
            for p in self.players:
            
                if p.auto:
                    
                    p.auto_update()
                
        self.update_game_logs()
        
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
        
    def shift_up(self, player):
        for i in range(len(self.players)):
            
            if self.players[i].pid == player.pid:
                
                self.players.insert(0, self.players.pop(i))
                
                self.advance_turn()

                break
                
        self.log.append({'t': 'su', 'pid': player.pid})
        
    def shift_down(self, player):
        for i in range(len(self.players)):
            
            if self.players[i].pid == player.pid:
                
                self.players.append(self.players.pop(i))
                
                self.advance_turn()
                
                break
                
        self.log.append({'t': 'sd', 'pid': player.pid})
        
    def shuffle_players(self):
        random.shuffle(self.players)
        
        self.log.append({'t': 'ord', 'ord': [p.pid for p in self.players]})
               
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
    
            for i, c in enumerate(p.equipped):
                if c.uid == uid:
                    p.unequip(c)
                    
            for i, c in enumerate(p.items):
                if c.uid == uid:
                    return (p, 'items', i)
                    
            for i, c in enumerate(p.spells):
                if c.uid == uid:
                    return (p, 'spells', i)
                    
            for i, c in enumerate(p.get_spells()):
                if c.uid == uid:
                    return (p, 'ongoing', i)
                    
    def swap(self, c1, c2):
        info1 = self.find_card_deep(c1.uid)
        info2 = self.find_card_deep(c2.uid)
        
        if info1 and info2:
            
            p1, d1, i1 = info1
            p2, d2, i2 = info2

            getattr(p1, d1)[i1], getattr(p2, d2)[i2] = getattr(p2, d2)[i2], getattr(p1, d1)[i1]
            
            self.log.append({'t': 'sw', 'c1': c1, 'c2': c2})
                 
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

    
            
    
                

