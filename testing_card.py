import card_base

class Hello(card_base.Card):
    name = 'hello'
    type = 'play'
    weight = 1
    tags = ['player']
    
    def start(self, player):
        self.reset()
        player.steal(self, 3, self.get_opponents(player)[-1])
