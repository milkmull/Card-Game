import random
from card_base import *

def any(elements):
    for e in elements:
        if e:
            return True
    return False

class Michael(Card):
    name = 'michael'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        sp = 5 if self.game.check_first(player) else 2
        for p in self.sort_players(player):
            player.steal(self, sp, p)
        
class Dom(Card):
    name = 'dom'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for p in self.game.players:
            gp = 5 if p == player else 1 
            for c in p.played:
                if 'animal' in c.tags: 
                    player.gain(self, gp)
        
class Jack(Card):
    name = 'jack'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.cards
        
    def start(self, player):               
        if len(player.played + player.unplayed) < self.game.get_setting('cards') + 5:

            self.cards = self.game.draw_cards('play', len(self.game.players))
            player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            self.cards.remove(c)
            player.add_card(c, 'unplayed')
            
            for p, c in zip(self.sort_players(player), self.cards):
                p.add_card(c, 'unplayed')
            
class Mary(Card):
    name = 'mary'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self.game.check_last(player):
            for p in self.sort_players(player):    
                p.lose(self, 6)
                    
class Daniel(Card):
    name = 'daniel'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        
        for p in self.sort_players(player):
            added, c = self.check_index(p, i, tags=['human'])
            if added:
                player.steal(self, 5, p)

class Emily(Card):
    name = 'emily'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
                  
class GamblingBoi(Card):
    name = 'gambling boi'
    tags = ['human', 'city']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        score = (len(player.played) - len(player.unplayed)) * 2

        if score < 0:
            player.lose(self, -score)
        elif score > 0:
            player.gain(self, score)
            
class Mom(Card):
    name = 'mom'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        if player.has_card('city', deck='landscapes'):
            player.draw_cards('treasure')
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin: 
            self.wait = 'select' 
        else: 
            player.lose(self, 4)
            
    def select(self, player, num):
        if num:
            player.steal(self, 6, player.selected.pop(0))
            
class Dad(Card):
    name = 'dad'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        hs = max({p.score for p in self.game.players}, default=-1)
        return [p for p in self.game.players if p.score == hs]
        
    def start(self, player):
        if player.has_card('curse', deck='active_spells'):
            for p in self.sort_players(player): 
                p.lose(self, 10)    
        else:
            player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            p = player.selected.pop(0)
            lp = 5 if p == player else 10
            p.lose(self, lp)
            
class AuntPeg(Card):
    name = 'aunt peg'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
            
    def start(self, player):
        if self in player.played:
            gp = player.played.index(self) + 1  
        else:
            gp = len(player.played) + 1
        player.gain(self, gp)
        
class UncleJohn(Card):
    name = 'uncle john'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        players = self.sort_players(player, 'steal')
        hs = max({p.score for p in players}, default=-1)
        
        return [p for p in players if p.score == hs]

    def start(self, player):
        if self.game.check_first(player):
            player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            player.steal(self, 7, player.selected.pop(0))
    
class Kristen(Card):
    name = 'kristen'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for _ in player.active_spells: 
            player.draw_cards('treasure')
    
class Joe(Card):
    name = 'joe'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return [p for p in self.sort_players(player, 'steal') if p.items]
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            p = player.selected.pop(0)
            sp = len(p.items) * 3
            player.steal(self, sp, p)
            
class Robber(Card):
    name = 'robber'
    tags = ['human', 'city']
    def __init__(self, game, uid):
        super().__init__(game, uid)
    
    def start(self, player):
        player.draw_cards('items')
        if self.game.is_event('item frenzy'): 
            player.add_request(self, 'flip')
            
    def coin(self, player, coin):
        if coin:
            player.draw_cards('treasure')
       
class Ninja(Card):
    name = 'ninja'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
              
    def start(self, player):
        if any({any({'human' in c.tags for c in p.played}) for p in self.sort_players(player)}):
            lp = 4
            for p in self.sort_players(player):
                p.lose(self, sum([lp for c in p.played if 'human' in c.tags]))
  
