import pygame as pg

import os
import cv2
from tkinter import Tk
from tkinter import filedialog

from custom_card_base import Card

import save
from constants import *
from ui import *

import nodes2

def init():
    globals()['SAVE'] = save.get_save()
    nodes2.init()

#Button funcs----------------------------------------------------------------------

def save_card(card, ne):
    node_data = ne.get_save_data()
    card.set_node_data(node_data)
    
    card.save()

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

        self.card = Card(**card_info)
        self.node_editor = nodes2.Node_Editor(self.card)
        
        self.elements = {'card': self.card}
        
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
        
        b = Button((100, 40), 'save card', func=save_card, args=[self.card, self.node_editor])
        b.rect.topleft = self.elements['cam'].rect.bottomleft
        b.rect.y += 20
        self.elements['save'] = b
        
        b = Button((100, 40), 'return to menu', func=self.quit)
        b.rect.topleft = self.elements['save'].rect.bottomleft
        b.rect.y += 20
        self.elements['quit'] = b
        
        b = Button((100, 40), 'node editor', func=self.node_editor.run)
        b.rect.topleft = self.elements['quit'].rect.bottomleft
        b.rect.y += 20
        self.elements['node_editor'] = b

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











