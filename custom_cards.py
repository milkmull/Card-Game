import card_base

class Hello(card_base.Card):
    name = 'hello'
    type = 'landscape'
    weight = 2
    tags = ['player']
    
    def start(self, player):
        self.reset()
        for p in self.get_opponents(player):
            if p.score < 20:
                p.gain(5)
            else:
                p.lose(5)
