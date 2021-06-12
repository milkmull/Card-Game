import random
import time
from math import exp

types = ('play', 'select')

def unpack_decision(d):
    if d['t'] == 'select':
            
        d = (d['t'], d['s'])
        
    elif d['t'] == 'play':
        
        d = (d['t'], d['c'])
        
    return d

class Player:
    def __init__(self, game, pid, ss, auto=False):
        self.game = game

        self.pid = pid
        
        self.name = f'Player {self.pid}'

        self.selecting = True #if player has to make a selection
        self.click = False
        self.play = False #attempt to play top card
        self.is_turn = False #indicates if player can go
        self.gone = False
        self.finished = False #indicates when player has completed their turn
        self.flipping = False
        self.rolling = False
        self.round_over = False
        self.game_over = False
        self.round_over = False
        self.ogp = False
        
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
        
        self.invincible = False

        self.active_card = None

        self.max = 80 #if not self.auto else 2
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
        self.used_items = []
        
        self.landscape = None

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
       
    def get_image(self, mini=False):
        return self.pc.text
        
    def get_spells(self):
        return [c for c in self.ongoing if c.type == 'spell']
        
    def get_items(self):
        return [c for c in self.items + self.equipped if c.wait is None]
        
    def count_type(self, type):
        return len([1 for c in self.played if c.type == type])
        
    def get_id(self):
        return self.pid

#starting stuff--------------------------------------------------------------------------------------------                

    def start(self):
        self.selecting = True #if player has to make a selection
        self.click = False
        self.play = False #attempt to play top card
        self.is_turn = False #indicates if player can go
        self.gone = False
        self.finished = False #indicates when player has completed their turn
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.round_over = False
        self.ogp = False
        
        self.invincible = False

        self.active_card = None
        
        self.ft = 0
        self.rt = 0
        self.coin = None
        self.dice = None

        self.played.clear()
        self.unplayed.clear()
        self.items.clear()
        self.selection.clear()
        self.selected.clear()
        self.equipped.clear()
        self.ongoing.clear()
        self.treasure.clear()
        self.spells.clear()
        self.used_items.clear()
        
        self.requests.clear()
        
        self.master_log.clear()
        self.log.clear()
        self.temp_log.clear()
        self.reset_brain()
        
        self.set_score()
        self.set_landscape()
        
        if self.auto and not self.turbo:
            
            self.set_difficulty(self.game.get_setting('diff'))
        
    def set_landscape(self):
        self.landscape = self.game.draw_cards(deck='landscapes')[0]
        self.add_og(self.landscape)
        
        self.log.append({'t': 'sl', 'c': self.landscape.copy()})
        
    def set_score(self):
        self.score = self.game.get_setting('ss')
        
    def new_round(self):
        self.ongoing = [c for c in self.ongoing if c in self.equipped]
        self.requests.clear()
        self.selection.clear()
        self.selected.clear()
        self.played.clear()
        self.unplayed.clear()
        self.used_items.clear()
        
        self.log.clear()
        self.master_log.clear()
        self.temp_log.clear()
        self.reset_brain()
        
        self.draw_items(max(self.game.get_setting('items') - len(self.items), 0))
        self.draw_spells(max(self.game.get_setting('spells') - len(self.spells), 0))
        
        self.is_turn = False
        
        self.finished = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.round_over = False
        self.ogp = False
        
        self.invincible = False

        self.active_card = None
        
        self.selecting = True
        
        self.set_landscape()
        
    def reset(self):
        self.selecting = True 
        self.click = False
        self.play = False 
        self.is_turn = False 
        self.gone = False
        self.finished = False 
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.round_over = False
        self.ogp = False
        
        self.invincible = False

        self.active_card = None

        self.max = 60
        self.ft = 0
        self.rt = 0
        self.coin = None
        self.dice = None

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
        
        self.landscape = None

        self.requests = []
        
        self.reset_brain()
        
        self.master_log = []
        self.log = []
        self.temp_log = []
        
        self.set_score()
        
#draft stuff-----------------------------------------------------------------------------------------

    def new_draft(self, cards):
        self.selecting = True

        self.new_deck('selection', cards)
        
    def draft(self, card):
        if self.selecting and card:

            for c in self.selection:
                        
                if c == card:
                    
                    self.unplayed.append(c)
                    
                    self.selection.remove(c)
                    
                    self.log.append({'t': 'd', 'c': c})
                    
                    self.selecting = False
                    
                    break
                
