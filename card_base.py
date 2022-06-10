
class Card:
    name = 'card'
    type = 'base'
    weight = 0
    tags = []
    
    @classmethod
    def get_subclasses(cls):
        return cls.__subclasses__()
    
    def __init__(self, game, uid):
        self.game = game
        self.uid = uid
        
        self.mode = 0

        self.t_coin = -1
        self.t_roll = -1
        self.t_select = None

        self.cards = []
        self.players = []
        
        self.extra_card = None
        self.extra_player = None

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
            
    def __hash__(self):
        return self.uid
        
    def copy(self): 
        T = type(self)
        if T.__name__ != 'Blank':
            c = T(self.game, self.uid)
        else:
            c = T(self.game, self.uid, self.name)
        return c
        
    def light_sim_copy(self, game):
        T = type(self)
        if T.__name__ != 'Blank':
            c = T(game, self.uid)
        else:
            c = T(game, self.uid, self.name)
        return c
        
    def sim_copy(self, game, parent=None, pcopy=None):
        T = type(self)
        if T.__name__ != 'Blank':
            c = T(game, self.uid)
        else:
            c = T(game, self.uid, self.name)

        c.mode = self.mode

        c.wait = self.wait
        c.log_types = self.log_types.copy()
        
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
        
    def get_id(self):
        return self.uid
        
    def get_name(self):
        return self.name
         
    def can_use(self, player):
        return True
        
    def can_cast(self, player):
        return True

    def get_players(self):
        return self.game.players.copy()
   
    def get_opponents(self, player):
        return [p for p in self.game.players if p != player]
        
    def get_opponents_with_points(self, player):
        return [p for p in self.game.players if p.pid != player.pid and p.score]
        
    def get_players_custom(self, player, key):
        return [p for p in self.game.players if p.pid != player.pid and key(p)]
    
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

    def get_selection(self, player):
        return []
        
    def select(self, player, num):
        pass
        
    def flip(self, player, coin):
        pass
        
    def roll(self, player, dice):
        pass
        
    def start_ongoing(self, player):
        pass
        
    def ongoing(self, player, log):
        pass
        
    def start(self, player):
        pass
        
    def end(self, player):
        pass
        
        
        
        
        
        