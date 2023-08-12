# -*- codning: utf-8 -*-
"""
PyGame_ClassExt_smongan1
Game Development Framework using Pygame

This package provides a versatile framework for developing 2D games using the Pygame library. The framework includes a set of classes and functionalities designed to streamline various aspects of game development, such as managing graphical elements, interactive widgets, user input, and more.

Features:
1. Easily create and manage game layers, widgets, actors, buttons, textboxes, and graphics.
2. Automate component removal with the Deleteable class.
3. Handle user input, mouse events, and keyboard input seamlessly.
4. Implement interactive elements with customizable appearance and behavior.
5. Develop complex game logic, movement, and physics for actors.
6. Create dynamic user interfaces with buttons and textboxes for user interaction.

This package consists of the following classes:

- GameHandler: Manages the execution and display of a game, handling framerate, scaling, and more.

- Game: The core class responsible for managing the game's state, logic, and components.

- Layer: Represents a layer in the game, containing various widgets and components.

- Widget: Represents a graphical widget within a layer, capable of containing other components.

- Actor: Represents interactive game objects with movement and behavior.

- Button: Represents interactive buttons with customizable appearance and actions.

- Textbox: Represents interactive text input fields for user interaction.

- Graphic: Represents graphical elements that can be added to the game's interface.

Created on Wed Dec 21 15:31:19 2022

@author: Sean Mongan
"""
"""
features to add:
    1. ordereddicts for all dicts
    2. maintain order for blitting on save and load
    3. make save and load without surfaces (i.e. no surfs as strings)
    4. add subwidgets?
    5. improve alpha layer handling throughout (especiallly in graphics)
    6. create multiprocess blitting (make blitting tree data structure)
    7. blit only on changes? (may not be possible and maintain speed)
    8. add percentile scalling for all objects (
        i.e. actor.size = [0-1, 0-1] where elements of the size are 
        proportions of widget/layer/screen
        )
    9. maintain object ids on save and load
    10. change all lists to np.array where possible (many places) EDIT: Some have been done
    11. make save and load be something other than joblib dump/load
"""


from PyGame_ClassExt_smongan1.utilities import is_same_vec, timer, center_rects, make_subset_surf
from PyGame_ClassExt_smongan1.utilities import make_fancy_rect_border, deep_finder
from PyGame_ClassExt_smongan1.utilities import convert_surfs_to_str, convert_str_to_surfs
from PyGame_ClassExt_smongan1.utilities import convert_fonts_to_str, convert_str_to_fonts
from PyGame_ClassExt_smongan1.utilities import load_image, point_in_obj, run_updates
from PyGame_ClassExt_smongan1.utilities import make_shadow, split_text_into_lines
import numpy as np
import pygame as pg
from copy import copy
import joblib
from collections import OrderedDict
import os
    
class GameHandler():
    """
    A class responsible for managing the execution and display of a game.

    Parameters:
    - MyGame (object): An instance of the game class to be managed.
    - framerate (int, optional): Target frames per second for the game loop. Default is 60.
    - scale (float or tuple, optional): Scaling factor for the game window. Default is None.
    - resolution (tuple, optional): Desired resolution for the game window. Default is None.
    - path (str, optional): The path to the game's resources. Default is None.

    Attributes:
    - path (str): The path to the game's resources.
    - time (function): A reference to the time function.
    - sleep (function): A reference to the sleep function.
    - game (object): The instance of the game class being managed.
    - screen (pygame.Surface): The drawing surface for the game.
    - times (list): A list to store frame time measurements.
    - cursor_loc (numpy.ndarray or None): The current cursor location on the screen.
    - screen_display (pygame.Surface): The display surface for rendering the game.
    - framerate (int): The target frames per second for the game loop.
    - needs_draw (bool): Flag indicating whether a redraw is required.
    - to_update_attrs (dict): A dictionary of attributes to be updated.

    Methods:
    - run(): Main game loop that handles event processing, updates, and rendering.
    - chkFrameTime(): Ensures a consistent frame rate by adjusting frame timing.
    - Resize(scale_width, height=None): Resizes the game window based on the scaling factor.
    - setup_screen(resolution, scale): Configures the game window's initial settings.
    """
    
    def __init__(self, MyGame, framerate = 60, scale = None, 
                 resolution = None, path = None):
        from time import sleep, time
        MyGame.handler = self
        if path is None:
            path = os.getcwd()
        self.path = path
        self.time = time
        self.sleep = sleep
        self.game = MyGame
        self.screen = pg.Surface([MyGame.width, MyGame.height])
        self.times = []
        self.setup_screen(resolution, scale)
        self.cursor_loc = None
        self.screen_display = pg.display.set_mode(self.screen_size)
        self.game.framerate = framerate
        self.framerate = framerate + 10
        self.needs_draw = True
        self.game.dt = 1/framerate
        self.to_update_attrs = dict()
        
    def run(self):
        pg.init()
        self.timer = timer()
        self.game.setup()
        pg.display.flip()
        self.lastFrameTime = self.time()
        running = True
        while running:
            self.timer.restart()
            # Did the user click the window close button?
            for event in pg.event.get():
                if event.type == pg.QUIT or not self.game.is_running:
                    running = False
            self.cursor_loc = np.array(pg.mouse.get_pos())
            if self.needs_draw:
                trans_size = self.scale * self.game.size
                if self.scale != 1:
                    self.screen_display.blit(pg.transform.smoothscale(self.screen, 
                                                            trans_size), 
                                                             self.padding)
                else:
                    self.screen_display.blit(self.screen, [0,0])
                pg.display.flip()
                self.needs_draw = False
            self.game.update()
            if self.needs_draw:
                self.game.draw()
            self.chkFrameTime()
            
    def chkFrameTime(self):
        while self.timer.getTime() < 1/self.framerate:
            self.sleep(0.000001)
        self.times.append(self.timer.getTime())
        self.lastFrameTime = self.time()
        
    def Resize(self, scale_width, height = None):
        if height == None:
            scale = scale_width
            self.scale *= scale
            #self.screen_size = [round(scale*x)//1 for x in self.screen_size]
            self.screen_size = scale*self.screen_size//1
        pg.display.set_mode(self.screen_size)
    
    def setup_screen(self, resolution, scale):
        h = self.game.height
        w = self.game.width
        if resolution is None:
            if scale is None:
                self.screen_size = np.array([w, h])
                self.scale = 1
            else:
                self.screen_size = np.array([w*scale[0], h*scale[1]])
                self.scale = scale
        else:
            
            self.screen_size = np.array(resolution)
            self.scale = min([resolution[0]/w, resolution[1]/h])
            self.padding = np.array([x//2 for x in [resolution[0] - self.scale*w, 
                            resolution[1] - self.scale*h]])
            
