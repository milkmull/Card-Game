import os, json

def create_folders():
    os.mkdir('img/temp')

def get_save_data():
    return globals()['SAVE_DATA']
    
def set_save_data(save_data):
    globals()['SAVE_DATA'] = save_data

def get_blank_data():
    save_data = {'username': 'Player 0', 'port': 5555, 'ips': [],
             'settings': {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4},
             'cards': [{'name': 'Player 0', 'description': 'description', 'tags': ['player'], 
                        'image': 'img/user.png', 'id': 0}]}
                      
    return save_data

def update_save(save_data):
    os.mkdir('save')
    with open('save/save.json', 'w') as f:
        json.dump(save_data, f, indent=4)
        
    set_save_data(save_data)

def load_save():
    save_data = get_blank_data()
    try:
        with open('save/save.json', 'r') as f:
            save_data = json.load(f)       
    except:
        update_save(save_data) 
    finally:
        if 'f' in locals():
            f.close()

    return save_data
    
def refresh_save():
    save_data = get_blank_data()
    update_save(save_data)
    
    for f in os.listdir('img/custom'):
        if '0' not in f:
            os.remove(f'img/custom/{f}')
    
def reload_save():
    set_save_data(load_save())
    
def get_data(key):
    save_data = get_save_data()
    val = save_data.get(key)
    return val
    
def set_data(key, val):
    save_data = get_save_data()
    
    if save_data[key] != val: 
        save_data[key] = val

        update_save(save_data)
    
def update_ips(entry):
    ips = get_data('ips').copy()

    if entry not in ips:
    
        ips.append(entry)
        set_data('ips', ips)

def del_ips(entry):
    ips = get_data('ips').copy()
    
    if entry in ips:
    
        ips.remove(entry)
        set_data('ips', ips)
 
def update_cards(entry):
    update = False
    cards = get_data('cards').copy()

    for i, c in enumerate(cards):
        if c['id'] == entry['id']:
            cards[i] = entry
            update = True
            break

    if not update and entry not in cards:
        cards.append(entry)
        update = True
            
    if update:
        set_data('cards', cards)
      
def del_card(entry):
    file = 'img/custom/{}.png'
    cards = get_data('cards').copy()
    
    if entry in cards:
        i = cards.index(entry)
        cards.remove(entry)
        os.remove(file.format(entry['id']))
        
    for i in range(i, len(cards)):
        cards[i]['id'] -= 1
        id = cards[i]['id']
        os.rename(file.format(id + 1), file.format(id))
        
    set_data('cards', cards)
    
def new_card_id():
    return len(get_data('cards'))

def verify_data():
    username = get_data('username')
    if not isinstance(username, str):
        refresh_save()
    
    port = get_data('port')
    if not isinstance(port, int):
        refresh_save()
        
    ips = get_data('ips')
    if not isinstance(ips, list):
        refresh_save()
        
    port = get_data('port')
    if not isinstance(port, int):
        refresh_save()
        
    settings = get_data('settings')
    if not isinstance(settings, dict):
        refresh_save()

    base_settings = {'rounds': range(1, 6), 'ss': range(5, 51), 'cards': range(1, 11),
                     'items': range(0, 6), 'spells': range(0, 4), 'cpus': range(1, 15), 'diff': range(0, 5)}
    
    if any(key not in settings for key in base_settings):
        settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
        set_data('settings', settings)
        
    elif any(settings.get(key) not in base_settings[key] for key in base_settings):
        settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
        set_data('settings', settings)

SAVE_DATA = load_save()
verify_data()
create_folders()
