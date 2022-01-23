import socket
import subprocess
import sys
import traceback

import urllib.request

import pygame as pg

import save
import network
import builder
import client
import game

import image_handler
import spritesheet
import customsheet

from constants import *
import ui

def init():
    globals()['SAVE'] = save.get_save()
    globals()['IMAGE_HANDLER'] = image_handler.get_image_handler()
    globals()['SPRITESHEET'] = spritesheet.get_sheet()
    globals()['CUSTOMSHEET'] = customsheet.get_sheet()
    
#errors----------------------------------------------------------------

class PortInUse(Exception):
    pass
    
#objects---------------------------------------------------------------

class Button_Timer(ui.Base_Object):
    def __init__(self, button, start_time, new_message):
        self.button = button
        self.textbox = button.object
        self.new_message = new_message
        self.original_message = self.textbox.get_message()
        self.start_time = start_time
        self.timer = 0
        super().__init__()
        
    def update(self):
        if self.button.get_state():
            self.button.object.set_message(self.new_message)
            self.timer = self.start_time
        if self.timer:
            self.timer -= 1
            if self.timer == 0:
                self.textbox.set_message(self.original_message)

#menus-----------------------------------------------------------------

def main_menu():
    objects = []
    
    b = ui.Button.text_button('single player', size=(200, 25), func=single_player)
    b.rect.center = (width // 2, height // 2)
    b.rect.midbottom = b.rect.midtop
    objects.append(b)
    
    b = ui.Button.text_button('host game', size=(200, 25), func=start_game)
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = ui.Button.text_button('find online game', size=(200, 25), func=ui.Menu.build_and_run, args=[select_host_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = ui.Button.text_button('find local game', size=(200, 25), func=connect, args=['', SAVE.get_data('port')])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = ui.Button.text_button('card builder', size=(200, 25), func=ui.Menu.build_and_run, args=[builder_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = ui.Button.text_button('settings', size=(200, 25), func=ui.Menu.build_and_run, args=[settings_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    b = ui.Button.text_button('exit game', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    b.rect.y += b.rect.height
    objects.append(b)
    
    ui.Position.center_objects_y(objects)
    
    b.rect.y += b.rect.height
    
    return objects

def settings_menu():
    objects = []
    
    t = ui.Textbox.static_textbox('display name:  ')
    t.rect.right = width // 2
    t.rect.bottom = height // 2
    t.rect.midbottom = t.rect.midtop
    objects.append(t)
    
    t = ui.Input((100, 0), message=SAVE.get_data('username'), color=(0, 0, 0), fgcolor=(255, 255, 255), length=50, scroll=True)
    t.rect.midleft = objects[-1].rect.midright
    objects.append(t)

    t = ui.Textbox.static_textbox('default port:  ')
    t.rect.right = width // 2
    t.rect.y = objects[-1].rect.bottom + 5
    objects.append(t)
    
    i = ui.Input((200, 0), message=str(SAVE.get_data('port')), color=(0, 0, 0), fgcolor=(255, 255, 255), 
                    check=ui.Input.positive_int_check, length=5)
    i.rect.midleft = objects[-1].rect.midright
    objects.append(i)

    b = ui.Button.text_button('reset save data', size=(200, 25), func=reset_save, tag='refresh')
    b.rect.centerx = width // 2
    b.rect.y = objects[-1].rect.bottom
    b.rect.y += b.rect.height
    objects.append(b)
    
    b = ui.Button.text_button('save', size=(200, 25), func=save_user_settings)
    b.set_args(args=[b, objects[1], objects[3]])
    b.rect.centerx = width // 2
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    b = ui.Button.text_button('cancel', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    return objects

def select_host_menu():
    objects = []
    
    w = ui.Live_Window((300, 300), label='saved ips:', label_height=30)
    w.rect.centerx = width // 2
    w.rect.y = 70
    objects.append(w)
    
    buttons = []
    for entry in SAVE.get_data('ips'):
        message = f"{entry['name']}: {entry['ip']}"
        b = ui.Button.text_button(message, padding=(10, 3), func=ui.Menu.build_and_run, args=[join_game_menu, entry['name'], entry['ip']], tag='refresh')
        buttons.append(b)
    w.join_objects(buttons)
    objects += buttons

    b = ui.Button.text_button('new entry', size=(200, 25), func=ui.Menu.build_and_run, args=[new_entry_menu], kwargs={'overlay': True}, tag='refresh')
    if objects:
        b.rect.midtop = objects[0].rect.midbottom   
    else:
        b.rect.midbottom = (width // 2, height // 2) 
    b.rect.y += 20
    objects.append(b)
    
    b = ui.Button.text_button('view my ip', size=(200, 25), func=ui.Menu.build_and_run, args=[view_ip_menu])
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
        
    b = ui.Button.text_button('back', size=(200, 25), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += b.rect.height
    objects.append(b)

    return objects

def new_entry_menu():
    objects = []
    
    window = ui.Image_Manager.get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = ui.Image(window)
    window.rect.center = (width // 2, height // 2)
    objects.append(window)
    body = window.rect
    
    input_box = ui.Image_Manager.get_surface((130, 25), color=(0, 0, 0), width=1, olcolor=(255, 255, 255))

    x0 = body.centerx - 10
    x1 = body.centerx + 10
    y0 = body.centery - 20
    y1 = body.centery + 20
    
    tb = ui.Textbox.static_textbox('entry name: ')
    tb.rect.right = x0
    tb.rect.centery = y0
    name_entry = ui.Input.from_image(input_box, message='name', tsize=15)
    name_entry.rect.left = x1
    name_entry.rect.centery = y0
    objects += [tb, name_entry]

    tb = ui.Textbox.static_textbox('entry IP: ')
    tb.rect.right = x0
    tb.rect.centery = y1
    ip_entry = ui.Input.from_image(input_box, message='255.255.255.255', tsize=15, check=lambda txt: txt.isnumeric() or txt == '.', scroll=True)
    ip_entry.rect.left = x1
    ip_entry.rect.centery = y1
    objects += [tb, ip_entry]
    
    b = ui.Button.text_button('save', size=(150, 25), func=new_entry, args=[name_entry, ip_entry])
    b.set_tag('break')
    b.rect.centerx = body.right - b.rect.width // 2
    b.rect.y = body.bottom + b.rect.height + 5
    objects.append(b)
    
    b = ui.Button.text_button('cancel', size=(150, 25))
    b.set_tag('break')
    b.rect.centerx = body.left + b.rect.width // 2
    b.rect.y = body.bottom + b.rect.height + 5
    objects.append(b)
 
    return objects
   
def view_ip_menu():
    objects = []
    
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    window = ui.Image_Manager.get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = ui.Image(window)
    window.rect.center = (width // 2, height // 2)
    objects.append(window)
    body = window.rect

    t = ui.Textbox.static_textbox(f'your online IP:  {public_ip}')
    t.rect.midbottom = (width // 2, height // 2)
    objects.append(t)
    
    text_kwargs = {'fgcolor': (255, 255, 0)}
    b = ui.Button.text_button('copy online IP to clipboard', padding=(10, 0), color1=(0, 0, 0, 0), color2=(128, 128, 0), text_kwargs=text_kwargs, func=ui.Input.copy_to_clipboard, args=[public_ip])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    t = Button_Timer(b, 125, 'coppied')
    objects.append(t)
    
    t = ui.Textbox.static_textbox(f'your local IP: {local_ip}')
    t.rect.midtop = objects[-2].rect.midbottom
    t.rect.y += 5
    objects.append(t)
    
    b = ui.Button.text_button('copy local IP to clipboard', padding=(10, 0), color1=(0, 0, 0, 0), color2=(128, 128, 0), text_kwargs=text_kwargs, func=ui.Input.copy_to_clipboard, args=[local_ip])
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    t = Button_Timer(b, 125, 'coppied')
    objects.append(t)
    
    b = ui.Button.text_button('back', tag='break')
    b.rect.midtop = objects[-2].rect.midbottom
    objects.append(b)
    
    ui.Position.center_objects_y(objects[1:-1], rect=body, padding=5)
    
    b.rect.y += b.rect.height
    
    return objects

def join_game_menu(name, ip):
    objects = []
    
    window = ui.Image_Manager.get_surface((350, 150), color=(100, 100, 100), border_radius=10, olcolor=(0, 0, 128), width=5)
    window = ui.Image(window)
    window.rect.center = (width // 2, height // 2)
    objects.append(window)
    body = window.rect
    
    x0 = body.centerx - 10
    x1 = body.centerx + 10
    y0 = body.top + body.height // 4
    y1 = body.centery
    y2 = body.bottom - body.height // 4
    
    t = ui.Textbox.static_textbox('name: ')
    t.rect.midright = (x0, y0)
    objects.append(t)
    
    t = ui.Textbox.static_textbox(name)
    t.rect.midleft = (x1, y0)
    objects.append(t)

    t = ui.Textbox.static_textbox('ip: ')
    t.rect.midleft = (objects[-2].rect.x, y1)
    objects.append(t)
    
    t = ui.Textbox.static_textbox(ip)
    t.rect.midleft = (x1, y1)
    objects.append(t)
    
    t = ui.Textbox.static_textbox('port: ')
    t.rect.midleft = (objects[-2].rect.x, y2)
    objects.append(t)
    
    input_box = ui.Image_Manager.get_surface((60, 30), color=(0, 0, 0), width=1, olcolor=(255, 255, 255))
    
    i = ui.Input.from_image(input_box, message=str(SAVE.get_data('port')), length=4, check=ui.Input.positive_int_check, tsize=20)
    i.rect.midleft = (x1 - 5, y2)
    objects.append(i)
    
    for o in objects[1:]:
        o.rect.x -= 30
        
    b = ui.Button.text_button('back', size=(100, 24), color1=(0, 0, 0), color2=(255, 0, 0))
    b.set_tag('break')
    b.rect.midtop = (body.right - (body.width * 0.33), body.bottom + 15)
    objects.append(b)
        
    b = ui.Button.text_button('join game', size=(100, 24), color1=(0, 0, 0), color2=(0, 255, 0), func=join_game, args=[ip, objects[-2]])
    b.rect.midtop = (body.left + (body.width * 0.33), body.bottom + 15)
    objects.append(b)
    
    b = ui.Button.image_button(IMAGE_HANDLER.get_image('trash'), padding=(5, 5), color1=(0, 0, 0, 0), color2=(128, 0, 0), border_radius=5,
                               func=del_ip, args=[{'name': name, 'ip': ip}])
    b.set_tag('break')
    b.rect.topright = (body.right - 10, body.y + 10)
    objects.append(b)
    
    return objects

def builder_menu():
    objects = []
    
    w = ui.Live_Window((300, 300), label='custom cards:', label_height=30)
    w.rect.centerx = width // 2
    w.rect.y = 70
    objects.append(w)

    cards = SAVE.get_data('cards').copy()
    
    buttons = []
    for c in cards:
        name = c['name']
        b = ui.Button.text_button(name, size=(200, 22), func=ui.Menu.build_and_run, args=[card_edit_menu, c], tag='refresh')
        buttons.append(b)    
    w.join_objects(buttons)
    objects += buttons
        
    b = ui.Button.text_button('new', padding=(10, 2), func=run_builder, args=[SAVE.get_new_card_data()], tag='refresh')
    b.rect.midbottom = (width // 2, height)
    b.rect.y -= b.rect.height * 2
    objects.append(b)
    
    b = ui.Button.text_button('back', padding=(10, 2), tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.y += 5
    objects.append(b)
    
    return objects

def card_edit_menu(card):
    objects = []

    t = ui.Textbox.static_textbox(card['name'] + ':', tsize=30)
    t.rect.centerx = width // 2
    objects.append(t)
    
    i = ui.Image(CUSTOMSHEET.get_image(card['name'], size=(card_width // 3, card_height // 3)))
    i.rect.midtop = objects[-1].rect.midbottom
    i.rect.y += 5
    objects.append(i)
    
    b = ui.Button.text_button('edit card', func=run_builder, kwargs={'card_info': card}, tag='break')
    b.rect.centerx = width // 2
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    if card['id'] != 0:
        b = ui.Button.text_button('delete card', func=del_card, args=[card], tag='break')
        b.rect.centerx = width // 2
        b.rect.y = objects[-1].rect.bottom + 5
        objects.append(b)
    
    b = ui.Button.text_button('back', tag='break')
    b.rect.centerx = width // 2
    b.rect.y = objects[-1].rect.bottom + b.rect.height
    objects.append(b)
    
    ui.Position.center_objects_y(objects)
    
    return objects

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
    
def reset_save():
    menu = ui.Menu.yes_no('Are you sure you want to reset your save data?', overlay=True)
    r = menu.run()
    if r:
        SAVE.reset_save()
        
def del_ip(entry):
    menu = ui.Menu.yes_no('Delete this entry?', overlay=True)
    r = menu.run()
    if r:
        SAVE.del_ips(entry)

#main--------------------------------------------------------------------

def connect(ip, port):
    menu = ui.Menu.timed_message('searching for game...', 25)
    menu.run()

    try:       
        net = network.Network(ip, port)
        c = client.Client(net, mode='online')
        c.run()
        
    except network.InvalidIP:
        menu = ui.Menu.notice('An invalid IP address has been entered.', overlay=True)
        menu.run()
        
    except network.NoGamesFound:  
        menu = ui.Menu.notice('no games could be found', overlay=True)
        menu.run()
        
    except EOFError as e:
        print(e)
        menu = ui.Menu.timed_message('disconnecting...', 25)
        menu.run()
        
    except Exception as e: 
        print(e, 'c1')
        print(traceback.format_exc())
        menu = ui.Menu.timed_message('en error occurred', 25)
        menu.run()
        
    finally:
        if 'c' in locals():
            c.exit()
        
def start_game():
    menu = ui.Menu.timed_message('starting game...', 10)
    menu.run()

    try:
    
        pipe = subprocess.Popen([sys.executable, 'server.py'], stderr=sys.stderr, stdout=sys.stdout)
        
        try:
            _, error = pipe.communicate(timeout=1)
            if 'PortInUse' in error.decode():
                raise PortInUse
        except subprocess.TimeoutExpired:
            pass

        net = network.Network(get_local_ip(), SAVE.get_data('port'))
        c = client.Client(net, mode='online')
        c.run()
        
    except EOFError as e:
        print(e)
        menu = ui.Menu.timed_message('disconnected', 10)
        menu.run()
        
    except PortInUse:
        message = 'The port you requested is currently being used by another device. Try changing the default port in settings'
        menu = ui.Menu.notice(message, overlay=True)
        menu.run()
        
    except network.NoGamesFound:
        menu = ui.Menu.notice('game could not be started', 10)
        menu.run()
       
    except Exception as e:
        print(e)
        menu = ui.Menu.notice('an error occurred', 10)
        menu.run()
        
    finally:
        if 'c' in locals():
            c.exit()
        
def single_player():
    menu = ui.Menu.timed_message('starting game...', 10)
    menu.run()

    g = game.Game(mode='single')
    c = client.Client(g, 'single')
    c.run()
    
    menu = ui.Menu.timed_message('returning to main menu...', 25)
    menu.run()

#user settings-------------------------------------------------------------

def save_user_settings(button, username_field, port_field):
    username = username_field.object.get_message()
    port = int(port_field.object.get_message())
    
    SAVE.set_data('username', username)
    
    if port < 1023:
        message = 'Port value too small. Please enter a value between 1023 and 65535.'
    elif port > 65535:
        message = 'Port value too large. Please enter a value between 1023 and 65535.'
    else:
        SAVE.set_data('port', port)
        message = 'Changes saved.'
    notice = ui.Menu.notice(message=message, overlay=True)
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
    b.cam.close()

def del_card(entry):
    r = menu(yes_no, args=['Are you sure you want to delete this card?'], overlay=True)
    if not r:
        return

    CUSTOMSHEET.del_card(entry)
