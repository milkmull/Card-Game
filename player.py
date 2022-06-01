import random
import time
from constants import *

def any(elements):
    for e in elements:
        if e:
            return True
    return False

class Player:
    tags = ['player']
    
    @staticmethod
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
            
    @staticmethod
    def sort_cards_og(c): 
        if c.name in ('the void', 'negative zone'):
            return 4
        elif any({tag in ('item', 'equipment') for tag in c.tags}):   
            return 1   
        elif 'spell' in c.tags:    
            return 2   
        elif 'landscape' in c.tags:   
            return 3
        else:
            return 0
            
    @staticmethod
    def sort_cards_requests(c): 
        if any({tag in ('item', 'equipment') for tag in c.tags}):   
            return 1   
        elif 'spell' in c.tags:    
            return 2   
        elif 'event' in c.tags:
            return 3
        else:   
            return 0
            
    def __init__(self, game, pid, player_info):
        self.game = game
        self.pid = pid

        self.player_info = player_info
        self.set_name()
        self.name = self.player_info['name']

        self.score = 0
        self.vote = None

        self.selecting = True
        self.gone = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.invincible = False

        self.max = 60
        self.ft = 0
        self.rt = 0
        self.coin = None
        self.dice = None

        self.played = []
        self.unplayed = []
        
        self.items = []
        self.equipped = []
        
        self.spells = []
        self.active_spells = []
        
        self.treasure = []
        self.landscapes = []
        
        self.selection = []
        self.selected = []

        self.ongoing = []
        self.active_og = []
        
        self.requests = []
        self.active_card = None
        
        self.master_log = []
        self.log = []
        
    def __eq__(self, other):
        if hasattr(other, 'get_id'):
            return self.pid == other.get_id()
        else:
            return False
            
    def __hash__(self):
        return self.pid
       
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name

    def get_id(self):
        return self.pid

    def is_auto(self):
        return isinstance(self, Auto_Player)
        
    def get_name(self):
        return self.name
        
    def get_info(self):
        return self.player_info

    def set_name(self):
        name = self.player_info['name']
        names = self.game.get_active_names()
        
        while True:
            c = len(name) + 2
            
            if any({name == n for n in names}):
                name = name.center(c)
                c += 2
            else:
                break

        self.player_info['name'] = name
        
    def copy(self, g):
        return Player_Copy(g, self)

#starting stuff--------------------------------------------------------------------------------------------                

    def reset(self, score=True):
        self.master_log.clear()
        self.log.clear()
        
        self.selecting = False
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
        self.active_og.clear()
        
        self.requests.clear()
        self.played.clear()
        self.unplayed.clear()
        self.selection.clear()
        self.selected.clear()
        self.equipped.clear()
        self.items.clear()
        self.spells.clear()
        self.active_spells.clear()
        self.ongoing.clear()
        self.treasure.clear()
        self.landscapes.clear()
        
        if score:
            self.update_score(0)

    def start(self):
        self.update_score(self.game.get_setting('ss'))
        self.draw_cards('landscapes')
        self.draw_cards('unplayed', self.game.get_setting('cards'))
        self.draw_cards('items', self.game.get_setting('items'))
        self.draw_cards('spells', self.game.get_setting('spells'))
        self.new_deck('treasure', [self.game.get_card('gold coins')])
        
        self.max = 60 * len([p for p in self.game.players if not p.is_auto()]) * 2

    def new_round(self):
        self.unequip_all()
        items = self.items.copy()
        spells = self.spells.copy()
        treasure = self.treasure.copy()
        if not any({c.name == 'gold coins' for c in treasure}):
            treasure.append(self.game.get_card('gold coins'))
        
        self.reset(score=False)
        
        self.new_deck('items', items)
        self.new_deck('spells', spells)
        self.new_deck('treasure', treasure)

        self.draw_cards('landscapes')
        self.draw_cards('unplayed', self.game.get_setting('cards'))
        self.draw_cards('items', max(self.game.get_setting('items') - len(self.items), 0))
        self.draw_cards('spells', max(self.game.get_setting('spells') - len(self.spells), 0))
        
        self.update_score(self.score)
 
