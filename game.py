import random
import json
import importlib
import save
import func
import new_card
from player import Player

def reload():
    importlib.reload(new_card)

class InfiniteLoop(Exception):
    pass

def pack_log(logs):
    new_log = []
    
    for log in logs:

        new_entry = {}
        
        for key in log:
            
            val = log[key]
            
            if isinstance(val, Player):
                new_entry[key] = val.pid
                
            elif hasattr(val, 'uid'):
                new_entry[key] = (val.name, val.uid)
                
            elif isinstance(val, list):
                new_list = []
                
                for i in val:
                    
                    if hasattr(i, 'get_id'):
                        new_list.append([i.name, i.get_id()])   
                    else:   
                        new_list.append(i)
                        
                new_entry[key] = new_list

            else:
                new_entry[key] = val
                
        new_log.append(new_entry)
                
    return new_log
    
def sort_logs(log):
    u = log.get('u')
    
    if u == 'g':
        return -1
    else:
        return u
    
def blank_player_info(pid):
    return {'name': f'player {pid}', 'description': '', 'tags': ['player'], 'image': 'img/user.png'}
  
def get_card_data():
    with open('save/cards.json', 'r') as f:
        data = json.load(f)
    return data
  
class Game:
    def __init__(self, mode='online', cards=None):
        self.running = True
        
        self.settings = save.get_data('settings')
        if cards is not None:
            self.cards = cards
        else:
            self.cards = get_card_data()
        
        self.uid = 0
        self.pid = 0

        self.shop = []

        self.discard = []
        
        self.log = []
        self.master_log = []
        self.logs = {}
        self.frame = 0
        
        self.mem = []
        self.counter = 0

        self.turn = 0
        self.current_turn = 0
        self.round = 0
        
        self.end_timer = 0

        self.event = None
        
        self.players = []
        self.current_player = 0
        self.main_p = None

        self.mode = mode
        self.status = ''
        self.new_status('waiting')

        if self.mode == 'single':
            player_info = save.get_data('cards')[0]
            player_info['name'] = save.get_data('username')
            self.new_player(0, player_info)
            self.add_cpus()

    def done(self):
        return self.status in ('new game', 'next round')
            
#copy stuff---------------------------------------------------------------------------------------------------

    def copy(self):
        g = Game(mode='turbo')
        
        g.uid = self.uid
        
        g.settings = self.settings.copy()
        g.cards = self.cards.copy()

        g.turn = self.turn
        g.current_turn = self.current_turn
        g.round = self.round
        
        g.end_timer = self.end_timer

        g.current_player = self.current_player

        g.status = self.status
        
        g.players = [Player(g, p.pid, p.score, p.get_info(), auto=True) for p in self.players]
        g.main_p = g.players[g.current_player]
            
        for i in range(len(self.players)):
            g.players[i].start_copy(g, self.players[i])

        g.discard = [c.light_sim_copy(g) for c in self.discard[:3]]
        
        g.event = self.event.light_sim_copy(g) if self.event is not None else None
            
        return g
        
#new game stuff-----------------------------------------------------------------------------------------------

    def new_game(self):
        self.clear_logs()
        self.frame = 0
        self.add_log({'t': 'res'})
        
        if self.mode == 'single':
            
            self.players = [self.get_player(0)]
            self.players[0].reset()
            
            self.add_cpus()
            
        else:
            
            for p in self.players: 
                p.reset()
     
        self.shuffle_players()
        self.current_player = 0
        self.main_p = self.players[0] 

        self.uid = len(self.players)
        
        for p in self.players:
            p.start()

        self.new_status('playing')
        
        self.turn = 0
        self.current_turn = 0
        self.round = 1
        self.update_round()
        
        self.end_timer = 0

        self.mem.clear()
        self.counter = 0

        self.discard.clear()
        
        self.restock_shop()

        self.event = self.draw_cards('events', 1)[0]
        self.event.start(self)
        self.add_log({'t': 'se', 'c': self.event.copy()})
            
        self.main_p.start_turn()
        self.add_log({'t': 'nt', 'pid': self.main_p.pid})

    def new_round(self):
        self.clear_logs()
        self.frame = 0
        self.add_log({'t': 'nr'})
        
        self.shuffle_players() 
        self.current_player = 0
        self.main_p = self.players[0]

        for p in self.players:
            p.new_round()

        self.new_status('playing')
        
        self.turn = 0
        self.current_turn = 0
        
        self.end_timer = 0
        
        self.round += 1
        self.update_round()
        
        self.restock_shop()

        self.event = self.draw_cards('events', 1)[0]
        self.event.start(self)
        self.add_log({'t': 'se', 'c': self.event.copy()})
            
        self.main_p.start_turn()
        self.add_log({'t': 'nt', 'pid': self.main_p.pid})
 
    def reset(self):
        self.new_status('waiting')
        for p in self.players: 
            p.reset()   
        self.add_log({'t': 'res'})
 
    def start(self, pid):
        if (pid == 0 and len(self.players) > 1) or self.mode == 'single':
            self.new_game()
            
    def isinit(self):
        return any(p.is_turn for p in self.players)
 
