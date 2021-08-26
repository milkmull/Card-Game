import random
import time
from math import exp
from constants import *

def unpack_decision(d):
    if d['t'] == 'select':     
        d = (d['t'], d['s']) 
    elif d['t'] == 'wait':
        d = (d['t'], None)
        
    return d
    
def get_deck(c):
    if 'treasure' in c.tags:
        return 'treasure'
    elif 'landscape' in c.tags:
        return 'landscapes' 
    elif 'item' in c.tags or 'equipment' in c.tags:
        return 'items' 
    elif 'spell' in c.tags:   
        return 'spell'  
    else: 
        return 'unplayed'

class Player:
    def __init__(self, game, pid, ss, auto=False):
        self.game = game
        self.pid = pid
        
        self.tags = ['player']
        
        self.name = f'Player {self.pid}'

        self.selecting = True #if player has to make a selection
        self.is_turn = False #indicates if player can go
        self.gone = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        
        self.auto = auto
        self.turbo = False
        self.thinking = False
        self.sims = 0
        self.seed = 0
        self.max_sims = 1
        self.turns = 0
        self.choices = 0
        self.timeout = 0
        self.info = []
        self.decision = {}
        self.tree = []
        self.diff = 0
        self.temp_tree = []
        self.len_check = 0
        self.stable_counter = 0
        self.max_stable = 0
        self.sim_timer = 0
        self.timer = 0
        
        self.invincible = False

        self.active_card = None

        self.max = 60 #if not self.auto else 2
        self.ft = 0
        self.rt = 0
        self.tt = 0
        self.coin = None
        self.dice = None

        self.played = [] #cards that have already been played
        self.unplayed = [] #cards that have not yet been played
        self.items = [] #items in hand
        self.selection = [] #cards in the selection pane
        self.selected = [] #cards the player has selected
        self.equipped = [] #cards waiting for condition to be met
        self.ongoing = []
        self.treasure = []
        self.spells = [] #spell cards in your hand
        self.landscapes = []

        self.requests = []
        
        self.master_log = []
        self.log = []
        self.temp_log = []
        
        self.attempted = []
        
        self.score = self.game.get_setting('ss')
        
        self.safety_pin = [0, []] #times, card
        
    def __eq__(self, other):
        return self.pid == other.get_id()
       
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name

    def get_id(self):
        return self.pid
        
    def get_name(self):
        return self.name

    def set_name(self, name):
        names = self.game.get_active_names()
        
        while True:
            c = len(name) + 2
            
            if any(name == n for n in names):
                name = name.center(c)
                c += 2
            else:
                break

        self.name = name
        self.add_log({'t': 'cn', 'pid': self.pid, 'name': name})
        return True

#starting stuff--------------------------------------------------------------------------------------------                

    def reset(self):
        self.master_log.clear()
        self.log.clear()
        self.temp_log.clear()
        self.reset_brain()
        
        self.selecting = False
        self.is_turn = False
        self.gone = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.invincible = False

        self.ft = 0
        self.rt = 0
        self.coin = None
        self.dice = None
        
        self.active_card = None
        
        self.requests.clear()
        self.played.clear()
        self.unplayed.clear()
        self.selection.clear()
        self.selected.clear()
        self.equipped.clear()
        self.items.clear()
        self.spells.clear()
        self.ongoing.clear()
        self.treasure.clear()
        self.landscapes.clear()
        
        self.score = self.game.get_setting('ss')
        
        if self.auto and not self.turbo:
            
            self.set_difficulty(self.game.get_setting('diff'))

    def start(self):
        self.reset()
        
        self.draw_cards('landscapes')
        self.draw_cards('unplayed', self.game.get_setting('cards'))
        self.draw_cards('items', self.game.get_setting('items'))
        self.draw_cards('spells', self.game.get_setting('spells'))
        self.new_deck('treasure', [self.game.get_card('gold coins')])

    def new_round(self):
        items = self.items.copy()
        spells = self.spells.copy()
        
        self.reset()
        
        self.items = items
        self.spells = spells
        
        self.draw_cards('landscapes')
        self.draw_cards('unplayed', self.game.get_setting('cards'))
        self.draw_cards('items', max(self.game.get_setting('items') - len(self.items), 0))
        self.draw_cards('spells', max(self.game.get_setting('spells') - len(self.spells), 0))
 
