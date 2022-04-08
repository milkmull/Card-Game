from card_base import *

class Player_1(Card):
    name = 'player 1'
    tags = []
    def __init__(self, game, uid):
        super().__init__(game, uid)
    
    def start(self, player):
        self.reset()
        if True:
            player.gain(self, 0)

class Player_2(Card):
    name = 'player 2'
    tags = []
    def __init__(self, game, uid):
        super().__init__(game, uid)
    
    def start(self, player):
        self.reset()
        player.add_request(self, 'select')
    
    def get_selection(self, player):
        if (not self.extra_card):
            return getattr(player, 'played', []).copy()
        else:
            return self.sort_players(player)
    
    def select(self, player, num):
        if not num:
            return
        sel = player.selected[-1]
        self.t_select = sel
        sel_c = None
        sel_p = None
        if isinstance(sel, Card):
            sel_c = sel
        else:
            sel_p = sel
        if sel_c:
            self.extra_card = sel_c
            self.wait = 'select'
        else:
            player.give_card(self.extra_card, sel_p)
