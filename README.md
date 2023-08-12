# PyGame_ClassExt_smongan1 Package
<par>This package provides a collection of utility classes and functions designed to enhance game development using the Pygame library. It offers a variety of features to streamline the creation of interactive and animated game elements, manage inventories, implement physics, and more.

## BaseClasses.py
<par>Description: This module provides a versatile framework for developing 2D games using the Pygame library. The framework includes a set of classes and functionalities designed to streamline various aspects of game development, such as managing graphical elements, interactive widgets, user input, and more.

### Features:

<par>Easily create and manage game layers, widgets, actors, buttons, textboxes, and graphics.
<par>Automate component removal with the Deleteable class.
<par>Handle user input, mouse events, and keyboard input seamlessly.
<par>Implement interactive elements with customizable appearance and behavior.
<par>Develop complex game logic, movement, and physics for actors.
<par>Create dynamic user interfaces with buttons and textboxes for user interaction.

## utilities.py
Description: This module contains a collection of utility functions for various tasks involving Pygame, ranging from image loading and manipulation to geometric calculations and widget positioning.

### Functions:

<par>center_rects(ref_rect, rect_to_center): Calculate the position to center a rectangle within another reference rectangle.
<par>split_text_into_lines(text, width, font_size): Split a text into lines that fit within a given width based on the font size.
<par>load_image(name, data_dir, colorkey=None, scale=1, size=None): Load an image from a file with optional scaling and colorkey.
... (List of all utility functions)

### Classes:

<par>timer: Timer class for measuring time intervals.

## AnimationClasses.py
<par>Description: This module extends Pygame's capabilities by offering classes and utilities for creating interactive and animated game objects.

### Classes:

<par>AnimatedActor: Manages animated game objects with animations, effects, and rotation.
<par>Animation: Represents animations with frame rotation, specifications, and shadow rendering.
<par>HoverWidget: Creates interactive widgets with hover effects.
<par>DisplacementEffects: Defines displacement effects for modifying actor position.

## RPGElements.py
<par>Description: This module introduces classes and utilities for implementing game-related functionality using Pygame. It includes classes for managing inventories, creating interactive scrollbars, and handling game items.

### Classes:

<par>InventoryItem: Represents individual items within an inventory widget.
<par>Inventory: Manages inventory widgets in games.
<par>ScrollBar: Creates interactive scrollbars for user interface scrolling.

## Physics2d.py (WIP)
<par>Description: This module provides an unfinished 2D physics engine designed for game development. It includes classes for managing collidable objects, rigid bodies, and a basic physics simulation.

### Classes:

<par>PhysicsGame2D: Extends the Game class to include basic physics simulation and collision handling.
<par>PhysicsActor2D: Extends the Actor class to add physical properties and interactions.