#card stuff--------------------------------------------------------------------------------------

    def sort_cards(self, c): 
        if c.name in ('the void', 'negative zone'):
            return 4
        elif any(tag in ('animal', 'plant', 'human', 'monster', 'treasure') for tag in c.tags):  
            return 0 
        elif any(tag in ('item', 'equipment') for tag in c.tags):   
            return 1   
        elif 'spell' in c.tags:    
            return 2   
        else:   
            return 3

    def draw_cards(self, pdeck, num=1):
        if pdeck in ('played', 'unplayed'):
            gdeck = 'play'
            
        elif pdeck in ('items', 'spells', 'treasure', 'landscapes'):
            gdeck = pdeck
            
        cards = self.game.draw_cards(gdeck, num)
        self.new_deck(pdeck, getattr(self, pdeck) + cards)
        
        if pdeck == 'landscapes':
            
            for c in cards:
                
                self.ongoing.append(c)
                
        if len(cards) == 1:     
            self.add_log({'t': f'd{pdeck[0]}', 'c': cards[0]})
            
        self.add_log({'t': 'draw', 'deck': pdeck, 'num': len(cards)})
                
        return cards
   
    def add_card(self, c, deck):
        self.new_deck(deck, getattr(self, deck) + [c])
        
    def remove_card(self, c, deck):
        self.new_deck(deck, [o for o in getattr(self, deck) if o != c])
        
    def get_played_card(self, i):
        if i in range(len(self.played)):
            return self.played[i]
   
    def play_card(self, c=None, d=False):
        if c is None and self.unplayed:
            c = self.unplayed[0]
            
        if c:
            self.cancel_request()

            if c in self.unplayed:
                self.unplayed.remove(c)

            self.add_log({'t': 'play', 'c': c.copy(), 'd': d})
            
            c.start(self)

            if c not in self.played and not d:
                self.played.append(c.copy())
                self.gone = True
                
    def can_cancel(self):
        c = self.active_card
        return c.wait == 'cast' or (c.wait == 'select' and c in self.items) or c.name == 'gold coins'

    def cancel(self):
        if self.requests:   
            c = self.requests[0]
            
            if self.can_cancel():
                self.requests.pop(0)
                self.cancel_request()
                
    def new_deck(self, deck, cards):
        setattr(self, deck, cards)
        self.add_log({'t': 'nd', 'deck': deck, 'cards': cards.copy()})

    def discard_card(self, c, d=False, ogd=False):
        deck = ''
        
        if c in self.equipped:
            self.unequip(c)
            
        if c in self.items:
            self.items.remove(c)
            deck = 'items'
            self.add_log({'t': 'ui', 'c': c.copy(), 'd': d})
            
        if ogd:
            self.remove_og(c)
            
        if c in self.unplayed:
            self.unplayed.remove(c)
            deck = 'unplayed'
            
        if c in self.played: 
            self.played.remove(c)
            deck = 'played'
            
        if c in self.treasure:
            self.treasure.remove(c)
            deck = 'treasure'
            
        if c in self.landscapes:
            self.landscapes.remove(c)
            deck = 'landscapes'
            
        if c in self.spells:
            self.spells.remove(c)
            deck = 'spells'
        
        if not d:
            self.game.discard.append(c)
            
        if deck:
            self.new_deck(deck, getattr(self, deck))

    def has_landscape(self, ls):
        return any(landscape.name == ls for landscape in self.landscapes)     
    
    def get_spells(self):
        return [c for c in self.ongoing if 'spell' in c.tags]
        
    def get_items(self):
        return [c for c in self.items + self.equipped if c.wait is None]
        
    def give_card(self, c, target):
        self.discard_card(c, d=True)
        
        deck = get_deck(c)
        target.new_deck(deck, getattr(target, deck) + [c])
        
    def has_card(self, deck, name):
        return any(c.name == name for c in getattr(self, deck))
        
    def steal_card(self, c, target):
        deck = get_deck(c)
        self.discard_card(c, d=True)
        target.add_card(c, deck)
        
    def steal_random_card(self, pdeck, target):
        deck = getattr(target, pdeck)
        
        if deck:
            
            c = random.choice(deck)
            target.discard_card(c, d=True)
            self.add_card(c, pdeck)
            
        else:
            
            if pdeck == 'treasure':
                self.draw_cards('treasure')

