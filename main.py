import pygame as pg

import save

pg.init()
pg.display.set_mode(save.CONSTANTS['screen_size'], flags=pg.SCALED | pg.RESIZABLE)
pg.display.set_caption('card game')

import ui

import image_handler
import spritesheet
import customsheet

import client
import game
import network
import builder
import menu

def start():
    image_handler.init()
    menu.init()
    ui.init()

    main_menu = ui.Menu(get_objects=menu.main_menu)
    main_menu.run()
        
    pg.quit()


start()