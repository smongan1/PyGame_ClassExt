# PyGame_ClassExt_smongan1 Package
<p>This package provides a collection of utility classes and functions designed to enhance game development using the Pygame library. It offers a variety of features to streamline the creation of interactive and animated game elements, manage inventories, implement physics, and more.

## BaseClasses.py
<p>Description: This module provides a versatile framework for developing 2D games using the Pygame library. The framework includes a set of classes and functionalities designed to streamline various aspects of game development, such as managing graphical elements, interactive widgets, user input, and more.

### Features:

<p>Easily create and manage game layers, widgets, actors, buttons, textboxes, and graphics.<\p>
<p>Automate component removal with the Deleteable class.
<p>Handle user input, mouse events, and keyboard input seamlessly.
<p>Implement interactive elements with customizable appearance and behavior.
<p>Develop complex game logic, movement, and physics for actors.
<p>Create dynamic user interfaces with buttons and textboxes for user interaction.

## utilities.py
Description: This module contains a collection of utility functions for various tasks involving Pygame, ranging from image loading and manipulation to geometric calculations and widget positioning.

### Functions:

<p>center_rects(ref_rect, rect_to_center): Calculate the position to center a rectangle within another reference rectangle.
<p>split_text_into_lines(text, width, font_size): Split a text into lines that fit within a given width based on the font size.
<p>load_image(name, data_dir, colorkey=None, scale=1, size=None): Load an image from a file with optional scaling and colorkey.
... (List of all utility functions)

### Classes:

<p>timer: Timer class for measuring time intervals.

## AnimationClasses.py
<p>Description: This module extends Pygame's capabilities by offering classes and utilities for creating interactive and animated game objects.

### Classes:

<p>AnimatedActor: Manages animated game objects with animations, effects, and rotation.
<p>Animation: Represents animations with frame rotation, specifications, and shadow rendering.
<p>HoverWidget: Creates interactive widgets with hover effects.
<p>DisplacementEffects: Defines displacement effects for modifying actor position.

## RPGElements.py
<p>Description: This module introduces classes and utilities for implementing game-related functionality using Pygame. It includes classes for managing inventories, creating interactive scrollbars, and handling game items.

### Classes:

<p>InventoryItem: Represents individual items within an inventory widget.
<p>Inventory: Manages inventory widgets in games.
<p>ScrollBar: Creates interactive scrollbars for user interface scrolling.

## Physics2d.py (WIP)
<p>Description: This module provides an unfinished 2D physics engine designed for game development. It includes classes for managing collidable objects, rigid bodies, and a basic physics simulation.

### Classes:

<p>PhysicsGame2D: Extends the Game class to include basic physics simulation and collision handling.
<p>PhysicsActor2D: Extends the Actor class to add physical properties and interactions.
