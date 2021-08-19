import sys
import random
import time
import copy
from save import load_settings
from cards import cards
from player import Player

class InfiniteLoop(Exception):
    pass

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
        
        self.settings = load_settings()
        self.cards = cards.copy()
        
        self.uid = 0
        self.pid = 0

        self.shop = []

        self.discard = []
        
        self.log = []
        self.master_log = []
        self.logs = {}
        
        self.mem = []
        self.counter = 0

        self.turn = 0 #turn of game
        self.current_turn = 0
        self.round = 0

        self.event = None #impliment multiple
        
        self.players = []
        self.current_player = 0 #index of player who is currently taking their turn
        self.main_p = None #main player

        self.mode = mode
        self.status = ''
        self.new_status('waiting')

        if self.mode == 'single':
            
            self.new_player(0)
            self.add_cpus()
            
    @property
    def done(self):
        return self.status in ('new game', 'next round')
            
#copy stuff---------------------------------------------------------------------------------------------------

    def copy(self):
        g = Game('turbo')
        
        g.uid = self.uid
        
        g.settings = self.settings.copy()

        g.turn = self.turn
        g.current_turn = self.current_turn
        g.round = self.round

        g.current_player = self.current_player

        g.status = self.status
        
        g.players = [Player(g, p.pid, p.score, True) for p in self.players]
        g.main_p = g.players[g.current_player]
            
        for i in range(len(self.players)):
            
            g.players[i].start_copy(g, self.players[i])

        g.discard = [c.light_sim_copy(g) for c in self.discard[:3]]
        
        g.event = self.event.light_sim_copy(g) if self.event is not None else None
            
        return g
        
#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        self.clear_logs()
        self.log.append({'t': 'res'})
        
        if self.mode == 'single':
            
            self.players = [self.get_player(0)]
            self.players[0].reset()
            
            self.add_cpus()
            
        else:
            
            for p in self.players: 
                p.reset()
     
        self.shuffle_players()
        self.current_player = 0
        self.main_p = self.players[0] 

        self.uid = len(self.players)
        
        for p in self.players:
            p.start()

        self.new_status('playing')
        
        self.turn = 0
        self.current_turn = 0
        self.round = 1
        self.update_round()

        self.mem.clear()
        self.counter = 0

        self.discard.clear()
        
        self.restock_shop()

        self.event = self.draw_cards('events', 1)[0]
        self.event.start(self)
        self.log.append({'t': 'se', 'c': self.event.copy()})
            
        self.main_p.start_turn()
        self.log.append({'t': 'nt', 'pid': self.main_p.pid})

    def new_round(self):
        self.clear_logs()
        self.log.append({'t': 'nr'})
        
        self.shuffle_players() 
        self.current_player = 0
        self.main_p = self.players[0]

        for p in self.players:
            p.new_round()

        self.new_status('playing')
        
        self.turn = 0
        self.current_turn = 0
        
        self.round += 1
        self.update_round()
        
        self.restock_shop()

        self.event = self.draw_cards('events', 1)[0]
        self.event.start(self)
        self.log.append({'t': 'se', 'c': self.event.copy()})
            
        self.main_p.start_turn()
        self.log.append({'t': 'nt', 'pid': self.main_p.pid})
 
    def reset(self):
        self.new_status('waiting')

        for p in self.players:
            
            p.reset()
            
        self.log.append({'t': 'res'})
 
    def start(self, pid):
        if (pid == 0 and len(self.players) > 1) or self.mode == 'single':

            self.new_game()
 
