import pygame as pg

import save

pg.init()
pg.display.set_mode(save.CONSTANTS['screen_size'], flags=pg.SCALED | pg.RESIZABLE)
pg.display.set_caption('card game')

import spritesheet
import customsheet
import client
import game
import network
import builder
import main_menu

from ui.menu import Menu

def start():
    mm = Menu(get_objects=main_menu.main_menu)
    mm.run()
        
    pg.quit()


start()