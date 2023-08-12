# -*- coding: utf-8 -*-
"""
PyGame_ClassExt_smongan1 Package Documentation

This package provides extended classes and utilities for creating interactive and animated game objects using the Pygame library.

Classes:
- AnimatedActor: A class for managing animated game objects, allowing addition of animations, effects, and rotation.
- Animation: A class representing animations with frame rotation, specifications, and shadow rendering.
- HoverWidget: A class for creating interactive widgets with hover effects.
- DisplacementEffects: A class defining displacement effects for modifying actor position.

Usage Example:
```python
# Import the classes from the package
from PyGame_ClassExt_smongan1.BaseClasses import AnimatedActor, Animation
from PyGame_ClassExt_smongan1.widgets import HoverWidget
from PyGame_ClassExt_smongan1.utilities import DisplacementEffects

# Create an instance of AnimatedActor and add animations
animated_actor = AnimatedActor(position=(100, 100), size=(64, 64), speed=120)
animated_actor.AddAnimation("walking", scale=2, path="assets/characters")
animated_actor.animation = "walking"

# Create an instance of Animation and rotate frames
animation = Animation(animation_dir="assets/character_animations/idle", scale=2, size=(64, 64))
animation.rotate_to_target()
next_frame = next(animation)

# Create an instance of HoverWidget for interactive widgets
hover_widget = HoverWidget(position=(200, 200), size=(100, 50), color=(0, 0, 255))
hover_widget.initial()

# Create an instance of DisplacementEffects and apply effects to an actor
effects = DisplacementEffects(effect_types=["shake", "hover"], speed=1.0, magnitude=10.0)
actor.blend_effects(effects)

Created on Fri Dec 30 20:17:06 2022

@author: Sean Mongan
"""

from glob import glob
from PyGame_ClassExt_smongan1.BaseClasses import *
from PyGame_ClassExt_smongan1.utilities import *
from math import atan2
import pygame as pg
import copy
import numpy as np

