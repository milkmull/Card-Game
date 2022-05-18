import random
import json
import importlib

import save
import exceptions

import func
import custom_cards
import testing_card
from player import Player, Auto_Player

def init():
    globals()['SAVE'] = save.get_save()

def load_testing_card():
    importlib.reload(testing_card)
    
def load_custom_cards():
    importlib.reload(custom_cards)

def any(elements):
    for e in elements:
        if e:
            return True
    return False
    
def sort_logs(log):
    u = log.get('u')
    if u == 'g':
        return -1
    else:
        return u
        
class Vote_Card(func.Card):
    name = 'vote'
    tags = ['extra']
    def __init__(self, game, *args):
        super().__init__(game, -1)
        self.c1 = func.Blank(game, -2, 'rotate')
        self.c2 = func.Blank(game, -3, 'keep')
        
    def start(self):
        for p in self.game.players:
            p.add_request(self, 'select')
        
    def get_selection(self, player):
        return [self.c1, self.c2]
        
    def select(self, player, num):
        player.set_vote(player.selected[0].name)
  
class Game:
    @staticmethod
    def blank_player_info(pid):
        return {'name': f'player {pid}', 'description': '', 'tags': ['player'], 'image': 'img/user.png'}
        
    @staticmethod
    def get_card_data():
        return SAVE.get_playable_card_data()
        
    @staticmethod
    def pack_log(logs):
        new_log = []
    
        for log in logs:
            log = log.copy()
            for key, val in log.items():

                if isinstance(val, Player):
                    log[key] = val.pid
                    
                elif hasattr(val, 'uid'):
                    log[key] = (val.name, val.uid)
                    
                elif isinstance(val, list):
                    new_list = []
                    for i in val:  
                        if hasattr(i, 'get_id'):
                            new_list.append((i.name, i.get_id()))   
                        else:   
                            new_list.append(i)       
                    log[key] = new_list

                else:
                    log[key] = val
                    
            new_log.append(log)
                    
        return new_log
  
    def __init__(self, mode='online', cards=None):
        self.settings = SAVE.get_data('settings')
        if cards is not None:
            self.cards = cards
        else:
            self.cards = Game.get_card_data()
            
        self.mode = mode
        self.status = ''
        self.current_turn = 0
        self.round = 0
        
        self.uid = 0
        self.pid = 0
        
        self.log = []
        self.master_log = []
        self.logs = {}
        self.frame = 0
        
        self.mem = []
        self.counter = 0

        self.event = None
        self.shop = []
        self.discard = []
        self.vote_card = Vote_Card(self)
        
        self.players = []

        self.new_status('waiting')

        if self.mode == 'single':
            player_info = SAVE.get_data('cards')[0]
            player_info['name'] = SAVE.get_data('username')
            self.add_player(0, player_info)
            self.add_cpus()

    def done(self):
        return self.status in ('new game', 'next round')
            
#copy stuff---------------------------------------------------------------------------------------------------

    def copy(self):
        return Game_Copy(self)
        
#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        self.clear_logs()
        self.frame = 0
        self.add_log({'t': 'res'})

        for p in self.players: 
            p.reset()
        self.shuffle_players()
        self.uid = len(self.players)
        for p in self.players:
            p.start()

        self.current_turn = 0
        self.round = 1
        self.update_round()
        
        self.mem.clear()
        self.counter = 0

        self.discard.clear()
        self.restock_shop()
        self.set_event()
            
        self.new_turn()
        
        self.new_status('playing')

    def new_round(self):
        self.clear_logs()
        self.frame = 0
        self.add_log({'t': 'nr'})
        
        self.shuffle_players() 
        for p in self.players:
            p.new_round()

        self.current_turn = 0

        self.round += 1
        self.update_round()

        self.mem.clear()
        self.counter = 0
        
        self.restock_shop()
        self.set_event()
            
        self.new_turn()
        
        self.new_status('playing')

    def reset(self):
        self.new_status('waiting')
        for p in self.players: 
            p.reset()   
        self.add_log({'t': 'res'})
 
    def start(self, pid):
        if pid == 0:
            if len(self.players) > 1:
                self.new_game()

