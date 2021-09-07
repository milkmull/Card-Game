import pygame as pg
import pygame.freetype
pg.init()


SIZE = WIDTH, HEIGHT = (1024, 720)
FPS = 30
screen = pg.display.set_mode(SIZE, pg.RESIZABLE)
clock = pg.time.Clock()

class Textbox:
    def __init__(self, message, tsize, font='freesansbold.ttf'):
        self.message = message
        
        self.tsize = tsize
        self.font = font
        self.text_font = pg.freetype.Font(font, tsize)
        self.text_font.pad = True

        self.image, self.rect, self.characters = self.create_text(message)
        
        self.index = 0
        
    def set_size(self, tsize):
        self.text_font.size = tsize
        self.tsize = tsize
        
    def move_characters(self):
        rect = self.rect

        for char, r, rel in self.characters:
            
            rx, ry = rel
            r.topleft = (rect.x + rx, rect.y + ry)
        
    def create_text(self, message):
        img, rect = self.text_font.render(message, fgcolor=(255, 255, 255))
        characters = self.get_chars(message, rect)
        
        return (img, rect, characters)
        
    def get_chars(self, message, rect):
        characters = []
        
        x, y = rect.topleft
        
        for char in message:
            r = self.text_font.get_rect(char)
            r.topleft = (x, y)
            characters.append((char, r))
            x += r.width
            
        return characters
        
    def events(self, input):
        for e in input:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RIGHT:
                    self.index = (self.index + 1) % len(self.message)
                elif e.key == pg.K_LEFT:
                    self.index = (self.index - 1) % len(self.message)
                print(self.characters[self.index])
                
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                p = pg.mouse.get_pos()
                
                for info in self.characters:
                    r = info[1]
                    if r.collidepoint(p):
                        self.index = self.characters.index(info)
                        break

    def update(self):
        self.move_characters()
        
    def draw(self, win):
        win.blit(self.image, self.rect)
        r = self.characters[self.index][1]
        pg.draw.line(win, (255, 255, 255), r.topleft, r.bottomleft)
        
    def fit_text(self, rect):
        text = self.message
        tsize = self.tsize
        
        words = [word.split(' ') for word in text.splitlines()]
        
        surface = pg.Surface(rect.size).convert()
        
        characters = []

        while True:

            space = self.text_font.get_rect(' ').width  # The width of a space.
            max_width, max_height = rect.size
            x, y = (0, 0)
            
            over_y = False
            rendered_lines = []
            current_line = []
            
            for line in words:
        
                for word in line:
                
                    word_surface, word_rect = self.text_font.render(word, fgcolor=(255, 255, 255))
                    width, height = word_rect.size
                    
                    if x + width >= max_width:
                        x = 0
                        y += height
                        if y + height > max_height:
                            over_y = True
                            break
                        else:
                            rendered_lines.append(current_line.copy())
                            current_line.clear()

                    word_rect.topleft = (x, y)
                    current_line.append((word, word_surface, word_rect))
                    x += width + space
                    
                if over_y:
                    self.set_size(tsize - 1)
                    tsize = self.tsize
                    break
                    
                x = 0
                y += height
                
            if not over_y:
                break
                
        rendered_lines.append(current_line)
                
        for line in rendered_lines:
            for word, surf, r in line:
                surface.blit(surf, r)
                
                x, y = r.topleft
                w, h = r.size
                for char in word:
                    r = self.text_font.get_rect(char)
                    r.topleft = (x, y)
                    characters.append((char, r, (r.x - rect.x, r.y - rect.y)))
                    x += r.width
                    
                if r is not line[-1][2]:
                    r = self.text_font.get_rect(' ')
                    r.topleft = (x, y)
                    characters.append((' ', r, (r.x - rect.x, r.y - rect.y)))
                    
        self.image = surface
        self.rect = rect
        self.characters = characters

def character_sizes(font, word):
    print(font.get_rect(word).size, [font.get_rect(char).size for char in word])

def blit_text(rect, text, font, color=(255, 255, 255)):

    characters = []
    
    while True:
    
        space = font.get_rect(' ').width  # The width of a space.
        max_width, max_height = rect.size
        x, y = (0, 0)
        
        over_y = False
        rendered_lines = []
        current_line = []

        for line in words:
        
            for word in line:
            
                word_surface, word_rect = font.render(word, fgcolor=color)
                width, height = word_rect.size
                
                if x + width >= max_width:
                    x = 0 # Reset the x.
                    y += height  # Start on new row.
                    if y + height > max_height:
                        over_y = True
                        break
                    else:
                        rendered_lines.append(current_line.copy())
                        current_line.clear()

                word_rect.topleft = (x, y)
                current_line.append((word, word_surface, word_rect))
                x += width + space
                
            if over_y:
                font.size -= 1
                break
                
            x = 0  # Reset the x.
            y += height  # Start on new row.
            
        if not over_y:
            break
            
    rendered_lines.append(current_line)
            
    for line in rendered_lines:
        for word, surf, r in line:
            surface.blit(surf, r)
            
            x, y = r.topleft
            for char in word:
                r = font.get_rect(char)
                r.topleft = (x, y)
                characters.append((char, r))
                
    print(characters)
        
    return surface 








class Game:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        
        self.running = True
        
        self.elements = self.set_screen()
        
    def set_screen(self):
        screen = []
        
        text = "This is a really long sentence with a couple of breaks.\nSometimes it will break even if there isn't a break " \
               "in the sentence, but that's because the text is too long to fit the screen.\nIt can look strange sometimes.\n" \
               "This function doesn't check if the text is too high to fit on the height of the surface though, so sometimes " \
               "text will disappear underneath the surface"
               
        tb = Textbox(text, 64)
        tb.fit_text(pg.Rect(0, 0, WIDTH, HEIGHT))
        tb.rect.topleft = (0, 0)
        screen.append(tb)
        
        return screen
        
    def run(self):
        while self.running:
            self.clock.tick(30)
            self.events()
            self.update()
            self.draw()
        
    def events(self):
        input = pg.event.get()
        
        for event in input:
            if event.type == pg.QUIT:
                self.running = False
                
        for e in self.elements:
            e.events(input)
                
    def update(self):
        for e in self.elements:
            e.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for e in self.elements:
            e.draw(self.screen)
        pg.display.flip()
        
pg.init()
g = Game()
g.run()
pg.quit()



