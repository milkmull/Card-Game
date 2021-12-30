def safe_remove(ls, val):
    if val in ls:
        ls.remove(val)
        
def safe_index(ls, i):
    return ls[i] if i in range(len(ls)) else None

class Card:
    def __init__(self, game, uid, name, tags=[]):
        self.game = game
        self.uid = uid
        
        self.name = name
        self.tags = tags
        
        self.mode = 0

        self.t_coin = -1
        self.t_roll = -1
        self.t_select = None

        self.cards = []
        self.players = []
        
        self.extra_card = None
        self.extra_player = None
        
        self.mult = True
        
        self.wait = None
        self.log_types = []

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def __eq__(self, other):
        if hasattr(other, 'get_id'):
            return self.uid == other.get_id() and self.name == other.get_name()
        else:
            return False
        
    def copy(self): 
        T = type(self)
        if T != Blank:
            c = T(self.game, self.uid)
        else:
            c = T(self.game, self.uid, self.name)
        return c
        
    def light_sim_copy(self, game):
        T = type(self)
        if T != Blank:
            c = T(game, self.uid)
        else:
            c = T(game, self.uid, self.name)
        return c
        
    def sim_copy(self, game, parent=None, pcopy=None):
        T = type(self)
        if T != Blank:
            c = T(game, self.uid)
        else:
            c = T(game, self.uid, self.name)

        c.mode = self.mode

        c.wait = self.wait
        c.log_types = self.log_types
        
        c.t_coin = self.t_coin
        c.t_roll = self.t_roll
        if self.t_select:
            if self.t_select is parent:
                c.t_select = pcopy
            else:
                c.t_select = self.t_select.sim_copy(game, parent=self, pcopy=c)
        
        c.players = [game.get_player(p.pid) for p in self.players]
        
        for o in self.cards:
            if o is parent:
                o = pcopy
            else:
                o = o.sim_copy(game, parent=self, pcopy=c)
            c.cards.append(o)

        if self.extra_card:
            if self.extra_card is parent:
                c.extra_card = pcopy
            else:
                c.extra_card = self.extra_card.sim_copy(game, parent=self, pcopy=c) 
        if self.extra_player: 
            c.extra_player = game.get_player(self.extra_player.pid)
    
        return c
        
    def storage_copy(self):
        c = self.copy()
        c.players = self.players.copy()
        c.cards = self.cards.copy()
        
        if self.extra_card:
            c.extra_card = self.extra_card
        if self.extra_player: 
            c.extra_player = self.extra_player

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
        
    def check_index(self, player, i, tags=[], inclusive=False): 
        added = False
        c = player.get_played_card(i)
        
        if c is not None:
            hastags = [t in c.tags for t in tags]
            
            if tags:
                if (not inclusive and any(hastags)) or (inclusive and all(hastags)):
                    if c not in self.cards:
                        self.cards.append(c)
                        added = True
            else:
                if c not in self.cards:
                    self.cards.append(c)
                    added = True
                    
        return (added, c)

    def set_log_types(self, types):
        if isinstance(types, str):
            types = [types]
        self.log_types = types
        
    def reset(self):
        self.mode = 0
        self.extra_card = None
        self.extra_player = None
        self.cards.clear()
        self.players.clear()
        
        self.log_types.clear()
        self.wait = None
        
        self.t_coin = -1
        self.t_roll = -1
        self.t_select = None
        
    def deploy(self, player, players, request, extra_card=None, extra_player=None):
        if player in players:
            players.remove(player)
        if not players or request not in ('flip', 'roll', 'select', 'og'):
            return
            
        self.players.clear()
        self.cards.clear()
        
        if extra_card is None:
            extra_card = self
        if extra_player is None:
            extra_player = player
        
        for p in players:
            c = self.copy()
            c.extra_player = extra_player
            c.extra_card = extra_card
            
            if request in ('flip', 'roll', 'select'):
                c = p.add_request(c, request)
            elif request == 'og':
                c.start_ongoing(p)
                
            self.players.append(p)
            self.cards.append(c)

    def get_flip_results(self):
        players = []
        results = []
        
        for c, p in zip(self.cards.copy(), self.players.copy()):
            if c.t_coin != -1:
                results.append(c.t_coin)
                players.append(p)

        return (players, results)

    def get_roll_results(self):
        players = []
        results = []
        
        for c, p in zip(self.cards.copy(), self.players.copy()):
            if c.t_roll != -1:
                results.append(c.t_roll)
                players.append(p)

        return (players, results)
        
    def get_select_results(self):
        players = []
        results = []
        
        for c, p in zip(self.cards.copy(), self.players.copy()):
            if c.t_select is not None:
                results.append(c.t_select)
                players.append(p)

        return (players, results)
        
class Blank(Card):
    def __init__(self, game, uid, name):
        super().__init__(game, game.get_new_uid(), name, tags=[])
        
    def __eq__(self, other):
        return self.name == other.get_name()