# -*- codning: utf-8 -*-

"""
A game development package providing a framework for building interactive game environments,
handling graphical user interface elements, and supporting various functionalities.

This package includes classes for managing game loops, actors, layers, widgets, buttons, text boxes,
graphics, and more. It offers a structured approach to creating and interacting with game components,
facilitating game development with a focus on graphical user interface interactions.

Classes:
- GameHandler: Manages the game loop, display handling, and updates.
- Game: Represents a game environment with various components and functionalities.
- Layer: Represents a layer within the game environment containing widgets and elements.
- Widget: Represents a graphical user interface element within a layer.
- Actor: Represents an entity within the game environment, handling movement and interactions.
- Button: Represents a graphical button element with customizable appearance and behavior.
- ChangeLayerButton: Subclass of Button, represents a button that changes the active layer.
- Textbox: Represents a text input box for user input and interactions.
- Graphic: Represents a graphical element for displaying images and surfaces.
- SaveButton, LoadButton: Subclasses of Button, represent buttons for saving and loading game states.
- SaveWidget, LoadWidget: Subclasses of Widget, represent widgets for saving and loading game states.
- ChangeUpdateStatusButton: Represents a button to change the update status of a component.
- Deleteable: A mixin class providing deletion functionality for game components.

Features to be added:
- Ordered dicts for all dictionaries.
- Maintain order for blitting on save and load.
- Enhanced alpha layer handling throughout, especially in graphics.
- Multiprocess blitting using a blitting tree data structure.
- Add percentile scaling for all objects, allowing size scaling based on proportions.
- Maintain object IDs on save and load.
- Conversion of lists to np.array where applicable.
- Alternative methods for saving and loading, beyond joblib dump/load.
Note: The package includes placeholder methods and comments for planned features and improvements.

Created on Wed Dec 21 15:31:19 2022

@author: Sean Mongan
"""


from PyGame_ClassExt_smongan1.utilities import is_same_vec, timer, center_rects, make_subset_surf
from PyGame_ClassExt_smongan1.utilities import make_fancy_rect_border, deep_finder
from PyGame_ClassExt_smongan1.utilities import convert_surfs_to_str, convert_str_to_surfs
from PyGame_ClassExt_smongan1.utilities import convert_fonts_to_str, convert_str_to_fonts
from PyGame_ClassExt_smongan1.utilities import load_image,  point_in_obj, run_updates
import numpy as np
import pygame as pg
from copy import copy
import joblib
from collections import OrderedDict
import os
    
