To Test this Example Simply call python run.py in the Game directory (same directory as run.py)

Creating a game using the provided scripts test_pygame.py, game_classes.py, game_setup.py, and run.py
 involves several steps. These scripts collectively demonstrate a structured approach to developing a 
game with Pygame. Here's a high-level overview of the process:

Game Concept and Design:

Begin by conceptualizing and designing your game. Define its mechanics, gameplay, 
characters, visuals, and interactions.

Game Classes (game_classes.py):

Define your custom game classes in game_classes.py. These classes represent your game elements such as 
characters, projectiles, and enemies.
Implement the logic and behaviors for these classes. In Projectile and MainActor, 
you define how they move, interact, and respond to various events.
Game Setup (game_setup.py):

In game_setup.py, define setup functions that configure different game screens and UI elements.
Utilize these functions to create dictionaries that define the appearance and behavior of game screens 
like the main menu, in-game menu, and inventory.
Entry Point (run.py):

run.py serves as the entry point to execute your game.
Configure the config.conf file to specify game settings, paths, and filenames.
This script imports modules, initializes Pygame, and sets up configurations.
It imports the RUNNING_GAME module from GameExecutionFile.
The safeRun function encapsulates game execution while handling exceptions and Pygame quitting.
Configuration (config.conf):

Define your game's configurations in the config.conf file.
Set paths, filenames, dimensions, and other parameters used by run.py and the executed scripts.
Specify the game state, Pygame base source, game execution file, save path, and more.
Game Execution (run.py):

run.py loads configurations from config.conf, sets up paths, and imports the RUNNING_GAME module.
It calls the safeRun function to execute the game using the specified handler configurations.
The game loop is managed by the GameHandler class, allowing you to interact with the game.
Using Custom Classes and Setup (test_pygame.py):

test_pygame.py demonstrates how to integrate your game classes and setup functions.
It shows how to create a Game instance, set up layers, widgets, actors, and buttons.
It defines the game loop and execution using the GameHandler.
Customizing and Expanding:

Customize the scripts and modules according to your game's requirements.
Extend the game by adding new classes, setup functions, and interactions.
Implement additional screens, characters, enemies, power-ups, and mechanics.
Art Assets and Resources:

Create or obtain the necessary art assets, sound effects, music, and animations for your game.
Integrate these resources into your game by loading images, sounds, and fonts using Pygame.
Testing and Debugging:

Test your game at each development stage to ensure functionality and identify bugs.
Debug and fix issues that arise during testing.
Iterative Development:
Continuously iterate and refine your game's design, mechanics, and features based on feedback and testing.
Fine-tune gameplay, balance, difficulty, and user experience.
Deployment:
When your game is complete and thoroughly tested, package it for distribution.
Compile it into an executable or create an installer package for players to install and play.
Remember that this overview provides a high-level guide to using the provided scripts. The actual implementation 
may require adapting these scripts to your game's specific needs, including creating additional game states, 
UI screens, and integrating the art assets and mechanics unique to your game.