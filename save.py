import os
import json
import copy

def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data
    
BASE_NAMES = (
    'michael', 'dom', 'jack', 'mary', 'daniel', 'emily', 'gambling boi', 'mom', 'dad',
    'aunt peg', 'uncle john', 'kristen', 'joe', 'robber', 'ninja', 'item frenzy', 'mustard stain', 'gold coins',
    'gold', 'max the dog', 'basil the dog', 'copy cat', 'racoon', 'fox', 'cow', 'shark', 'fish',
    'pelican', 'lucky duck', 'lady bug', 'mosquito', 'snail', 'dragon', 'clam', 'pearl', 'uphalump',
    'flu', 'cactus', 'poison ivy', 'rose', 'mr. squash', 'mrs. squash', 'ghost', 'fishing pole', 'invisibility cloak',
    'last turn pass', 'detergent', 'treasure chest', 'speed boost potion', 'fertilizer', 'mirror', 'sword', 'spell trap', 'item leech',
    'curse', 'treasure curse', 'bronze', 'negative zone', 'item hex', 'luck', 'fishing trip', 'bath tub', 'boomerang',
    'future orb', 'knife', 'magic wand', 'lucky coin', 'sapling', 'vines', 'zombie', 'jumble', 'demon water glass',
    'succosecc', 'sunflower', 'lemon lord', 'wizard', 'haunted oak', 'spell reverse', 'sunny day', 'garden', 'desert',
    'fools gold', 'graveyard', 'city', 'wind gust', 'sunglasses', 'metal detector', 'sand storm', 'mummy', 'mummys curse',
    'pig', 'corn', 'harvest', 'golden egg', 'bear', 'big rock', 'unlucky coin', 'trap', 'hunting season',
    'stardust', 'water lily', 'torpedo', 'bat', 'sky flower', 'kite', 'balloon', 'north wind', 'garden snake',
    'flower pot', 'farm', 'forest', 'water', 'sky', 'office fern', 'parade', 'camel', 'rattle snake',
    'tumble weed', 'watering can', 'magic bean', 'the void', 'bug net', 'big sand worm', 'lost palm tree', 'seaweed', 'scuba baby'
)

