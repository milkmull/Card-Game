import pygame as pg
from constants import *

def outline_points(r):
    x, y, e = r, 0, 1 - r
    points = []

    while x >= y:
    
        points.append((x, y))
        
        y += 1
        
        if e < 0:
        
            e += 2 * y - 1
            
        else:
        
            x -= 1
            e += 2 * (y - x) - 1
            
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    
    points.sort()
    
    return points

def create_text(message, size=10, color=(255, 255, 255)): #returns surface with rendered text
    font = 'freesansbold.ttf'
    
    if '\n' not in message:
        
        text_font = pg.font.Font(font, size)
        text = text_font.render(message, size, color).convert_alpha()

    else:
        
        lines = message.split('\n')
        images = []
        
        for message in lines:
        
            text = create_text(message.strip(), size, color)
            images.append(text)
            
        w = max(img.get_size()[0] for img in images)
        h = sum(img.get_size()[1] for img in images)
        
        text = pg.Surface((w, h)).convert_alpha()
        text.fill((0, 0, 0, 0))
        
        y = 0
        
        for img in images:
            
            text.blit(img, (0, y))
            y += img.get_size()[1]

    return text

class Textbox: #used to easily position text on screen
    def __init__(self, message, tsize=10, tcolor=(255, 255, 255), is_button=True):
        self.message = message

        self.text = create_text(message, tsize, tcolor) #rendered text image

        self.rect = self.text.get_rect() #indicates where textbox is
        
        self.tsize = tsize #text size
        self.tcolor = tcolor #text color (rgb)
        self.is_button = is_button
        self.outlined = False
        self.olc = None
        
        self.uid = id(self) #id of textbox
        
    def add_background(self, color):
        bg = self.text.copy()
        bg.fill(color)
        bg.blit(self.text, (0, 0))
        
        self.text = bg
        
    def update_text_multicolor(self, message, colors):
        c = self.rect.center
        x = 0
        j = 0
        
        img = create_text(message, self.tsize)
        img.fill((0, 0, 0, 0))
        
        for i in range(len(message)):
            
            color = colors[j % len(colors)]
            char = message[i]
            
            if char != ' ':
                
                j += 1
            
            char_img = create_text(char, self.tsize, color)
            img.blit(char_img, (x, 0))
            
            x += char_img.get_size()[0]

        self.message = message
        self.text = img
        self.rect = self.text.get_rect()
        self.rect.center = c

    def add_outline(self, olc=None, r=2):
        if self.is_button:
            
            c = self.rect.center
            
            if olc and not self.outlined:

                w, h = self.rect.size
                w = w + 2 * r
                
                osurf = pg.Surface((w, h + 2 * r)).convert_alpha()
                osurf.fill((0, 0, 0, 0))
                surf = osurf.copy()
                osurf.blit(create_text(self.message, self.tsize, olc), (0, 0))
                
                for dx, dy in outline_points(r):
                
                    surf.blit(osurf, (dx + r, dy + r))

                surf.blit(self.text, (r, r))
                self.text = surf
                
                self.outlined = True
                self.olc = olc
                
            elif not olc:

                self.text = create_text(self.message, self.tsize, self.tcolor)
                self.outlined = False
                self.olc = None
            
            self.rect = self.text.get_rect()
            self.rect.center = c
            
    def get_outline(self, color=(255, 0, 0)):
        if self.outlined:
            
            bg = self.text.copy()
            bg.set_colorkey(self.tcolor)
            
            olc = pg.Surface(bg.get_size()).convert()
            olc.fill(color)
            
            bg.blit(olc, (0, 0))
            
            return bg

    def update_text(self, message, tcolor=None, olc=None): #updates the text in the text box
        if tcolor is not None:
        
            self.tcolor = tcolor
            
        c = self.rect.center #maintains the top left position of text on screen even if textbox changes size
            
        self.message = message
        self.text = create_text(message, self.tsize, self.tcolor)
        self.rect = self.text.get_rect()
        self.rect.center = c
        
        self.outlined = False
        
    def clear(self):
        self.update_text('')
        
    def get_image(self, mini=False):
        return self.text #return text image
        
