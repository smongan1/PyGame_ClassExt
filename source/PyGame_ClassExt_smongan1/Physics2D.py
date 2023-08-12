# -*- coding: utf-8 -*-
"""
Unfinished 2D Physics Engine for Game Development

This module provides an unfinished 2D physics engine designed for game development. It includes classes for managing collidable objects, rigid bodies, and a basic physics simulation.

Module Structure:
- PhysicsGame2D: A class extending the Game class to include basic physics simulation and collision handling.
- PhysicsActor2D: A class extending the Actor class to add physical properties and interactions.
- COM: A class representing the center of mass for rigid bodies.
- collision2D: A function to detect and handle collisions between two actors.
- reposition_actors: A function to reposition overlapping actors after a collision.
- getParallel: A function to calculate the parallel component of a vector.
- getPerp: A function to calculate the perpendicular component of a vector.

Usage Example:
```python
# Import classes and functions from the module
from physics_engine import PhysicsGame2D, PhysicsActor2D

# Create a physics-based game instance
physics_game = PhysicsGame2D()

# Create physics-enabled actors
actor1 = PhysicsActor2D(position=(100, 100), size=(50, 50), mass=1.0)
actor2 = PhysicsActor2D(position=(200, 200), size=(30, 30), mass=0.5)

# Add actors to the game
physics_game.add_actor(actor1)
physics_game.add_actor(actor2)

# Main game loop
while True:
    # Update physics simulation
    physics_game.physics_check()

    # Update game logic and rendering
    update_game_logic()
    render_game()

# Note: This example is a simplified representation. Actual usage may involve more complex interactions and setups.

Created on Mon Jan  2 12:51:48 2023

@author: Sean Mongan
"""
from glob import glob
from PyGame_ClassExt_smongan1.BaseClasses import Actor, Widget, Game
from PyGame_ClassExt_smongan1.utilities import load_image
from math import atan2
import pygame as pg
import copy
import numpy as np

class PhysicsGame2D(Game):
    def physics_check(self):
        self.bins = dict()
        if not hasattr(self, 'min_actor_size'):
            self.min_actor_size = [min([size[0] for size in self.actors.values()]),
                                   min([size[1] for size in self.actors.values()])]
            
        for widge in self.layers[self.current_layer].values():
            for actor in widge.actors.values():
                self.get_bins(actor)
        
        for b in self.bins.values():
            for i, actor1 in enumerate(b):
                for actor2 in b[(i+1):]:
                    collision2D(actor1, actor2)
                    
    def get_bins(self, actor):
        pos = actor.position
        pos_max = np.array(actor.position) + np.array(actor.size)
        min_bin_x = pos[0]//(4*self.min_actor_size[0])
        min_bin_y = pos[1]//(4*self.min_actor_size[1])
        max_bin_x = pos_max[0]//(4*self.min_actor_size[0])
        max_bin_y = pos_max[1]//(4*self.min_actor_size[1])
        for x_pos in range(min_bin_x, max_bin_x + 1):
            for y_pos in range(min_bin_y, max_bin_y):
                b = '@'.join([str(x_pos), str(y_pos)])
                if not b in self.bins:
                    self.bins[b] = []
                self.bins[b].append(actor)
                
