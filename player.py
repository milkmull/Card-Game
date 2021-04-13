import random

def pack_log(log):
    if log['type'] == 'gp':
        
        return ('gp', log['gp'], log['card'].uid)
        
    elif log['type'] == 'lp':
        
        return ('lp', log['lp'], log['card'].uid)
        
    elif log['type'] == 'sp':   
        
        return ('sp', log['sp'], log['target'].pid, log['card'].uid)
        
    elif log['type'] == 'rp':
        
        return ('rp', log['rp'], log['robber'].pid, log['card'].uid)

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
        self.game_over = False
        self.ogp = False
        
        self.auto = auto
        
        self.invincible = False

        self.active_card = None

        self.max = 60 #if not self.auto else 2
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
        self.dump_log = []
        
        self.score = self.game.get_setting('ss')
        
    def __eq__(self, other):
        return self.pid == other.pid
       
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

    def get_info(self):
        if not self.game.wait:
        
            self.update()
            
        info = {
                
                'coin': self.coin, 
            
                'dice': self.dice,
                
                'flipping': self.flipping,
                
                'rolling': self.rolling,
                
                'score': self.score,
                    
                'selection': [(c.name, c.get_id()) for c in self.selection],
                
                'unplayed': [(c.name, c.uid) for c in self.unplayed],
                
                'played': [(c.name, c.uid) for c in self.played],
                
                'equipped': [(c.name, c.uid) for c in self.equipped],
                
                'items': [(c.name, c.uid) for c in self.items],
                
                'spells': [(c.name, c.uid) for c in self.spells],
                
                'ongoing': [(c.name, c.uid) for c in self.get_spells()],
                
                'treasure': [(c.name, c.uid) for c in self.treasure],
                
                'used_items': [(c.name, c.uid) for c in self.used_items]
                
                }      
                
        if self.active_card is not None:
            
            info['active_card'] = (self.active_card.name, self.active_card.uid)
            
        if self.landscape is not None:
            
            info['landscape'] = (self.landscape.name, self.landscape.uid)
            
        points = []
        
        for log in self.dump_log:
            
            pack = pack_log(log)
            
            if pack:
                
                points.append(pack)
                
        if points:
            
            info['points'] = points
            
        self.dump_log.clear()

        return info

    def get_light_info(self):
        info = {
            
                'flipping': self.flipping,
                
                'rolling': self.rolling,
                
                'is_turn': self.is_turn,
                
                'coin': self.coin,
                
                'dice': self.dice,

                'score': self.score,

                'played': [(c.name, c.uid) for c in self.played],
                
                'ongoing': [(c.name, c.uid) for c in self.get_spells()],
                
                'used_items': [(c.name, c.uid) for c in self.used_items]

                }
                
        if self.active_card is not None:
            
            info['active_card'] = (self.active_card.name, self.active_card.uid)
                
        if self.landscape is not None:
            
            info['landscape'] = (self.landscape.name, self.landscape.uid)
            
        return info

        

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
        self.dump_log.clear()
        
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
        self.dump_log.clear()
        
        self.draw_items(max(self.game.get_setting('items') - len(self.items), 0))
        self.draw_spells(max(self.game.get_setting('spells') - len(self.spells), 0))
        
        self.is_turn = False
        
        self.finished = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
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
        self.ogp = False
        
        self.invincible = False

        self.active_card = None

        self.max = 60 
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
        
        self.master_log = []
        self.log = []
        self.dump_log = []
        
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
        
    def end_turn(self):
        self.cancel_select()
            
        if not self.requests:
        
            self.play = False
            self.is_turn = False
            self.gone = False
            self.finished = True
            self.ogp = False
            
            if not (self.unplayed or self.game_over):
                
                self.end_game()
                
    def end_game(self):         
        if hasattr(self.game.event, 'end'):
            
            self.game.event.end(self)
            
        if self.game.round == self.game.get_setting('rounds'):

            for c in self.treasure.copy():

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
        if c.type in ('animal', 'plant', 'huamn', 'monster'):
            
            return 0
            
        elif c.type == 'item':
            
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
            
            if c.wait != 'cast':
                
                self.cancel_select()
            
                c.start_request(self)

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
         
    def cancel(self):
        if self.requests:
                
            c = self.requests[0]
            
            if c.wait == 'cast' or (c.wait == 'select' and c in self.items):
                
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
        if cmd == 'select' and card:
            
            self.select(card)
 
        elif cmd == 'cancel':
            
            self.cancel()

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
        self.dump_log += self.log
        
        self.log.clear()

        self.game.check_advance()
        
