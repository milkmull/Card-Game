import json
import os

def load_save():
    if not os.path.exists('save.json'):
        save_data = new_save() 
    else:
        save_data = read_save()
        
    return save_data

def new_save():
    save_data = {'username': 'Player 0', 'port': 5555, 'ips': [],
                 'settings': {'rounds': 3, 'ss': 20, 'cards': 5, 'items': 3, 'spells': 1, 'cpus': 1, 'diff': 4}}
    
    with open('save.json', 'w') as f:
        
        json.dump(save_data, f, indent=4)
        
    return save_data

def read_save():
    try:
    
        with open('save.json', 'r') as f:

            save_data = json.load(f)
            
    except:
    
        new_message('an error occurred, save data has been cleared', 2000)
        
        save_data = new_save()

    return save_data
    
def get_data(key):
    global save_data

    return save_data[key]
    
def set_data(key, val):
    global save_data

    if save_data[key] != val:
        
        save_data[key] = val

        with open('save.json', 'w') as f:
        
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
      
save_data = load_save()
