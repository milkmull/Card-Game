import random

from . import card_base
from . import extra_cards

#play

class Michael(card_base.Card):
    name = 'michael'
    type = 'play'
    weight = 1
    tags = ['human']
    def start(self, player):
        sp = 5 if self.game.check_first(player) else 2
        for p in self.get_opponents_with_points(player):
            player.steal(self, sp, p)
        
class Dom(card_base.Card):
    name = 'dom'
    type = 'play'
    weight = 3
    tags = ['human']  
    def start(self, player):
        for p in self.game.players:
            gp = 5 if p == player else 1 
            for c in p.played:
                if 'animal' in c.tags: 
                    player.gain(self, gp)
        
class Jack(card_base.Card):
    name = 'jack'
    type = 'play'
    weight = 1
    tags = ['human'] 
    def get_selection(self, player):
        return self.cards
        
    def start(self, player):               
        if len(player.played + player.unplayed) < self.game.get_setting('cards') + 5:
            self.cards = self.game.draw_cards('play', num=len(self.game.players))
            player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:  
            c = player.selected.pop(0)
            self.cards.remove(c)
            player.add_card(c, deck_string='unplayed')
            for p, c in zip(self.get_opponents(player), self.cards):
                p.add_card(c, deck_string='unplayed')
            
class Mary(card_base.Card):
    name = 'mary'
    type = 'play'
    weight = 3
    tags = ['human']
    def start(self, player):
        if self.game.check_last(player):
            for p in self.get_opponents(player):    
                p.lose(self, 6)
                    
class Daniel(card_base.Card):
    name = 'daniel'
    type = 'play'
    weight = 2
    tags = ['human']   
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        for p in self.get_opponents(player):
            added, c = self.check_index(p, i, tags=['human'])
            if added:
                player.steal(self, 5, p)

class Emily(card_base.Card):
    name = 'emily'
    type = 'play'
    weight = 2
    tags = ['human']  
    def start(self, player):
        self.start_ongoing(player)

    def start_ongoing(self, player):
        player.add_og(self, 'cont')
 
    def ongoing(self, player, log):
        i = player.played.index(self)
        for j in range(i + 1, i + 3):
            added, c = self.check_index(player, j, tags=['human'])
            if added:
                player.gain(self, 5 * (j - i))
                  
class GamblingBoi(card_base.Card):
    name = 'gambling boi'
    type = 'play'
    weight = 3
    tags = ['human', 'city']   
    def start(self, player):
        score = (len(player.played) - len(player.unplayed)) * 2
        if score < 0:
            player.lose(self, -score)
        elif score > 0:
            player.gain(self, score)
            
class Mom(card_base.Card):
    name = 'mom'
    type = 'play'
    weight = 2
    tags = ['human']  
    def get_selection(self, player):
        return self.get_opponents_with_points(player)
        
    def start(self, player):
        if player.has_card('city', deck_string='landscapes'):
            player.draw_cards('treasure')
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if coin: 
            self.wait = 'select' 
        else: 
            player.lose(self, 4)
            
    def select(self, player, num):
        if num:
            player.steal(self, 6, player.selected.pop(0))
            
class Dad(card_base.Card):
    name = 'dad'
    type = 'play'
    weight = 1
    tags = ['human']   
    def get_selection(self, player):
        hs = max({p.score for p in self.game.players}, default=-1)
        return [p for p in self.game.players if p.score == hs]
        
    def start(self, player):
        if player.has_card('curse', deck_string='active_spells'):
            for p in self.get_opponents(player): 
                p.lose(self, 10)    
        else:
            player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            p = player.selected.pop(0)
            lp = 5 if p == player else 10
            p.lose(self, lp)
            
class AuntPeg(card_base.Card):
    name = 'aunt peg'
    type = 'play'
    weight = 2
    tags = ['human']    
    def start(self, player):
        if self in player.played:
            gp = player.played.index(self) + 1  
        else:
            gp = len(player.played) + 1
        player.gain(self, gp)
        
class UncleJohn(card_base.Card):
    name = 'uncle john'
    type = 'play'
    weight = 1
    tags = ['human']  
    def get_selection(self, player):
        players = self.get_opponents_with_points(player)
        hs = max({p.score for p in players}, default=-1)
        
        return [p for p in players if p.score == hs]

    def start(self, player):
        if self.game.check_first(player):
            player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            player.steal(self, 7, player.selected.pop(0))
    
class Kristen(card_base.Card):
    name = 'kristen'
    type = 'play'
    weight = 1
    tags = ['human']  
    def start(self, player):
        for _ in player.active_spells: 
            player.draw_cards('treasure')
    
class Joe(card_base.Card):
    name = 'joe'
    type = 'play'
    weight = 1
    tags = ['human']
    def get_selection(self, player):
        return [p for p in self.get_opponents_with_points(player) if p.items]
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            p = player.selected.pop(0)
            sp = len(p.items) * 3
            player.steal(self, sp, p)
            
class Robber(card_base.Card):
    name = 'robber'
    type = 'play'
    weight = 3
    tags = ['human', 'city']
    def start(self, player):
        player.draw_cards('item')
        if self.game.is_event('item frenzy'): 
            player.add_request(self, 'flip')
            
    def flip(self, player, coin):
        if coin:
            player.draw_cards('treasure')
       
class Ninja(card_base.Card):
    name = 'ninja'
    type = 'play'
    weight = 3
    tags = ['human']         
    def start(self, player):
        if any({any({'human' in c.tags for c in p.played}) for p in self.get_opponents(player)}):
            lp = 4
            for p in self.get_opponents(player):
                p.lose(self, sum([lp for c in p.played if 'human' in c.tags]))
  