#card stuff-------------------------------------------------------------------------------------- 

    def find_card_deck(self, c):
        if c in self.played:
            return 'played'
        elif c in self.unplayed:
            return 'unplayed'
        elif c in self.items:
            return 'items'
        elif c in self.equipped:
            return 'equipped'
        elif c in self.spells:
            return 'spells'
        elif c in self.active_spells:
            return 'active_spells'
        elif c in self.treasure:
            return 'treasure'
        elif c in self.landscapes:
            return 'landscapes'
            
    def has_card(self, name, deck=None):
        if deck:
            return any({c.name == name for c in getattr(self, deck)})
            
        if any({c.name == name for c in self.played}):
            return 'played'
        elif any({c.name == name for c in self.unplayed}):
            return 'unplayed'
        elif any({c.name == name for c in self.items}):
            return 'items'
        elif any({c.name == name for c in self.equipped}):
            return 'equipped'
        elif any({c.name == name for c in self.spells}):
            return 'spells'
        elif any({c.name == name for c in self.active_spells}):
            return 'active_spells'
        elif any({c.name == name for c in self.treasure}):
            return 'treasure'
        elif any({c.name == name for c in self.landscapes}):
            return 'landscapes'

    def draw_cards(self, pdeck, num=1):
        if pdeck == 'unplayed':
            gdeck = 'play'  
        elif pdeck in ('items', 'spells', 'treasure', 'landscapes'):
            gdeck = pdeck
        else:
            return []
            
        cards = self.game.draw_cards(gdeck, num)
        self.new_deck(pdeck, getattr(self, pdeck) + cards)
        
        if pdeck == 'landscapes': 
            for c in cards:
                c.start_ongoing(self)
            
        self.add_log({'t': 'draw', 'deck': pdeck, 'c': cards.copy()})
                
        return cards
   
    def add_card(self, c, deck, i=None):
        nd = getattr(self, deck).copy()
        if i is None:
            i = len(nd)
        nd.insert(i, c)
        self.new_deck(deck, nd)
        
        if deck == 'played' and hasattr(c, 'start_ongoing') and c not in self.ongoing:
            c.start_ongoing(self)
            
    def safe_add(self, c):
        deck = Plyer.get_deck(c)
        self.add_card(c, deck)
        
    def remove_card(self, c, deck):
        self.new_deck(deck, [o for o in getattr(self, deck) if o != c])

    def replace_card(self, c1, c2):
        deck = self.find_card_deck(c1)
        if not deck:
            return
        nd = getattr(self, deck).copy()
        i = nd.index(c1)
        self.safe_discard(c1)
        self.add_card(c2, deck, i=i)
        
    def get_played_card(self, i):
        c = None
        try:
            c = self.played[i]
        except IndexError:
            pass
        finally:
            return c
   
    def play_card(self, c, et=True):    
        d = False
        self.cancel_request()
        if c in self.unplayed:
            self.remove_card(c, 'unplayed')
        c.start(self)
        if c not in self.played:
            self.add_card(c, 'played')
        else:
            et = False
            d = True
        if et:
            self.gone = True
        self.add_log({'t': 'play', 'c': c, 'd': d})
                
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
        
    def use_item(self, c):
        self.discard_card(c)
        self.add_log({'t': 'ui', 'c': c})
        
    def safe_discard(self, c):
        self.discard_card(c, d=True)

    def discard_card(self, c, d=False):            
        self.end_og(c)
        
        if c in self.equipped:
            self.unequip(c)
            
        if c in self.items:
            self.remove_card(c, 'items')

        if c in self.unplayed:
            self.remove_card(c, 'unplayed')
            
        if c in self.played: 
            self.remove_card(c, 'played')
            
        if c in self.treasure:
            self.remove_card(c, 'treasure')
            
        if c in self.landscapes:
            self.remove_card(c, 'landscapes')
            
        if c in self.spells:
            self.remove_card(c, 'spells')
            
        if c in self.active_spells:
            self.remove_card(c, 'active_spells')
            
        if not d:
            self.add_log({'t': 'disc', 'c': c, 'tags': c.tags}) #maybe change in the future
            self.game.discard.append(c)

    def get_items(self):
        return [c for c in self.items + self.equipped if c.wait is None]
        
    def give_card(self, c, target):
        self.safe_discard(c) 
        deck = Player.get_deck(c)
        target.new_deck(deck, getattr(target, deck) + [c])

    def steal_card(self, c, target):
        deck = Player.get_deck(c)
        self.safe_discard(c)
        target.add_card(c, deck)
        
    def steal_random_card(self, pdeck, target):
        deck = getattr(target, pdeck)
        
        if deck:  
            c = random.choice(deck)
            target.safe_discard(c)
            self.add_card(c, pdeck)
            
        else:
            if pdeck == 'treasure':
                self.draw_cards('treasure')

#equipment stuff------------------------------------------------------------------------------------

    def equip(self, c):
        self.remove_card(c, 'items')
        self.add_card(c, 'equipped')
        
    def unequip(self, c): 
        self.remove_card(c, 'equipped')
        self.add_card(c, 'items')
        self.end_og(c)
    
    def unequip_all(self):
        for c in self.equipped.copy():
            self.unequip(c)
    
#vote stuff------------------------------------------------------------------------------------

    def set_vote(self, vote):
        self.vote = vote
        self.add_log({'t': 'v', 'v': vote})

