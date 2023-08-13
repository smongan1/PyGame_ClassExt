# PyGame_ClassExt_smongan1 Package
<p>This package provides a collection of utility classes and functions designed to enhance game development using the Pygame library. It offers a variety of features to streamline the creation of interactive and animated game elements, manage inventories, implement physics, and more.
  
## Flowchart Diagram
![Diagram](./Pygame_ClassExtOverview.png)

## Containerized Diagram
![Diagram](./PygameFramework_Example.png)
<p><b>GameHandler</b>: The core element managing game functionality. It comprises two main parts: "Screen" and "Game."
<p><b>Screen</b>: Represents the visible game interface for players. It contains a "Display Layer" where visual elements are presented.
<p><b>Game</b>: Responsible for game logic. Interacts with the "Current Layer" and includes a connection to "Change Current Layer."
<p><b>Current Layer</b>: The currently active game layer displayed on the screen. It encompasses elements like "Widget1," "Widget2," and so on.
<p><b>Widget1</b>: Contains in-game entities and interactive elements (like <b>Buttons</b> and <b>Actors</b> aka characters).
<p><b>Widget2</b>: Similar to Widget1, also containing game entities and interactive elements.
<p><b>Unused Layers</b>: Inactive layers, such as "Layer2" and "Layer3."
<p><b>Layer2</b>: Similar to the active layers, holding "Widget3" and "Widget4."
<p><b>Layer3</b>: Also similar to the active layers, housing "Widget5" and "Widget6."
<p><b>ChangeLayerButton</b>: Transitions active layer when pressed.
<p>The directional arrows in the diagram represent interactions:
<p>The arrow "Send Current Layer To Screen" indicates that the content of the Current Layer is displayed on the Screen.
<p>In summary, the diagram visually outlines the relationships between different components within the game framework.

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
<p>load_image(name, data_dir, colorkey=None, scale=1, size=None): Load an image from a file and optionally apply scaling and colorkey.
<p>load_image_strip(name, data_dir, colorkey=None, scale=1, size=None): Load an image strip from a file and optionally apply scaling and colorkey.
<p>simple_sheer_arr(img, coordinate, direction=1, pixels=None, scale=None, with_smoothing=None): Apply a simple shear transformation to an image along a specified coordinate.
<p>is_same_vec(vec1, vec2): Compare two vectors element-wise and determine if they are identical.
<p>centered_buttons_locs_vert(button_size, num_buttons, screen_dim, num_cols=None, spacing=None, hori_offset=0, vert_offset=0, padding=100): Calculate the positions of vertically centered buttons.
<p>centered_buttons_locs_hori(button_size, num_buttons, screen_dim, spacing=None, vert_offset=0, hori_offset=0, padding=100): Calculate the positions of horizontally centered buttons.
<p>make_subset_surf(surf, subset_color, subset_alpha, padding): Create a subset surface with a colored background.
<p>make_fancy_rect_border(size, padding=0): Create a list of coordinates for creating a fancy rectangular border.
<p>make_widget_dict(size, position, bkg_color, buttons=None, actors=None, textboxs=None, graphics=None, alpha=255): Create a dictionary representing a widget with various attributes.
<p>deep_finder(x): Recursively search for objects within nested iterables.
<p>convert_surfs_to_str(x): Convert pygame Surfaces in an object to strings.
<p>convert_str_to_surfs(x): Convert string representations back to pygame Surfaces.
<p>convert_fonts_to_str(x): Convert pygame fonts in an object to string representations.
<p>convert_str_to_fonts(x): Convert string representations of pygame fonts back to pygame fonts.
<p>point_in_rect(point, rect): Check if a point is within a pygame Rect.
<p>point_in_obj(point, obj, greater_than_0_check=True): Check if a point is within a custom object.
<p>run_updates(obj): Run update methods of an object based on predefined attributes.
<p>blackwhite(img, sheer_amt=None): Convert an image to black and white with optional shearing.
<p>make_shadow(surf, sheer_amt=None): Create a shadow surface from an image with optional shearing.

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