#networking------------------------------------------------------------------------------------------
 
    def get_pid(self):
        return 0
        
    def get_winners(self):
        hs = max({p.score for p in self.players})
        return [p.pid for p in self.players if p.score == hs]
    
    def send(self, data):
        if not data:        
            return
            
        reply = ''

        if data == 'disconnect':
            return
        
        if data == 'pid':            
            reply = 0

        elif data == 'info':
            self.main()
            reply = self.get_info(0)
            
        elif data.startswith('name'):
            reply = self.get_player(0).set_name(data[5:])
        
        elif data == 'start':
            self.start(0)
            reply = 1
            
        elif data == 'reset':
            self.reset()
            reply = 1
            
        elif data == 'continue':
            status = self.status
            if status == 'next round':
                self.new_round()  
            elif status == 'new game': 
                self.new_game()
            reply = 1
            
        elif data == 'play':
            if self.status == 'playing':
                self.update_player(0, cmd='play')    
            reply = 1
            
        elif data == 'cancel':
            if self.status == 'playing':
                self.update_player(0, cmd='cancel')    
            reply = 1
            
        elif data.lstrip('-').isdigit():
            self.update_player(0, cmd=f'select {data}')
            reply = 1

        elif data == 'flip':
            if self.status == 'playing':
                self.update_player(0, cmd='flip')        
            reply = 1
            
        elif data == 'roll':
            if self.status == 'playing':
                self.update_player(0, cmd='roll')   
            reply = 1

        elif data == 'settings':
            reply = self.get_settings()
                
        elif data == 'us':
            self.update_settings()
            reply = 1

        return reply
        
    def recieve_player_info(self, pid):
        p = self.get_player(pid)
        return p.get_info()

    def close(self):
        pass

#log stuff--------------------------------------------------------------------------------------------------

    def get_scores(self):
        return {p.pid: p.score for p in self.players}

    def add_log(self, log):
        log['u'] = 'g'
        log['frame'] = self.frame
        self.log.append(log)

    def clear_logs(self):
        for key in self.logs:
            self.logs[key].clear()      
        self.log.clear()
        self.master_log.clear()

    def get_info(self, pid):
        p = self.get_player(pid)
        
        logs = self.logs[pid][:6]
        if logs:
            info = Game.pack_log(logs)
            self.logs[pid] = self.logs[pid][6:]
        else:
            info = logs

        return info
                
    def update_game_logs(self):
        for pid, sublog in self.logs.items():
            sublog += self.log
            sublog.sort(key=sort_logs)
        self.master_log += self.log
        self.log.clear()
        
    def update_player_logs(self, p):
        for pid, sublog in self.logs.items():
            sublog += p.log
        
    def get_startup_log(self):
        logs = []
        logs.append({'u': 'g', 't': 'ns', 'stat': 'waiting'})
        logs.append({'u': 'g', 't': 'set', 'settings': self.get_settings()})
        
        for p in self.players:
            logs.append({'u': p.pid, 't': 'add', 'pid': p.pid})
            logs.append({'u': p.pid, 't': 'cn', 'pid': p.pid, 'name': p.name})
            
        logs.append({'u': 'g', 't': 'ord', 'ord': [p.pid for p in self.players]})

        for log in logs:
            log['frame'] = self.frame

        return logs

#player stuff ------------------------------------------------------------------------

    def add_cpus(self):
        self.pid = 1

        for _ in range(self.get_setting('cpus')):  
            player_info = Game.blank_player_info(self.pid)
            p = Auto_Player(self, self.pid, player_info)
            self.players.append(p)      
            self.add_log({'t': 'add', 'pid': p.pid})
            self.pid += 1
            
    def add_player(self, pid, player_info):
        if self.status == 'waiting':

            p = Player(self, pid, player_info)
            self.players.append(p)  
            self.pid += 1
            
            self.add_log({'t': 'add', 'pid': pid})
            self.logs[pid] = self.get_startup_log()
            
            self.new_status('waiting')

            return p 
            
    def remove_player(self, pid):
        p = self.get_player(pid)
        
        if p:
            if p.pid in self.logs:
                self.logs.pop(p.pid)
            self.players.remove(p)
            self.add_log({'t': 'del', 'pid': p.pid})
            
            if self.mode == 'online':
                if self.status == 'playing':
                    self.reset()
                else:
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
                if p.is_auto():    
                    self.remove_player(p.pid)        
            self.add_cpus()
   
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