class MaxTheDog(card_base.Card):
    name = 'max the dog'
    type = 'play'
    weight = 1
    tags = ['animal', 'city', 'dog']    
    def start(self, player):
        if self in player.played:
            lp = player.played.index(self) + 1 
        else:
            lp = len(player.played) + 1
            
        for p in self.get_opponents(player):  
            p.lose(self, lp)
 
class BasilTheDog(card_base.Card):
    name = 'basil the dog'
    type = 'play'
    weight = 1
    tags = ['animal', 'city', 'dog']            
    def start(self, player):
        if self.game.check_last(player) or any({'dog' in c.tags and c != self for c in player.played}):
            player.gain(self, 10)
            
class CopyCat(card_base.Card):
    name = 'copy cat'
    type = 'play'
    weight = 2
    tags = ['animal', 'city'] 
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, i + 1)
        if added:
            player.play_card(c)
                
class Racoon(card_base.Card):
    name = 'racoon'
    type = 'play'
    weight = 2
    tags = ['animal', 'city', 'forest']  
    def get_selection(self, player):
        return [c.copy() for c in self.game.shop]
        
    def start(self, player):  
        player.add_request(self, 'select')

    def select(self, player, num): 
        if num:
            c = player.selected.pop(0)
            player.buy_card(c.uid, free=True)
            if c.name == 'robber':
                player.gain(self, 15)
            
class Fox(card_base.Card):
    name = 'fox'
    type = 'play'
    weight = 2
    tags = ['animal', 'forest', 'city']  
    def get_selection(self, player):
        return self.get_opponents_with_points(player)
        
    def start(self, player):
        player.add_request(self, 'select')
        if self.game.check_first(player):
            c = self.copy()
            player.add_request(c, 'flip')
    
    def select(self, player, num):
        if num:
            player.steal(self, 5, player.selected.pop(0))
            
    def flip(self, player, coin):
        if coin:
            player.draw_cards('treasure')
            
class Cow(card_base.Card):
    name = 'cow'
    type = 'play'
    weight = 2
    tags = ['animal', 'farm']   
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')

    def ongoing(self, player, log):
        i = player.played.index(self)
        for i in range(i + 1, len(player.played)):
            added, c = self.check_index(player, i, tags=['plant'])
            if added:
                player.gain(self, 4)
                if 'farm' in c.tags:
                    player.draw_cards('treasure')
            
class Shark(card_base.Card):
    name = 'shark'
    type = 'play'
    weight = 1
    tags = ['animal', 'water']
    def start(self, player):
        for p in self.get_opponents(player):
            for i in range(len(p.played)):
                self.check_index(p, i, tags=['water', 'animal'], inclusive=True)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
            
    def ongoing(self, player, log):
        for p in self.get_opponents(player): 
            for i in range(len(p.played)):
                added, c = self.check_index(p, i, tags=['water', 'animal'], inclusive=True)
                if added:
                    player.steal(self, 5, p)

class Fish(card_base.Card):
    name = 'fish'
    type = 'play'
    weight = 15
    tags = ['animal', 'water']   
    def start(self, player):
        for c in player.played:
            if c.name == 'fish':
                player.gain(self, 5)  
        player.gain(self, 5)
                
class Pelican(card_base.Card):
    name = 'pelican'
    type = 'play'
    weight = 1
    tags = ['animal', 'sky', 'water']      
    def start(self, player):     
        gp = 0
        for p in self.game.players:
            for c in p.played:  
                if c.name == 'fish':
                    gp += 5
        player.gain(self, gp)
                
class LuckyDuck(card_base.Card):
    name = 'lucky duck'
    type = 'play'
    weight = 1
    tags = ['animal', 'sky', 'water']  
    def start(self, player):
        for _ in range(len(player.active_spells)):
            player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if coin:
            player.gain(self, 5)
                
class LadyBug(card_base.Card):
    name = 'lady bug'
    type = 'play'
    weight = 2
    tags = ['animal', 'sky', 'garden', 'bug']   
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, i + 1)
        if added:
            if 'animal' in c.tags:
                player.gain(self, 10)
            else:
                player.lose(self, 5)
            
class Mosquito(card_base.Card):
    name = 'mosquito'
    type = 'play'
    weight = 2
    tags = ['animal', 'sky', 'bug']   
    def start(self, player):
        for p in self.get_opponents_with_points(player): 
            for c in p.played:
                if 'human' in c.tags:
                    sp = 8 if self.game.is_event('flu') else 4
                    player.steal(self, 4, p)
                        
class Snail(card_base.Card):
    name = 'snail'
    type = 'play'
    weight = 1
    tags = ['animal', 'garden', 'water', 'bug'] 
    def start(self, player):
        if self.game.check_last(player):
            player.gain(self, 20) 
        else:     
            player.lose(self, 5)
    
class Dragon(card_base.Card):
    name = 'dragon'
    type = 'play'
    weight = 1
    tags = ['monster', 'sky'] 
    def get_selection(self, player):
        return self.get_opponents_with_points(player)

    def start(self, player):
        players = self.get_players_custom(player, lambda p: p.treasure)
        self.deploy(player, players, 'flip')
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        if self.players:
            player.add_og(self, 'cont')
            
    def flip(self, target, coin):
        self.t_coin = coin
        
    def ongoing(self, player, log):
        if self.players:
            players, results = self.get_flip_results()
            for p, t_coin in zip(players, results):
                if not t_coin: 
                    player.steal_random_card('treasure', p)
                    self.players.remove(p)
        else:
            player.end_og(self)

class Clam(card_base.Card):
    name = 'clam'
    type = 'play'
    weight = 2
    tags = ['animal', 'water']
    def start(self, player):
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):  
        if coin:
            t = player.draw_cards('treasure')[0]
            if t.name == 'pearl': 
                player.add_request(self, 'flip')
    
class Cactus(card_base.Card):
    name = 'cactus'
    type = 'play'
    weight = 3
    tags = ['plant', 'desert']
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        if player.get_played_card(-1) == self:
            player.invincible = True
        else:
            player.invincible = False
    