#turn stuff-----------------------------------------------------------------------------------------

    def start_turn(self):
        self.finished = False
        self.is_turn = True
        
    def check_end_round(self):
        return not (self.requests or self.unplayed) and self.round_over
        
    def check_end_game(self):
        return not (self.requests or self.unplayed) and self.round_over and self.game_over
        
    def end_turn(self):
        if not self.requests:
        
            self.play = False
            self.is_turn = False
            self.gone = False
            self.finished = True
            self.ogp = False
                
    def end_round(self):
        if hasattr(self.game.event, 'end'):
            
            self.game.event.end(self)
            
        self.round_over = True
                
    def end_game(self):         
        for c in self.treasure:

            if hasattr(c, 'end'):
                
                c.end(self)
        
        self.game_over = True
  
    def turn(self):
        if self.is_turn and not (self.gone or self.requests):
        
            self.cancel_select()
            
            if self.unplayed:
            
                self.play_card()
                
                self.gone = True
            
    def play_card(self, c=None, d=False):
        self.active_card = None
        
        if not c:
        
            c = self.unplayed.pop(0)
            
        elif c in self.unplayed and self.game.get_setting('fp'):
            
            c = self.unplayed.pop(self.unplayed.index(c))

        self.log.append({'t': 'play', 'c': c.copy(), 'd': False})
        
        c.start(self)
        
        if c not in self.played and not d:
        
            self.played.append(c.copy())
            
    def add_og(self, c):
        self.ongoing.append(c.copy())
            
    def og(self, cond):
        self.ongoing.sort(key=self.sort_cards)

        og = self.ongoing.copy()
        
        for c in og:

            if c.tag == cond:

                done = c.ongoing(self)
                        
                if done and c in self.ongoing:

                    if c.type == 'equipment':
                        
                        self.discard_item(c)
                        
                    else:
                        
                        self.ongoing.remove(c)

    def sort_cards(self, c):  
        if c.type in ('animal', 'plant', 'human', 'monster', 'treasure'):
            
            return 0
            
        elif c.type in ('item', 'equipment'):
            
            return 1
            
        elif c.type == 'spell':
            
            return 2
            
        else:
            
            return 3
            
    def process_request(self):
        self.requests.sort(key=self.sort_cards)
        
        c = self.requests[0]

        if c is not self.active_card:

            self.active_card = c
            
            if self.selection:
            
                self.cancel_select()
            
            if c.wait != 'cast':

                c.start_request(self)
                
            else:
                
                self.start_cast(c)
                
            self.log.append({'t': 'aac', 'c': self.active_card, 'w': self.active_card.wait})

        if c.wait == 'coin' and self.ft == 1:

            if self.coin is not None:
                
                c.wait = None

                c.coin(self, self.coin)
                
        elif c.wait == 'dice' and self.rt == 1:
            
            if self.dice is not None:
                
                c.wait = None
                
                c.roll(self, self.dice)

        elif c.wait == 'select':
            
            if self.selected:
                
                c.wait = None

                c.select(self, len(self.selected))
            
        elif c.wait == 'cast':
            
            if self.selected:
                
                c.wait = None

                target = self.selected.pop(0)
                
                self.cast(target, c)

        if c.wait is None:
            
            self.requests.pop(0)
            
            self.active_card = None
            
            self.cancel_select()
            
            self.log.append({'t': 'rac'})

        if self.turbo and self.requests:
            
            if self.safety_pin[1] != self.requests:
                
                self.safety_pin[1] = self.requests.copy()
                self.safety_pin[0] = 0
                
            else:
                
                self.safety_pin[0] += 1
        
                if self.safety_pin[0] > 20:
                    
                    print('ex', self.pid, self.requests, self.active_card, self.selection, self.selected, self.spells, self.ft, self.rt)
                    print('')
                    print(self.master_log + self.log)
                    
                    self.ongoing[99]
          
    def select(self, card):
        if self.selection:
        
            for c in self.selection:
                
                if c == card:
                    
                    self.selected.append(c)
                    
                    return
                    
        else:
            
            if self.game.get_setting('fp') and self.is_turn and not self.gone:
                
                for c in self.unplayed:
                
                    if c == card and c not in self.requests:
                        
                        self.unplayed.insert(0, self.unplayed.pop(self.unplayed.index(c)))
                        
                        self.turn()
                        
                        return
        
            for c in self.items:
                
                if c == card and c not in self.requests:
                    
                    c.start(self)
                    
                    return
                    
            for c in self.spells:
                
                if c == card and c not in self.requests:

                    self.start_cast(c)
                    
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
      
            for c in self.game.shop:
                
                if c == card and self.can_buy():

                    self.buy_card(c.uid)
                    
                    return
         
    def cancel(self):
        if self.requests:
                
            c = self.requests[0]
            
            if c.wait == 'cast' or (c.wait == 'select' and c in self.items) or c.name == 'gold coins':
                
                self.requests.pop(0)
                
                self.active_card = None
                
                self.cancel_select()
                
                self.log.append({'t': 'rac'})
 
    def update(self, cmd='', card=None):
        if cmd == 'select' and card is not None and not self.check_end_game() and not ((self.flipping and self.coin != -1) or (self.rolling and self.dice != -1)):
        
            self.select(card)
 
        elif cmd == 'cancel':
            
            self.cancel()

        elif cmd == 'play':

            self.turn()
            
        elif cmd == 'flip' and self.coin == -1:
            
            self.coin = 0
            self.log.append({'t': 'cfs'})
            
        elif cmd == 'roll' and self.dice == -1:
            
            self.dice = 0
            self.log.append({'t': 'drs'})

        if self.gone and not self.ogp:
            
            self.og('play')
            
            self.ogp = True

        if self.flipping and self.coin != -1:
            
            self.flip()
                
        if self.rolling and self.dice != -1:

            self.roll()

        if self.requests:
            
            self.process_request()
            
        else:
            
            self.active_card = None
            
        if self.gone and not self.requests:
            
            self.end_turn()
            
        self.og('cont')
        
        if self.score == 0 and self.game.get_setting('score wrap'):
            
            self.score = self.game.get_setting('ss') * 2

        self.master_log += self.log
        self.temp_log += self.log
        self.game.update_player_logs(self.pid)
        
        self.log.clear()

        self.game.check_advance()
        
    def buy_card(self, uid):
        c = self.game.buy(self, uid)
        
        if c and self.can_buy():
            
            if c.type == 'item' or c.type == 'equipment':
                
                self.items.append(c)
                
            elif c.type == 'spell':
                
                self.spells.append(c)
                
            elif c.type == 'treasure':
                
                self.treasure.append(c)
                
            else:
                
                self.unplayed.append(c)
                
            self.remove_coins()
            
            self.log.append({'t': 'buy', 'c': c, 'ctype': c.type})
                
        return c
        
    def can_buy(self):
        return any(c.name == 'gold coins' for c in self.treasure)
        
    def remove_coins(self):
        for c in self.treasure:
        
            if c.name == 'gold coins' and c in self.treasure:
                
                self.treasure.remove(c)
                
                self.log.append({'t': 'rc', 'c': c})
                
                return