class GameHandler():
    """
    The `GameHandler` class manages the game loop, display handling, and updates.
    It is responsible for controlling the execution flow of the game, handling
    display scaling, and managing updates for game elements.

    Attributes:
        game (Game): The associated Game instance.
        screen (Surface): The game screen surface for rendering.
        screen_size (numpy.ndarray): The size of the screen.
        screen_display (Surface): The display surface for rendering on the screen.
        scale (float): The scaling factor for display.
        padding (numpy.ndarray): Padding applied to the screen for centered display.
        cursor_loc (numpy.ndarray): Current cursor location.
        needs_draw (bool): Flag indicating if screen needs to be redrawn.
        framerate (int): Target frame rate for the game loop.
        timer (timer): Timer instance for frame rate control.
        lastFrameTime (float): Time of the last frame update.
        to_update_attrs (dict): Dictionary to track attributes to be updated.

    Methods:
        __init__(self, MyGame, framerate, scale, resolution, path):
            Initializes the GameHandler with the given settings.
        
        run(self):
            Initiates the game loop and manages the execution flow.

        chkFrameTime(self):
            Waits to maintain a consistent frame rate before continuing.

        Resize(self, scale_width, height=None):
            Resizes the game display based on the provided scaling factors.
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
        if resolution is None:
            if scale is None:
                self.screen_size = np.array([MyGame.width, MyGame.height])
                self.scale = 1
            else:
                self.screen_size = np.array([MyGame.width*scale[0], MyGame.height*scale[1]])
                self.scale = scale
        else:
            
            self.screen_size = np.array(resolution)
            self.scale = min([resolution[0]/MyGame.width, resolution[1]/MyGame.height])
            self.padding = np.array([x//2 for x in [resolution[0] - self.scale*MyGame.width, 
                            resolution[1] - self.scale*MyGame.height]])
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
    
class Game():
    """
    A class representing a game environment with various components and functionalities.

    Attributes:
        actors (dict): Dictionary of actor instances within the game.
        text_boxes (dict): Dictionary of text box instances within the game.
        buttons (dict): Dictionary of button instances within the game.
        layers (dict): Dictionary of layer instances within the game.
        widgets (dict): Dictionary of widget instances within the game.
        graphics (dict): Dictionary of graphic instances within the game.
        actors_index (int): Index counter for actors.
        buttons_index (int): Index counter for buttons.
        text_boxes_index (int): Index counter for text boxes.
        graphics_index (int): Index counter for graphics.
        is_running (bool): Flag indicating if the game is running.
        cursor_loc (list): Current cursor location.
        mouse_pressed (bool): Flag indicating if the mouse button is pressed.
        disable_PC_movement (bool): Flag indicating whether player character movement is disabled.
        autosavename (str): Base name for autosave files.
        autosaveindex (int): Index counter for autosave files.
        save_name (str): Name of the save file.
        load_name (str): Name of the file to be loaded.
        to_save (bool): Flag indicating if the game should be saved.
        to_load (bool): Flag indicating if a game should be loaded.

    Methods:
        __init__(self, width, height, save_layers, layer_funcs, always_draw, background_color,
                 units_per_pixel, save_folder, assets_folder): Constructor method for the Game class.
        setup(self): Initializes the game environment and sets up layers and widgets.
        update(self): Updates the game state, handles input, and manages component updates.
        update_PC(self): Updates the player character's movement based on the current layer.
        change_layer(self, layer_id): Changes the current active layer of the game.
        add_layer(self, widget_dicts, **kwargs): Adds a new layer with specified widgets and attributes.
        load_layer(self, layer, name): Loads a layer from a saved state.
        get_component(self, component_id): Retrieves a component based on its ID.
        get_all_components(self): Retrieves a list of all components in the game.
        get_component_dict(self): Retrieves a dictionary containing all component types.
        get_all_ids(self): Retrieves a list of IDs for all components.
        get_all_ids_dict(self): Retrieves a dictionary mapping IDs to their respective components.
        save(self): Saves the game's current state to a file.
        load(self): Loads a saved game state from a file.
        convert_all_strs(self): Converts graphical components to their string representations.
        convert_to_save(self): Converts components to a format suitable for saving.
        logic(self): Placeholder method for game logic.
        physics_check(self): Placeholder method for physics checks.
    """
    actors = dict()
    text_boxes = dict()
    buttons = dict()
    layers = dict()
    widgets = dict()
    graphics = dict()
    actors_index = 0
    buttons_index = 0
    text_boxes_index = 0
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
                 assets_folder = './'):
        self.layer_funcs = layer_funcs
        self.width = width
        self.height = height
        self.size = np.array([width, height])
        self.always_draw = always_draw
        self.background_color = background_color
        self.PC = dict()
        self.units_per_pixel = units_per_pixel
        self.ind_to_letter = { getattr(pg,'K_' + x) : x for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}
        self.letter_to_ind =  { x : getattr(pg,'K_' + x) for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}
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
        self.assets_folder = assets_folder
        self.pressed_status = pg.key.get_pressed()
        
    def setup(self):
        self.screen = self.handler.screen
        self.screen.fill(self.background_color)
        for fun in self.layer_funcs:
            widgets, layer_dict = fun(self)
            self.add_layer(widgets, **layer_dict)
        self.current_layer = "Main_menu"
    
    def update(self):
        self.screen.fill(self.background_color)
        self.mouse_pressed = pg.mouse.get_pressed()
        self.cursor_loc = ((self.handler.cursor_loc - self.handler.padding) / 
                           self.handler.scale)
        self.prev_held = copy(self.held_index)
        self.pressed_status = pg.key.get_pressed()
        self.held_index = {i for i, tf, in self.letter_to_ind.items() if self.pressed_status[tf]}
        if self.to_save: self.save()
        if self.to_load: self.load()
        self.layers[self.current_layer].update()
        run_updates(self)
        self.physics_check()
        
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
                       self.text_boxes, self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.layers, self.widgets, 
                       self.buttons, self.actors, 
                       self.text_boxes, self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'layers' : self.layers,
            'widgets' : self.widgets,
                'buttons' : self.buttons, 
                'actors' : self.actors, 
                'text_boxes' : self.text_boxes, 
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
    A class representing a layer within a game environment containing various widgets and elements.

    Attributes:
        game (Game): Reference to the game instance to which the layer belongs.
        always_draw (bool): Flag indicating whether the layer's contents should be drawn continuously.
        id (str): Unique identifier for the layer.
        initialized (bool): Flag indicating if the layer has been initialized.
        actors (dict): Dictionary of actor instances within the layer.
        buttons (dict): Dictionary of button instances within the layer.
        widgets (dict): Dictionary of widget instances within the layer.
        text_boxes (dict): Dictionary of text box instances within the layer.
        graphics (dict): Dictionary of graphic instances within the layer.
        widget_id_index (int): Index counter for widget IDs.
        prev_screen (Surface): Previous screen snapshot used for screen clearing.
        uses_prev_screen (bool): Flag indicating whether the previous screen snapshot is used.
        to_update_attrs (dict): Dictionary of attributes to update when the layer updates.

    Methods:
        __init__(self, uses_prev_screen=False, name=None): Constructor method for the Layer class.
        initial(self): Initializes the layer's widgets.
        update(self): Updates the layer's state and manages widget updates.
        add_widget(self, widget_dict): Adds a new widget to the layer.
        add_widget_id(self): Generates and returns a new widget ID.
        get_component(self, component_id): Retrieves a component based on its ID.
        get_all_components(self): Retrieves a list of all components in the layer.
        get_component_dict(self): Retrieves a dictionary containing all component types.
        get_all_ids(self): Retrieves a list of IDs for all components.
        to_dict(self): Converts the layer's widgets to a dictionary representation.
        logic(self): Placeholder method for layer-specific logic.
    """
    
    def __init__(self, uses_prev_screen = False, name = None):
        self.game = None
        self.always_draw = False
        self.id = name
        self.initialized = False
        self.actors = dict()
        self.buttons = dict()
        self.widgets = dict()
        self.text_boxes = dict()
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
        
        for obj_type in ['actors', 'buttons', 'text_boxes', 'graphics']:
            if obj_type in widget_dict:
                for obj in widget_dict[obj_type]:
                    widget.__getattribute__('add_' + obj_type[:-1])(obj)
                    
        if 'id' in widget_dict:
            if not  widget_dict['id'].startswith("widget_"):
                 widget_dict['id'] = 'widget_' +  widget_dict['id']
            widget.id = widget_dict['id']
        else: widget.id = self.add_widget_id()
        if 'other' in widget_dict:
            for key in widget_dict['other']:
                widget.__setattr__(key, widget_dict['other'][key])
        self.widgets[widget.id] = widget
        
    def add_widget_id(self):
        id_num = str(self.widget_id_index)
        self.widget_id_index += 1
        return "widget_" + id_num
    
    def get_component(self, component_id):
        components =  [self.widgets, self.buttons,
                       self.actors, self.text_boxes, 
                       self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.widgets, self.buttons,
                       self.actors, self.text_boxes, 
                       self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'widgets' : self.widgets,
                'buttons' : self.buttons, 
                'actors' : self.actors, 
                'text_boxes' : self.text_boxes, 
                'graphics' : self.graphics}
    
    def get_all_ids(self):
        return [x.id for x in self.get_all_components()]

    def to_dict(self):
        return [w.to_dict() for w in self.widgets.values()]
    
    def logic(self):
        None
        