class PoisonIvy(card_base.Card):
    name = 'poison ivy'
    type = 'play'
    weight = 2
    tags = ['plant', 'forest']
    def start(self, player):
        for p in self.get_opponents(player):
            for c in p.played:
                if 'human' in c.tags:  
                    p.lose(self, 5)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):   
        i = player.played.index(self)
        for i in range(i + 1, len(player.played)):
            added, c = self.check_index(player, i, tags=['human'])
            if added:
                player.lose(self, 5)
    
class Rose(card_base.Card):
    name = 'rose'
    type = 'play'
    weight = 2
    tags = ['plant', 'garden'] 
    def get_selection(self, player):
        return self.get_opponents(player)

    def start(self, player):   
        ss = self.game.get_setting('ss')
        if player.score < ss:
            player.gain(self, 10)      
        elif player.score > ss:  
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num: 
            player.give(self, 15, player.selected.pop(0))
     
class MrSquash(card_base.Card):
    name = 'mr. squash'
    type = 'play'
    weight = 1
    tags = ['plant', 'farm']   
    def start(self, player):
        for p in self.get_opponents(player): 
            for c in p.played:   
                if 'plant' in c.tags:
                    player.steal(self, 5, p)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
            
    def ongoing(self, player, log):
        for p in self.game.players:
            if any({c.name == 'mrs. squash' for c in p.played}):
                player.gain(self, 20)
                player.end_og(self)
                
class MrsSquash(card_base.Card):
    name = 'mrs. squash'
    type = 'play'
    weight = 1
    tags = ['plant', 'farm']
    def start(self, player):
        for p in self.get_opponents(player): 
            for c in p.played:   
                if 'plant' in c.tags:
                    player.steal(self, 5, p)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
            
    def ongoing(self, player, log):
        for p in self.game.players:
            if any({c.name == 'mr. squash' for c in p.played}):
                player.gain(self, 20)
                player.end_og(self)

class Uphalump(card_base.Card):
    name = 'uphalump'
    type = 'play'
    weight = 1
    tags = ['monster']
    def start(self, player):
        player.lose(self, 5)
            
class Ghost(card_base.Card):
    name = 'ghost'
    type = 'play'
    weight = 2
    tags = ['monster']   
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, max({i - 1, 0}), tags=['human'])
        if added:
            player.play_card(c)

class Sapling(card_base.Card):
    name = 'sapling'
    type = 'play'
    weight = 2
    tags = ['plant', 'forest']    
    def start(self, player):
        player.add_request(self, 'roll')
            
    def roll(self, player, roll):
        lp = sum([roll for c in player.played if 'plant' in c.tags])
        for p in self.get_opponents(player):   
            p.lose(self, lp)
           
class Vines(card_base.Card):
    name = 'vines'
    type = 'play'
    weight = 2
    tags = ['plant', 'garden']  
    def start(self, player):
        if self in player.played:   
            i = player.played.index(self)    
        else:  
            i = len(player.played) - 1 
        for c in player.played[i::-1]: 
            self.game.transform(c, 'vines')
            
class Zombie(card_base.Card):
    name = 'zombie'
    type = 'play'
    weight = 2
    tags = ['monster', 'human']   
    def start(self, player):
        for p in self.get_opponents(player):
            if any({'human' in c.tags for c in p.played}):   
                player.steal(self, 5, p)
                
        if player.has_card('curse', deck_string='active_spells'):
            player.draw_cards('treasure')
            player.draw_cards('item')
            
class Jumble(card_base.Card):
    name = 'jumble'
    type = 'play'
    weight = 1
    tags = ['monster']
    def start(self, player):
        if player.has_card('item hex', deck_string='active_spells'): 
            player.draw_cards('treasure', num=2)    
        self.deploy(player, self.get_opponents(player), 'flip')
            
    def flip(self, player, coin):
        if not coin: 
            player.lose(self, 10)
            
class DemonWaterGlass(card_base.Card):
    name = 'demon water glass'
    type = 'play'
    weight = 1
    tags = ['monster', 'water']
    def start(self, player):
        player.gain(self, 5)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, i + 1, tags=['human'])
        if added:
            player.lose(self, 10)

class Succosecc(card_base.Card):
    name = 'succosecc'
    type = 'play'
    weight = 1
    tags = ['monster'] 
    def get_selection(self, player):
        return self.cards
        
    def start(self, player):
        for p in self.game.players:
            items = p.get_items()
            if items: 
                c = random.choice(items)
                p.safe_discard(c) 
            else: 
                c = self.game.draw_cards('item')[0]
            self.players.append(p)
            self.cards.append(c)
        player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            c = player.selected.pop(0)
            self.cards.remove(c)
            self.players.remove(player)
            random.shuffle(self.cards)
            for p, c in zip(self.players, self.cards):
                p.add_card(c, deck_string='items')
            self.players.clear()
            self.cards.clear()
                
class Sunflower(card_base.Card):
    name = 'sunflower'
    type = 'play'
    weight = 3
    tags = ['plant', 'garden']   
    def start(self, player):
        if self in player.played:
            i = player.played.index(self)  
        else: 
            i = len(player.played)   
        points = 5 - i
        if points > 0: 
            player.gain(self, points)  
        elif points < 0: 
            player.lose(self, -points)

class LemonLord(card_base.Card):
    name = 'lemon lord'
    type = 'play'
    weight = 1
    tags = ['plant', 'farm']   
    def start(self, player): 
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        for i in range(i + 1, len(player.played)):
            added, c = self.check_index(player, i, tags=['plant'])
            if added:
                player.gain(self, 5)
            