#spell stuff----------------------------------------------------------------------------------------

    def add_active_spell(self, c):
        self.add_card(c, 'active_spells')
        if hasattr(c, 'start_ongoing'):
            c.start_ongoing(self)

    def cast(self, target, c):
        if not c.can_cast(target):
            return

        self.safe_discard(c)
        
        if c is not self.active_card:
            self.end_request(c)
        
        target.add_active_spell(c)
        self.add_log({'t': 'cast', 'c': c, 'target': target, 'd': False})
            
#buying stuff---------------------------------------------------------------------------------------

    def can_buy(self):
        return any({c.name == 'gold coins' for c in self.treasure}) and not self.game_over

    def buy_card(self, uid, free=False):
        c = self.game.buy(self, uid)
        
        if c and (self.can_buy() or free):

            if any({tag in ('item', 'equipment') for tag in c.tags}):
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
        c = c.storage_copy()
        c.wait = wait
        self.requests.append(c)
        return c
        
    def start_request(self, c):
        if c.wait == 'flip': 
            self.coin = -1
            self.ft = self.max
            
        elif c.wait == 'roll':
            self.dice = -1
            self.rt = self.max
            
        else:
            
            cards = None

            if c.wait == 'select':
                cards = c.get_selection(self)
                
            elif c.wait == 'cast': 
                cards = [p for p in self.game.players if c.can_cast(p)]

            if cards:
                if cards != self.selection:
                    self.new_deck('selection', cards)
                    self.selecting = True     
                    
            else:
                c.wait = None
                if self.active_card:
                    self.requests.pop(0)
                    self.cancel_request()

    def process_request(self):
        self.requests.sort(key=Player.sort_cards_requests)
        c = self.requests[0]
        if c is not self.active_card:
            self.cancel_request()
            self.start_request(c)
            self.active_card = c
            self.add_log({'t': 'aac', 'c': self.active_card, 'w': self.active_card.wait, 'cancel': self.can_cancel()})

        confirm = False

        if c.wait == 'flip' and not self.ft:
            if self.coin is not None:  
                c.wait = None
                c.coin(self, self.coin)
                confirm = True
                
        elif c.wait == 'roll' and not self.rt:
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
            self.soft_cancel_request()
            self.start_request(c)
            
    def soft_cancel_request(self):
        self.flipping = False
        self.coin = None
        self.rolling = False
        self.dice = None
                    
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
            
    def end_request(self, c):
        while c in self.requests:
            self.requests.remove(c)

    def select(self, uid):
        if self.selection:
            for c in self.selection:  
                if c.get_id() == uid:
                    self.selected.append(c)
                    return

        if not (self.gone or self.requests):
            for c in self.unplayed:
                if c.get_id() == uid:   
                    self.play_card(c)
                    return
                    
        for c in self.requests:
            if c.get_id() == uid:
                return
        
        if not self.game_over:

            for c in self.items: 
                if c.get_id() == uid:
                    if c.can_use(self):
                        c.start(self)
                    return
                    
            for c in self.spells:    
                if c.get_id() == uid:
                    c.wait = 'cast'
                    self.requests.append(c)
                    return
                    
            for c in self.treasure:
                if c.get_id() == uid:  
                    if hasattr(c, 'start'):
                        c.start(self)     
                    return
                    
            for c in self.equipped:                   
                if c.get_id() == uid:  
                    self.unequip(c)
                    return

    def flip(self):
        if self.ft == self.max / 2:
            self.coin = random.choice((1, 0))
            self.add_log({'t': 'cfe', 'coin': self.coin, 'ft': self.ft - 2, 'd': False})
            
        self.ft = max(self.ft - 1, 0)

    def roll(self): 
        if self.rt == self.max / 2:
            self.dice = random.randrange(0, 6) + 1
            self.add_log({'t': 'dre', 'dice': self.dice, 'rt': self.rt - 2, 'd': False})  
            
        self.rt = max(self.rt - 1, 0)

#ongoing stuff--------------------------------------------------------------------------------------
   
    def add_og(self, c, types):
        if types:
            c = c.storage_copy()
            c.set_log_types(types)
            self.ongoing.append(c)
            if c in self.items:
                self.equip(c)
        
    def end_og(self, c):
        while c in self.ongoing:
            self.ongoing.remove(c)
   
    def og(self, log={'t': 'cont'}):
        self.ongoing.sort(key=Player.sort_cards_og)

        t = log['t']
        
        for c in self.ongoing.copy():
        
            if c not in self.ongoing:
                continue

            if log.get('c') != c and not any({o is c for o in self.active_og}):
                self.active_og.append(c)
                if t in c.log_types:
                    c.ongoing(self, log)
                self.active_og.pop(-1)
       
#log stuff------------------------------------------------------------------------------------------

    def add_log(self, log, kwargs={}):
        kwargs['u'] = self.pid
        kwargs['frame'] = self.game.frame
        log.update(kwargs)
        self.log.append(log)
        if not log.get('d'):
            self.og(log=log)

    def update_logs(self):
        self.master_log += self.log
        self.game.update_player_logs(self)
        self.log.clear()

