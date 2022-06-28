import os
import shutil
import ast

import pygame as pg

from data.save import CONSTANTS, CUSTOM_IMG_PATH, CUSTOM_SND_PATH, TEMP_SND_PATH

from node.node.node_base import pack
from node.parser import Node_Parser
from node.tester import tester

from ui.image import get_surface
from ui.element.base import Compound_Object
from ui.element.standard import Image, Textbox, Input
from ui.menu import Menu

CARD_SIZE = CONSTANTS['card_size']
CARD_WIDTH, CARD_HEIGHT = CARD_SIZE
IMAGE_SIZE = (CARD_WIDTH - 75, 210)

def is_valid_code(code):
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return True

class Card(Compound_Object):
    @staticmethod
    def load_pic(path):
        if os.path.exists(path):
            pic = pg.image.load(path).convert_alpha()
            pic = pg.transform.smoothscale(pic, IMAGE_SIZE)
        else:
            pic = pg.Surface(IMAGE_SIZE).convert_alpha()
        return pic
        
    @classmethod
    def build_card(cls, info):
        self = cls(**info)
        return self.get_card_image()
   
    def __init__(
        self,
        name='name',
        type='play',
        description='description',
        tags=None,
        color=[161, 195, 161],
        id=None, 
        image='',
        sound=None,
        node_data={},
        weight=1,
        code='',
        lines=(0, 0),
        published=False,
        **kwargs
    ):
        super().__init__()
        
        self.sound = sound
        self.id = id
        self.node_data = node_data
        self.weight = weight
        self.code = code
        self.lines = lines
        self.published = published
        
        if tags is None:
            tags = []

        self.image = pg.Surface(CARD_SIZE).convert_alpha()
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect()
        r = self.rect.inflate(-30, -30)
        pg.draw.rect(self.image, (1, 0, 0), r)
        self.image.set_colorkey((1, 0, 0))

        self.objects_dict = {}

        bg = Image(pg.Surface(r.size).convert())
        bg.image.fill(color)
        bg.rect.center = self.rect.center
        self.add_child(bg, current_offset=True)
        self.objects_dict['bg'] = bg
        
        style_kwargs = {
            'padding': (5, 5),
            'color': (255, 255, 255),
            'outline_width': 2,
            'outline_color': (0, 0, 0),
            'border_radius': 0
        }
        
        text_kwargs = {
            'fitted': True,
            'fgcolor': (0, 0, 0)
        }

        name = Input(size=(255, 45), message=name, default='name', tsize=30, **text_kwargs, **style_kwargs)
        print(name.rect, name.textbox.rect)
        name.rect.centerx = bg.rect.centerx
        name.rect.y = 30
        self.add_child(name, current_offset=True)
        self.objects_dict['name'] = name
        
        pw, ph = IMAGE_SIZE
        pic_outline = Image.from_style((pw + 4, ph + 4), color=(0, 0, 0))
        pic_outline.rect.centerx = bg.rect.centerx
        pic_outline.rect.y = name.rect.bottom + 6
        self.objects_dict['pic_outline'] = pic_outline
        self.add_child(pic_outline, current_offset=True)

        pic = Image(Card.load_pic(image))
        pic.rect.center = pic_outline.rect.center
        self.objects_dict['pic'] = pic
        self.add_child(pic, current_offset=True)

        desc = Input(size=(255, 170), message=description, default='description', tsize=35, length=300, **text_kwargs, **style_kwargs)
        desc.rect.centerx = bg.rect.centerx
        desc.rect.y += 300
        self.add_child(desc, current_offset=True)
        self.objects_dict['desc'] = desc
        
        type_box_image = get_surface(((pic.rect.width // 3) - 4, 20), color=(255, 255, 255), olcolor=(0, 0, 0))
        type_box = Image(type_box_image)
        type_box.rect.x = pic.rect.x
        type_box.rect.y += 475
        self.add_child(type_box, current_offset=True)
        self.objects_dict['type_box'] = type_box
        type_rect = type_box_image.get_rect()
        
        type = Textbox(type, tsize=45, fgcolor=(0, 0, 0))
        type.fit_text(type_rect)
        type.rect.center = type_box.rect.center
        self.add_child(type, current_offset=True)
        self.objects_dict['type'] = type
        
        tags_box_image = get_surface((pic.rect.width - type.rect.width - 4, 20), color=(255, 255, 255), olcolor=(0, 0, 0))
        tags_box = Image(tags_box_image)
        tags_box.rect.right = pic.rect.right
        tags_box.rect.y += 475
        self.add_child(tags_box, current_offset=True)
        self.objects_dict['tags_box'] = tags_box
        tags_rect = tags_box_image.get_rect()

        tags = Textbox(str(tags).replace("'", ''), tsize=45, fgcolor=(0, 0, 0))
        tags.fit_text(tags_rect)
        tags.rect.center = tags_box.rect.center
        self.add_child(tags, current_offset=True)
        self.objects_dict['tags'] = tags
        
        self.update()
      
    @property
    def name(self):
        return self.objects_dict['name'].message.lower()
        
    @property
    def type(self):
        return self.objects_dict['type'].message
        
    @property
    def description(self):
        return self.objects_dict['desc'].message
        
    @property
    def tags(self):
        tags = self.objects_dict['tags'].message.strip('[]').split(', ')
        if '' in tags:
            tags.remove('')
        return tags
        
    @property
    def classname(self):
        name = self.name.title().replace(' ', '_')
        
        cname = ''
        for char in name:
            if char.isalnum() or char == '_':
                cname += char
                
        if cname[0].isnumeric():
            cname = '_' + cname

        return cname
        
    @property
    def color(self):
        return list(self.objects_dict['bg'].image.get_at((0, 0)))
        
    @property
    def pic(self):
        return self.objects_dict['pic'].image
        
    @property
    def image_path(self):
        return f'{CUSTOM_IMG_PATH}{self.id}.png'
        
    @property
    def sound_path(self):
        return f'{CUSTOM_SND_PATH}{self.id}.wav'
        
    def get_info(self):
        info = {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'tags': self.tags, 
            'color': self.color, 
            'image': self.image_path,
            'sound': self.sound,
            'id': self.id,
            'weight': self.weight, 
            'classname': self.classname, 
            'custom': True,
            'code': self.code,
            'lines': self.lines,
            'published': self.published,
            'node_data': self.node_data
        }
        return info
 
    def is_user(self):
        return self.id == 0
        
    def set_color(self, color):
        self.objects_dict['bg'].fill(color)  
            
    def update_image(self, img):
        self.objects_dict['pic'].set_image(img)
        
    def clear_image(self):
        self.objects_dict['pic'].fill(self.color)
        
    def get_card_image(self):
        img = self.image.copy()
        self.draw(img)
        return img
        
    def set_type(self, type):
        tb = self.objects_dict['type']
        tb.set_message(type)
        r = self.objects_dict['type_box'].image.get_rect()
        tb.fit_text(r)
        tb.rect.center = self.objects_dict['type_box'].rect.center
        tb.set_current_offset()
        
    def add_tag(self, tag):
        tags = self.tags
        if tag not in tags:
            tags.append(tag)
            tb = self.objects_dict['tags']
            tb.set_message(str(tags).replace("'", ''))
            r = self.objects_dict['tags_box'].image.get_rect()
            tb.fit_text(r)
            tb.rect.center = self.objects_dict['tags_box'].rect.center
            tb.set_current_offset()
        
    def remove_tag(self, tag):
        tags = self.tags
        if tag in tags:
            tags.remove(tag)
            tb = self.objects_dict['tags']
            tb.set_message(str(tags).replace("'", ''))
            r = self.objects_dict['tags_box'].image.get_rect()
            tb.fit_text(r)
            tb.rect.center = self.objects_dict['tags_box'].rect.center
            tb.set_current_offset()
            
    def set_weight(self, weight):
        self.weight = weight
            
    def set_sound(self):
        path = f'{TEMP_SND_PATH}custom.wav'
        if os.path.exists(path):
            shutil.copyfile(path, self.sound_path)
            self.sound = self.sound_path
        else:
            if os.path.exists(self.sound_path):
                os.remove(self.sound_path)
            self.sound = None

    def set_node_data(self, nodes):
        data = pack(nodes)
        self.node_data = data
        
        prev_code = self.code
        parser = Node_Parser(self, nodes)
        code = parser.get_text()
        self.set_code(code)
        
        if prev_code != code:
            self.published = False
            
        return parser
   
    def set_code(self, code):
        self.code = code
            
    def set_lines(self, s, e):
        self.lines = (s, e)
        
    def publish(self, nodes=None):
        if nodes is not None:
            parser = self.set_node_data(nodes)
            missing = parser.missing
            if missing:
                if len(missing) == 1:
                    text = f'Missing {missing[0]} node.\n'
                else:
                    text = f"Missing {', '.join(missing)} nodes.\n"
                m = Menu.notice(text, tsize=20, size=(400, 200))
                m.run()
                return
            
        if not self.code:
            m = Menu.notice('No writable nodes found.')
            m.run()
            return
            
        saved = self.save(suppress=True)
        if not saved:
            m = Menu.notice('An error occurred while saving.')
            m.run()
            return
        
        if not is_valid_code(self.code):
            m = Menu.notice('Error: invalid code.')
            m.run()
            return
  
        passed = tester.run_tester(self)
        if not passed:
            return

        from data.save import SAVE
        s, e = SAVE.publish_card(self)
        self.set_lines(s, e)
        
        self.published = True
        self.save(suppress=True)
        
        m = Menu.notice('Card has been published successfully!')
        m.run()
        
    def draw(self, surf):
        super().draw(surf)
        surf.blit(self.image, self.rect)
            
    def save(self, nodes=None, suppress=False):
        self.set_sound()
        
        if nodes is not None:
            self.set_node_data(nodes)
            
        from spritesheet.customsheet import CUSTOMSHEET
        saved = CUSTOMSHEET.save_card(self)
        if not suppress:
            if not saved:
                menu = Menu.notice('A card with that name already exists.', overlay=True)
                menu.run()
                return
            else:
                menu = Menu.timed_message('Card saved successfully!', 50, overlay=True)
                menu.run()
        return saved
        
    
