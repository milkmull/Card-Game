import socket, subprocess, sys
import urllib.request

import save
import network
import builder
import client
import game

import spritesheet
import customsheet

from constants import *
from ui import *

def init():
    globals()['SPRITESHEET'] = spritesheet.get_sheet()
    globals()['CUSTOMSHEET'] = customsheet.get_sheet()
    
#errors----------------------------------------------------------------

class PortInUse(Exception):
    pass

#menus-----------------------------------------------------------------

def main_menu(args=[]):
    screen = []
    
    btn = Button((200, 30), 'single player', (0, 0, 0), (100, 100, 100), func=single_player)
    btn.rect.center = (width // 2, height // 2)
    btn.rect.midbottom = btn.rect.midtop
    screen.append(btn)
    
    btn = Button((200, 30), 'host game', (0, 0, 0), (100, 100, 100), func=start_game)
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'find online game', (0, 0, 0), (100, 100, 100),
    func=menu, args=[select_host_menu])
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'find local game', (0, 0, 0), (100, 100, 100), func=connect, args=['', save.get_data('port')])
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'card builder', (0, 0, 0), (100, 100, 100), func=menu, args=[builder_menu])
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'settings', (0, 0, 0), (100, 100, 100), func=menu, args=[settings_menu])
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'exit game', (0, 0, 0), (100, 100, 100), tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    btn.rect.y += btn.rect.height
    screen.append(btn)
    
    center_buttons_y(screen)
    
    return screen

