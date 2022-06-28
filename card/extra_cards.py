from . import card_base

class Blank(card_base.Card):
    type = 'extra'
    def __init__(self, game, uid, name, type='play', tags=None):
        self.name = name
        self.type = type
        if tags is None:
            tags = []
        self.tags = tags
        super().__init__(game, uid)
        
    def __eq__(self, other):
        return self.name == getattr(other, 'name', None)
        
    def __hash__(self):
        return self.uid

class VoteCard(card_base.Card):
    name = 'vote'
    type = 'extra'
    def __init__(self, game, *args):
        super().__init__(game, -1)
        self.c1 = Blank(game, -2, 'rotate')
        self.c2 = Blank(game, -3, 'keep')
        
    def start(self):
        for p in self.game.players:
            p.add_request(self, 'select')
        
    def get_selection(self, player):
        return [self.c1, self.c2]
        
    def select(self, player, num):
        if num:
            player.set_vote(player.selected[0].name)