class Widget():
    
    """
    A class representing a graphical user interface widget within a layer of the game.

    Attributes:
        game (Game): Reference to the game instance to which the widget belongs.
        always_draw (bool): Flag indicating whether the widget should be drawn continuously.
        id (str): Unique identifier for the widget.
        initialized (bool): Flag indicating if the widget has been initialized.
        actors (dict): Dictionary of actor instances associated with the widget.
        buttons (dict): Dictionary of button instances associated with the widget.
        text_boxes (dict): Dictionary of text box instances associated with the widget.
        graphics (dict): Dictionary of graphic instances associated with the widget.
        position (ndarray): Position of the widget on the screen.
        size (ndarray): Size of the widget.
        colorkey (tuple or None): Colorkey used for transparency in the widget's surface.
        surf_orig (Surface): Original surface of the widget.
        has_colorkey (bool): Flag indicating if the widget has a colorkey set.
        to_draw (bool): Flag indicating whether the widget should be drawn.
        to_update (bool): Flag indicating whether the widget should be updated.
        alpha (int): Alpha value for the widget's transparency.
        color (tuple): Background color of the widget.
        hover_over (bool): Flag indicating if the cursor is hovering over the widget.
        is_selected (bool): Flag indicating if the widget is currently selected.
        is_pressed (bool): Flag indicating if the widget is currently being pressed.
        to_update_attrs (dict): Dictionary of attributes to update when the widget updates.

    Methods:
        __init__(self, size, position, bkg_color, colorkey=None, alpha=255):
            Constructor method for the Widget class.
        initial(self): Initializes the widget's surface and associated components.
        add_actor(self, act): Adds an actor instance to the widget.
        add_button(self, button): Adds a button instance to the widget.
        add_textbox(self, text_box): Adds a text box instance to the widget.
        add_graphic(self, graphic): Adds a graphic instance to the widget.
        add_obj(self, obj, obj_type): Adds a component to the widget.
        update(self): Updates the widget's state and manages associated component updates.
        update_actors(self): Updates actor instances associated with the widget.
        update_buttons(self): Updates button instances associated with the widget.
        update_text_boxes(self): Updates text box instances associated with the widget.
        update_graphics(self): Updates graphic instances associated with the widget.
        get_component(self, component_id): Retrieves a component based on its ID.
        get_all_components(self): Retrieves a list of all components associated with the widget.
        get_component_dict(self): Retrieves a dictionary containing all component types.
        get_all_ids(self): Retrieves a list of IDs for all components associated with the widget.
        remove_component(self, component_id): Removes a component from the widget.
        move_component(self, component_id, new_widget_id): Moves a component to a different widget.
        return_ids(self): Restores component IDs and associations after loading.
        to_dict(self): Converts the widget and its associated components to a dictionary representation.
        logic(self): Placeholder method for widget-specific logic.
    """
    
    def __init__(self, size, position, bkg_color, colorkey = None, alpha = 255):
        self.game = None
        self.always_draw = False
        self.id = None
        self.initialized = False
        self.actors = dict()
        self.buttons = dict()
        self.text_boxes = dict()
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
        self.add_obj(text_box, 'text_boxes')
        
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
            self.cursor_loc = self.game.cursor_loc - self.position
            self.hover_over = all(x > 0 and x < self.size[i] for i, x 
                   in enumerate(self.cursor_loc))
            self.logic()
            self.surf = self.surf_orig.copy()
            run_updates(self)
        if self.to_draw:
            self.game.screen.blit(self.surf, self.position)
        # pg.display.flip()
        # Your drawing code goes here
        
    def update_actors(self):
        acts =  [x for x in self.actors.values()]
        for act in acts:
            if point_in_obj(self.cursor_loc, act):
                act.hover_over = True
            else: 
                act.hover_over = False
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
                if point_in_obj(self.cursor_loc, button):
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
            
    def update_text_boxes(self):
        text_boxes = [x for x in self.text_boxes.values()]
        for text_box in text_boxes:
            try:
                if (self.game.mouse_pressed[0] and 
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
                       self.text_boxes, self.graphics]
        for component_type in components:
            if component_id in component_type:
                return component_type[component_id]
            
        return None
    
    def get_all_components(self):
        components =  [self.buttons, self.actors,
                       self.text_boxes, self.graphics]
        return [component for component_type in components for 
                component in component_type.values()]
    
    def get_component_dict(self):
        return {'buttons' : self.buttons, 
                'actors' : self.actors, 
                'text_boxes' : self.text_boxes, 
                'graphics' : self.graphics}
    
    def get_all_ids(self):
        return [x.id for x in self.get_all_components()]
    
    def remove_component(self, component_id):
        components =  [self.buttons, self.actors,
                       self.text_boxes, self.graphics]
        for component_type in components:
            if component_id in component_type:
                del component_type[component_id]
                break
        self.layer.remove_component(component_id)
        
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
        #print(colors[])
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
    A mixin class providing deletion functionality for game components.
    
    Methods:
        __del__(self): Destructor method to remove the instance from associated stores (actors, buttons, etc.).
    """
    def __del__(self):
        stores = [getattr(self, storeName) for storeName in ['game', 'layer', 'widget'] if storeName in dir(self)]
        for store in stores:
            if self.id in store.actors: del store.actors[self.id]
            elif self.id in store.buttons: del store.buttons[self.id]
            elif self.id in store.text_boxes: del store.text_boxes[self.id]
            elif self.id in store.graphics: del store.graphics[self.id]
            
class Actor(Deleteable):
    """
    A class representing an actor within the game environment.

    Attributes:
        position (ndarray): Current position of the actor.
        target (ndarray): Target position the actor aims to reach.
        size (ndarray or None): Size of the actor.
        speed (float): Movement speed of the actor in pixels per second.
        current_action (function): Current action the actor is performing.
        color (list): Color of the actor.
        always_draw (bool): Flag indicating whether the actor should always be drawn.
        id (str): Unique identifier for the actor.
        to_draw (bool): Flag indicating whether the actor should be drawn.
        to_update (bool): Flag indicating whether the actor should be updated.
        is_pc (bool): Flag indicating if the actor is the player character.
        hover_over (bool): Flag indicating if the cursor is hovering over the actor.
        is_selected (bool): Flag indicating if the actor is currently selected.
        is_pressed (bool): Flag indicating if the actor is currently being pressed.
        death_timer (float): Timer tracking actor's lifespan after death.
        death_timer_limit (float or None): Time limit after which the actor is removed after death.
        surf (Surface): Surface representing the visual appearance of the actor.
        is_physics_object (bool): Flag indicating if the actor is affected by physics checks.
        to_update_attrs (dict): Dictionary of attributes to update when the actor updates.

    Methods:
        update(self): Updates the actor's state, movement, and behavior.
        move_to(self, dt): Moves the actor toward a target position.
        move_away(self, dt): Moves the actor away from a target position.
        center(self): Returns the center position of the actor.
        do_nothing(self, dt): Placeholder method for no-action state.
        change_position(self, prev_position, prev_size): Updates the position of the actor.
        init_draw(self): Initializes the actor's appearance and surface.
        logic(self): Placeholder method for AI and movement logic.
        movement(self): Placeholder method for player input and movement.
        physics_check(self): Placeholder method for physics-related checks.
        kill(self): Destroys the actor instance.
        retarget_by_center(self): Adjusts the target based on the center position.
    """
    def __init__(self, position, size = None, speed = 120, 
                 target = np.array([800,800]), color = [0,0,0],
                 always_draw = False, death_timer_limit = None):
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
            
    def update(self):
        if not self.death_timer_limit is None and self.death_timer >= self.death_timer_limit:
            self.kill()
        prev_size = copy(self.size)
        prev_position = copy(self.position)
        if self.is_physics_object:
            self.physics_check()
        if self.to_update:
            self.movement()
            self.logic()
            self.current_action(self.game.dt)
            run_updates(self)
        #if self.always_draw or not is_same_vec(self.position, prev_position):
        self.change_position(prev_position, prev_size)
        return 1
        return 0
        
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
        
    def change_position(self, prev_position, prev_size):
        if self.to_draw:
            self.widget.surf.blit(self.surf, self.position)
            
    def init_draw(self):
        if type(self.size) != type(None):
            upp = self.game.units_per_pixel
            
            self.surf = pg.Surface(self.size)
            self.surf.fill(self.color)
            self.change_position(self.position, self.size)
    
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
    A class representing a graphical button within the game environment.

    Attributes:
        size (ndarray): Size of the button.
        position (ndarray): Position of the button on the screen.
        surf (Surface): Surface representing the visual appearance of the button.
        hover_over_surf (Surface): Surface for button appearance when hovered over.
        pressed_surf (Surface): Surface for button appearance when pressed.
        font (Font): Font used for displaying text on the button.
        font_details (list): Font details including name, size, and color.
        color (tuple): Color of the button.
        alpha (int): Transparency value of the button's text.
        text (str or None): Text displayed on the button.
        always_draw (bool): Flag indicating whether the button should always be drawn.
        id (str): Unique identifier for the button.
        to_update (bool): Flag indicating whether the button should be updated.
        to_draw (bool): Flag indicating whether the button should be drawn.
        is_pressed (bool): Flag indicating if the button is currently being pressed.
        hover_over (bool): Flag indicating if the cursor is hovering over the button.
        is_selected (bool): Flag indicating if the button is currently selected.
        to_update_attrs (dict): Dictionary of attributes to update when the button updates.

    Methods:
        init_draw(self): Initializes the button's appearance and surface.
        update(self): Updates the button's state, appearance, and behavior.
        run_pressed(self): Placeholder method to run when the button is pressed.
        logic(self): Placeholder method for button-specific logic.
    """
    
    def __init__(self, position, size, color, alpha, text = None, 
                 font = ['Arial', 25, (255, 0, 0)]):
        self.size = np.array(size)
        self.position = np.array(position)
        self.surf = pg.Surface(self.size)
        self.surf.fill((3,5,7))
        self.surf.set_colorkey((3,5,7))
        #self.surf.set_alpha(0)
        
        pg.draw.polygon(self.surf, color, make_fancy_rect_border(size))
        self.hover_over_surf = self.surf.copy()
        pg.draw.polygon(self.hover_over_surf, (180, 240, 200), 
                        make_fancy_rect_border(size,4))
        self.pressed_surf = self.hover_over_surf.copy()
        pg.draw.polygon(self.pressed_surf, (140, 220, 140), 
                        make_fancy_rect_border(size,12))
        
        self.font = pg.font.SysFont(font[0], font[1])
        self.font_details = font
        self.color = color
        self.alpha = alpha
        self.text = text
        self.always_draw = True
        self.id = None
        self.to_update = True
        self.to_draw = True
        self.is_pressed = False
        self.hover_over = False
        self.is_selected = False
        self.to_update_attrs = dict()
        
    def init_draw(self):
        self.update()
        
    def update(self):
        if self.to_update:
            self.logic()
            if self.is_pressed: 
                surf = self.pressed_surf
                self.font.set_bold(True)
            elif self.hover_over: surf = self.hover_over_surf.copy()
            else: surf = self.surf.copy()
            run_updates(self)
        else: surf = self.surf.copy()
        if self.to_draw:
            if not self.text is None:
                font_surf = self.font.render(self.text, True,
                                             self.font_details[2], None)
                font_surf.set_alpha(self.alpha)
                font_size = np.array(font_surf.get_size())
                font_button_size_diff = (self.size - font_size)//2
                
                surf.blit(font_surf, font_button_size_diff)
            self.widget.surf.blit(surf, [self.position[0], self.position[1]])
        if self.is_pressed:
            self.font.set_bold(False)
        return 1
        
    def run_pressed(self):
        None
        
    def logic(self):
        None