class Game():
    """
    Main application class for managing the game's state, logic, and components.

    Attributes:
    - actors (dict): Dictionary to store actor objects.
    - textboxs (dict): Dictionary to store textbox objects.
    - buttons (dict): Dictionary to store button objects.
    - layers (dict): Dictionary to store layer objects.
    - widgets (dict): Dictionary to store widget objects.
    - graphics (dict): Dictionary to store graphic objects.
    - actors_index (int): Index counter for actors.
    - buttons_index (int): Index counter for buttons.
    - textboxs_index (int): Index counter for textboxes.
    - graphics_index (int): Index counter for graphics.
    - is_running (bool): Flag indicating whether the game is running.
    - cursor_loc (list): List to store the current cursor location.
    - mouse_pressed (bool): Flag indicating whether the mouse button is pressed.
    - disable_PC_movement (bool): Flag to disable player character movement.
    - autosavename (str): Default name for autosave files.
    - autosaveindex (int): Index counter for autosave files.
    - save_name (str): Name for the save file.
    - load_name (str): Name for the load file.
    - to_save (bool): Flag indicating whether a save operation is requested.
    - to_load (bool): Flag indicating whether a load operation is requested.

    Methods:
    - __init__(self, width, height, save_layers, layer_funcs, always_draw, background_color,
             units_per_pixel, save_folder, enable_shadows, assets_folder): Initialize the Game instance.
    - setup(self): Setup the game's initial configuration and layers.
    - update(self): Update game state, input, and physics.
    - draw(self): Draw the current game frame.
    - update_PC(self): Update player character movement based on the current layer.
    - change_layer(self, layer_id): Change the current active layer.
    - add_layer(self, widget_dicts, **kwargs): Add a new layer with widgets to the game.
    - load_layer(self, layer, name): Load a layer into the game.
    - get_component(self, component_id): Get a component by its ID.
    - get_all_components(self): Get a list of all components in the game.
    - get_component_dict(self): Get a dictionary of all components categorized by type.
    - get_all_ids(self): Get a list of all component IDs in the game.
    - get_all_ids_dict(self): Get a dictionary of all components indexed by their IDs.
    - save(self): Save the current game state to a file.
    - load(self): Load a saved game state from a file.
    - convert_all_strs(self): Convert graphical components to use string representations.
    - convert_to_save(self): Convert components to a format suitable for saving.
    - logic(self): Placeholder method for game logic updates.
    - physics_check(self): Placeholder method for physics checks.
    """
    
    actors = dict()
    textboxs = dict()
    buttons = dict()
    layers = dict()
    widgets = dict()
    graphics = dict()
    actors_index = 0
    buttons_index = 0
    textboxs_index = 0
    graphics_index = 0
    is_running = True
    cursor_loc = []
    mouse_pressed = False
    
    disable_PC_movement = False
    autosavename = "autosave"
    autosaveindex = 0
    save_name = None
    load_name = None
    to_save = False
    to_load = False
    
    def __init__(self, 
                 width, 
                 height, 
                 save_layers,
                 layer_funcs,
                 always_draw = False, 
                 background_color = (255, 255, 255), 
                 units_per_pixel = 1,
                 save_folder = 'Saves',
                 enable_shadows = True,
                 assets_folder = 'Assets'):
        self.layer_funcs = layer_funcs
        self.width = width
        self.height = height
        self.size = np.array([width, height])
        self.always_draw = always_draw
        self.background_color = background_color
        self.PC = dict()
        self.units_per_pixel = units_per_pixel
        self.held_index = set()
        self.save_layers = save_layers
        self.cursor_loc = None
        self.prev_layer_id = None
        if save_folder[-1:] != '/':
            save_folder += '/'
        self.save_folder = save_folder
        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)
        self.to_update_attrs = dict()
        self.enable_shadows = enable_shadows
        self.assets_folder = assets_folder
        self.pressed_status = pg.key.get_pressed()
        self.ind_to_letter = { getattr(pg,'K_' + x) : x for x in 'abcdefghijklmnopqrstuvwxyz'}
        self.letter_to_ind =  { x : getattr(pg,'K_' + x) for x in 'abcdefghijklmnopqrstuvwxyz'}
        
    def setup(self):
        self.screen = self.handler.screen
        self.screen.fill(self.background_color)
        for fun in self.layer_funcs:
            widgets, layer_dict = fun(self)
            self.add_layer(widgets, **layer_dict)
        self.current_layer = "Main_menu"
    
    def update(self):
        self.mouse_pressed = pg.mouse.get_pressed()
        self.cursor_loc = ((self.handler.cursor_loc - self.handler.padding) / 
                           self.handler.scale)
        self.prev_held = copy(self.held_index)
        self.pressed_status = pg.key.get_pressed()
        self.held_index = {tf for i, tf, in self.letter_to_ind.items() if self.pressed_status[tf]}
        if self.to_save: self.save()
        if self.to_load: self.load()
        self.layers[self.current_layer].update()
        run_updates(self)
        self.physics_check()
    
    def draw(self):
        #Ideally this would return a blit_tree kind of class (run in parallel)
        #The blit_tree would then be called by blit_tree.blit_onto(self.screen)
        
        self.screen.fill(self.background_color)
        self.layers[self.current_layer].draw()
    
    def update_PC(self):
        if self.current_layer in self.PC:
            self.PC[self.current_layer].movement()
        
    def change_layer(self, layer_id):
        if self.layers[layer_id].uses_prev_screen:
            self.layers[layer_id].prev_screen = self.screen.copy()
        self.screen.fill(self.background_color)
        self.prev_layer_id = self.current_layer
        self.current_layer = layer_id
        

    def add_layer(self, widget_dicts, **kwargs):
        layer = Layer(**kwargs)
        layer.game = self
        layer.always_draw = self.always_draw
        for widget_dict in widget_dicts:
            layer.add_widget(widget_dict)
        self.layers[layer.id] = layer
        
    def load_layer(self, layer, name):
        with open('error_log.log', 'a') as f:
            f.write('\n')
            f.write(str(layer) + '\n')
        #pg.quit()
        del self.layers[name]
        for widge in layer:
            for key in widge:
                if '__iter__' in dir(widge[key]):
                    for a in widge[key]:
                        if 'id' in dir(a):
                            a.id = None
        self.add_layer(layer, name)
    
    def get_component(self, component_id):
        components =  [self.layers, self.widgets, 
                       self.buttons, self.actors, 
                       self.textboxs, self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.layers, self.widgets, 
                       self.buttons, self.actors, 
                       self.textboxs, self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'layers' : self.layers,
            'widgets' : self.widgets,
                'buttons' : self.buttons, 
                'actors' : self.actors, 
                'textboxs' : self.textboxs, 
                'graphics' : self.graphics}
    
    def get_all_ids(self):
        return [x.id for x in self.get_all_components()]
    
    def get_all_ids_dict(self):
        return {x.id : x for x in self.get_all_components()}
    
    def save(self):
        save_dict = dict()
        self.convert_to_save()
        for layer in self.save_layers:
            save_dict[layer] = self.layers[layer].to_dict()
        if self.save_name is None:
            self.save_name = self.autosavename + '_' + str(self.autosaveindex)
            self.autosaveindex += 1
        save_path = self.save_folder + self.save_name + '.sav'
        with open('error_log.log', 'w') as f:
            f.write('Save Path:' + save_path + '\n')
        joblib.dump(save_dict, save_path)
        for layer in self.save_layers:
            for widget in self.layers[layer].widgets.values():
                widget.return_ids()
        self.convert_all_strs()
        self.to_save = False
        self.save_name = None
        
    def load(self):
        load_path = self.save_folder + self.load_name + '.sav'
        with open('error_log.log', 'a') as f:
            f.write('Load Path:' + load_path + '\n')
        save_dict = joblib.load(load_path)
        for key in save_dict.keys():
            with open('error_log.log', 'a') as f:
                f.write('Layer Key:' + key + '\n')
                f.write(str(save_dict[key]) + '\n')
            self.load_layer(save_dict[key], key)
        self.current_layer = 'Main'
        self.load_name = None
        self.to_load = False
        self.convert_all_strs()
        #pg.quit()
        
    def convert_all_strs(self):
        for x in self.get_all_components():
            convert_str_to_surfs(x)
            convert_str_to_fonts(x)
            
    def convert_to_save(self):
        for x in self.get_all_components():
            convert_surfs_to_str(x)
            convert_fonts_to_str(x)
            if hasattr(x, 'animations'):
                x.animations = None
                
    def logic(self):
        None
    
    def physics_check(self):
        None
        