class Wizard(card_base.Card):
    name = 'wizard'
    type = 'play'
    weight = 3
    tags = ['human']   
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.active_spells.copy() 
        elif len(player.selected) == 1: 
            return [p for p in self.get_opponents(player) if player.selected[0].can_cast(p)]

    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
            
    def select(self, player, num):      
        if num == 1:
            self.wait = 'select'
        elif num == 2:
            c, p = player.selected
            player.cast(p, c)
            if any({c.name == 'wizard' for c in p.played}):
                player.gain(self, 10)
                
class HauntedOak(card_base.Card):
    name = 'haunted oak'
    type = 'play'
    weight = 1
    tags = ['plant', 'forest', 'monster']
    def get_selection(self, player):
        return self.get_opponents_with_points(player)
        
    def start(self, player):
        plants = len([c for c in player.played if 'plant' in c.tags])
        if (self in player.played and plants >= 3) or (self not in player.played and plants >= 2):
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.steal(self, 10, player.selected.pop(0))
  
class OfficeFern(card_base.Card):
    name = 'office fern'
    type = 'play'
    weight = 3
    tags = ['plant', 'city']  
    def start(self, player):
        if self in player.played:
            i = player.played.index(self) 
        else: 
            i = len(player.played)
        lp = i + 1
        player.lose(self, lp)

class Camel(card_base.Card):
    name = 'camel'
    type = 'play'
    weight = 2
    tags = ['animal', 'desert']
    def check_water(self, p):
        return any({'water' in c.tags for c in p.played})
        
    def count_water(self, p):
        return len([c for c in p.played if 'water' in c.tags])
        
    def get_selection(self, player):
        m = max({self.count_water(p) for p in self.get_opponents(player)})    
        return [p for p in self.get_opponents(player) if self.count_water(p) == m]
        
    def start(self, player):
        if any({self.check_water(p) for p in self.get_opponents_with_points(player)}):
            r = 'select'
        else:  
            r = 'flip'
        player.add_request(self, r)
                
    def select(self, player, num):
        if num:
            player.steal(self, 5, player.selected.pop(0))
            
    def flip(self, player, coin):
        if coin: 
            player.draw_cards('treasure')
            
class RattleSnake(card_base.Card):
    name = 'rattle snake'
    type = 'play'
    weight = 2
    tags = ['animal', 'desert'] 
    def start(self, player):
        players = self.get_players_custom(player, lambda p: p.score and p.treasure)
        if len(players) > 1:
            self.deploy(player, players, 'roll')
            self.start_ongoing(player)
            
        elif players:
            player.steal_random_card('treasure', players[0])
            
    def start_ongoing(self, player):
        if self.players:
            player.add_og(self, 'cont')
            
    def roll(self, player, roll):
        self.t_roll = roll

    def ongoing(self, player, log):
        for c, p in zip(self.cards.copy(), self.players.copy()):
            if not p.treasure:
                self.players.remove(p)
                self.cards.remove(c)
        players, results = self.get_roll_results()
        if len(self.players) == len(results) > 0:
            m = max({r for r in results})
            highest = []
            for p, r in zip(players, results):
                if r == m and p.treasure:
                    highest.append(p)
            if len(highest) <= 1:
                if highest:
                    player.steal_random_card('treasure', highest[0])
                player.end_og(self)
            else: 
                self.deploy(player, highest, 'roll')
        elif not self.players:
            player.end_og(self)
            
class TumbleWeed(card_base.Card):
    name = 'tumble weed'
    type = 'play'
    weight = 3
    tags = ['plant', 'desert']
    def start(self, player):
        if any({'human' in c.tags for c in player.played}):
            player.lose(self, 10)
        else:
            player.gain(self, 5)

class Mummy(card_base.Card):
    name = 'mummy'
    type = 'play'
    weight = 2
    tags = ['human', 'desert', 'monster']     
    def get_selection(self, player):
        return self.get_opponents_with_points(player)
        
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        for i in range(i + 1, len(player.played)):
            added, c = self.check_index(player, i, tags=['monster'])
            if added:
                player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            player.steal(self, 5, player.selected.pop(0))
      
class Pig(card_base.Card):   
    name = 'pig'
    type = 'play'
    weight = 2
    tags = ['animal', 'farm'] 
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        for i in range(i + 1, len(player.played)):
            added, c = self.check_index(player, i, tags=['plant'])
            if added:
                if 'farm' in c.tags:
                    player.gain(self, 10)
                else:
                    player.gain(self, 5)
            elif not c:
                break
            
class Corn(card_base.Card):
    name = 'corn'
    type = 'play'
    weight = 2
    tags = ['plant', 'farm']
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.get_items()
        elif len(player.selected) == 1: 
            return self.get_opponents(player)
        
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, i + 1)
        if added:
            if 'human' in c.tags:
                player.gain(self, 10)
            else:
                player.add_request(self, 'select')
            
    def select(self, player, num):
        if num == 1:
            self.wait = 'select'          
        elif num == 2:   
            c, p = player.selected
            player.give_card(c, p)
  
class Bear(card_base.Card):
    name = 'bear'
    type = 'play'
    weight = 2
    tags = ['animal', 'forest'] 
    def start(self, player):
        sp = 4 if self.game.is_event('parade') else 2
        for p in self.get_opponents_with_points(player):   
            player.steal(self, sum([sp for c in p.played if 'human' in c.tags]), p)  
            
class WaterLily(card_base.Card):
    name = 'water lily'
    type = 'play'
    weight = 2
    tags = ['plant', 'water']  
    def start(self, player):
        gp = len(player.get_items() + player.spells) + (len(player.active_spells) * 5)
        player.gain(self, gp)

