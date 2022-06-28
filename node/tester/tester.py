import traceback
import random
import json
import inspect

from data.save import TEST_CARD_FILE, TEST_CARD_HEADER
from game.game import game_base
from spritesheet import spritesheet
from menu import screens

from ui.menu import Menu
  
def step_test(t):
    t.step_sim()
    if t.get_sims() == 100:
        return 1
        
def run_tester(card):
    t = Tester(card)
    m = Menu.loading_screen(step_test, fargs=[t], message='testing card...')
    m.run()
    t.process()
    messages = t.get_error_messages()
    if messages:
        m = Menu(get_objects=screens.error_screen, args=[messages])
        m.run()
        return
    return True

class Tester:
    @staticmethod
    def get_cards():
        from . import testing_card
        from card import cards as card_manager
        cards = card_manager.get_playable_card_data()
        test_card = inspect.getmembers(testing_card, inspect.isclass)[0][1]
        cards[test_card.type][test_card.name] = test_card
        return cards
        
    @staticmethod
    def get_settings():
        settings = {
            'rounds': 1, 
            'ss': 20, 
            'cards': 5,
            'items': 3,
            'spells': 1,
            'cpus': 3,
            'diff': 1
        }
        return settings
        
    def __init__(self, card):
        self.card = card
        self.write_card()
        self.settings = Tester.get_settings()
        self.cards = Tester.get_cards()
        
        self.sims = 0
        self.errors = []
        
    def write_card(self):         
        with open(TEST_CARD_FILE, 'w') as f:
            f.write(TEST_CARD_HEADER + self.card.code) 
  
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
            g = game_base.Game_Base.simulator(self.settings, self.cards)
            err = None

            try:
                while not g.done():
                    g.main()
            except:
                err = traceback.format_exc()

            if err and err not in self.errors:
                self.errors.append(err)
                print_logs(g)
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
        
def print_logs(g):
    for p in g.players:
        print(f'{p.pid}: ' + '{')
        for log in p.master_log:
            print('\t{')
            for k, v in log.items():
                print(f'\t\t{k}: {v}')
            print('\t}')
        print('}\n')
    