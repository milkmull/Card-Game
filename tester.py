import traceback
import random
import json

import save
import game

import client
import spritesheet

class TestClient(client.Client):
    def __init__(self, game):
        super().__init__(game, 'single')
        
    def quit(self):
        self.n.close()
        self.playing = False

def init():
    globals()['SAVE'] = save.get_save()
    game.init()
    spritesheet.init()
    client.init()
    #save.init()

class Tester:
    @staticmethod
    def get_cards(c):
        cards = SAVE.get_playable_card_data()
        cards['play'][c.name] = {'weight': 5, 'classname': c.classname, 'custom': True, 'test': True}
        return cards
        
    def __init__(self, card):
        self.card = card
        self.cards = Tester.get_cards(card)
        
        self.sims = 0
        self.errors = []
        
        game.load_testing_card()
  
    def get_errors(self):
        return self.errors
        
    def get_error_messages(self):
        return [err.splitlines()[-2] for err in self.errors]
        
    def get_error_lines(self):
        lines = []
        
        for err in self.errors:
            end = err.split('line ')[-1]
            text = ''
            for char in end:
                if char.isnumeric():
                    text += char
                else:
                    break
            lines.append(text)
            
        return lines
        
    def filter_errors(self):
        endings = set(err.split('line ')[-1] for err in self.errors)
        for err in self.errors.copy():
            end = err.split('line ')[-1]
            if end in endings:
                endings.remove(end)
            else:
                self.errors.remove(err)

    def show_data(self):
        for err in self.errors:
            print(err)
            
    def step_sim(self):
        self.sim(1)
        
    def get_sims(self):
        return self.sims
        
    def sim(self, num):
        for _ in range(num):
            g = game.Game(mode='single', cards=self.cards).copy()
            g.new_game()
            err = None
            
            try:
                while not g.done():
                    g.main()
            except:
                err = traceback.format_exc()
                
            if err and err not in self.errors:
                self.errors.append(err)
                
            self.sims += 1
            
    def process(self):
        self.filter_errors()
    
def test_run(card):
    text = ''
    g = game.Game(mode='single', cards=Tester.get_cards(card))
    c = TestClient(g)
    try:
        c.run()
    except:
        err = traceback.format_exc()
        text = f'the following errors occurred: {err.splitlines()[-2]}'
    finally:
        c.quit()
        return text
    
    