class Layer():
    """
    A class representing a layer in the game, which contains various widgets.

    Parameters:
    - uses_prev_screen (bool): Flag indicating whether the layer uses the previous screen content.
    - name (str, optional): Name of the layer.

    Attributes:
    - game (object): Reference to the main game object.
    - always_draw (bool): Flag indicating whether the layer should always be drawn.
    - id (str): Unique identifier for the layer.
    - initialized (bool): Flag indicating whether the layer has been initialized.
    - actors (dict): Dictionary to store actor objects.
    - buttons (dict): Dictionary to store button objects.
    - widgets (dict): Dictionary to store widget objects.
    - textboxs (dict): Dictionary to store textbox objects.
    - graphics (dict): Dictionary to store graphic objects.
    - widget_id_index (int): Index counter for widget IDs.
    - prev_screen (pygame.Surface): Previous screen content for restoring the layer's state.
    - uses_prev_screen (bool): Flag indicating whether the layer uses the previous screen content.
    - to_update_attrs (dict): Dictionary to store attributes to be updated.

    Methods:
    - initial(self): Perform initial setup for the layer and its widgets.
    - update(self): Update the layer's logic and widgets.
    - draw(self): Draw the layer's widgets.
    - add_widget(self, widget_dict): Add a widget to the layer.
    - add_widget_id(self): Generate and return a unique widget ID.
    - get_component(self, component_id): Get a component by its ID.
    - get_all_components(self): Get a list of all components in the layer.
    - get_component_dict(self): Get a dictionary of all components categorized by type.
    - get_all_ids(self): Get a list of all component IDs in the layer.
    - to_dict(self): Convert the layer and its widgets to a dictionary.
    - logic(self): Placeholder method for layer-specific logic updates.
    """
    
    def __init__(self, uses_prev_screen = False, name = None):
        self.game = None
        self.always_draw = False
        self.id = name
        self.initialized = False
        self.actors = dict()
        self.buttons = dict()
        self.widgets = dict()
        self.textboxs = dict()
        self.graphics = dict()
        self.widget_id_index = 0
        self.prev_screen = None
        self.uses_prev_screen = uses_prev_screen
        self.to_update_attrs = dict()
        
    def initial(self):
        for widget in self.widgets:
            widget.initial()
        self.initialized = True
        
    def update(self):
        
        self.logic()
        if self.uses_prev_screen and not self.prev_screen is None:
            self.game.screen.blit(self.prev_screen, [0,0])
        run_updates(self)
        for widget in self.widgets.values():
            widget.update()
            
    def draw(self):
        for widget in self.widgets.values():
            widget.draw()
            
    def add_widget(self, widget_dict):
        alpha = 255
        colorkey = None
        if 'alpha' in widget_dict: alpha = widget_dict['alpha']
        if 'colorkey' in widget_dict: colorkey = widget_dict['colorkey']
        if not 'class' in widget_dict: widget_dict['class'] = Widget
        
        widget = widget_dict['class'](widget_dict['size'], 
                    widget_dict['position'], 
                    widget_dict['color'],
                    alpha = alpha, colorkey = colorkey)
        
        widget.always_draw = self.always_draw
        widget.layer = self
        widget.game = self.game
        
        for obj_type in ['actors', 'buttons', 'textboxs', 'graphics']:
            if obj_type in widget_dict:
                for obj in widget_dict[obj_type]:
                    o_type_fun = obj_type[:-1]
                    if o_type_fun[-1] == 'e': o_type_fun = o_type_fun[:-1]
                    widget.__getattribute__('add_' + o_type_fun)(obj)
                    
        if 'id' in widget_dict:
            if not  widget_dict['id'].startswith("widget_"):
                 widget_dict['id'] = 'widget_' +  widget_dict['id']
            widget.id = widget_dict['id']
        else: widget.id = self.add_widget_id()
        if 'other' in widget_dict:
            for key in widget_dict['other']:
                widget.__setattr__(key, widget_dict['other'][key])
        self.widgets[widget.id] = widget
        self.game.widgets[widget.id] = widget
        
    def add_widget_id(self):
        id_num = str(self.widget_id_index)
        self.widget_id_index += 1
        return "widget_" + id_num
    
    def get_component(self, component_id):
        components =  [self.widgets, self.buttons,
                       self.actors, self.textboxs, 
                       self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.widgets, self.buttons,
                       self.actors, self.textboxs, 
                       self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'widgets' : self.widgets,
                'buttons' : self.buttons, 
                'actors' : self.actors, 
                'textboxs' : self.textboxs, 
                'graphics' : self.graphics}
    
    def get_all_ids(self):
        return [x.id for x in self.get_all_components()]

    def to_dict(self):
        return [w.to_dict() for w in self.widgets.values()]
    
    def logic(self):
        None
        
