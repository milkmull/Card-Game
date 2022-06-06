from card_base import *

class Hhhhh(Card):
    name = 'hhhhh'
    tags = []
    
    def start(self, player):
        self.reset()
        seq24 = player.draw_cards('treasure', num=1)
    
    def get_selection(self, player):
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
    
    def start_ongoing(self, player):
        player.add_og(self, '')
    
    def ongoing(self, player, log):
        pass
