from game import Game

for _ in range(1000):

    g = Game('single')
    
    g.new_game()
    g.start(0)
    
    for p in g.players:
    
        p.start_turbo()
        
    while not g.done:
    
        g.main()

