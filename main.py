import pygame as pg

import save

import ui

import image_handler
import spritesheet
import customsheet

import client
import game
import network
import builder
import menu

from constants import *

def start():
    pg.init()

    pg.display.set_mode((width, height), flags=pg.SCALED|pg.RESIZABLE)
    pg.display.set_caption('card game')

    save.init()
    image_handler.init()
    spritesheet.init()
    customsheet.init()
    menu.init()
    client.init()
    game.init()
    network.init()
    builder.init()
    ui.init()

    main_menu = ui.Menu(get_objects=menu.main_menu)
    main_menu.run()
        
    pg.quit()


start()