#auto stuff-----------------------------------------------------------------------------------------

    def set_cmd(self):
        if self.selection or (not self.requests and random.randrange(5) == 1 and self.is_turn and self.items + self.spells):
            
            return 'select'
            
        elif self.is_turn and not self.gone:
        
            return 'play'
            
    def auto_select(self):
        if self.selection:
        
            return random.choice(self.selection)
            
        else:
            
            return random.choice(self.items + self.spells)
        
    def auto_update(self):
        cmd = self.set_cmd()
        
        if cmd == 'select':
            
            card = self.auto_select()
            
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
        self.dump_log += self.log
        
        self.log.clear()

        self.game.check_advance()

#request stuff ------------------------------------------------------------------------------------------
        
    def cast(self, c):
        self.new_selection(c, [p for p in self.game.players if p.can_cast(c.name)])
        c.wait = 'cast'
        
    def new_flip(self, c, r=False):
        self.coin = None
        self.flipping = True
        
        self.tf = 60
        
        c.wait = 'coin'
        
        if c is not self.active_card:
        
            self.requests.append(c)
            
            self.active_card = None
            
        self.cancel_select()
        
    def coin_flip(self):
        if self.tf <= 30:
            
            self.log.append({'type': 'cf', 'coin': self.coin, 'd': False})
            
        else:
            
            self.coin = random.choice((1, 0))
        
    def new_roll(self, c):
        self.dice = None
        self.rolling = True
        
        self.tr = 60

        c.wait = 'dice'
        
        if c is not self.active_card:
            
            self.requests.append(c)
            
            self.active_card = None
            
        self.cancel_select()
            
    def dice_roll(self):
        if self.tr <= 30:
        
            self.log.append({'type': 'rd', 'dice': self.dice, 'd': False})
            
        else:
            
            self.dice = random.randrange(0, 6) + 1

    def new_selection(self, c, cards, r=False): #empty list could cause problems with active card waiting for selection
        self.selection.clear()
        
        if cards:

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
        return [log for log in self.log if log.get('type') == type and log.get('d') == False]
                
    def check_log(self, c, type):
        return any(log.get('type') == type and log.get('d') == False for log in self.log)
        
    def get_m_logs(self, type):
        return [log for log in self.master_log if log.get('type') == type and log.get('d') == False]
        
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
        
            self.items += self.game.draw_cards('items')
                
            self.log.append({'type': 'di', 'card': self.items[-1].copy(), 'd': d})
  
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
        
    def draw_spells(self, num=1):
        self.spells += self.game.draw_cards('spells', num)
        
    def has_spell(self, name):
        return any(c.name == name for c in self.get_spells())

    def remove_spell(self, c):
        self.ongoing.pop(self.ongoing.index(c))

    def can_cast(self, s):
        return not any(s == c.name and not c.mult for c in self.get_spells())
        
#treasure stuff-----------------------------------------------------------------------------------------

    def draw_treasure(self, num=1, d=False):
        t = self.game.draw_cards('treasure', num)
        
        for c in t:
            
            if hasattr(c, 'draw'):
                
                c.draw(self)
                
            self.treasure.append(c)
            
            self.log.append({'type': 'dt', 'card': c.copy(), 'd': d})
            
    def steal_treasure(self, target):
        self.treasure.append(target.treasure.pop(random.randrange(len(target.treasure))))
        
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
        
        
        
        
        
        