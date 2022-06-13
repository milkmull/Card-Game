import pygame as pg

def get_surface(size, color=(0, 0, 0), width=1, olcolor=None, key=None, **border_kwargs):
    s = pg.Surface(size).convert()
    r = s.get_rect()
    if border_kwargs:
        s.fill((0, 0, 1))
        s.set_colorkey((0, 0, 1))
        pg.draw.rect(s, color, r, **border_kwargs)
    else:
        s.fill(color)
    if olcolor:
        pg.draw.rect(s, olcolor, r, width=width, **border_kwargs)
    if key:
        s.set_colorkey(key)
    return s

def rect_outline(img, color=(0, 0, 0), width=2):
    ol = img.copy()
    ol.fill(color)
    w, h = img.get_size()
    img = pg.transform.smoothscale(img, (w - (width * 2), h - (width * 2)))
    ol.blit(img, (width, width))
    return ol

def get_arrow(dir, size, padding=(0, 0), color=(255, 255, 255), bgcolor=(0, 0, 0, 0)):
    s = pg.Surface(size).convert_alpha()
    s.fill(bgcolor)
    w, h = size
    top = (w // 2, padding[1] // 2)
    bottomleft = (padding[0] // 2, h - (padding[1] // 2))
    bottomright = (w - (padding[0] // 2), h - (padding[1] // 2))
    pg.draw.polygon(s, color, (top, bottomleft, bottomright))
    
    a = 0
    if dir == 'd':
        a = 180
    elif dir == 'l':
        a = 90
    elif dir == 'r':
        a = -90
    if a:
        s = pg.transform.rotate(s, a)
        
    return s

def crop(img, x, y, w, h):
    surf = pg.Surface((w, h))
    surf.blit(img, (0, 0), (x, y, w, h))
    return surf
 