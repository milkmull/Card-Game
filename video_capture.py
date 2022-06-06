import cv2

import pygame as pg

class Video_Capture:  
    def __init__(self):
        self.vid = None
        
    @property
    def recording(self):
        if self.vid:
            return self.vid.isOpened()
        
    def start(self):
        self.vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
    def stop(self):
        if self.vid:
            self.vid.release()
            self.vid = None
      
    def close(self):
        self.stop()
        cv2.destroyAllWindows()
        
    def get_frame(self):
        ret, frame = self.vid.read()
        if ret:
            image = pg.image.frombuffer(frame.tobytes(), frame.shape[1::-1], 'BGR').convert()
            return image
            
    