CONSTANTS = {
    'width': 1024,
    'height': 576,
    'screen_size': (1024, 576),
    'center': (1024 // 2, 576 // 2),
    'cw': 375 // 10,
    'ch': 525 // 10,
    'mini_card_size': (375 // 10, 525 // 10),
    'card_width': 375,
    'card_height': 525,
    'card_size': (375, 525),
    'fps': 30
}

CONFIRMATION_CODE = 'thisisthecardgameserver'
    
class Save:
    BASE_SETTINGS = {
        'rounds': range(1, 6), 
        'ss': range(5, 51), 
        'cards': range(1, 11),
        'items': range(0, 6), 
        'spells': range(0, 4), 
        'cpus': range(1, 15), 
        'diff': range(0, 5)
    }

    @staticmethod
    def create_folders():
        if not os.path.exists('img/temp'):
            os.mkdir('img/temp')
        if not os.path.exists('snd/temp'):
            os.mkdir('snd/temp')
        if not os.path.exists('img/custom'):
            os.mkdir('img/custom')
        if not os.path.exists('snd/custom'):
            os.mkdir('snd/custom')
        if not os.path.exists('save'):
            os.mkdir('save')
            
    @staticmethod
    def get_base_settings():
        settings = {
            'rounds': 3, 
            'ss': 20, 
            'cards': 5,
            'items': 3,
            'spells': 1,
            'cpus': 1,
            'diff': 4
        }
        return settings

    @staticmethod
    def get_blank_card_data():
        data = {
            'name': 'Player 0', 
            'type': 'user',
            'description': 'description', 
            'tags': ['player'], 
            'color': [161, 195, 161],
            'image': 'img/user.png', 
            'sound': None,
            'id': 0, 
            'weight': 1,
            'classname': 'Player_0',
            'custom': True,
            'code': '',
            'lines': [0, 0],
            'published': False,
            'node_data': {}
        }
        return data
 
    @staticmethod
    def get_blank_data():
        save_data = {
            'username': 'Player 0', 
            'port': 5555, 
            'ips': [],
            'settings': Save.get_base_settings(),
            'cards': [Save.get_blank_card_data()]
        }             
        return save_data
                
    @staticmethod
    def get_card_data():
        with open('save/cards.json', 'r') as f:
            data = json.load(f)
        return data
        
    @staticmethod
    def get_sheet_info(info):
        return load_json('data/sheet_info.json').get(info)

    def __init__(self):
        self.save_data = None
        self.reset = False
        
        self.archive = None
        
        Save.create_folders()
        self.load_save()
        self.verify_data()
        
    def load_save(self):
        try:
            with open('save/save.json', 'r') as f:
                save_data = json.load(f)  
            self.save_data = save_data
        except:
            self.reset_save() 
        finally:
            if 'f' in locals():
                f.close()
                
        self.archive = copy.deepcopy(self.save_data)
        
    def reset_save(self):
        self.save_data = Save.get_blank_data()
        self.update_save()

        for f in os.listdir('img/custom'):
            os.remove(f'img/custom/{f}')
        for f in os.listdir('snd/custom'):
            os.remove(f'snd/custom/{f}')
                
        import customsheet
        sheet = customsheet.CUSTOMSHEET
        if sheet:
            sheet.reset()
            
        with open('custom_cards.py', 'w') as f:
            f.write('import card_base\n')
        
    def update_save(self):
        try:
            with open('save/save.json', 'w') as f:
                json.dump(self.save_data, f, indent=4)
        except:
            self.save_data = copy.deepcopy(self.archive)
        else:
            self.archive = copy.deepcopy(self.save_data)
        
    def verify_data(self):
        username = self.get_data('username')
        if not isinstance(username, str):
            self.set_data('username', 'Player 0')
        
        port = self.get_data('port')
        if not isinstance(port, int):
            self.set_data('port', 5555)
            
        ips = self.get_data('ips')
        if not isinstance(ips, list):
            self.set_data('ips', [])
            
        cards = self.get_data('cards')
        if not isinstance(cards, list):
            self.reset_save()
            
        settings = self.get_data('settings')
        if not isinstance(settings, dict):
            self.reset_save()
            
        base_settings = Save.BASE_SETTINGS
        if any({key not in settings for key in base_settings}):
            self.set_data('settings', Save.get_base_settings()) 
        elif any({settings.get(key) not in base_settings[key] for key in base_settings}):
            self.set_data('settings', Save.get_base_settings())
            
        if len(self.get_data('cards')) == 0:
            cards = [Save.get_blank_card_data()]
            self.set_data('cards', cards)
        
    def get_data(self, key):
        val = copy.deepcopy(self.save_data.get(key))
        return val
        
    def set_data(self, key, val):
        if self.save_data[key] != val: 
            self.save_data[key] = val
            self.update_save()
        
    def update_ips(self, entry):
        ips = self.get_data('ips')
        if entry not in ips:
            ips.append(entry)
            self.set_data('ips', ips)
        
    def del_ips(self, entry):
        ips = self.get_data('ips')
        if entry in ips:
            ips.remove(entry)
            self.set_data('ips', ips)
        
    def update_cards(self, entry):
        update = False
        cards = self.get_data('cards')

        for i, c in enumerate(cards):
            if c['id'] == entry['id']:
                cards[i] = entry
                update = True
                break

        if not update and entry not in cards:
            cards.append(entry)
            update = True
                
        if update:
            self.set_data('cards', cards)
      
    def del_card(self, entry):
        image_file = 'img/custom/{}.png'
        sound_file = 'snd/custom/{}.wav'
        cards = self.get_data('cards')
        text_shift_start = 0
        text_shift = 0

        image_shift_start = cards.index(entry)
        cards.remove(entry)
        os.remove(entry['image'])
        if entry['sound']:
            os.remove(entry['sound'])
        
        s, e = entry['lines']
        if s or e:
            with open('custom_cards.py', 'r') as f:
                lines = f.readlines()
            lines = lines[:s] + lines[e:]
            with open('custom_cards.py', 'w') as f:
                f.writelines(lines)
            text_shift_start = e
            text_shift = -(e - s)
            
        for i, card in enumerate(cards):
            if i >= image_shift_start:
                card['id'] -= 1
                id = card['id']
                old_image_path = image_file.format(id + 1)
                new_image_path = image_file.format(id)
                os.rename(old_image_path, new_image_path)
                card['image'] = new_image_path
                if card['sound']:
                    old_sound_path = sound_file.format(id + 1)
                    new_sound_path = sound_file.format(id)
                    os.rename(old_sound_path, new_sound_path)
                    card['sound'] = new_sound_path
            if text_shift:
                s, e = card['lines']
                if (s or e) and s >= text_shift_start:
                    card['lines'] = (s + text_shift, e + text_shift)
            
        self.set_data('cards', cards)

    def new_card_id(self):
        return len(self.get_data('cards'))
        
    def get_new_card_data(self):
        data = Save.get_blank_card_data()
        data['id'] = self.new_card_id()
        return data
        
    def get_custom_card_data(self):
        data = {}
        cards = self.get_data('cards')
        for c in cards:
            data[c['name']] = {
                'weight': c['weight'], 
                'classname': c['classname'], 
                'custom': True, 
                'published': c['published']
            }
        return data
        
    def get_all_card_data(self):
        data = Save.get_card_data()
        data['play'].update(self.get_custom_card_data())
        return data
        
    def get_playable_card_data(self):
        data = Save.get_card_data()
        cards = self.get_data('cards')
        for c in cards:
            if c['published'] and c['id']:
                data['play'][c['name']] = {
                    'weight': c['weight'], 
                    'classname': c['classname'], 
                    'custom': True
                }
        return data
        
    def get_custom_names(self):
        return tuple([c['name'] for c in self.get_data('cards')])
        
    def id_to_name(self, id):
        for c in self.get_data('cards'):
            if c['id'] == id:
                return c['name']
        
    def publish_card(self, card):
        shift_start = 0
        shift = 0
        s, e = card.lines
        text = card.code

        with open('custom_cards.py', 'r') as f:
            lines = f.readlines()
            
        if s or e:
            lines = lines[:s] + lines[e:]
            shift_start = e
            shift = -(e - s)
            
        with open('custom_cards.py', 'w') as f:
            f.writelines(lines)
            f.write(text)
                
        s = len(lines)
        e = s + len(text.splitlines())

        if shift_start:
            self.shift_cards(shift_start, shift)
            
        import cards
        cards.load_custom_cards()
            
        return (s, e)
            
    def shift_cards(self, shift_start, shift):
        cards = self.get_data('cards')
        for i, card in enumerate(cards):
            s, e = card['lines']
            if (s or e) and s >= shift_start:
                card['lines'] = (s + shift, e + shift)
        
        self.set_data('cards', cards)
        
SAVE = Save()
        
        
        
        
        
        
        
        
        
        
