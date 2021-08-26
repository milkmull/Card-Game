import traceback
from game import *

class Tester:
    def __init__(self, settings=None, cards=None):
        self.sims = {}
        self.game = Game('single')
        
        if settings is not None:
            self.game.settings = settings.copy()
            
        if cards is not None:
            self.game.cards = cards.copy()
            
        self.game.new_game()
        
    def sim(self, num, process=lambda g: None):
        games = []
        
        for _ in range(num):
            
            g = self.game.copy()
            err = None
            st = time.time()
            
            try:
                
                while not g.done():
                    g.main()
                    
            except:
                err = traceback.format_exc()
                
            t = time.time() - st
            games.append({'error': err, 'time': t, 'turns': g.turn, 'game': None})
            
            if err:
                games[-1]['game'] = g
                
            process(g)
            
        return games
            
info = []
            
for _ in range(100):
            
    t = Tester()
    info += t.sim(10)

for i in info:
    print(i)
        
        
        
        
        
        
        
        
        
              