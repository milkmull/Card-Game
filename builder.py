import shutil
from tkinter import filedialog

import pygame as pg

from video_capture import Video_Capture
from audio_capture import Audio_Capture
from custom_card_base import Card
from node_editor import Node_Editor

from ui.image import get_surface
from ui.element.base import Compound_Object
from ui.element.standard import Image, Textbox, Button, Input, Text_Flipper, Slider, Dropdown
from ui.element.extended import Dropdown_Multi_Select, RGBSlider
from ui.menu import Menu
    
#visual stuff----------------------------------------------------------------------

class Type_Selector(Dropdown):
    def __init__(self, card, ne):
        types = (
            'play',
            'item',
            'spell',
            'treasure',
            'landscape',
            'event'
        )
        super().__init__(types, selected=card.type)
        self.card = card
        self.ne = ne

    def set_value(self, type):
        m = Menu.yes_no('Changing the card type could result in some nodes being deleted.\nAre you sure you want to change the card type?')
        if m.run():
            super().set_value(type)
            self.card.set_type(type)
            self.ne.load_required_nodes()
        
class Tag_Selector(Dropdown_Multi_Select):
    def __init__(self, card):
        from save import SAVE
        all_tags = SAVE.get_sheet_info('tags')
        tags = all_tags['biomes'] + all_tags['descriptors']
        super().__init__(tags, 3)
        self.card = card
        
        for tag in self.card.tags:
            self.add_value(tag)
        
    def add_value(self, tag):
        if super().add_value(tag):
            self.card.add_tag(tag)
        
    def remove_value(self, tb, b):
        tag = tb.get_message()
        super().remove_value(tb, b)
        self.card.remove_tag(tag)