#update stuff---------------------------------------------------------------------------------------

    def update(self, cmd=''):
        if 'select' in cmd and (self.dice is self.coin is None):
            uid = int(cmd.split()[1])
            self.select(uid)
 
        elif cmd == 'cancel':
            self.cancel()

        elif cmd == 'play' and not self.gone:
            if self.unplayed:
                card = self.unplayed[0]
                self.play_card(card)
            
        elif cmd == 'flip' and self.coin == -1:  
            self.add_log({'t': 'cfs'})
            self.flipping = True   

        elif cmd == 'roll' and self.dice == -1:
            self.add_log({'t': 'drs'})
            self.rolling = True
            
        if self.flipping:
            self.flip()
        elif self.rolling:
            self.roll()

        if self.requests:
            self.process_request()
        self.og()
        
        self.update_logs()
        
        self.game.advance_turn()

#turn stuff-----------------------------------------------------------------------------------------

    def start_turn(self):
        self.gone = False
        
    def done_with_turn(self):
        return (self.gone or not (self.gone or self.unplayed)) and not self.requests
  
    def done_with_round(self):
        return not self.unplayed + self.requests
        
    def end_round(self, use_treasure):
        if hasattr(self.game.event, 'end'):
            self.game.event.end(self)
            
        if use_treasure:
            for c in self.treasure:
                if hasattr(c, 'end'):
                    c.end(self)

        self.game_over = True
        
    def finished_game(self):
        return self.game_over and not self.requests
        
#sim stuff------------------------------------------------------------------------------------------

    def sim_copy(self, game):
        return game.get_player(self.pid)

#point stuff-----------------------------------------------------------------------------------------
 
    def update_score(self, score):
        self.score = score
        self.add_log({'t': 'score', 'score': self.score})
 
    def steal(self, c, sp, target, d=False):  
        sp = target.get_robbed(c, sp, self, d)
        if sp: 
            self.update_score(self.score + sp)
            self.add_log({'t': 'sp', 'c': c, 'target': target, 'sp': sp, 'd': d})
        return sp
            
    def get_robbed(self, c, rp, robber, d=False):
        rp = rp if self.score >= rp else self.score
        if self.invincible:
            self.add_log({'t': 'iv', 'c': c})
            rp = 0
        if rp:
            self.update_score(self.score - rp)
            self.add_log({'t': 'rp', 'c': c, 'robber': robber, 'rp': rp, 'd': d})
        return rp
        
    def gain(self, c, gp, d=False):
        if gp:
            self.update_score(self.score + gp)
            self.add_log({'t': 'gp', 'c': c, 'gp': gp, 'd': d})
        return gp
        
    def lose(self, c, lp, d=False):
        lp = lp if self.score >= lp else self.score
        if lp:
            self.update_score(self.score - lp)
            self.add_log({'t': 'lp', 'c': c, 'lp': lp, 'd': d})
        return lp
        
    def give(self, c, gp, target, d=False):
        gp = gp if self.score >= gp else self.score
        if gp:
            self.update_score(self.score - gp)
            target.update_score(target.score + gp)
            self.add_log({'t': 'give', 'c': c, 'target': target, 'gp': -gp, 'd': d})
        return gp
        
