"""
This script serves as an example and potential main script for simple implementations using Pygame and custom game classes.

It sets up a game environment, initializes necessary modules, imports required classes and functions, and defines a function
to obtain the game handle. The game handle is used to manage game execution, including the game loop and handling events.

Note: This script assumes the presence of custom modules and classes from the 'PyGame_ClassExt_smongan1' package. Ensure that
the required files and definitions are properly linked and accessible.

Script Overview:
- Imports necessary modules including 'sys', 'pygame', and custom modules.
- Initializes Pygame and sets up necessary paths.
- Imports classes and functions from custom modules.
- Defines a function 'GetGameHandle' to set up and obtain the game handle.
- Executes game setup code from specified files and creates a Game instance.
- Creates a GameHandler instance to manage game execution.
- Handles exceptions, ensuring proper quitting of Pygame.
- Prints the average execution time of the game loop.
- Finally, quits Pygame.

Usage:
- Ensure that the required 'PyGame_ClassExt_smongan1' package is available.
- Customize the paths, filenames, and parameters according to your game setup.
- Run the script to start the game and observe the execution time.

Note: This script's functionality heavily relies on external modules and classes that are not fully provided here.

Author: Sean Mongan
Created on: Sat Jun 4 21:50:06 2022
"""

from PyGame_ClassExt_smongan1.utilities import *
from PyGame_ClassExt_smongan1.BaseClasses import *
from PyGame_ClassExt_smongan1.AnimationClasses import *
from PyGame_ClassExt_smongan1.RPGElements import *

import time
import numpy as np
import os
from copy import copy, deepcopy
from glob import glob

def GetGameHandle(SCREEN_WIDTH=800,
                    SCREEN_HEIGHT=800, res=[1900,900],
                    framerate = 60,
                    gameClassFiles = "game_classes.py",
                    gameSetupFiles = "game_setup.py",
                    gameSource = './',
                    saveLayers = 'Main',
                    assets_folder = './',
                    **kwargs):
    # Convert single file paths to lists for uniform processing
    if isinstance(gameClassFiles, str):
        gameClassFiles = [gameClassFiles]

    if isinstance(gameSetupFiles, str):
        gameSetupFiles = [gameSetupFiles]

    if isinstance(saveLayers, str):
        saveLayers = [saveLayers]

    # Execute game class files to define game classes
    for gameClassFile in gameClassFiles:
        gameClassFile = os.path.join(gameSource, gameClassFile)
        with open(gameClassFile, 'r') as f:
            exec(f.read(), globals())

    # Execute game setup files to define layer setup functions
    layer_funcs = []
    for gameSetupFile in gameSetupFiles:
        gameSetupFile = os.path.join(gameSource, gameSetupFile)
        with open(gameSetupFile, 'r') as f:
            script = f.read()
        exec(script, globals())
        # Extract function names defined in the script
        functions = [line.split('def ')[-1].split('(')[0].strip()
                     for line in script.split('\n') if line.startswith('def ')]
        # Convert function names to function objects and add to the list
        layer_funcs.extend([eval(function) for function in functions])

    # Create the Game object using defined settings and setup functions
    game = Game(width = SCREEN_WIDTH,
                  height = SCREEN_HEIGHT,
                  save_layers = saveLayers,
                  layer_funcs = layer_funcs,
                  always_draw = True,
                  assets_folder = assets_folder,
                  **kwargs)

    # Create a GameHandler to manage game execution
    handler = GameHandler(game, framerate = framerate, resolution = res, path = gameSource)
    # Run the game loop using the handler
    handler.run()

    # Return the GameHandler object for external use
    return handler

if __name__ == "__main__":
    try:
        handle = GetGameHandle()
    except:
        e = Exception("quiting")
        raise(e)
    finally:
        pg.quit()
    print(sum(handle.times)/len(handle.times))
    # Run until the user asks to quit

    # Done! Time to quit.
    pg.quit()