#equipment stuff------------------------------------------------------------------------------------

    def equip(self, c):
        if c in self.items:
            
            self.remove_card(c, 'items')
            self.add_card(c, 'equipped')
            self.ongoing.append(c)
        
    def unequip(self, c): 
        self.remove_card(c, 'equipped')
        self.add_card(c, 'items')

        if c in self.ongoing:
            self.ongoing.remove(c)
        
#buying stuff---------------------------------------------------------------------------------------

    def can_buy(self):
        return any(c.name == 'gold coins' for c in self.treasure) and not self.game_over

    def buy_card(self, uid, free=False):
        c = self.game.buy(self, uid)
        
        if c and (self.can_buy() or free):

            if any(tag in ('item', 'equipment') for tag in c.tags):
                deck = 'items'
                
            elif 'spell' in c.tags: 
                deck = 'spells'
                
            elif 'treasure' in c.tags:
                deck = 'treasure'
                
            else:   
                deck = 'unplayed'
                
            if not free:
                
                self.remove_coins()
            
            self.add_card(c, deck)
            
            self.add_log({'t': 'buy', 'c': c})
                
        return c
    
    def remove_coins(self):
        for c in self.treasure:
        
            if c.name == 'gold coins':
                
                self.new_deck('treasure', [t for t in self.treasure if t != c])
                
                return