class Bat(card_base.Card):
    name = 'bat'
    type = 'play'
    weight = 2
    tags = ['animal', 'sky']
    def get_selection(self, player):
        if self.mode == 0:
            return self.get_players_custom(player, lambda p: p.treasure) 
        elif self.mode == 1: 
            o1 = extra_cards.Blank(self.game, self.game.get_new_uid(), 'draw item')
            o2 = extra_cards.Blank(self.game, self.game.get_new_uid(), 'draw spell')
            return [o1, o2]
        
    def start(self, player):
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if not coin: 
            self.mode = 1  
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if self.mode == 0: 
            if num: 
                player.steal_random_card('treasure', player.selected.pop(0))     
        elif self.mode == 1:  
            if num: 
                o = player.selected.pop(0)
                if 'item' in o.name:  
                    player.draw_cards('item')   
                elif 'spell' in o.name:
                    player.draw_cards('spell')
        
class SkyFlower(card_base.Card):
    name = 'sky flower'
    type = 'play'
    weight = 2
    tags = ['plant', 'sky']  
    def get_selection(self, player):
        return self.get_opponents(player)
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.give(self, 5, player.selected.pop(0))
            player.draw_cards('treasure')

class GardenSnake(card_base.Card):
    name = 'garden snake'
    type = 'play'
    weight = 2
    tags = ['animal', 'garden', 'snake']   
    def get_selection(self, player):
        return self.get_opponents_with_points(player)
        
    def start(self, player):
        if self.game.check_first(player):
            player.add_request(self, 'select')  
        else:    
            player.lose(self, 4)
            
    def select(self, player, num):
        if num: 
            p = player.selected.pop(0)
            player.steal(self, 4, p)
 
class BigSandWorm(card_base.Card):
    name = 'big sand worm'
    type = 'play'
    weight = 2
    tags = ['animal', 'desert'] 
    def start(self, player):
        if self.game.check_last(player):
            player.gain(self, 5)  
        else: 
            player.lose(self, 5)
            
class LostPalmTree(card_base.Card):
    name = 'lost palm tree'
    type = 'play'
    weight = 2
    tags = ['plant', 'desert', 'water']  
    def start(self, player):
        t = False
        for c in player.landscapes.copy():
            if c.name == 'desert':
                self.game.transform(c, 'water')
                t = True
        if t:
            player.draw_cards('treasure')
                    
class Seaweed(card_base.Card):
    name = 'seaweed'
    type = 'play'
    weight = 3
    tags = ['plant', 'water']   
    def start(self, player):
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if coin: 
            player.gain(self, 3)
            player.draw_cards('treasure') 
        else:
            player.lose(self, 4)
        
class ScubaBaby(card_base.Card):
    name = 'scuba baby'
    type = 'play'
    weight = 3
    tags = ['human', 'water']  
    def start(self, player):
        player.gain(self, 3)

#item
     
class FishingPole(card_base.Card):
    name = 'fishing pole'
    type = 'item'
    weight = 4
    def can_use(self, player):
        return bool([c for p in self.get_opponents(player) for c in p.played if c.name == 'fish'])
        
    def get_selection(self, player):
        if len(player.selected) == 0: 
            return player.played.copy()  
        elif len(player.selected) == 1: 
            return [c for p in self.get_opponents(player) for c in p.played if c.name == 'fish']

    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num == 1:
            self.wait = 'select'
        elif num == 2:
            self.game.swap(player.selected[0], player.selected[1])
            player.use_item(self)
       
class InvisibilityCloak(card_base.Card):
    name = 'invisibility cloak'
    type = 'item'
    weight = 2
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.invincible = True
        player.add_og(self, 'iv')

    def ongoing(self, player, log): 
        player.invincible = False
        player.use_item(self)
       
class LastTurnPass(card_base.Card):
    name = 'last turn pass'
    type = 'item'
    weight = 4
    def can_use(self, player):
        return self.game.players[-1] != player
                
    def start(self, player):
        if self.game.players[-1] != player:
            self.game.shift_down(player)
            player.use_item(self)
                
class SpeedBoostPotion(card_base.Card):
    name = 'speed boost potion'
    type = 'item'
    weight = 4   
    def can_use(self, player):
        return self.game.players[0] != player

    def start(self, player):
        if self.game.players[0].pid != player.pid:
            self.game.shift_up(player)
            player.use_item(self)
        
class Mirror(card_base.Card):
    name = 'mirror'
    type = 'item'
    weight = 2   
    def can_use(self, player):
        return player.active_spells and all({any({c.can_cast(p) for p in self.get_opponents(player)}) for c in player.spells})
        
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.active_spells.copy()
        elif len(player.selected) == 1:
            return [p for p in self.get_opponents(player) if player.selected[0].can_cast(p)]
            
    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num == 1:
            self.wait = 'select'
        elif num == 2:
            c, p = player.selected
            player.cast(p, c)
            player.use_item(self)
       
class Sword(card_base.Card):
    name = 'sword'
    type = 'item'
    weight = 2  
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'sp')

    def ongoing(self, player, log):
        player.steal(self, log['sp'], log['target'])         
        player.use_item(self)
       
class Fertilizer(card_base.Card):
    name = 'fertilizer'
    type = 'item'
    weight = 3
    def can_use(self, player):
        return any({'plant' in c.tags for c in player.played})
        
    def get_selection(self, player):
        return [c for c in player.played if 'plant' in c.tags]
        
    def start(self, player):
        if any({'plant' in c.tags for c in player.played}):
            player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            player.play_card(player.selected.pop(0))
            player.use_item(self)
               
class TreasureChest(card_base.Card):
    name = 'treasure chest'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('treasure')
        player.use_item(self)
    
class Boomerang(card_base.Card):
    name = 'boomerang'
    type = 'item'
    weight = 4
    def start(self, player):
        if not any({c.name == self.name for c in player.equipped}):
            self.start_ongoing(player)
            
    def start_ongoing(self, player):
        if not self.game.is_event('negative zone'):
            player.add_og(self, 'lp')
        else:
            player.add_og(self, 'gp')
        
    def ongoing(self, player, log):
        if log['t'] == 'lp':  
            attr = 'gain'
            key1 = 'lp'
            key2 = 'gp'   
        else:   
            attr = 'lose'
            key1 = 'gp'
            key2 = 'lp'

        log[key2] = getattr(player, attr)(self, log[key1] * 2, d=True) // 2
        log['t'] = key2
            
        player.use_item(self)
     
