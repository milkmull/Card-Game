import random
import time
import copy

class Textbox:
    def __init__(self, name):
        self.name = name
        
        self.uid = id(self)
        
    def __repr__(self):
        return self.name
        
    def get_id(self):
        return self.uid
        
    def sim_copy(self, game):
        return self

class Card:
    def __init__(self, name, cid, type, habitat=None):

        self.name = name
        self.cid = cid
        self.type = type
        self.habitat = habitat
        
        self.mode = 0
        self.counter = 0

        self.tag = None
        self.wait = None
        self.t_coin = None
        
        self.mult = True
        
        self.cards = []
        self.pids = []
        self.horses = {}
        
        self.extra_card = None
        
    def sort_players(self, player, cond=None):
        if cond is None:
        
            return [p for p in self.game.players if p.pid != player.pid]
            
        elif cond == 'steal':
            
            return [p for p in self.game.players if p.pid != player.pid and not p.invincible and p.score]
            
        else:
            
            return [p for p in self.game.players if p.pid != player.pid and cond(p)]
            
    def pid(self, pid):
        return self.game.get_player(pid)

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        return self.uid == other.get_id()
        
    def copy(self): 
        return type(self)(self.game, self.uid)
        
    def light_sim_copy(self, game):
        return type(self)(game, self.uid)
        
    def sim_copy(self, game):
        c = type(self)(game, self.uid)
        
        c.counter = self.counter
        c.mode = self.mode
        
        c.tag = self.tag
        c.wait = self.wait
        c.t_coin = self.t_coin
        
        c.pids = self.pids.copy()
        c.cards = [c.sim_copy(game) for c in self.cards]
        c.horses = {pid: c.sim_copy(game) for pid, c in self.horses.items()}
        
        if self.extra_card:
        
            c.extra_card = self.extra_card.sim_copy(game)
    
        return c
        
    def get_id(self):
        return self.uid