#player stuff ------------------------------------------------------------------------
 
    def get_pid(self):
        return 0
 
    def add_cpus(self):
        self.pid = 1

        for _ in range(self.get_setting('cpus')):
            
            p = Player(self, self.pid, self.get_setting('ss'), auto=True)
            self.players.append(p)      
            self.logs[0][p.pid] = []
            
            self.log.append({'t': 'add', 'pid': p.pid})

            self.pid += 1
            
    def new_player(self, pid): #add player to game
        if self.status == 'waiting':

            p = Player(self, pid, self.settings['ss'])
            self.players.append(p)  
            
            if pid == 0:
                self.main_p = p
                
            self.pid += 1
            
            self.log.append({'t': 'add', 'pid': pid})
            self.logs[pid] = self.get_startup_log()
            
            for p in self.players:
                if p.pid != pid:
                    self.logs[p.pid][pid] = []
                    
            if len(self.players) > 1:
                self.new_status('start')

            return True
            
        else:
            
            return False
            
    def remove_player(self, pid):
        p = self.get_player(pid)
        
        if p:
            
            for key in self.logs:
                del self.logs[key][p.pid]
                
            if p.pid in self.logs:
                del self.logs[p.pid]
            
            self.players.remove(p)
            self.log.append({'t': 'del', 'pid': p.pid})
            
            if self.mode == 'online':
                if self.status == 'playing':
                    self.reset()
                if len(self.players) == 1:
                    self.new_status('waiting')

    def balance_cpus(self):
        players = sorted(self.players, key=lambda p: p.pid, reverse=True)

        dif = (len(self.players) - 1) - self.get_setting('cpus')
        
        if dif > 0:
            
            for i in range(dif):
                
                p = players[i]
                self.remove_player(p.pid)
                
        elif dif < 0:
            
            for p in self.players.copy():
                
                if p.auto:
                    
                    self.remove_player(p.pid)
                    
            self.add_cpus()
   
    def get_player(self, pid):
        return next((p for p in self.players if p.pid == pid), None)

    def check_last(self, player):
        return all(len(p.played) > len(player.played) for p in self.players if p is not player)
        
    def check_first(self, player):
        return all(len(p.played) <= len(player.played) for p in self.players)
        
    def shift_up(self, player):
        self.players.remove(player)
        self.players.insert(0, player)
        self.current_player = self.players.index(self.main_p)
                
        self.log.append({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shift_down(self, player):
        self.players.remove(player)
        self.players.append(player)
        self.current_player = self.players.index(self.main_p)
                
        self.log.append({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shuffle_players(self):
        random.shuffle(self.players)
        
        self.log.append({'t': 'ord', 'ord': [p.pid for p in self.players]})

#card stuff---------------------------------------------------------------------------------------
     
    def get_new_uid(self):
        uid = self.uid
        self.uid += 1
        return uid
     
    def draw_cards(self, deck='play', num=1):
        deck = self.cards[deck]
        weights = [val[0] for val in deck.values()]
        
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        
        for i, card in enumerate(cards):

            cards[i] = deck[card][1](self, self.uid)
            self.uid += 1
            
        test = [c.name for c in cards]
            
        return cards
        
    def get_card(self, name):
        for deck in self.cards.values():
        
            info = deck.get(name)
            
            if info is not None:
                
                card = info[1](self, self.uid)
                self.uid += 1
                
                return card
  
    def transform(self, old_card, const):
        uid = old_card.uid
        new_card = const(self, uid)
        
        if old_card != new_card:

            info = self.find_card_deep(old_card)

            if info:

                owner, attr, i = info
                getattr(owner, attr)[i] = new_card
                self.log.append({'t': 'tf', 'c': old_card, 'name': new_card.name})

                return self.transform(old_card, const)
                
            else:
                
                return new_card
                
        else:
            
            return new_card
       
    def find_card_deep(self, card):
        for p in self.players:
        
            for i, c in enumerate(p.unplayed):
                if c == card:
                    return (p, 'unplayed', i)
                    
            for i, c in enumerate(p.played):
                if c == card:
                    return (p, 'played', i)
    
            for i, c in enumerate(p.equipped):
                if c == card:
                    p.unequip(c)
                    
            for i, c in enumerate(p.items):
                if c == card:
                    return (p, 'items', i)
                    
            for i, c in enumerate(p.spells):
                if c == card:
                    return (p, 'spells', i)
                    
            for i, c in enumerate(p.ongoing):
                if c == card:
                    return (p, 'ongoing', i)
                    
            for i, c in enumerate(p.landscapes):
                if c == card:
                    return (p, 'landscapes', i)
                    
    def swap(self, c1, c2):
        self.transform(c1, type(c2))
        self.transform(c2, type(c1))
                 
    def find_card(self, player, uid):
        for c in player.played + player.unplayed + player.get_spells() + player.items + player.spells + player.treasure + player.equipped + player.selection + player.landscapes:
            
            if c.get_id() == uid:
                
                return c
   
    def find_owner(self, c):
        return next((p for p in self.players if c in p.played), None)
        
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if 'item' in c.tags or 'equipment' in c.tags]
        
    def check_exists(self, uid):
        return any(self.find_card(p, uid) for p in self.players)
        
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
    
    def get_event(self):
        return self.event.name if hasattr(self, 'event') else None
  
#shop stuff---------------------------------------------------------------------------------------
        
    def fill_shop(self, m=3):
        num = max(m - len(self.shop), 0)
        cards = []
        
        decks = ('play', 'items', 'spells')
        
        for _ in range(num):
            
            deck = random.choice(decks)
            cards += self.draw_cards(deck)
            
        self.shop += cards
        
        self.log.append({'t': 'fill', 'cards': self.shop.copy()})

    def restock_shop(self):
        self.shop.clear()
        self.fill_shop()
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            
            if c.uid == uid:
                
                self.shop.remove(c)
                self.fill_shop()
                
                return c
                
#log stuff--------------------------------------------------------------------------------------------------

    def clear_logs(self):
        for key in self.logs:
            
            for sublog in self.logs[key].values():
                
                sublog.clear()
                
        self.log.clear()
        self.master_log.clear()

    def get_info(self, pid):
        p = self.get_player(pid)

        info = {}
        
        sublog = self.logs[pid]
        
        for key in sublog:
            
            log = sublog[key]
            
            if log:
            
                info[key] = pack_log(log)
                sublog[key].clear()

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
        
        scores = {p.pid: p.score for p in self.players}
        
        return (any(log for log in sublog.values()), scores)
        
    def get_startup_log(self):
        log = {'g': [{'t': 'ns', 'stat': 'waiting'}]}
        
        for p in self.players:
            
            log[p.pid] = [{'t': 'add', 'pid': p.pid}, {'t': 'cn', 'pid': p.pid, 'name': p.name}]
            
        log['g'].append({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
        return log

#update info stuff---------------------------------------------------------------------------------------
 
    def update_round(self):
        text = f"round {self.round}/{self.get_setting('rounds')}"
        
        self.log.append({'t': 'ur', 's': text})
            
    def new_status(self, stat):
        self.status = stat
        
        self.log.append({'t': 'ns', 'stat': stat})

    def is_status(self, stat):
        return self.status == stat

    def update_player(self, pid, cmd=''):
        p = self.get_player(pid)
   
        p.update(cmd)
          
    def main(self):
        if self.status != 'waiting':

            for p in self.players:
            
                if p.auto:
                    
                    p.auto_update()
      
        if not self.mode == 'turbo':
                
            self.update_game_logs()
            
        else:
            
            self.master_log += self.log
            self.log.clear()
            
        up = []
        
        for p in self.players:
            
            up += p.played
            
        if up == self.mem:
            
            self.counter += 1
            
        else:
            
            self.mem = up
            self.counter = 0
 
        if (self.mode == 'turbo' and self.counter > 100) or (not self.mode != 'turbo' and self.counter > 9999):
            
            raise InfiniteLoop
          
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
                
                if self.status == 'playing':
                
                    self.update_player(0, 'play')
                    
                reply = 1
                
            elif data == 'cancel': #cancel selection
                
                if self.status == 'playing':
                
                    self.update_player(0, 'cancel')
                    
                reply = 1
                
            elif data.isdigit():

                self.update_player(0, f'select {data}')
                reply = 1

            elif data == 'flip':
                
                if self.status == 'playing':
                
                    self.update_player(0, 'flip')
                    
                reply = 1
                
            elif data == 'roll':
                
                if self.status == 'playing':
                
                    self.update_player(0, 'roll')
                    
                reply = 1

            elif data == 'settings':
                
                reply = self.get_settings()
                    
            elif data == 'us':
                
                if self.status == 'waiting':
                    
                    self.update_settings()
                    reply = 1
                
                else:
                    
                    reply = 0

        return reply
                     
#settings stuff---------------------------------------------------------------------------------------

    def get_settings(self):
        return self.settings.copy()
        
    def get_setting(self, setting):
        return self.settings[setting]
        
    def update_settings(self):
        self.settings = load_settings()   
        self.balance_cpus()

#turn stuff-----------------------------------------------------------------------------------------------

    def rotate_cards(self):
        selections = []

        for p in self.players:
        
            selections.append(p.unplayed)
            
        selections.insert(0, selections.pop(-1))
            
        for p, s in zip(self.players, selections):
        
            p.new_deck('unplayed', s)

    def check_advance(self):
        if self.status == 'playing':
        
            if not self.done and self.main_p.finished:
                
                self.advance_turn()
                
    def advance_turn(self):
        if self.status != 'playing':
            
            return 

        if all(p.finished_game() for p in self.players):

            if all(p.game_over for p in self.players):

                if not self.done:
                    
                    if self.round <= self.get_setting('rounds') - 1:
                        
                        self.new_status('next round')
                        
                    else:
                        
                        self.new_status('new game')
                        
                    self.log.append({'t': 'fin', 'w': self.get_winners()})
                    
            else:
                
                for p in self.players:
                    
                    p.end_game()
                    
            return  
            
        elif self.main_p.finished_turn():

            self.find_turn()
            
    def find_turn(self):
        if any(p.unplayed for p in self.players):
            
            self.main_p.end_turn()
            
            while True:  
                
                self.current_player = (self.current_player + 1) % len(self.players)
                self.current_turn = (self.current_turn + 1) % len(self.players)
                p = self.players[self.current_player]

                if self.current_turn == 0:
                    self.rotate_cards()
                
                if p.unplayed:
                    break

            self.main_p = self.players[self.current_player]
            self.main_p.start_turn()
            
            self.log.append({'t': 'nt', 'pid': self.main_p.pid})
            
            self.turn += 1
            
#ending stuff---------------------------------------------------------------------------------------

    def close(self):
        self.running = False

    def get_winners(self):
        hs = max(self.players, key=lambda p: p.score).score
            
        return [p.pid for p in self.players if p.score == hs]

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
                
    def finished_game(self):
        return self.round + 1 > self.get_setting('rounds')

    
            
    
                