class MaxTheDog(Card):
    name = 'max the dog'
    tags = ['animal', 'city', 'dog']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self in player.played:
            lp = player.played.index(self) + 1 
        else:
            lp = len(player.played) + 1
            
        for p in self.sort_players(player):  
            p.lose(self, lp)
 
class BasilTheDog(Card):
    name = 'basil the dog'
    tags = ['animal', 'city', 'dog']
    def __init__(self, game, uid):
        super().__init__(game, uid)
                
    def start(self, player):
        if self.game.check_last(player) or any({'dog' in c.tags and c != self for c in player.played}):
            player.gain(self, 10)
            
class CopyCat(Card):
    name = 'copy cat'
    tags = ['animal', 'city']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, i + 1)
        if added:
            player.play_card(c)
                
class Racoon(Card):
    name = 'racoon'
    tags = ['animal', 'city', 'forest']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Fox(Card):
    name = 'fox'
    tags = ['animal', 'forest', 'city']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        player.add_request(self, 'select')
        
        if self.game.check_first(player):
            
            c = self.copy()
            player.add_request(c, 'flip')
    
    def select(self, player, num):
        if num:

            player.steal(self, 5, player.selected.pop(0))
            
    def coin(self, player, coin):
        if coin:
            
            player.draw_cards('treasure')
            