class Auto_Player(Player):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid, player_info)

        self.decision = {}
        self.tree = []
        self.diff = 0
        self.temp_tree = set()
        self.stable_counter = 0
        self.max_stable = 0
        self.sim_timer = 0
        self.timer = 0
        
    def reset(self, score=True):
        super().reset(score=score)
        self.reset_brain()
        
    def start(self):
        super().start()
        self.set_difficulty(self.game.get_setting('diff'))

    def set_timer(self):
        self.timer = random.randrange(60, 120)
        
    def start_turn(self):
        super().start_turn()
        self.set_timer()
        
    def new_choice(self, g):
        p = g.get_player(self.pid)
        choice = p.get_choice()
        
        if choice:
            score = round(sum([p.score - o.score for o in g.players]) / (len(g.players) - 1))
            for i, (d, info) in enumerate(self.tree.copy()):
                if d == choice:
                    count, ave = info
                    info[0] += 1
                    new_ave = ave + ((score - ave) / (count + 1))
                    info[1] = round(new_ave, 2)
                    break
            else:
                self.tree.append((choice, [1, score]))
       
        if self.diff < 4:
            temp_tree = {info[0] for info in self.tree}
        else:
            self.tree.sort(key=lambda info: info[1][1], reverse=True)
            temp_tree = [info[0] for info in self.tree]
        if temp_tree == self.temp_tree:
            self.stable_counter += 1
        else:
            self.stable_counter = 0
            self.temp_tree = temp_tree

    def simulate(self):
        g = self.game.copy()
        t = time.time()
        while not (g.done() or time.time() - t > self.sim_timer):
            g.main()
        self.new_choice(g)
        
    def get_decision(self):
        self.tree.sort(key=lambda info: info[1][1], reverse=True)
        print(self.tree)
        cards = self.get_selection()

        for info in self.tree:
            d = info[0]
            if d == 'w' and not self.selection:
                return 
            elif d in cards:
                return d

    def reset_brain(self):
        self.stable_counter = 0 
        self.decision = None
        self.tree.clear()
        self.set_timer()
      
    def is_stable(self):
        return self.stable_counter > self.max_stable# // 4 or self.timer < -200

    def timer_up(self):
        return self.timer <= 0

    def set_difficulty(self, diff):
        p = len(self.game.players)
        self.diff = diff
        
        if diff == 0:
            self.max_stable = 0
        elif diff == 1:
            self.max_stable = 5 // len(self.game.players)
        elif diff == 2:
            self.max_stable = 10 // len(self.game.players)
        elif diff == 3:
            self.max_stable = 50 // len(self.game.players)
        elif diff == 4:
            self.max_stable = 100 // len(self.game.players)
            
        #if diff:
        self.sim_timer = self.get_sim_time()
        #else:
        #    self.sim_timer = 0
        
    def get_sim_time(self):
        players = len([p for p in self.game.players if p.is_auto()])
        if players <= 5:
            total_update_time = 0.006
            return round(max({((1 / fps) - total_update_time) / players, 0}), 5)
        else:
            return 0 

    def start_request(self, c):
        sel = self.selection.copy()
        super().start_request(c)
        if not self.selecting or (self.selecting and self.selection != sel):
            self.set_timer()
        
    def get_selection(self):
        if self.selection:
            return self.selection.copy()
            
        cards = [c for c in self.items if c.can_use(self)] + self.spells
        for c in self.treasure:
            if c.name == 'gold coins':
                cards.append(c)
                break
        if not self.gone:      
            cards += self.unplayed  
            
        return cards
     
    def random_choice(self):
        if self.selection:
            return random.choice(self.selection)

        cards = self.get_selection()
        
        if cards:
            if self.gone and random.choice(range(len(cards) + 1)) == 0:
                return
            else:
                return random.choice(cards)

    def auto_select(self):
        s = None
        
        if self.game.done():
            return
            
        if self.sim_timer:
   
            if not self.is_stable():
                self.simulate()
                self.decision = None
                
            elif self.timer_up() and not (self.flipping or self.rolling):
                s = self.get_decision()
                if s:
                    if not random.choice((0, 1)):
                        s = None
                        self.stable_counter = 0
                else:
                    self.reset_brain()
                
        elif self.timer_up() and not (self.flipping or self.rolling):
            s = self.random_choice()

        if s is not None:
            if s == 'w':
                s = None
            else:
                self.add_log({'t': 'select', 's': s})
            self.reset_brain()
        return s

    def update(self):
        s = self.auto_select()
        if s:
            self.select(s.get_id())
            
        if self.timer < 30:
            if self.coin == -1:
                self.flipping = True
                self.add_log({'t': 'cfs'})
            elif self.dice == -1:
                self.rolling = True
                self.add_log({'t': 'drs'})   
                
        if self.flipping:
            self.flip()
        elif self.rolling:
            self.roll()

        if self.requests:
            self.process_request()   
        self.og()
        
        self.timer -= 1
        
        self.update_logs()

        self.game.advance_turn()  
        
