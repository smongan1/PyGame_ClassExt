"""
Pygame Game Initialization Script

This script sets up a Pygame environment based on configuration settings, retrieves the game handle,
and manages its execution. It utilizes custom configuration parsing and game handling functions.

Overview:
- Imports necessary modules, including 'sys', 'pygame', and custom modules.
- Initializes Pygame and configures it using parsed settings from a configuration file.
- Utilizes a custom configuration parsing module ('Configs') to load configuration settings.
- Appends paths and initializes Pygame's font module.
- Retrieves the game handle based on configuration settings.
- Handles exceptions to ensure proper quitting of Pygame.
- Runs the game loop until the user decides to quit.

Usage:
- Ensure that required modules and the configuration file ('config.conf') are available.
- Customize the paths, filenames, and configuration settings in the 'config.conf' file.
- Run the script to initiate the game as per the provided configuration.

Note: This script relies on custom modules and the 'Configs' class, which are not fully provided here.

Author: Sean Mongan
Date: 8/11/2023

Configuration Options (config.conf):
- 'handlerConfigs': A dictionary containing configuration settings for the game handler.

Example Configuration (config.conf):
[DEFAULT]
gameState=None
PygameBaseSource="../../PyGame_ClassExt/src"
GameExecutionFile="test_pygame.py"
savePath="Saves"
max_speed=1000
GameSource="./GameFiles"

[handlerConfigs]
gameClassFiles="game_classes.py"
gameSetupFiles="game_setup.py"
SCREEN_WIDTH=800
SCREEN_HEIGHT=800
res=[1900, 900]
framerate=60
saveLayers="Main"
assets_folder="Assets"
gameSource="./GameFiles"

"""

import os
from executionTools import Config, Execute

configs = Config.parse("config.conf")
Config.printConfig(configs)

setupConfigs = configs['DEFAULT']
if isinstance(setupConfigs['PygameBaseSource'], str):
    setupConfigs['PygameBaseSource'] = [setupConfigs['PygameBaseSource']]
if isinstance(setupConfigs['GameSource'], str):
    setupConfigs['GameSource'] = [setupConfigs['GameSource']]
os.sys.path.extend(setupConfigs['GameSource'])
os.sys.path.extend(setupConfigs['PygameBaseSource'])

game_execution = setupConfigs['GameExecutionFile'].split('.')[0]
exec(f"import {game_execution} as RUNNING_GAME")

handlerConfigs = configs["handlerConfigs"]
Execute.safeRun(RUNNING_GAME, handlerConfigs)