class Cow(Card):
    name = 'cow'
    tags = ['animal', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Shark(Card):
    name = 'shark'
    tags = ['animal', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        for p in self.sort_players(player):
            for i in range(len(p.played)):
                self.check_index(p, i, tags=['water', 'animal'], inclusive=True)
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
            
    def ongoing(self, player, log):
        for p in self.sort_players(player): 
            for i in range(len(p.played)):
                added, c = self.check_index(p, i, tags=['water', 'animal'], inclusive=True)
                if added:
                    player.steal(self, 5, p)

class Fish(Card):
    name = 'fish'
    tags = ['animal', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for c in player.played:
            if c.name == 'fish':
                player.gain(self, 5)  
        player.gain(self, 5)
                
class Pelican(Card):
    name = 'pelican'
    tags = ['animal', 'sky', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
            
    def start(self, player):     
        gp = 0
        
        for p in self.game.players:
            for c in p.played:  
                if c.name == 'fish':
                    gp += 5
                    
        player.gain(self, gp)
                
class LuckyDuck(Card):
    name = 'lucky duck'
    tags = ['animal', 'sky', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for _ in range(len(player.active_spells)):
            player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:
            player.gain(self, 5)
                
class LadyBug(Card):
    name = 'lady bug'
    tags = ['animal', 'sky', 'garden', 'bug']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Mosquito(Card):
    name = 'mosquito'
    tags = ['animal', 'sky', 'bug']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for p in self.sort_players(player, 'steal'): 
            for c in p.played:
                if 'human' in c.tags:
                    sp = 8 if self.game.is_event('flu') else 4
                    player.steal(self, 4, p)
                        
class Snail(Card):
    name = 'snail'
    tags = ['animal', 'garden', 'water', 'bug']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self.game.check_last(player):
            player.gain(self, 20) 
        else:     
            player.lose(self, 5)
    
class Dragon(Card):
    name = 'dragon'
    tags = ['monster', 'sky']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')

    def start(self, player):
        self.deploy(player, self.sort_players(player, cond=lambda p: p.treasure), 'flip')
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        if self.players:
            player.add_og(self, 'cont')
            
    def coin(self, target, coin):
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

class Clam(Card):
    name = 'clam'
    tags = ['animal', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):  
        if coin:
            t = player.draw_cards('treasure')[0]
            if t.name == 'pearl': 
                player.add_request(self, 'flip')
    
class Cactus(Card):
    name = 'cactus'
    tags = ['plant', 'desert']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        if player.get_played_card(-1) == self:
            player.invincible = True
        else:
            player.invincible = False
    
class PoisonIvy(Card):
    name = 'poison ivy'
    tags = ['plant', 'forest']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for p in self.sort_players(player):
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
    
class Rose(Card):
    name = 'rose'
    tags = ['plant', 'garden']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player)

    def start(self, player):   
        ss = self.game.get_setting('ss')
        
        if player.score < ss:
            player.gain(self, 10)      
        elif player.score > ss:  
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num: 
            player.give(self, 15, player.selected.pop(0))
     
class MrSquash(Card):
    name = 'mr. squash'
    tags = ['plant', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for p in self.sort_players(player): 
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
                
class MrsSquash(Card):
    name = 'mrs. squash'
    tags = ['plant', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        for p in self.sort_players(player): 
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
     
class FishingPole(Card):
    name = 'fishing pole'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return bool([c for p in self.sort_players(player) for c in p.played if c.name == 'fish'])
        
    def get_selection(self, player):
        if len(player.selected) == 0: 
            return player.played.copy()  
        elif len(player.selected) == 1: 
            return [c for p in self.sort_players(player) for c in p.played if c.name == 'fish']

    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num == 1:
            self.wait = 'select'
                
        elif num == 2:
            self.game.swap(player.selected[0], player.selected[1])
            player.use_item(self)
                
class InvisibilityCloak(Card):
    name = 'invisibility cloak'
    tags = ['equipment']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.invincible = True
        player.add_og(self, 'iv')

    def ongoing(self, player, log): 
        player.invincible = False
        player.use_item(self)
           
class LastTurnPass(Card):
    name = 'last turn pass'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return self.game.players[-1] != player
                
    def start(self, player):
        if self.game.players[-1] != player:
        
            self.game.shift_down(player)
            player.use_item(self)
                
class SpeedBoostPotion(Card):
    name = 'speed boost potion'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return self.game.players[0] != player

    def start(self, player):
        if self.game.players[0].pid != player.pid:

            self.game.shift_up(player)
            player.use_item(self)
        
class Mirror(Card):
    name = 'mirror'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return player.active_spells and all({any({c.can_cast(p) for p in self.sort_players(player)}) for c in player.spells})
        
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.active_spells.copy()
        elif len(player.selected) == 1:
            return [p for p in self.sort_players(player) if player.selected[0].can_cast(p)]
            
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
                
class Sword(Card):
    name = 'sword'
    tags = ['equipment']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'sp')

    def ongoing(self, player, log):
        player.steal(self, log['sp'], log['target'])         
        player.use_item(self)
        
class Fertilizer(Card):
    name = 'fertilizer'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
       
class MustardStain(Card):
    name = 'mustard stain'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def end(self, player):
        for c in player.items:
            if c.name == 'detergent':
                player.gain(self, 25)
                player.use_item(c)
                break
            
class Gold(Card):
    name = 'gold'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def end(self, player):
        player.gain(self, 20)
        
class Pearl(Card):
    name = 'pearl'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def end(self, player):
        player.gain(self, 10)
        
class Uphalump(Card):
    name = 'uphalump'
    tags = ['monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        player.lose(self, 5)
            
class Ghost(Card):
    name = 'ghost'
    tags = ['monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
        
    def ongoing(self, player, log):
        i = player.played.index(self)
        added, c = self.check_index(player, max({i - 1, 0}), tags=['human'])
        if added:
            player.play_card(c)
            
class Detergent(Card):
    name = 'detergent'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return False
        
    def start(self, player):
        return
            
class TreasureChest(Card):
    name = 'treasure chest'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('treasure')
        player.use_item(self)
                
class GoldCoins(Card):
    name = 'gold coins'
    tags = ['item', 'treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
        
class SpellTrap(Card):
    name = 'spell trap'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'cast')
        
    def ongoing(self, player, log):
        player.lose(self, len(player.unplayed))
        
class Curse(Card):
    name = 'curse'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_cast(self, player):
        return True
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        player.add_request(self, 'flip')
            
    def coin(self, player, coin):
        if not coin:
            player.lose(self, 3)
    
class TreasureCurse(Card):
    name = 'treasure curse'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'dt')
        
    def ongoing(self, player, log):
        t = log['c']
        self.extra_card = t
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if not coin:
            target = random.choice(self.sort_players(player))
            player.give_card(self.extra_card, target)
                
class Bronze(Card):
    name = 'bronze'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def end(self, player):
        player.gain(self, 5)
        
class ItemHex(Card):
    name = 'item hex'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def get_selection(self, player):
        return player.items.copy()
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        if len(player.get_items()) < 6:
            player.add_request(self, 'flip')
      
    def coin(self, player, coin):
        if coin:
            player.draw_cards('items')    
        else:
            self.wait = 'select'
            
    def select(self, player, num):
        if num:
            player.discard_card(player.selected.pop(0))
                
class Luck(Card):
    name = 'luck'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'cfe')
        
    def ongoing(self, player, log):
        log['coin'] = 1
        player.coin = 1
            
class Boomerang(Card):
    name = 'boomerang'
    tags = ['equipment']
    def __init__(self, game, uid):
        super().__init__(game, uid)

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
            
class BathTub(Card):
    name = 'bath tub'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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

class ItemLeech(Card):
    name = 'item leech'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'ui')
        
    def ongoing(self, player, log):
        i = log['c']
        if i:
            c = player.add_request(self, 'flip')
            c.extra_card = i
        
    def coin(self, player, coin):
        if not coin: 
            target = random.choice(self.sort_players(player))
            if len(target.get_items()) < 6:
                if self.game.restore(self.extra_card):
                    target.add_card(self.extra_card, 'items')
            
class ItemFrenzy(Card):
    name = 'item frenzy'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, game):
        for p in game.players:
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'ui')
            
    def ongoing(self, player, log):
        if len(player.get_items()) < 6:
            player.draw_cards('items')
         
class Flu(Card):
    name = 'flu'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, game):
        for p in game.players:
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')
            
    def ongoing(self, player, log):  
        c = log['c'] 
        if 'human' in c.tags:  
            player.lose(self, 5)
                                      
class NegativeZone(Card):
    name = 'negative zone'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
                
class FishingTrip(Card):
    name = 'fishing trip'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:
            if c.name == 'fish': 
                player.gain(self, 5)
                    
class FutureOrb(Card):
    name = 'future orb'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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

class Knife(Card):
    name = 'knife'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        cards = [c for p in self.game.players for c in p.played if 'human' in c.tags] + [c for c in player.unplayed if 'human' in c.tags]
        return bool(cards)
        
    def get_selection(self, player):
        return [c for p in self.game.players for c in p.played if 'human' in c.tags] + [c for c in player.unplayed if 'human' in c.tags]
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            c = self.game.transform(c, 'ghost')

            player.use_item(self)
            
class MagicWand(Card):
    name = 'magic wand'
    tags = 'item'
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('spells')
        player.use_item(self)
            
class LuckyCoin(Card):
    name = 'lucky coin'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
       
class Sapling(Card):
    name = 'sapling'
    tags = ['plant', 'forest']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        player.add_request(self, 'roll')
            
    def roll(self, player, roll):
        lp = sum([roll for c in player.played if 'plant' in c.tags])
        for p in self.sort_players(player):   
            p.lose(self, lp)
           
class Vines(Card):
    name = 'vines'
    tags = ['plant', 'garden']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self in player.played:   
            i = player.played.index(self)    
        else:  
            i = len(player.played) - 1 
        for c in player.played[i::-1]: 
            self.game.transform(c, 'vines')
            
class Zombie(Card):
    name = 'zombie'
    tags = ['monster', 'human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        for p in self.sort_players(player):
            if any({'human' in c.tags for c in p.played}):   
                player.steal(self, 5, p)
                
        if player.has_card('curse', deck='active_spells'):
            player.draw_cards('treasure')
            player.draw_cards('items')
            
class Jumble(Card):
    name = 'jumble'
    tags = ['monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        if player.has_card('item hex', deck='ongoing'): 
            player.draw_cards('treasure', 2)    
        self.deploy(player, self.sort_players(player), 'flip')
            
    def coin(self, player, coin):
        if not coin: 
            player.lose(self, 10)
            
class DemonWaterGlass(Card):
    name = 'demon water glass'
    tags = ['monster', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)

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

class Succosecc(Card):
    name = 'succosecc'
    tags = ['monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.cards
        
    def start(self, player):
        for p in self.game.players:
            
            items = p.get_items()
            if items: 
                c = random.choice(items)
                p.safe_discard(c) 
            else: 
                c = self.game.draw_cards('items')[0]
                
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
                p.add_card(c, 'items')
                
            self.players.clear()
            self.cards.clear()
                
class Sunflower(Card):
    name = 'sunflower'
    tags = ['plant', 'garden']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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

class LemonLord(Card):
    name = 'lemon lord'
    tags = ['plant', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Wizard(Card):
    name = 'wizard'
    tags = ['human']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.active_spells.copy() 
        elif len(player.selected) == 1: 
            if player.pid == 0 and not player.is_auto():
                print('yeet')
            return [p for p in self.sort_players(player) if player.selected[0].can_cast(p)]

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
                
class HauntedOak(Card):
    name = 'haunted oak'
    tags = ['plant', 'forest', 'monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        plants = len([c for c in player.played if 'plant' in c.tags])
        if (self in player.played and plants >= 3) or (self not in player.played and plants >= 2):
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.steal(self, 10, player.selected.pop(0))
            
class SpellReverse(Card):
    name = 'spell reverse'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, game):
        for p in game.players:
            for c in p.spells.copy():
                p.cast(p, c)
                
class SunnyDay(Card):
    name = 'sunny day'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, game):
        return
            
    def end(self, player):
        for c in player.played:
            if 'plant' in c.tags: 
                player.gain(self, 5)
        
class Garden(Card):
    name = 'garden'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'garden' in c.tags:
            player.play_card(c)
            
class Desert(Card):
    name = 'desert'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'desert' in c.tags:
            player.play_card(c)            
            
class FoolsGold(Card):
    name = 'fools gold'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player)
        
    def start(self, player):
        self.end(player)
        
    def end(self, player):
        if player.score:
            player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.give(self, 5, player.selected.pop(0))
                        
class Graveyard(Card):
    name = 'graveyard'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'monster' in c.tags:
            player.play_card(c)
            
class City(Card):
    name = 'city'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'city' in c.tags:
            player.play_card(c)
                
class Farm(Card):
    name = 'farm'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'farm' in c.tags:
            player.play_card(c)
                
class Forest(Card):
    name = 'forest'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'forest' in c.tags:
            player.play_card(c)
                
class Water(Card):
    name = 'water'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'water' in c.tags:
            player.play_card(c)
                
class Sky(Card):
    name = 'sky'
    tags = ['landscape']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        c = log['c']
        if 'sky' in c.tags:
            player.play_card(c)
            
class OfficeFern(Card):
    name = 'office fern'
    tags = ['plant', 'city']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self in player.played:
            i = player.played.index(self) 
        else: 
            i = len(player.played)

        lp = i + 1
        player.lose(self, lp)
        
class Parade(Card):
    name = 'parade'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Camel(Card):
    name = 'camel'
    tags = ['animal', 'desert']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def check_water(self, p):
        return any({'water' in c.tags for c in p.played})
        
    def count_water(self, p):
        return len([c for c in p.played if 'water' in c.tags])
        
    def get_selection(self, player):
        m = max({self.count_water(p) for p in self.sort_players(player)})    
        return [p for p in self.sort_players(player) if self.count_water(p) == m]
        
    def start(self, player):
        if any({self.check_water(p) for p in self.sort_players(player, 'steal')}):
            r = 'select'
        else:  
            r = 'flip'
        player.add_request(self, r)
                
    def select(self, player, num):
        if num:
            player.steal(self, 5, player.selected.pop(0))
            
    def coin(self, player, coin):
        if coin: 
            player.draw_cards('treasure')
            
class RattleSnake(Card):
    name = 'rattle snake'
    tags = ['animal', 'desert']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        players = self.sort_players(player, lambda p: p.score and p.treasure)
        
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
            
class TumbleWeed(Card):
    name = 'tumble weed'
    tags = ['plant', 'desert']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        if any({'human' in c.tags for c in player.played}):
            player.lose(self, 10)
        else:
            player.gain(self, 5)
            
class WindGust(Card):
    name = 'wind gust'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, game):
        for p in game.players: 
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        self.game.restock_shop()
            
class Sunglasses(Card):
    name = 'sunglasses'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class MetalDetector(Card):
    name = 'metal detector'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return self.game.get_discarded_items()
            
    def start(self, player):
        items = self.game.get_discarded_items()[::-1]
        
        while items:
            
            i = items.pop(0)
            
            if not self.game.check_exists(i.uid):

                self.game.restore(i)
                player.add_card(i, 'items')
                player.use_item(self)
                
                break
            
class SandStorm(Card):
    name = 'sand storm'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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

class Mummy(Card):
    name = 'mummy'
    tags = ['human', 'desert', 'monster']
    def __init__(self, game, uid):
        super().__init__(game, uid)
            
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
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
            
class MummysCurse(Card):
    name = 'mummys curse'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return True
        
    def get_selection(self, player):
        return [c for c in player.played if 'human' in c.tags]
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')
        
    def ongoing(self, player, log):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:
            self.wait = 'select' 
        else: 
            player.lose(self, 5)
            
    def select(self, player, num):
        if num: 
            player.play_card(player.selected.pop(0))
            
class Pig(Card):   
    name = 'pig'
    tags = ['animal', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class Corn(Card):
    name = 'corn'
    tags = ['plant', 'farm']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def get_selection(self, player):
        if len(player.selected) == 0:
            return player.get_items()
        elif len(player.selected) == 1: 
            return self.sort_players(player)
        
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
            
class Harvest(Card):
    name = 'harvest'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)
            
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:   
            if 'plant' in c.tags:  
                gp = 10 if any({l.name in c.tags for l in player.landscapes}) else 5
                player.gain(self, gp)
            
class GoldenEgg(Card):
    name = 'golden egg'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def end(self, player):
        player.gain(self, sum([5 for c in player.played if 'animal' in c.tags]))
        
class Bear(Card):
    name = 'bear'
    tags = ['animal', 'forest']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        sp = 4 if self.game.is_event('parade') else 2
        for p in self.sort_players(player, 'steal'):   
            player.steal(self, sum(sp for c in p.played if 'human' in c.tags), p)
            
class BigRock(Card):
    name = 'big rock'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
                player.add_card(c2, 'played', i=i)

                player.use_item(self)
            
class UnluckyCoin(Card):
    name = 'unlucky coin'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
            
class HuntingSeason(Card):
    name = 'hunting season'
    tags = ['event']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, game):
        for p in game.players: 
            self.start_ongoing(p)
            
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        c = log['c']
        if 'animal' in c.tags:
            player.add_request(self, 'flip')
            
    def coin(self, player, coin):
        if not coin: 
            player.lose(self, 3)
            
class Stardust(Card):
    name = 'stardust'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})

    def start_ongoing(self, player):
        if not self.extra_player:
            self.deploy(player, self.sort_players(player), 'og')
        else:
            player.add_og(self, 'dt')
        
    def ongoing(self, player, log):
        p = self.extra_player
        c = self.extra_card
        if p.requests.count(c) < 5 and len(p.treasure) < 6:
            p.add_request(c, 'flip')
                
    def coin(self, player, coin):
        if coin:
            player.draw_cards('treasure')
        else: 
            player.lose(self, 5)
            