class Player_Copy:
    @staticmethod
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
            
    @staticmethod
    def sort_cards_og(c): 
        if c.name in ('the void', 'negative zone'):
            return 4
        elif any({tag in ('item', 'equipment') for tag in c.tags}):   
            return 1   
        elif 'spell' in c.tags:    
            return 2   
        elif 'landscape' in c.tags:   
            return 3
        else:
            return 0

    @staticmethod
    def sort_cards_requests(c): 
        if any({tag in ('item', 'equipment') for tag in c.tags}):   
            return 1   
        elif 'spell' in c.tags:    
            return 2   
        elif 'event' in c.tags:
            return 3
        else:   
            return 0
            
    def __init__(self, game, p):
        self.game = game
        self.pid = p.pid
        
        self.tags = p.tags

        self.name = p.name
        
        self.selecting = p.selecting
        self.gone = p.gone
        self.flipping = p.flipping
        self.rolling = p.rolling      
        self.invincible = p.invincible
        self.game_over = p.game_over
        
        self.auto = True
        self.first_choice = None

        self.coin = p.coin
        self.dice = p.dice
        
        self.score = p.score
        self.vote = p.vote
        
        self.played = []
        self.unplayed = []
        self.items = []
        self.selection = []
        self.selected = []
        self.equipped = []
        self.ongoing = []
        self.treasure = []
        self.spells = []
        self.active_spells = []
        self.landscapes = []
        self.requests = []

        self.active_card = None
        self.active_og = []
        
        self.master_log = p.master_log.copy()
        self.log = p.log.copy()
        
    def set_cards(self, game, p):
        self.played = [c.sim_copy(game) for c in p.played]
        self.unplayed = [c.light_sim_copy(game) for c in p.unplayed]
        self.items = [c.light_sim_copy(game) for c in p.items]
        self.selection = [c.sim_copy(game) for c in p.selection]
        self.selected = [c.sim_copy(game) for c in p.selected]
        self.equipped = [c.sim_copy(game) for c in p.equipped]
        self.ongoing = [c.sim_copy(game) for c in p.ongoing]
        self.treasure = [c.light_sim_copy(game) for c in p.treasure]
        self.spells = [c.light_sim_copy(game) for c in p.spells]
        self.active_spells = [c.sim_copy(game) for c in p.active_spells]
        self.landscapes = [c.sim_copy(game) for c in p.landscapes]
        self.requests = [c.sim_copy(game) for c in p.requests]

        self.active_card = next((c for c in self.requests if c == p.active_card), None)  
        self.active_og = [c.sim_copy(game) for c in p.active_og]
        
    def __eq__(self, other):
        if hasattr(other, 'get_id'):
            return self.pid == other.get_id()
        else:
            return False
            
    def __hash__(self):
        return self.pid
       
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name

    def get_id(self):
        return self.pid
        
    def get_name(self):
        return self.name
        
    def get_choice(self):
        return self.first_choice
        
    def is_auto(self):
        return True

#card stuff-------------------------------------------------------------------------------------- 

    def find_card_deck(self, c):
        if c in self.played:
            return 'played'
        elif c in self.unplayed:
            return 'unplayed'
        elif c in self.items:
            return 'items'
        elif c in self.equipped:
            return 'equipped'
        elif c in self.spells:
            return 'spells'
        elif c in self.active_spells:
            return 'active_spells'
        elif c in self.treasure:
            return 'treasure'
        elif c in self.landscapes:
            return 'landscapes'
            
    def has_card(self, name, deck=None):
        if deck:
            return any({c.name == name for c in getattr(self, deck)})
            
        if any({c.name == name for c in self.played}):
            return 'played'
        elif any({c.name == name for c in self.unplayed}):
            return 'unplayed'
        elif any({c.name == name for c in self.items}):
            return 'items'
        elif any({c.name == name for c in self.equipped}):
            return 'equipped'
        elif any({c.name == name for c in self.spells}):
            return 'spells'
        elif any({c.name == name for c in self.active_spells}):
            return 'active_spells'
        elif any({c.name == name for c in self.treasure}):
            return 'treasure'
        elif any({c.name == name for c in self.landscapes}):
            return 'landscapes'

    def draw_cards(self, pdeck, num=1):
        if pdeck == 'unplayed':
            gdeck = 'play'  
        elif pdeck in ('items', 'spells', 'treasure', 'landscapes'):
            gdeck = pdeck
        else:
            return []
            
        cards = self.game.draw_cards(gdeck, num)
        self.new_deck(pdeck, getattr(self, pdeck) + cards)
        
        if pdeck == 'landscapes': 
            for c in cards:
                c.start_ongoing(self)
                
        if len(cards) == 1:     
            self.add_log({'t': f'd{pdeck[0]}', 'c': cards[0]})
     
        return cards
   
    def add_card(self, c, deck, i=None):
        nd = getattr(self, deck).copy()
        if i is None:
            i = len(nd)
        nd.insert(i, c)
        self.new_deck(deck, nd)
        
        if deck == 'played' and hasattr(c, 'start_ongoing') and c not in self.ongoing:
            c.start_ongoing(self)
            
    def safe_add(self, c):
        deck = Player.get_deck(c)
        self.add_card(c, deck)
        
    def remove_card(self, c, deck):
        self.new_deck(deck, [o for o in getattr(self, deck) if o != c])

    def replace_card(self, c1, c2):
        deck = self.find_card_deck(c1)
        if not deck:
            return
        nd = getattr(self, deck).copy()
        i = nd.index(c1)
        self.safe_discard(c1)
        self.add_card(c2, deck, i=i)
        
    def get_played_card(self, i):
        c = None
        try:
            c = self.played[i]
        except IndexError:
            pass
        finally:
            return c
   
    def play_card(self, c, et=True):    
        d = False
        self.cancel_request()
        if c in self.unplayed:
            self.remove_card(c, 'unplayed')
        c.start(self)
        if c not in self.played:
            self.add_card(c, 'played')
        else:
            et = False
            d = True
        if et:
            self.gone = True
        self.add_log({'t': 'play', 'c': c, 'd': d})
                
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
        
    def use_item(self, c):
        self.discard_card(c)
        self.add_log({'t': 'ui', 'c': c})
        
    def safe_discard(self, c):
        self.discard_card(c, d=True)

    def discard_card(self, c, d=False): 
        self.end_og(c)

        if c in self.equipped:
            self.unequip(c)
            
        if c in self.items:
            self.remove_card(c, 'items')

        if c in self.unplayed:
            self.remove_card(c, 'unplayed')
            
        if c in self.played: 
            self.remove_card(c, 'played')
            
        if c in self.treasure:
            self.remove_card(c, 'treasure')
            
        if c in self.landscapes:
            self.remove_card(c, 'landscapes')
            
        if c in self.spells:
            self.remove_card(c, 'spells')
            
        if c in self.active_spells:
            self.remove_card(c, 'active_spells')
            
        if not d:
            self.game.discard.append(c)

    def has_landscape(self, ls):
        return any({landscape.name == ls for landscape in self.landscapes})     

    def get_items(self):
        return [c for c in self.items + self.equipped if c.wait is None]
        
    def give_card(self, c, target):
        self.safe_discard(c)
        deck = Player.get_deck(c)
        target.new_deck(deck, getattr(target, deck) + [c])

    def steal_card(self, c, target):
        deck = Player.get_deck(c)
        self.safe_discard(c)
        target.add_card(c, deck)
        
    def steal_random_card(self, pdeck, target):
        c = None
        deck = getattr(target, pdeck)
        
        if deck:  
            c = random.choice(deck)
            target.safe_discard(c)
            self.add_card(c, pdeck)
            
        else:
            if pdeck == 'treasure':
                cards = self.draw_cards('treasure')
                c = cards[0]
                
        return c

