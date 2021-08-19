import pygame as pg
import cv2

def cvimage_to_pygame(image):
    return pg.image.frombuffer(image.tobytes(), image.shape[1::-1], 'BGR')

class Video:
    def __init__(self, win):
        self.screen = win
        self.frame = pg.Surface((1024, 576)).convert()
        self.captured_image = None

        self.clock = pg.time.Clock()
        
        self.vid = cv2.VideoCapture(0)
        self.recording = False
        
        self.running = True
        
        self.run()
        
    def close_capture(self):
        self.recording = False
        self.vid.release()
        cv2.destroyAllWindows()
        
    def quit(self):
        self.close_capture()
        self.running = False
        
    def run(self):
        while self.running:
            
            self.clock.tick(60)
            
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        for e in pg.event.get():
            
            if e.type == pg.QUIT:
                
                self.quit()
                
            elif e.type == pg.KEYDOWN:
                
                if e.key == pg.K_ESCAPE:
                    
                    self.quit()
                    
                elif e.key == pg.K_s:
                    
                    self.recording = True
                    
            elif e.type == pg.KEYUP:
                    
                if e.key == pg.K_s:
                    
                    self.recording = False
                    
    def update(self):
        if self.recording:
            
            _, frame = self.vid.read()
            if frame is not None:
                self.captured_image = cvimage_to_pygame(frame)
        
    def draw(self):
        self.frame.fill((0, 0, 0))
        
        if self.recording:
            
            self.frame.blit(self.captured_image, (0, 0))
            
        self.screen.blit(self.frame, (0, 0))
            
        pg.display.flip()
            
if __name__ == '__main__':
   
    pg.init()
    win = pg.display.set_mode((1024, 576))
    
    v = Video(win)
    
    pg.quit()