class Widget():
    
    """
    A class representing a graphical widget within a layer.

    Parameters:
    - size (tuple): Size of the widget (width, height).
    - position (tuple): Position of the widget's top-left corner (x, y).
    - bkg_color (tuple): Background color of the widget.
    - colorkey (tuple, optional): Color key for transparency.
    - alpha (int, optional): Alpha value for transparency.
    - draw_shadows (bool, optional): Flag indicating whether to draw shadows.
    - shadow_stretch (numpy.array, optional): Stretch factor for shadows.

    Attributes:
    - game (object): Reference to the main game object.
    - always_draw (bool): Flag indicating whether the widget should always be drawn.
    - id (str): Unique identifier for the widget.
    - initialized (bool): Flag indicating whether the widget has been initialized.
    - actors (dict): Dictionary to store actor objects within the widget.
    - buttons (dict): Dictionary to store button objects within the widget.
    - textboxs (dict): Dictionary to store textbox objects within the widget.
    - graphics (dict): Dictionary to store graphic objects within the widget.
    - position (numpy.array): Position of the widget's top-left corner (x, y).
    - size (numpy.array): Size of the widget (width, height).
    - colorkey (tuple): Color key for transparency.
    - surf_orig (pygame.Surface): Original surface representing the widget.
    - has_colorkey (bool): Flag indicating whether the widget has a color key.
    - to_draw (bool): Flag indicating whether the widget should be drawn.
    - to_update (bool): Flag indicating whether the widget should be updated.
    - alpha (int): Alpha value for transparency.
    - color (tuple): Background color of the widget.
    - hover_over (bool): Flag indicating whether the cursor is over the widget.
    - is_selected (bool): Flag indicating whether the widget is selected.
    - is_pressed (bool): Flag indicating whether the widget is pressed.
    - blit_offset (numpy.array): Offset for blitting the widget.
    - draw_shadows (bool): Flag indicating whether to draw shadows.
    - shadow_stretch (numpy.array): Stretch factor for shadows.

    Methods:
    - initial(self): Perform initial setup for the widget and its components.
    - add_actor(self, act): Add an actor object to the widget.
    - add_button(self, button): Add a button object to the widget.
    - add_textbox(self, text_box): Add a textbox object to the widget.
    - add_graphic(self, graphic): Add a graphic object to the widget.
    - add_obj(self, obj, obj_type): Add a component object to the widget.
    - update(self): Update the widget's logic and components.
    - draw(self): Draw the widget and its components.
    - update_actors(self): Update actor components within the widget.
    - update_buttons(self): Update button components within the widget.
    - update_textboxs(self): Update textbox components within the widget.
    - update_graphics(self): Update graphic components within the widget.
    - get_component(self, component_id): Get a component by its ID.
    - get_all_components(self): Get a list of all components in the widget.
    - get_component_dict(self): Get a dictionary of components categorized by type.
    - get_all_ids(self): Get a list of all component IDs in the widget.
    - remove_component(self, component_id): Remove a component from the widget.
    - get_cursor_loc(self): Get the cursor location relative to the widget.
    - move_component(self, component_id, new_widget_id): Move a component to another widget.
    - return_ids(self): Restore component IDs and references.
    - to_dict(self): Convert the widget and its components to a dictionary.
    - logic(self): Placeholder method for widget-specific logic updates.
    """
    
    def __init__(self, size, position, bkg_color, 
                 colorkey = None, alpha = 255,
                 draw_shadows = False,
                 shadow_stretch = np.ones(2)):
        self.game = None
        self.always_draw = False
        self.id = None
        self.initialized = False
        self.actors = dict()
        self.buttons = dict()
        self.textboxs = dict()
        self.graphics = dict()
        self.position = np.array(position)
        self.size = np.array(size)
        self.colorkey = colorkey
        self.surf_orig = pg.Surface(size)
        self.surf_orig.fill(bkg_color)
        self.surf_orig.set_alpha(alpha)
        self.has_colorkey = False
        if not colorkey is None:
            self.surf_orig.set_colorkey(colorkey)
            self.has_colorkey = True
        self.to_draw = True
        self.to_update = True
        self.alpha = alpha
        self.color = bkg_color
        self.hover_over = False
        self.is_selected = False
        self.is_pressed = False
        self.to_update_attrs = dict()
        self.blit_offset = np.zeros(2)
        self.draw_shadows = draw_shadows
        self.shadow_stretch = shadow_stretch
        
    def initial(self):
        self.surf = self.surf_orig.copy()
        for act in self.actors.values():
            act.init_draw()
        for button in self.buttons.values():
            button.init_draw()
        self.initialized = True
    
    def add_actor(self, act):
        self.add_obj(act, 'actors')
        
    def add_button(self, button):
        self.add_obj(button, 'buttons')
    
    def add_textbox(self, text_box):
        self.add_obj(text_box, 'textboxs')
        
    def add_graphic(self, graphic):
        self.add_obj(graphic, 'graphics')

    def add_obj(self, obj, obj_type):
        obj.__setattr__('widget', self)
        obj.__setattr__('layer', self.layer)
        obj.__setattr__('game', self.game)
        if obj_type.endswith('xes'):
            obj_prefix = obj_type[:-2] + '_'
        else:
            obj_prefix = obj_type[:-1] + '_'
        if obj.id is None:
            current_obj_index = self.game.__getattribute__(obj_type + '_index')
            obj.__setattr__('id', obj_prefix + str(current_obj_index))
            self.game.__setattr__(obj_type + '_index', current_obj_index + 1)
        else:
            if not obj.id.startswith(obj_prefix):
                obj.__setattr__('id', obj_prefix + obj.id)
        self.__getattribute__(obj_type)[obj.id] = obj
        self.layer.__getattribute__(obj_type)[obj.id] = obj
        self.game.__getattribute__(obj_type)[obj.id] = obj
        
    def update(self):
        if not self.initialized:
            self.initial()
        """ Render the screen. """
        #self.screen.fill((255, 255, 255))
        if self.to_update:
            self.blit_offset = np.zeros(2)
            self.get_cursor_loc()
            self.hover_over = all(x > 0 and x < self.size[i] for i, x 
                   in enumerate(self.cursor_loc))
            self.logic()
            self.surf = self.surf_orig.copy()
            run_updates(self)
        # pg.display.flip()
        # Your drawing code goes here
        
    def draw(self):
        if not self.initialized:
            self.initial()
        for obj_type in ['actors', 'graphics', 'buttons', 'textboxs']:
            for obj in self.__getattribute__(obj_type).values():
                obj.draw()
            
        if self.to_draw:
            self.game.screen.blit(self.surf, self.position + self.blit_offset)
        
    def update_actors(self):
        acts =  [x for x in self.actors.values()]
        for act in acts:
            act.hover_over = (self.hover_over 
                              and point_in_obj(self.cursor_loc, act))
            try:
                self.game.handler.needs_draw += act.update()
            except Exception as err:
                print(act.id)
                print(act.surf)
                print(err)
                
    def update_buttons(self):
        buttons = [x for x in self.buttons.values()]
        for button in buttons:
            try:
                if (self.hover_over and
                    point_in_obj(self.cursor_loc, button)):
                    if self.game.mouse_pressed[0]:
                        button.is_pressed = True
                    else:
                        if button.is_pressed:
                            button.run_pressed()
                        button.is_pressed = False
                    button.hover_over = True
                else: 
                    button.hover_over = False
                    button.is_pressed = False
                self.game.handler.needs_draw += button.update()
                
            except Exception as err:
                print(button.id)
                print(err)
            
    def update_textboxs(self):
        textboxs = [x for x in self.textboxs.values()]
        for text_box in textboxs:
            try:
                if (self.game.mouse_pressed[0] and 
                    self.hover_over and
                point_in_obj(self.cursor_loc, text_box)):
                        text_box.is_selected = True
                elif self.game.mouse_pressed[0]:
                    text_box.is_selected = False
                self.game.handler.needs_draw += text_box.update()
            except Exception as err:
                print(text_box.id)
                print(err)
                
    def update_graphics(self):
        for graphic in self.graphics.values():
            try:
                graphic.update()
            except Exception as err:
                print(graphic.id)
                print(err)
                
    def get_component(self, component_id):
        components =  [self.buttons, self.actors,
                       self.textboxs, self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.buttons, self.actors,
                       self.textboxs, self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'buttons' : self.buttons, 
                'actors' : self.actors, 
                'textboxs' : self.textboxs, 
                'graphics' : self.graphics}
    
    def get_all_ids(self):
        return [x.id for x in self.get_all_components()]
    
    def remove_component(self, component_id):
        components =  [self.buttons, self.actors,
                       self.textboxs, self.graphics]
        for component_type in components:
            if component_id in component_type:
                del component_type[component_id]
                break
        self.layer.remove_component(component_id)
    
    def get_cursor_loc(self):
        self.cursor_loc = self.game.cursor_loc - self.position
    
    def move_component(self, component_id, new_widget_id):
        component = self.get_component(component_id)
        self.remove_component(component_id)
        
    def return_ids(self):
        comp_dict = self.get_component_dict()
        for comp_type in comp_dict.keys():
            for comp_id in comp_dict[comp_type].keys():
                x = comp_dict[comp_type][comp_id]
                x.id = comp_id
                x.game = self.game
                x.layer = self.layer
                x.widget = self
        #pg.quit()
        
    def to_dict(self):
        out_dict = dict()
        out_dict['alpha'] = self.alpha
        out_dict['size'] = self.size
        out_dict['position'] = self.position
        out_dict['color'] = self.color
        out_dict['class'] = self.__class__
        comps = self.get_component_dict()
        
        for x in deep_finder(comps):
            convert_surfs_to_str(x)
            x.game = None
            x.layer = None
            x.widget = None
            
        for key in comps.keys():
            out_dict[key] = [x for x in comps[key].values()]
        return out_dict
    
    def logic(self):
        None

    