#player stuff ------------------------------------------------------------------------
 
    def get_pid(self):
        return 0
 
    def add_cpus(self):
        self.pid = 1

        for _ in range(self.get_setting('cpus')):  
            player_info = blank_player_info(self.pid)
            p = Player(self, self.pid, self.get_setting('ss'), player_info, auto=True)
            self.players.append(p)      
            self.add_log({'t': 'add', 'pid': p.pid})
            self.pid += 1
            
    def new_player(self, pid, player_info):
        if self.status == 'waiting':

            p = Player(self, pid, self.settings['ss'], player_info)
            self.players.append(p)  
            
            if pid == 0:
                self.main_p = p
                
            self.pid += 1
            
            self.add_log({'t': 'add', 'pid': pid})
            self.logs[pid] = self.get_startup_log()

            if len(self.players) > 1:
                self.new_status('start')

            return True
            
        else:
        
            return False
            
    def remove_player(self, pid):
        p = self.get_player(pid)
        
        if p:

            if p.pid in self.logs:
                del self.logs[p.pid]
            
            self.players.remove(p)
            self.add_log({'t': 'del', 'pid': p.pid})
            
            if self.mode == 'online':
                if self.status == 'playing':
                    self.reset()
                if len(self.players) == 1:
                    self.new_status('waiting')

    def balance_cpus(self):
        players = sorted(self.players, key=lambda p: p.pid, reverse=True)

        dif = (len(self.players) - 1) - self.get_setting('cpus')
        
        if dif > 0:
            
            for i in range(dif):
                
                p = players[i]
                self.remove_player(p.pid)
                
        elif dif < 0:
            
            for p in self.players.copy():
                
                if p.auto:
                    
                    self.remove_player(p.pid)
                    
            self.add_cpus()
   
    def get_player(self, pid):
        return next((p for p in self.players if p.pid == pid), None)

    def check_last(self, player):
        return all(len(p.played) > len(player.played) for p in self.players if p is not player)
        
    def check_first(self, player):
        return all(len(p.played) <= len(player.played) for p in self.players)
        
    def shift_up(self, player):
        self.players.remove(player)
        self.players.insert(0, player)
        self.current_player = self.players.index(self.main_p)
                
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shift_down(self, player):
        self.players.remove(player)
        self.players.append(player)
        self.current_player = self.players.index(self.main_p)
                
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})
        
    def shuffle_players(self):
        random.shuffle(self.players)
        self.add_log({'t': 'ord', 'ord': [p.pid for p in self.players]})

#card stuff---------------------------------------------------------------------------------------
     
    def get_new_uid(self):
        uid = self.uid
        self.uid += 1
        return uid
     
    def draw_cards(self, deck='play', num=1):
        deck = self.cards[deck]
        weights = [val['weight'] for val in deck.values()]
        
        cards = random.choices(list(deck.keys()), weights=weights, k=num)
        
        for i, card in enumerate(cards):
            cards[i] = self.get_card(card)

        return cards
        
    def get_card(self, name, uid=None):
        if uid is None:
            uid = self.get_new_uid()
        for deck in self.cards.values():
            info = deck.get(name)
            if info is not None:  
                if info.get('custom'):
                    card = getattr(new_card, info['init'])(self, uid)
                else:
                    card = getattr(func, info['init'])(self, uid)
                return card
            
    def transform(self, c1, name):
        c2 = self.get_card(name, uid=c1.uid)
        owner = self.find_owner(c1)
        if owner and c2:
            owner.replace_card(c1, c2) 
        return c2
                   
    def swap(self, c1, c2):
        self.transform(c1, c2.name)
        self.transform(c2, c1.name)
       
    def find_card_deep(self, card):
        for p in self.players:
        
            for i, c in enumerate(p.unplayed):
                if c == card:
                    return (p, 'unplayed', i)
                    
            for i, c in enumerate(p.played):
                if c == card:
                    return (p, 'played', i)
    
            for i, c in enumerate(p.equipped):
                if c == card:
                    p.unequip(c)
                    
            for i, c in enumerate(p.items):
                if c == card:
                    return (p, 'items', i)
                    
            for i, c in enumerate(p.spells):
                if c == card:
                    return (p, 'spells', i)
                    
            for i, c in enumerate(p.landscapes):
                if c == card:
                    return (p, 'landscapes', i)
                 
    def find_card(self, player, uid):
        for c in player.played + player.unplayed + player.active_spells + player.items + player.spells + player.treasure + player.equipped + player.selection + player.landscapes:  
            if c.get_id() == uid:
                
                return c
   
    def find_owner(self, c):
        p = None
        for p in self.players:
            if p.find_card_deck(c):
                return p
        
    def get_discarded_items(self):
        return [c.copy() for c in self.discard if 'item' in c.tags or 'equipment' in c.tags]
        
    def get_discard(self):
        return self.discard.copy()
        
    def check_exists(self, uid):
        return any(self.find_card(p, uid) for p in self.players)
        
    def restore(self, c):
        restored = False
        if c in self.discard:
            self.discard.remove(c)
            restored = True
        return restored
            
    def get_last_item(self):
        i = self.get_discarded_items()
        
        if not i: 
            i = self.draw_cards('items')[0]   
        else:
            i = i[0]
            
        return i.copy()
    
    def get_event(self):
        return self.event.name if hasattr(self, 'event') else None
    
    def is_event(self, name):
        if hasattr(self, 'event'):
            return self.event.name == name 
  
