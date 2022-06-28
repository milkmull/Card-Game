import pygame as pg

from data.save import SAVE, CONSTANTS

pg.init()
pg.display.set_mode(CONSTANTS['screen_size'], flags=pg.SCALED | pg.RESIZABLE)
pg.display.set_caption('card game')

if SAVE.failed_to_load:
    SAVE.reset_save()

from spritesheet import spritesheet, customsheet
from client import client
from menu import main_menu

from ui.menu import Menu

def start():
    mm = Menu(get_objects=main_menu.main_menu)
    mm.run()
        
    pg.quit()


start()