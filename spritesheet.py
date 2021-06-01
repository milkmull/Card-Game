import pygame as pg

def create_text(message, size=10, color=(255, 255, 255), font='freesansbold.ttf'): #returns surface with rendered text
    text_font = pg.font.Font(font, size)
    text = text_font.render(message, size, color)
    return text

class Textbox: #used to easily position text on screen
    def __init__(self, message, tsize=10, tcolor=(255, 255, 255)):
        self.message = message
        
        self.text = create_text(message, tsize, tcolor) #rendered text image
        
        self.rect = self.text.get_rect() #indicates where textbox is
        
        self.tsize = tsize #text size
        self.tcolor = tcolor #text color (rgb)
        
        self.uid = id(self) #id of textbox

    def update_text(self, message, tcolor=None): #updates the text in the text box
        if tcolor is not None:
        
            self.tcolor = tcolor
            
        c = self.rect.center #maintains the top left position of text on screen even if textbox changes size
            
        self.message = message
        self.text = create_text(message, self.tsize, self.tcolor)
        self.rect = self.text.get_rect()
        self.rect.center = c
        
    def get_image(self, mini=False):
        return self.text #return text image
        
class Counter:
    def __init__(self, message, counter=0, r=range(-999, 999), tsize=10, tcolor=(255, 255, 255)):
        self.textbox = Textbox(message, tsize, tcolor)

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
        
    def incriment(self, dir): #incriments counter value by updating text
        if dir == 'up' and self.get_count() + 1 in self.range:
            
            self.counter['num'].update_text(str(int(self.counter['num'].message) + 1))
            
        elif dir == 'down' and self.get_count() - 1 in self.range:
            
            self.counter['num'].update_text(str(int(self.counter['num'].message) - 1))
            
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
    def __init__(self, message='', tsize=10, tcolor=(255, 255, 255)):
        super().__init__(message, tsize, tcolor)
        
        self.active = True
        
        self.timer = 50
        
        self.lock = False
        
    def set_lock(self):
        self.lock = True
        
    def close(self):
        self.update_text(self.get_message())
        
    def get_message(self):
        return self.message.replace('|', '')
        
    def send_keys(self, char=''):
        tl = self.rect.topleft
        
        if char:
            
            self.update_text(self.get_message() + char)
            
        else:
            
            self.update_text(self.get_message()[:-1])
            
        if self.lock:
            
            self.rect.topleft = tl
        
    def update(self):
        self.timer -= 1
    
        if self.active and not self.timer:
            
            tl = self.rect.topleft
        
            if '|' in self.message:
                
                self.update_text(self.message[:-1])
                
            else:
                
                self.update_text(self.message + '|') 
                
            if self.lock:
                
                self.rect.topleft = tl
    
            self.timer = 50

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
        
    def make_player(self, name):
        return Textbox(name, 15).text #returns "fake" card to represent the player. Used when players need to be displayed in the selection pane
        
    def check_name(self, name):
        return any(name in row for row in self.names)
        
    def get_by_id(self, id):
        return self.ids.get(id)
        
    def get_image(self, name, mini=True): #get the image of given card by name. Used when card needs to be displayed on screen
        if not self.check_name(name):
            
            img = self.make_player(name) #get fake player card
            
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
        
        
        
        
        