#shop stuff---------------------------------------------------------------------------------------
        
    def fill_shop(self, m=3):
        num = max(m - len(self.shop), 0)
        cards = []
        
        decks = ('play', 'items', 'spells')
        
        for _ in range(num):
            
            deck = random.choice(decks)
            cards += self.draw_cards(deck)
            
        self.shop += cards
        
        self.add_log({'t': 'fill', 'cards': self.shop.copy()})

    def restock_shop(self):
        self.shop.clear()
        self.fill_shop()
            
    def buy(self, player, uid):
        for c in self.shop.copy():
            
            if c.uid == uid:
                
                self.shop.remove(c)
                self.fill_shop()
                
                return c
                
#log stuff--------------------------------------------------------------------------------------------------

    def get_scores(self):
        return {p.pid: p.score for p in self.players}

    def add_log(self, log):
        log['u'] = 'g'
        log['frame'] = self.frame
        self.log.append(log)

    def clear_logs(self):
        for key in self.logs:
            self.logs[key].clear()
                
        self.log.clear()
        self.master_log.clear()

    def get_info(self, pid):
        p = self.get_player(pid)
        
        logs = self.logs[pid][:6]
        
        if logs:
            info = pack_log(logs)
            self.logs[pid] = self.logs[pid][6:]
        else:
            info = logs

        return info
                
    def update_game_logs(self):
        for key in self.logs:
            
            self.logs[key] += self.log
            self.logs[key].sort(key=sort_logs)
            
        self.master_log += self.log
        self.log.clear()
        
    def update_player_logs(self, pid):
        p = self.get_player(pid)
        
        for key in self.logs:
            sublog = self.logs[key]
            sublog += p.log
            
        p.log.clear()
        
    def get_startup_log(self):
        logs = []
        logs.append({'u': 'g', 't': 'ns', 'stat': 'waiting'})
        logs.append({'u': 'g', 't': 'set', 'settings': self.get_settings()})
        
        for p in self.players:
            logs.append({'u': p.pid, 't': 'add', 'pid': p.pid})
            logs.append({'u': p.pid, 't': 'cn', 'pid': p.pid, 'name': p.name})
            
        logs.append({'u': 'g', 't': 'ord', 'ord': [p.pid for p in self.players]})

        for log in logs:
            log['frame'] = self.frame

        return logs

