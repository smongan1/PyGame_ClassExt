# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 14:22:52 2022

@author: Sean
"""

import warnings
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def draw_circle(position, rc):
    x = position[0]
    y = position[1]
    r = rc[0]
    c = rc[1]
    arcade.draw_circle_filled(x, y, r, c)
    
def draw_nothing(x):
    pass

def no_update(x):
    pass

def gravity(position, source):
    from np import array
    m = source[2]
    G = 6.6743 * 10**(-11)
    dis = array(position) - array(source[:2])
    mag = sum(dis**2)
    return m * G/mag

class actor():
    
    draw_fun = draw_nothing
    draw_params = []
    vel_updates = [[no_update,  []]]
    
    def __init__(self, position, velocity = [0, 0]):
        self.position = position
        self.velocity = velocity
        
    def draw(self):
        self.draw_fun(self.position, self.draw_params)
        
    def a_update(self, dt):
        for [update_fun, params] in self.vel_updates:
            self.velocity = self.velocity + update_fun(self.position, params)*dt
    
class MyGame(arcade.Window):
    """ Main application class. """
    actors = []
    def __init__(self, width, height):
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):
        a1 = actor([400, 300])
        a1.draw_fun = draw_circle
        a1.draw_params = [100, (125, 10, 80)]
        self.actors.append(a1)
        # Set up your game here
        pass

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        #for actor in self.actors:
        #    actor.draw()
            
        # Your drawing code goes heren

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        #for actor in self.actors:
        #    actor.a_update(delta_time)
        pass
        
def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()
    


if __name__ == "__main__":
    main()