#sim stuff------------------------------------------------------------------------------------------

    def start_turbo(self):
        self.turbo = True
        self.auto = True
        self.max = 2

    def sim_copy(self, game):
        return game.get_player(self.pid)

    def start_copy(self, game, ref):
        self.turbo = True
        self.auto = True
        self.max = 2
        self.seed = 99
        
        self.selecting = ref.selecting
        self.click = ref.click
        self.play = ref.play
        self.is_turn = ref.is_turn
        self.gone = ref.gone
        self.finished = ref.finished
        self.flipping = ref.flipping
        self.rolling = ref.rolling
        self.game_over = ref.game_over
        self.round_over = ref.round_over
        self.ogp = ref.ogp
        
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
        self.used_items = [c.sim_copy(game) for c in ref.used_items]
        
        self.landscape = ref.landscape.sim_copy(game) if ref.landscape is not None else None

        self.requests = [c.sim_copy(game) for c in ref.requests]
        
        if ref.active_card is not None:
        
            self.active_card = next(c for c in self.requests if c == ref.active_card)
            
        else:
        
            self.active_card = None
        
        self.master_log = ref.master_log.copy()
        self.log = [L.copy() for L in ref.log]
        self.temp_log = []
        
    def unpack_log(self, g):
        p = g.get_player(self.pid)

        gain = p.score - self.score
        lead = sum(p.score - o.score for o in g.players) / (len(g.players) - 1)
        score = gain + lead

        d = [unpack_decision(log) for log in p.temp_log if log.get('t') in types and not log.get('d')]
        
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
                
        choices = len(self.tree)
        
        if self.choices == choices:
        
            self.timeout += 1
            
        else:
            
            self.choices = choices
            self.timeout = 0
            
        if self.timeout > self.max_sims // 3:
            
            self.sims = self.max_sims
        
    def simulate(self):
        if self.turns >= 25 or (self.turns < 25 and self.game.counter % len(self.game.players) == self.pid):

            g = self.game.copy()
            p = g.get_player(self.pid)

            while not (g.done or g.current_turn > self.turns):
                
                g.main()

            self.unpack_log(g)
            
            self.sims += 1
        
    def get_decision(self):
        self.tree.sort(key=lambda info: info[1][1], reverse=True)

        cards = self.get_selection() + self.selection
        
        for d in self.tree:
            
            t, c = d[0]
            
            if (t == 'play' and c in self.unplayed) or (t == 'select' and c in cards):
            
                return d[0]

    def reset_brain(self):
        self.sims = 0 
        self.decision = None
        self.tree.clear()
 
