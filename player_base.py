import random
     
class Player_Base:
    type = 'player'
    tags = []
    
    type_to_deck_dict = {
        'treasure': 'treasure',
        'landscape': 'landscapes',
        'item': 'items',
        'spell': 'spells',
        'play': 'unplayed'
    }
    
    deck_strings = (
        'played',
        'unplayed',
        'items',
        'equipped',
        'spells',
        'active_spells',
        'treasure',
        'landscapes'
    )
    
    @classmethod
    def card_to_deck_string(cls, c):
        return cls.type_to_deck_dict[c.type]
        
    @classmethod
    def type_to_deck_string(cls, type):
        return cls.type_to_deck_dict[type]
            
    @staticmethod
    def sort_og_cards(c): 
        if c.name in ('the void', 'negative zone'):
            return 4
        elif c.type == 'item':   
            return 1   
        elif c.type == 'spell':    
            return 2   
        elif c.type == 'landscape':   
            return 3
        else:
            return 0
            
    @staticmethod
    def sort_request_cards(c): 
        if c.type == 'item':   
            return 1   
        elif c.type == 'spell':   
            return 2   
        elif c.type == 'event':
            return 3
        else:   
            return 0
            
    def __init__(self, game, pid):
        self.game = game
        self.pid = pid

        self.name = f'player {pid}'
        
        self.score = 0
        self.vote = None
        
        self.selecting = True
        self.gone = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.invincible = False

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
        
    def get_name(self):
        return self.name
        
    def get_choice(self):
        return self.first_choice
        
    def is_auto(self):
        return True
        
#starting stuff--------------------------------------------------------------------------------------------                

    def reset(self):
        self.master_log.clear()
        self.log.clear()
        
        self.selecting = False
        self.gone = False
        self.flipping = False
        self.rolling = False
        self.game_over = False
        self.invincible = False

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

        self.update_score(0)

    def start(self):
        self.update_score(self.game.get_setting('ss'))
        self.draw_cards('landscape')
        self.draw_cards('play', self.game.get_setting('cards'))
        self.draw_cards('item', self.game.get_setting('items'))
        self.draw_cards('spell', self.game.get_setting('spells'))
        self.new_deck('treasure', [self.game.get_card('gold coins')])

    def new_round(self):
        self.unequip_all()
        items = self.items.copy()
        spells = self.spells.copy()
        treasure = self.treasure.copy()
        if not any({c.name == 'gold coins' for c in treasure}):
            treasure.append(self.game.get_card('gold coins'))
        
        score = self.score
        self.reset()
        self.update_score(score)
        
        self.new_deck('items', items)
        self.new_deck('spells', spells)
        self.new_deck('treasure', treasure)

        self.draw_cards('landscape')
        self.draw_cards('play', self.game.get_setting('cards'))
        self.draw_cards('item', max((self.game.get_setting('items') - len(self.items), 0)))
        self.draw_cards('spell', max((self.game.get_setting('spells') - len(self.spells), 0)))