class Michael(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('michael', 0, 'human')

    def start(self, player):
        sp = 5 if self.game.current_player == 0 else 2

        for p in self.sort_players(player):

            player.steal(self, sp, p)
        
class Dom(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('dom', 1, 'human')
        
    def start(self, player):
        points = 0
        
        for p in self.game.players:
            
            gp = 2 if p == player and player.has_item('big rock') else 1
            
            points += len([gp for c in p.played if c.type == 'animal'])
                    
        player.gain(self, points)
        
class Jack(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('jack', 2, 'human')
        
    def start_request(self, player):
        if not self.cards:
            
            self.cards = self.game.draw_cards(num=len(self.game.players))

        player.new_selection(self, self.cards.copy())
        
    def start(self, player):
        if len(self.game.deck) >= len(self.game.players):
            
            self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            self.cards.remove(c)
            
            player.unplayed.append(c)
            
            for p, c in zip(self.sort_players(player), self.cards):
            
                p.unplayed.append(c)
                
            self.cards.clear()
            
class Mary(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mary', 3, 'human')
        
    def start(self, player):
        if self.game.check_last(player) or player.has_item('lucky coin'):
        
            for p in self.sort_players(player):
                    
                p.lose(self, 2)
                    
class Daniel(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('daniel', 4, 'human')
        
    def start_request(self, player):
        player.new_selection(self, [self.game.get_player(pid) for pid in self.pids.copy()])
        
    def start(self, player):    
        if player.has_spell('item leech'):
            
            player.draw_treasure(2)
            
        players = [p.count_type('human') for p in self.sort_players(player, 'steal')]
        
        if players:
            
            m = max(players)

            if m:
                
                self.pids = [p.pid for p in self.sort_players(player, 'steal') if p.count_type('human') == m]

                self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.steal(self, 5, player.selected.pop(0))

class Emily(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('emily', 5, 'human')
        
        self.tag = 'cont'
        
    def start(self, player):
        self.counter = 0
        
        player.add_og(self)

    def ongoing(self, player): 
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        while self.counter < 2:
            
            try:
                
                c = owner.played[i + self.counter]
                
                if c.type == 'human':
                    
                    player.gain(self, 5)
                    self.counter += 1
                    
                else:
                    
                    return True

            except IndexError:
                
                break
                
        if self.counter == 2:
            
            return True
                  
class GamblingBoi(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('gambling boi', 6, 'human')
        
    def start(self, player):
        score = len(player.played) - len(player.unplayed)

        if score < 0:
        
            player.lose(self, -score)
        
        elif score > 0:
        
            player.gain(self, score)
            
class Mom(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mom', 7, 'human')
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_flip(self)
            
        elif self.mode == 1:
            
            player.new_selection(self, self.sort_players(player, 'steal'))
        
    def start(self, player):
        if player.has_landscape('city'):
            
            player.draw_treasure()
            
        self.mode = 0
        
        self.start_request(player)
        
    def coin(self, player, coin):
        if coin:
            
            self.mode = 1
            
            self.start_request(player)
            
        else:
            
            player.lose(self, 4)
            
    def select(self, player, num):
        if num:
            
            player.steal(self, 4, player.selected.pop(0))
            
class Dad(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('dad', 8, 'human')
        
    def start_request(self, player):
        player.new_selection(self, [self.game.get_player(pid) for pid in self.pids.copy()])
        
    def start(self, player):
        if player.has_spell('curse'):
            
            for p in self.sort_players(player):
                
                p.lose(self, 10)
                
        else:

            hs = max(p.score for p in self.game.players)
            
            self.pids = [p.pid for p in self.game.players if p.score == hs]

            self.start_request(player)
                
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            lp = 5 if p == player else 10
            
            p.lose(self, lp)
            
class AuntPeg(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('aunt peg', 9, 'human')
            
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if owner:
            
            gp = owner.played.index(self)
            
        else:
            
            gp = len(player.played) + 1

        player.gain(self, gp)
        
class UncleJohn(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('uncle john', 10, 'human')
        
    def start_request(self, player):
        player.new_selection(self, [self.game.get_player(pid) for pid in self.pids.copy()])
    
    def start(self, player):
        if self.game.check_first(player) and self.sort_players(player, 'steal'):
            
            hs = max(p.score for p in self.sort_players(player, 'steal'))
            
            self.pids = [p.pid for p in self.sort_players(player, 'steal') if p.score == hs]

            self.start_request(player)
                
    def select(self, player, num):
        if num:
            
            player.steal(self, 5, player.selected.pop(0))
            
class Joe(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('joe', 11, 'human')
        
    def start_request(self, player):
        player.new_selection(self, [p for p in self.sort_players(player, 'steal') if p.items])
        
    def start(self, player):
        if any(p.items for p in self.sort_players(player, 'steal')):
            
            self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            sp = 10 if self.game.check_last(player) else len(p.items)
            
            player.steal(self, sp, p)
            
class Ninja(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('ninja', 12, 'human')
              
    def start(self, player):
        if any(any(c.type == 'human' for c in p.played) for p in self.sort_players(player)):

            lp = 5 if player.has_item('sword') else 2

            for p in self.sort_players(player):

                p.lose(self, sum(lp for c in p.played if c.type == 'human'))
                        
class Robber(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('robber', 13, 'human')
        
    def start_request(self, player):
        player.new_flip(self)
    
    def start(self, player):
        player.draw_items()
        
        if self.game.get_event() == 'item frenzy':
            
            self.start_request(player)
            
    def coin(self, player, coin):
        if coin:
            
            player.draw_treasure()
        
class MaxTheDog(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('max the dog', 14, 'animal', 'city')
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player, lambda p: p.treasure))
    
    def start(self, player):
        if not player.unplayed:
            
            for p in self.sort_players(player):
            
                p.lose(self, 10)
                
        if player.has_item('unlucky coin'):
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.steal_treasure(player.selected.pop(0))
 
class BasilTheDog(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('basil the dog', 15, 'animal', 'city')
                
    def start(self, player):
        if self.game.check_last(player):
            
            player.gain(self, 10)
            
        if player.has_landscape('city'):
            
            player.draw_spells()
            
class CopyCat(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('copy cat', 16, 'animal', 'city')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        cards = [c.copy() for c in player.played if c.name != self.name]
        
        try:
            
            cards.append(player.unplayed[0].copy())
            
        except IndexError:
            
            pass

        player.new_selection(self, cards)
        
    def start(self, player): #maybe offer choice
        if player.has_item('mirror') and player.played:
        
            self.start_request(player)
            
        else:
        
            player.add_og(self)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        while self.counter < 1:
            
            try:
                
                c = owner.played[i]
                
                player.play_card(c, d=True)
                
                self.counter = 1
                
            except IndexError:
                
                break
    
        if self.counter == 1:
   
            return True
            
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            if c in player.played:
            
                player.play_card(c)
            
            else:
                
                player.add_og(self)
                
class Racoon(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('racoon', 17, 'animal', 'city')
        
    def start_request(self, player):
        if self.mode == 0:

            player.new_selection(self, [c.copy() for c in player.items])
            
        elif self.mode == 1:
            
            player.new_selection(self, self.sort_players(player, lambda p: p.treasure))
        
    def start(self, player):    
        if player.items and any(p.items for p in self.sort_players(player)):

            self.start_request(player)
            
        if player.has_spell('spell trap'):
            
            c = self.copy() #visuals look bad
            
            c.mode = 1
            
            c.start_request(player)

    def select(self, player, num): 
        if self.mode == 0:
        
            if num == 1:
            
                player.new_selection(self, [p for p in self.sort_players(player) if p.items])
                
            elif num == 2:
                
                player.new_selection(self, [c.copy() for c in player.selected[-1].items])
                
            elif num == 3:

                self.game.swap(player.selected[0], player.selected[2]) #caused some problems
                
        elif self.mode == 1:
            
            if num:
                
                player.steal_treasure(player.selected.pop(0))
            
class Fox(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fox', 18, 'animal', 'forest')
        
    def start_request(self, player):
        self.start(player)
        
    def start(self, player):
        player.new_selection(self, self.sort_players(player, 'steal'))
    
    def select(self, player, num):
        if num:
        
            sp = 10 if self.game.check_first(player) else 5
            
            player.steal(self, sp, player.selected.pop(0))
            
class Cow(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('cow', 19, 'animal', 'farm')

        self.tag = 'cont'
        
    def start_request(self, player):
        self.counter = len([c for c in player.played if c.type == 'plant']) #may need extra log to track plant cards
        
        player.new_flip(self)
        
    def start(self, player):
        player.add_og(self)
        
        if player.has_landscape('farm') and any(c.type == 'plant' for c in player.played):
            
            self.start_request(player)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            c = owner.played[i]
            
            if c.type == 'plant':
                
                player.gain(self, 4)
                
            return True
            
        except IndexError:
            
            return
            
    def coin(self, player, coin):
        if coin:
            
            player.draw_treasure()
            
        self.counter -= 1
        
        if self.counter:
            
            player.new_flip(self)
            
class Shark(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('shark', 20, 'animal', 'water')
        
    def start_request(self, player):
        self.start(player)
        
    def start(self, player):
        player.new_selection(self, self.sort_players(player, 'steal'))
            
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            sp = 10 + sum(1 for c in p.played if c.name == 'fish') if player.has_item('fishing pole') else 10

            player.steal(self, sp, p)

class Fish(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fish', 21, 'animal', 'water')
        
    def start(self, player):
        for c in player.played:
            
            if c.name == 'fish':
                
                player.gain(self, 5)
                
class Pelican(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('pelican', 22, 'animal', 'sky')
            
    def start(self, player):     
        gp = 4 if player.has_item('balloon') else 2

        player.gain(self, sum(gp for c in player.played if c.name == 'fish'))
                
class LadyBug(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('lady bug', 23, 'animal', 'sky')
        
        self.tag = 'cont'
        
    def start(self, player):
        player.add_og(self)
            
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            c = owner.played[i]
            
            if c.type == 'animal':
                
                player.gain(self, 10)
                
            else:
                
                player.lose(self, 5)
                
            return True
            
        except IndexError:
            
            return
            
class Mosquito(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mosquito', 24, 'animal', 'graveyard')
        
    def start(self, player):
        for p in self.sort_players(player, 'steal'):
            
            sp = 2 if self.game.get_event() == 'flu' else 1
        
            player.steal(self, sum(sp for c in p.played if c.type == 'human'), p)
                        
class Snail(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('snail', 25, 'animal', 'garden')
        
    def start_request(self, player):
        player.new_flip(self)
        
    def start(self, player):
        if len(player.unplayed) == 1:
                
            player.gain(self, 20)
            
        if player.has_item('last turn pass'):
            
            self.start_request(player)
 
    def coin(self, player, coin):
        if coin:
                
            player.draw_treasure()
            
class PoisonIvy(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('poison ivy', 26, 'plant', 'forest')
        
    def start_request(self, player):
        player.new_selection(self, [s.copy() for s in player.get_spells()])
        
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if owner:
            
            i = owner.played.index(self)
            
        else:
            
            i = len(player.played)
        
        for p in self.sort_players(player, 'steal'):

            try:
            
                c = p.played[i]
                
                if c.type == 'human':
                    
                    player.steal(self, 5, p)
            
            except IndexError:
            
                continue
                
        if player.has_item('treasure chest'):
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.remove_spell(player.selected.pop(0))
                    
class Rose(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('rose', 27, 'plant', 'garden')
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player))
                
    def start(self, player):
        if player.has_item('flower pot'):
            
            player.draw_treasure()
            
        if player.score < 15:
        
            player.gain(self, 5)
            
        elif player.score > 15:
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.give(self, 5, player.selected.pop(0))
            
class LastTurnPass(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('last turn pass', 28, 'item')
        
    def can_use(self, player):
        return self.game.players[-1] != player
                
    def start(self, player):
        if self.game.players[-1] != player:
        
            for i in range(len(self.game.players)):
                
                if self.game.players[i].pid == player.pid:
                    
                    self.game.players.append(self.game.players.pop(i))
                    
                    self.game.advance_turn()
                    
                    player.use_item(self)
                    
                    return
                
class SpeedBoostPotion(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('speed boost potion', 29, 'item')
        
        self.option1 = Textbox('go first')
        self.option2 = Textbox('steal treasure')
        
    def can_use(self, player):
        return self.game.players[0] != player
        
    def start_request(self, player):
        if self.mode == 0:

            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1:
            
            player.new_selection(self, self.sort_players(player, lambda p: p.treasure))

    def start(self, player):
        self.mode = 0
        
        if self.game.players[0].pid != player.pid:

            if player.has_spell('treasure curse') and any(p.treasure for p in self.sort_players(player)):

                self.start_request(player)
                
            else:
                
                self.o1(player)
            
    def select(self, player, num):
        if self.mode == 0:
        
            if num:
                
                o = player.selected.pop(0)
                    
                if o is self.option1:
                    
                    self.o1(player)
                    
                elif o is self.option2:

                    self.mode = 1
                    
                    self.start_request(player)
                    
        elif self.mode == 1:
            
            if num:
            
                self.o2(player)

    def o1(self, player):
        for i in range(len(self.game.players)):
            
            if self.game.players[i].pid == player.pid:
                
                self.game.players.insert(0, self.game.players.pop(i))
                
                self.game.advance_turn()
                
                player.use_item(self)
                
                return
                
    def o2(self, player):
        player.steal_treasure(player.selected.pop(0))

        player.use_item(self)
                
class Sword(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sword', 30, 'equipment')

        self.tag = 'cont'
        
        self.option1 = Textbox('recover last item')
        self.option2 = Textbox('equip')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, [self.option1, self.option2])
        
    def start(self, player):
        if player.has_spell('item leech') and player.get_m_logs('ui'):
            
            self.start_request(player)
            
        else:
            
            player.equip(self)
            
    def select(self, player, num):
        if num:
        
            o = player.selected.pop(0)
            
            if o is self.option1:
                
                self.o1(player)
                
            elif o is self.option2:
                
                player.equip(self)
                
    def o1(self, player):
        c = player.get_m_logs('ui')[-1]['card']
        
        player.items.append(c)
        
        player.use_item(self)

    def ongoing(self, player):
        logs = player.get_logs('sp')
        
        if logs:
            
            for log in logs:
                
                log['sp'] += player.steal(self, log['sp'], log['target'], d=True)
                
            player.use_item(self)

class FishingPole(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fishing pole', 31, 'item')
        
        self.option1 = Textbox('flip for treasure')
        self.option2 = Textbox('move fish')
        
    def can_use(self, player):
        return [c.copy() for p in self.sort_players(player) for c in p.played if c.name == 'fish']
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1:
            
            player.new_flip(self)
            
        elif self.mode == 2:
            
            player.new_selection(self, [c.copy() for c in player.played])
        
    def start(self, player):
        self.mode = 0

        self.cards = [c.copy() for p in self.sort_players(player) for c in p.played if c.name == 'fish']
        
        if self.cards:

            if not self.game.get_event() == 'fishing trip':
                
                self.mode = 2
                
            self.start_request(player)
        
    def coin(self, player, coin):
        if coin:
            
            player.draw_treasure()
            
        player.use_item(self)
        
    def select(self, player, num):
        if self.mode == 0:
        
            if num:

                o = player.selected.pop(0)
                
                if o is self.option1:
                    
                    self.mode = 1
                    
                elif o is self.option2:
                    
                    self.mode = 2
                    
                self.start_request(player)
        
        elif self.mode == 2:

            if num == 1:

                player.new_selection(self, self.cards.copy())
                    
            elif num == 2:

                self.game.swap(player.selected[0], player.selected[1])
                
                player.use_item(self)
        
class Fertilizer(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fertilizer', 32, 'item')

        self.option1 = Textbox('draw treasure')
        self.option2 = Textbox('play plant card')
        
    def can_use(self, player):
        return any(c.type == 'plant' for c in player.played)
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1:
            
            player.new_selection(self, [c.copy() for c in player.played if c.type == 'plant'])
        
    def start(self, player):
        self.mode = 0
        
        if any(c.type == 'plant' for c in player.played):

            if not self.game.get_event() == 'harvest':

                self.mode = 1
            
            self.start_request(player)
        
    def select(self, player, num):
        if self.mode == 0:
        
            if num:
                
                o = player.selected.pop(0)
                
                if o is self.option1:
                    
                    player.draw_treasure()
                    
                    player.use_item(self)
                    
                elif o is self.option2:
                    
                    self.mode = 1
                    
                    self.start_request(player)
                    
        elif self.mode == 1:
            
            if num:
                
                player.play_card(player.selected.pop(0), d=True)

                player.use_item(self)
    
class Cactus(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('cactus', 33, 'plant', 'desert')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player, 'steal'))
        
    def start(self, player):
        player.add_og(self)
        
        if player.has_landscape('desert') and player.played:

            if player.played[0] != self:
                
                self.start_request(player)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            if owner.played[i] != self:

                player.invincible = False
                
                return True
                
            else:
                
                player.invincible = True
                
        except IndexError:
            
            return
            
    def select(self, player, num):
        if num:
            
            player.steal(self, 5, player.selected.pop(0))
            
class MustardStain(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mustard stain', 34, 'treasure')
        
    def end(self, player):
        if player.has_item('detergent'):
            
            player.gain(self, 25)
            
            player.use_item(next(c for c in player.items if c.name == 'detergent'))
            
class Gold(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('gold', 35, 'treasure')
        
    def draw(self, player):
        player.draw_items()
        
    def end(self, player):
        player.gain(self, 15)
        
class Uphalump(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('uphalump', 36, 'monster')

    def start_request(self, player):
        self.start(player)
        
    def start(self, player):
        player.new_selection(self, self.sort_players(player, 'steal'))
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            sp = 10 if player.has_landscape('graveyard') else len(p.items) * 2
            
            player.steal(self, sp, p)
            
            if sp == 10:
                
                player.draw_spells()
            
class Ghost(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('ghost', 37, 'monster')
        
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if not owner:
            
            owner = player
        
        if owner.played:
        
            if owner.played[-1].type == 'human':
                
                player.play_card(owner.played[-1])
                
        if player.has_item('invisibility cloak'):
            
            player.unplayed += self.game.draw_cards()
            
class TreasureChest(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('treasure chest', 38, 'item')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_roll(self)
        
    def start(self, player):
        if player.has_spell('luck'):
        
            self.start_request(player)
        
        else:
        
            player.use_item(self)
            
            player.draw_treasure()
            
    def roll(self, player, roll):
        if roll in (1, 2, 3):
            
            player.draw_treasure(2)
            
        player.use_item(self)
        
class Pearl(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('pearl', 39, 'treasure')
        
    def end(self, player):
        player.gain(self, 10)
        
class Dragon(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('dragon', 40, 'monster')

        self.tag = 'cont'
        
        self.t_coin = None
        
        self.horses = {} #pid: card
        
    def start_request(self, player):
        if self.mode == 0:
        
            player.new_selection(self, self.sort_players(player, 'steal'))
            
        elif self.mode == 1:
            
            player.new_flip(self)
            
    def deploy(self, players):
        for p in players:
                
            horse = self.copy()
            horse.mode = 1
            p.new_flip(horse) #could cause problems
            self.horses[p.pid] = horse

    def start(self, player):
        players = self.sort_players(player, 'steal')
        
        if player.has_item('treasure chest') and players:

            self.deploy(players)
            
            player.ongoing.append(self)

        else:
            
            self.mode = 0
        
            self.start_request(player)
            
    def coin(self, target, coin):
        self.t_coin = coin
            
    def select(self, player, num):
        p = player.selected.pop(0)
        
        sp = len(p.items + p.treasure + p.spells)
        
        player.steal(self, sp, p)
        
    def ongoing(self, player):
        if self.horses:
        
            for pid in self.horses.copy():
                
                c = self.horses[pid]
                p = self.game.get_player(pid)
                
                if c.t_coin is not None:
                    
                    if not c.t_coin:
                        
                        player.steal(self, 10, p)
                        
                    del self.horses[pid]
            
        else:
            
            return True

class Clam(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('clam', 41, 'animal', 'water')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_flip(self)
        
    def start(self, player):
        if self.game.check_first(player):
                
            player.add_og(self)

        self.start_request(player)
        
    def coin(self, player, coin):  
        if coin:
            
            player.draw_treasure()
                
            if player.treasure[-1].name == 'pearl':
                
                player.draw_items()
                player.draw_spells()
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            c = owner.played[i]
            
            if c.habitat == 'water' and c.type == 'animal':
                
                player.new_flip(self)
                
            return True
            
        except IndexError:
            
            return
                
class GoldCoins(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('gold coins', 42, 'item')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, self.game.shop.copy())
        
    def start(self, player):   
        self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            if player.buy_card(c.uid):
                
                if self in player.treasure:
                
                    player.treasure.remove(self)
        
class InvisibilityCloak(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('invisibility cloak', 43, 'equipment')

        self.tag = 'cont'
        
        self.option1 = Textbox('remove spells')
        self.option2 = Textbox('equip')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, [self.option1, self.option2])
        
    def start(self, player):
        if self.game.get_event() == 'spell reverse':
            
            self.start_request(player)
            
        else:
            
            player.equip(self)
            
    def select(self, player, num):
        if num:
            
            o = player.selected.pop(0)
            
            if o is self.option1:
                
                self.o1(player)
                
            elif o is self.option2:
                
                player.equip(self)
                
    def o1(self, player):
        for c in player.get_spells():
                
            player.remove_spell(c)
            
        player.use_item(self)
        
    def ongoing(self, player):
        logs = player.get_logs('rp')
        
        if logs:
        
            for log in logs:
                
                p, rp = log['robber'], log['rp']
                
                player.steal(self, rp, p, d=True)
                player.remove_log(log)
                
            player.use_item(self)
                        
class Curse(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('curse', 44, 'spell')

        self.tag = 'play'
        
    def start_request(self, player):
        self.ongoing(player)

    def ongoing(self, player):
        player.new_flip(self)
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 2)
    
class TreasureCurse(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('treasure curse', 45, 'spell')

        self.tag = 'cont'

        self.mult = False
        
    def start_request(self, player):
        if self.mode == 0:
        
            player.new_flip(self)
            
        elif self.mode == 1:
            
            player.new_selection(self, self.sort_players(player))
        
    def ongoing(self, player):
        treasure = [log['card'].copy() for log in player.get_logs('dt') if log['card'] not in self.cards]
        
        self.cards += treasure
        
        while treasure:
            
            c = self.copy()
            
            c.extra_card = treasure.pop(0)
            
            c.start_request(player) 
        
    def coin(self, player, coin):
        if not coin:
            
            self.mode = 1
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            target = player.selected.pop(0)
            
            target.take_treasure(self.extra_card, player)
                
class Bronze(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('bronze', 46, 'treasure')
        
    def end(self, player):
        player.gain(self, 5)
        
class ItemHex(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('item hex', 47, 'spell')

        self.tag = 'play'
        
    def start_request(self, player):
        self.ongoing(player)
        
    def ongoing(self, player):
        player.new_flip(self)
      
    def coin(self, player, coin):
        if coin:

            player.gain(self, len(player.get_items()))
            
        else:
            
            player.lose(self, len(player.get_items()))
                
class Luck(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('luck', 48, 'spell')

        self.tag = 'cont'

        self.mult = False
        
    def start_request(self, player):
        self.ongoing(player)
        
    def ongoing(self, player):
        if player.flipping:
        
            player.coin = 1
            
class Boomerang(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('boomerang', 49, 'equipment')

        self.tag = 'cont'
        
    def can_use(self, player):
        return True
        
    def start(self, player):
        if not any(c.name == self.name for c in player.equipped):
        
            player.equip(self)
        
    def ongoing(self, player):
        logs = player.get_logs('lp')
        
        if logs:
            
            for log in logs:
                
                if self.game.get_event() != 'negative zone':
                
                    log['gp'] = player.gain(self, log['lp'] * 2, d=True) // 2
                    
                    log['type'] = 'gp'
                
            player.use_item(self)
        
class BathTub(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('bath tub', 50, 'item')
        
    def can_use(self, player):
        return (player.has_landscape('water') and any(p.get_spells() for p in self.sort_players(player))) or player.get_spells()
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [c.copy() for c in player.get_spells()])
            
        elif self.mode == 1:
            
            player.new_selection(self, [p for p in self.game.players if p.get_spells()])
        
    def start(self, player):
        if player.has_landscape('water') and any(p.get_spells() for p in self.sort_players(player)):
            
            self.mode = 1
            
            self.start_request(player)
            
        elif player.get_spells():
            
            self.mode = 0
            
            self.start_request(player)

    def select(self, player, num):
        if self.mode == 0:
            
            if num:
                
                player.remove_spell(player.selected.pop(0))
                
                player.use_item(self)
                
        elif self.mode == 1:
            
            if num == 1:
                
                p = player.selected[0]
                
                player.new_selection(self, [c.copy() for c in p.get_spells()])
                
            elif num == 2:
                
                p, c = player.selected
                
                p.remove_spell(c)
                
                player.use_item(self)
        
class ItemLeech(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('item leech', 51, 'spell')

        self.tag = 'cont'
        
        self.mult = False
        
    def start_request(self, player):
        if self.mode == 0:
        
            player.new_flip(self)
            
        elif self.mode == 1:
            
            player.new_selection(self, self.sort_players(player))
        
    def ongoing(self, player):
        items = [log['card'].copy() for log in player.get_logs('ui') if log['card'] not in self.cards and not self.game.find_card(log['card'].uid)]
        
        self.cards += items
        
        while items:
            
            c = self.copy()
            
            c.extra_card = items.pop(0)
            
            c.start_request(player)
        
    def coin(self, player, coin):
        if not coin:
            
            self.mode = 1
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            self.game.restore(self.extra_card) #causing problems when self.item is None

            p.items.append(self.extra_card)
            
class Kristen(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('kristen', 52, 'human')
        
    def start(self, player):
        if len(player.get_spells()) == 2:
            
            d = True if player.has_spell('treasure curse') else False
            num = 2 if d else 1

            player.draw_treasure(num, d)
            
class Mirror(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mirror', 53, 'item')
        
    def can_use(self, player):
        return player.get_spells()
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.get_spells()])
        
    def start(self, player):
        self.counter = 0
        
        self.start_request(player)
        
    def select(self, player, num):
        if num == 1:
            
            c = player.selected[0]
            
            player.new_selection(self, [p for p in self.sort_players(player) if p.can_cast(c.name)])
        
        elif num == 2:
            
            c, p = player.selected
            
            player.remove_spell(c)
            p.ongoing.append(c)
            
            player.log.append({'type': 'cast', 'card': c.copy(), 'target': p, 'd': False})
            
            player.cancel_select()

            if self.counter == 0 and player.get_spells() and self.game.get_event() == 'negative zone':
                
                self.counter = 1
                
                self.start_request(player)
                
            else:

                player.use_item(self)

class LuckyDuck(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('lucky duck', 54, 'animal', 'sky')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_flip(self)
        
    def start(self, player):
        self.counter = 0
        
        if not self.counter and player.spells:
        
            self.counter = len(player.spells)

            self.start_request(player)
                
        if player.has_landscape('sky'):
            
            player.add_og(self)
        
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 5)
            
        self.counter -= 1
        
        if self.counter:
            
            player.new_flip(self)
            
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            player.play_card(owner.played[i], d=True)
            
            return True
            
        except IndexError:
            
            return
    
class MrSquash(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mr. squash', 55, 'plant', 'farm')
        
        self.tag = 'cont'
        
    def start(self, player):
        for p in self.sort_players(player, 'steal'):
            
            player.steal(self, sum(5 for c in p.played if c.type == 'plant'), p)
            
        player.add_og(self)
            
    def ongoing(self, player):
        for p in self.game.players:
            
            if any(c.name == 'mrs. squash' for c in p.played):
                
                player.gain(self, 20)
                
                return True
                
class MrsSquash(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mrs. squash', 56, 'plant', 'farm')
        
        self.tag = 'cont'

    def start(self, player):
        for p in self.sort_players(player, 'steal'):
            
            player.steal(self, sum(5 for c in p.played if c.type == 'plant'), p)

        player.add_og(self)
            
    def ongoing(self, player):
        for p in self.game.players:
            
            if any(c.name == 'mr. squash' for c in p.played):
                
                player.gain(self, 20)
                
                return True
                
class Detergent(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('detergent', 57, 'item')
        
        self.tag = 'cont'
        
    def can_use(self, player):
        return False
        
    def start(self, player):
        return
                
class SpellTrap(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('spell trap', 58, 'spell')
        
        self.tag = 'cont'

        self.mult = False
        
    def ongoing(self, player):
        logs = player.get_logs('cast')
        
        for log in logs:
            
            if log['card'] != self:
            
                player.lose(self, len(player.unplayed))
            
class Flu(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('flu', 59, 'event')

        self.tag = 'cont'
        
    def start(self, game):
        for p in game.players:
            
            p.ongoing.append(self)
            
    def ongoing(self, player):
        player.lose(self, sum(1 for log in player.get_logs('play') if log['card'].type == 'human'))
                                      
class NegativeZone(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('negative zone', 60, 'event')

        self.tag = 'cont'
        
    def start(self, game):
        for p in self.game.players:
            
            p.ongoing.append(self)
            
    def ongoing(self, player):
        for log in [log for log in player.log.copy() if log.get('d') is False]:
            
            if log['type'] == 'gp':
                
                log['lp'] = player.lose(self, log['gp'] * 2, d=True) // 2
                
                log['type'] = 'lp'
                
            elif log['type'] == 'lp':
                
                log['gp'] = player.gain(self, log['lp'] * 2, d=True) // 2
                
                log['type'] = 'gp'
                
            elif log['type'] == 'sp':
                
                log['lp'] = player.lose(self, log['sp'] * 2, d=True) // 2
                
                log['type'] = 'lp'
                
            elif log['type'] == 'rp':
                
                log['gp'] = player.gain(self, log['rp'] * 2, d=True) // 2
                
                log['type'] = 'gp'
                
            elif log['type'] == 'give':
            
                log['sp'] = player.steal(self, -log['gp'] * 2, log['target'], d=True) // 2
                
                log['type'] = 'sp'
                
class FishingTrip(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fishing trip', 61, 'event')
        
    def start(self, game):
        return
        
    def end(self, player):
        player.gain(self, sum(5 for c in player.played if c.name == 'fish'))
                    
class FutureOrb(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('future orb', 62, 'item')
        
    def can_use(self, player):  
        return len(player.unplayed) > 2
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.unplayed])
        
    def start(self, player):
        if player.unplayed:
            
            self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            player.unplayed.remove(c)
            player.unplayed.insert(0, c)

            player.use_item(self)
            
class Knife(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('knife', 63, 'equipment')
        
        self.tag = 'cont'

        self.info = [] #[pid, treasure]

        self.option1 = Textbox('equip')
        self.option2 = Textbox('draw items')
        
    def can_use(self, player):
        return True
        
    def equip(self, player):
        self.mode = 2
        
        self.cards = [log['card'].copy() for p in self.sort_players(player) for log in p.get_m_logs('dt')]
        
        self.horses.clear()
        
        player.equip(self)
            
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1 or self.mode == 2:
            
            player.new_flip(self)
        
    def start(self, player):
        self.mode = 0

        if self.game.get_event() == 'hunting season':
            
            self.start_request(player)
            
        else:
            
            self.equip(player)
            
    def select(self, player, num):
        if num:
            
            o = player.selected.pop(0)
            
            if o is self.option1:
                
                self.equip(player)
                
            elif o is self.option2:
                
                self.counter = len([c for c in player.played if c.type == 'animal'])
                
                if self.counter:
                
                    self.mode = 1
                
                    self.start_request(player)
        
    def ongoing(self, player):
        for p in self.sort_players(player):
            
            treasure = [log['card'] for log in p.get_m_logs('dt') if log['card'] not in self.cards]
            
            if treasure:
                
                self.horses.clear()

                self.horses[p.pid] = treasure[-1]
                
                self.start_request(player)
                
                return True
        
    def coin(self, player, coin):
        if self.mode == 1:
            
            if coin:
                
                player.draw_items()
                
            self.counter -= 1
            
            if self.counter:
                
                self.start_request(player)
                
            else:
            
                player.use_item(self)
                
        elif self.mode == 2:
            
            pid, c = next(iter(self.horses.items()))
            p = self.game.get_player(pid)
            
            if c in p.treasure:
            
                if coin:

                    player.take_treasure(c, p)
                    
                player.use_item(self)
                
            else:
            
                player.equip(self)
                           
class Garden(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('garden', 64, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:

            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
            
class Desert(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('desert', 65, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
                        
class Graveyard(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('graveyard', 66, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
            
class City(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('city', 67, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
                
class Farm(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('farm', 68, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
                
class Forest(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('forest', 69, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:

                    player.play_card(c, d=True)
                
class Water(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('water', 70, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name and c.name != 'fish':
                
                    player.play_card(c, d=True)
                
class Sky(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sky', 71, 'landscape')
        
        self.tag = 'cont'
        
    def ongoing(self, player):
        logs = player.get_logs('play')
        
        if logs:
            
            for log in logs:
                
                c = log['card']

                if c.habitat == self.name:
                
                    player.play_card(c, d=True)
                
class ItemFrenzy(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('item frenzy', 72, 'event')
        
    def start(self, game):
        for p in game.players:
            
            p.draw_items()
            
class MagicWand(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('magic wand', 73, 'item')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.get_spells()])
        
    def start(self, player):
        player.draw_spells()
        
        if self.game.get_event() == 'spell reverse':
            
            self.start_request(player)

        player.use_item(self)
            
    def select(self, player, num):
        if num:

            player.remove_spell(player.selected.pop(0))
            
class Sapling(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sapling', 74, 'plant', 'forest')
        
    def start_request(self, player):
        player.new_roll(self)
        
    def start(self, player):
        if player.has_landscape('forest'):
            
            player.draw_items(2)
            
        self.start_request(player)
            
    def roll(self, player, roll):
        lp = sum(roll for c in player.played if c.type == 'plant')
        
        for p in self.sort_players(player):
            
            p.lose(self, lp)
            
class Vines(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('vines', 75, 'plant', 'garden')
        
    def start(self, player):
        if player.has_landscape('garden'):
            
            player.draw_items()
            
        if any(p.get_spells() for p in self.game.players):
            
            all_spells = []

            for p in self.game.players:
                
                spells = p.get_spells()
                
                for c in spells:
                    
                    p.remove_spell(c)
                    
                all_spells.append(spells)
   
            for i in range(-1, len(all_spells) - 1):
                
                p = self.game.players[i + 1]
                
                s = all_spells[i]
                
                for c in s:
                    
                    p.add_og(c)
            
class Zombie(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('zombie', 76, 'monster', 'graveyard')
        
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if owner:
            
            i = owner.played.index(self)
            
        else:
            
            i = len(player.played)

        for p in self.sort_players(player, 'steal'):
            
            try:
                
                if p.played[i].type == 'human':
                    
                    player.steal(self, 5, p)
                    
            except IndexError:
                
                continue
                
        if player.has_spell('curse'):
            
            player.draw_items()
            player.draw_treasure()
            
class Jumble(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('jumble', 77, 'monster')
        
    def deploy(self, players):
        for p in players:
            
            horse = self.copy()
            p.new_flip(horse)
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_flip(self)
            
        elif self.mode == 1:
            
            player.new_selection(self, [c.copy() for c in player.get_items()])
        
    def start(self, player):
        if player.has_spell('item hex'):
            
            player.draw_treasure(2)
            
        self.deploy(self.sort_players(player))
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 10)
            
            self.mode = 1
            
            self.start_request(player)

    def select(self, player, num):
        if num:
            
            player.discard_item(player.selected.pop(0))
            
class DemonWaterGlass(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('demon water glass', 78, 'monster', 'water')
        
    def start_request(self, player):
        self.start(player)
        
    def start(self, player):
        player.new_selection(self, self.sort_players(player, lambda p: p.score and any(c.type == 'human' for c in p.played)))
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            sp = 10 if not p.get_spells() else 5
            
            player.steal(self, sp, p)
            
class Succosecc(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('succosecc', 79, 'monster')
        
        self.items = {} #p.pid: item
        
    def start_request(self, player):
        player.new_selection(self, list(self.items.values()))
        
    def start(self, player):
        for p in self.game.players:
            
            if p.get_items():
                
                c = random.choice(p.get_items())
                p.discard_item(c, True)
                
            else:
                
                items = self.game.draw_cards('items')
                
                if items:
                
                    c = items[0]
                    
                else:
                    
                    return
                
            self.items[p.pid] = c
                
        self.start_request(player)
                
    def select(self, player, num):
        if num:
            
            i = player.selected.pop(0)
            
            player.items.append(i)
            
            for p, c in zip([self.pid(pid) for pid in self.items.keys() if pid != player.pid], [c for c in self.items.values() if c != i]):

                p.items.append(c)
                
class Sunflower(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sunflower', 80, 'plant', 'garden')
        
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if owner:
            
            i = owner.played.index(self)
            
        else:
            
            i = len(player.played)
            
        points = 5 - i
        
        if points > 0:
            
            player.gain(self, points)
            
        elif points < 0:
            
            player.lose(self, points)
            
        if player.has_item('sunglasses'):
            
            player.draw_items(2)

class LemonLord(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('lemon lord', 70, 'plant', 'farm')
        
        self.tag = 'cont'
        
        self.counter = 1
        
    def start(self, player): 
        player.ongoing.append(self)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + self.counter
            
        try:
            
            c = owner.played[i]
            
            if c.type == 'plant':
            
                player.gain(self, 5)
                
                self.counter += 1

            else:
                
                self.counter = 0
                
        except IndexError:
            
            pass

        if self in player.played:
            
            if player.played[-1] != self: #IndexError: list index out of range

                logs = player.get_logs('ui')
                
                if player.played[-2] == self and any(log['card'].name == 'future orb' for log in logs) and player.played[-1].type == 'monster':
                    
                    player.draw_treasure()
                
            if self.counter == 0:
                
                return True
                
        else:
            
            return True
            
class Wizard(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('wizard', 71, 'human')
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [p for p in self.sort_players(player) if p.treasure])

        elif self.mode == 1:
            
            player.new_selection(self, [c.copy() for c in player.get_spells()])

    def start(self, player):
        self.mode = 0
        
        if player.has_item('treasure chest') and any(p.treasure for p in self.sort_players(player)):

            self.start_request(player)
            
        else:
            
            self.mode = 1
            
            self.start_request(player)
            
    def select(self, player, num):
        if self.mode == 0:
            
            if num:
                
                player.steal_treasure(player.selected.pop(0))
                
                player.cancel_select()
                
                self.mode = 1
                
                self.start_request(player)
                
        elif self.mode == 1:

            if num == 1:
                
                c = player.selected[0]

                player.new_selection(self, [p for p in self.sort_players(player) if p.can_cast(c.name)])
                
            elif num == 2:
                
                c, p = player.selected
                
                p.add_og(c)
                player.remove_spell(c)
                
class HauntedOak(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('haunted oak', 72, 'plant')
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player, 'steal'))
        
    def start(self, player):
        plants = len([c for c in player.played if c.type == 'plant'])
        
        if (self in player.played and plants >= 3) or (self not in player.played and plants >= 2):

            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.steal(self, 10, player.selected.pop(0))
            
class SpellReverse(Card): #casts spells without checking can_cast()
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('spell reverse', 73, 'event')
        
    def start(self, game):
        for p in game.players:
            
            for _ in range(len(p.spells)):
                
                p.ongoing.append(p.spells.pop(0))
                
class SunnyDay(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sunny day', 74, 'event')
        
    def start(self, game):
        return
            
    def end(self, player):
        player.gain(self, sum(2 for c in player.played if c.type == 'plant'))
            
class FoolsGold(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('fools gold', 75, 'treasure')
        
    def start(self, player):
        self.end(player)
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player))
        
    def end(self, player):
        if player.score:
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.give(self, 5, player.selected.pop(0))
            
class OfficeFern(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('office fern', 76, 'plant', 'city')
        
    def start(self, player):
        owner = self.game.find_owner(self)
        
        if owner:
            
            i = owner.played.index(self)
            
        else:
            
            i = len(player.played)
        
        
        lp = i + 1
        
        player.lose(self, lp)
        
class Parade(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('parade', 77, 'event')
        
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
            
            if c.type == 'human':
                
                count += 1
                
            else:
                
                self.gain(player, count)
                    
                count = 0
                
        if count:
            
            self.gain(player, count)
            
class Camel(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('camel', 78, 'animal', 'desert')
        
    def check_water(self, p):
        return any(c.habitat == 'water' for c in p.played)
        
    def count_water(self, p):
        return len([c for c in p.played if c.habitat == 'water'])
        
    def start_request(self, player):
        if self.mode == 0:
            
            m = max(len([c for c in p.played if c.habitat == 'water']) for p in self.sort_players(player)) #ValueError: max() arg is an empty sequence
            
            player.new_selection(self, [p for p in self.sort_players(player) if self.count_water(p) == m])
            
        elif self.mode == 1:
            
            player.new_flip(self)
        
    def start(self, player):
        players = [p for p in self.sort_players(player) if self.check_water(p)]
        
        if players:

            self.start_request(player)
                
        elif not self.check_water(player):
            
            self.mode = 1
            
            self.start_request(player)
                
    def select(self, player, num):
        if num:
            
            player.steal(self, 5, player.selected.pop(0))
            
    def coin(self, player, coin):
        if coin:
            
            player.draw_treasure()
            
class RattleSnake(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('rattle snake', 79, 'animal', 'desert')
        
        self.tag = 'cont'
        
        self.t_roll = None
        
        self.horses = {} #pid: horse
        
    def deploy(self, players):
        for p in players:
            
            horse = self.copy()
            horse.mode = 1
            p.new_roll(horse)
            self.horses[p.pid] = horse
        
    def start_request(self, player):
        if self.mode == 0:
        
            player.new_selection(self, [c.copy() for c in player.get_spells()])
            
        elif self.mode == 1:
            
            player.new_roll(self)
        
    def start(self, player):
        players = self.sort_players(player, lambda p: p.score and p.treasure)
        
        if len(players) > 1:

            self.deploy(players)

            player.ongoing.append(self)
            
        elif players:

            player.steal_treasure(players[0])
            
        if self.game.check_first(player) and player.get_spells():
            
            self.start_request(player)
            
    def roll(self, player, roll):
        self.t_roll = roll
            
    def select(self, player, num):
        if num:
        
            player.remove_spell(player.selected.pop(0))
        
    def ongoing(self, player):
        for pid, c in self.horses.copy().items():
            
            p = self.pid(pid)
            
            if not p.treasure:

                c.wait = None
                
                del self.horses[pid]
                
        if not self.horses:
            
            return True

        if all(c.t_roll is not None for c in self.horses.values()):
            
            m = max(c.t_roll for c in self.horses.values())
            
            players = []
            
            for pid, c in self.horses.items():
                
                p = self.pid(pid)
                
                if c.t_roll == m and p.treasure:

                    players.append(p)

            if len(players) <= 1:
                
                if players:
                
                    player.steal_treasure(players[0])
                
                return True
                
            else:
                
                self.deploy(players)
            
class TumbleWeed(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('tumble weed', 80, 'plant', 'desert')
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player, lambda p: p.get_items()))
        
    def start(self, player):
        if any(c.type == 'human' for c in player.played):
            
            player.lose(self, 10)
            
        else:
            
            player.gain(self, 5)
            
        if self.game.get_event() == 'wind gust':
            
            self.start_request(player)
            
    def select(self, player, num):
        if num == 1:
            
            p = player.selected[0]
            
            player.new_selection(self, [c.copy() for c in p.get_items()])
            
        elif num == 2:
            
            p, c = player.selected
            
            p.discard_item(c, d=True)
            
            player.items.append(c)
            
class Mummy(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mummy', 81, 'monster', 'desert')
        
    def deploy(self, players):
        for p in players:
            
            horse = self.copy()
            horse.start_request(p)
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.get_items()])
        
    def start(self, player):
        self.deploy(self.sort_players(player, lambda p: p.get_items()))
        
        if player.has_spell('mummys curse'):
            
            for p in self.sort_players(player):
                
                p.lose(self, len(p.get_items() + p.spells) * 2)
                
    def select(self, player, num):
        if num:
            
            c = player.selected.pop(0)
            
            player.discard_item(c)
            
class Pig(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('pig', 82, 'animal', 'farm')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_selection(self, self.sort_players(player, lambda p: p.treasure))
        
    def start(self, player):
        self.counter = 0
        
        if self.game.check_last(player):
            
            self.start_request(player)
            
        player.add_og(self)
        
    def select(self, player, num):
        if num:
            
            player.steal_treasure(player.selected.pop(0))
            
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + self.counter + 1
        
        try:
            
            c = owner.played[i]

            if c.type == 'plant':
                
                gp = 10 if c.habitat == 'farm' else 2
                
                player.gain(self, gp)
                
                self.counter += 1
                
            else:
                
                return True
                
        except IndexError:
            
            return
            
class Corn(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('corn', 83, 'plant', 'farm')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.get_items()])
        
    def start(self, player):
        player.add_og(self)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            c = owner.played[i]
            
            if c.type == 'human':
                
                player.gain(self, 10)
                
            else:
                
                self.start_request(player)
                
            return True
            
        except IndexError:
            
            return
            
    def select(self, player, num):
        if num == 1:
            
            player.new_selection(self, self.sort_players(player))
            
        elif num == 2:
            
            c, p = player.selected
            
            player.discard_item(c, d=True)
            
            p.items.append(c)
        
class Bear(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('bear', 84, 'animal', 'forest')
        
    def start(self, player):
        sp = 4 if self.game.get_event() == 'parade' else 2
        
        for p in self.sort_players(player, 'steal'):
            
            player.steal(self, sum(sp for c in p.played if c.type == 'human'), p)
            
class WaterLilly(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('water lilly', 85, 'plant', 'water')
        
    def start(self, player):
        player.gain(self, (len(player.get_items() + player.spells) * 2) + len(player.get_spells()))
        
class Bat(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('bat', 86, 'animal', 'sky')
        
        self.option1 = Textbox('draw item')
        self.option2 = Textbox('draw spell')
        
    def start_request(self, player):
        self.start(player)
        
    def start(self, player):
        player.new_flip(self)
        
    def coin(self, player, coin):
        if coin:
            
            player.new_selection(self, self.sort_players(player, lambda p: p.treasure))
            
        else:
            
            self.mode = 1
            
            player.new_selection(self, [self.option1, self.option2])
            
    def select(self, player, num):
        if self.mode == 0:
            
            if num:
                
                player.steal_treasure(player.selected.pop(0))
                
        elif self.mode == 1:
            
            if num:
                
                o = player.selected.pop(0)
                
                if o is self.option1:
                    
                    player.draw_items()
                    
                elif o is self.option2:
                    
                    player.draw_spells()
        
class SkyFlower(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sky flower', 87, 'plant', 'sky')
        
    def start_request(self, player):
        if self.mode == 0:
        
            m = min(p.score for p in self.sort_players(player))
            
            if m:
            
                player.new_selection(self, [p for p in self.sort_players(player) if p.score == m])
            
        elif self.mode == 1:
            
            player.new_roll(self)
        
    def start(self, player):
        self.start_request(player)
        
        if player.has_item('kite'):
            
            c = self.copy()
            
            c.mode = 1
            
            c.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.give(self, 7, player.selected.pop(0))
            
            player.draw_treasure()
            
    def roll(self, player, roll):
        player.gain(self, roll)
        
class GardenSnake(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('garden snake', 88, 'animal', 'garden')
        
        self.tag = 'cont'
        
    def start_request(self, player):
        player.new_roll(self)
        
    def start(self, player):
        player.add_og(self)
        
    def roll(self, player, roll):
        player.gain(self, roll)
        
    def ongoing(self, player):
        owner = self.game.find_owner(self)
        
        i = owner.played.index(self) + 1
        
        try:
            
            c = owner.played[i]
            
            if player.has_landscape(c.habitat):
                
                self.start_request(player)
                
            return True
            
        except IndexError:
            
            return
            
class MummysCurse(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('mummys curse', 89, 'spell')

        self.tag = 'play'
        
    def start_request(self, player):
        self.ongoing(player)
        
    def ongoing(self, player):
        player.new_flip(self)
        
    def coin(self, player, coin):
        if coin:
            
            player.new_selection(self, [c.copy() for c in player.played if c.type == 'human'])
            
        else:
            
            player.lose(self, 5)
            
    def select(self, player, num):
        if num:
            
            player.play_card(player.selected.pop(0))
            
class Stardust(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('stardust', 90, 'spell')

        self.tag = 'cont'
        
        self.cards = self.get_log() #list of cards
        
        self.mult = False
        
    def get_log(self):
        treasure = []
        
        for p in self.game.players:
            
            treasure += [log['card'] for log in p.get_m_logs('dt')]
            
        return treasure
        
    def start_request(self, player):
        player.new_flip(self)
        
    def ongoing(self, player):
        for p in self.sort_players(player):
            
            treasure = [log['card'] for log in p.get_m_logs('dt') if log['card'] not in self.cards]
            
            self.cards += treasure
            
            self.counter += len(treasure)
            
        while self.counter:
            
            c = self.copy()
            
            c.start_request(player)
            
            self.counter -= 1
                
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 5)
            
        else:
            
            player.lose(self, 5)
            
class NorthWind(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('north wind', 91, 'spell')

        self.tag = 'play'
        
        self.mult = False
        
    def start_request(self, player):
        player.new_flip(self)

    def ongoing(self, player):
        if len(player.get_spells()) > 1:
        
            self.start_request(player)
        
    def coin(self, player, coin):
        if coin:
            
            player.gain(self, 2 * sum(1 for c in player.get_spells() if c is not self))
            
class WindGust(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('wind gust', 92, 'event')
        
    def start(self, game):
        sequences = [p.unplayed.copy() for p in game.players]
        
        for i in range(-1, len(sequences) - 1):
            
            p = game.players[i]
            
            s = sequences[i + 1]
            
            p.unplayed = s
            
class SandStorm(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sand storm', 93, 'event')
        
        self.tag = 'play'

    def start_request(self, player):
        player.new_flip(self)
        
    def start(self, game):
        for p in game.players:

            p.ongoing.append(self)
            
    def ongoing(self, player):
        if self.game.check_last(player) and any(p.get_spells() for p in self.game.players):
            
            self.start_request(player)
            
    def coin(self, player, coin):
        if coin:
            
            self.rotate_spells()
            
    def rotate_spells(self):
        all_spells = []

        for p in self.game.players:
            
            spells = p.get_spells()
            
            for c in spells:
                
                p.remove_spell(c)
                
            all_spells.append(spells)
  
        for i in range(-1, len(all_spells) - 1):
            
            p = self.game.players[i + 1]
            
            s = all_spells[i]
            
            for c in s:
                
                p.add_og(c)
        
class HuntingSeason(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('hunting season', 94, 'event')

        self.tag = 'cont'
        
    def start(self, game):
        for p in game.players:
            
            p.ongoing.append(self)
        
    def start_request(self, player):
        player.new_flip(self)
        
    def ongoing(self, player):
        animals = [log['card'].copy() for log in player.get_logs('play') if log['card'].type == 'animal' and log['card'] not in self.cards] #maybe change
        
        for _ in range(len(animals)):
            
            cop = self.copy()
            
            cop.start_request(player)
            
            self.cards.append(cop)
            
    def coin(self, player, coin):
        if not coin:
            
            player.lose(self, 2)
            
class Harvest(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('harvest', 95, 'event')
            
    def start(self, game):
        return
        
    def end(self, player):
        for c in player.played:
            
            if c.type == 'plant':
                
                gp = 5 if player.has_landscape(c.habitat) else 2
                
                player.gain(self, gp)
            
class GoldenEgg(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('golden egg', 96, 'treasure')
        
    def end(self, player):
        player.gain(self, sum(1 for c in player.played if c.type == 'animal'))
        
class MagicBean(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('magic bean', 97, 'treasure')
        
    def end(self, player):
        player.gain(self, sum(1 for c in player.played if c.type == 'plant'))
        
class LuckyCoin(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('lucky coin', 98, 'item')
        
        self.tag = 'cont'
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, self.game.players.copy())
        
    def start(self, player):
        self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            player.use_item(self)
            
            p.add_og(self)

    def ongoing(self, player):
        if player.flipping:
        
            player.coin = 1
            
            self.mode = 1
            
        if self.mode == 1 and player.get_logs('cf'):

            return True
                
class Sunglasses(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('sunglasses', 99, 'equipment')
        
        self.tag = 'cont'

        self.t_coin = None
        
        self.option1 = Textbox('equip')
        self.option2 = Textbox('repeat human')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
        
        elif self.mode == 1:
            
            player.new_flip(self)
            
        elif self.mode == 2:
            
            player.new_selection(self, [c.copy() for c in player.played if c.type == 'human'])
            
    def start(self, player):
        self.horses.clear()
        
        if self.game.get_event() == 'sunny day' and any(c.type == 'human' for c in player.played):
            
            self.mode = 0
            
            self.start_request(player)
            
        elif not any(c.name == self.name for c in player.equipped):
            
            player.equip(self)
            
    def select(self, player, num):
        if self.mode == 0:
            
            if num:
            
                o = player.selected.pop(0)
                
                if o is self.option1:
                    
                    player.equip(self)
                    
                elif o is self.option2:
                    
                    self.mode = 2

                    self.start_request(player)
                
        elif self.mode == 2:
            
            player.play_card(player.selected.pop(0), d=True)
            
            player.use_item(self)
            
    def coin(self, player, coin):
        self.t_coin = coin
            
    def ongoing(self, player):
        if not self.horses:
        
            logs = player.get_logs('rp')
            
            if logs:
                
                p, rp = logs[-1]['robber'], logs[-1]['rp']
                
                c = self.copy()
                
                c.mode = 1
                
                p.new_flip(c)
                
                self.horses[p.pid] = c
                self.counter = rp
                
        elif list(self.horses.values())[0].t_coin is not None:
            
            pid, c = next(iter(self.horses.items()))
            p = self.pid(pid)
            sp = self.counter
            
            if not c.t_coin:

                player.steal(self, sp, p, d=True)
   
            player.use_item(self)
            
class MetalDetector(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('metal detector', 100, 'item')
        
        self.option1 = Textbox('roll')
        self.option2 = Textbox('get last\n item')
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1:
            
            player.new_roll(self)
            
    def start(self, player):
        self.mode = 0
        
        if player.has_landscape('desert'):
            
            self.start_request(player)
            
        else:
            
            self.mode = 1
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            o = player.selected.pop(0)
            
            if o is self.option1:
                
                self.mode = 1
                
                self.start_request(player)
                
            elif o is self.option2:
                
                c = self.game.get_last_item()
                
                self.game.restore(c)
                
                player.items.append(c)
                
                player.use_item(self)
                
    def roll(self, player, roll):
        if roll in (1, 2, 3):
            
            player.draw_items()
            
        elif roll in (4, 5):
            
            player.draw_spells()
            
        elif roll == 6:
            
            player.draw_treasure()
            
        player.use_item(self)
                    
class BigRock(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('big rock', 101, 'item')
        
    def can_use(self, player):
        return len(player.unplayed) > 2
        
    def start_request(self, player):
        player.new_selection(self, [c.copy() for c in player.unplayed])
        
    def start(self, player):
        if len(player.unplayed) >= 2:
            
            self.start_request(player)
            
    def select(self, player, num):
        if num == 1:
            
            player.new_selection(self, [c for c in player.selection if c not in player.selected])
            
        elif num == 2:
            
            c1, c2 = player.selected
            
            self.game.swap(c1, c2)
            
            player.use_item(self)
            
class UnluckyCoin(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('unlucky coin', 102, 'item')
        
        self.tag = 'cont'
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_selection(self, self.game.players.copy())
        
    def start(self, player):
        self.start_request(player)
        
    def select(self, player, num):
        if num:
            
            p = player.selected.pop(0)
            
            player.use_item(self)
            
            p.add_og(self)

    def ongoing(self, player):
        if player.tf != 0:
        
            player.coin = 0
            
            if player.get_logs('cf'):
                
                return True
            
class Torpedo(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('torpedo', 103, 'equipment')

        self.tag = 'cont'
        
    def can_use(self, player):
        return True
        
    def start_request(self, player):
        player.new_flip(self)
        
    def start(self, player):
        self.pids.clear()
        
        player.equip(self)
        
    def coin(self, player, coin):
        if coin:
            
            pid, sp = self.pids
            p = self.pid(pid)
            
            player.steal(self, sp, p, d=True)
            
        player.use_item(self)

    def ongoing(self, player):
        logs = player.get_logs('sp')
        
        if logs:

            self.pids = [logs[-1]['target'].pid, logs[-1]['sp']]
            
            self.start_request(player)
            
            return True

class Kite(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('kite', 104, 'item')
        
    def can_use(self, player):
        return [c.copy() for p in self.sort_players(player) for c in p.played if player.has_landscape(c.habitat) and p.played.index(c) >= len(player.played) and c.type in ('plant', 'animal')]
        
    def start_request(self, player):
        player.new_selection(self, self.cards.copy())
        
    def start(self, player):
        self.cards = [c.copy() for p in self.sort_players(player) for c in p.played if player.has_landscape(c.habitat) and p.played.index(c) >= len(player.played) and c.type in ('plant', 'animal')]
        
        if self.cards:
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.play_card(player.selected.pop(0), d=True)
            
            player.use_item(self)
        
class Balloon(Card): #stuck in loop
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('balloon', 105, 'equipment')
        
        self.tag = 'cont'
        
        self.option1 = Textbox('equip')
        self.option2 = Textbox('flip for treasure')
        
    def can_use(self, player):
        return True
        
    def equip(self, player):
        self.mode = 2
        
        self.cards = [log['card'] for p in self.sort_players(player) for log in p.get_m_logs('di')]
        
        player.equip(self)
            
    def start_request(self, player):
        if self.mode == 0:
            
            player.new_selection(self, [self.option1, self.option2])
            
        elif self.mode == 1:
            
            player.new_flip(self)
        
    def start(self, player):
        self.mode = 0

        if player.has_spell('north wind'):
            
            self.start_request(player)
            
        else:
            
            self.equip(player)
            
    def select(self, player, num):
        if num:
            
            o = player.selected.pop(0)
            
            if o is self.option1:
                
                self.equip(player)
                
            elif o is self.option2:
                
                self.mode = 1
                
                self.start_request(player)
        
    def ongoing(self, player):
        for p in self.sort_players(player):
            
            items = [log['card'] for log in p.get_m_logs('di') if log['card'] not in self.cards and log['card'] in p.get_items()]
            
            if items:
                
                c = items[-1]

                p.discard_item(c) #could replicate items
                
                player.items.append(c)
                
                player.use_item(self)
                
                return
        
    def coin(self, player, coin):
        if coin:
            
            player.draw_treasure()
            
        player.draw_treasure()
        
        player.use_item(self)
        
class WateringCan(Card):
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        super().__init__('watering can', 105, 'item')
        
    def can_use(self, player):
        return [c.copy() for p in self.sort_players(player) for c in p.played if p.played.index(c) >= len(player.played) and c.type == 'plant']
        
    def start_request(self, player):
        player.new_selection(self, self.cards.copy())
            
    def start(self, player):
        self.cards = [c.copy() for p in self.sort_players(player) for c in p.played if p.played.index(c) >= len(player.played) and c.type == 'plant']
        
        if self.cards:
            
            self.start_request(player)
            
    def select(self, player, num):
        if num:
            
            player.play_card(player.selected.pop(0), d=True)
            
            player.use_item(self)
        
        
        
        