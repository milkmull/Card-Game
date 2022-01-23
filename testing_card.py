from card_base import *

class Player_0(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'player 0', tags=[])
    
    def start(self, player):
        self.reset()
        self.start_ongoing(player)
    
    def start_ongoing(self, player):
        player.add_og(self, 'cont')
    
    def ongoing(self, player, log):
        added6, c6 = self.check_index(player, (player.played.index(self) + 1), tags=['human'])
        if added6:
            player.gain(self, 5)