#equipment stuff------------------------------------------------------------------------------------

    def equip(self, c):
        self.remove_card(c, 'items')
        self.add_card(c, 'equipped')
        
    def unequip(self, c): 
        self.remove_card(c, 'equipped')
        self.add_card(c, 'items')
        self.end_og(c)
            
#spell stuff----------------------------------------------------------------------------------------

    def add_active_spell(self, c):
        self.add_card(c, 'active_spells')
        if hasattr(c, 'start_ongoing'):
            c.start_ongoing(self)

    def cast(self, target, c):
        if not c.can_cast(target):
            return

        self.safe_discard(c)
        
        if c is not self.active_card:
            self.end_request(c)
        
        target.add_active_spell(c)
        self.add_log({'t': 'cast', 'c': c, 'target': target, 'd': False})
            
#buying stuff---------------------------------------------------------------------------------------

    def can_buy(self):
        return any({c.name == 'gold coins' for c in self.treasure}) and not self.game_over

    def buy_card(self, uid, free=False):
        c = self.game.buy(self, uid)
        
        if c and (self.can_buy() or free):

            if any({tag in ('item', 'equipment') for tag in c.tags}):
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
                
        return c
    
    def remove_coins(self):
        for c in self.treasure:
            if c.name == 'gold coins':        
                self.new_deck('treasure', [t for t in self.treasure if t != c])        
                return

#request stuff--------------------------------------------------------------------------------------
              
    def set_vote(self, vote):
        self.vote = vote
              
    def add_request(self, c, wait):
        c = c.storage_copy()
        c.wait = wait
        self.requests.append(c)
        return c
        
    def start_request(self, c):      
        if c.wait == 'flip': 
            self.coin = -1
        elif c.wait == 'roll':
            self.dice = -1
            
        else:
            
            cards = None
        
            if c.wait == 'select':
                cards = c.get_selection(self)
                
            elif c.wait == 'cast': 
                cards = [p for p in self.game.players if c.can_cast(p)]

            if cards:
                if cards != self.selection:
                    self.new_deck('selection', cards)
                    self.selecting = True     
                    
            else:
                c.wait = None
                if self.active_card:
                    self.requests.pop(0)
                    self.cancel_request()
  
    def process_request(self):
        self.requests.sort(key=Player.sort_cards_requests)
        c = self.requests[0]
        if c is not self.active_card:
            self.cancel_request()
            self.start_request(c)
            self.active_card = c
  
        confirm = False

        if c.wait == 'flip':
            if self.coin is not None:
                c.wait = None
                c.coin(self, self.coin)
                confirm = True
                
        elif c.wait == 'roll':
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
            self.soft_cancel_request()
            self.start_request(c)
     
    def soft_cancel_request(self):
        self.flipping = False
        self.coin = None
        self.rolling = False
        self.dice = None
                    
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
            
    def end_request(self, c):
        while c in self.requests:
            self.requests.remove(c)

    def select(self, c):
        if c in self.selection:
            self.selected.append(c)

        elif not (self.gone or self.requests):
            if c in self.unplayed:
                self.play_card(c)
   
        elif not self.game_over and c not in self.requests:
        
            if c in self.items and c.can_use(self):
                c.start(self)
                
            elif c in self.spells:
                c.wait = 'cast'
                self.requests.append(c)
                
            elif c in self.treasure:
                if hasattr(c, 'start'):
                    c.start(self)     
                    
            elif c in self.equipped:
                self.unequip(c)

    def flip(self):
        self.coin = random.choice((1, 0))
        self.add_log({'t': 'cfe', 'coin': self.coin, 'd': False})
        self.flipping = False

    def roll(self):
        self.dice = random.randrange(0, 6) + 1
        self.add_log({'t': 'dre', 'dice': self.dice, 'd': False}) 
        self.rolling = False