#card stuff---------------------------------------------------------------------------------------
  
    def get_new_uid(self):
        uid = self.uid
        self.uid += 1
        return uid

    def get_card(self, name, uid=None):
        if uid is None:
            uid = self.get_new_uid()
        for deck in self.cards.values():
            info = deck.get(name)
            if info is not None:  
                if info.get('custom'):
                    if not info.get('test'):
                        card = getattr(custom_cards, info['classname'])(self, uid)
                    else:
                        card = getattr(testing_card, info['classname'])(self, uid)
                else:
                    card = getattr(func, info['classname'])(self, uid)
                return card

    def draw_cards(self, deck='play', num=1):
        deck = self.cards[deck]
        weights = [val['weight'] for val in deck.values()]
        
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        
        for i, name in enumerate(cards):
            cards[i] = self.get_card(name)

        return cards

#main game logic---------------------------------------------------------------------------------

    def update_round(self):
        text = f"round {self.round}/{self.get_setting('rounds')}"
        self.add_log({'t': 'ur', 's': text})
            
    def new_status(self, stat):
        self.status = stat
        self.add_log({'t': 'ns', 'stat': stat})

    def update_player(self, pid, cmd=''):
        p = self.get_player(pid)
        p.update(cmd)
            
    def check_loop(self):
        up = []
        
        for p in self.players:
            up += p.played
            
        if up == self.mem:
            self.counter += 1
            
        else:
            self.mem = up
            self.counter = 0
 
        if self.counter > 9999:
            #for p in self.players:
                #print(p.played, p.requests, p.active_card, p.game_over)
                #print(self.status)
            raise exceptions.InfiniteLoop

    def main(self):
        if self.status != 'waiting':
            for p in self.players:
                p.update()
         
        self.update_game_logs()  
        self.frame += 1

        self.check_loop()

    def rotate_cards(self):
        selections = []

        for p in self.players:
            selections.append(p.unplayed)  
        selections.insert(0, selections.pop(-1))
            
        for p, s in zip(self.players, selections):
            p.new_deck('unplayed', s)
            
    def shuffle_cards(self):
        cards = [c for p in self.players for c in p.unplayed]
        random.shuffle(cards)
        self.shuffle_players()
        
        unplayed = [(p, []) for p in self.players]
        i = 0
        for c in cards:
            unplayed[i][1].append(c)
            i = (i + 1) % len(unplayed)
        for p, deck in unplayed:
            p.new_deck('unplayed', deck)

    def count_votes(self):
        v = 'keep'
        rotate = 0
        keep = 0
        
        for p in self.players:
            if p.vote == 'rotate':
                rotate += 1
            elif p.vote == 'keep':
                keep += 1
            p.set_vote(None)
        
        if rotate > keep:
            self.rotate_cards()
            v = 'rotate'
        elif rotate == keep:
            self.shuffle_cards()
            v = 'shuffle'
            
        self.add_log({'t': 'v', 'v': v})

    def new_turn(self):
        for p in self.players:
            if p.unplayed:
                p.start_turn()
        self.add_log({'t': 'nt'})
    
    def advance_turn(self):
        if self.status != 'playing':
            return 
            
        finished_round = set()
        finished_playing = set()
        finished_turn = set()
        voting = False
        voted = set()
        
        for p in self.players:
            finished_round.add(p.finished_game())
            finished_playing.add(p.done_with_round())
            finished_turn.add(p.done_with_turn())
            if p.active_card == self.vote_card or p.vote:
                voting = True
            voted.add(p.vote)

        if all(finished_round):
            if not self.done():
                if self.round <= self.get_setting('rounds') - 1: 
                    self.new_status('next round')   
                else:
                    self.new_status('new game')
                self.add_log({'t': 'fin', 'w': self.get_winners()})
                return
                
        elif all(finished_playing): 
            for p in self.players:
                p.end_round(not (self.round % self.get_setting('rounds')))
      
        elif voting and all(voted):
            self.count_votes()
            self.new_turn()

        elif all(finished_turn):
            if not voting:
                self.vote_card.start()