#auto stuff-----------------------------------------------------------------------------------------

    def set_difficulty(self, diff):
        p = len(self.game.players)
        
        if diff == 0:
            
            self.max_sims = 0
            
        elif diff == 1:
            
            self.max_sims = 5 // len(self.game.players)
            
        elif diff == 2:
            
            self.max_sims = 25 // len(self.game.players)
            
        elif diff == 3:
            
            self.max_sims = 100 // len(self.game.players)
            
        elif diff == 4:
            
            self.max_sims = 200 // len(self.game.players)
 
        if self.max_sims:
            
            turns = ((len(self.game.players) * (self.game.get_setting('cards') + self.game.get_setting('items') + self.game.get_setting('spells') + 1)) + 1.77) / 1.61
            t = exp(0.0654 * turns) / 1000
            
            self.turns = max(int(turns / (30 * len(self.game.players) * t)) - 5, 1)
 
    def can_play(self):
        return self.game.phase != 'draft' and self.is_turn and not self.gone and not self.requests
        
    def can_select(self, c):
        if self.game.phase == 'draft':
            
            return c in self.selection
            
        else:
            
            cards = self.get_selection()
            
            if self.game.get_setting('fp'):
                
                cards += self.unplayed
                
            return c in cards
        
    def get_selection(self):
        cards = [c for c in self.items if c.can_use(self)] + self.spells
        
        if self.can_buy():
        
            cards += self.game.shop
        
        if self.game.get_setting('fp') and self.is_turn and not self.gone:
                
            cards += self.unplayed
            
        return cards

    def set_cmd(self):
        if self.game.done:
            
            return
            
        if not self.turbo and self.max_sims:

            if self.sims < self.max_sims:
            
                self.simulate()
                self.decision = None
            
            elif self.sims >= self.max_sims:

                d = self.get_decision()

                if d:

                    type = d[0]

                    if type == 'play':

                        self.decision = d

                        return 'play'
                        
                    elif type == 'select':
                        
                        if (self.selection or self.game.phase == 'draft' or len(self.selection) == 1) or random.choice((0, 1)):

                            self.decision = d
                        
                            return 'select'
                            
                        else:
                            
                            self.sims = len(self.tree) // 2
                        
                elif self.max_sims > 0:
                
                    self.simulate()
                    
        elif self.turbo or self.max_sims == 0:

            if self.game.phase == 'draft' or self.selection:
                
                if self.selecting:
                    
                    return 'select'
                    
                else:
                    
                    return
                
            cards = self.get_selection()
            
            if cards and (not self.requests and random.choice(range(len(cards) + 1)) != 0):
                
                return 'select'
            
            elif self.can_play():
                
                if self.game.get_setting('fp'):
                    
                    return 'select'
                    
                else:
            
                    return 'play'
                            
    def auto_select(self):
        s = None
        
        if not self.turbo and self.max_sims:
            
            if self.decision:
                
                s = self.decision[1]
                
        else:
    
            if self.game.phase == 'draft' or self.selection:
                
                s = random.choice(self.selection)
                
            elif not self.requests:
                
                cards = self.get_selection()

                if cards:

                    s = random.choice(cards)
                    
                else:
                    
                    return
          
        if s is not None:
          
            self.log.append({'t': 'select', 's': s}) #move to select function
                
        return s
        
    def auto_update(self):
        cmd = self.set_cmd()

        if cmd == 'select':
            
            card = self.auto_select()

            if card is not None:
                
                self.reset_brain()
            
                if self.game.phase == 'draft':
                
                    self.draft(card)
                    self.game.check_rotate()
                    
                else:
                
                    self.select(card)

        elif cmd == 'play':
                
            self.turn()
            self.reset_brain()

        if self.gone and not self.ogp:

            self.og('play')
            self.ogp = True

        if self.flipping:
            
            self.flip()
                
        if self.rolling:

            self.roll()

        if self.requests:

            self.process_request()
            
        else:
            
            self.active_card = None
            
        if self.gone and not self.requests:
            
            self.end_turn()
            
        self.og('cont')
        
        if self.score == 0 and self.game.get_setting('score wrap'):
            
            self.score = self.game.get_setting('ss') * 2

        self.master_log += self.log
        self.temp_log += self.log
        
        if not self.turbo:
        
            self.game.update_player_logs(self.pid)
        
        self.log.clear()

        self.game.check_advance()
        
        #print('out', self.requests, self.pid, self.ft)

