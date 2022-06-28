import random

import exceptions

from . import player_base

class Game_Base:
    @classmethod
    def copy(cls, g):
        self = cls('turbo', g.settings.copy(), g.cards)
        
        self.uid = g.uid
        
        self.status = g.status
        self.current_turn = g.current_turn
        self.round = g.round

        self.players = [p.copy(self) for p in g.players]
        for i in range(len(self.players)):
            self.players[i].set_cards()

        self.event = g.event.light_sim_copy(self) if g.event else None
        self.shop = [c.light_sim_copy(self) for c in g.shop]
        self.discard = [c.light_sim_copy(self) for c in g.discard[:3]]
        
        return self
        
    @classmethod
    def simulator(cls, settings, cards):
        self = cls('turbo', settings, cards)
        self.add_cpus()
        self.new_game()
        return self
        
    def __init__(self, mode, settings, cards):
        self.mode = mode
        self.settings = settings
        self.cards = cards

        self.pid = 0
        self.uid = 0
        self.status = ''
        self.current_turn = 0
        self.round = 0

        self.players = [] 
        self.shop = []
        self.discard = []
        
        self.event = None
        self.vote_card = self.get_card('vote', uid=-1)

        self.mem = []
        self.counter = 0
        
    def done(self):
        return self.status == 'new game' or self.status == 'next round'

#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        for p in self.players: 
            p.reset()
        self.shuffle_players()
        self.uid = len(self.players)
        for p in self.players:
            p.start()

        self.current_turn = 0
        self.round = 1

        self.discard.clear()
        self.restock_shop()
        self.set_event()
        
        self.mem.clear()
        self.counter = 0
  
        self.new_turn()
        self.new_status('playing')

    def new_round(self):
        self.shuffle_players() 
        for p in self.players:
            p.new_round()

        self.current_turn = 0
        self.round += 1

        self.restock_shop()
        self.set_event()

        self.mem.clear()
        self.counter = 0
   
        self.new_turn()
        self.new_status('playing')

    def reset(self):
        for p in self.players: 
            p.reset()   
                
    def add_cpus(self):
        self.pid = 0
        for _ in range(self.get_setting('cpus')):  
            p = player_base.Player_Base(self, self.pid)
            self.players.append(p)      
            self.pid += 1

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
     
    def add_card_data(self, cls):
        self.cards[cls.type][cls.name] = cls
     
    def set_card_data(self, data):
        self.cards = data
     
    def get_new_uid(self):
        uid = self.uid
        self.uid += 1
        return uid
     
    def draw_cards(self, type='play', num=1):
        deck = self.cards[type]
        weights = [cls.weight for cls in deck.values()]
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        for i, name in enumerate(cards):
            cards[i] = self.get_card(name)
        return cards
        
    def get_card(self, name, uid=None):
        if uid is None:
            uid = self.get_new_uid()
        for type, deck in self.cards.items():
            cls = deck.get(name)
            if cls:
                return cls(self, uid)
            
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
            if p.find_card_deck_string(c):
                return p
        
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if c.type == 'item']
        
    def get_discard(self):
        return self.discard.copy()
        
    def restore(self, c):
        restored = False
        if c in self.discard:
            self.discard.remove(c)
            restored = True
        return restored
            
    def get_last_item(self):
        items = self.get_discarded_items()
        if items: 
            return i[0] 
        else:
            return self.draw_cards('item')[0]    

    def is_event(self, name):
        if self.event:
            return self.event.name == name 
  
#shop stuff---------------------------------------------------------------------------------------
        
    def fill_shop(self, m=3):
        num = max({m - len(self.shop), 0})
        cards = [] 
        decks = ('play', 'item', 'spell')
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
            #self.debug()
            #self.debug()
            raise exceptions.InfiniteLoop
                     
#settings stuff---------------------------------------------------------------------------------------

    def get_setting(self, setting):
        return self.settings[setting]
        
    def get_settings(self):
        return self.settings.copy()

#turn stuff-----------------------------------------------------------------------------------------------
   
    def main(self):
        for p in self.players:
            p.update()
            self.advance_turn() 

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
            
    def set_event(self):
        self.event = self.draw_cards('event', 1)[0]
        self.event.start(self)
            
#ending stuff---------------------------------------------------------------------------------------

    def get_winners(self):
        hs = max({p.score for p in self.players})
        return [p.pid for p in self.players if p.score == hs]

    def debug(self):
        for p in self.players:
            print(p.requests, p.selection, p.get_selection(), p.unplayed, p.gone, p.vote)
        print(self.status, self.done())
  