class Deleteable():
    """
    A mixin class providing automatic deletion of object references.

    Methods:
    - __del__(self): Automatically delete object references from parent objects.
    - show_data(self): Display object attributes and their IDs.
    """
    def __del__(self):
        for parent_id in ['game', 'layer', 'widget']:
            if not hasattr(self, parent_id): continue
            parent = self.__getattribute__(parent_id)
            if not parent: continue
            for id_type in ['actors', 'buttons', 'textboxs', 'graphics']:
                store = parent.__getattribute__(id_type)
                if not store: continue
                if self.id in store: 
                    del store[self.id]
                    break
    def show_data(self):
        for x in dir(self):
            if not x.startswith('__'):
                data = self.__getattribute__(x)
                print(x,data)
                if hasattr(data, 'id'):
                    print(x+'_id', data.id)
class Actor(Deleteable):
    """
    A class representing an actor in the game.

    Methods:
    - __init__(self, position, size=None, speed=120, target=np.array([800,800]),
               color=[0,0,0], always_draw=False, death_timer_limit=None,
               has_shadow=False): Initialize the Actor instance.
    - update(self): Update the Actor's position and behavior.
    - draw(self): Draw the Actor on the screen.
    - draw_shadow(self): Draw the shadow of the Actor.
    - move_to(self, dt): Move the Actor towards a target point.
    - move_away(self, dt): Move the Actor away from a target point.
    - center(self): Get the center position of the Actor.
    - do_nothing(self, dt): A method to do nothing.
    - init_draw(self): Initialize drawing properties of the Actor.
    - logic(self): Handle AI and movement selection.
    - movement(self): Handle player input-related movements.
    - physics_check(self): Check for physics interactions.
    - kill(self): Destroy the Actor.
    - retarget_by_center(self): Adjust the target based on the center of the Actor.
    """
    def __init__(self, position, size = None, speed = 120, 
                 target = np.array([800,800]), color = [0,0,0],
                 always_draw = False, death_timer_limit = None,
                 has_shadow = False):
        self.position = np.array(position)
        self.target = np.array(target)
        self.size = np.array(size)
        # in pixels per second
        self.speed = speed
        self.current_action = self.do_nothing
        self.color = color
        self.always_draw = always_draw
        self.id = None
        self.to_draw = True
        self.to_update = True
        self.is_pc = False
        self.hover_over = False
        self.is_selected = False
        self.is_pressed = False
        self.death_timer = 0
        self.death_timer_limit = death_timer_limit
        self.surf = None
        self.is_physics_object = False
        self.to_update_attrs = dict()
        self.blit_offset = np.zeros(2)
        self.has_shadow = has_shadow
        
    def update(self):
        if not self.death_timer_limit is None and self.death_timer >= self.death_timer_limit:
            self.kill()
        prev_size = copy(self.size)
        prev_position = copy(self.position)
        if self.is_physics_object:
            self.physics_check()
        if self.to_update:
            self.blit_offset = np.zeros(2)
            self.movement()
            self.logic()
            self.current_action(self.game.dt)
            run_updates(self)
        return 1
        return 0
    
    def draw(self):
        if self.to_draw and not self.surf is None:
            if self.game.enable_shadows and self.widget.draw_shadows and self.has_shadow:
                self.draw_shadow()
            self.widget.surf.blit(self.surf, self.position + self.blit_offset)
            
    def draw_shadow(self):
        if not hasattr(self, 'shadow') or self.shadow_size != self.size:
            self.shadow = make_shadow(self.surf, self.widget.sheer_amt)
            self.shadow_size = (np.array(self.shadow.get_size()) * 
                                self.widget.shadow_stretch)
            self.shadow = pg.transform.smoothscale(self.shadow, 
                                     self.shadow_size)
            self.shadow_offset = self.size - self.shadow_size
        self.widget.surf.blit(self.shadow, self.position +
                                           self.blit_offset + 
                                           self.shadow_offset)
    def move_to(self, dt):
        direction =  self.target - self.center()
        mag = sum(direction**2)**.5
        upp = self.game.units_per_pixel
        if mag > 1:
            direction = direction/(mag)
        speed = min(dt * self.speed * upp, mag)
        self.position = self.position + speed*direction

    def move_away(self, dt):
        direction =  self.center() - self.target
        speed = dt * self.speed * self.game.units_per_pixel
        self.position = self.position + speed*direction
        
    def center(self):
        if self.size is None:
            return self.position
        return self.position + self.size//2
            
    def do_nothing(self, dt):
        None
            
    def init_draw(self):
        if not self.size is None:
            upp = self.game.units_per_pixel
            
            self.surf = pg.Surface(self.size)
            self.surf.fill(self.color)
            self.draw()
    
    def logic(self):
        """
        AI and movement selection goes here and is called every frame
        """
        None
        
    def movement(self):
        """
        Things related to player input goes here
        """
        None
    
    def physics_check(self):
        None
        
    def kill(self):
        self.__del__()
    
    def retarget_by_center(self):
        self.target = self.target - self.center()/2
    