class WaterLily(Card):
    name = 'water lily'
    tags = ['plant', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        gp = len(player.get_items() + player.spells) + (len(player.active_spells) * 5)
        player.gain(self, gp)
        
class Torpedo(Card):
    name = 'torpedo'
    tags = ['equipment']
    def __init__(self, game, uid):
        super().__init__(game, uid)

    def start(self, player):
        self.start_ongoing(player)
        
    def start_ongoing(self, player):
        player.add_og(self, 'sp')
        
    def coin(self, player, coin):
        if coin:
            p = self.extra_player
            sp = self.mode
            player.steal(self, sp, p)
        player.use_item(self)

    def ongoing(self, player, log):
        self.extra_player = log['target']
        self.mode = log['sp']
        player.add_request(self, 'flip')
        
class Bat(Card):
    name = 'bat'
    tags = ['animal', 'sky']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
        self.option1 = Blank(self.game, self.game.get_new_uid(), 'draw item')
        self.option2 = Blank(self.game, self.game.get_new_uid(), 'draw spell')
        
    def get_selection(self, player):
        if self.mode == 0:
            return self.sort_players(player, lambda p: p.treasure) 
        elif self.mode == 1: 
            return [self.option1, self.option2]
        
    def start(self, player):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
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
                
                if o is self.option1:  
                    player.draw_cards('items')   
                elif o is self.option2:
                    player.draw_cards('spells')
        
class SkyFlower(Card):
    name = 'sky flower'
    tags = ['plant', 'sky']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player)
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            player.give(self, 5, player.selected.pop(0))
            player.draw_cards('treasure')
        