class BathTub(card_base.Card):
    name = 'bath tub'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return any([p.active_spells for p in self.game.players])
        
    def get_selection(self, player):
        return [c for p in self.game.players for c in p.active_spells]
        
    def start(self, player):
        player.add_request(self, 'select')

    def select(self, player, num):
        if num:
            c = player.selected.pop(0)
            for p in self.game.players:
                if c in p.active_spells:  
                    p.discard_card(c)
                    player.use_item(self)  
                    break
                    
class Detergent(card_base.Card):
    name = 'detergent'
    type = 'item'
    weight = 1
    def can_use(self, player):
        return False
        
    def start(self, player):
        return
        
class FutureOrb(card_base.Card):
    name = 'future orb'
    type = 'item'
    weight = 1
    def get_target(self, player):
        i = self.game.players.index(player) - 1
        p = self.game.players[i]
        return p
        
    def can_use(self, player):  
        return self.get_target(player).unplayed
        
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.unplayed.copy()
        elif len(player.selected) == 1:
            return self.get_target(player).unplayed.copy()
        
    def start(self, player):
        player.add_request(self, 'select')

    def select(self, player, num):
        if num == 1:
            self.wait = 'select'
        elif num == 2:
            c1, c2 = player.selected
            t = self.get_target(player)
            if c1 in player.unplayed and c2 in t.unplayed:
                self.game.swap(c1, c2)
                player.use_item(self)

class Knife(card_base.Card):
    name = 'knife'
    type = 'item'
    weight = 4
    def can_use(self, player):
        return bool(self.get_selection(player))
        
    def get_selection(self, player):
        return [c for p in self.game.players for c in p.played if 'human' in c.tags] + [c for c in player.unplayed if 'human' in c.tags]
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            c = player.selected.pop(0)
            c = self.game.transform(c, 'ghost')
            player.use_item(self)
            
class MagicWand(card_base.Card):
    name = 'magic wand'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('spell')
        player.use_item(self)
            
class LuckyCoin(card_base.Card):
    name = 'lucky coin'
    type = 'item'
    weight = 1
    def can_use(self, player):
        return True
        
    def get_selection(self, player):
        return self.game.players.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            p = player.selected.pop(0)
            player.safe_discard(self)
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'cfe')

    def ongoing(self, player, log):
        log['coin'] = 1
        player.coin = 1
        player.use_item(self)
 
class Sunglasses(card_base.Card):
    name = 'sunglasses'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return len(player.unplayed) > 1 and not player.gone
        
    def get_selection(self, player):
        return player.unplayed.copy()

    def start(self, player):
        player.add_request(self, 'select')

    def select(self, player, num):
        if num:
            c = player.selected.pop(0)
            if c in player.unplayed:
                player.play_card(c, et=False)
                player.use_item(self)
            
class MetalDetector(card_base.Card):
    name = 'metal detector'
    type = 'item'
    weight = 3
    def can_use(self, player):
        return self.game.get_discarded_items()
            
    def start(self, player):
        items = self.game.get_discarded_items()[::-1]
        if items:
            i = items.pop(0)
            self.game.restore(i)
            player.add_card(i, deck_string='items')
            player.use_item(self)
  
class BigRock(card_base.Card):
    name = 'big rock'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return player.played
        
    def get_selection(self, player):
        return player.played.copy()
        
    def start(self, player): 
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            c1 = player.selected.pop(0)
            c2 = self.game.get_card(c1.name)
            if c1 in player.played:
                i = player.played.index(c1) + 1
                player.add_card(c2, deck_string='played', i=i)
                player.use_item(self)
            
class UnluckyCoin(card_base.Card):
    name = 'unlucky coin'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return True
        
    def get_selection(self, player):
        return self.game.players.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:   
            p = player.selected.pop(0)
            player.safe_discard(self)
            self.start_ongoing(p)

    def start_ongoing(self, player):
        player.add_og(self, 'cfe')

    def ongoing(self, player, log):
        log['coin'] = 0
        player.coin = 0
        player.use_item(self)
     
class Torpedo(card_base.Card):
    name = 'torpedo'
    type = 'item'
    weight = 2
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'sp')
        
    def flip(self, player, coin):
        if coin:
            p = self.extra_player
            sp = self.mode
            player.steal(self, sp, p)
        player.use_item(self)

    def ongoing(self, player, log):
        self.extra_player = log['target']
        self.mode = log['sp']
        player.add_request(self, 'flip')
     
class Kite(card_base.Card):
    name = 'kite'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return bool(player.unplayed)
        
    def start(self, player):
        player.draw_cards('play')
        player.use_item(self)
        
class Balloon(card_base.Card):
    name = 'balloon'
    type = 'item'
    weight = 3
    def can_use(self, player):
        return len(player.played) > 1
        
    def start(self, player):
        player.new_deck('played', player.played[::-1])  
        player.use_item(self)
    
class WateringCan(card_base.Card):
    name = 'watering can'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return not player.has_card('water', deck_string='landscapes')
        
    def start(self, player):
        for c in player.landscapes.copy(): 
            self.game.transform(c, 'water')    
        player.use_item(self)
    
class Trap(card_base.Card):
    name = 'trap'
    type = 'item'
    weight = 3
    def can_use(self, player):
        return self.game.shop
        
    def get_selection(self, player):
        return self.game.shop.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            s = player.selected.pop(0)
            self.deploy(player, self.game.players.copy(), 'og', extra_card=s)    
            player.safe_discard(self)
                
    def start_ongoing(self, player):
        player.add_og(self, 'buy')
 
    def ongoing(self, player, log):
        if log['c'] == self.extra_card:
            player.lose(self, 5)
            self.extra_player.use_item(self)
        
