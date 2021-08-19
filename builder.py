import pygame as pg
from constants import *
from ui import *
from tkinter import Tk
from tkinter import filedialog
import cv2

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
    
def build_card(name, description, tags, color=(161, 195, 161), image='img/user.jpg'):
    name = name.title()
    
    if len(tags) > 1: 
        tags = str(tags).replace("'", '')
    else: 
        tags = tags[0]
        
    c = Card(name=name, description=description, tags=tags, color=color, image=image)
    
    return c.get_image()
    
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

class Card:
    def __init__(self, name='Title', description='description', tags='tags', color=(161, 195, 161), image=''):
        self.file = 'newcard.txt'
        
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

        pic = pg.Surface((card_width - 75, 210)).convert()
        pic.fill((1, 1, 1))
        pic_textbox = pic.get_rect()
        pic = rect_outline(pic)
        pic.set_colorkey((1, 1, 1))
        pic_rect = pic.get_rect()
        pic_rect.centerx = self.rects['bg'].centerx
        pic_rect.y = self.rects['name'].bottom + 10
        self.image.blit(pic, pic_rect)
        self.pic = pic
        self.rects['pic'] = pic_rect
        self.textboxes['pic'] = pic_textbox
        
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
        
        if image:
            
            image = pg.image.load(image).convert()
            self.update_image(image)
            
        self.update()
        
    def set_screen(self, name, description, tags):
        i = Input(self.textboxes['name'].size, message=name, fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0))
        i.rect.center = self.textboxes['name'].center
        self.elements['name'] = i
        
        i = Input(self.textboxes['desc'].size, message='description', fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0))
        i.rect.center = self.textboxes['desc'].center
        self.elements['desc'] = i
        i.update_message(description)
        
        i = Input(self.textboxes['tags'].size, message=tags, fitted=True, color=(0, 0, 0, 0), tcolor=(0, 0, 0))
        i.rect.center = self.textboxes['tags'].center
        self.elements['tags'] = i
        
    @property
    def name(self):
        return self.elements['name'].get_message()
        
    @property
    def description(self):
        return self.elements['desc'].get_message()
        
    @property
    def tags(self):
        return self.elements['tags'].get_message()
        
    def fill_bg(self, color):
        if self.color != color:
            
            self.color = color
            self.bg.fill(self.color)
            
    def update_image(self, img):
        self.pic = rect_outline(pg.transform.scale(img, self.textboxes['pic'].size))
        
    def clear_image(self):
        self.pic.fill(self.color)
            
    def events(self, input):
        for e in self.elements.values():
            
            e.events(input)
            
    def update(self):
        for e in self.elements.values():
            
            e.update()
        
    def draw(self, win):
        win.blit(self.bg, self.rects['bg'])
        win.blit(self.pic, self.rects['pic'])
        win.blit(self.image, self.rect)
        
        for e in self.elements.values():
            
            e.draw(win)

    def get_image(self):
        image = pg.Surface(self.rect.size).convert()
        image.blit(self.bg, self.rects['bg'])
        img = self.image.copy()
        img.set_colorkey((50, 50, 50))
        image.blit(img, (0, 0))
        
        image.blit(self.pic, self.rects['pic'])
        
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
            
    def save(self):
        try:
        
            pg.image.save(self.get_image(), 'img/test.png')
            pg.image.save(self.pic, f'img/custom/{self.name}.png')
            
        except pygame.error:
            
            pass
        
class Builder:
    def __init__(self, win):
        self.screen = win
        self.frame = pg.Surface((width, height)).convert()
        
        self.clock = pg.time.Clock()
        
        self.running = True
        
        self.cam = VideoCapture()
        self.recording = False

        self.elements = {'card': Card()}
        
        self.input = []
        
        self.set_screen()

    def set_screen(self):
        x = self.elements['card'].rect.right + 10
        
        for rgb in ('r', 'g', 'b'):
            
            s = RGBSlider((20, 200), rgb, hcolor=(255, 255, 255))
            s.rect.topleft = (x, 10)
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
        
        b = Button((100, 40), 'save card', func=self.elements['card'].save)
        b.rect.topleft = self.elements['cam'].rect.bottomleft
        b.rect.y += 20
        self.elements['save'] = b

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

        bgc = tuple(self.elements[rgb].get_state() for rgb in ('r', 'g', 'b'))
        self.elements['card'].fill_bg(bgc)

    def draw(self):
        self.frame.fill((0, 0, 0))

        for e in self.elements.values():
            
            e.draw(self.frame)

        self.screen.blit(self.frame, (0, 0))
        pg.display.flip()
   
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

if __name__ == '__main__':

    pg.init()

    win = pg.display.set_mode((width, height))
    pg.display.set_caption('card game')
    
    b = Builder(win)  
    b.run()
    b.cam.close()
    
    pg.quit()















