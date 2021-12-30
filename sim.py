import traceback, time
import save
import random
from game import *

save.init()

class Tester:
    def __init__(self, settings=None, cards=None):
        self.sims = {}
        self.game = Game(mode='single')
        
        if settings is not None:
            self.game.settings = settings.copy()
            
        if cards is not None:
            self.game.cards = cards.copy()
            
        self.game.new_game()
        
    def sim(self, num, process=lambda g: None):
        games = []
        
        for _ in range(num):
            
            g = self.game.copy()
            g.new_game()
            err = None
            st = time.time()
            
            try:
                while not g.done():
                    g.main()
                    
            except:
                err = traceback.format_exc()
                
            t = time.time() - st
            games.append({'error': err, 'time': t, 'turns': g.turn, 'game': g})
            
            if err:
                games[-1]['game'] = g
                break
                
            process(g)
            
        return games
            
info = []
            
for _ in range(1):
    t = Tester()
    info += t.sim(1)

for i in info:
    g = i['game']
    print(g.master_log)
    for p in g.players:
        print(p.master_log)
        
        
        
        
        
        
        
        
              