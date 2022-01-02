from card_base import *

class Big_Boi(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'big boi', tags=[])
    
    def start(self, player):
        self.reset()
        for p1 in self.game.players.copy():
            p1.lose(self, 5)
