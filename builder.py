import pygame as pg

import os
import cv2
from tkinter import Tk
from tkinter import filedialog

import customsheet

import save
from constants import *
from ui import *

def init():
    globals()['CUSTOMSHEET'] = customsheet.get_sheet()
    
def reset(info):
    CUSTOMSHEET.reset()
    c = Card(name=info['name'], description=info['description'], tags=info['tags'], color=info['color'], id=info['id'], image=info['image'])
    save_card(c, suppress=True)

#Button funcs----------------------------------------------------------------------
     
def init_colors():
    images = []
    
    for i in range(3):
        
        color = [0, 0, 0]
        surf = pg.Surface((1, 255)).convert()

        for y in range(0, 256):

            color[i] = y
            surf.set_at((0, y), color)
            
        images.append(surf)
                
    return images
    
def build_card(name, description, tags, color=[161, 195, 161], image='img/user.png', id=None, save=False):
    name = name.title()
    
    if len(tags) > 1: 
        tags = str(tags).replace("'", '')
    elif tags: 
        tags = tags[0]
    else:
        tags = ''
    c = Card(name=name, description=description, tags=tags, color=color, id=id, image=image)
    
    if save:
        save_card(c)
    
    return c.get_card_image()

def save_card(card, suppress=False):
    sheet = CUSTOMSHEET.sheet
    cards = CUSTOMSHEET.cards

    if card.name in NAMES or ((card.name in CUSTOMSHEET.names and card.id != CUSTOMSHEET.get_id(card.name)) and not suppress):
        menu(notice, args=['A card with that name already exists.'], overlay=True)
        return
  
    id = card.id

    if id <= len(cards) - 1:
        surf = sheet
        pos = ((id % 9) * 375, (id // 9) * 525)
    elif not cards:
        surf = pg.Surface((375, 525)).convert()
        pos = (0, 0)
    elif not len(cards) % 9:
        surf = pg.Surface((sheet.get_width(), sheet.get_height() + 525)).convert()
        pos = (0, sheet.get_height())
    elif len(cards) < 9:
        surf = pg.Surface((sheet.get_width() + 375, 525)).convert()
        pos = (len(cards) * 375, 0)
    else:
        surf = pg.Surface(sheet.get_size()).convert()
        pos = ((len(cards) % 9) * 375, (len(cards) // 9) * 525)

    surf.blit(sheet, (0, 0))
    surf.blit(card.get_card_image(), pos)
    
    pg.image.save(card.pic, card.get_image_path())
    pg.image.save(surf, 'img/customsheet.png')
    #if id == 0:
    #    pg.image.save(card.get_card_image(), 'img/user_card.png')
    
    card_info = card.get_info()
    save.update_cards(card_info)
    
    if not suppress:
        new_message('card saved!', 2000)
    
    CUSTOMSHEET.refresh()

class Card:
    def __init__(self, name='Title', description='description', tags='tags', color=[161, 195, 161], id=None, image=''):
        self.file = 'newcard.txt'
        
        self.id = save.new_card_id() if id is None else id
        
        self.rects = {}
        self.textboxes = {}
        self.elements = {}
        
        self.color = color
        self.bg = pg.Surface((345, 500)).convert()
        self.bg.fill(self.color)
        
        self.image = pg.Surface(card_size).convert_alpha()
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect()
        
        bg = pg.Surface((345, 500)).convert_alpha()
        bg.fill((1, 1, 1))
        bg_rect = bg.get_rect()
        bg_rect.center = self.rect.center
        self.image.blit(bg, bg_rect)
        self.rects['bg'] = bg_rect

        title = pg.Surface((225, 45)).convert()
        title.fill((255, 255, 255))
        title_textbox = title.get_rect()
        title = rect_outline(title)
        title_rect = title.get_rect()
        title_rect.centerx = bg_rect.centerx
        title_rect.y = 30
        title_textbox.center = title_rect.center
        self.image.blit(title, title_rect)
        self.rects['name'] = title_rect
        self.textboxes['name'] = title_textbox

        pic = self.load_pic(image)
        pic_rect = pic.get_rect()
        pic_rect.centerx = self.rects['bg'].centerx
        pic_rect.y = self.rects['name'].bottom + 10
        window = pic.copy()
        window.fill((0, 0, 0, 0))
        self.image.blit(window, pic_rect)
        self.pic = pic
        self.rects['pic'] = pic_rect
        
        desc = pg.Surface((225, 170)).convert()
        desc.fill((255, 255, 255))
        desc_textbox = desc.get_rect()
        desc = rect_outline(desc)
        desc_rect = desc.get_rect()
        desc_rect.centerx = self.rects['bg'].centerx
        desc_rect.y = 300
        desc_textbox.center = desc_rect.center
        self.image.blit(desc, desc_rect)
        self.rects['desc'] = desc_rect
        self.textboxes['desc'] = desc_textbox
        
        tags_image = pg.Surface((230, 20)).convert()
        tags_image.fill((255, 255, 255))
        tags_textbox = tags_image.get_rect()
        tags_image = rect_outline(tags_image)
        tags_rect = tags_image.get_rect()
        tags_rect.centerx = self.rects['bg'].centerx
        tags_rect.y = 480 - 5
        tags_textbox.center = tags_rect.center
        self.image.blit(tags_image, tags_rect)
        self.rects['tags'] = tags_rect
        self.textboxes['tags'] = tags_textbox
        
        self.image.set_colorkey((1, 1, 1))
        
        self.set_screen(name, description, tags)
            
        self.update()
      
    @property
    def name(self):
        return self.elements['name'].get_message()
        
    @property
    def description(self):
        return self.elements['desc'].get_message()
        
    @property
    def tags(self):
        return self.elements['tags'].get_message()
  
    def load_pic(self, path):
        if os.path.exists(path):
            pic = pg.image.load(path).convert_alpha()
        else:
            pic = pg.Surface((card_width - 75, 210)).convert_alpha()
        pic = pg.transform.smoothscale(pic, (card_width - 75, 210))
        return pic
        
    def set_screen(self, name, description, tags):
        tb = self.textboxes['name']
        i = Input((tb.width - 5, tb.height - 5), message=name, fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0), tsize=30)
        i.rect.center = self.textboxes['name'].center
        self.elements['name'] = i
        
        tb = self.textboxes['desc']
        i = Input((tb.width - 5, tb.height - 5), message='description', fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0), tsize=35, length=300)
        i.rect.center = self.textboxes['desc'].center
        self.elements['desc'] = i
        i.update_message(description)
        
        tb = self.textboxes['tags']
        i = Input((tb.width - 5, tb.height - 5), message=str(tags), fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0), tsize=50)
        i.rect.center = self.textboxes['tags'].center
        self.elements['tags'] = i

    def is_user(self):
        return self.id == 0
        
    def get_image_path(self):
        return f'img/custom/{self.id}.png'
    
    def get_info(self):
        return {'name': self.name, 'description': self.description, 'tags': self.tags, 
                'color': self.color, 'image': self.get_image_path(), 'id': self.id}
            
    def update_color(self, rgb, val):
        self.color[rgb] = val
        self.bg.fill(self.color)
            
    def update_image(self, img):
        self.pic = pg.transform.smoothscale(img, self.rects['pic'].size)
        
    def clear_image(self):
        self.pic.fill(self.color)

    def get_card_image(self):
        image = pg.Surface(self.rect.size).convert()
        image.blit(self.bg, self.rects['bg'])
        img = self.image.copy()
        img.set_colorkey((50, 50, 50))
        image.blit(img, (0, 0))
        
        image.blit(rect_outline(self.pic), self.rects['pic'])
        
        for e in self.elements.values(): 
            e.draw(image)

        return image

    def write(self, start_node):
        tabs = 0
        with open(self.file, 'w+') as f:
            
            CLASS = self.title_text.title().replace(' ', '')
            NAME = self.title_text.lower()
            TYPES = '[]'
            
            f.write(def_line.format(CLASS, NAME, TYPES))
            tabs = 2
            
            parse_node(f, tabs, start_node)
            
    def events(self, input):
        for e in self.elements.values():
            e.events(input)
            
    def update(self):
        for e in self.elements.values():
            e.update()
        
    def draw(self, win):
        win.blit(self.bg, self.rects['bg'])
        win.blit(rect_outline(self.pic), self.rects['pic'])
        win.blit(self.image, self.rect)
        
        for e in self.elements.values():
            e.draw(win)

class VideoCapture:  
    def start(self):
        self.vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
    def get_frame(self):
        _, frame = self.vid.read()
        if frame is not None:
            image = pg.image.frombuffer(frame.tobytes(), frame.shape[1::-1], 'BGR').convert()
            return image
            
    def close(self):
        if hasattr(self, 'vid'):
            self.vid.release()
            cv2.destroyAllWindows()
        
class Builder:
    def __init__(self, card_info):
        self.screen = pg.display.get_surface()
        self.frame = pg.Surface((width, height)).convert()
        
        self.clock = pg.time.Clock()
        
        self.running = True
        
        self.cam = VideoCapture()
        self.recording = False

        self.elements = {'card': Card(**card_info)}
        
        self.input = []
        
        self.set_screen()
        
    def close(self):
        self.cam.close()

    def set_screen(self):
        x = self.elements['card'].rect.right + 10
        
        for i, rgb in enumerate(('r', 'g', 'b')):
            
            s = RGBSlider((20, 200), rgb, hcolor=(255, 255, 255), func=self.elements['card'].update_color, args=[i])
            s.rect.topleft = (x, 10)
            s.set_state(self.elements['card'].color[i])
            self.elements[rgb] = s
            
            x += s.rect.width + 40
            
        b = Button((100, 40), 'import image', func=self.open_image)
        b.rect.topleft = self.elements['r'].rect.bottomleft
        b.rect.y += 20
        self.elements['image'] = b
        
        b = Button((100, 40), 'use webcam', func=self.record)
        b.rect.topleft = self.elements['image'].rect.bottomleft
        b.rect.y += 20
        self.elements['cam'] = b
        
        b = Button((100, 40), 'save card', func=save_card, args=[self.elements['card']])
        b.rect.topleft = self.elements['cam'].rect.bottomleft
        b.rect.y += 20
        self.elements['save'] = b
        
        b = Button((100, 40), 'return to menu', func=self.quit)
        b.rect.topleft = self.elements['save'].rect.bottomleft
        b.rect.y += 20
        self.elements['quit'] = b

    def run(self):
        while self.running:
            
            self.clock.tick(fps)
            
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        self.input = pg.event.get()
        
        for e in self.input:
            
            if e.type == pg.QUIT:
                self.running = False
            
            elif e.type == pg.KEYDOWN:
                
                if e.key == pg.K_ESCAPE:
                    self.running = False
                    
            elif e.type == pg.MOUSEBUTTONDOWN:
                pass
        
        for e in self.elements.values():
            e.events(self.input)
       
    def update(self):
        for e in self.elements.values():
            e.update()
            
        if self.recording:
            self.send_recorded_image()

        #bgc = tuple(self.elements[rgb].get_state() for rgb in ('r', 'g', 'b'))
        #self.elements['card'].fill_bg(bgc)

    def draw(self):
        self.frame.fill((0, 0, 0))

        for e in self.elements.values():
            e.draw(self.frame)

        self.screen.blit(self.frame, (0, 0))
        pg.display.flip()
        
    def quit(self):
        self.running = False
        self.cam.close()
   
    def record(self):
        self.recording = not self.recording
        
        if self.recording:
            
            self.elements['cam'].update_message('take picture')
            self.cam.start()
            
        else:
            
            self.elements['cam'].update_message('use webcam')
            self.cam.close()

    def open_image(self):
        self.cam.close()

        Tk().withdraw()
        file = filedialog.askopenfilename(initialdir='/', title='select an image', filetypes=(('image files', '*.jpg'), ('image files', '*.png')))
        
        if file:
        
            image = pg.image.load(file).convert()
            self.elements['card'].update_image(image)
            
    def send_recorded_image(self):
        image = self.cam.get_frame()
        if image is not None:
            self.elements['card'].update_image(image)















