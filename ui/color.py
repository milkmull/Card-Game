import colorsys

GOLDEN_RATIO = (1 + 5 ** 0.5) / 2

def tint(color, factor=4):
    return tuple([round(((255 - rgb) / factor) + rgb) for rgb in color])
    
def shade(color, factor=4):
    return tuple([round(rgb / factor) for rgb in color])
    
def gen_colors(num):
    colors = []
    for i in range(num):
        h = (i * (GOLDEN_RATIO - 1)) % 1
        r, g, b = colorsys.hsv_to_rgb(h, 0.8, 1)
        rgb = (r * 255, g * 255, b * 255)
        colors.append(rgb)
    return colors
    
def mix(c1, c2):
    return tuple([(c1[i] + c2[i]) // 2 for i in range(3)])
    
def grayscale(c):
    return sum(c) // 3
    
def is_light(c):
    return sum(c) < 382