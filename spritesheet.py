import pygame as pg

def create_text(message, size=10, color=(255, 255, 255), font='freesansbold.ttf'): #returns surface with rendered text
    text_font = pg.font.Font(font, size)
    text = text_font.render(message, size, color)
    return text

class Textbox: #used to easily position text on screen
    def __init__(self, message, tsize=10, tcolor=(255, 255, 255), counter=None, r=range(-999, 999)):
        self.message = message
        
        self.text = create_text(message, tsize, tcolor) #rendered text image
        
        if counter is not None: #counter argument is number which is default value for the displayed counter text

            self.counter = {'down': Textbox('<', tsize), 'num': Textbox(str(counter), tsize), 'up': Textbox('>', tsize)} #display for simple counter "<num>"
            self.range = r #set upper and lower limit for counter
        
        self.rect = self.text.get_rect() #indicates where textbox is
        
        self.tsize = tsize #text size
        self.tcolor = tcolor #text color (rgb)
        
        self.uid = id(self) #id of textbox
        
    def move_counter(self): #used to move all textboxes associated with a counter textbox
        self.counter['down'].rect.midleft = self.rect.midright
        self.counter['num'].rect.midleft = self.counter['down'].rect.midright
        self.counter['up'].rect.midleft = self.counter['num'].rect.midright

    def update_text(self, message, tcolor=None): #updates the text in the text box
        if tcolor is not None:
        
            self.tcolor = tcolor
            
        tl = self.rect.topleft #maintains the top left position of text on screen even if textbox changes size
            
        self.message = message
        self.text = create_text(message, self.tsize, self.tcolor)
        self.rect = self.text.get_rect()
        self.rect.topleft = tl
        
        if hasattr(self, 'counter'): #if textbox is counter, move all associated counter textboxes to new positions
        
            self.move_counter()
        
    def get_image(self, mini=False):
        if not hasattr(self, 'counter'):
        
            return self.text #return text image
            
        else: #if textbox is counter, merge all associated textbox images into one image

            x = 0
            
            img = pg.Surface((self.rect.width + sum(t.rect.width for t in self.counter.values()), self.rect.height)).convert()
            
            img.blit(self.text, (x, 0))
            
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
                      ('metal detector', 'sand storm', 'mummy', 'mummys curse', 'pig', 'corn', 'ticking time bomb', 'harvest', 'golden egg'),
                      ('bear', 'big rock', 'unlucky coin', 'hunting season', 'stardust', 'water lilly', 'torpedo', 'bat', 'sky flower'),
                      ('kite', 'balloon', 'north wind', 'garden snake', 'flower pot', 'watering can', 'magic bean', '', '')
                       )
                             
        self.sheet, self.images = self.load_cards() #spritesheet and dictionary of names with coordinates for each image
        
    def make_player(self, name):
        return Textbox(name, 15).text #returns "fake" card to represent the player. Used when players need to be displayed in the selection pane
        
    def get_image(self, name, mini=True): #get the image of given card by name. Used when card needs to be displayed on screen
        if 'player' in name:
            
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
        
        
        
        
        
        