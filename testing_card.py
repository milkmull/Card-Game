from card_base import *

class Player_1(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'Player 1', tags=[])
    
    def start(self, player):
        self.reset()
        if True:
            player.gain(self, 5)