def settings_menu():
    screen = []
    
    text = Textbox('display name:  ', 20)
    text.rect.right = width // 2
    text.rect.bottom = height // 2
    text.rect.midbottom = text.rect.midtop
    screen.append(text)
    
    text = Input((200, 30), save.get_data('username'), color=(0, 0, 0), tcolor=(255, 255, 255), length=12)
    text.rect.midleft = screen[-1].rect.midright
    screen.append(text)

    text = Textbox('default port:  ', 20)
    text.rect.right = width // 2
    text.rect.y = screen[-1].rect.bottom + 5
    screen.append(text)
    
    text = Input((200, 30), str(save.get_data('port')), color=(0, 0, 0), tcolor=(255, 255, 255), 
                                                   check=lambda char: char.isnumeric(), length=5)
    text.rect.midleft = screen[-1].rect.midright
    screen.append(text)

    b = Button((200, 30), 'reset save data', func=refresh_save, tag='refresh')
    b.rect.centerx = width // 2
    b.rect.y = screen[-1].rect.bottom
    b.rect.y += b.rect.height
    screen.append(b)
    
    btn = Button((200, 30), 'save', (0, 0, 0), (100, 100, 100), func=save_user_settings)
    btn.set_args(args=[btn, screen[1], screen[3]])
    btn.rect.centerx = width // 2
    btn.rect.y = screen[-1].rect.bottom + btn.rect.height
    screen.append(btn)
    
    btn = Button((200, 30), 'cancel', (0, 0, 0), (100, 100, 100), tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    screen.append(btn)
    
    return screen

def select_host_menu():
    screen = []
    
    y = 0

    for entry in save.get_data('ips'):

        btn = Button((200, 30), entry['name'] + ': ' + entry['ip'], (0, 0, 0), (100, 100, 100), func=menu,
                     args=[join_game_menu], kwargs={'args': [entry['name'], entry['ip']]}, tag='refresh')
        btn.rect.centerx = width // 2
        btn.rect.y = y
        screen.append(btn)
        
        y += btn.rect.height + 5
        
    if screen:  
        center_buttons_y(screen)

    btn = Button((200, 30), 'new entry', (0, 0, 0), (100, 100, 100), func=menu, args=[new_entry_menu], tag='refresh')
    if screen:
        btn.rect.midtop = screen[-1].rect.midbottom   
    else:
        btn.rect.midbottom = (width // 2, height // 2) 
    btn.rect.y += 20
    screen.append(btn)
    
    btn = Button((200, 30), 'view my ip', (0, 0, 0), (100, 100, 100), func=menu, args=[view_ip_menu])
    btn.rect.midtop = screen[-1].rect.midbottom
    screen.append(btn)
        
    btn = Button((200, 30), 'back', (0, 0, 0), (100, 100, 100), tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += btn.rect.height
    screen.append(btn)

    center_buttons_y(screen)
    
    return screen
    
def view_ip_menu():
    screen = []
    
    public_ip = get_public_ip()
    local_ip = get_local_ip()

    text = Textbox(f'your online IP:  {public_ip}', 20)
    text.rect.midbottom = (width // 2, height // 2)
    screen.append(text)
    
    btn = Button((200, 30), 'copy online IP to clipboard', tcolor=(255, 255, 0),
                 func=copy_to_clipboard, args=[public_ip])
    btn.set_timer_rule(125, 'coppied')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    text = Textbox(f'your local IP: {local_ip}', 20)
    text.rect.midtop = screen[-1].rect.midbottom
    text.rect.y += 5
    screen.append(text)
    
    btn = Button((200, 30), 'copy local IP to clipboard', tcolor=(255, 255, 0))
    btn.set_func(copy_to_clipboard, args=[local_ip])
    btn.set_timer_rule(125, 'coppied')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'back', tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += btn.rect.height
    screen.append(btn)
    
    center_buttons_y(screen)
    
    return screen

def new_entry_menu():
    screen = []
    
    text = Textbox('entry name: ', 20)
    text.rect.midright = (width // 2, height // 2)
    text.rect.midbottom = text.rect.midtop
    screen.append(text)
    
    input = Input((100, 20), 'name', tsize=20)
    input.rect.midleft = screen[-1].rect.midright 
    screen.append(input)
    
    center_buttons_x(screen[-2:])
    
    text = Textbox('entry IP: ', 20)
    text.rect.topright = screen[-2].rect.bottomright
    text.rect.y += 20
    screen.append(text)
    
    input = Input((100, 20), '255.255.255.255', tsize=20, check=lambda txt: txt.isnumeric() or txt == '.')
    input.rect.midleft = screen[-1].rect.midright      
    screen.append(input)
    
    center_buttons_x(screen[-2:])
    
    btn = Button((200, 30), 'save', (0, 0, 0), (100, 100, 100), func=new_entry,
                                          args=[screen[1], screen[3]], tag='break')
    btn.rect.centerx = width // 2
    btn.rect.y = screen[-1].rect.bottom + (btn.rect.height * 2)
    screen.append(btn)
    
    btn = Button((200, 30), 'cancel', (0, 0, 0), (100, 100, 100), tag='break')
    btn.rect.centerx = width // 2
    btn.rect.y = screen[-1].rect.bottom + 5
    screen.append(btn)
    
    return screen

def join_game_menu(name, ip):
    screen = []

    text = Textbox('name: ' + name, 20)
    text.rect.center = (width // 2, height // 2)
    screen.append(text)

    text = Textbox('ip: ' + ip, 20)
    text.rect.midtop = screen[-1].rect.midbottom
    text.rect.y += 5
    screen.append(text)
    
    text = Textbox('port: ', 20)
    text.rect.top = screen[-1].rect.bottom
    text.rect.y += 5
    text.rect.right = width // 2
    screen.append(text)
    
    input = Input((100, 20), str(save.get_data('port')))
    input.rect.midleft = screen[-1].rect.midright
    screen.append(input)
    
    center_buttons_x(screen[-2:])

    btn = Button((200, 30), 'join game', (0, 0, 0), (0, 255, 0), func=join_game, args=[ip, screen[-1]])
    btn.rect.top = screen[-1].rect.bottom
    btn.rect.y += btn.rect.height
    btn.rect.centerx = width // 2
    screen.append(btn)
    
    btn = Button((200, 30), 'delete', (0, 0, 0), (255, 0, 0), func=save.del_ips,
                 args=[{'name': name, 'ip': ip}], tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    btn = Button((200, 30), 'back', (0, 0, 0), (255, 0, 0), tag='break')
    btn.rect.midtop = screen[-1].rect.midbottom
    btn.rect.y += 5
    screen.append(btn)
    
    center_buttons_y(screen)
    
    return screen

def builder_menu():
    screen = []
    
    p = Pane((300, 300), label='custom cards:', label_space=10, tsize=30, ul=True, live=True)
    p.rect.centerx = width // 2
    p.rect.y = 70
    screen.append(p)
    
    #t = Textbox('custom cards:', tsize=30)
    #t.rect.centerx = width // 2
    #t.rect.y = t.rect.height * 2
    #screen.append(t)

    cards = save.get_data('cards').copy()
    
    buttons = []
    for c in cards:
        name = c['name']
        b = Button((200, 30), name, func=menu, args=[card_edit_menu], kwargs={'args': [c]}, tag='refresh')
        screen.append(b)
        buttons.append(b)
        
    p.join_objects(buttons)
        
    b = Button((200, 30), 'new', func=run_builder, tag='refresh')
    b.rect.midbottom = (width // 2, height)
    b.rect.y -= b.rect.height * 2
    screen.append(b)
    
    b = Button((200, 30), 'back', tag='break')
    b.rect.midtop = screen[-1].rect.midbottom
    b.rect.y += 5
    screen.append(b)
    
    return screen

def card_edit_menu(card):
    screen = []

    t = Textbox(card['name'] + ':', tsize=30)
    t.rect.centerx = width // 2
    screen.append(t)
    
    i = Image(CUSTOMSHEET.get_image(card['name'], size=(card_width // 3, card_height // 3)))
    i.rect.midtop = screen[-1].rect.midbottom
    i.rect.y += 5
    screen.append(i)
    
    b = Button((200, 30), 'edit card', func=run_builder, kwargs={'card_info': card}, tag='break')
    b.rect.centerx = width // 2
    b.rect.y = screen[-1].rect.bottom + b.rect.height
    screen.append(b)
    
    if card['id'] != 0:
        b = Button((200, 30), 'delete card', func=del_card, args=[card], tag='break')
        b.rect.centerx = width // 2
        b.rect.y = screen[-1].rect.bottom + 5
        screen.append(b)
    
    b = Button((200, 30), 'back', tag='break')
    b.rect.centerx = width // 2
    b.rect.y = screen[-1].rect.bottom + b.rect.height
    screen.append(b)
    
    center_buttons_y(screen)
    
    return screen

#other-------------------------------------------------------------------

def get_local_ip():
    return socket.gethostbyname(socket.gethostname())
    
def get_public_ip():
    ip = 'no internet connection'
    
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode()
    except urllib.error.URLError:
        pass
        
    return ip
    
def refresh_save():
    r = menu(yes_no, args=['Are you sure you want to reset your save data?'], overlay=True)
    if r:
        save.refresh_save()
        CUSTOMSHEET.refresh()

#main--------------------------------------------------------------------

def connect(ip, port):
    new_message('searching for game...', 500)

    try:       
        net = network.Network(ip, port)
        c = client.Client(net, 'online') 
        c.run()
        
    except network.InvalidIP:
        menu(notice, args=['An invalid IP address has been entered.'], overlay=True)
        
    except network.NoGamesFound:  
        new_message('no games could be found', 2000)
        
    except EOFError as e:
        print(e)
        new_message('disconnecting...', 1000)  
        
    except Exception as e: 
        print(e, 'c1')
        new_message('an error occurred', 2000)
        
    finally:
        if 'c' in locals():
            c.exit()
        
def start_game():
    new_message('starting game...', 500)

    try:
    
        pipe = subprocess.Popen([sys.executable, 'server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            _, error = pipe.communicate(timeout=1)
            if 'PortInUse' in error.decode():
                raise PortInUse
        except subprocess.TimeoutExpired:
            pass

        net = network.Network(get_local_ip(), save.get_data('port'))
        c = client.Client(net, 'online')
        c.run()
        
    except EOFError as e:
        print(e)
        new_message('diconnected', 1000)
        
    except PortInUse:
        menu(notice, args=['The port you requested is currently being used by another device. Try changing the default port in settings'], overlay=True)
        
    except network.NoGamesFound:
        new_message('game could not be started', 2000)
        
    except Exception as e:
        print(e, 'c2')
        new_message('an error occurred', 2000)
        
    finally:
        if 'c' in locals():
            c.exit()
        
def single_player():
    new_message('starting game...', 500)

    g = game.Game('single')
    c = client.Client(g, 'single')
    c.run()
    
    new_message('returning to main menu...', 1000)

#user settings-------------------------------------------------------------

def save_user_settings(button, username_field, port_field):
    username = username_field.get_message()
    port = int(port_field.get_message())
    
    save.set_data('username', username)
    
    if port < 1023:
        menu(notice, args=['Port value too small. Please enter a value between 1023 and 65535.'], overlay=True)
    elif port > 65535:
        menu(notice, args=['Port value too large. Please enter a value between 1023 and 65535.'], overlay=True)
    else:
        save.set_data('port', port)
        menu(notice, args=['Changes saved.'], overlay=True)
        button.set_tag('break')
        
#join game-------------------------------------------------------------
        
def join_game(ip, field):
    port = int(field.get_message())
    connect(ip, port)

def new_entry(name_field, ip_field):
    name = name_field.get_message()
    ip = ip_field.get_message()

    save.update_ips({'name': name, 'ip': ip})
    
#builder-----------------------------------------------------------------------

def run_builder(card_info={}):
    b = builder.Builder(card_info)
    b.run()
    b.cam.close()

def del_card(entry):
    r = menu(yes_no, args=['Are you sure you want to delete this card?'], overlay=True)
    if not r:
        return

    sheet = CUSTOMSHEET.sheet
    cards = CUSTOMSHEET.cards
    
    id = entry['id']
    
    if id == 0:
        return
        
    if len(cards) < 10:
        surf = pg.Surface((sheet.get_width() - 375, 525)).convert()
        x = id * 375
        surf.blit(sheet, (0, 0), (0, 0, x, 525))
        surf.blit(sheet, (x, 0), (x + 375, 0, sheet.get_width() - (x + 375), 525))

    else:
        if (len(cards) - 1) % 9 == 0:
            size = (375 * 9, sheet.get_height() - 525)
        else:
            size = (375 * 9, sheet.get_height())
            
        surf = pg.Surface(size).convert()
        found = False
        
        for row in range(sheet.get_height() // 525):
            
            if not found:
                if id // 9 == row:           
                    x = (id % 9) * 375
                    y = row * 525
                    surf.blit(sheet, (0, y), (0, y, x, 525))
                    surf.blit(sheet, (x, y), (x + 375, y, sheet.get_width() - (x + 375), 525))
                    found = True
                else:
                    surf.blit(sheet, (0, row * 525), (0, row * 525, sheet.get_width(), 525))
            else:
                surf.blit(sheet, (8 * 375, (row - 1) * 525), (0, row * 525, 375, 525))
                surf.blit(sheet, (0, row * 525), (375, row * 525, 8 * 375, 525))
    
    pg.image.save(surf, 'img/customsheet.png')
    save.del_card(entry)
    
    CUSTOMSHEET.refresh()