class FlowerPot(card_base.Card):
    name = 'flower pot'
    type = 'item'
    weight = 2
    def can_use(self, player):
        return not player.has_card('garden', deck_string='landscapes')
        
    def start(self, player):
        for c in player.landscapes.copy():
            self.game.transform(c, 'garden')    
        player.use_item(self)       
 
class BugNet(card_base.Card):
    name = 'bug net'
    type = 'item'
    weight = 3
    def can_use(self, player):
        return player.played
        
    def get_selection(self, player):
        return player.played.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:   
            c = player.selected.pop(0)
            if c in player.played:
                player.discard_card(c)
                player.use_item(self)
    
#spell

class SpellTrap(card_base.Card):
    name = 'spell trap'
    type = 'spell'
    weight = 3
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'cast')
        
    def ongoing(self, player, log):
        player.lose(self, len(player.unplayed))
        
class Curse(card_base.Card):
    name = 'curse'
    type = 'spell'
    weight = 5
    def can_cast(self, player):
        return True
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        player.add_request(self, 'flip')
            
    def flip(self, player, coin):
        if not coin:
            player.lose(self, 3)
    
class TreasureCurse(card_base.Card):
    name = 'treasure curse'
    type = 'spell'
    weight = 2
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'draw')
        
    def ongoing(self, player, log):
        if log['deck'] == 'treasure':
            t = log['c'][0]
            self.extra_card = t
            player.add_request(self, 'flip')
            
    def flip(self, player, coin):
        if not coin:
            target = random.choice(self.get_opponents(player))
            player.give_card(self.extra_card, target)

class ItemHex(card_base.Card):
    name = 'item hex'
    type = 'spell'
    weight = 5
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def get_selection(self, player):
        return player.items.copy()
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        if len(player.get_items()) < 6:
            player.add_request(self, 'flip')
      
    def flip(self, player, coin):
        if coin:
            player.draw_cards('item')    
        else:
            self.wait = 'select'
            
    def select(self, player, num):
        if num:
            player.discard_card(player.selected.pop(0))
                
class Luck(card_base.Card):
    name = 'luck'
    type = 'spell'
    weight = 1
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'cfe')
        
    def ongoing(self, player, log):
        log['coin'] = 1
        player.coin = 1

class ItemLeech(card_base.Card):
    name = 'item leech'
    type = 'spell'
    weight = 4
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'ui')
        
    def ongoing(self, player, log):
        i = log['c']
        if i:
            c = player.add_request(self, 'flip')
            c.extra_card = i
        
    def flip(self, player, coin):
        if not coin: 
            target = random.choice(self.get_opponents(player))
            if len(target.get_items()) < 6:
                if self.game.restore(self.extra_card):
                    target.add_card(self.extra_card, deck_string='items')

class MummysCurse(card_base.Card):
    name = 'mummys curse'
    type = 'spell'
    weight = 3
    def can_cast(self, player):
        return True
        
    def get_selection(self, player):
        return [c for c in player.played if 'human' in c.tags]
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if coin:
            self.wait = 'select' 
        else: 
            player.lose(self, 5)
            
    def select(self, player, num):
        if num: 
            player.play_card(player.selected.pop(0))
   
class Stardust(card_base.Card):
    name = 'stardust'
    type = 'spell'
    weight = 2
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})

    def start_ongoing(self, player):
        if not self.extra_player:
            self.deploy(player, self.get_opponents(player), 'og')
        else:
            player.add_og(self, 'draw')
        
    def ongoing(self, player, log):
        if log['deck'] == 'treasure':
            p = self.extra_player
            c = self.extra_card
            if p.requests.count(c) < 5 and len(p.treasure) < 6:
                p.add_request(c, 'flip')
                
    def flip(self, player, coin):
        if coin:
            player.draw_cards('treasure')
        else: 
            player.lose(self, 5)
   
class NorthWind(card_base.Card):
    name = 'north wind'
    type = 'spell'
    weight = 1
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        player.add_request(self, 'flip')
        
    def flip(self, player, coin):
        if coin:  
            player.gain(self, 3 * len(player.active_spells))
   
class TheVoid(card_base.Card):
    name = 'the void'
    type = 'spell'
    weight = 1
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})

    def start_ongoing(self, player):
        if not self.game.is_event('negative zone'):
            player.add_og(self, 'lp')
        else:
            player.add_og(self, 'gp')
        
    def ongoing(self, player, log):
        if log['t'] == 'lp':  
            attr = 'gain'
            key1 = 'lp'
            key2 = 'gp'   
        else:   
            attr = 'lose'
            key1 = 'gp'
            key2 = 'lp'

        log[key2] = getattr(player, attr)(self, log[key1] * 2, d=True) // 2
        log['t'] = key2   

#treasure
     
class MustardStain(card_base.Card):
    name = 'mustard stain'
    type = 'treasure'
    weight = 1
    def end(self, player):
        for c in player.items:
            if c.name == 'detergent':
                player.gain(self, 25)
                player.use_item(c)
                break
            
class Gold(card_base.Card):
    name = 'gold'
    type = 'treasure'
    weight = 1
    def end(self, player):
        player.gain(self, 20)
        
class Pearl(card_base.Card):
    name = 'pearl'
    type = 'treasure'
    weight = 4
    def end(self, player):
        player.gain(self, 10)
     
class GoldCoins(card_base.Card):
    name = 'gold coins'
    type = 'treasure'
    weight = 10
    def can_use(self, player):
        return not player.game_over
        
    def get_selection(self, player):
        return self.game.shop.copy()
        
    def start(self, player):   
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            c = player.selected.pop(0)
            if player.buy_card(c.uid):
                if self in player.treasure:
                    player.treasure.remove(self)
                    
    def end(self, player):
        player.gain(self, 1)
     