class ChangeLayerButton(Button):
    """
    A class representing a button that changes the active layer in the game environment.

    Attributes:
        layer_id (str): Identifier of the layer to switch to when the button is pressed.
        
    Inherited Attributes (from Button):
        size (ndarray): Size of the button.
        position (ndarray): Position of the button on the screen.
        surf (Surface): Surface representing the visual appearance of the button.
        hover_over_surf (Surface): Surface for button appearance when hovered over.
        pressed_surf (Surface): Surface for button appearance when pressed.
        font (Font): Font used for displaying text on the button.
        font_details (list): Font details including name, size, and color.
        color (tuple): Color of the button.
        alpha (int): Transparency value of the button's text.
        text (str or None): Text displayed on the button.
        always_draw (bool): Flag indicating whether the button should always be drawn.
        id (str): Unique identifier for the button.
        to_update (bool): Flag indicating whether the button should be updated.
        to_draw (bool): Flag indicating whether the button should be drawn.
        is_pressed (bool): Flag indicating if the button is currently being pressed.
        hover_over (bool): Flag indicating if the cursor is hovering over the button.
        is_selected (bool): Flag indicating if the button is currently selected.
        to_update_attrs (dict): Dictionary of attributes to update when the button updates.

    Methods:
        init_draw(self): Initializes the button's appearance and surface.
        update(self): Updates the button's state, appearance, and behavior.
        run_pressed(self): Method to run when the button is pressed, changing the active layer.
        logic(self): Placeholder method for button-specific logic.
    """
    def __init__(self, layer_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_id = layer_id
        
    def run_pressed(self):
        self.game.change_layer(self.layer_id)

class Textbox(Deleteable):
    
    """
    A class representing a text box that allows user input.
    
    Attributes:
        ind_to_letter (dict): Mapping of key indices to corresponding letters.
        ind_to_num (dict): Mapping of key indices to corresponding numerical digits.
        num_to_ind (dict): Mapping of numerical digits to corresponding key indices.
        period_ind (int): Key index for the period character ('.').
        font (Font): Font used for displaying text in the textbox.
        font_details (list): Font details including name, size, and color.
        size (ndarray): Size of the textbox.
        position (ndarray): Position of the textbox on the screen.
        surf (Surface): Surface representing the visual appearance of the textbox.
        blink_count (int): Counter for text cursor blinking animation.
        delay_count (int): Counter to manage key press delay.
        text (str): Text currently entered in the textbox.
        default_text (str): Default text displayed when the textbox is empty and not selected.
        max_text_length (int or None): Maximum length of the entered text (or None for no limit).
        id (str): Unique identifier for the textbox.
        to_draw (bool): Flag indicating whether the textbox should be drawn.
        to_update (bool): Flag indicating whether the textbox should be updated.
        hover_over (bool): Flag indicating if the cursor is hovering over the textbox.
        is_selected (bool): Flag indicating if the textbox is currently selected for input.
        to_update_attrs (dict): Dictionary of attributes to update when the textbox updates.

    Methods:
        update(self): Updates the textbox's state, appearance, and behavior.
        init_draw(self): Initializes the textbox's appearance and surface.
        get_pressed_index_dict(self, exclude_numbers, exclude_letters, exclude_period): Creates a dictionary of pressed key indices and their corresponding characters.
        add_pressed_letters(self): Adds pressed letters to the textbox's entered text.
        on_enter(self): Placeholder method for handling the "Enter" key press action.
    """
    
    ind_to_letter = { getattr(pg, 'K_' + x) : x for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}
    
    ind_to_letter[pg.K_SPACE] = " "
    period_ind = pg.K_PERIOD
    ind_to_letter[pg.K_COMMA] = ","
    letter_to_ind = {y : x for y,x in ind_to_letter.items()}
    ind_to_num = {getattr(pg, 'K_' + x) : x for i,x in enumerate("1234567890")}
    num_to_ind = {y : x for y,x in ind_to_num.items()}
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
        self.size = np.array([length, round(font[1] * 16/12)+12])
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
        
    def update(self):
        if self.is_selected and self.to_update:
            if self.delay_count == 0:
                if self.game.pressed_status[pg.K_BACKSPACE]:
                    self.delay_count+=1
                    self.text = self.text[:-1]
                if self.max_text_length is None or len(self.text) < self.max_text_length:
                    self.add_pressed_letters()
                if self.game.pressed_status[pg.K_RETURN]:
                    self.on_enter()
            else:
                self.delay_count+=1
                if self.delay_count == 5:
                    self.delay_count = 0
            output_text = self.text
            if self.blink_count < 20:
                output_text = self.text + "|"
            elif self.blink_count >= 40:
                self.blink_count = -1
            self.blink_count += 1
            run_updates(self)
        else:
            output_text = self.text
        if output_text == "" and not self.is_selected:
            output_text = self.default_text
        if self.to_draw:
            font_surf = self.font.render(output_text, True, 
                                     self.font_details[2], None)
        temp = self.surf.copy()
        temp.blit(font_surf, [6,6])
        self.widget.surf.blit(temp, self.position)
        #print(output_text)
        return 1
    
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
   A class representing a graphical element that can display images and surfaces.

   Attributes:
       width (int): Width of the graphic.
       height (int): Height of the graphic.
       position (ndarray): Position of the graphic on the screen.
       surf (Surface): Main surface of the graphic.
       orig_color (tuple): Original color of the graphic's background.
       surfs (dict): Dictionary storing information about additional surfaces and their properties.
       surf_index (int): Index used to track additional surfaces.
       id (str): Unique identifier for the graphic.
       to_draw (bool): Flag indicating whether the graphic should be drawn.
       to_update (bool): Flag indicating whether the graphic should be updated.
       to_update_attrs (dict): Dictionary of attributes to update when the graphic updates.

   Methods:
       add_surf(self, surf, position): Adds a new surface to the graphic.
       update(self): Updates the graphic's state and appearance.
       redraw(self): Restores the original graphic surface and redraws all added surfaces.
       surf_update(self, surf, surf_ind): Updates an existing added surface with a new surface.
       reposition_surf(self, surf_ind, position): Repositions an added surface.
       shift_surf(self, surf_ind, shift_amt): Shifts the position of an added surface by a given amount.
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
        
    def add_surf(self, surf, position):
        self.surfs[self.surf_index] = [pg.image.tostring(surf, "RGBA"),
                                       np.array(surf.get_size()),
                                       np.array(position)]
        self.surf_index += 1
        self.surf.blit(surf, position)
    
    def update(self):
        if self.to_update:
            run_updates(self)
        if self.to_draw:
            self.widget.surf.blit(self.surf, self.position)
        return 0
    
    def redraw(self):
        self.surf = self.surf_orig.copy()
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
        
class SaveButton(Button):
    
    def run_pressed(self):
        self.game.to_save = True
        if not self.save_name_textbox.text is None:
            self.game.save_name = self.save_name_textbox.text

class LoadButton(Button):
    
    def run_pressed(self):
        self.game.to_load = True

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