class AnimatedActor(Actor):
    """
    AnimatedActor class extending the Actor class for managing animated game objects.
    
    This class inherits from the Actor class and extends its functionality to manage animated game objects. It provides methods for adding animations, effects, and rotating animations based on direction or tags.
    
    Attributes:
    - animations (dict): A dictionary storing Animation instances for various animations.
    - asset_folders (list): A list of asset folders to search for animation files.
    - effects (dict): A dictionary storing Effect instances for various effects.
    - effects_cnt (int): Counter for generating unique effect names.
    - default_none_animation (str): A default identifier for animations when none is specified.
    - animation (str): The currently active animation name.
    - prev_animation (str): The previously active animation name.
    - sheer_amt (numpy.array or None): The sheer amount applied to animations.
    - shadow_size (numpy.array): The size of the shadow for the animated object.
    - shadow (pygame.Surface): The shadow surface for the animated object.
    - shadow_offset (numpy.array): The offset position for rendering the shadow.
    
    Methods:
    - AddAnimation(self, asset_folder, scale=1, path=None, colorkey=None, frame_wait=None):
        Add animations from a specified asset folder to the animated actor.
    - AddEffect(self, effect, effect_name=None):
        Add an effect to the animated actor.
    - choose_animation(self):
        Choose and display the appropriate animation frame based on the current animation.
    - rotate_animations(self, direction=None, tags=None, names=None):
        Rotate the animations of the actor based on a given direction or tags.
    - update_effects(self):
        Update the effects associated with the animated actor.
    - draw_shadow(self):
        Draw the shadow of the animated actor based on its animation frames.
    
    Usage Example:
    ```python
    # Create an instance of AnimatedActor
    animated_actor = AnimatedActor(position=(100, 100), size=(64, 64), speed=120)
    
    # Add animations to the actor
    animated_actor.AddAnimation("walking", scale=2, path="assets/characters")
    
    # Choose an animation to play
    animated_actor.animation = "walking"
    
    # Rotate animations based on a direction
    animated_actor.rotate_animations(direction=(1, 0))
    
    # Add effects to the actor
    animated_actor.AddEffect(MyEffect(), effect_name="unique_effect")
    
    # Update animations and effects
    animated_actor.choose_animation()
    animated_actor.update_effects()
    
    # Draw the actor and its shadow
    animated_actor.draw()
    animated_actor.draw_shadow()
    """
    
    def AddAnimation(self, asset_folder, scale = 1, path = None,
                     colorkey = None, frame_wait = None):
        if not hasattr(self, 'asset_folder') or self.animations is None:
            self.asset_folders = []
            self.animations = dict()
            self.sheer_amt = None
        if asset_folder not in self.asset_folders:
            self.asset_folders.append(asset_folder)
        if path is None:
            path = self.game.handler.path
        path = '/'.join([path, asset_folder, '**/'])
        path = path.replace('/./', './')
        animation_folder = glob(path)
        for animation_fname in animation_folder:
            animation_name = animation_fname.split('_')[-1].lower()[:-1]
            animation = Animation(animation_fname, scale, self.size, colorkey)
            animation.actor = self
            animation.frame_wait = frame_wait
            if animation.name not in self.animations:
                self.animations[animation.name] = []
            self.animations[animation.name].append(animation)
        self.default_none_animation = 'DEFAULT_NONE_ANIMATION'
        self.animation = animation_name
        self.prev_animation = self.animation
        
    def AddEffect(self, effect, effect_name = None):
        if not hasattr(self, 'effects'):
            self.effects = dict()
            self.effects_cnt = 0
            
        if effect_name is None:
            effect_name = "effect_" + str(self.effects_cnt)
            self.effects_cnt += 1
        effect.actor = self
        self.effects[effect_name] = effect
        
    def choose_animation(self):
        if self.animations is None:
            for folder in self.asset_folders:
                self.AddAnimation(folder, path = '')
        if self.animation == self.default_none_animation:
            return None
        if not self.animation is None and self.animation in self.animations:
            self.surf = None
            for animation_frame in self.animations[self.animation]:
                if self.surf is None:
                    self.surf = next(animation_frame)
                else:
                    self.surf.blit(next(animation_frame), [0,0])
            size = np.array(self.surf.get_size())
            if not size is self.size:
                
                self.position = (self.position + self.size//2 -
                                 size//2)
                self.size = size
            self.prev_animation = self.animation
        else:
            if not self.animation is None:
                print("Animation not found:", self.animation)

    def rotate_animations(self, direction = None, tags = None, names = None):
        for key in self.animations.keys():
            for animation in self.animations[key]:
                if ((tags is None or animation.tag in tags) and 
                    (names is None or animation.name in names)):
                    if direction is None:
                        animation.rotate_to_target()
                    else:
                        animation.rotate_to_direction(direction)
    
    def update_effects(self):
        if not hasattr(self, 'effects'):
            return None
        for effect in self.effects:
            next(self.effects[effect])
    
    def draw_shadow(self):
        if self.animation is None:
            return None
        for animation in self.animations[self.prev_animation]:
            if (not self.widget.sheer_amt is None and 
                self.sheer_amt != self.widget.sheer_amt):
                self.sheer_amt = self.widget.sheer_amt[:]
                animation.redraw_shadows()
            shadow_size = (animation.shadow_size *
                                              self.widget.shadow_stretch)
            if not hasattr(self, 'shadow_size'):
                self.shadow_size = shadow_size
                self.shadow = pg.transform.scale(animation.shadow,
                                                  shadow_size)
                self.shadow_offset = (self.size - shadow_size)
            if sum(abs(self.shadow_size - shadow_size))>0:
                self.shadow = pg.transform.scale(animation.shadow,
                                                  shadow_size)
                self.shadow_offset = self.size - shadow_size
            else:
                self.shadow = pg.transform.scale(animation.shadow,
                                                  self.shadow_size)
                self.shadow_offset = self.size - shadow_size
            self.widget.surf.blit(self.shadow, self.position +
                                               self.blit_offset + 
                                               self.shadow_offset)
        
class Animation():
    """
    Animation class for managing animation frames and properties.

    This class represents an animation with multiple frames and provides methods for rotating frames based on direction, applying specifications, and managing shadow rendering.
    
    Attributes:
    - name (str): The name of the animation.
    - tag (str): The tag associated with the animation.
    - animation_frames (list): A list of pygame.Surface objects representing animation frames.
    - animation_index (int): The index of the current animation frame.
    - actor (AnimatedActor): The associated AnimatedActor instance.
    - wait_time (float): The time waited for the next animation frame.
    - prev_target (numpy.array or None): The previous target position of the actor.
    - direction (numpy.array): The direction vector for frame rotation.
    - spec (dict): A dictionary storing animation specifications.
    
    Methods:
    - __next__(self): Get the next animation frame based on time elapsed and frame specifications.
    - rotate_to_target(self): Rotate animation frames to face the actor's target position.
    - rotate_to_direction(self, direction): Rotate animation frames to face a given direction.
    - add_spec(self, spec_file): Add animation specifications from a file.
    - kill_after_last_frame_check(self): Check if the animation should end and trigger actor death.
    - redraw_shadows(self): Redraw shadow frames based on the actor's sheer amount.
    
    Usage Example:
    ```python
    # Create an instance of Animation
    animation = Animation(animation_dir="assets/character_animations/idle",
                          scale=2, size=(64, 64))
    
    # Rotate animation frames based on target position
    animation.rotate_to_target()
    
    # Get the next animation frame
    next_frame = next(animation)
    
    # Add animation specifications from a file
    animation.add_spec("specifications.txt")
    
    # Redraw shadow frames with updated sheer amount
    animation.redraw_shadows()
    """
    
    def __init__(self, animation_dir, scale, size, colorkey = None):
        identifiers = animation_dir.replace('\\', '/').split('_')
        self.name = identifiers[-1].lower()[:-1]
        self.tag = '_'.join(identifiers[:-1]).lower().split('/')[-1]
        self.animation_frames = []
        self.animation_index = 0
        self.actor = None
        self.wait_time = 0
        self.prev_target = None
        self.direction = [0,0]
        self.spec = {'time_per_frame' : 1/20,
                     'repeat' : True}
        files_in_folder = glob(animation_dir + '/' + '**')
        for animation_frame_fname in files_in_folder:
            if animation_frame_fname.endswith('dat'):
                self.add_spec(animation_frame_fname)
        size = np.array(size)
        if 'scale' in self.spec:
            scale *= self.spec['scale']
            size = size*self.spec['scale']
            
        if colorkey is None:
            if 'colorkey' in self.spec:
                colorkey = self.spec['colorkey']
            
        self.animation_frames = [
                load_image(animation_frame_fname, '', scale = scale, 
                           size = size, colorkey = colorkey)[0]
                for animation_frame_fname in files_in_folder
                if not animation_frame_fname.endswith('dat')]
        self.shadow_frames = [make_shadow(x) for x in self.animation_frames]
        self.shadow = self.shadow_frames[0]
        self.shadow_sizes = [x.get_size() for x in self.shadow_frames]
        self.shadow_size = self.shadow_sizes[0]
        
    def __next__(self):
        if (self.spec['time_per_frame'] is None) or (self.wait_time >= 
                                                     self.spec['time_per_frame']):
            self.animation_index += 1
            self.wait_time = 0
        else:
            self.wait_time += self.actor.game.dt
        if self.animation_index >= len(self.animation_frames):
            if self.spec['repeat']: self.animation_index = 0
            else: 
                self.animation_index = len(self.animation_frames) - 1
                self.kill_after_last_frame_check()
        self.shadow = self.shadow_frames[self.animation_index]
        self.shadow_size = self.shadow_sizes[self.animation_index]
        return self.animation_frames[self.animation_index]
    
    def rotate_to_target(self):
        if not self.actor.target is self.prev_target:
            self.prev_target = self.actor.target
            direction = [x-y for x,y in zip(self.actor.target, self.actor.center())]
            self.rotate_to_direction(direction)
            
    def rotate_to_direction(self, direction):
        
        if not self.direction is direction and (not 'never_rotate' in self.spec
                                                or not self.spec['never_rotate']):
            dir2 = [x-y for x,y in zip(self.direction, direction)]
            self.direction = direction
            for i,x in enumerate(self.animation_frames):
                rotate_angle = round(360*atan2(dir2[1], -dir2[0]) /( 2 * 3.14145))
                while rotate_angle < 0:
                    rotate_angle+=360
                test = pg.transform.rotate(x, rotate_angle)
                self.animation_frames[i] = test
                
    def add_spec(self, spec_file):
        with open(spec_file, 'r') as fspec:
            for line in fspec.readlines():
                line = line.replace('\n', '').split('=')
                if len(line) > 1:
                    arg = line[1].strip()
                    if arg.lower() in ['true', 'false', '"true"', '"false"',
                                       "'true'", "'false'"]:
                        arg = arg.replace("'", "").replace('"', '')
                        arg = arg[0].upper() + arg[1:]
                    self.spec[line[0].strip()] = eval(arg)
            
    def kill_after_last_frame_check(self):
        if 'kill_on_end' in self.spec and self.spec['kill_on_end']:
            self.actor.death_timer += self.actor.game.dt
    
    def redraw_shadows(self):
        self.shadow_frames = [make_shadow(x, self.actor.sheer_amt) for
                              x in self.animation_frames]
        self.shadow = self.shadow_frames[0]
        self.shadow_sizes = [x.get_size() for x in self.shadow_frames]
        self.shadow_size = self.shadow_sizes[0]
        
class HoverWidget(Widget):
    
    """
    HoverWidget class for creating interactive widgets with hover effect.
    
    This class represents a widget that responds to cursor hovering by adjusting its transparency. It provides methods to update the widget's appearance and behavior based on cursor interactions.
    
    Attributes:
    - game (Game): The reference to the main game object.
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
    - hover_over (bool): Flag indicating whether the cursor is over the widget.
    - alpha_has_changed (bool): Flag indicating whether the alpha value has changed due to hovering.
    
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
    - logic(self): Handle widget-specific logic updates, including hover effect.
    """
    
    def logic(self):
        if not hasattr(self, 'alpha_has_changed'):
            self.alpha_has_changed = False
        if self.hover_over:
            self.surf_orig.set_alpha(min(self.surf_orig.get_alpha() + 10, 255))
            self.alpha_has_changed = self
        else:
            if self.alpha_has_changed:
                alpha = self.surf_orig.get_alpha()
                self.surf_orig.set_alpha(max(alpha - 10, self.alpha))
                if alpha == self.alpha:
                    self.alpha_has_changed = False
                    
class DisplacementEffects():
    """
    A class representing displacement effects applied to an actor.

    This class defines various displacement effects that can be applied to an actor,
    such as shaking and hovering. The effects can be combined to achieve different visual
    effects. The displacement effects modify the blit offset of the actor to create the
    visual displacement.

    Parameters:
    - effect_types (str or list): The type(s) of displacement effect(s) to apply.
    - speed (float): The speed of the displacement effects.
    - magnitude (float): The magnitude of the displacement effects.
    - direction (numpy.array, optional): The direction of displacement. Default is [1, 0].

    Attributes:
    - effects (list): List of displacement effect types.
    - effect_count (list): List of counters for each displacement effect.
    - speed (float): The speed of the displacement effects.
    - magnitude (float): The magnitude of the displacement effects.
    - direction (numpy.array): The normalized direction of displacement.

    Methods:
    - __next__(self): Apply the displacement effects on the actor's blit offset.
    - shake(self, cnt): Apply a shaking effect based on the counter value.
    - hover(self, cnt): Apply a hovering effect based on the counter value.
    """
    def __init__(self, effect_types, speed, magnitude, direction = None):
        if isinstance(effect_types, str):
            effect_types = [effect_types]
        self.effects = effect_types
        self.effect_count = [0 for x in self.effects]
        self.speed = speed
        self.magnitude = magnitude
        if direction == None:
            self.direction = np.array([1, 0])
        else:
            self.direction = direction/np.linalg.norm(direction)
             
    def __next__(self):
        offsets = np.zeros(2)
        for i, effect in enumerate(self.effects):
             offset, self.effect_count[i] = self.__getattribute__(effect)(self.effect_count[i])
             offsets += offset
        self.actor.blit_offset += offsets
        
    def shake(self, cnt):
        if not hasattr(self, 'shake_dir'):
            self.shake_dir = 1
        displace_mag = self.speed * cnt
        if abs(displace_mag) >= self.magnitude:
            displace_mag = self.magnitude * self.shake_dir
            self.shake_dir = -self.shake_dir
        cnt = cnt + self.shake_dir
        if self.direction is None:  out = (np.ones(2)/(2**0.5))
        else: out = self.direction
        return out * displace_mag, cnt
    
    def hover(self, cnt):
        if not hasattr(self, 'hover_dir'):
            self.hover_dir = 1
        displace_mag = self.speed * cnt/10
        if abs(displace_mag) >= self.magnitude*0.1:
            displace_mag = self.magnitude*0.1 * self.hover_dir
            self.hover_dir = -self.hover_dir
        cnt = cnt + self.hover_dir
        return np.array([0, -self.magnitude + displace_mag]), cnt