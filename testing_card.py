from card_base import *

class Player_0(Card):
    name = 'player 0'
    tags = []
    
    def start(self, player):
        self.reset()
        x = 5
        for i in range(20):
            player.gain(self, i * 5)
