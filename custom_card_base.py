import os
import ast

import pygame as pg

import node_data
import node_parser
import tester

import ui

card_width = 375
card_height = 525

card_size = (375, 525)

def is_valid_code(code):
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    return True

class Card(ui.Advanced_Object):
    IMAGE_SIZE = (card_width - 75, 210)
    @staticmethod
    def build_card(info):
        c = Card(**info)
        return c.get_card_image()
        
    @classmethod
    def load_pic(cls, path):
        if os.path.exists(path):
            pic = pg.image.load(path).convert_alpha()
            pic = pg.transform.smoothscale(pic, cls.IMAGE_SIZE)
        else:
            pic = pg.Surface(cls.IMAGE_SIZE).convert_alpha()
        return pic
        
    def __init__(self, name='Title', description='description', tags='tags', color=[161, 195, 161], id=None, 
                 image='', node_data={}, weight=1, code='', lines=(0, 0), published=False, **kwargs):
        super().__init__()
        
        self.id = id
        self.node_data = node_data
        self.weight = weight
        self.code = code
        self.lines = lines
        self.published = published

        self.image = pg.Surface(card_size).convert_alpha()
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect()
        r = self.rect.inflate(-30, -30)
        pg.draw.rect(self.image, (1, 0, 0), r)
        self.image.set_colorkey((1, 0, 0))

        self.objects_dict = {}

        bg = ui.Image(pg.Surface(r.size).convert())
        bg.image.fill(color)
        bg.rect.center = self.rect.center
        self.add_child(bg, current_offset=True)
        self.objects_dict['bg'] = bg

        name_box = ui.Image_Manager.get_surface((255, 45), color=(255, 255, 255), olcolor=(0, 0, 0))
        name = ui.Input.from_image(name_box, message=name, fitted=True, color=(0, 0, 0, 0), fgcolor=(0, 0, 0), tsize=30)
        name.rect.centerx = bg.rect.centerx
        name.rect.y = 30
        self.add_child(name, current_offset=True)
        self.objects_dict['name'] = name
        
        pw, ph = Card.IMAGE_SIZE
        pic_outline = ui.Image.from_style((pw + 4, ph + 4), color=(0, 0, 0))
        pic_outline.rect.centerx = bg.rect.centerx
        pic_outline.rect.y = name.rect.bottom + 6
        self.objects_dict['pic_outline'] = pic_outline

        pic = ui.Image(Card.load_pic(image))
        pic.rect.center = pic_outline.rect.center
        self.objects_dict['pic'] = pic
        self.add_child(pic, current_offset=True)

        desc_box = ui.Image_Manager.get_surface((225, 170), color=(255, 255, 255), olcolor=(0, 0, 0))
        desc = ui.Input.from_image(desc_box, message=description, fitted=True, color=(0, 0, 0, 0), fgcolor=(0, 0, 0), tsize=35, length=300)
        desc.rect.centerx = bg.rect.centerx
        desc.rect.y += 300
        self.add_child(desc, current_offset=True)
        self.objects_dict['desc'] = desc

        tags_box = ui.Image_Manager.get_surface((230, 20), color=(255, 255, 255), olcolor=(0, 0, 0))
        tags = ui.Input.from_image(tags_box, message=str(tags), fitted=True, color=(0, 0, 0, 0), fgcolor=(0, 0, 0), tsize=50)
        tags.rect.centerx = bg.rect.centerx
        tags.rect.y += 475
        self.add_child(tags, current_offset=True)
        self.objects_dict['tags'] = tags
        
        self.objects = list(self.objects_dict.values())
      
    @property
    def name(self):
        return self.objects_dict['name'].get_message().lower()
        
    @property
    def description(self):
        return self.objects_dict['desc'].get_message()
        
    @property
    def tags(self):
        return self.objects_dict['tags'].get_message()
        
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
        return f'img/custom/{self.id}.png'
        
    def get_info(self):
        info = {
            'name': self.name,
            'description': self.description,
            'tags': self.tags, 
            'color': self.color, 
            'image': self.image_path,
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
        image = self.image.copy()
        for o in self.objects:
            o.draw_on(image, self.rect)
        return image

    def set_node_data(self, nodes):
        data = node_data.pack(nodes)
        self.node_data = data
        
        prev_code = self.code
        np = node_parser.Node_Parser(self, nodes)
        code = np.get_text()
        self.set_code(code)
        
        if prev_code != code:
            self.published = False
   
    def set_code(self, code):
        self.code = code
            
    def set_lines(self, s, e):
        self.lines = (s, e)
        
    def publish(self, nodes=None):
        if nodes is not None:
            self.set_node_data(nodes)
            
        if not self.code:
            m = ui.Menu.notice('No writable nodes found.')
            m.run()
            return
            
        saved = self.save(suppress=True)
        if not saved:
            m = ui.Menu.notice('An error occurred while saving.')
            m.run()
            return
        
        if not is_valid_code(self.code):
            m = ui.Menu.notice('Error: invalid code.')
            m.run()
            return
  
        passed = tester.run_tester(self)
        if not passed:
            return

        import save
        s = save.get_save()
        s, e = s.publish_card(self)
        self.set_lines(s, e)
        
        self.published = True
        self.save(suppress=True)
        
        m = ui.Menu.notice('Card has been published successfully!')
        m.run()
        
    def draw(self, surf):
        for o in self.objects:
            o.draw_on(self.image, self.rect)
        surf.blit(self.image, self.rect)
            
    def save(self, nodes=None, suppress=False):
        if nodes is not None:
            self.set_node_data(nodes)
            
        import customsheet
        CUSTOMSHEET = customsheet.get_sheet()
        if not CUSTOMSHEET:
            return
        saved = CUSTOMSHEET.save_card(self)
        if not suppress:
            if not saved:
                menu = ui.Menu.notice('A card with that name already exists.', overlay=True)
                menu.run()
                return
            else:
                menu = ui.Menu.timed_message('Card saved successfully!', 50, overlay=True)
                menu.run()
        return saved
        
    