class Counter:
    def __init__(self, message, counter=0, r=range(-999, 999), tsize=10, tcolor=(255, 255, 255)):
        self.textbox = Textbox(message, tsize, tcolor, False)

        self.counter = {'down': Textbox('<', tsize), 'num': Textbox(str(counter), tsize), 'up': Textbox('>', tsize)} #display for simple counter "<num>"
        self.range = r #set upper and lower limit for counter
        
        self.message = self.textbox.message
        self.rect = self.textbox.rect
        
    def update_text(self, message, tcolor=None):
        self.textbox.update_text(message, tcolor)
        
        self.move_counter()
        
    def move_counter(self): #used to move all textboxes associated with a counter textbox
        self.counter['down'].rect.midleft = self.rect.midright
        self.counter['num'].rect.midleft = self.counter['down'].rect.midright
        self.counter['up'].rect.midleft = self.counter['num'].rect.midright
        
    def get_image(self, mini=False):
        x = 0
            
        img = pg.Surface((self.rect.width + sum(t.rect.width for t in self.counter.values()), self.rect.height)).convert()
        
        img.blit(self.textbox.text, (x, 0))
        
        x += self.rect.width
        
        for t in self.counter.values():
            
            img.blit(t.text, (x, 0))
            
            x += t.rect.width
            
        return img
        
    def incriment(self, dir):
        if dir == 'up' and self.get_count() + 1 in self.range:
            
            self.counter['num'].update_text(str(int(self.counter['num'].message) + 1))
            
        elif dir == 'down' and self.get_count() - 1 in self.range:
            
            self.counter['num'].update_text(str(int(self.counter['num'].message) - 1))
            
        self.move_counter()
            
    def get_count(self): #get the current number the counter is displaying as integer
        return int(self.counter['num'].message)
        
    def click_counter(self, rect): #check if player clicked on any of the counter incriment buttons
        if rect.colliderect(self.counter['up']):
            
            self.incriment('up')
            
            return True
            
        elif rect.colliderect(self.counter['down']):
            
            self.incriment('down')
            
            return True
            
        return False
        
class Input(Textbox):
    def __init__(self, message='', tsize=10, tcolor=(255, 255, 255), type=0):
        super().__init__(message, tsize, tcolor, False)
        
        self.defmessage = message

        self.active = True
        
        self.timer = 25
        self.btimer = 0
        
        self.lock = False

        if type == 1:
            
            self.chars = alpha
            
        elif type == 2:
            
            self.chars = numeric
            
        elif type == 3:
            
            self.chars = numeric + '.'
            
        else:
            
            self.chars = chars
            
    def clear(self):
        tl = self.rect.topleft
        self.update_text('')
        
        if self.lock:
            
            self.rect.topleft = tl
            
    def reset(self):
        tl = self.rect.topleft
        self.update_text(self.defmessage)
        
        if self.lock:
            
            self.rect.topleft = tl
        
    def set_lock(self):
        self.lock = True
        
    def close(self):
        tl = self.rect.topleft
        
        m = self.get_message()
        
        if not m:
            
            m = self.defmessage
        
        self.update_text(m)
        
        if self.lock:
            
            self.rect.topleft = tl
        
    def get_message(self):
        return self.message.replace('|', '')
        
    def send_keys(self, text=''):
        tl = self.rect.topleft
        
        if text:
            
            if all(char in self.chars for char in text):
            
                self.update_text(self.get_message() + text)
            
        elif self.btimer <= 0:
            
            self.update_text(self.get_message()[:-1])
            
            self.btimer = 5
            
        if self.lock:
            
            self.rect.topleft = tl
        
    def update(self):
        self.timer -= 1
        self.btimer -= 1
    
        if self.active and not self.timer:
            
            tl = self.rect.topleft
        
            if '|' in self.message:
                
                self.update_text(self.message[:-1])
                
            else:
                
                self.update_text(self.message + '|') 
                
            if self.lock:
                
                self.rect.topleft = tl
    
            self.timer = 25