class Audio_Manager(Compound_Object):
    def __init__(self, card, mic):
        super().__init__()
        self.rect = pg.Rect(0, 0, 1, 1)
        
        self.card = card
        self.mic = mic
        self.sound = None
        self.sound_length = 0
        self.playing_sound = False
        self.start_time = 0
        
        self.record_image = get_surface((14, 14), key=(0, 0, 0))
        self.stop_image = self.record_image.copy()
        self.play_image = self.record_image.copy()
        self.clear_image = self.record_image.copy()
        self.import_image = self.record_image.copy()
        
        pg.draw.circle(self.record_image, (255, 0, 0), (7, 7), 7)
        self.stop_image.fill((0, 0, 255))
        pg.draw.polygon(self.play_image, (0, 255, 0), ((0, 0), (0, 14), (14, 7)))
        pg.draw.line(self.clear_image, (255, 0, 0), (-2, -2), (16, 16), width=3)
        pg.draw.line(self.clear_image, (255, 0, 0), (-2, 16), (16, -2), width=3)
        pg.draw.polygon(self.import_image, (255, 255, 0), ((0, 0), (6, 0), (6, 2), (14, 2), (14, 14), (0, 14)))

        b = Button.image_button(self.record_image, func=self.start_record, padding=(2, 2))
        b.rect.topleft = self.rect.topleft
        self.add_child(b, current_offset=True)
        self.record_button = b
        
        b = Button.image_button(self.play_image, func=self.play_sound, padding=(2, 2))
        b.rect.midleft = self.record_button.rect.midright
        b.rect.x += 10
        self.add_child(b, current_offset=True)
        b.turn_off()
        self.play_button = b
        
        b = Button.image_button(self.clear_image, func=self.clear_sound, padding=(2, 2))
        b.rect.midleft = self.play_button.rect.midright
        b.rect.x += 10
        self.add_child(b, current_offset=True)
        b.turn_off()
        self.clear_button = b
        
        s = Slider((200, 5), range(200), hcolor=(255, 0, 0))
        s.rect.topleft = self.record_button.rect.bottomleft
        s.rect.y += 15
        self.add_child(s, current_offset=True)
        self.bar = s
        s.set_enabled(False)
        
        b = Button.image_button(self.import_image, func=self.import_file, padding=(2, 2))
        b.rect.bottomright = self.bar.rect.topright
        b.rect.y -= 15
        self.add_child(b, current_offset=True)
        self.import_button = b
        
        if card.sound:
            self.load_sound(path=card.sound_path)

    def start_record(self):
        if self.playing_sound:
            self.stop_sound()
            
        self.mic.start()
        
        b = self.record_button
        b.object.set_image(self.stop_image)
        b.set_func(self.stop_record)

    def stop_record(self):
        self.mic.stop()
        if self.mic.saved_file:
            self.load_sound()
        self.mic.reset()
        
        self.bar.set_state(0)
        
        b = self.record_button
        b.object.set_image(self.record_image)
        b.set_func(self.start_record)
        
    def import_file(self):
        file = filedialog.askopenfilename(initialdir='/', title='select a sound', filetypes=(('sound files', '*.wav'), ('sound files', '*.ogg')))
        if file:
            self.load_sound(path=file)
            
    def load_sound(self, path=None):
        temp_path = self.mic.get_path()
        if path is not None:
            shutil.copyfile(self.card.sound_path, temp_path)
  
        self.sound = pg.mixer.Sound(temp_path)
        self.sound_length = self.sound.get_length()
        
        self.play_button.turn_on()
        self.clear_button.turn_on()
 
    def play_sound(self):
        self.playing_sound = True
        self.start_time = pg.time.get_ticks()
        self.sound.play()
        
        b = self.play_button
        b.object.set_image(self.stop_image)
        b.set_func(self.stop_sound)
        
    def stop_sound(self):
        self.sound.stop()
        self.playing_sound = False
        
        self.bar.set_state(0)
        
        b = self.play_button
        b.object.set_image(self.play_image)
        b.set_func(self.play_sound)
        
    def clear_sound(self):
        if self.sound:
            self.stop_sound()
            self.sound = None
        self.mic.clear_path()
            
        self.play_button.turn_off()
        self.clear_button.turn_off()
            
    def update(self):
        super().update()

        if self.mic.recording:
            s = self.mic.get_current_length() / 5
            self.bar.set_state_as_ratio(s)
        if self.mic.finished:
            self.stop_record()
                
        if self.playing_sound:
            s = (pg.time.get_ticks() - self.start_time) / (1000 * self.sound_length)
            self.bar.set_state_as_ratio(s)
            if s >= 1:
                self.stop_sound()
                
    def draw(self, surf):
        super().draw(surf)
        r = pg.Rect(self.bar.rect.x, self.bar.rect.y, self.bar.handel.rect.centerx - self.bar.rect.x, self.bar.rect.height)
        pg.draw.rect(surf, (255, 0, 0), r)
   
