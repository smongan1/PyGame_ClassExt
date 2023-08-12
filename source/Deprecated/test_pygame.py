# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 21:50:06 2022

@author: Sean
"""
import sys
import pygame as pg
pg.init()
sys.path.append("../PyGame_ClassExt/src/")
pg.font.init()

from PyGame_ClassExt_smongan1.utilities import *
from PyGame_ClassExt_smongan1.BaseClasses import *
from PyGame_ClassExt_smongan1.AnimationClasses import *
from PyGame_ClassExt_smongan1.RPGElements import *

import time
import numpy as np
import os
from copy import copy, deepcopy
from glob import glob

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
max_speed = 1000
ind_to_letter = { 4+i : x for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}
letter_to_ind = { x : 4+i for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}

with open("game_classes.py", 'r') as f:
    exec(f.read())
    for line in f.readlines():
        if 'class' in line:
            exec(line.split('class')[1].split("(" )[0].strip())
            
import game_setup

with open("game_setup.py", 'r') as f:
    exec(f.read())
    
def main():
    game = Game(width = SCREEN_WIDTH, 
                  height = SCREEN_HEIGHT,
                  save_layers = ['Main'],
                  layer_funcs = [eval(attr) for attr in dir(game_setup) 
                                if not attr.startswith('__')],
                  always_draw = True)
    res = [1900, 900]
    handle = GameHandler(game, framerate = 60, resolution = res)
    handle.run()
    return handle
try:
    if __name__ == "__main__":
        handle = main()
except:
    e = Exception("quiting")
    raise(e)
finally:
    pg.quit()
print(sum(handle.times)/len(handle.times))
# Run until the user asks to quit

# Done! Time to quit.
pg.quit()
