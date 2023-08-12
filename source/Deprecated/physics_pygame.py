# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 21:50:06 2022

@author: Sean
"""

# Simple pygame program

# Import and initialize the pygame library
import pygame
import time
import numpy as np
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

def draw_circle(position, screen, rc):
    x = position[0]
    y = position[1]
    r = rc[0]
    c = rc[1]
    pygame.draw.circle(screen, c, (x, y), r)
    max_x = x + r
    min_x = x - r
    max_y = y + r
    min_y = y - r
    max_dim = r*2
    return max_x, max_y, min_x, min_y, max_dim

def draw_rect(position, screen, hwcrot):
    x = position[0]
    y = position[1]
    height = hwcrot[0]
    width = hwcrot[1]
    color = hwcrot[2]
    if len(hwcrot) >= 4:
        rot = hwcrot[3]
    else:
        rot = 0
    max_x = position[0]
    min_x = position[0]
    max_y = position[1]
    min_y = position[1]
    points = [[0,0], [0,0], [0,0], [0,0]]
    w_points = [1, 1, -1, -1]
    for i, k in enumerate([1, -1, -1, 1]):
        x_p = x + width/2*w_points[i]
        y_p = y + height/2*k
        points[i][0] = x_p * np.cos(rot) + y_p * np.sin(rot)
        points[i][1] = y_p * np.cos(rot) + x_p * np.sin(rot)
        max_x = max(max_x, points[i][0])
        min_x = min(min_x, points[i][0])
        max_y = max(max_y, points[i][1])
        min_y = min(min_y, points[i][1])
    max_dim = max(height, width)
    pygame.draw.polygon(screen, color, points)
    return max_x, max_y, min_x, min_y, max_dim
    
def draw_nothing(position, screen, params):
    return None, None, None, None

def no_update(position, params):
    from numpy import array
    return array([0,0])

def gravity(position, source):
    from numpy import array,square
    m = source[2]
    G = 6.6743 * 10**(-11)
    dis = (array(position) - array(source[:2]))
    mag = sum(square(dis))**.5
    return -m * dis * G/(mag**3)

def cirsqcoll(actor1, actor2):
    dis = actor1.position - actor2.position
    angle = np.arctan2(dis[0], dis[1])
    h = actor2.to_draw[0]
    w = actor2.to_draw[1]
    hs = w/(2*np.cos(angle))
    if hs < h:
        closestpoint = np.array([w,hs])
    else:
        ws = w/(2*np.cos(np.pi - angle))
        closestpoint = np.array([ws,h])
    dis = (actor1.position - closestpoint)
    dis = dis/abs(dis)
    if sum((dis)**2) < actor1.max_dimension**2:
        boo = True
    else:
        boo = False
    return dis, -dis, boo

def sqsqcoll(actor1, actor2):
    h1 = actor2.to_draw[0]
    w1 = actor2.to_draw[1]
    h2 = actor2.to_draw[0]
    w2 = actor2.to_draw[1]
    return 

class timer():
    def __init__(self):
        from time import time
        self.time = time
        
    def start(self):
        try: self.clk
        except: self.clk = 0
        self.start_time = self.time()
    
    def stop(self):
        self.clk += self.time() - self.start_time
    
    def reset(self):
        self.clk = 0
    
loop_timer = timer()

class actor():
    
    from numpy import array as array
    to_draw = [[draw_nothing,  []]]
    vel_updates = [[no_update,  []]]
    
    def __init__(self, position, velocity = [0, 0]):
        self.position = position
        self.velocity = self.array(velocity)
        self.max_x = self.position[0]
        self.min_x = self.position[0]
        self.max_y = self.position[1]
        self.min_y = self.position[1]
        self.type = None
        
    def draw(self, screen):
        for [fun, params] in self.to_draw:
            max_x, max_y, min_x, min_y, max_dim = fun(self.position, screen, params)
            self.max_x = max(max_x, self.max_x)
            self.min_x = min(min_x, self.min_x)
            self.max_y = max(max_y, self.max_y)
            self.min_y = min(min_y, self.min_y)
            self.max_dimension = max_dim
            
    def update(self, dt):
        is_updated = True
        for [update_fun, params] in self.vel_updates:
            dv = self.array(update_fun(self.position, params))*dt
            self.velocity = self.velocity + dv
        self.position = self.position + self.velocity*dt/self.game.scale
        
    def collide(self, actor2):
        dv1, dv2, boo = self.getcoll(self, actor2)
        if boo:
            self.velocity = self.velocity * dv1
            actor2.velocity = actor2.velocity * dv2
        pass
    
    def get_bin_index(self, h, w):
        bin_x1 = np.floor(self.max_x/w)
        bin_x2 = np.floor(self.min_x/w)
        bin_y1 = np.floor(self.max_x/w)
        bin_y2 = np.floor(self.min_x/w)
        xs = set([bin_x1, bin_x2])
        ys = set([bin_x1, bin_x2])
        ind = []
        for x in xs:
            for y in ys:
                ind.append([x,y])
        return ind
        
    def getDist(self, actor2):
        actor1 = self
        types = sorted(actor1.type, actor2.type)
        if types[0] == None or types[1] == None:
            return 1, 1, False
        order = [0, 1]
        if types[0] != actor1.type:
            actor1 = actor2
            actor2 = self
            order = [1, 0]
        if types[0] == 'triangle':
            dv, boo = tritricoll(actor1, actor2)
        elif types[0] == 'square':
            if types[1] == 'triangle':
                dv, boo = sqtricoll(actor1,actor2)
            else:
                dv, boo = sqsqcoll(actor1,actor2)
        elif types[0] == 'circle':
            if types[1] == 'circle':
                dv, boo = (actor1.max_dimensions + actor2.max_dimensions)/2
            elif types[1] == 'square':
                return cirsqcoll(actor1,actor2)
            else:
                return cirtricoll(actor1,actor2)
        return dv[order[0]], dv[order[1]], boo
    
class GameHandler():
    def __init__(self, MyGame, framerate = 60):
        from time import sleep, time
        MyGame.handler = self
        self.time = time
        self.sleep = sleep
        self.game = MyGame
        self.screen = pygame.display.set_mode([MyGame.width, MyGame.height])
        self.framerate = framerate
        
    def run(self):
        pygame.init()
        self.game.setup()
        self.lastFrameTime = self.time()
        running = True
        while running:
            loop_timer.start()
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT or not self.game.is_running:
                    running = False
            self.game.on_draw()
            pygame.display.flip()
            self.game.update(1/self.framerate)
            loop_timer.stop()
            self.chkFrameTime()
            
    def chkFrameTime(self):
        count = 0
        while self.time() - self.lastFrameTime < 1/self.framerate:
            self.sleep(0.000001)
            count += 1
        self.lastFrameTime = self.time()
    
class MyGame():
    """ Main application class. """
    
    actors = []
    is_running = True
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scale = 10
        
    def setup(self):
        self.screen = self.handler.screen
        a1 = actor([400, 300])
        a1.to_draw = [[draw_circle, [100, (125, 10, 80)]]]
        a1.vel_updates = [[gravity, [400.0, 6371000.0, 5.97*10**24, self.scale]]]
        floor = actor([400, 780])
        floor.to_draw = [[ draw_rect, [20, 600, (0, 0, 0) ] ]]
        self.add_actor(a1)
        self.add_actor(floor)
        self.screen.fill((255, 255, 255))
        # Set up your game here
        pass

    def on_draw(self):
        """ Render the screen. """
        self.screen.fill((255, 255, 255))
        for actor in self.actors:
            actor.draw(self.screen)
        pygame.display.flip()
        # Your drawing code goes here

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        num_bins = np.ceil(len(self.actors)**1/6)
        max_dim = self.max_dimension()
        w = min(self.width/num_bins, max_dim)
        h = min(self.height/num_bins, max_dim)
        actor_bins = dict()
        for actor in self.actors:
            actor.update(delta_time)
            indicies = actor.get_bin_index(w, h)
            for index in indicies:
                try:
                    actor_bins[index[0]][index[1]].append(actor)
                except: 
                    try: actor_bins[index[0]]
                    except: actor_bins[index[0]] = dict()
                    actor_bins[index[0]][index[1]] = [actor]
        self.collision(actor_bins)
        
    def collision(self, actor_bins):
        for key1 in actor_bins.keys():
            for key2 in actor_bins[key1].keys():
                actors = actor_bins[key1][key2]
                for i, actor1 in enumerate(actors):
                    for actor2 in actors[i+1:]:
                        actor1.collide(actor2)
                        
    def add_actor(self, actor):
        actor.game = self
        self.actors.append(actor)
    
    def max_dimension(self):
        max_dim = 0
        for actor in self.actors:
            max_dim = max(actor.max_dimension, max_dim)
        if max_dim == 0:
            return max(self.width, self.height)
        return max_dim
        
def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    handle = GameHandler(game)
    handle.run()

if __name__ == "__main__":
    main()

# Set up the drawing window
screen = pygame.display.set_mode([800, 600])

# Run until the user asks to quit

# Done! Time to quit.
pygame.quit()
