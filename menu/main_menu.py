import subprocess
import sys
import traceback

import pygame as pg

from data.save import SAVE, CONSTANTS
from network.network import Network
from network.net_base import get_public_ip, get_local_ip
from builder import builder
from client import client
from game import game
from spritesheet.customsheet import CUSTOMSHEET

from ui.icons.icons import icons
from ui.image import get_surface
from ui.geometry import position
from ui.element.background import Button_Timer, On_Click
from ui.element.standard import Image, Textbox, Button, Input
from ui.element.window import Live_Window
from ui.menu import Menu

import exceptions

WIDTH, HEIGHT = CONSTANTS['screen_size']
CENTER = CONSTANTS['center']
CENTERX = WIDTH // 2
CENTERY = HEIGHT // 2
CARD_WIDTH, CARD_HEIGHT = CONSTANTS['card_size']

#menus-----------------------------------------------------------------

def main_menu():
    objects = []
    
    b = Button.text_button('single player', size=(200, 25), func=single_player)
    b.rect.center = CENTER
    b.rect.midbottom = b.rect.midtop
    objects.append(b)
    
    b = Button.text_button('host game', size=(200, 25), func=start_game)
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('find online game', size=(200, 25), func=Menu.build_and_run, args=[select_host_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('find local game', size=(200, 25), func=connect, args=['', SAVE.get_data('port')])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('card builder', size=(200, 25), func=Menu.build_and_run, args=[builder_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('settings', size=(200, 25), func=Menu.build_and_run, args=[settings_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = Button.text_button('exit game', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    b.rect.y += b.rect.height
    objects.append(b)
    
    position.center_objects_y(objects)
    
    b.rect.y += b.rect.height

    return objects

def settings_menu():
    objects = []
    
    t = Textbox.static_textbox('display name:  ')
    t.rect.right = CENTERX
    t.rect.bottom = CENTERY
    t.rect.midbottom = t.rect.midtop
    objects.append(t)
    
    t = Input(size=(100, 20), message=SAVE.get_data('username'), color=(0, 0, 0), fgcolor=(255, 255, 255), length=50, scroll=True)
    t.rect.midleft = objects[-1].rect.midright
    objects.append(t)

    t = Textbox.static_textbox('default port:  ')
    t.rect.right = CENTERX
    t.rect.y = objects[-1].rect.bottom + 5
    objects.append(t)
    
    i = Input(
        size=(200, 20), message=str(SAVE.get_data('port')), color=(0, 0, 0), fgcolor=(255, 255, 255), 
        check=Input.positive_int_check, length=5
    )
    i.rect.midleft = objects[-1].rect.midright
    objects.append(i)

    b = Button.text_button('reset save data', size=(200, 25), func=reset_save, tag='refresh')
    b.rect.centerx = CENTERX
    b.rect.y = objects[-1].rect.bottom
    b.rect.y += b.rect.height
    objects.append(b)
    
    b = Button.text_button('save', size=(200, 25), func=save_user_settings)
    b.set_args(args=[b, objects[1], objects[3]])
    b.rect.centerx = CENTERX
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    b = Button.text_button('cancel', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    return objects

def select_host_menu():
    objects = []
    
    w = Live_Window((300, 300))
    w.rect.centerx = CENTERX
    w.rect.y = 70
    objects.append(w)
    objects.append(w.get_label('saved ips:', height=30))
    
    buttons = []
    for entry in SAVE.get_data('ips'):
        message = f"{entry['name']}: {entry['ip']}"
        b = Button.text_button(message, padding=(10, 3), func=Menu.build_and_run, args=[join_game_menu, entry['name'], entry['ip']], tag='refresh', ohandle=True)
        buttons.append(b)
    w.join_objects(buttons)
    objects += buttons

    b = Button.text_button('new entry', size=(200, 25), func=Menu.build_and_run, args=[new_entry_menu], kwargs={'overlay': True}, tag='refresh')
    if objects:
        b.rect.midtop = objects[0].rect.midbottom   
    else:
        b.rect.midbottom = CENTER 
    b.rect.y += 20
    objects.append(b)
    
    b = Button.text_button('view my ip', size=(200, 25), func=Menu.build_and_run, args=[view_ip_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
        
    b = Button.text_button('back', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += b.rect.height
    objects.append(b)

    return objects

def new_entry_menu():
    objects = []
    
    window = get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = Image(window)
    window.rect.center = CENTER
    objects.append(window)
    body = window.rect
    
    input_box = get_surface((130, 25), color=(0, 0, 0), width=1, olcolor=(255, 255, 255))

    x0 = body.centerx - 10
    x1 = body.centerx + 10
    y0 = body.centery - 20
    y1 = body.centery + 20
    
    tb = Textbox.static_textbox('entry name: ')
    tb.rect.right = x0
    tb.rect.centery = y0
    name_entry = Input.from_image(input_box, default='name', tsize=15)
    name_entry.rect.left = x1
    name_entry.rect.centery = y0
    objects += [tb, name_entry]

    tb = Textbox.static_textbox('entry IP: ')
    tb.rect.right = x0
    tb.rect.centery = y1
    ip_entry = Input.from_image(input_box, default='255.255.255.255', tsize=15, check=lambda txt: txt.isnumeric() or txt == '.', scroll=True)
    ip_entry.rect.left = x1
    ip_entry.rect.centery = y1
    objects += [tb, ip_entry]
    
    b = Button.text_button('save', size=(150, 25), func=new_entry, args=[name_entry, ip_entry])
    b.set_tag('break')
    b.rect.centerx = body.right - b.rect.width // 2
    b.rect.y = body.bottom + b.rect.height + 5
    objects.append(b)
    
    b = Button.text_button('cancel', size=(150, 25))
    b.set_tag('break')
    b.rect.centerx = body.left + b.rect.width // 2
    b.rect.y = body.bottom + b.rect.height + 5
    objects.append(b)
 
    return objects
   
def view_ip_menu():
    objects = []
    
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    window = get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = Image(window)
    window.rect.center = CENTER
    objects.append(window)
    body = window.rect

    t = Textbox.static_textbox(f'your online IP:  {public_ip}')
    t.rect.midbottom = CENTER
    objects.append(t)

    b = Button.text_button('copy online IP to clipboard', padding=(10, 0), color1=(0, 0, 0, 0), color2=(128, 128, 0), fgcolor=(255, 255, 0), func=Input.copy_to_clipboard, args=[public_ip])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    t = Button_Timer(b, 125, 'coppied')
    objects.append(t)
    
    t = Textbox.static_textbox(f'your local IP: {local_ip}')
    t.rect.midtop = objects[-2].rect.midbottom
    t.rect.y += 5
    objects.append(t)
    
    b = Button.text_button('copy local IP to clipboard', padding=(10, 0), color1=(0, 0, 0, 0), color2=(128, 128, 0), fgcolor=(255, 255, 0), func=Input.copy_to_clipboard, args=[local_ip])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    t = Button_Timer(b, 125, 'coppied')
    objects.append(t)
    
    b = Button.text_button('back', tag='break')
    b.rect.midtop = objects[-2].rect.midbottom
    objects.append(b)
    
    position.center_objects_y(objects[1:-1], rect=body, padding=5)
    
    b.rect.y += b.rect.height
    
    return objects

def join_game_menu(name, ip):
    objects = []
    
    window = get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = Image(window)
    window.rect.center = CENTER
    objects.append(window)
    body = window.rect
    
    x0 = body.centerx - 10
    x1 = body.centerx + 10
    y0 = body.top + body.height // 4
    y1 = body.centery
    y2 = body.bottom - body.height // 4
    
    t = Textbox.static_textbox('name: ')
    t.rect.midright = (x0, y0)
    objects.append(t)
    
    t = Textbox.static_textbox(name)
    t.rect.midleft = (x1, y0)
    objects.append(t)

    t = Textbox.static_textbox('ip: ')
    t.rect.midleft = (objects[-2].rect.x, y1)
    objects.append(t)
    
    t = Textbox.static_textbox(ip)
    t.rect.midleft = (x1, y1)
    objects.append(t)
    
    t = Textbox.static_textbox('port: ')
    t.rect.midleft = (objects[-2].rect.x, y2)
    objects.append(t)
    
    input_box = get_surface((60, 30), color=(0, 0, 0), width=1, olcolor=(255, 255, 255))
    
    i = Input.from_image(input_box, message=str(SAVE.get_data('port')), length=4, check=Input.positive_int_check, tsize=20)
    i.rect.midleft = (x1 - 5, y2)
    objects.append(i)
    
    for o in objects[1:]:
        o.rect.x -= 30
        
    b = Button.text_button('back', size=(100, 24), color1=(0, 0, 0), color2=(255, 0, 0))
    b.set_tag('break')
    b.rect.midtop = (body.right - (body.width * 0.33), body.bottom + 15)
    objects.append(b)
        
    b = Button.text_button('join game', size=(100, 24), color1=(0, 0, 0), color2=(0, 255, 0), func=join_game, args=[ip, objects[-2]])
    b.rect.midtop = (body.left + (body.width * 0.33), body.bottom + 15)
    objects.append(b)

    b = Button.text_button(
        icons['trash'], padding=(5, 5), color1=(0, 0, 0, 0), color2=(128, 0, 0), border_radius=5,
        func=del_ip, args=[{'name': name, 'ip': ip}], text_kwargs={'font': 'icons'}
    )
    b.set_tag('break')
    b.rect.topright = (body.right - 10, body.y + 10)
    objects.append(b)
    
    return objects

def builder_menu():
    objects = []
    
    w = Live_Window(size=(300, 300))
    w.rect.centerx = CENTERX
    w.rect.y = 70
    objects.append(w)
    objects.append(w.get_label('custom cards:', height=30))

    cards = SAVE.get_data('cards').copy()
    
    buttons = []
    for c in cards:
        name = c['name']
        b = Button.text_button(name, size=(200, 22), func=Menu.build_and_run, args=[card_edit_menu, c], tag='refresh', ohandle=True)
        buttons.append(b)    
    w.join_objects(buttons)
    objects += buttons

    b = Button.text_button('new', padding=(10, 2), func=run_builder, args=[SAVE.get_new_card_data()], tag='refresh')
    b.rect.midbottom = (CENTERX, HEIGHT)
    b.rect.y -= b.rect.height * 2
    objects.append(b)
    
    b = Button.text_button('back', padding=(10, 2), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    return objects

def card_edit_menu(card):
    objects = []

    t = Textbox.static_textbox(card['name'] + ':', tsize=30)
    t.rect.centerx = CENTERX
    objects.append(t)
    
    i = Image(CUSTOMSHEET.get_image(card['name'], size=(CARD_WIDTH // 3, CARD_HEIGHT // 3)))
    i.rect.midtop = objects[-1].rect.midbottom
    i.rect.y += 5
    objects.append(i)
    
    b = Button.text_button('edit card', func=run_builder, kwargs={'card_info': card}, tag='break')
    b.rect.centerx = CENTERX
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    if card['id'] != 0:
        b = Button.text_button('delete card', func=del_card, args=[card], tag='break')
        b.rect.centerx = CENTERX
        b.rect.y = objects[-1].rect.bottom + 5
        objects.append(b)
    
    b = Button.text_button('back', tag='break')
    b.rect.centerx = CENTERX
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    position.center_objects_y(objects)
    
    return objects

#other-------------------------------------------------------------------
    
def reset_save():
    menu = Menu.yes_no('Are you sure you want to reset your save data?', overlay=True)
    r = menu.run()
    if r:
        SAVE.reset_save()
        
def del_ip(entry):
    menu = Menu.yes_no('Delete this entry?', overlay=True)
    r = menu.run()
    if r:
        SAVE.del_ips(entry)

#main--------------------------------------------------------------------

def connect(ip, port):
    menu = Menu.timed_message('searching for game...', 25)
    menu.run()

    try:       
        net = Network(ip, port)
        c = client.Client(net, mode='online')
        c.run()
        
    except exceptions.InvalidIP:
        menu = Menu.notice('An invalid IP address has been entered.', overlay=True)
        menu.run()
        
    except exceptions.NoGamesFound:  
        menu = Menu.notice('no games could be found', overlay=True)
        menu.run()
        
    except EOFError as e:
        print(e)
        menu = Menu.timed_message('disconnecting...', 25)
        menu.run()
        
    except Exception as e: 
        print(e, 'c1')
        print(traceback.format_exc())
        menu = Menu.timed_message('en error occurred', 25)
        menu.run()
        
    finally:
        if 'c' in locals():
            c.exit()
        
def start_game():
    menu = Menu.timed_message('starting game...', 10)
    menu.run()

    try:
        pipe = subprocess.Popen([sys.executable, 'server.py'], stderr=sys.stderr, stdout=sys.stdout)
        
        try:
            _, error = pipe.communicate(timeout=1)
            if 'PortInUse' in error.decode():
                raise exceptions.PortInUse
        except subprocess.TimeoutExpired:
            pass

        net = Network(get_local_ip(), SAVE.get_data('port'))
        c = client.Client(net, mode='online')
        c.run()
        
    except EOFError as e:
        print(e)
        menu = Menu.timed_message('disconnected', 10)
        menu.run()
        
    except exceptions.PortInUse:
        message = 'The port you requested is currently being used by another device. Try changing the default port in settings'
        menu = Menu.notice(message, overlay=True)
        menu.run()
        
    except exceptions.NoGamesFound:
        menu = Menu.notice('game could not be started', 10)
        menu.run()
       
    except Exception as e:
        print(e, traceback.format_exc())
        menu = Menu.notice('an error occurred', 10)
        menu.run()
        
    finally:
        if 'c' in locals():
            c.exit()
        
def single_player():
    menu = Menu.timed_message('starting game...', 10)
    menu.run()

    g = game.Game(mode='single')
    c = client.Client(g, 'single')
    c.run()
    
    menu = Menu.timed_message('returning to main menu...', 25)
    menu.run()

#user settings-------------------------------------------------------------

def save_user_settings(button, username_field, port_field):
    username = username_field.textbox.get_message()
    port = int(port_field.textbox.get_message())
    
    SAVE.set_data('username', username)
    
    if port < 1023:
        message = 'Port value too small. Please enter a value between 1023 and 65535.'
    elif port > 65535:
        message = 'Port value too large. Please enter a value between 1023 and 65535.'
    else:
        SAVE.set_data('port', port)
        message = 'Changes saved.'
    notice = Menu.notice(message=message, overlay=True)
    notice.run()
        
#join game-------------------------------------------------------------
        
def join_game(ip, field):
    port = int(field.textbox.get_message())
    connect(ip, port)

def new_entry(name_field, ip_field):
    name = name_field.textbox.get_message()
    ip = ip_field.textbox.get_message()
    SAVE.update_ips({'name': name, 'ip': ip})
    
#builder-----------------------------------------------------------------------

def run_builder(card_info):
    b = builder.Builder(card_info)
    b.run()
    b.close()

def del_card(entry):
    m = Menu.yes_no('Are you sure you want to delete this card?', overlay=True)
    r = m.run()
    if r:
        CUSTOMSHEET.del_card(entry)
