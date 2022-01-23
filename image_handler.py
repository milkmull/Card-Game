import pygame as pg

def init():
    globals()['IMAGE_HANDLER'] = Image_Handler()
    
def get_image_handler():
    return globals().get('IMAGE_HANDLER')

class Image_Handler:
    def __init__(self):
        self.images = self.import_images()
        self.default = pg.Surface((1, 1)).convert()
        
    def import_images(self):
        images = {}
        
        images['trash'] = pg.image.load('img/icons/trash_icon2.png').convert_alpha()
        
        return images
        
    def get_image(self, image):
        return self.images.get(image, self.default)