class Spritesheet:
    def __init__(self):
        self.names = (('michael', 'dom', 'jack', 'mary', 'daniel', 'emily', 'gambling boi', 'mom', 'dad'),
                      ('aunt peg', 'uncle john', 'kristen', 'joe', 'robber', 'ninja', 'max the dog', 'basil the dog', 'copy cat'),
                      ('racoon', 'fox', 'cow', 'shark', 'fish', 'pelican', 'lucky duck', 'lady bug', 'mosquito'),
                      ('snail', 'dragon', 'clam', 'cactus', 'poison ivy', 'rose', 'mr. squash', 'mrs. squash', ''),
                      ('fishing pole', 'invisibility cloak', 'last turn pass', 'speed boost potion', 'mirror', 'sword', 'fertilizer', '', ''),
                      ('mustard stain', 'gold', 'pearl', 'uphalump', 'ghost', 'detergent', 'treasure chest', 'gold coins', ''),
                      ('spell trap', 'curse', 'treasure curse', 'bronze', 'item hex', 'luck', 'boomerang', 'bath tub', 'item leech'),
                      ('item frenzy', 'flu', 'negative zone', 'fishing trip', 'future orb', 'knife', 'magic wand', 'lucky coin', 'sapling'),
                      ('vines', 'zombie', 'jumble', 'demon water glass', 'succosecc', 'sunflower', 'lemon lord', 'wizard', 'haunted oak'),
                      ('spell reverse', 'sunny day', 'garden', 'desert', 'fools gold', 'graveyard', 'city', 'farm', 'forest'),
                      ('water', 'sky', 'office fern', 'parade', 'camel', 'rattle snake', 'tumble weed', 'wind gust', 'sunglasses'),
                      ('metal detector', 'sand storm', 'mummy', 'mummys curse', 'pig', 'corn', '', 'harvest', 'golden egg'),
                      ('bear', 'big rock', 'unlucky coin', 'hunting season', 'stardust', 'water lilly', 'torpedo', 'bat', 'sky flower'),
                      ('kite', 'balloon', 'north wind', 'garden snake', '', 'watering can', 'magic bean', '', '')
                       )
                       
        self.ids = self.make_ids()
                             
        self.sheet, self.images = self.load_cards() #spritesheet and dictionary of names with coordinates for each image
        
    def make_player(self, c):
        color = c.color if c.color is not None else (255, 255, 255)
        tb = Textbox(c.name, 18, tcolor=color)
        tb.add_outline((0, 0, 0), 2)
        
        return tb.text
        
    def check_name(self, name):
        return any(name in row for row in self.names)
        
    def get_by_id(self, id):
        return self.ids.get(id)
        
    def get_image(self, c, mini=True): #get the image of given card by name. Used when card needs to be displayed on screen
        name = c.name
        
        if not self.check_name(name):
            
            img = self.make_player(c) #get fake player card
            
        else:
            
            try:
        
                img = pg.Surface((375, 525)).convert()

                img.blit(self.sheet, (0, 0), self.images[name]) #try to find card in images dictionary
                
                if mini: #shrink card if we don't have to display at full size
                
                    w, h = img.get_size()
                    
                    img = pg.transform.scale(img, (w // 10, h // 10))
                    
            except KeyError: #if card can't be found in images dictionary, used textbox with card name as substitute image
                
                img = Textbox(name).text
        
        return img
        
    def load_cards(self): #loads spritesheet into memory
        f = 'spritesheet.png'
        
        images = {} #dictionary used to look up card by name. formatted as name: (x, y, width, height) where x, y are top left coordinates on sprite sheet
        
        sheet = pg.image.load(f).convert()
        
        size = sheet.get_size()
        
        row = 0
        
        for y in range(0, size[1], 525): #loops over each row and column to get coordinates of each card
            
            col = 0
        
            for x in range(0, size[0], 375):
                
                name = self.names[row][col] #get name of card based on index
                
                if name:
                
                    images[name] = (x, y, 375, 525)
                
                col += 1
                
            row += 1
            
        return (sheet, images)
        
    def make_ids(self):
        ids = {}
        
        i = 0
        
        for row in self.names:
            
            for name in row:
                
                if name:
                    
                    ids[i] = name
                    
                    i += 1
                    
        return ids
        
        
        
        
        