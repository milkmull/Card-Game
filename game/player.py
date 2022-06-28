import random
import time

from . import player_base

class Player(player_base.Player_Base):
    def __init__(self, game, pid, player_info):
        super().__init__(game, pid)
        
        self.player_info = player_info
        self.set_name()
        self.name = self.player_info['name']

        self.max = 60
        self.ft = 0
        self.rt = 0

    def is_auto(self):
        return isinstance(self, Auto_Player)

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

    def reset(self):
        super().reset()
        self.ft = 0
        self.rt = 0

    def start(self):
        super().start()
        self.max = 30 * len([p for p in self.game.players if not p.is_auto()]) * 2
 
#card stuff-------------------------------------------------------------------------------------- 
                
    def new_deck(self, deck, cards):
        setattr(self, deck, cards)
        self.add_log({'t': 'nd', 'deck': deck, 'cards': cards.copy()})
        
    def discard_card(self, c, add_to_discard=True): 
        super().discard_card(c, add_to_discard=add_to_discard)
        if add_to_discard:
            self.add_log({'t': 'disc', 'c': c, 'tags': c.tags}) #maybe change in the future
    
#vote stuff------------------------------------------------------------------------------------

    def set_vote(self, vote):
        self.vote = vote
        self.add_log({'t': 'v', 'v': vote})

#request stuff--------------------------------------------------------------------------------------

    def ready_coin(self):
        self.coin = -1
        self.ft = self.max
        
    def ready_dice(self):
        self.dice = -1
        self.rt = self.max

    def set_active_card(self, c):
        self.active_card = c
        self.add_log({'t': 'aac', 'c': c, 'w': c.wait, 'cancel': self.can_cancel()})
        
    def remove_active_card(self):
        self.active_card = None
        self.add_log({'t': 'rac'})
        
    def process_request(self):
        self.requests.sort(key=Player.sort_request_cards)
        c = self.requests[0]
        if c is not self.active_card:
            self.cancel_request()
            self.start_request(c)
            self.set_active_card(c)
  
        confirm = False

        if c.wait == 'flip' and not self.ft:
            if self.coin is not None:
                c.wait = None
                c.flip(self, self.coin)
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

#turn stuff-----------------------------------------------------------------------------------------

    def end_round(self, end_all):
        if hasattr(self.game.event, 'end'):
            self.game.event.end(self)
        if end_all:
            for c in self.played + self.active_spells + self.treasure:
                if hasattr(c, 'end'):
                    c.end(self)
        self.game_over = True

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

#point stuff-----------------------------------------------------------------------------------------
 
    def update_score(self, score):
        self.score = score
        self.add_log({'t': 'score', 'score': self.score})
        
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
        
    def reset(self):
        super().reset()
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
            temp_tree = [info[0] for info in self.tree][:3]
        if temp_tree == self.temp_tree:
            self.stable_counter += 1
        else:
            print(self.temp_tree)
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
            return round(max(((1 / 60) - total_update_time) / players, 0), 5)
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
        return super().get_selection()
     
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
        
    def start_request(self, c):
        sel = self.selection.copy()
        super().start_request(c)
        if not self.selecting or (self.selecting and self.selection != sel):
            self.set_timer()

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
        
class Player_Copy(player_base.Player_Base):
    def __init__(self, game, p):
        super().__init__(game, p.pid)
        
        self.player = p
        
        self.name = p.name
        
        self.score = p.score
        self.vote = p.vote
        
        self.selecting = p.selecting
        self.gone = p.gone
        self.flipping = p.flipping
        self.rolling = p.rolling      
        self.game_over = p.game_over
        self.invincible = p.invincible

        self.coin = p.coin
        self.dice = p.dice
        
        self.master_log = p.master_log.copy()
        self.log = p.log.copy()

        self.first_choice = None
        
    def set_cards(self):
        self.played = [c.sim_copy(self.game) for c in self.player.played]
        self.unplayed = [c.light_sim_copy(self.game) for c in self.player.unplayed]
        
        self.items = [c.light_sim_copy(self.game) for c in self.player.items]
        self.equipped = [c.sim_copy(self.game) for c in self.player.equipped]

        self.spells = [c.light_sim_copy(self.game) for c in self.player.spells]
        self.active_spells = [c.sim_copy(self.game) for c in self.player.active_spells]
        
        self.treasure = [c.light_sim_copy(self.game) for c in self.player.treasure]
        self.landscapes = [c.sim_copy(self.game) for c in self.player.landscapes]
        
        self.selection = [c.sim_copy(self.game) for c in self.player.selection]
        self.selected = [c.sim_copy(self.game) for c in self.player.selected]
        
        self.ongoing = [c.sim_copy(self.game) for c in self.player.ongoing]
        self.active_og = [c.sim_copy(self.game) for c in self.player.active_og]
        
        self.requests = [c.sim_copy(self.game) for c in self.player.requests]
        self.active_card = next(iter([c for c in self.requests if c == self.player.active_card]), None)  

#auto stuff-----------------------------------------------------------------------------------------

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
        