#in game operations------------------------------------------------------------------------------

    def check_last(self, player):
        return all({len(p.played) > len(player.played) for p in self.players if p is not player})
        
    def check_first(self, player):
        return all({len(p.played) <= len(player.played) for p in self.players})
        
    def shift_up(self, player):
        self.players.remove(player)
        self.players.insert(0, player)    
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shift_down(self, player):
        self.players.remove(player)
        self.players.append(player)      
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shuffle_players(self):
        random.shuffle(self.players)
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})

    def set_event(self):
        self.event = self.draw_cards('events', 1)[0]
        self.event.start(self)
        self.add_log({'t': 'se', 'c': self.event.copy()})

    def transform(self, c1, name):
        c2 = self.get_card(name, uid=c1.uid)
        owner = self.find_owner(c1)
        if owner and c2:
            owner.replace_card(c1, c2) 
        return c2
                   
    def swap(self, c1, c2):
        self.transform(c1, c2.name)
        self.transform(c2, c1.name)
       
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
                    
            for i, c in enumerate(p.landscapes):
                if c == card:
                    return (p, 'landscapes', i)

    def find_owner(self, c):
        p = None
        for p in self.players:
            if p.find_card_deck(c):
                return p
        
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if 'item' in c.tags or 'equipment' in c.tags]
        
    def get_discard(self):
        return self.discard.copy()
    
    def find_card(self, player, uid):
        for p in self.players:
            
            for c in p.played:
                if c.get_id() == uid:
                    return c
            for c in p.unplayed:
                if c.get_id() == uid:
                    return c
            for c in p.active_spells:
                if c.get_id() == uid:
                    return c
            for c in p.items:
                if c.get_id() == uid:
                    return c
            for c in p.spells:
                if c.get_id() == uid:
                    return c
            for c in p.treasure:
                if c.get_id() == uid:
                    return c
            for c in p.equipped:
                if c.get_id() == uid:
                    return c
            for c in p.selection:
                if c.get_id() == uid:
                    return c
            for c in p.landscapes:
                if c.get_id() == uid:
                    return c
    
    def check_exists(self, uid):
        return self.find_card
        
    def restore(self, c):
        restored = False
        if c in self.discard:
            self.discard.remove(c)
            restored = True
        return restored
            
    def get_last_item(self):
        i = self.get_discarded_items()
        
        if not i: 
            i = self.draw_cards('items')[0]   
        else:
            i = i[0]
            
        return i.copy()

    def is_event(self, name):
        if hasattr(self, 'event'):
            return self.event.name == name 
  
#shop stuff---------------------------------------------------------------------------------------
        
    def fill_shop(self, m=3):
        num = max({m - len(self.shop), 0})
        cards = []
        
        decks = ('play', 'items', 'spells')
        for _ in range(num):
            deck = random.choice(decks)
            cards += self.draw_cards(deck)
            
        self.shop += cards
        
        self.add_log({'t': 'fill', 'cards': self.shop.copy()})

    def restock_shop(self):
        self.shop.clear()
        self.fill_shop()
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            if c.uid == uid:   
                self.shop.remove(c)
                self.fill_shop()  
                return c
                  