class Button(Deleteable):
    
    """
    A class representing a button in the game.

    Methods:
    - __init__(self, position, size, color, alpha, text=None, 
              font=['Arial', 25, (255, 0, 0)], 
              hover_over_color=(180, 240, 200),
              pressed_color=(140, 220, 140), justification='Centered'): Initialize the Button instance.
    - init_draw(self): Initialize drawing properties of the Button.
    - update(self): Update the Button's appearance and behavior.
    - render_font(self): Render the font of the Button's text.
    - draw(self): Draw the Button on the screen.
    - run_pressed(self): Execute actions when the Button is pressed.
    - logic(self): Handle Button-specific logic.
    """
    
    def __init__(self, position, size, color, alpha, text = None, 
                 font = ['Arial', 25, (255, 0, 0)], 
                 hover_over_color = (180, 240, 200),
                 pressed_color = (140, 220, 140), justification = 'Centered'):
        self.size = np.array(size)
        self.position = np.array(position)
        self.font = pg.font.SysFont(font[0], font[1])
        self.font_details = font
        self.color = color
        self.hover_over_color = hover_over_color
        self.pressed_color = pressed_color
        self.alpha = alpha
        self.text = text
        self.last_text = ''
        self.always_draw = True
        self.id = None
        self.to_update = True
        self.to_draw = True
        self.is_pressed = False
        self.hover_over = False
        self.is_selected = False
        self.widget = None
        self.to_update_attrs = dict()
        self.blit_offset = np.zeros(2)
        self.justification = justification
        self.init_draw()

    def init_draw(self):
        self.surf = pg.Surface(self.size)
        self.surf.fill((3,5,7))
        self.surf.set_colorkey((3,5,7))
        pg.draw.polygon(self.surf, self.color, make_fancy_rect_border(self.size))
        self.hover_over_surf = self.surf.copy()
        if all(x > 8 for x in self.size):
            pg.draw.polygon(self.hover_over_surf, self.hover_over_color, 
                        make_fancy_rect_border(self.size,4))
        self.pressed_surf = self.hover_over_surf.copy()
        if all(x > 24 for x in self.size):
            pg.draw.polygon(self.pressed_surf, self.pressed_color, 
                        make_fancy_rect_border(self.size,12))
        self.to_draw_surf = self.surf.copy()
        self.draw()
        
    def update(self):
        if self.to_update:
            self.blit_offset = np.zeros(2)
            self.logic()
            if self.is_pressed: 
                self.to_draw_surf = self.pressed_surf.copy()
                self.font.set_bold(True)
            elif self.hover_over: self.to_draw_surf = self.hover_over_surf.copy()
            else: self.to_draw_surf = self.surf.copy()
            run_updates(self)
        else: surf = self.surf.copy()
        if self.is_pressed:
            self.font.set_bold(False)
        return 1
    
    def render_font(self):
        if self.text != self.last_text:
            self.last_text = self.text
            split_text, locs = split_text_into_lines(self.text,
                                               self.size[0] - 10,
                                               self.font_details[1])
            locs = [[x[0] + 5, x[1] + 5] for x in locs]
            
            fonts = [
                self.font.render(text, True, self.font_details[2], None)
                for text in split_text]
            blits_squence = [[fnt, loc] for fnt, loc in zip(fonts,locs)]
            if self.justification == 'Centered':
                for x in blits_squence:
                    sze = x[0].get_size()
                    x[1][0] += (self.size[0] - sze[0])/2 - 5
            self.surf_font = pg.Surface([self.size[0], locs[-1][1] + 
                                        16/12*self.font_details[1]])
            self.surf_font.fill((5,7,11))
            self.surf_font.set_colorkey((5,7,11))
            self.surf_font.blits(blits_squence)
            
    def draw(self):
        if self.to_draw:
            if not self.text is None:
                self.render_font()
                self.to_draw_surf.blit(self.surf_font, [0,0])
            if self.widget:
                self.widget.surf.blit(self.to_draw_surf, self.position + self.blit_offset)
            
    def run_pressed(self):
        None
        
    def logic(self):
        None
        