#request stuff ------------------------------------------------------------------------------------------
        
    def set_name(self, name):
        self.name = name
        self.log.append({'t': 'cn', 'pid': self.pid, 'name': name})
        return True
        
    def start_cast(self, c):
        self.new_selection(c, [p for p in self.game.players if p.can_cast(c)])
        
        if c.wait == 'select':
        
            c.wait = 'cast'
        
    def cast(self, target, c):
        target.ongoing.append(c)
        self.spells.remove(c)
        
        self.cancel_select() 
        
        self.log.append({'t': 'cast', 'c': c.copy(), 'target': target, 'd': False})
        
    def dry_cast(self, target, c):
        target.ongoing.append(c)
        
        self.log.append({'t': 'cast', 'c': c.copy(), 'target': target, 'd': False})
        
    def new_flip(self, c, r=False):
        self.coin = -1
        self.flipping = True
        
        self.ft = self.max
        
        c.wait = 'coin'

        if c is not self.active_card:
        
            self.requests.append(c)
            self.active_card = None
            self.coin = None
            
        self.cancel_select()
        
    def flip(self):
        if self.auto and not self.turbo:
            
            if self.ft == self.max - 1:
                
                self.log.append({'t': 'cfs'})
    
        if self.flipping and self.ft > 0:
                
            self.coin_flip()
            
        self.ft = max(self.ft - 1, 0)
        
        if self.ft == 0:
            
            self.flipping = False
            self.coin = None
        
    def coin_flip(self):
        if self.ft <= self.max / 2:
            
            if self.ft == self.max / 2:
            
                self.log.append({'t': 'cfe', 'coin': self.coin, 'ft': self.ft - 2, 'd': False})
            
        else:
            
            self.coin = random.choice((1, 0))

    def new_roll(self, c):
        self.dice = -1
        self.rolling = True
        
        self.rt = self.max

        c.wait = 'dice'

        if c is not self.active_card:
            
            self.requests.append(c)
            self.active_card = None
            self.dice = None
            
        self.cancel_select()
        
    def roll(self):
        if self.auto and not self.turbo:
            
            if self.rt == self.max - 1:
                
                self.log.append({'t': 'drs'})
                
        if self.rolling and self.rt > 0:
                
            self.dice_roll()
            
        self.rt = max(self.rt - 1, 0)
        
        if self.rt == 0:
            
            self.rolling = False
            self.dice = None
            
    def dice_roll(self):
        if self.rt <= self.max / 2:
            
            if self.rt == self.max / 2:
        
                self.log.append({'t': 'dre', 'dice': self.dice, 'rt': self.rt - 2, 'd': False})
            
        else:
            
            self.dice = random.randrange(0, 6) + 1

    def new_selection(self, c, cards, r=False): #empty list could cause problems with active card waiting for selection
        if cards:
            
            if cards != self.selection:
            
                self.selection.clear()

                self.selection = cards
                self.selecting = True
                
                self.rolling = self.flipping = False
                
                self.log.append({'t': 'sels', 'cards': cards.copy(), 'c': c})
            
            c.wait = 'select'

            if c is not self.active_card:
            
                self.requests.append(c)
                
                self.active_card = None
                
        else:
            
            c.wait = None
       
    def cancel_select(self):
        self.selection.clear()
        self.selected.clear()
        
        self.selecting = False
        
        self.log.append({'t': 'sele'})