class Kite(Card):
    name = 'kite'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return bool(player.unplayed)
        
    def start(self, player):
        player.draw_cards('unplayed')
        player.use_item(self)
        
class Balloon(Card):
    name = 'balloon'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return len(player.played) > 1
        
    def start(self, player):
        player.new_deck('played', player.played[::-1])  
        player.use_item(self)
        
class NorthWind(Card):
    name = 'north wind'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_cast(self, player):
        return not any({c.name == self.name for c in player.active_spells})
        
    def start_ongoing(self, player):
        player.add_og(self, 'play')

    def ongoing(self, player, log):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:  
            player.gain(self, 3 * len(player.active_spells))
        
class GardenSnake(Card):
    name = 'garden snake'
    tags = ['animal', 'garden', 'snake']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        if self.game.check_first(player):
            player.add_request(self, 'select')  
        else:    
            player.lose(self, 4)
            
    def select(self, player, num):
        if num: 
            p = player.selected.pop(0)
            player.steal(self, 4, p)

class WateringCan(Card):
    name = 'watering can'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return not player.has_card('water', deck='landscapes')
        
    def start(self, player):
        for c in player.landscapes.copy(): 
            self.game.transform(c, 'water')    
        player.use_item(self)
        
class MagicBean(Card):
    name = 'magic bean'
    tags = ['treasure']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def end(self, player):
        player.gain(self, sum([5 for c in player.played if 'plant' in c.tags]))
        
