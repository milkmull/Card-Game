from card_base import *

class Test(Card):
    def __init__(self, game, uid):
        super().__init__(game, uid, 'test', tags=[])
    
    def start(self, player):
        self.reset()
        for x1 in range(1):
            pass
