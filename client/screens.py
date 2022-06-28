from data.save import SAVE, CONSTANTS

from ui.geometry import position
from ui.element.standard import Textbox, Button, Text_Flipper
from ui.menu import Menu

WIDTH, HEIGHT = CONSTANTS['screen_size']
CENTER = CONSTANTS['center']

def game_options_menu(client):
    objects = []

    b = Button.text_button('disconnect', tag='break', func=client.disconnect)
    b.rect.midtop = CENTER
    objects.append(b)
    
    b = Button.text_button('game settings', func=Menu.build_and_run, args=[settings_menu, client])
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    if client.is_host():
        b = Button.text_button('new game', tag='break', func=client.send, args=['reset'])
        b.rect.midtop = objects[-1].rect.midbottom
        objects.append(b)
        
    b = Button.text_button('back', tag='break')
    b.rect.midtop = objects[-1].rect.midbottom
    objects.append(b)
    
    position.center_objects_y(objects)

    return objects

def settings_menu(client):
    objects = []

    settings = client.get_settings()

    space = 70
    x0 = (WIDTH // 2) - space
    x1 = x0 + (2 * space)
    
    t = Textbox.static_textbox('rounds: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting score: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting cards: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting items: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('starting spells: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('number of cpus: ')
    t.rect.centerx = x0
    objects.append(t)
    
    t = Textbox.static_textbox('cpu difficulty: ')
    t.rect.centerx = x0
    objects.append(t)
    
    position.center_objects_y(objects)
    row_sep = len(objects)
    
    c = Text_Flipper.counter(range(1, 6), index=settings['rounds'] - 1, size=(50, 25))
    c.set_tag('rounds')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(5, 51), index=settings['ss'] - 5, size=(50, 25))
    c.set_tag('ss')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(1, 11), index=settings['cards'] - 1, size=(50, 25))
    c.set_tag('cards')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 6), index=settings['items'], size=(50, 25))
    c.set_tag('items')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 4), index=settings['spells'], size=(50, 25))
    c.set_tag('spells')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(1, 15), index=settings['cpus'] - 1, size=(50, 25))
    c.set_tag('cpus')
    c.rect.centerx = x1
    objects.append(c)

    c = Text_Flipper.counter(range(0, 5), index=settings['diff'], size=(50, 25))
    c.set_tag('diff')
    c.rect.centerx = x1
    objects.append(c)
    
    position.center_objects_y(objects[row_sep:])

    counters = [c for c in objects if isinstance(c, Text_Flipper)]
    if not client.is_host():
        for c in counters:
            c.set_enabled(False)
    else:
    
        def save_game_settings(client, counters):
            settings = {c.tag: int(c.current_value) for c in counters}  
            SAVE.set_data('settings', settings)
            client.update_settings(settings)
            
        b = Button.text_button('save', size=(100, 25), func=save_game_settings, args=[client, counters])
        b.set_tag('break')
        b.rect.midtop = objects[-1].rect.midbottom
        b.rect.y += b.rect.height
        b.rect.centerx = WIDTH // 2
        objects.append(b)
        
    b = Button.text_button('back', size=(100, 25))
    b.set_tag('break')
    b.rect.midtop = objects[-1].rect.midbottom
    b.rect.centerx = WIDTH // 2
    objects.append(b)

    return objects