#ongoing stuff--------------------------------------------------------------------------------------
   
    def add_og(self, c, types):
        if types:
            c = c.storage_copy()
            c.set_log_types(types)
            self.ongoing.append(c)
            if c in self.items:
                self.equip(c)
        
    def end_og(self, c):
        while c in self.ongoing:
            self.ongoing.remove(c)
   
    def og(self, log={'t': 'cont'}):
        self.ongoing.sort(key=Player.sort_cards_og)

        t = log['t']
        
        for c in self.ongoing.copy():
        
            if c not in self.ongoing:
                continue

            if log.get('c') != c and not any({o is c for o in self.active_og}):
                self.active_og.append(c)
                if t in c.log_types:
                    c.ongoing(self, log)
                self.active_og.pop(-1)
  
#log stuff------------------------------------------------------------------------------------------

    def add_log(self, log):
        self.log.append(log)
        if not log.get('d'):
            self.og(log=log)
            
    def update_logs(self):
        self.master_log += self.log
        self.log.clear()

#turn stuff-----------------------------------------------------------------------------------------

    def start_turn(self):
        self.gone = False  
  
    def done_with_turn(self):
        return (self.gone or not (self.gone or self.unplayed)) and not self.requests
        
    def done_with_round(self):
        return not self.unplayed + self.requests
        
    def end_round(self, use_treasure):
        if hasattr(self.game.event, 'end'):
            self.game.event.end(self)

        for c in self.treasure:
            if hasattr(c, 'end'):
                c.end(self)

        self.game_over = True
        
    def finished_game(self):
        return self.game_over and not self.requests
        
#sim stuff------------------------------------------------------------------------------------------

    def sim_copy(self, game):
        return game.get_player(self.pid)
        
#auto stuff-----------------------------------------------------------------------------------------

    def get_selection(self):
        cards = [c for c in self.items if c.can_use(self)] + self.spells
        
        for c in self.treasure:
            if c.name == 'gold coins':
                cards.append(c)
                break
        if not self.gone:      
            cards += self.unplayed  
            
        return cards

    def auto_select(self):
        s = None
        
        if self.game.done():
            return
            
        if self.selection:
            s = random.choice(self.selection)
            
        elif not self.requests:
            cards = self.get_selection()
            
            if cards:
                if not self.first_choice and random.choice(range(len(cards) + 1)) == 0:
                    self.first_choice = 'w'
                else:
                    s = random.choice(cards) 
                    
        if s and not self.first_choice:
            self.first_choice = s
        
        return s

    def update(self):
        s = self.auto_select()
        if s:
            self.select(s)
                
        if self.coin is not None:
            self.flipping = True
            self.flip()
                
        if self.dice is not None:
            self.rolling = True
            self.roll()

        if self.requests:
            self.process_request()   
        self.og()
        
        self.update_logs()

        self.game.advance_turn()  

#point stuff-----------------------------------------------------------------------------------------
 
    def update_score(self, score):
        self.score = score
 
    def steal(self, c, sp, target, d=False):  
        sp = target.get_robbed(c, sp, self, d)
        if sp: 
            self.update_score(self.score + sp)
            self.add_log({'t': 'sp', 'c': c, 'target': target, 'sp': sp, 'd': d})
        return sp
            
    def get_robbed(self, c, rp, robber, d=False):
        rp = rp if self.score >= rp else self.score
        if self.invincible:
            self.add_log({'t': 'iv', 'c': c})
            rp = 0
        if rp:
            self.update_score(self.score - rp)
            self.add_log({'t': 'rp', 'c': c, 'robber': robber, 'rp': rp, 'd': d})
        return rp
        
    def gain(self, c, gp, d=False):
        if gp:
            self.update_score(self.score + gp)
            self.add_log({'t': 'gp', 'c': c, 'gp': gp, 'd': d})
        return gp
        
    def lose(self, c, lp, d=False):
        lp = lp if self.score >= lp else self.score
        if lp:
            self.update_score(self.score - lp)
            self.add_log({'t': 'lp', 'c': c, 'lp': lp, 'd': d})
        return lp
        
    def give(self, c, gp, target, d=False):
        gp = gp if self.score >= gp else self.score
        if gp:
            self.update_score(self.score - gp)
            target.update_score(target.score + gp)
            self.add_log({'t': 'give', 'c': c, 'target': target, 'gp': -gp, 'd': d})
        return gp
        
        