#settings stuff---------------------------------------------------------------------------------------

    def get_active_names(self): #will need to update if custom cards can be toggled
        card_names = [name for deck in self.cards for name in self.cards[deck]]
        player_names = [p.name for p in self.players]
        return card_names + player_names

    def get_settings(self):
        return self.settings.copy()
        
    def get_setting(self, setting):
        return self.settings[setting]
        
    def update_settings(self):
        self.settings = SAVE.get_data('settings')  
        if self.mode == 'single':
            self.balance_cpus()
        self.add_log({'t': 'set', 'settings': self.get_settings()})
  
class Game_Copy:
    def __init__(self, g, settings=None, cards=None):
        self.mode = 'turbo'
        
        if settings is None:
            settings = g.settings
        self.settings = settings
        if cards is None:
            cards = g.cards
        self.cards = cards

        self.uid = g.uid
        
        self.status = g.status
        self.current_turn = g.current_turn
        self.round = g.round

        self.players = [p.copy(self) for p in g.players]
        for i in range(len(self.players)):
            self.players[i].set_cards(self, g.players[i])
        
        self.event = g.event.light_sim_copy(self) if g.event else None
        self.shop = [c.light_sim_copy(self) for c in g.shop]
        self.discard = [c.light_sim_copy(self) for c in g.discard[:3]]
        self.vote_card = Vote_Card(self)

        self.mem = []
        self.counter = 0

    def done(self):
        return self.status in ('new game', 'next round')

#player stuff ------------------------------------------------------------------------
   
    def get_player(self, pid):
        for p in self.players:
            if p.pid == pid:
                return p

    def check_last(self, player):
        return all({len(p.played) > len(player.played) for p in self.players if p is not player})
        
    def check_first(self, player):
        return all({len(p.played) <= len(player.played) for p in self.players})
        
    def shift_up(self, player):
        self.players.remove(player)
        self.players.insert(0, player)    
        
    def shift_down(self, player):
        self.players.remove(player)
        self.players.append(player)     
        
    def shuffle_players(self):
        random.shuffle(self.players)

#card stuff---------------------------------------------------------------------------------------
     
    def get_new_uid(self):
        uid = self.uid
        self.uid += 1
        return uid
     
    def draw_cards(self, deck='play', num=1):
        deck = self.cards[deck]
        weights = [val['weight'] for val in deck.values()]
        
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        
        for i, name in enumerate(cards):
            cards[i] = self.get_card(name)

        return cards
        
    def get_card(self, name, uid=None):
        if uid is None:
            uid = self.get_new_uid()
        for deck in self.cards.values():
            info = deck.get(name)
            if info is not None:  
                if info.get('custom'):
                    if not info.get('test'):
                        card = getattr(custom_cards, info['classname'])(self, uid)
                    else:
                        card = getattr(testing_card, info['classname'])(self, uid)
                else:
                    card = getattr(func, info['classname'])(self, uid)
                return card
            
    def transform(self, c1, name):
        c2 = self.get_card(name, uid=c1.uid)
        owner = self.find_owner(c1)
        if owner and c2:
            owner.replace_card(c1, c2) 
        return c2
                   
    def swap(self, c1, c2):
        self.transform(c1, c2.name)
        self.transform(c2, c1.name)

    def find_owner(self, c):
        p = None
        for p in self.players:
            if p.find_card_deck(c):
                return p
        
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if 'item' in c.tags or 'equipment' in c.tags]
        
    def get_discard(self):
        return self.discard.copy()
    
    def find_card(self, player, uid):
        for p in self.players:
            
            for c in p.played:
                if c.get_id() == uid:
                    return c
            for c in p.unplayed:
                if c.get_id() == uid:
                    return c
            for c in p.active_spells:
                if c.get_id() == uid:
                    return c
            for c in p.items:
                if c.get_id() == uid:
                    return c
            for c in p.spells:
                if c.get_id() == uid:
                    return c
            for c in p.treasure:
                if c.get_id() == uid:
                    return c
            for c in p.equipped:
                if c.get_id() == uid:
                    return c
            for c in p.selection:
                if c.get_id() == uid:
                    return c
            for c in p.landscapes:
                if c.get_id() == uid:
                    return c
    
    def check_exists(self, uid):
        return self.find_card
        
    def restore(self, c):
        restored = False
        if c in self.discard:
            self.discard.remove(c)
            restored = True
        return restored
            
    def get_last_item(self):
        i = self.get_discarded_items()
        
        if not i: 
            i = self.draw_cards('items')[0]   
        else:
            i = i[0]
            
        return i.copy()

    def is_event(self, name):
        if hasattr(self, 'event'):
            return self.event.name == name 
  