#card stuff-------------------------------------------------------------------------------------- 

    def type_to_deck(self, type):
        deck_string = Player_Base.type_to_deck_string(type)
        deck = getattr(self, deck_string, None)
        return deck.copy()
        
    def card_to_deck(self, c):
        deck_string = Player_Base.card_to_deck_string(c)
        deck = getattr(self, deck_string, None)
        return deck.copy()
        
    def string_to_deck(self, deck_string):
        deck = getattr(self, deck_string, None)
        return deck.copy()
                
    def find_card_deck_string(self, c):
        for deck_string in Player_Base.deck_strings:
            if c in self.string_to_deck(deck_string):
                return deck_string
                
    def find_card_deck_string_and_deck(self, c):
        for deck_string in Player_Base.deck_strings:
            deck = self.string_to_deck(deck_string)
            if c in deck:
                return (deck_string, deck)
                
    def has_card(self, name, deck_string=None):
        if deck_string:
            return any({name == o.name for o in self.string_to_deck(deck_string)})
            
        for deck_string in Player_Base.deck_strings:
            if any({name == o.name for o in self.string_to_deck(deck_string)}):
                return deck_string

    def draw_cards(self, type, num=1):
        cards = self.game.draw_cards(type, num=num)
        deck_string = Player_Base.type_to_deck_string(type)
        nd = self.string_to_deck(deck_string) + cards
        self.new_deck(deck_string, nd)
        
        if deck_string == 'landscapes': 
            for c in cards:
                c.start_ongoing(self)
            
        self.add_log({'t': 'draw', 'deck': deck_string, 'c': cards.copy()})
                
        return cards
   
    def add_card(self, c, deck_string=None, i=None):
        if deck_string is None:
            deck_string = Player_Base.card_to_deck_string(c)
        nd = self.string_to_deck(deck_string)
        if nd is not None:
            if i is None:
                i = len(nd)
            nd.insert(i, c)
            self.new_deck(deck_string, nd)
        
            if deck_string == 'played' and hasattr(c, 'start_ongoing') and c not in self.ongoing:
                c.start_ongoing(self)
        
    def remove_card(self, c, deck_string=None):
        if deck_string is None:
            deck_string = Player_Base.card_to_deck_string(c)
        deck = self.string_to_deck(deck_string)
        if c in deck:
            nd = [o for o in deck if o != c]
            self.new_deck(deck_string, nd)

    def replace_card(self, c1, c2):
        data = self.find_card_deck_string_and_deck(c1)
        if data is not None:
            deck_string, nd = data
            i = nd.index(c1)
            self.safe_discard(c1)
            self.add_card(c2, deck_string=deck_string, i=i)
        
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
            self.remove_card(c, deck_string='unplayed')
        c.start(self)
        if c not in self.played:
            self.add_card(c, deck_string='played')
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
                
    def new_deck(self, deck_string, cards):
        setattr(self, deck_string, cards)
        
    def use_item(self, c):
        self.discard_card(c)
        self.add_log({'t': 'ui', 'c': c})
        
    def safe_discard(self, c):
        self.discard_card(c, add_to_discard=False)

    def discard_card(self, c, add_to_discard=True): 
        self.end_og(c)
        if c in self.equipped:
            self.unequip(c)
        for deck_string in Player_Base.deck_strings:
            self.remove_card(c, deck_string=deck_string)
        if add_to_discard:
            self.game.discard.append(c)

    def get_items(self):
        return [c for c in self.items + self.equipped if c.wait is None]
        
    def give_card(self, c, target):
        self.safe_discard(c)
        deck_string = Player_Base.card_to_deck_string(c)
        nd = target.string_to_deck(deck_string)
        nd.append(c)
        target.new_deck(deck_string, nd)

    def steal_card(self, c, target):
        self.safe_discard(c)
        deck_string = Player_Base.card_to_deck_string(c)
        target.add_card(c, deck_string=deck_string)
        
    def steal_random_card(self, type, target):
        c = None
        deck_string = Player_Base.type_to_deck_string(type)
        deck = target.string_to_deck(deck_string)
        if deck:  
            c = random.choice(deck)
            target.safe_discard(c)
            self.add_card(c, deck_string=deck_string)
        else:
            if deck_string == 'treasure':
                cards = self.draw_cards(deck_string)
                c = cards[0]
        return c

#equipment stuff------------------------------------------------------------------------------------

    def equip(self, c):
        self.remove_card(c, deck_string='items')
        self.add_card(c, deck_string='equipped')
        
    def unequip(self, c): 
        self.remove_card(c, deck_string='equipped')
        self.add_card(c, deck_string='items')
        self.end_og(c)
        
    def unequip_all(self):
        for c in self.equipped.copy():
            self.unequip(c)
            
#spell stuff----------------------------------------------------------------------------------------

    def add_active_spell(self, c):
        self.add_card(c, deck_string='active_spells')
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
            if not free:
                self.remove_coins()
            self.add_card(c)
            self.add_log({'t': 'buy', 'c': c})
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
        
    def ready_coin(self):
        self.coin = -1
        
    def ready_dice(self):
        self.dice = -1
        
    def start_request(self, c):      
        if c.wait == 'flip': 
            self.ready_coin()
        elif c.wait == 'roll':
            self.ready_dice()
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
                    
    def set_active_card(self, c):
        self.active_card = c
        
    def remove_active_card(self):
        self.active_card = None
  
    def process_request(self):
        self.requests.sort(key=Player_Base.sort_request_cards)
        c = self.requests[0]
        if c is not self.active_card:
            self.cancel_request()
            self.start_request(c)
            self.set_active_card(c)
  
        confirm = False

        if c.wait == 'flip':
            if self.coin is not None:
                c.wait = None
                c.flip(self, self.coin)
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
            self.remove_active_card()
            
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
        self.ongoing.sort(key=Player_Base.sort_og_cards)

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
        return not (self.unplayed or self.requests)
        
    def end_round(self, use_treasure):
        if hasattr(self.game.event, 'end'):
            self.game.event.end(self)

        for c in self.treasure:
            if hasattr(c, 'end'):
                c.end(self)

        self.game_over = True
        
    def finished_game(self):
        return self.game_over and not self.requests
        
    def auto_select(self):
        s = None
        
        if self.game.done():
            return
            
        if self.selection:
            s = random.choice(self.selection)
            
        elif not self.requests:
            cards = self.get_selection()
            if cards:
                s = random.choice(cards) 

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

#sim stuff------------------------------------------------------------------------------------------

    def sim_copy(self, game):
        return game.get_player(self.pid)        

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
        
        