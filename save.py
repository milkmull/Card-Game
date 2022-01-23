import os, json, copy

def init():
    globals()['SAVE'] = Save()

def get_save():
    return globals().get('SAVE')

class Save:
    @staticmethod
    def create_folders():
        if not os.path.exists('img/temp'):
            os.mkdir('img/temp')
        if not os.path.exists('img/custom'):
            os.mkdir('img/custom')
        if not os.path.exists('save'):
            os.mkdir('save')
 
    @staticmethod
    def get_blank_data():
        save_data = {'username': 'Player 0', 'port': 5555, 'ips': [],
         'settings': {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4},
         'cards': [{'name': 'Player 0', 'description': 'description', 'tags': ['player'], 
                    'image': 'img/user.png', 'color': [161, 195, 161], 'id': 0, 'node_data': {}}]}
                      
        return save_data
        
    @staticmethod
    def get_blank_card_data():
        return {'name': 'Player 0', 'description': 'description', 'tags': ['player'], 
                'image': 'img/user.png', 'color': [161, 195, 161], 'id': 0, 'node_data': {}}
                
    @staticmethod
    def get_card_data():
        with open('save/cards.json', 'r') as f:
            data = json.load(f)
        return data

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
                
        import customsheet
        sheet = customsheet.get_sheet()
        if sheet:
            sheet.reset()
            
        with open('custom_cards.py', 'w') as f:
            f.write('from card_base import *\n')
        
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

        base_settings = {'rounds': range(1, 6), 'ss': range(5, 51), 'cards': range(1, 11),
                         'items': range(0, 6), 'spells': range(0, 4), 'cpus': range(1, 15), 'diff': range(0, 5)}
        
        if any(key not in settings for key in base_settings):
            settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
            self.set_data('settings', settings)
            
        elif any(settings.get(key) not in base_settings[key] for key in base_settings):
            settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
            self.set_data('settings', settings)
        
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
        file = 'img/custom/{}.png'
        cards = self.get_data('cards')
        text_shift_start = 0
        text_shift = 0

        image_shift_start = cards.index(entry)
        cards.remove(entry)
        os.remove(file.format(entry['id']))
        
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
                old_image_path = file.format(id + 1)
                new_image_path = file.format(id)
                os.rename(old_image_path, new_image_path)
                card['image'] = new_image_path
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
            data[c['name']] = {'weight': c['weight'], 'classname': c['classname'], 'custom': True, 'published': c['published']}
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
                data['play'][c['name']] = {'weight': c['weight'], 'classname': c['classname'], 'custom': True}
        return data
        
    def get_custom_names(self):
        return tuple(c['name'] for c in self.get_data('cards'))
        
    def publish_card(self, card, text):
        shift_start = 0
        shift = 0
        s, e = card.lines

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
        card.publish(s, e)

        if shift_start:
            self.shift_cards(shift_start, shift)
            
    def shift_cards(self, shift_start, shift):
        cards = self.get_data('cards')
        for i, card in enumerate(cards):
            s, e = card['lines']
            if (s or e) and s >= shift_start:
                card['lines'] = (s + shift, e + shift)
        
        self.set_data('cards', cards)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