class Trap(Card):
    name = 'trap'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
        
class FlowerPot(Card):
    name = 'flower pot'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def can_use(self, player):
        return not player.has_card('garden', deck='landscapes')
        
    def start(self, player):
        for c in player.landscapes.copy():
            self.game.transform(c, 'garden')    
        player.use_item(self)       
        
class TheVoid(Card):
    name = 'the void'
    tags = ['spell']
    def __init__(self, game, uid):
        super().__init__(game, uid)

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
        
class BugNet(Card):
    name = 'bug net'
    tags = ['item']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
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
        
class BigSandWorm(Card):
    name = 'big sand worm'
    tags = ['animal', 'desert']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        if self.game.check_last(player):
            player.gain(self, 5)  
        else: 
            player.lose(self, 5)
            
class LostPalmTree(Card):
    name = 'lost palm tree'
    tags = ['plant', 'desert', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        t = False
        
        for c in player.landscapes.copy():
            if c.name == 'desert':
                self.game.transform(c, 'water')
                t = True
                
        if t:
            player.draw_cards('treasure')
                    
class Seaweed(Card):
    name = 'seaweed'
    tags = ['plant', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin: 
            player.gain(self, 3)
            player.draw_cards('treasure') 
        else:
            player.lose(self, 4)
        
class ScubaBaby(Card):
    name = 'scuba baby'
    tags = ['human', 'water']
    def __init__(self, game, uid):
        super().__init__(game, uid)
        
    def start(self, player):
        player.gain(self, 3)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        