#log stuff -----------------------------------------------------------------------------------------------

    def get_logs(self, type):
        logs = []
        
        for log in self.log:
            
            if log.get('t') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
                
    def check_log(self, c, type):
        return any(log.get('t') == type and log.get('d') == False for log in self.log)
        
    def get_m_logs(self, type):
        logs = []
    
        for log in self.master_log:
            
            if log.get('t') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
        
    def remove_log(self, log):
        if log in self.master_log:
            
            self.master_log.remove(log)
            
        if log in self.log:
            
            self.log.remove(log)
            
    def new_deck(self, deck, cards):
        setattr(self, deck, cards)
        
        self.log.append({'t': 'nd', 'deck': deck, 'cards': cards.copy()})
        
    def clear_deck(self, deck):
        getattr(self, deck).clear()
        
        self.log.append({'t': 'cd', 'd': deck})
            
#item stuff-------------------------------------------------------------------------------------------------------------

    def use_item(self, c):
        self.log.append({'t': 'ui', 'c': c.copy(), 'd': False})
        
        self.used_items.append(c)
        
        self.discard_item(c)

    def draw_items(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.items + self.equipped) > 10:
                
                break
        
            item = self.game.draw_cards('items')
            
            if item:
                
                self.items += item
                
                self.log.append({'t': 'di', 'c': self.items[-1].copy(), 'd': d})

            else:
                
                break
                
    def steal_item(self, target, c=None):
        if c is None:
    
            items = [c for c in target.items if c not in target.requests]
            
            if items:
                
                c = random.choice(items)
                
            else:
                
                return
                
        else:
            
            if c in target.items:
                
                target.items.remove(c)

        if c in target.equipped:
            
            target.unequip(c)

        self.items.append(c)
        
        self.log.append({'t': 'si', 'target': target, 'c': c})
            
    def give_item(self, c, target):
        if c in self.equipped:
            
            self.unequip(c)

        if c in self.items and c not in self.requests:
            
            self.items.remove(c)
            target.items.append(c)
            
            self.log.append({'t': 'gi', 'target': target, 'c': c})
            
    def add_item(self, c):
        self.items.append(c)
        
        self.log.append({'t': 'ai', 'c': c})
            
    def discard_item(self, c, d=False):
        if c in self.equipped:
            
            self.unequip(c)
            
        if c in self.ongoing:
            
            self.ongoing.remove(c)
            
        if c in self.items:
            
            self.items.remove(c)
            
            self.log.append({'t': 'disc', 'c': c.copy()})
            
        if not d:
            
            self.game.discard.append(c)

    def has_item(self, name):
        return any(c.name == name for c in self.items + self.equipped)
        
    def equip(self, c):
        if c in self.items:
        
            self.items.remove(c)
            self.ongoing.append(c)
            self.equipped.append(c)
            
            self.log.append({'t': 'eq', 'c': c})
        
    def unequip(self, c):  
        c = c.copy()
        if c not in self.ongoing:
            print(c, self.ongoing, self.items, self.equipped, self.master_log + self.log)
        self.items.append(c)
        self.ongoing.remove(c)
        self.equipped.remove(c)
        
        self.log.append({'t': 'ueq', 'c': c})
        