#update info stuff---------------------------------------------------------------------------------------
 
    def update_round(self):
        text = f"round {self.round}/{self.get_setting('rounds')}"
        
        self.add_log({'t': 'ur', 's': text})
            
    def new_status(self, stat):
        self.status = stat
        
        self.add_log({'t': 'ns', 'stat': stat})

    def is_status(self, stat):
        return self.status == stat

    def update_player(self, pid, cmd=''):
        p = self.get_player(pid)
   
        p.update(cmd)
            
    def check_loop(self):
        up = []
        
        for p in self.players:
            up += p.played
            
        if up == self.mem:
            self.counter += 1
            
        else:
            self.mem = up
            self.counter = 0
 
        if (self.mode == 'turbo' and self.counter > 100) or (not self.mode != 'turbo' and self.counter > 9999):
            #print(self.main_p.ongoing, self.main_p.requests, self.main_p.active_card)
            raise InfiniteLoop
          
    def send(self, data):
        reply = ''
        
        if not data:        
            return
            
        else:
            
            if data == 'disconnect':
                return
            
            if data == 'pid':            
                reply = 0

            elif data == 'info':
                self.update_player(0)
                self.main()
                reply = self.get_info(0)
                
            elif data.startswith('name'):
                reply = self.get_player(0).set_name(data[5:])
            
            elif data == 'start':
                self.start(0)
                reply = 1
                
            elif data == 'reset':
                self.reset()
                reply = 1
                
            elif data == 'continue':
                status = self.status
                if status == 'next round':
                    self.new_round()  
                elif status == 'new game': 
                    self.new_game()
                reply = 1
                
            elif data == 'play':
                if self.status == 'playing':
                    self.update_player(0, 'play')    
                reply = 1
                
            elif data == 'cancel':
                if self.status == 'playing':
                    self.update_player(0, 'cancel')    
                reply = 1
                
            elif data.isdigit():
                self.update_player(0, f'select {data}')
                reply = 1

            elif data == 'flip':
                if self.status == 'playing':
                    self.update_player(0, 'flip')        
                reply = 1
                
            elif data == 'roll':
                if self.status == 'playing':
                    self.update_player(0, 'roll')   
                reply = 1

            elif data == 'settings':
                reply = self.get_settings()
                    
            elif data == 'us':
                self.update_settings()
                reply = 1

        return reply
        
    def recieve_player_info(self, pid):
        p = self.get_player(pid)
        return p.get_info()
                     
#settings stuff---------------------------------------------------------------------------------------

    def get_active_names(self):
        card_names = [name for deck in self.cards for name in self.cards[deck]]
        player_names = [p.name for p in self.players]
        return card_names + player_names

    def get_settings(self):
        return self.settings.copy()
        
    def get_setting(self, setting):
        return self.settings[setting]
        
    def update_settings(self):
        save.reload_save()
        self.settings = save.get_data('settings')  
        if self.mode == 'single':
            self.balance_cpus()
        self.add_log({'t': 'set', 'settings': self.get_settings()})

#turn stuff-----------------------------------------------------------------------------------------------
   
    def main(self):
        if self.status != 'waiting':
            for p in self.players:
                if p.auto: 
                    p.auto_update()
      
        if self.mode != 'turbo':            
            self.update_game_logs()  
        else:
            self.master_log += self.log
            self.log.clear()
        self.frame += 1
            
        self.check_loop()

    def rotate_cards(self):
        selections = []

        for p in self.players:
            selections.append(p.unplayed)  
        selections.insert(0, selections.pop(-1))
            
        for p, s in zip(self.players, selections):
            p.new_deck('unplayed', s)
                
    def advance_turn(self):
        if self.status != 'playing':
            return 
            
        all_done = all(p.finished_game() for p in self.players)
            
        if all_done:
            self.end_timer += 1
            
        if self.end_timer > 2:

            if all(p.game_over for p in self.players):

                if not self.done():
                    
                    if self.round <= self.get_setting('rounds') - 1: 
                        self.new_status('next round')   
                    else:
                        self.new_status('new game')
                        
                    self.add_log({'t': 'fin', 'w': self.get_winners()})
                    
            else: 
                for p in self.players:
                    p.end_game(not (self.round % self.get_setting('rounds')))
                    
            return  
            
        elif self.main_p.finished_turn() and not all_done:
            self.find_turn()
            
    def find_turn(self):
        if any(p.unplayed for p in self.players):
            
            self.main_p.end_turn()
            
            while True:  
                
                self.current_player = (self.current_player + 1) % len(self.players)
                self.current_turn = (self.current_turn + 1) % len(self.players)
                p = self.players[self.current_player]

                if self.current_turn == 0:
                    self.rotate_cards()
                
                if p.unplayed:
                    break

            self.main_p = self.players[self.current_player]
            self.main_p.start_turn()
            
            self.add_log({'t': 'nt', 'pid': self.main_p.pid})
            
            self.turn += 1
            
#ending stuff---------------------------------------------------------------------------------------

    def close(self):
        self.running = False

    def get_winners(self):
        hs = max(self.players, key=lambda p: p.score).score
            
        return [p.pid for p in self.players if p.score == hs]

    def end_round(self):
        for p in self.players:
            if not p.round_over:
                p.end_round()
        
    def end_game(self):
        for p in self.players:

            if not p.round_over:
                p.end_round()
                
            if not p.game_over:
                p.end_game()
                
    def finished_game(self):
        return self.round + 1 > self.get_setting('rounds')

    
            
    
                

