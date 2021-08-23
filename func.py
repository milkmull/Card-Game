import random
import time

class Card:
    def __init__(self, game, uid, name, tags=[]):
        self.game = game
        self.uid = uid
        
        self.name = name
        self.tags = tags
        
        self.mode = 0

        self.t_coin = -1
        self.t_roll = -1

        self.cards = []
        self.pids = []
        
        self.extra_card = None
        self.extra_player = None
        
        self.mult = True
        
        self.wait = None

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return self.uid == other.get_id() and self.name == other.get_name()
        
    def copy(self): 
        return type(self)(self.game, self.uid)
        
    def light_sim_copy(self, game):
        return type(self)(game, self.uid)
        
    def sim_copy(self, game):
        c = type(self)(game, self.uid)

        c.mode = self.mode

        c.wait = self.wait
        c.t_coin = self.t_coin
        c.t_roll = self.t_roll
        
        c.pids = self.pids.copy()
        c.cards = [o.sim_copy(game) for o in self.cards if o is not self]
        
        if self.extra_card:
        
            c.extra_card = self.extra_card.sim_copy(game)
            
        if self.extra_player:
            
            c.extra_player = game.get_player(self.extra_player.pid)
    
        return c
         
    def can_use(self, player):
        return True
        
    def sort_players(self, player, cond=None):
        if cond is None:
        
            return [p for p in self.game.players if p.pid != player.pid]
            
        elif cond == 'steal':
            
            return [p for p in self.game.players if p.pid != player.pid and p.score]
            
        else:
            
            return [p for p in self.game.players if p.pid != player.pid and cond(p)]
   
    def get_players(self):
        return self.game.players
   
    def get_opponents(self, player):
        return [p for p in self.game.players if p != player]

    def get_id(self):
        return self.uid
        
    def get_name(self):
        return self.name
        
    def find_owner(self, c):
        info = self.game.find_card_deep(c)
        
        if info:
            
            if info[1] == 'played':

                return info[0]
   
    def get_cards_from_logs(self, player, type, key=lambda c: True, add=True):
        cards = []
        logs = player.get_all_logs(type)
        
        for log in logs:
            
            c = log.get('c')
            
            if c is None:
                continue
                
            if key(c) and add:
                if c not in self.cards:
                    self.cards.append(c)
                    cards.append(c)
                    
        return cards

class Blank(Card):
    def __init__(self, game, name):
        super().__init__(game, game.get_new_uid(), name, [])

class Michael(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'michael', ['human'])

    def start(self, player):
        sp = 5 if self.game.current_player == 0 else 2

        for p in self.sort_players(player):

            player.steal(self, sp, p)
        
class Dom(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'dom', ['human'])
        
    def start(self, player):
        for p in self.game.players:
            
            gp = 5 if p == player else 1
            
            for c in p.played:
                
                if 'animal' in c.tags:
                    
                    player.gain(self, gp)
        