#shop stuff---------------------------------------------------------------------------------------
        
    def fill_shop(self, m=3):
        num = max({m - len(self.shop), 0})
        cards = [] 
        decks = ('play', 'items', 'spells')
        for _ in range(num):  
            deck = random.choice(decks)
            cards += self.draw_cards(deck)     
        self.shop += cards

    def restock_shop(self):
        self.shop.clear()
        self.fill_shop()
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            if c.uid == uid:      
                self.shop.remove(c)
                self.fill_shop()
                return c

#update info stuff---------------------------------------------------------------------------------------
            
    def new_status(self, stat):
        self.status = stat
            
    def check_loop(self):
        up = []
        for p in self.players:
            up += p.played
            
        if up == self.mem:
            self.counter += 1  
        else:
            self.mem = up
            self.counter = 0
 
        if self.counter > 100:
            self.debug()
            raise exceptions.InfiniteLoop
                     
#settings stuff---------------------------------------------------------------------------------------

    def get_setting(self, setting):
        return self.settings[setting]

#turn stuff-----------------------------------------------------------------------------------------------
   
    def main(self):
        if self.status != 'waiting':
            for p in self.players:
                p.update()

        self.check_loop()

    def rotate_cards(self):
        selections = []

        for p in self.players:
            selections.append(p.unplayed)  
        selections.insert(0, selections.pop(-1))
            
        for p, s in zip(self.players, selections):
            p.new_deck('unplayed', s)
            
    def shuffle_cards(self):
        cards = [c for p in self.players for c in p.unplayed]
        random.shuffle(cards)
        self.shuffle_players()
        
        unplayed = [(p, []) for p in self.players]
        i = 0
        for c in cards:
            unplayed[i][1].append(c)
            i = (i + 1) % len(unplayed)
        for p, deck in unplayed:
            p.new_deck('unplayed', deck)
            
    def count_votes(self):
        rotate = 0
        keep = 0
        
        for p in self.players:
            if p.vote == 'rotate':
                rotate += 1
            elif p.vote == 'keep':
                keep += 1
            p.set_vote(None)
            
        if rotate > keep:
            self.rotate_cards()
        elif rotate == keep:
            self.shuffle_cards()

    def new_turn(self):
        for p in self.players:
            if p.unplayed:
                p.start_turn()
            
    def advance_turn(self):
        if self.status != 'playing':
            return 
            
        finished_round = set()
        finished_playing = set()
        finished_turn = set()
        voting = False
        voted = set()
        
        for p in self.players:
            finished_round.add(p.finished_game())
            finished_playing.add(p.done_with_round())
            finished_turn.add(p.done_with_turn())
            if p.active_card == self.vote_card or p.vote:
                voting = True
            voted.add(p.vote)

        if all(finished_round):
            if not self.done():
                
                if self.round <= self.get_setting('rounds') - 1: 
                    self.new_status('next round')   
                else:
                    self.new_status('new game')
                
        elif all(finished_playing): 
            for p in self.players:
                p.end_round(True)
     
        elif all(voted):
            self.count_votes()
            self.new_turn()

        elif all(finished_turn):
            if not voting:
                self.vote_card.start()
            
#ending stuff---------------------------------------------------------------------------------------

    def get_winners(self):
        hs = max({p.score for p in self.players})
        return [p.pid for p in self.players if p.score == hs]

    def debug(self):
        for p in self.players:
            print(p.requests, p.selection, p.get_selection(), p.unplayed, p.gone, p.vote)
        print(self.status, self.done())
        
            
    
                


            
    
                

