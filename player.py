import random
import copy

types = ('play', 'select', 'wait')

class RequestError(Exception):
    pass

def parse_log(type, log):
    return [L for L in log if L.get('type') == type]

class Player:
    def __init__(self, game, pid, ss, auto=False):
        self.game = game

        self.pid = pid
        
        self.name = 'player {}'.format(self.pid)

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
        self.max_sims = 50
        self.info = []
        self.decision = {}
        
        self.invincible = False

        self.active_card = None

        self.max = 30 #if not self.auto else 2
        self.tf = 0
        self.tr = 0
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
        return 'player {}'.format(self.pid)
        
    def __repr__(self):
        return 'player {}'.format(self.pid)
       
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
        
#network stuff------------------------------------------------------------------------------------------

    def get_info(self, attr):    
        if attr == 'coin':
            
            return self.coin
            
        elif attr == 'dice':
            
            return self.dice
            
        elif attr == 'flipping':
            
            return self.flipping
            
        elif attr == 'rolling':
            
            return self.rolling
            
        elif attr == 'score':
            
            return self.score
            
        elif attr == 'is_turn':

            return self.is_turn

        elif attr == 'selection':
            
            return [(c.name, c.get_id()) for c in self.selection]
            
        elif attr == 'unplayed':
            
            return [(c.name, c.uid) for c in self.unplayed]
            
        elif attr == 'played':
            
            return [(c.name, c.uid) for c in self.played]
            
        elif attr == 'equipped':
            
            return [(c.name, c.uid) for c in self.equipped]
            
        elif attr == 'items':
            
            return [(c.name, c.uid) for c in self.items]
            
        elif attr == 'spells':
            
            return [(c.name, c.uid) for c in self.spells]
            
        elif attr == 'ongoing':
            
            return [(c.name, c.uid) for c in self.get_spells()]
            
        elif attr == 'treasure':
            
            return [(c.name, c.uid) for c in self.treasure]
            
        elif attr == 'log':
            
            return
            
        elif attr == 'active_card':
            
            return (self.active_card.name, self.active_card.uid) if self.active_card is not None else False
            
        elif attr == 'landscape':
            
            return (self.landscape.name, self.landscape.uid) if self.landscape is not None else False

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
        
        self.tf = 0
        self.tr = 0
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
        
    def set_landscape(self):
        self.landscape = self.game.draw_cards(deck='landscapes')[0]
        self.add_og(self.landscape)
        
    def set_score(self):
        self.score = self.game.get_setting('ss')
        
    def new_round(self):
        self.ongoing.clear()
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

        self.max = 30
        self.tf = 0
        self.tr = 0
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
        
        self.selection = cards
        
    def draft(self, card):
        if self.selecting and card:

            for c in self.selection:
                        
                if c == card:
                    
                    self.unplayed.append(c)
                    
                    self.selection.remove(c)
                    
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

        self.log.append({'type': 'play', 'card': c.copy(), 'd': False})
        
        c.start(self)
        
        if c not in self.played and not d:
        
            self.played.append(c.copy())
            
    def add_og(self, c):
        self.ongoing.append(c.copy())
            
    def og(self, cond):
        self.ongoing.sort(key=self.sort_cards)

        i = 0
        
        while i in range(len(self.ongoing)):

            c = self.ongoing[i]

            if c.tag == cond:
                    
                try:
                
                    done = c.ongoing(self)
                            
                    if done:
                        
                        self.ongoing.pop(i)

                        continue
                        
                except ValueError as e:

                    self.ongoing.pop(i)
                    
                    continue
                    
            i += 1
            
    def sort_cards(self, c):  
        if c.type in ('animal', 'plant', 'huamn', 'monster', 'treasure'):
            
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
                
                self.cast(c)

        if c.wait == 'coin' and self.tf == 1:

            if self.coin is not None:
                
                c.wait = None

                c.coin(self, self.coin)
                
        elif c.wait == 'dice' and self.tr == 1:
            
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

                p = self.selected.pop(0)
                
                p.ongoing.append(c)
                self.spells.remove(c)
                
                self.cancel_select() 
                
                self.log.append({'type': 'cast', 'card': c.copy(), 'target': p, 'd': False})
            
        if c.wait is None:
            
            self.requests.pop(0)
            
            self.active_card = None
            
            self.cancel_select()

        if self.turbo and self.requests:
            
            if self.safety_pin[1] != self.requests:
                
                self.safety_pin[1] = self.requests.copy()
                self.safety_pin[0] = 0
                
            else:
                
                self.safety_pin[0] += 1
        
                if self.safety_pin[0] > 20:
                    
                    print('ex', self.pid, self.requests, self.active_card, self.selection, self.selected, self.spells, self.tf, self.tr)
                    
                    for p in self.game.players:
                
                        print(p.pid, p.master_log + p.log)
                    
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

                    self.cast(c)
                    
                    return
                    
            for c in self.treasure:
                
                if c == card:
                    
                    if hasattr(c, 'start'):
                    
                        c.start(self)
                        
                    return
                    
            for c in self.equipped:
                
                if c == card and c.wait is None:
                    
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
                
    def flip(self):
        if self.flipping and self.tf > 0:
                
            self.coin_flip()
            
        self.tf = max(self.tf - 1, 0)
        
        if self.tf == 0:
            
            self.flipping = False
            self.coin = None
            
    def roll(self):
        if self.rolling and self.tr > 0:
                
            self.dice_roll()
            
        self.tr = max(self.tr - 1, 0)
        
        if self.tr == 0:
            
            self.rolling = False
            self.dice = None
         
    def update(self, cmd='', card=None):
        if cmd == 'select' and card is not None and not self.check_end_game() and not ((self.flipping and self.coin != -1) or (self.rolling and self.dice != -1)):
        
            self.select(card)
 
        elif cmd == 'cancel':
            
            self.cancel()

        elif cmd == 'play':

            self.turn()
            
        elif cmd == 'flip':
            
            self.coin = 0
            
        elif cmd == 'roll':
            
            self.dice = 0

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
        self.game.update_logs(self.pid, self.log.copy())
        
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
            
            self.log.append({'type': 'buy', 'card': c, 'd': False})
                
        return c
        
    def can_buy(self):
        return any(c.name == 'gold coins' for c in self.treasure)
        
    def remove_coins(self):
        for c in self.treasure:
        
            if c.name == 'gold coins' and c in self.treasure:
                
                self.treasure.remove(c)
                
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

        self.tf = min(ref.tf, 2)
        self.tr = min(ref.tr, 2)
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
        
        self.master_log = [L.copy() for L in ref.master_log]
        self.log = [L.copy() for L in ref.log]
        self.temp_log = []
        
    def simulate(self, attr):
        info = [0, []]
        
        turns = 99
        
        def stop(g):
            return g.done or g.current_turn > turns

        g = self.game.copy()
        
        p = g.get_player(self.pid)

        while not stop(g):
            
            g.main()
            
        p = g.get_player(self.pid)
        
        lead = sum(p.score - o.score for o in g.players) / (len(g.players) - 1)
            
        info = [p.score + lead, next((log for log in getattr(p, attr) if log.get('type') in types), None)]
            
        return info
        
    def think(self):
        info = self.simulate('temp_log')
        
        if info[1]:
            
            score, d = info
            
            keys, vals = [i[0] for i in self.info], [i[1] for i in self.info]
            
            if d in vals:

                key = keys[vals.index(d)]
                count, ave = key
                
                key[0] += 1
                key[1] = ave + ((score - ave) // count + 1)
                
            else:
                
                self.info.append([[1, score], d])

            self.sims += 1
        
    def get_decision(self):
        info = [i[1] for i in sorted(self.info, key=lambda info: info[0][1], reverse=True)]
        
        if self.game.phase == 'draft' and self.selecting:
            
            d = next(i for i in info if i.get('card') in self.selection)
            
        else:
            
            d = info[0]

        return d

    def reset_brain(self):
        self.sims = 0
        self.info.clear()   
        self.decision = None
        
        if self.game.phase != 'draft':
        
            self.max_sims = 2
            
        else:
            
            self.max_sims = 2
 
#auto stuff-----------------------------------------------------------------------------------------

    def can_play(self):
        return self.game.phase != 'draft' and self.is_turn and not self.gone and not self.requests
        
    def get_selection(self):
        return [c for c in self.items if c.can_use(self) and c not in self.equipped] + self.spells + [c for c in self.game.shop if self.can_buy()]

    def set_cmd(self):
        if self.game.done:
            
            return
            
        if not self.turbo:
        
            if self.sims < self.max_sims:
            
                self.think()
                self.decision = None
            
            elif self.sims >= self.max_sims:

                d = self.get_decision()

                type = d.get('type')

                if type == 'play':
                    
                    self.reset_brain()
                    self.decision = d

                    return 'play'
                    
                elif type == 'select':
                    
                    self.reset_brain()
                    self.decision = d
                    
                    return 'select'
                    
                else:
                
                    self.think()
                    
        else:
            
            if self.game.phase == 'draft' or self.selection:
                
                if self.selecting:
                    
                    return 'select'
                    
                else:
                    
                    return
                
            cards = self.get_selection()
            
            if self.game.get_setting('fp') and self.is_turn and not self.gone:
                
                cards += self.unplayed
            
            if cards and (not self.requests and random.randrange(len(cards)) != 0):
                
                return 'select'
            
            elif self.can_play():
                
                if self.game.get_setting('fp'):
                    
                    return 'select'
                    
                else:
            
                    return 'play'
                            
    def auto_select(self):
        s = None
        
        if not self.turbo:
            
            if self.decision:
                
                s = self.decision.get('card')
                
        else:
    
            if self.game.phase == 'draft' or self.selection:
                
                s = random.choice(self.selection)
                
            elif not self.requests:
                
                cards = self.get_selection()
                
                if self.game.get_setting('fp') and self.is_turn and not self.gone:
                    
                    cards += self.unplayed
                    
                if cards:
                
                    s = random.choice(cards)
                    
                else:
                    
                    return
          
        if s:
          
            self.log.append({'type': 'select', 'card': s}) #move to select function
                
        return s
        
    def auto_update(self):
        cmd = self.set_cmd()

        if cmd == 'select':
            
            card = self.auto_select()
            
            if card is not None:
            
                if self.game.phase == 'draft':
                
                    self.draft(card)
                
                    self.game.check_rotate()
                    
                else:
                
                    self.select(card)

        elif cmd == 'play':
                
            self.turn()

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
        
            self.game.update_logs(self.pid, self.log.copy())
        
        self.log.clear()

        self.game.check_advance()
        
        #print('out', self.requests, self.pid, self.tf)

#request stuff ------------------------------------------------------------------------------------------
        
    def set_name(self, name):
        self.name = name
        return True
        
    def cast(self, c):
        self.new_selection(c, [p for p in self.game.players if p.can_cast(c.name)])
        
        if c.wait == 'select':
        
            c.wait = 'cast'
        
    def new_flip(self, c, r=False):
        self.coin = -1
        self.flipping = True
        
        self.tf = self.max
        
        c.wait = 'coin'
        
        if c is not self.active_card:
        
            self.requests.append(c)
            
            self.active_card = None
            
        self.cancel_select()
        
    def coin_flip(self):
        if self.tf <= self.max / 2:
            
            if self.tf <= 1:
            
                self.log.append({'type': 'cf', 'coin': self.coin, 'd': False})
            
        else:
            
            self.coin = random.choice((1, 0))
        
    def new_roll(self, c):
        self.dice = -1
        self.rolling = True
        
        self.tr = self.max

        c.wait = 'dice'
        
        if c is not self.active_card:
            
            self.requests.append(c)
            
            self.active_card = None
            
        self.cancel_select()
            
    def dice_roll(self):
        if self.tr <= self.max / 2:
            
            if self.tr <= 1:
        
                self.log.append({'type': 'rd', 'dice': self.dice, 'd': False})
            
        else:
            
            self.dice = random.randrange(0, 6) + 1

    def new_selection(self, c, cards, r=False): #empty list could cause problems with active card waiting for selection
        if cards:
            
            self.selection.clear()

            self.selection = cards
            self.selecting = True
            
            self.rolling = self.flipping = False
            
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

#log stuff -----------------------------------------------------------------------------------------------

    def get_logs(self, type):
        logs = []
        
        for log in self.log:
            
            if log.get('type') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
                
    def check_log(self, c, type):
        return any(log.get('type') == type and log.get('d') == False for log in self.log)
        
    def get_m_logs(self, type):
        logs = []
    
        for log in self.master_log:
            
            if log.get('type') == type and not log.get('d'):
                
                logs.append(log)
                
        return logs
        
    def remove_log(self, log):
        if log in self.master_log:
            
            self.master_log.remove(log)
            
        if log in self.log:
            
            self.log.remove(log)
            
#item stuff-------------------------------------------------------------------------------------------------------------

    def use_item(self, c):
        self.log.append({'type': 'ui', 'card': c.copy(), 'd': False})
        
        self.used_items.append(c)
        
        self.discard_item(c)

    def draw_items(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.items + self.equipped) > 10:
                
                break
        
            item = self.game.draw_cards('items')
            
            if item:
                
                self.items += item
                
                self.log.append({'type': 'di', 'card': self.items[-1].copy(), 'd': d})

            else:
                
                break
  
    def discard_item(self, c, d=False):
        if c in self.items:
        
            self.items.remove(c)
            
        if c in self.ongoing:
            
            self.ongoing.remove(c)
            
        if c in self.equipped:
            
            self.equipped.remove(c)
            
        if not d:
            
            self.game.discard.append(c)
        
    def has_item(self, name):
        return any(c.name == name for c in self.items + self.equipped)
        
    def equip(self, c):
        if c in self.items:
        
            self.items.remove(c)
            self.ongoing.append(c)
            self.equipped.append(c)
        
    def unequip(self, c):
        self.items.append(c)
        self.ongoing.remove(c)
        self.equipped.remove(c)
        
#spell stuff-----------------------------------------------------------------------------------------
        
    def draw_spells(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.spells) > 10:
                
                break
        
            spell = self.game.draw_cards('spells')
            
            if spell:
                
                self.spells += spell
                
                self.log.append({'type': 'ds', 'card': self.spells[-1].copy(), 'd': d})

            else:
                
                break
        
    def has_spell(self, name):
        return any(c.name == name for c in self.get_spells())

    def remove_spell(self, c):
        if c in self.ongoing:
        
            self.ongoing.pop(self.ongoing.index(c))

    def can_cast(self, s):
        return not any(s == c.name and not c.mult for c in self.get_spells())
        
#treasure stuff-----------------------------------------------------------------------------------------

    def draw_treasure(self, num=1, d=False):
        for _ in range(num):
            
            if len(self.treasure) > 10:
                
                    break
        
            t = self.game.draw_cards('treasure')
            
            if t:
                
                self.treasure += t
                
                self.log.append({'type': 'dt', 'card': self.treasure[-1].copy(), 'd': d})
                
                if hasattr(t, 'draw'):
                    
                    t.draw(self)

            else:
                
                break
            
    def steal_treasure(self, target):
        treasure = [c for c in target.treasure if c not in target.requests]
        
        if treasure:
            
            c = random.choice(treasure)
            
            target.treasure.remove(c)
            
            self.treasure.append(c)
            
    def take_treasure(self, c, target):
        if c in target.treasure and c not in target.requests:
            
            target.treasure.remove(c)
            
            self.treasure.append(c)
        
#landscape stuff-----------------------------------------------------------------------------------------
        
    def get_landscape(self):
        return self.landscape.name
        
    def has_landscape(self, ls):
        return self.landscape.name == ls
        
#point stuff-----------------------------------------------------------------------------------------
 
    def steal(self, c, sp, target, d=False):  
        sp = target.get_robbed(c, sp, self, d)
        
        self.score += sp
        
        if sp:
            
            self.log.append({'type': 'sp', 'card': c.copy(), 'target': target, 'sp': sp, 'd': d})
            
        return sp
            
    def get_robbed(self, c, rp, robber, d=False):
        rp = rp if self.score >= rp else self.score
        
        if self.invincible:
            
            rp = 0

        self.score -= rp
        
        if rp:
            
            self.log.append({'type': 'rp', 'card': c.copy(), 'robber': robber, 'rp': rp, 'd': d})
        
        return rp
        
    def gain(self, c, gp, d=False):
        self.score += gp
        
        if gp:
        
            self.log.append({'type': 'gp', 'card': c.copy(), 'gp': gp, 'd': d})
            
        return gp
        
    def lose(self, c, lp, d=False):
        lp = lp if self.score >= lp else self.score
        
        self.score -= lp
        
        if lp:

            self.log.append({'type': 'lp', 'card': c.copy(), 'lp': lp, 'd': d})
            
        return lp
        
    def give(self, c, gp, target, d=False):
        gp = gp if self.score >= gp else self.score
        
        self.score -= gp
        
        target.score += gp
        
        if gp:

            self.log.append({'type': 'give', 'card': c.copy(), 'target': target, 'gp': -gp, 'd': d})
            
        return gp
        
        
        
        
        
        