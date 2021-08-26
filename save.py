import json
import os

def load_save():
    if not os.path.exists('save/save.json'):
        save_data = new_save() 
    else:
        save_data = read_save()
        
    return save_data

def new_save():
    save_data = {'username': 'Player 0', 'port': 5555, 'ips': [],
                 'settings': {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}}
    
    with open('save/save.json', 'w') as f:
        json.dump(save_data, f, indent=4)
        
    return save_data

def read_save():
    try:
        with open('save/save.json', 'r') as f:
            save_data = json.load(f)
            
    except:
        save_data = new_save()
        
    finally:
        if 'f' in locals():
            f.close()

    return save_data
    
def refresh_save():
    global save_data
    save_data = new_save()
    
def get_data(key):
    global save_data
    
    if key == 'username':
        expected = str
    elif key == 'port':
        expected = int
    elif key == 'ips':
        expected = list
    elif key == 'settings':
        expected = dict

    val = save_data.get(key)
    
    if not isinstance(val, expected):
        save_data = new_save()

    return val
    
def set_data(key, val):
    global save_data

    if save_data[key] != val: 
        save_data[key] = val

        with open('save/save.json', 'w') as f:
            json.dump(save_data, f, indent=4)
    
def update_ips(entry):
    ips = get_data('ips').copy()

    if entry not in ips:
    
        ips.append(entry)
        set_data('ips', ips)

def del_ips(name, ip):
    ips = get_data('ips').copy()
    
    for data in ips.copy():
        
        if data['name'] == name and data['ip'] == ip:
            
            ips.remove(data)
            set_data('ips', ips)
            
            break
            
def set_port(new_port):
    old_port = get_data('port')
    if new_port != old_port:
        set_data('port', new_port)
  
def set_username(new_name):
    old_name = get_data('username')
    if new_name != old_name:
        set_data('username', new_name)
        
def load_settings():
    return load_save()['settings']
      
def get_settings():
    return load_save()['settings']
 
def verify_settings():
    settings = get_settings()
    
    base_settings = {'rounds': range(1, 6), 'ss': range(5, 51), 'cards': range(1, 11),
                     'items': range(0, 6), 'spells': range(0, 4), 'cpus': range(1, 15), 'diff': range(0, 5)}
    
    if any(key not in settings for key in base_settings):
        settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
        set_data('settings', settings)
        
    elif any(settings.get(key) not in base_settings[key] for key in base_settings):
        settings = {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}
        set_data('settings', settings)

save_data = load_save()
verify_settings()
