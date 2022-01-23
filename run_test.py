import save
import game
import time
import traceback
import sys
import random
import cProfile

save.init()
game.init()

times = []
error_info = None

for _ in range(10000):

    seed = round(float(str(time.time())[::-1]))
    random.seed(seed)
    
    g = game.Game(mode='single')
    
    g.new_game()
    gc = g.copy()
    
    try:
        
        while not gc.done():
            gc.main()
            
    except Exception as e:
        print(e)
        print(seed)
        break

#cProfile.run('run(g)')