class Bronze(card_base.Card):
    name = 'bronze'
    type = 'treasure'
    weight = 8
    def end(self, player):
        player.gain(self, 5)
    
class FoolsGold(card_base.Card):
    name = 'fools gold'
    type = 'treasure'
    weight = 3
    def get_selection(self, player):
        return self.get_opponents(player)
        
    def start(self, player):
        self.end(player)
        
    def end(self, player):
        if player.score:
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.give(self, 5, player.selected.pop(0))
  
class GoldenEgg(card_base.Card):
    name = 'golden egg'
    type = 'treasure'
    weight = 2
    def end(self, player):
        player.gain(self, sum([5 for c in player.played if 'animal' in c.tags]))
  
class MagicBean(card_base.Card):
    name = 'magic bean'
    type = 'treasure'
    weight = 2
    def end(self, player):
        player.gain(self, sum([5 for c in player.played if 'plant' in c.tags]))
  
#event
         
class Flu(card_base.Card):
    name = 'flu'
    type = 'event'
    weight = 2
    def start(self, game):
        for p in game.players:
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')
            
    def ongoing(self, player, log):  
        c = log['c'] 
        if 'human' in c.tags:  
            player.lose(self, 5)
                                      
class NegativeZone(card_base.Card):
    name = 'negative zone'
    type = 'event'
    weight = 1
    def start(self, game):
        for p in self.game.players: 
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, ['gp', 'lp', 'sp', 'give'])
            
    def ongoing(self, player, log):
        if log['t'] == 'gp':          
            log['lp'] = player.lose(log['c'], log['gp'] * 2, d=True) // 2
            log['t'] = 'lp'    
            
        elif log['t'] == 'lp':   
            log['gp'] = player.gain(log['c'], log['lp'] * 2, d=True) // 2
            log['t'] = 'gp' 
            
        elif log['t'] == 'sp':   
            log['gp'] = -player.give(log['c'], log['sp'] * 2, log['target'], d=True) // 2
            log['t'] = 'give'  
            
        elif log['t'] == 'give':
            log['sp'] = player.steal(self, -log['gp'] * 2, log['target'], d=True) // 2
            log['t'] = 'sp'
                
class FishingTrip(card_base.Card):
    name = 'fishing trip'
    type = 'event'
    weight = 2
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:
            if c.name == 'fish': 
                player.gain(self, 5)
 
class ItemFrenzy(card_base.Card):
    name = 'item frenzy'
    type = 'event'
    weight = 1
    def start(self, game):
        for p in game.players:
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'ui')
            
    def ongoing(self, player, log):
        if len(player.get_items()) < 6:
            player.draw_cards('item')
 
class SpellReverse(card_base.Card):
    name = 'spell reverse'
    type = 'event'
    weight = 2
    def start(self, game):
        for p in game.players:
            for c in p.spells.copy():
                p.cast(p, c)
                
class SunnyDay(card_base.Card):
    name = 'sunny day'
    type = 'event'
    weight = 2
    def start(self, game):
        return
            
    def end(self, player):
        for c in player.played:
            if 'plant' in c.tags: 
                player.gain(self, 5)
 
class Parade(card_base.Card):
    name = 'parade'
    type = 'event'
    weight = 2
    def start(self, game):
        return
        
    def gain(self, player, count):
        if count == 2:        
            player.gain(self, 2)    
        elif count == 3:   
            player.gain(self, 5)      
        elif count > 4:  
            player.gain(self, 15)
        
    def end(self, player):
        count = 0

        for i in range(len(player.played)):
            c = player.played[i]
            
            if 'human' in c.tags:
                count += 1  
            else:
                self.gain(player, count)   
                count = 0
                
        if count:
            self.gain(player, count)
  
class WindGust(card_base.Card):
    name = 'wind gust'
    type = 'event'
    weight = 1
    def start(self, game):
        for p in game.players: 
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        self.game.restock_shop()
 
class SandStorm(card_base.Card):
    name = 'sand storm'
    type = 'event'
    weight = 0
    def start(self, game):
        for p in game.players:
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')
            
    def ongoing(self, player, log):
        played = [p.played for p in self.game.players]
        random.shuffle(played)
        for p, played in zip(self.game.players, played):
            p.new_deck('played', played)
            
class HuntingSeason(card_base.Card):
    name = 'hunting season'
    type = 'event'
    weight = 2
    def start(self, game):
        for p in game.players: 
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        c = log['c']
        if 'animal' in c.tags:
            player.add_request(self, 'flip')
            
    def flip(self, player, coin):
        if not coin: 
            player.lose(self, 3)

class Harvest(card_base.Card):
    name = 'harvest'
    type = 'event'
    weight = 2
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:   
            if 'plant' in c.tags:  
                gp = 10 if any({l.name in c.tags for l in player.landscapes}) else 5
                player.gain(self, gp)
   
#landscape

class Garden(card_base.Card):
    name = 'garden'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'garden' in c.tags:
            player.play_card(c)
            
class Desert(card_base.Card):
    name = 'desert'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'desert' in c.tags:
            player.play_card(c)            
   
class Graveyard(card_base.Card):
    name = 'graveyard'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'monster' in c.tags:
            player.play_card(c)
            
class City(card_base.Card):
    name = 'city'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'city' in c.tags:
            player.play_card(c)
                
class Farm(card_base.Card):
    name = 'farm'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'farm' in c.tags:
            player.play_card(c)
                
class Forest(card_base.Card):
    name = 'forest'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'forest' in c.tags:
            player.play_card(c)
                
class Water(card_base.Card):
    name = 'water'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'water' in c.tags:
            player.play_card(c)
                
class Sky(card_base.Card):
    name = 'sky'
    type = 'landscape'
    weight = 1
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'sky' in c.tags:
            player.play_card(c)
    