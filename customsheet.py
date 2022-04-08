import os
import pygame as pg
import save
from spritesheet_base import Base_Sheet
from custom_card_base import Card
from constants import *

def init():
    globals()['SAVE'] = save.get_save()
    globals()['CUSTOMSHEET'] = Customsheet()

def get_sheet():
    return globals().get('CUSTOMSHEET')
    
class Customsheet(Base_Sheet):
    @staticmethod
    def get_blank_custom():
        if os.path.exists('img/user.png'):
            img = pg.image.load('img/user.png').convert()
        else:
            img = pg.Surface((1, 1)).convert() 
        img = pg.transform.smoothscale(img, (card_width - 75, 210))
        return img
    
    def __init__(self):
        names = tuple([c['name'] for c in self.cards])
        super().__init__(names, 'img/customsheet.png')
        if self.failed_to_load():
            self.create_blank_sheet()
            self.restore_data()
        for d in self.cards:
            path = d['image']
            self.get_card_image(path)
            
    def reset(self):
        self.create_blank_sheet()
        c = Card(**self.cards[0])
        self.save_card(c)
        
    def refresh(self):
        self.names = tuple([c['name'] for c in self.cards])
        self.refresh_sheet()
        
    @property
    def cards(self):
        return SAVE.get_data('cards')
        
    def create_blank_sheet(self):
        cards = self.cards
        if len(cards) < 9:
            w = 375 * len(cards)
            h = 525
        else:
            w = 375 * 9
            h = 575 * ((len(cards) // 9) + 1)
        print(w, h)
        surf = pg.Surface((w, h)).convert()
        self.resave_sheet(surf)
        
    def restore_data(self):
        data = self.cards
        for d in data:
            c = Card(**d)
            self.save_card(c)
            
    def get_card_image(self, path):
        loaded = False
        try:
            image = pg.image.load(path).convert()
            loaded = True
        except:
            image = Customsheet.get_blank_custom()
        finally:
            if not loaded:
                pg.image.save(image, path)
        return image
        
    def get_id(self, name):
        if name in self.names:
            return self.names.index(name)
            
    def check_exists(self, card):
        if card.name in NAMES:
            return True
        if card.name in self.names and card.id != self.get_id(card.name):
            return True
        #for c in self.cards:
        #    if c.get('classname') == card.classname and card.id != self.get_id(c['name']):
        #        return True
            
    def save_card(self, card):
        if self.check_exists(card):
            return

        id = card.id
        cards = self.cards
        sheet = self.sheet
        
        num = len(cards)

        if id <= num - 1:
            surf = sheet
            pos = ((id % 9) * 375, (id // 9) * 525)
        elif not cards:
            surf = pg.Surface((375, 525)).convert()
            pos = (0, 0)
        elif not num % 9:
            surf = pg.Surface((sheet.get_width(), sheet.get_height() + 525)).convert()
            pos = (0, sheet.get_height())
        elif num < 9:
            surf = pg.Surface((sheet.get_width() + 375, 525)).convert()
            pos = (num * 375, 0)
        else:
            surf = pg.Surface(sheet.get_size()).convert()
            pos = ((num % 9) * 375, (num // 9) * 525)

        surf.blit(sheet, (0, 0))
        surf.blit(card.get_card_image(), pos)

        pg.image.save(card.pic, card.image_path)
        self.resave_sheet(surf)  
        SAVE.update_cards(card.get_info())
        self.refresh()
        return True
        
    def del_card(self, entry):        
        id = entry['id']
        sheet = self.sheet
        cards = self.cards
        
        if id == 0:
            return
            
        if len(cards) < 10:
            surf = pg.Surface((sheet.get_width() - 375, 525)).convert()
            x = id * 375
            surf.blit(sheet, (0, 0), (0, 0, x, 525))
            surf.blit(sheet, (x, 0), (x + 375, 0, sheet.get_width() - (x + 375), 525))

        else:
            if (len(cards) - 1) % 9 == 0:
                size = (375 * 9, sheet.get_height() - 525)
            else:
                size = (375 * 9, sheet.get_height())
                
            surf = pg.Surface(size).convert()
            found = False
            
            for row in range(sheet.get_height() // 525):
                
                if not found:
                    if id // 9 == row:           
                        x = (id % 9) * 375
                        y = row * 525
                        surf.blit(sheet, (0, y), (0, y, x, 525))
                        surf.blit(sheet, (x, y), (x + 375, y, sheet.get_width() - (x + 375), 525))
                        found = True
                    else:
                        surf.blit(sheet, (0, row * 525), (0, row * 525, sheet.get_width(), 525))
                else:
                    surf.blit(sheet, (8 * 375, (row - 1) * 525), (0, row * 525, 375, 525))
                    surf.blit(sheet, (0, row * 525), (375, row * 525, 8 * 375, 525))
        
        self.resave_sheet(surf)
        SAVE.del_card(entry)
        self.refresh()