class SaveButton(Button):
    
    def run_pressed(self):
        self.game.to_save = True
        if not self.save_name_textbox.text is None:
            self.game.save_name = self.save_name_textbox.text

class LoadButton(Button):
    
    def run_pressed(self):
        self.game.to_load = True

class ChangeLayerButton(Button):
    def __init__(self, layer_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_id = layer_id
        
    def run_pressed(self):
        self.game.change_layer(self.layer_id)

class Textbox(Deleteable):
    """
        Initialize the Textbox instance.

        Parameters:
        - position (numpy.array): The position of the Textbox.
        - length (int, optional): The length of the Textbox. Default is 100.
        - box_color (tuple, optional): The color of the Textbox. Default is (100,100,150).
        - font (list, optional): The font details for the text. Default is ["Arial", 25, (255,0,0)].
        - default_text (str, optional): The default text to display in the Textbox. Default is "".
        - exclude_numbers (bool, optional): Exclude numbers from input. Default is False.
        - exclude_letters (bool, optional): Exclude letters from input. Default is False.
        - exclude_period (bool, optional): Exclude period from input. Default is False.
        - max_text_length (int, optional): The maximum allowed length of the text. Default is None.
        """
    ind_to_letter = { getattr(pg,'K_' + x) : x for x in 'abcdefghijklmnopqrstuvwxyz'}
    ind_to_letter[pg.K_SPACE] = " "
    period_ind = pg.K_PERIOD
    ind_to_letter[pg.K_COMMA] = ","
    ind_to_num = { getattr(pg,'K_' + x) : x for x in "1234567890"}
    def __init__(self, position, length = 100,
                 box_color = (100,100,150),
                 font = ["Arial", 25, (255,0,0)],
                 default_text = "",
                 exclude_numbers = False,
                 exclude_letters = False,
                 exclude_period = False,
                 max_text_length = None):
        
        if exclude_numbers and exclude_letters:
            raise(Exception("ValueError"))
        self.get_pressed_index_dict(exclude_numbers, exclude_letters, exclude_period)
        self.font = pg.font.SysFont(font[0], font[1])
        self.font_details = font
        self.size = np.array([length, round(font[1] * 16/12)+10])
        self.position = np.array(position)
        #self.rect = pg.Rect(self.position, self.size)
        self.surf = pg.Surface(self.size)
        self.surf.fill(box_color)
        self.surf = make_subset_surf(self.surf, 
                                     [min(x+30, 255) for x in box_color],
                                     255, 10)
        self.surf.fill(box_color)
        self.blink_count = 0
        self.delay_count = 0
        self.text = ""
        self.default_text = default_text
        self.max_text_length = max_text_length
        self.id = None
        self.to_draw = True
        self.to_update = True
        self.hover_over = False
        self.is_selected = False
        self.to_update_attrs = dict()
        self.blit_offset = np.zeros(2)
        self.backspace_held = False
        self.backspace_cnt = 0
        
    def update(self):
        cnt_threshold = np.floor(5 * self.game.framerate/60)
        if self.is_selected and self.to_update:
            if self.backspace_held:
                if self.game.pressed_status[pg.K_BACKSPACE]:
                    self.text = self.text[:-1]
                    run_updates(self)
                    return 1
                else:
                    self.backspace_held = False
                    self.backspace_cnt = 0
            self.blit_offset = np.zeros(2)
            if self.delay_count == 0:
                if self.game.pressed_status[pg.K_BACKSPACE]:
                    self.backspace_cnt += 1
                    if self.backspace_cnt >= cnt_threshold: 
                        self.backspace_held = True
                    if self.game.pressed_status[pg.K_BACKSPACE]:
                        self.delay_count+=1
                        self.text = self.text[:-1]
                if self.max_text_length is None or len(self.text) < self.max_text_length:
                    self.add_pressed_letters()
                if self.game.pressed_status[pg.K_RETURN]:
                    self.on_enter()
            else:
                self.delay_count+=1
                if self.delay_count >= cnt_threshold:
                    self.delay_count = 0
            self.blink_count += 1
            run_updates(self)
        return 1
    
    def draw(self):
        if self.to_draw:
            output_text = self.default_text
            if self.text or self.is_selected:
                output_text = self.text
                if self.blink_count < 20: output_text += "|"
                elif self.blink_count >= 40: self.blink_count = -1
            
            font_surf = self.font.render(output_text, True, 
                                     self.font_details[2], None)
            self.to_draw_surf = self.surf.copy()
            self.to_draw_surf.blit(font_surf, [6,6])
            self.widget.surf.blit(self.to_draw_surf, self.position + self.blit_offset)
            
    def init_draw(self):
        self.update()
        
    def get_pressed_index_dict(self, exclude_numbers, exclude_letters, exclude_period):
        self.letter_dict = dict()
        if not exclude_numbers:
            for key in self.ind_to_num.keys():
                self.letter_dict[key] = self.ind_to_num[key]
        if not exclude_letters:
            for key in self.ind_to_letter.keys():
                self.letter_dict[key] = self.ind_to_letter[key]
        if not exclude_period:
            self.letter_dict[self.period_ind] = "."
            
    def add_pressed_letters(self):
        for ind in self.game.held_index:
            if not ind in self.letter_dict or ind in self.game.prev_held:
                continue
            letter = self.letter_dict[ind]
            if letter != "":
                if pg.K_LSHIFT in  self.game.held_index or pg.K_RSHIFT in  self.game.held_index:
                    letter = letter.upper()
                self.text += letter
                if self.delay_count == 0: self.delay_count+=1
                
    def on_enter(self):
        None
                
class Graphic(Deleteable):
    """
    A class representing a graphical element.

    This class allows you to create and manage graphical elements that can be
    added to the game's interface. Graphics can consist of multiple surfaces
    and are responsible for their own drawing and updating.

    :param size: The size of the Graphic (width, height).
    :type size: list or tuple
    :param position: The position of the Graphic.
    :type position: numpy.array
    """
    def __init__(self, size, position):
        [self.width, self.height] = size
        self.position = position
        self.surf = pg.Surface([self.width, self.height])
        self.surf = self.surf.convert_alpha()
        self.orig_color = (5, 7, 11)
        self.surf.fill(self.orig_color)
        self.surf_orig = self.surf.copy()
        self.surfs = dict()
        self.surf_index = 0
        self.id = None
        self.to_draw = True
        self.to_update = True
        self.to_update_attrs = dict()
        self.blit_offset = np.zeros(2)
        self.size = size
        
    def add_surf(self, surf, position):
        self.surfs[self.surf_index] = [pg.image.tostring(surf, "RGBA"),
                                       np.array(surf.get_size()),
                                       np.array(position)]
        self.surf_index += 1
        self.surf.blit(surf, position)
    
    def update(self):
        if self.to_update:
            self.blit_offset = np.zeros(2)
            run_updates(self)
        return 0
    
    def draw(self):
        if self.to_draw:
            self.widget.surf.blit(self.surf, self.position + self.blit_offset)
                
    def redraw(self):
        self.surf = pg.transform.smoothscale(self.surf_orig.copy(), 
                                             self.size)
        for i in range(self.surf_index):
            if i in self.surfs:
                surf = pg.image.fromstring(self.surfs[i][0], self.surfs[i][1], "RGBA") 
                self.surf.blit(surf, self.surfs[i][2])
            
    def surf_update(self, surf, surf_ind):
        self.surfs[surf_ind] = [pg.image.tostring(surf, "RGBA"), np.array(surf.get_size()), 
                                self.surfs[surf_ind][2]]
        self.redraw()
        
    def reposition_surf(self, surf_ind, position):
        self.surfs[surf_ind][2] = position
        self.redraw()
        
    def shift_surf(self, surf_ind, shift_amt):
        self.reposition(surf_ind, self.position + np.array(shift_amt))

class SaveWidget(Widget):
    
    def logic(self):
        if 'button_save_game' not in self.buttons:
            button = SaveButton([0,0], [self.size[0]*.25, self.size[0]*.1], (50,50,150), 255, "Save")
            button.id = 'button_save_game'
            save_name_textbox =  Textbox([0,button.size[1] + 25])
            button.save_name_textbox = save_name_textbox
            exit_button = ChangeLayerButton(self.game.prev_layer_id, [0,0], [self.size[0]*.25, self.size[0]*.1], 
                                            (50,50,150), 255, "EXIT")
            self.add_button(button)
            self.add_textbox(save_name_textbox)
            
class LoadWidget(Widget):
    
    def logic(self):
        if 'button_save_game' not in self.buttons:
            button = SaveButton([0,0], [100,25], (50,50,150), 255, "Save")
            button.id = 'button_save_game'
            save_name_textbox =  Textbox([0,button.size[1] + 25])
            button.save_name_textbox = save_name_textbox
            self.add_button(button)
            self.add_textbox(save_name_textbox)
            
class ChangeUpdateStatusButton(Button):
    def __init__(self, obj_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj_id = obj_id
        
    def run_pressed(self):
        if not hasattr(self,'update_status_obj'):
            self.update_status_obj = self.game.get_component(self.obj_id)
        self.update_status_obj.to_update = not self.update_status_obj.to_update
        self.update_status_obj.to_draw = not self.update_status_obj.to_draw