class PhysicsActor2D(Actor):
    
    def AddCOM(self, mass = 0, position_offset = 0):
        self.COM = COM(mass, position_offset)
        self.velocity = np.array([0, 0])
        self.rotational_velocity = np.array([0, 0])
        self.is_physics_object = True
        self.is_stationary = False
        self.friction_coeff = 0
        self.num_jumps = 1
        self.forces = []
        self.is_jumping = False
        self.jump_count = 0
        self.jump_speed = 120
        self.fall_speed = 120
        self.jump_speed_time = 1/20
        self.jump_speed_change = 0
        self.touching = []
        
    def ApplyLinearForce(self, force):
        self.velocity += self.game.dt * force/self.mass
    
    def ApplyRotationalForce(self, force_mag, pos_vec):
        self.rotational_velocity += pos_vec * force_mag
        
    def SplitApplyForce(self, force, position):
        COM_position = self.position + self.COM.position_offset
        pos_vec = COM_position - position
        para_force = getParallel(pos_vec, force) * force
        perp_force = getPerp(pos_vec, force)
        self.ApplyLinearForce(para_force)
        self.ApplyRotationalForce(perp_force, pos_vec)
        
    def Jump(self):
        if self.is_jumping:
            jump_speed_inc = (self.jump_speed / self.jump_speed_time) * self.game.dt
            jump_speed_inc = min(jump_speed_inc, self.jump_speed - self.jump_speed_change)
            self.jump_speed_change += jump_speed_inc
            if self.jump_speed_change == self.jump_speed:
                self.is_jumping = False
            self.velocity += np.array([0, jump_speed_inc])
            
        if (44 in self.game.held_index and
            44 not in self.game.prev_held and self.jump_count < self.num_jumps):
            self.is_jumping = True
            self.jump_count += 1
            
        if self.is_on_ground:
            self.jump_count = 0
            
    def Falling(self):
        for actor in self.touching:
            if abs(self.position[1] + self.size[1] - actor.position[1]) <= 1.5:
                if ((self.position[0] > actor.position[0] and 
                    self.position[0] < (actor.position[0] + actor.size[0]))
                or ((self.position[0] + self.size[0]) > actor.position[0] and 
                    (self.position[0] + self.size[0]) < (actor.position[0] + actor.size[0]))):
                    self.is_on_ground = True
                    break
                
        if not self.is_on_ground:
            if self.velocity[1] > -self.fall_speed:
                self.velocity[1] += self.fall_speed * self.game.dt * self.fall_inc
    
class COM():
    
    def __init__(self, mass = 0, position_offset = np.array([0, 0])):
        self.mass = mass
        self.position_offset = position_offset
        
def collision2D(actor1, actor2):
    for actor_order in [[actor1, actor2], [actor2, actor1]]:
        true_false = True
        for i, pos1 in enumerate(actor_order[0].position):
            if not (pos1 > actor_order[1].position[i] and pos1 < (actor_order[1].position[i] +
                                                             actor_order[1].size[i])):
                true_false = False
                break
            
        if true_false:
            overlap = [(actor1.size[i]/2 + actor2.size[i]/2 - 
                        abs(actor1.position[i] - actor2.position[i])) for i in range(2)]
            if overlap[0] > overlap[1]:
                reposition_actors(actor1, actor2, 0)
            actor1.is_touching.append(actor2)
            actor2.is_touching.append(actor1)
            break
    
def reposition_actors(actor1, actor2, ind):     
    if actor1.is_stationary:
        if actor2.center()[ind] < actor1.center()[ind]:
            actor2.position[ind] = actor1.position[ind] + actor2.size[ind]
        else:
            actor2.position[ind] = actor1.position[ind] - actor1.size[ind]
            
    elif actor2.is_stationary:
        if actor1.center()[ind] < actor2.center()[ind]:
            actor1.position[ind] = actor2.position[ind] + actor1.size[ind]
        else:
            actor1.position[ind] = actor2.position[ind] - actor2.size[ind]
            
    else:
        overlap = (actor1.size[ind]/2 + actor2.size[ind]/2 - 
                        abs(actor1.position[ind] - actor2.position[ind]))
        if actor1.center()[ind] > actor2.center[ind]:
            actor1.position[ind] = actor1.position[ind] + overlap/2
            actor2.position[ind] = actor2.position[ind] - overlap/2
        else:
            actor1.position[ind] = actor1.position[ind] - overlap/2
            actor2.position[ind] = actor2.position[ind] + overlap/2
            
def getParallel(vec1, vec2):
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

def getPerp(vec1, vec2):
    getParallel(np.array([vec1[1], -vec1[0]]), vec2)