#spell stuff-----------------------------------------------------------------------------------------
        
    def draw_spells(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.spells) > 10:
                
                break
        
            spell = self.game.draw_cards('spells')
            
            if spell:
                
                self.spells += spell
                
                self.log.append({'t': 'ds', 'c': self.spells[-1].copy(), 'd': d})

            else:
                
                break
                
    def steal_spell(self, target):
        spells = target.spells.copy()
        
        if spells:
            
            c = random.choice(spells)
            target.spells.remove(c)
            self.spells.append(c)
            
            self.log.append({'t': 'si', 'target': target, 'c': c})
            
    def give_spell(self, c, target):
        if c in self.spells:
            
            self.spells.remove(c)
            target.spells.append(c)
            
            self.log.append({'t': 'gi', 'target': target, 'c': c})
        
    def has_spell(self, name):
        return any(c.name == name for c in self.get_spells())
        
    def add_spell(self, c):
        if self.can_cast(c):
            
            self.ongoing.append(c)
            
            self.log.append({'t': 'as', 'c': c})

    def remove_spell(self, c):
        if c in self.ongoing:
        
            self.ongoing.pop(self.ongoing.index(c))
            
            self.log.append({'t': 'rs', 'c': c})

    def can_cast(self, s):
        return not any(s.name == c.name and not c.mult for c in self.get_spells())
        
#treasure stuff-----------------------------------------------------------------------------------------

    def draw_treasure(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.treasure) > 10:
                
                break
        
            t = self.game.draw_cards('treasure')
            
            if t:
                
                self.treasure += t
                
                self.log.append({'t': 'dt', 'c': self.treasure[-1].copy(), 'd': d})
                
                if hasattr(t, 'draw'):
                    
                    t.draw(self)

            else:
                
                break
            
    def steal_treasure(self, target, c=None):
        treasure = [c for c in target.treasure if c not in target.requests]
        
        if c is not None:
            
            for t in treasure:
                
                if t == c:
                    
                    target.treasure.remove(c)
                    self.treasure.append(c)
                    
                    self.log.append({'t': 'st', 'target': target, 'c': c})
        
        elif treasure:
            
            c = random.choice(treasure)
            target.treasure.remove(c)
            self.treasure.append(c)
            
            self.log.append({'t': 'st', 'target': target, 'c': c})
            
        else:
            
            self.draw_treasure()
            
    def give_treasure(self, c, target):
        if c in self.treasure and c not in self.requests:
            
            self.treasure.remove(c)
            target.treasure.append(c)
            
            self.log.append({'t': 'gt', 'target': target, 'c': c})
            
    def use_treasure(self, c):
        if c in self.treasure:
            
            self.treasure.remove(c)
            
            self.log.append({'t': 'ut', 'c': c})
            
    def add_treasure(self, c):
        self.treasure.append(c)
        
        self.log.append({'t': 'at', 'c': c})
        
#landscape stuff-----------------------------------------------------------------------------------------
        
    def get_landscape(self):
        return self.landscape.name
        
    def has_landscape(self, ls):
        return self.landscape.name == ls
        
#unplayed stuff--------------------------------------------------------------------------------------

    def add_unplayed(self, c):
        self.unplayed.append(c)
        
        self.log.append({'t': 'au', 'c': c})
        
#point stuff-----------------------------------------------------------------------------------------
 
    def steal(self, c, sp, target, d=False):  
        sp = target.get_robbed(c, sp, self, d)
        
        self.score += sp
        
        if sp:
            
            self.log.append({'t': 'sp', 'c': c.copy(), 'target': target, 'sp': sp, 'd': d})
            
        return sp
            
    def get_robbed(self, c, rp, robber, d=False):
        rp = rp if self.score >= rp else self.score
        
        if self.invincible:
            
            rp = 0

        self.score -= rp
        
        if rp:
            
            self.log.append({'t': 'rp', 'c': c.copy(), 'robber': robber, 'rp': rp, 'd': d})
        
        return rp
        
    def gain(self, c, gp, d=False):
        self.score += gp
        
        if gp:
        
            self.log.append({'t': 'gp', 'c': c.copy(), 'gp': gp, 'd': d})
            
        return gp
        
    def lose(self, c, lp, d=False):
        lp = lp if self.score >= lp else self.score
        
        self.score -= lp
        
        if lp:

            self.log.append({'t': 'lp', 'c': c.copy(), 'lp': lp, 'd': d})
            
        return lp
        
    def give(self, c, gp, target, d=False):
        gp = gp if self.score >= gp else self.score
        
        self.score -= gp
        
        target.score += gp
        
        if gp:

            self.log.append({'t': 'give', 'c': c.copy(), 'target': target, 'gp': -gp, 'd': d})
            
        return gp
        
        
        
        
        
        