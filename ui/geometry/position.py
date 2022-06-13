import pygame as pg

def center_objects_y(objects, rect=None, padding=10):
    width, height = pg.display.get_window_size()
    objects = [o for o in objects if hasattr(o, 'rect')]
    r = pg.Rect(0, 0, 0, 0)
    for o in objects:
        r.height += o.rect.height + padding
    if rect:
        r.centery = rect.centery
    else:
        r.centery = height // 2
    y = r.top + padding
    for o in objects:
        o.rect.top = y
        y += o.rect.height + padding
        
def center_objects_x(objects, rect=None, padding=10):
    width, height = pg.display.get_window_size()
    objects = [o for o in objects if hasattr(o, 'rect')]
    r = pg.Rect(0, 0, 0, 0)
    for o in objects:
        r.width += o.rect.width + padding
    if rect:
        r.centerx = rect.centerx
    else:
        r.centerx = width // 2
    x = r.left + padding
    for o in objects:
        o.rect.left = x
        x += o.rect.width + padding
    
def center_objects(objects, rect=None, padding=(10, 10)):
    Position.center_objects_y(objects, rect=rect, padding=padding[0])
    Position.center_objects_x(objects, rect=rect, padding=padding[1])