from card_base import *

class Player_1(Card):
    name = 'player 1'
    tags = []
    def __init__(self, game, uid):
        super().__init__(game, uid)
    
    def start(self, player):
        self.reset()
        for i1 in range(0, 10):
            player.gain(self, i1)
