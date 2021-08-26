from constants import *
from ui import rect_outline
from builder import build_card
import pygame as pg

class Spritesheet:
    def __init__(self):
        self.names = (('michael', 'dom', 'jack', 'mary', 'daniel', 'emily', 'gambling boi', 'mom', 'dad'),
                      ('aunt peg', 'uncle john', 'kristen', 'joe', 'robber', 'ninja', 'item frenzy', 'mustard stain', 'gold coins'),
                      ('gold', 'max the dog', 'basil the dog', 'copy cat', 'racoon', 'fox', 'cow', 'shark', 'fish'),
                      ('pelican', 'lucky duck', 'lady bug', 'mosquito', 'snail', 'dragon', 'clam', 'pearl', 'uphalump'),
                      ('flu', 'cactus', 'poison ivy', 'rose', 'mr. squash', 'mrs. squash', 'ghost', 'fishing pole', 'invisibility cloak'),
                      ('last turn pass', 'detergent', 'treasure chest', 'speed boost potion', 'fertilizer', 'mirror', 'sword', 'spell trap', 'item leech'),
                      ('curse', 'treasure curse', 'bronze', 'negative zone', 'item hex', 'luck', 'fishing trip', 'bath tub', 'boomerang'),
                      ('future orb', 'knife', 'magic wand', 'lucky coin', 'sapling', 'vines', 'zombie', 'jumble', 'demon water glass'),
                      ('succosecc', 'sunflower', 'lemon lord', 'wizard', 'haunted oak', 'spell reverse', 'sunny day', 'garden', 'desert'),
                      ('fools gold', 'graveyard', 'city', 'wind gust', 'sunglasses', 'metal detector', 'sand storm', 'mummy', 'mummys curse'),
                      ('pig', 'corn', 'harvest', 'golden egg', 'bear', 'big rock', 'unlucky coin', 'trap', 'hunting season'),
                      ('stardust', 'water lilly', 'torpedo', 'bat', 'sky flower', 'kite', 'balloon', 'north wind', 'garden snake'),
                      ('flower pot', 'farm', 'forest', 'water', 'sky', 'office fern', 'parade', 'camel', 'rattle snake'),
                      ('tumble weed', 'watering can', 'magic bean', 'the void', 'bug net', 'big sand worm', 'lost palm tree', 'seaweed', 'scuba baby')
                       )
               
        self.sheet, self.images = self.load_cards()

        self.extras = {'back': pg.image.load('img/back.png').convert()}
        
    def add_extra(self, name):
        self.extras[name] = create_text(name)
        
    def check_name(self, name):
        return any(name in row for row in self.names)
        
    def get_by_id(self, id):
        return self.ids.get(id)
        
    def add_player_card(self, name, color):
        description = ''
        tags = ['extra']

        img = build_card(name, description, tags, color=color)
        self.extras[name] = img
        
    def remove_player_card(self, name):
        if name in self.extras:
            del self.extras[name]
        
    def get_image(self, c, outline, scale=(cw, ch)):
        name = c.name
        
        scale = [int(s) for s in scale]

        if not self.check_name(name):

            if name in self.extras:
                
                img = self.extras[name]
                
            else:

                description = ''
                tags = ['extra']
                color = c.color if c.color is not None else (255, 255, 255)

                img = build_card(name, description, tags, color=color)
                self.extras[name] = img
        
        else:
        
            img = pg.Surface((375, 525)).convert()
            img.blit(self.sheet, (0, 0), self.images[name])

        img = pg.transform.scale(img, scale)

        if scale == [cw, ch]:
            
            olcolor = None
                
            if outline:
                olcolor = (255, 0, 0)
            elif c.color is not None:
                olcolor = c.color
      
            if olcolor is not None:
                img = rect_outline(img, color=olcolor)
        
        return img
        
    def load_cards(self):
        f = 'img/spritesheet.png'
        images = {}
        
        sheet = pg.image.load(f).convert()
        size = sheet.get_size()
        
        row = 0
        
        for y in range(0, size[1], 525):
            
            col = 0
        
            for x in range(0, size[0], 375):
                
                name = self.names[row][col]
                
                if name:
                
                    images[name] = (x, y, 375, 525)
                
                col += 1
                
            row += 1
            
        return (sheet, images)
        
        
        
        
        