class Jack(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'jack', ['human'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mary', ['human'])
        
    def start(self, player):
        if self.game.check_last(player):
        
            for p in self.sort_players(player):
                    
                p.lose(self, 6)
                    
class Daniel(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__(game, uid, 'daniel', ['human'])
        
    def start(self, player):
        self.pids.clear()
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True

        i = player.played.index(self)
        
        for p in self.sort_players(player):
        
            c = p.get_played_card(i)
            
            if c is None:
                continue
            
            if 'human' in c.tags:

                if c not in self.cards:
                    self.cards.append(c)
                    player.steal(self, 5, p)

class Emily(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'emily', ['human'])
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True

        i = player.played.index(self)
        
        for j in range(i + 1, i + 3):
        
            c = player.get_played_card(j)
            
            if c is None:
                break
            
            if 'human' in c.tags:

                if c not in self.cards:
                    self.cards.append(c)
                    player.gain(self, 5 * (j - i))
                    
            else:
                break
                  
class GamblingBoi(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'gambling boi', ['human', 'city'])
        
    def start(self, player):
        score = (len(player.played) - len(player.unplayed)) * 2

        if score < 0:
        
            player.lose(self, -score)
        
        elif score > 0:
        
            player.gain(self, score)
            
class Mom(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mom', ['human'])
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        if player.has_card('landscapes', 'city'):
            
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'dad', ['human'])
        
    def get_selection(self, player):
        hs = max((p.score for p in self.game.players), default=-1)
        
        return [p for p in self.game.players if p.score == hs]
        
    def start(self, player):
        if player.has_card('ongoing', 'curse'):
            
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'aunt peg', ['human'])
            
    def start(self, player):
        if self in player.played:
            
            gp = player.played.index(self) + 1
            
        else:
            
            gp = len(player.played) + 1

        player.gain(self, gp)
        
class UncleJohn(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'uncle john', ['human'])
        
    def get_selection(self, player):
        players = self.sort_players(player, 'steal')
        hs = max((p.score for p in players), default=-1)
        
        return [p for p in players if p.score == hs]

    def start(self, player):
        if self.game.check_first(player):
            
            player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            
            player.steal(self, 7, player.selected.pop(0))
    
class Kristen(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'kristen', ['human'])
        
    def start(self, player):
        for _ in player.get_spells():
            
            player.draw_cards('treasure')
    
class Joe(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'joe', ['human'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'robber', ['human', 'city'])
    
    def start(self, player):
        player.draw_cards('items')
        
        if self.game.get_event() == 'item frenzy':
            
            player.add_request(self, 'flip')
            
    def coin(self, player, coin):
        if coin:
            
            player.draw_cards('treasure')
       
class Ninja(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'ninja', ['human'])
              
    def start(self, player):
        if any(any('human' in c.tags for c in p.played) for p in self.sort_players(player)):

            lp = 4

            for p in self.sort_players(player):

                p.lose(self, sum(lp for c in p.played if 'human' in c.tags))
  
class MaxTheDog(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'max the dog', ['animal', 'city', 'dog'])
        
    def start(self, player):
        if self in player.played:
            
            lp = player.played.index(self) + 1
            
        else:
            
            lp = len(player.played) + 1
            
        for p in self.sort_players(player):
            
            p.lose(self, lp)
 
class BasilTheDog(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'basil the dog', ['animal', 'city', 'dog'])
                
    def start(self, player):
        if self.game.check_last(player) or any('dog' in c.tags and c != self for c in player.played):
            
            player.gain(self, 10)
            
class CopyCat(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'copy cat', ['animal', 'city'])
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        else:

            i = player.played.index(self)
            c = player.get_played_card(i + 1)
            
            if c is not None:

                if c not in self.cards:
                    self.cards.append(c)
                    player.play_card(c, d=True)
                
class Racoon(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'racoon', ['animal', 'city', 'forest'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fox', ['animal', 'forest', 'city'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'cow', ['animal', 'farm'])
        
    def start(self, player):
        player.ongoing.append(self)

    def ongoing(self, player):
        if self not in player.played:
            return True
        
        i = player.played.index(self)
        
        for i in range(i + 1, len(player.played)):
            
            c = player.get_played_card(i)
            
            if c is None:
                break
                
            if 'plant' in c.tags:
            
                if c not in self.cards:

                    self.cards.append(c)
                    
                    player.gain(self, 4)
                    if 'farm' in c.tags:
                        player.draw_cards('treasure')
            
class Shark(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'shark', ['animal', 'water'])
        
    def check(self, c):
        return 'water' in c.tags and 'animal' in c.tags
        
    def start(self, player):
        for p in self.sort_players(player):
            self.get_cards_from_logs(p, 'play', key=self.check)
        player.ongoing.append(self)
            
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        for p in self.sort_players(player):
            
            cards = self.get_cards_from_logs(p, 'play', key=self.check)
            
            for _ in cards:
                player.steal(self, 5, p)

class Fish(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fish', ['animal', 'water'])
        
    def start(self, player):
        for c in player.played:
            
            if c.name == 'fish':
                
                player.gain(self, 5)
                
class Pelican(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'pelican', ['animal', 'sky', 'water'])
            
    def start(self, player):     
        gp = 0
        
        for p in self.game.players:
        
            for c in p.played:
                
                if c.name == 'fish':
                    
                    gp += 5
                    
        player.gain(self, gp)
                
class LuckyDuck(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'lucky duck', ['animal', 'sky', 'water'])
        
    def start(self, player):
        for _ in range(len(player.get_spells())):
            
            c = self.copy()
            player.add_request(c, 'flip')
        
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 5)
                
class LadyBug(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'lady bug', ['animal', 'sky', 'garden', 'bug'])
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        c = player.get_played_card(i + 1)
        
        if c is not None:
            if c not in self.cards:
                self.cards.append(c)
                
                if 'animal' in c.tags:
                    player.gain(self, 10)
                else:
                    player.lose(self, 5)
            
class Mosquito(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mosquito', ['animal', 'sky', 'bug'])
        
    def start(self, player):
        for p in self.sort_players(player, 'steal'):
            
            for c in p.played:
            
                if 'human' in c.tags:
                    
                    sp = 8 if self.game.get_event() == 'flu' else 4
        
                    player.steal(self, 4, p)
                        
class Snail(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'snail', ['animal', 'garden', 'water', 'bug'])
        
    def start(self, player):
        if self.game.check_last(player):
            
            player.gain(self, 20)
            
        else:
            
            player.lose(self, 5)
    
class Dragon(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'dragon', ['monster', 'sky'])
        
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
            
    def deploy(self, player):
        self.pids.clear()
        self.cards.clear()
        
        for p in [p for p in self.sort_players(player) if p.treasure]:
                
            c = self.copy()
            p.add_request(c, 'flip')
            
            self.pids.append(p.pid)
            self.cards.append(c)

    def start(self, player):
        self.deploy(player) 
        player.ongoing.append(self)
            
    def coin(self, target, coin):
        self.t_coin = coin
        
    def ongoing(self, player):
        if self.pids:
            
            i = 0
        
            while i in range(len(self.pids)):

                c = self.cards[i]
                pid = self.pids[i]
                p = self.game.get_player(pid)
                
                if c.t_coin != -1:
                    
                    if not c.t_coin:
                        
                        player.steal_random_card('treasure', p)
                        
                    self.pids.pop(i)
                    self.cards.pop(i)
                    
                else:
                    
                    i += 1
            
        else:
            
            return True

class Clam(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'clam', ['animal', 'water'])

    def start(self, player):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):  
        if coin:

            t = player.draw_cards('treasure')[0]

            if t.name == 'pearl':
                
                c = self.copy()
                player.add_request(c, 'flip')
    
class Cactus(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'cactus', ['plant', 'desert'])

    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self in player.played:
        
            i = player.played.index(self) + 1
            
            try:
                
                c = player.played[i]
                player.invincible = False
                    
            except IndexError:
                
                player.invincible = True
    
class PoisonIvy(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'poison ivy', ['plant', 'forest'])
        
    def start(self, player):
        for p in self.sort_players(player):
            
            for c in p.played:
                
                if 'human' in c.tags:
                    
                    p.lose(self, 5)
                    
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        
        for i in range(i + 1, len(player.played)):
            
            c = player.get_played_card(i)
            
            if c is None:
                break
                
            if 'human' in c.tags:
                if c not in self.cards:
                    self.cards.append(c)
                    player.lose(self, 5)
    
class Rose(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'rose', ['plant', 'garden'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mr. squash', ['plant', 'farm'])
        
    def start(self, player):
        for p in self.sort_players(player):
            
            for c in p.played:
                
                if 'plant' in c.tags:
                    
                    player.steal(self, 5, p)
            
        player.ongoing.append(self)
            
    def ongoing(self, player):
        for p in self.game.players:
            
            if any(c.name == 'mrs. squash' for c in p.played):
                
                player.gain(self, 20)
                
                return True
                
class MrsSquash(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mrs. squash', ['plant', 'farm'])

    def start(self, player):
        for p in self.sort_players(player):
            
            for c in p.played:
                
                if 'plant' in c.tags:
                    
                    player.steal(self, 5, p)
            
        player.ongoing.append(self)
            
    def ongoing(self, player):
        for p in self.game.players:
            
            if any(c.name == 'mr. squash' for c in p.played):
                
                player.gain(self, 20)
                
                return True
     
class FishingPole(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fishing pole', ['item'])
        
    def can_use(self, player):
        if not player.auto:
            print([c.copy() for p in self.sort_players(player) for c in p.played if c.name == 'fish'])
        return bool([c.copy() for p in self.sort_players(player) for c in p.played if c.name == 'fish'])
        
    def get_selection(self, player):
        if len(player.selected) == 0:
            
            return [c.copy() for c in player.played]
            
        elif len(player.selected) == 1:
            
            return [c.copy() for p in self.sort_players(player) for c in p.played if c.name == 'fish']

    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num == 1:

            self.wait = 'select'
                
        elif num == 2:

            self.game.swap(player.selected[0], player.selected[1])
            player.discard_card(self)
                
class InvisibilityCloak(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'invisibility cloak', ['equipment'])

    def start(self, player):
        self.get_cards_from_logs(player, 'iv')
        player.equip(self)

    def ongoing(self, player):
        if self.get_cards_from_logs(player, 'iv'):
            
            player.invincible = False
            player.discard_card(self)
            
            return True
            
        else:
            
            player.invincible = True
           
class LastTurnPass(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'last turn pass', ['item'])
        
    def can_use(self, player):
        return self.game.players[-1] != player
                
    def start(self, player):
        if self.game.players[-1] != player:
        
            self.game.shift_down(player)
            player.discard_card(self)
                
class SpeedBoostPotion(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'speed boost potion', ['item'])
        
    def can_use(self, player):
        return self.game.players[0] != player

    def start(self, player):
        if self.game.players[0].pid != player.pid:

            self.game.shift_up(player)
            player.discard_card(self)
        
class Mirror(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mirror', ['item'])
        
    def can_use(self, player):
        return player.get_spells() and any(any(p.can_cast(c) for c in player.get_spells()) for p in self.sort_players(player))
        
    def get_selection(self, player):
        if len(player.selected) == 0:

            return [c.copy() for c in player.get_spells()]
            
        elif len(player.selected) == 1:

            return [p for p in self.sort_players(player) if p.can_cast(player.selected[0])]
            
    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num == 1:

            self.wait = 'select'

        elif num == 2:

            c, p = player.selected
            player.cast(p, c)

            player.discard_card(self)
                
class Sword(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sword', ['equipment'])

    def start(self, player):
        player.equip(self)

    def ongoing(self, player):
        logs = player.get_logs('sp')
        
        if logs:
        
            for log in logs:
                
                c = log.get('c')
                
                if c:

                    log['sp'] += player.steal(self, log['sp'], log['target'], d=True)
                    
            player.discard_card(self)
            
            return True
        
class Fertilizer(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fertilizer', ['item'])
        
    def can_use(self, player):
        return any('plant' in c.tags for c in player.played)
        
    def get_selection(self, player):
        return [c.copy() for c in player.played if 'plant' in c.tags]
        
    def start(self, player):
        if any('plant' in c.tags for c in player.played):
            
            player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            player.play_card(player.selected.pop(0), d=True)
            player.discard_card(self)
       
class MustardStain(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mustard stain', ['treasure'])
        
    def end(self, player):
        if player.has_card('items', 'detergent'):
            
            player.gain(self, 25)
            player.discard_card(next(c for c in player.items if c.name == 'detergent'))
            
class Gold(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'gold', ['treasure'])

    def end(self, player):
        player.gain(self, 20)
        
class Pearl(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'pearl', ['treasure'])
        
    def end(self, player):
        player.gain(self, 10)
        
class Uphalump(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'uphalump', ['monster'])

    def start(self, player):
        player.lose(self, 5)
            
class Ghost(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'ghost', ['monster'])
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        c = player.get_played_card(i - 1)
        
        if c is None:
            return
            
        if 'human' in c.tags:
            if c not in self.cards:
                self.cards.append(c)
                player.play_card(c, d=True)
            
class Detergent(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'detergent', ['item'])
        
    def can_use(self, player):
        return False
        
    def start(self, player):
        return
            
class TreasureChest(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'treasure chest', ['item'])
        
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('treasure')
        player.discard_card(self)
                
class GoldCoins(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'gold coins', ['item', 'treasure'])
        
    def can_use(self, player):
        return player.is_turn and not player.game_over
        
    def get_selection(self, player):
        return [c.copy() for c in self.game.shop]
        
    def start(self, player):   
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            if player.buy_card(c.uid):
                
                if self in player.treasure:
                
                    player.treasure.remove(self)
        
class SpellTrap(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'spell trap', ['spell'])

        self.mult = False
        
    def start(self, player):
        self.get_cards_from_logs(player, 'cast')
        
    def ongoing(self, player):
        for _ in self.get_cards_from_logs(player, 'cast'):

            player.lose(self, len(player.unplayed))
        
class Curse(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'curse', ['spell'])

    def ongoing(self, player):
        if player.check_log('play'):
        
            player.add_request(self, 'flip')
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 3)
    
class TreasureCurse(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'treasure curse', ['spell'])

        self.mult = False
        
    def start(self, player):
        self.get_cards_from_logs(player, 'dt')
        
    def ongoing(self, player):
        for t in self.get_cards_from_logs(player, 'dt'):

            c = self.copy()
            c.extra_card = t
            player.add_request(c, 'flip')
        
    def coin(self, player, coin):
        if not coin:
            
            target = random.choice(self.sort_players(player))
            player.give_card(self.extra_card, target)
                
class Bronze(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'bronze', ['treasure'])
        
    def end(self, player):
        player.gain(self, 5)
        
class ItemHex(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'item hex', ['spell'])
        
        self.mult = False
        
    def get_selection(self, player):
        return [c.copy() for c in player.items]
        
    def ongoing(self, player):
        if player.check_log('play') and len(player.get_items()) < 6:

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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'luck', ['spell'])

        self.mult = False
        
    def ongoing(self, player):
        if player.flipping:
        
            player.coin = 1
            
class Boomerang(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'boomerang', ['equipment'])

    def start(self, player):
        if not any(c.name == self.name for c in player.equipped):
        
            player.equip(self)
        
    def ongoing(self, player):
        if self.game.get_event() != 'negative zone':
            
            attr = 'gain'
            key1 = 'lp'
            key2 = 'gp'
            
        else:
            
            attr = 'lose'
            key1 = 'gp'
            key2 = 'lp'
            
        logs = player.get_logs(key1)
        
        if logs:
            
            for log in logs:
                
                log[key2] = getattr(player, attr)(self, log[key1] * 2, d=True) // 2
                log['t'] = key2
                
            player.discard_card(self)
            
            return True
            
class BathTub(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'bath tub', ['item'])
        
    def can_use(self, player):
        return any(p.get_spells() for p in self.game.players)
        
    def get_selection(self, player):
        return [c.copy() for p in self.game.players for c in p.get_spells()]
        
    def start(self, player):
        player.add_request(self, 'select')

    def select(self, player, num):
        if num:
        
            c = player.selected.pop(0)
            
            for p in self.game.players:
                
                if c in p.get_spells():
                    
                    p.remove_og(c)
                    player.discard_card(self)
                    
                    break

class ItemLeech(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'item leech', ['spell'])

        self.mult = False
        
    def ongoing(self, player):
        for log in player.get_logs('ui'):
            
            i = log.get('c')
            
            if i:
                
                c = self.copy()
                c.extra_card = i.copy()
                player.add_request(c, 'flip')
        
    def coin(self, player, coin):
        if not coin:
            
            target = random.choice(self.sort_players(player))
            
            if len(target.get_items()) < 6:
            
                target.add_card(self.extra_card, 'items')
            
class ItemFrenzy(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'item frenzy', ['event'])

    def start(self, game):
        for p in game.players:
            
            p.ongoing.append(self)
            
    def ongoing(self, player):
        if len(player.get_items()) < 6:
        
            for log in player.get_logs('ui'):

                player.draw_cards('items')
         
class Flu(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'flu', ['event'])
        
    def start(self, game):
        for p in game.players:
            
            p.ongoing.append(self)
            
    def ongoing(self, player):
        for log in player.get_logs('play'):
            
            c = log.get('c')
            
            if c:
            
                if 'human' in c.tags:
                    
                    player.lose(self, 5)
                                      
class NegativeZone(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'negative zone', ['event'])
        
    def start(self, game):
        for p in self.game.players:
            
            p.ongoing.append(self)
            
    def ongoing(self, player):
        for log in [log for log in player.log.copy() if log.get('d') is False]:
            
            if log['t'] == 'gp':          
                log['lp'] = player.lose(self, log['gp'] * 2, d=True) // 2
                log['t'] = 'lp'    
            elif log['t'] == 'lp':   
                log['gp'] = player.gain(self, log['lp'] * 2, d=True) // 2
                log['t'] = 'gp' 
            elif log['t'] == 'sp':   
                log['lp'] = player.lose(self, log['sp'] * 2, d=True) // 2
                log['t'] = 'lp'  
            elif log['t'] == 'rp':   
                log['gp'] = player.gain(self, log['rp'] * 2, d=True) // 2
                log['t'] = 'gp' 
            elif log['t'] == 'give':
                log['sp'] = player.steal(self, -log['gp'] * 2, log['target'], d=True) // 2
                log['t'] = 'sp'
                
class FishingTrip(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fishing trip', ['event'])
        
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:
            
            if c.name == 'fish':
                
                player.gain(self, 5)
                    
class FutureOrb(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'future orb', ['item'])
        
    def get_target(self, player):
        i = self.game.players.index(player) - 1
        p = self.game.players[i]
        
        return p
        
    def can_use(self, player):  
        return (player.is_turn and not player.gone) and self.get_target(player).unplayed
        
    def get_selection(self, player):
        return [c.copy() for c in self.get_target(player).unplayed]
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            p = self.get_target(player)
            
            if c in p.unplayed:
            
                p.discard_card(c, d=True)
                
                player.add_card(c, 'unplayed')
                player.play_card(c)
                
                player.discard_card(self)

class Knife(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'knife', ['item'])
        
    def can_use(self, player):
        cards = [c for p in self.game.players for c in p.played if 'human' in c.tags] + [c for c in player.unplayed if 'human' in c.tags]
        return bool(cards)
        
    def get_selection(self, player):
        return [c.copy() for p in self.game.players for c in p.played if 'human' in c.tags] + [c.copy() for c in player.unplayed if 'human' in c.tags]
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            c = self.game.transform(c, Ghost)
            
            p = self.find_owner(c)
            
            if p:
            
                p.play_card(c, d=True)
            
            player.discard_card(self)
            
class MagicWand(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'magic wand', ['item'])
        
    def can_use(self, player):
        return True
        
    def start(self, player):
        player.draw_cards('spells')
        player.discard_card(self)
            
class LuckyCoin(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'lucky coin', ['item'])
        
    def can_use(self, player):
        return True
        
    def get_selection(self, player):
        return self.game.players.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            c = self.copy()
            p.ongoing.append(c)
            
            player.discard_card(self)

    def ongoing(self, player):
        if player.flipping:
        
            player.coin = 1
            self.mode = 1
            
        if self.mode == 1 and player.get_logs('cfe'):
        
            return True
       
class Sapling(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sapling', ['plant', 'forest'])
        
    def start(self, player):
        player.add_request(self, 'roll')
            
    def roll(self, player, roll):
        lp = sum(roll for c in player.played if 'plant' in c.tags)
        
        for p in self.sort_players(player):
            
            p.lose(self, lp)
           
class Vines(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'vines', ['plant', 'garden'])
        
    def start(self, player):
        if self in player.played:
            
            i = player.played.index(self)
            
        else:
            
            i = len(player.played) - 1
            
        for c in player.played[i::-1]:
            
            self.game.transform(c.copy(), Vines)
            
class Zombie(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'zombie', ['monster', 'human'])
        
    def start(self, player):
        for p in self.sort_players(player):
            
            if any('human' in c.tags for c in p.played):
                
                player.steal(self, 5, p)
                
        if player.has_card('ongoing', 'curse'):
            
            player.draw_cards('treasure')
            player.draw_cards('items')
            
class Jumble(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'jumble', ['monster'])
        
    def deploy(self, players):
        for p in players:
            
            c = self.copy()
            p.add_request(c, 'flip')
        
    def start(self, player):
        if player.has_card('ongoing', 'item hex'):
            
            player.draw_cards('treasure', 2)
            
        self.deploy(self.sort_players(player))
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 10)
            
class DemonWaterGlass(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'demon water glass', ['monster', 'water'])

    def start(self, player):
        player.gain(self, 5)
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        c = player.get_played_card(i + 1)
        
        if c is None:
            return
            
        if 'human' in c.tags:
            if c not in self.cards:
                self.cards.append(c)
                player.lose(self, 10)

class Succosecc(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'succosecc', ['monster'])
        
    def get_selection(self, player):
        return self.cards
        
    def start(self, player):
        for p in self.game.players:
            
            if p.get_items():
                
                c = random.choice(p.get_items())
                p.discard_card(c, d=True)
                
            else:
                
                c = self.game.draw_cards('items')[0]
                
            self.pids.append(p.pid)
            self.cards.append(c)
                
        player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            self.cards.remove(c)
            self.pids.remove(player.pid)
            
            random.shuffle(self.cards)
            
            for pid, c in zip(self.pids, self.cards):
                
                p = self.game.get_player(pid)
                p.add_card(c, 'items')
                
            self.pids.clear()
            self.cards.clear()
                
class Sunflower(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sunflower', ['plant', 'garden'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'lemon lord', ['plant', 'farm'])
        
    def start(self, player): 
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        
        for i in range(i + 1, len(player.played)):
            
            c = player.get_played_card(i)
            
            if c is None:
                break
                
            if 'plant' in c.tags:
                if c not in self.cards:
                    self.cards.append(c)
                    player.gain(self, 5)
            else:
                break
            
class Wizard(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'wizard', ['human'])
        
    def get_selection(self, player):
        if len(player.selected) == 0:
        
            return [c.copy() for c in player.get_spells()]
            
        elif len(player.selected) == 1:
            
            return [p for p in self.sort_players(player) if p.can_cast(player.selected[0])]

    def start(self, player):
        self.mode = 0
        player.add_request(self, 'select')
            
    def select(self, player, num):      
        if num == 1:

            self.wait = 'select'
            
        elif num == 2:
            
            c, p = player.selected
            player.cast(p, c)
            
            if any(c.name == 'wizard' for c in p.played):
                
                player.gain(self, 10)
                
class HauntedOak(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'haunted oak', ['plant', 'forest', 'monster'])

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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'spell reverse', ['event'])
        
    def start(self, game):
        for p in game.players:
            
            for c in p.spells.copy():
                
                p.cast(p, c)
                
class SunnyDay(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sunny day', ['event'])
        
    def start(self, game):
        return
            
    def end(self, player):
        for c in player.played:
            
            if 'plant' in c.tags:
                
                player.gain(self, 5)
        
class Garden(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'garden', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:

            for log in logs:
                
                c = log['c']

                if 'garden' in c.tags:
                
                    player.play_card(c, d=True)
            
class Desert(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'desert', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'desert' in c.tags:
                
                    player.play_card(c, d=True)             
            
class FoolsGold(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'fools gold', ['treasure'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'graveyard', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'monster' in c.tags:
                
                    player.play_card(c, d=True)
            
class City(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'city', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'city' in c.tags:
                
                    player.play_card(c, d=True)
                
class Farm(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'farm', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'farm' in c.tags:
                
                    player.play_card(c, d=True)
                
class Forest(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'forest', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'forest' in c.tags:

                    player.play_card(c, d=True)
                
class Water(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'water', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'water' in c.tags:
                
                    player.play_card(c, d=True)
                
class Sky(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sky', ['landscape'])
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['c']

                if 'sky' in c.tags:
                
                    player.play_card(c, d=True)
            
class OfficeFern(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'office fern', ['plant', 'city'])
        
    def start(self, player):
        if self in player.played:
            
            i = player.played.index(self)
            
        else:
            
            i = len(player.played)

        lp = i + 1
        player.lose(self, lp)
        
class Parade(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'parade', ['event'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'camel', ['animal', 'desert'])
        
    def check_water(self, p):
        return any('water' in c.tags for c in p.played)
        
    def count_water(self, p):
        return len([c for c in p.played if 'water' in c.tags])
        
    def get_selection(self, player):
        m = max(self.count_water(p) for p in self.sort_players(player))
            
        return [p for p in self.sort_players(player) if self.count_water(p) == m]
        
    def start(self, player):
        if any(self.check_water(p) for p in self.sort_players(player, 'steal')):
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'rattle snake', ['animal', 'desert'])
        
    def deploy(self, players):
        self.pids.clear()
        self.cards.clear()
        
        for p in players:
            
            c = self.copy()
            p.add_request(c, 'roll')
            
            self.pids.append(p.pid)
            self.cards.append(c)
        
    def start(self, player):
        players = self.sort_players(player, lambda p: p.score and p.treasure)
        
        if len(players) > 1:

            self.deploy(players)
            player.ongoing.append(self)
            
        elif players:

            player.steal_random_card('treasure', players[0])
            
    def roll(self, player, roll):
        self.t_roll = roll
        
    def ongoing(self, player):
        i = 0
        
        while i in range(len(self.pids)):
            
            c = self.cards[i]
            pid = self.pids[i]
            p = self.game.get_player(pid)

            if not p.treasure:

                c.wait = None
                self.pids.pop(i)
                self.cards.pop(i)
                
            else:
                
                i += 1
                
        if not self.pids:
            
            return True

        if all(c.t_roll != -1 for c in self.cards):
            
            m = max(c.t_roll for c in self.cards)
            
            players = []

            for pid, c in zip(self.pids, self.cards):
                
                p = self.game.get_player(pid)

                if c.t_roll == m and p.treasure:

                    players.append(p)

            if len(players) <= 1:
                
                if players:
                
                    player.steal_random_card('treasure', players[0])
                
                return True
                
            else:
                
                self.deploy(players)
            
class TumbleWeed(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'tumble weed', ['plant', 'desert'])

    def start(self, player):
        if any('human' in c.tags for c in player.played):
            player.lose(self, 10)
        else:
            player.gain(self, 5)
            
class WindGust(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'wind gust', ['event'])
        
    def start(self, game):
        for p in game.players: 
            p.ongoing.append(self)
        
    def ongoing(self, player):
        if player.check_log('play'):
            self.game.restock_shop()
            
class Sunglasses(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sunglasses', ['item'])
        
    def can_use(self, player):
        return player.is_turn and len(player.unplayed) > 1 and not player.gone
        
    def get_selection(self, player):
        return [c.copy() for c in player.unplayed]

    def start(self, player):
        player.add_request(self, 'select')

    def select(self, player, num):
        if num:

            c = player.selected.pop(0)

            if c in player.unplayed:

                player.play_card(c)
                player.gone = False
                player.discard_card(self)
            
class MetalDetector(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'metal detector', ['item'])
        
    def can_use(self, player):
        return self.game.get_discarded_items()
            
    def start(self, player):
        items = self.game.get_discarded_items()[::-1]
        
        while items:
            
            i = items.pop(0)
            
            if not self.game.check_exists(i.uid):

                self.game.restore(i)
                player.add_card(i, 'items')
                player.discard_card(self)
                
                break
            
class SandStorm(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sand storm', ['event'])
        
    def start(self, game):
        for p in game.players:

            p.ongoing.append(self)
            
    def ongoing(self, player):
        if player.check_log('play'):

            played = [p.played for p in self.game.players]
            random.shuffle(played)
            
            for p, played in zip(self.game.players, played):
                
                p.new_deck('played', played)

class Mummy(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mummy', ['monster', 'desert', 'human'])
        
    def deploy(self, players):
        for p in players:
            
            horse = self.copy()
            p.requests.append(horse)
            
    def get_selection(self, player):
        return self.sort_players(player, 'steal')
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        
        for i in range(i + 1, len(player.played)):
            
            c = player.get_played_card(i)
            
            if c is None:
                break
                
            if 'monster' in c.tags:
                if c not in self.cards:
                    self.cards.append(c)
                    player.add_request(self, 'select')
                
    def select(self, player, num):
        if num:
            
            player.steal(self, 5, player.selected.pop(0))
            
class MummysCurse(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'mummys curse', ['spell'])
        
    def get_selection(self, player):
        return [c.copy() for c in player.played if 'human' in c.tags]
        
    def ongoing(self, player):
        if player.check_log('play'):
            player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:
            self.wait = 'select' 
        else: 
            player.lose(self, 5)
            
    def select(self, player, num):
        if num: 
            player.play_card(player.selected.pop(0), d=True)
            
class Pig(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'pig', ['animal', 'farm'])
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        
        for i in range(i + 1, len(player.played)):
            
            c = player.get_played_card(i)
            
            if c is None:
                break
                
            if 'plant' in c.tags:
                if c not in self.cards:
                    self.cards.append(c)
                    
                    if 'farm' in c.tags:
                        player.gain(self, 10)
                    else:
                        player.gain(self, 5)
                        
            else:
                break
            
class Corn(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'corn', ['plant', 'farm'])

    def get_selection(self, player):
        if len(player.selected) == 0:
        
            return [c.copy() for c in player.get_items()]
            
        elif len(player.selected) == 1:
            
            return self.sort_players(player)
        
    def start(self, player):
        player.ongoing.append(self)
        
    def ongoing(self, player):
        if self not in player.played:
            return True
            
        i = player.played.index(self)
        c = player.get_played_card(i + 1)
        
        if c is None:
            return 
            
        if c not in self.cards:
            self.cards.append(c)
            
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'harvest', ['event'])
            
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:
            
            if 'plant' in c.tags:
                
                gp = 10 if any(l.name in c.tags for l in player.landscapes) else 5
                player.gain(self, gp)
            
class GoldenEgg(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'golden egg', ['treasure'])
        
    def end(self, player):
        player.gain(self, sum(5 for c in player.played if 'animal' in c.tags))
        
class Bear(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'bear', ['animal', 'forest'])
        
    def start(self, player):
        sp = 4 if self.game.get_event() == 'parade' else 2
        
        for p in self.sort_players(player, 'steal'):
            
            player.steal(self, sum(sp for c in p.played if 'human' in c.tags), p)
            
class BigRock(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'big rock', ['item'])
        
    def can_use(self, player):
        return player.played
        
    def get_selection(self, player):
        return [c.copy() for c in player.played]
        
    def start(self, player): 
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:

            c1 = player.selected.pop(0)
            c2 = self.game.get_card(c1.name)
            
            if c1 in player.played:
            
                i = player.played.index(c1)
                deck = player.played.copy()
                deck.insert(i + 1, c2)
                
                player.new_deck('played', deck)
                
                player.discard_card(self)
                
                if hasattr(c2, 'ongoing'):
                    
                    player.ongoing.append(c2)
            
class UnluckyCoin(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'unlucky coin', ['item'])
        
    def can_use(self, player):
        return True
        
    def get_selection(self, player):
        return self.game.players.copy()
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            player.discard_card(self)
            
            p.ongoing.append(self)

    def ongoing(self, player):
        if player.flipping:
        
            player.coin = 0
            self.mode = 1
            
        if self.mode == 1 and player.get_logs('cfe'):

            return True
            
class HuntingSeason(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'hunting season', ['event'])

    def start(self, game):
        for p in game.players:
            
            p.ongoing.append(self)

    def ongoing(self, player):
        animals = [log['c'].copy() for log in player.get_logs('play') if 'animal' in log['c'].tags and log['c'] not in self.cards] #maybe change
        
        for _ in range(len(animals)):
            
            c = self.copy()
            player.add_request(c, 'flip')
            
        self.cards += animals
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 3)
            
class Stardust(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'stardust', ['spell'])

        self.mult = False
        
    def start(self, player):
        for p in self.sort_players(player):
            self.get_cards_from_logs(p, 'dt')
        
    def ongoing(self, player):
        for p in self.sort_players(player):
            
            for _ in self.get_cards_from_logs(p, 'dt')[:5]:
                
                c = self.copy()
                player.add_request(c, 'flip')
                
    def coin(self, player, coin):
        if coin:
            player.draw_cards('treasure')
        else: 
            player.lose(self, 5)
            
class WaterLilly(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'water lilly', ['plant', 'water'])
        
    def start(self, player):
        gp = len(player.get_items() + player.spells) + (len(player.get_spells()) * 5)
        player.gain(self, gp)
        
class Torpedo(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'torpedo', ['equipment'])

    def start(self, player):
        self.pids.clear()
        player.equip(self)
        
    def coin(self, player, coin):
        if coin:
            
            pid, sp = self.pids
            p = self.game.get_player(pid)
            
            player.steal(self, sp, p)

    def ongoing(self, player):
        logs = player.get_logs('sp')
        
        if logs:
            
            log = logs[-1]
            
            self.pids = [log['target'].pid, log['sp']]
            player.add_request(self, 'flip')
            player.discard_card(self)
            
            return True
        
class Bat(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'bat', ['animal', 'sky'])
        
        self.option1 = Blank(self.game, 'draw item')
        self.option2 = Blank(self.game, 'draw spell')
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'sky flower', ['plant', 'sky'])
        
    def get_selection(self, player):
        return self.sort_players(player)
        
    def start(self, player):
        player.add_request(self, 'select')
            
    def select(self, player, num):
        if num:
            
            player.give(self, 5, player.selected.pop(0))
            player.draw_cards('treasure')
        
class Kite(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'kite', ['item'])
        
    def can_use(self, player):
        return bool(player.unplayed)
        
    def start(self, player):
        player.draw_cards('unplayed')
        player.discard_card(self)
        
class Balloon(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'balloon', ['item'])
        
    def can_use(self, player):
        return len(player.played) > 1
        
    def start(self, player):
        player.new_deck('played', player.played[::-1])
        
        player.discard_card(self)
        
class NorthWind(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'north wind', ['spell'])
        
        self.mult = False

    def ongoing(self, player):
        if player.check_log('play'):
        
            player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 3 * len(player.get_spells()))
        
class GardenSnake(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'garden snake', ['animal', 'garden'])
        
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
    def __init__(self, game, uid):
        super().__init__(game, uid, 'watering can', ['item'])
        
    def can_use(self, player):
        return not player.has_card('landscapes', 'water')
        
    def start(self, player):
        for c in player.landscapes.copy():
            
            self.game.transform(c, Water)
            
        player.discard_card(self)
        
class MagicBean(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'magic bean', ['treasure'])
        
    def end(self, player):
        player.gain(self, sum(5 for c in player.played if 'plant' in c.tags))
        
class Trap(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'trap', ['item'])
        
    def can_use(self, player):
        return self.game.shop
        
    def get_selection(self, player):
        return [c.copy() for c in self.game.shop]
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            player.discard_card(self)
            
            s = player.selected.pop(0)
            
            for p in self.game.players:
                
                c = self.copy()
                c.extra_card = s.copy()
                p.ongoing.append(c)
 
    def ongoing(self, player):
        logs = player.get_logs('buy')

        for log in logs:

            if log['c'] == self.extra_card:
            
                player.lose(self, 5)
            
                return True
        
class FlowerPot(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'flower pot', ['item'])
        
    def can_use(self, player):
        return not player.has_card('landscapes', 'garden')
        
    def start(self, player):
        for c in player.landscapes.copy():
            
            self.game.transform(c, Garden)
            
        player.discard_card(self)       
        
class TheVoid(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'the void', ['spell'])
        
        mult = True
        
    def ongoing(self, player):
        if self.game.get_event() != 'negative zone':
            
            attr = 'gain'
            key1 = 'lp'
            key2 = 'gp'
            
        else:
            
            attr = 'lose'
            key1 = 'gp'
            key2 = 'lp'
            
        logs = player.get_logs(key1)
        
        if logs:
            
            for log in logs:
                
                log[key2] = getattr(player, attr)(self, log[key1] * 2, d=True) // 2
                log['t'] = key2
        
class BugNet(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'bug net', ['item'])
        
    def can_use(self, player):
        return player.played
        
    def get_selection(self, player):
        return [c.copy() for c in player.played]
        
    def start(self, player):
        player.add_request(self, 'select')
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            if c in player.played:
     
                player.discard_card(c, ogd=True)

                player.new_deck('played', player.played)
                
                player.discard_card(self)
        
class BigSandWorm(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'big sand worm', ['animal', 'desert'])
        
    def start(self, player):
        if self.game.check_last(player):
            
            player.gain(self, 5)
            
        else:
            
            player.lose(self, 5)
            
class LostPalmTree(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'lost palm tree', ['plant', 'desert', 'water'])
        
    def start(self, player):
        t = False
        
        for c in player.landscapes.copy():
            
            if c.name == 'desert':
                
                self.game.transform(c, Water)
                
                if not t:
                    
                    player.draw_cards('treasure')
                    t = True
                    
class Seaweed(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'seaweed', ['plant', 'water'])
        
    def start(self, player):
        player.add_request(self, 'flip')
        
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 3)
            player.draw_cards('treasure')
            
        else:
            
            player.lose(self, 4)
        
class ScubaBaby(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'scuba baby', ['human', 'water'])
        
    def start(self, player):
        player.gain(self, 3)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        