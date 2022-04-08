import os
import cv2
from tkinter import Tk
from tkinter import filedialog

import pygame as pg

from custom_card_base import Card

import ui
import save
from constants import *

import node_editor

def init():
    globals()['SAVE'] = save.get_save()
    node_editor.init()

#Button funcs----------------------------------------------------------------------

def save_card(card, ne):
    card.save(nodes=ne.nodes)
    
def publish_card(card, ne):
    card.publish(nodes=ne.nodes)

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
        
class Builder(ui.Menu):
    def __init__(self, card_info):
        self.cam = VideoCapture()
        self.recording = False

        self.card = Card(**card_info)
        self.node_editor = node_editor.Node_Editor(self.card)
        
        self.objects_dict = {'card': self.card}
        super().__init__(get_objects=self.builder_objects)
        
    def close(self):
        self.cam.close()

    def builder_objects(self):
        objects = self.card.objects + [self.card]
        
        x = self.objects_dict['card'].rect.right + 10
        
        for i, rgb in enumerate(('r', 'g', 'b')):
            
            s = ui.RGBSlider((20, 200), 'y', rgb, hcolor=(255, 255, 255), func=self.update_color)
            s.rect.topleft = (x, 10)
            s.set_state(self.objects_dict['card'].color[i])
            objects.append(s)
            self.objects_dict[rgb] = s
            
            x += s.rect.width + 40
            
        b = ui.Button.text_button('import image', func=self.open_image)
        b.rect.topleft = self.objects_dict['r'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['image'] = b
        
        b = ui.Button.text_button('use webcam', func=self.record)
        b.rect.topleft = self.objects_dict['image'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['cam'] = b
        
        b = ui.Button.text_button('node editor', func=self.node_editor.run)
        b.rect.topleft = self.objects_dict['cam'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['node_editor'] = b
    
        b = ui.Button.text_button('save card', func=save_card, args=[self.card, self.node_editor])
        b.rect.topleft = self.objects_dict['node_editor'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['save'] = b

        b = ui.Button.text_button('publish card', func=publish_card, args=[self.card, self.node_editor])
        b.rect.topleft = self.objects_dict['save'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['publish'] = b
       
        b = ui.Button.text_button('return to menu', tag='break')
        b.rect.topleft = self.objects_dict['publish'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['quit'] = b

        t = ui.Textbox('published: False', tsize=20)
        t.set_func(self.update_published)
        t.rect.topleft = self.objects_dict['quit'].rect.topright
        t.rect.x += 20
        objects.append(t)
        self.objects_dict['published'] = t
        
        return objects
       
    def update(self):
        super().update()
            
        if self.recording:
            self.send_recorded_image()
        
    def quit(self):
        self.cam.close()
        super().quit()
   
    def record(self):
        self.recording = not self.recording
        
        if self.recording: 
            self.objects_dict['cam'].object.set_message('take picture')
            self.cam.start()  
        else:
            self.objects_dict['cam'].object.set_message('use webcam')
            self.cam.close()

    def open_image(self):
        self.cam.close()

        Tk().withdraw()
        file = filedialog.askopenfilename(initialdir='/', title='select an image', filetypes=(('image files', '*.jpg'), ('image files', '*.png')))
        
        if file:
            image = pg.image.load(file).convert()
            self.objects_dict['card'].update_image(image)
            
    def send_recorded_image(self):
        image = self.cam.get_frame()
        if image is not None:
            self.objects_dict['card'].update_image(image)

    def update_published(self):
        t = self.objects_dict['published']
        if self.card.published and 'True' not in t.message:
            t.fgcolor = (0, 255, 0)
            t.set_message('published: True')
        elif not self.card.published and 'False' not in t.message:
            t.fgcolor = (255, 0, 0)
            t.set_message('published: False')

    def update_color(self):
        r = self.objects_dict['r']
        g = self.objects_dict['g']
        b = self.objects_dict['b']
        
        color = [r.get_state(), g.get_state(), b.get_state()]
        self.objects_dict['card'].set_color(color)