#request stuff--------------------------------------------------------------------------------------
              
    def add_request(self, c, wait):
        c.wait = wait
        self.requests.append(c)
        
    def start_request(self, c):
        if c.wait in ('select', 'cast'):
            
            if c.wait == 'select':
            
                cards = c.get_selection(self)
                
            elif c.wait == 'cast':
                
                cards = [p for p in self.game.players if p.can_cast(c)]

            if cards:
 
                if cards != self.selection:

                    self.new_deck('selection', cards)
                    self.selecting = True
                    
            else:
                
                c.wait = None
                
        elif c.wait == 'flip':
            
            self.coin = -1
            self.ft = self.max
            
        elif c.wait == 'roll':
            
            self.dice = -1
            self.rt = self.max
        
    def process_request(self):
        c = self.requests[0]

        if c is not self.active_card:
        
            self.cancel_request()
            self.active_card = c
            self.add_log({'t': 'aac', 'c': self.active_card, 'w': self.active_card.wait, 'cancel': self.can_cancel()})
            self.start_request(c)
            
        confirm = False

        if c.wait == 'flip' and self.ft == 1:

            if self.coin is not None:
                
                c.wait = None
                c.coin(self, self.coin)
                
                confirm = True
                
        elif c.wait == 'roll' and self.rt == 1:
            
            if self.dice is not None:
                
                c.wait = None
                c.roll(self, self.dice)
                
                confirm = True

        elif c.wait == 'select':
            
            if self.selected:
                
                c.wait = None
                c.select(self, len(self.selected))
                
                confirm = True
            
        elif c.wait == 'cast':
            
            if self.selected:
                
                c.wait = None
                target = self.selected.pop(0)
                self.cast(target, c)
                
                confirm = True

        if c.wait is None:
            
            self.requests.pop(0)
            self.cancel_request()
            
        elif confirm:
            
            self.start_request(c)

        if self.turbo and self.requests:
            
            if self.safety_pin[1] != self.requests:
                
                self.safety_pin[1] = self.requests.copy()
                self.safety_pin[0] = 0
                
            else:
                
                self.safety_pin[0] += 1
        
                if self.safety_pin[0] > 100:
                    
                    print('ex', self.pid, self.requests, self.active_card, self.selection, self.selected, self.spells, c.wait)
                    print('')
                    print(self.master_log + self.log)
                    
                    self.ongoing[99]
                    
    def cancel_request(self):
        if self.selecting:
        
            self.new_deck('selection', [])
            self.new_deck('selected', [])
            self.selecting = False
            
        if self.flipping:
        
            self.flipping = False
            self.coin = None
            
        if self.rolling:
        
            self.rolling = False
            self.dice = None
        
        if self.active_card is not None:
        
            self.active_card.mode = 0
            self.active_card = None
            self.add_log({'t': 'rac'})
 
    def select(self, card):
        if self.selection:
        
            for c in self.selection:
                
                if c == card:
                    
                    self.selected.append(c)

                    return
                    
        else:
            
            if self.is_turn and not (self.gone or self.requests):
                
                for c in self.unplayed:
                
                    if c == card:
                        
                        self.play_card(c)
                        
                        return
                        
            if not self.game_over:
        
                for c in self.items:
                    
                    if c == card and c not in self.requests:
                        
                        if c.can_use(self):
                        
                            c.start(self)
                        
                        return
                        
                for c in self.spells:
                    
                    if c == card and c not in self.requests:

                        c.wait = 'cast'
                        self.requests.append(c)
                        
                        return
                        
                for c in self.treasure:
                    
                    if c == card and c not in self.requests:
                        
                        if hasattr(c, 'start'):
                        
                            c.start(self)
                            
                        return
                        
                for c in self.equipped:
                    
                    if c == card and c not in self.requests:   

                        self.unequip(c)
                            
                        return

    def flip(self):
        if self.auto and not self.turbo:
            
            if self.ft == self.max - 1:
                
                if self.timer != 30:
                    return
                
                self.add_log({'t': 'cfs'})
    
        if self.flipping and self.ft > 0:
                
            if self.ft <= self.max / 2:
            
                if self.ft == self.max / 2:
                
                    self.add_log({'t': 'cfe', 'coin': self.coin, 'ft': self.ft - 2, 'd': False})
                
            else:
                
                self.coin = random.choice((1, 0))
            
        self.ft = max(self.ft - 1, 0)
        
        if self.ft == 0:
            
            self.flipping = False
            self.coin = None

    def roll(self):
        if self.auto and not self.turbo and self.timer_up():
            
            if self.rt == self.max - 1:
                
                if self.timer != 30:
                    return
                
                self.add_log({'t': 'drs'})
                
        if self.rolling and self.rt > 0:
                
            if self.rt <= self.max / 2:
            
                if self.rt == self.max / 2:
            
                    self.add_log({'t': 'dre', 'dice': self.dice, 'rt': self.rt - 2, 'd': False})
                
            else:
                
                self.dice = random.randrange(0, 6) + 1
            
        self.rt = max(self.rt - 1, 0)
        
        if self.rt == 0:
            
            self.rolling = False
            self.dice = None
        
    def cast(self, target, c):
        self.discard_card(c, d=True, ogd=True)

        if c in self.spells:
            self.spells.remove(c)  
        if c in self.requests and c is not self.active_card:
            self.requests.remove(c)

        target.ongoing.append(c)
        if hasattr(c, 'start'):
            c.start(target)
        
        self.add_log({'t': 'cast', 'c': c.copy(), 'target': target, 'd': False})
    
    def can_cast(self, s):
        return not any(s.name == c.name and not c.mult for c in self.get_spells())
    
