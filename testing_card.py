from card_base import *

class Play_Now(Card):
    name = 'play now'
    tags = []
    
    def start(self, player):
        self.reset()
        seq1 = player.draw_cards('unplayed', num=1)
        player.play_card(seq1[0])
