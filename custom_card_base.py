import os

import pygame as pg

from ui import rect_outline, Input, menu, notice, new_message

card_width = 375
card_height = 525

card_size = (375, 525)

class Card:
    @staticmethod
    def build_card(info):
        c = Card(**info)
        return c.get_card_image()
        
    def __init__(self, name='Title', description='description', tags='tags', color=[161, 195, 161], id=None, image='', node_data={}, weight=1, published=False, lines=(0, 0), **kwargs):
        self.id = id
        self.node_data = node_data
        self.weight = weight
        self.published = published
        self.lines = lines
        
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
        return self.elements['name'].get_message().lower()
        
    @property
    def description(self):
        return self.elements['desc'].get_message()
        
    @property
    def tags(self):
        return self.elements['tags'].get_message()
        
    @property
    def classname(self):
        return self.name.title().replace(' ', '_')
  
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
        return {'name': self.name, 'description': self.description, 'tags': self.tags, 'color': self.color, 
                'image': self.get_image_path(), 'id': self.id, 'node_data': self.node_data, 'weight': self.weight, 
                'classname': self.classname, 'custom': True, 'published': self.published, 'lines': self.lines}
            
    def update_color(self, rgb, val):
        self.color[rgb] = val
        self.bg.fill(self.color)
        
    def set_node_data(self, node_data):
        if self.node_data != node_data:
            self.node_data = node_data
            self.published = False
            
    def set_lines(self, s, e):
        self.lines = (s, e)
        
    def publish(self, s, e):
        self.set_lines(s, e)
        self.published = True
        import game
        game.load_custom_cards()
            
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
            
    def save(self, suppress=False):
        import customsheet
        CUSTOMSHEET = customsheet.get_sheet()
        if not CUSTOMSHEET:
            return
        saved = CUSTOMSHEET.save_card(self)
        if not suppress:
            if not saved:
                menu(notice, args=['A card with that name already exists.'], overlay=True)
                return
            else:
                new_message('card saved!', 2000)
        return saved
        
    