#ongoing stuff--------------------------------------------------------------------------------------
   
    def og(self):
        self.ongoing.sort(key=self.sort_cards)

        og = self.ongoing.copy()
        
        for c in og:
            
            if hasattr(c, 'ongoing'):

                done = c.ongoing(self)
                        
                if done and c in self.ongoing:
                        
                    self.ongoing.remove(c)
                        
            else:

                self.ongoing.remove(c)
       
    def transfer_og(self, c, p):
        while c in self.ongoing:
            
            self.ongoing.remove(c)
            
        p.ongoing.append(c)
       
    def remove_og(self, c):
        while c in self.ongoing:
            self.ongoing.remove(c)
            
        if 'spell' in c.tags:
            self.add_log({'t': 'rs', 'c': c})
       
#log stuff------------------------------------------------------------------------------------------

    def add_log(self, log):
        log['u'] = self.pid
        self.log.append(log)

    def update_logs(self):
        self.master_log += self.log
        self.temp_log += self.log
        self.game.update_player_logs(self.pid)
        
        self.log.clear()
        
    def get_logs(self, type):
        logs = []
        
        for log in self.log:
            
            if log.get('t') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
        
    def get_m_logs(self, type):
        logs = []
    
        for log in self.master_log:
            
            if log.get('t') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
        
    def get_all_logs(self, type):
        logs = []
        
        for log in self.log + self.master_log:
            
            if log.get('t') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
                
    def check_log(self, type):
        return any(log.get('t') == type and log.get('d') == False for log in self.log)

#update stuff---------------------------------------------------------------------------------------

    def update(self, cmd=''):
        if 'select' in cmd and (self.dice is self.coin is None):

            uid = int(cmd.split()[1])
            card = self.game.find_card(self, uid)

            if card:
            
                self.select(card)
 
        elif cmd == 'cancel':
            
            self.cancel()

        elif cmd == 'play' and self.is_turn:

            self.play_card()
            
        elif cmd == 'flip' or self.flipping:
            
            if self.coin == -1:
                
                self.add_log({'t': 'cfs'})
                self.flipping = True
                
            self.flip()

        elif cmd == 'roll' or self.rolling:
            
            if self.dice == -1:
                
                self.add_log({'t': 'drs'})
                self.rolling = True
            
            self.roll()

        if self.requests:
            
            self.process_request()

        self.og()

        self.update_logs()

        self.game.advance_turn()

#turn stuff-----------------------------------------------------------------------------------------

    def start_turn(self):
        self.is_turn = True
        self.gone = False
        
        if self.auto:
            self.timer = random.randrange(60, 120)
        
    def end_turn(self):
        self.is_turn = False
        self.gone = False
        
    def finished_turn(self):
        return (self.gone or not (self.gone or self.unplayed)) and not self.requests
        
    def finished_game(self):
        return not (self.unplayed or self.requests)
        
    def end_game(self):
        if hasattr(self.game.event, 'end'):
            
            self.game.event.end(self)
            
        for c in self.treasure:

            if hasattr(c, 'end'):
                
                c.end(self)
                
        self.game_over = True
        