class Builder(Menu):
    def __init__(self, card_info):
        self.cam = Video_Capture()
        self.mic = Audio_Capture(5)

        self.card = Card(**card_info)
        self.node_editor = Node_Editor(self.card)
        
        self.objects_dict = {'card': self.card}
        super().__init__(get_objects=self.builder_objects)
        
    def close(self):
        self.cam.close()
        self.mic.close()
    
    def quit(self):
        self.close()
        super().quit()

    def builder_objects(self):
        objects = [self.card]
        
        x = self.objects_dict['card'].rect.right + 10
        
        for i, rgb in enumerate(('r', 'g', 'b')):
            
            s = RGBSlider((20, 200), 'y', rgb, hcolor=(255, 255, 255), func=self.update_color)
            s.rect.topleft = (x, 10)
            s.set_state(self.objects_dict['card'].color[i])
            objects.append(s)
            self.objects_dict[rgb] = s
            
            x += s.rect.width + 40
            
        type_text = Textbox.static_textbox('card type:', fgcolor=(255, 255, 255))
        type_text.rect.topleft = s.rect.topleft
        type_text.rect.x += 50
        objects.append(type_text)

        ts = Type_Selector(self.card, self.node_editor)
        ts.rect.midtop = type_text.rect.midbottom
        ts.rect.y += 5
        objects.append(ts)
        self.objects_dict['type_select'] = ts

        f = Text_Flipper.counter(range(1, 5), size=(50, 20), index=self.card.weight - 1)
        f.rect.topleft = s.rect.bottomright
        f.rect.x += 100
        objects.append(f)
        self.objects_dict['weight'] = f
        
        def set_weight():
            w = int(f.current_value)
            self.card.set_weight(w)
            
        f.set_func(set_weight)
            
        tag_text = Textbox.static_textbox('card tags:', fgcolor=(255, 255, 255))
        tag_text.rect.topleft = type_text.rect.topright
        tag_text.rect.x += 50
        objects.append(tag_text)
        
        tag_select = Tag_Selector(self.card)
        tag_select.rect.midtop = tag_text.rect.midbottom
        tag_select.rect.y += 5
        objects.append(tag_select)
        self.objects_dict['tag_select'] = tag_select
        
        custom_text = Textbox.static_textbox('custom tag:', fgcolor=(255, 255, 255))
        custom_text.rect.topleft = tag_text.rect.topright
        custom_text.rect.x += 30
        objects.append(custom_text)
        
        def add_custom_tag(i, ts):
            tag = i.get_message()
            ts.add_value(tag)
            i.clear()
        
        custom = Input((100, 30), 'tag', color=(255, 255, 255), fgcolor=(0, 0, 0), check=Input.alnum_check)
        custom.set_func(add_custom_tag, args=[custom, tag_select])
        custom.rect.topleft = custom_text.rect.bottomleft
        custom.rect.y += 5
        objects.append(custom)
        self.objects_dict['custom_tag'] = custom
            
        b = Button.text_button('import image', func=self.open_image)
        b.rect.topleft = self.objects_dict['r'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['image'] = b
        
        b = Button.text_button('use webcam', func=self.record_video)
        b.rect.topleft = self.objects_dict['image'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['cam'] = b
        
        b = Button.text_button('node editor', func=self.node_editor.run)
        b.rect.topleft = self.objects_dict['cam'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['node_editor'] = b
        
        def save_card(card, ne):
            card.save(nodes=ne.nodes)

        b = Button.text_button('save card', func=save_card, args=[self.card, self.node_editor])
        b.rect.topleft = self.objects_dict['node_editor'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['save'] = b
        
        def publish_card(card, ne):
            card.publish(nodes=ne.nodes)

        b = Button.text_button('publish card', func=publish_card, args=[self.card, self.node_editor])
        b.rect.topleft = self.objects_dict['save'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['publish'] = b
       
        b = Button.text_button('return to menu', tag='break')
        b.rect.topleft = self.objects_dict['publish'].rect.bottomleft
        b.rect.y += 20
        objects.append(b)
        self.objects_dict['quit'] = b

        t = Textbox('published: False', tsize=20)
        t.set_func(self.update_published)
        t.rect.topleft = self.objects_dict['quit'].rect.topright
        t.rect.x += 20
        objects.append(t)
        self.objects_dict['published'] = t
        
        am = Audio_Manager(self.card, self.mic)
        am.rect.topleft = self.objects_dict['published'].rect.bottomleft
        am.rect.y += 20
        objects.append(am)
        self.objects_dict['audio_manager'] = am

        return objects
       
    def update(self):
        super().update()    
        if self.cam.recording:
            self.send_recorded_image()
            
#video stuff-------------------------------------------------------------------------------------
   
    def record_video(self):
        if not self.cam.recording: 
            self.objects_dict['cam'].object.set_message('take picture')
            self.cam.start()  
        else:
            self.objects_dict['cam'].object.set_message('use webcam')
            self.cam.stop()
            
    def send_recorded_image(self):
        image = self.cam.get_frame()
        if image is not None:
            self.objects_dict['card'].update_image(image)
            
#audio stff---------------------------------------------------------------------------------------

    def record_audio(self):
        if not self.mic.recording: 
            self.objects_dict['mic'].object.set_message('stop recording')
            self.mic.start()  
        else:
            self.objects_dict['mic'].object.set_message('record audio')
            self.mic.stop()
            
#image stuff--------------------------------------------------------------------------------------

    def open_image(self):
        self.cam.close()
        file = filedialog.askopenfilename(initialdir='/', title='select an image', filetypes=(('image files', '*.jpg'), ('image files', '*.png')))
        if file:
            image = pg.image.load(file).convert()
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