#sim stuff------------------------------------------------------------------------------------------

    def sim_copy(self, game):
        return game.get_player(self.pid)

    def start_copy(self, game, ref):
        self.turbo = True
        self.auto = True
        self.max = 2
        
        self.selecting = ref.selecting
        self.is_turn = ref.is_turn
        self.gone = ref.gone
        self.flipping = ref.flipping
        self.rolling = ref.rolling
        self.game_over = ref.game_over
        self.invincible = ref.invincible

        self.ft = min(ref.ft, 2)
        self.rt = min(ref.rt, 2)
        self.coin = ref.coin
        self.dice = ref.dice

        self.played = [c.sim_copy(game) for c in ref.played]
        self.unplayed = [c.sim_copy(game) for c in ref.unplayed]
        self.items = [c.sim_copy(game) for c in ref.items]
        self.selection = [c.sim_copy(game) for c in ref.selection]
        self.selected = [c.sim_copy(game) for c in ref.selected]
        self.equipped = [c.sim_copy(game) for c in ref.equipped]
        self.ongoing = [c.sim_copy(game) for c in ref.ongoing]
        self.treasure = [c.sim_copy(game) for c in ref.treasure]
        self.spells = [c.sim_copy(game) for c in ref.spells]
        self.landscapes = [c.sim_copy(game) for c in ref.landscapes]
        self.requests = [c.sim_copy(game) for c in ref.requests]
        
        if ref.active_card is not None:
        
            self.active_card = next(c for c in self.requests if c == ref.active_card)
            
        else:
        
            self.active_card = None
        
        self.master_log = ref.master_log.copy()
        self.log = ref.log.copy()
        self.temp_log = []
        
    def unpack_log(self, g):
        p = g.get_player(self.pid)

        gain = p.score - self.score
        lead = round(sum(p.score - o.score for o in g.players) / (len(g.players) - 1))
        score = gain + (lead * 2)
        
        cards = self.get_selection()
        
        d = []
        
        for log in p.temp_log:
            
            if log['t'] == 'select':
                
                c = log['s']
                
                if c in cards:
                    
                    d.append(unpack_decision(log))
                    
            elif log['t'] == 'wait':
                
                d.append(unpack_decision(log))
        if d:
            
            d = d[0]
        
            keys = [d[0] for d in self.tree]
            vals = [d[1] for d in self.tree]
            
            if d in keys:   
                
                i = keys.index(d)
            
                info = vals[i]
                count, ave = info
                
                info[0] += 1
                info[1] = ave + ((score - ave) // count + 1)
                
            else:

                self.tree.append([d, [1, score]])

        temp_tree = [t[0] for t in self.tree]
        
        if self.is_turn:
        
            for i in range(len(temp_tree)):
                
                t = temp_tree[i]
                
                if t[0] == 'wait':
                    
                    temp_tree.pop(i)
                    self.tree.pop(i)
                    
                    break
        
        if temp_tree == self.temp_tree:
            
            self.stable_counter += 1
            
        else:
            
            self.stable_counter = 0
            self.temp_tree = temp_tree
        
    def simulate(self):
        g = self.game.copy()
        p = g.get_player(self.pid)
        
        t = time.time()

        while not (g.done() or time.time() - t > self.sim_timer):
            g.main()

        self.unpack_log(g)
        
    def get_decision(self):
        self.tree.sort(key=lambda info: info[1][1], reverse=True)
        cards = self.get_selection()

        for d in self.tree:
            
            t, c = d[0]
            
            if (t == 'select' and c in cards) or (not self.selection and t == 'wait'):

                return d[0]

    def reset_brain(self):
        self.stable_counter = 0 
        self.decision = None
        self.tree.clear()
        
        self.timer = random.randrange(60, 120)
      
    def is_stable(self):
        return self.stable_counter > self.max_stable // 4
 
#auto stuff-----------------------------------------------------------------------------------------

    def timer_up(self):
        return self.timer <= 0

    def set_difficulty(self, diff):
        p = len(self.game.players)
        self.diff = diff
        
        if diff == 0:
            self.max_stable = 0  
        elif diff == 1:
            self.max_stable = 10 // len(self.game.players)
        elif diff == 2:
            self.max_stable = 50 // len(self.game.players)
        elif diff == 3:
            self.max_stable = 200 // len(self.game.players)
        elif diff == 4:
            self.max_stable = 400 // len(self.game.players)
            
        self.sim_timer = self.get_sim_time()
        
    def get_sim_time(self):
        total_update_time = 0.006
        players = len([p for p in self.game.players if p.auto and not p.turbo])
        return max(((1 / fps) - total_update_time) / players, 0)

    def get_selection(self):
        cards = [c for c in self.items if c.can_use(self)] + self.spells
        
        if self.can_buy():
            cards += [c for c in self.treasure if c.name == 'gold coins']
        if self.is_turn and not self.gone:      
            cards += self.unplayed  
        if self.selection:  
            cards += self.selection
            
        return cards

    def set_cmd(self):
        if self.game.done():  
            return
            
        if not self.turbo and self.max_stable > 0:

            if not self.is_stable():
            
                self.simulate()
                self.decision = None
            
            elif self.timer_up():

                d = self.get_decision()

                if d:
                    type = d[0]
                        
                    if type == 'select':
                        if random.choice((0, 1)):
                            self.decision = d
                            return 'select'
                            
                        else:
                            self.stable_counter = 0
                            
                    else:
                        self.stable_counter = 0
                        
                else:
                    self.reset_brain()
                    
        elif self.turbo or (not self.turbo and self.timer_up()):
                
            cards = self.get_selection()
            
            if cards:

                if self.is_turn or self.selection or (not (self.is_turn or self.selection) and random.choice(range(len(cards) + 1)) > 0):
                    
                    return 'select'
                    
                else:
                    
                    self.add_log({'t': 'wait'})
                            
    def auto_select(self):
        s = None
        
        if not self.turbo and self.max_stable > 0:
            
            if self.decision:
                
                s = self.decision[1]
                
        else:
    
            if self.selection:
                
                s = random.choice(self.selection)
                
            elif not self.requests:
                
                cards = self.get_selection()

                if cards:

                    s = random.choice(cards)
                    
                else:
                    
                    return
          
        if s is not None:

            self.add_log({'t': 'select', 's': s})
            self.reset_brain()
                
        return s
       
    def auto_update_logs(self):
        self.master_log += self.log
        self.temp_log += self.log
        
        if not self.turbo:
        
            self.game.update_player_logs(self.pid)
        
        self.log.clear()
       
    def auto_update(self):
        cmd = self.set_cmd()

        if cmd == 'select':
            
            card = self.auto_select()

            if card is not None:

                self.select(card)

        if self.coin is not None:
            
            self.flipping = True
            self.flip()
                
        if self.dice is not None:

            self.rolling = True
            self.roll()

        if self.requests:

            self.process_request()
            
        self.og()
        
        self.timer -= 1
        
        self.auto_update_logs()

        self.game.advance_turn()  

#point stuff-----------------------------------------------------------------------------------------
 
    def steal(self, c, sp, target, d=False):  
        sp = target.get_robbed(c, sp, self, d)
        
        self.score += sp
        
        if sp:
            
            self.add_log({'t': 'sp', 'c': c.copy(), 'target': target, 'sp': sp, 'd': d})
            
        return sp
            
    def get_robbed(self, c, rp, robber, d=False):
        rp = rp if self.score >= rp else self.score
        
        if self.invincible:
            
            self.add_log({'t': 'iv', 'c': c})
            rp = 0

        self.score -= rp
        
        if rp:
            
            self.add_log({'t': 'rp', 'c': c.copy(), 'robber': robber, 'rp': rp, 'd': d})
        
        return rp
        
    def gain(self, c, gp, d=False):
        self.score += gp
        
        if gp:
        
            self.add_log({'t': 'gp', 'c': c.copy(), 'gp': gp, 'd': d})
            
        return gp
        
    def lose(self, c, lp, d=False):
        lp = lp if self.score >= lp else self.score
        
        self.score -= lp
        
        if lp:

            self.add_log({'t': 'lp', 'c': c.copy(), 'lp': lp, 'd': d})
            
        return lp
        
    def give(self, c, gp, target, d=False):
        gp = gp if self.score >= gp else self.score
        
        self.score -= gp
        
        target.score += gp
        
        if gp:

            self.add_log({'t': 'give', 'c': c.copy(), 'target': target, 'gp': -gp, 'd': d})
            
        return gp
        
        
        
        
        
        