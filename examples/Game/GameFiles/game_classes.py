"""
This script defines classes related to character movement and interactions in a game environment.

Script Overview:
- Defines the 'possible_character_augments' dictionary and 'max_speed' constant.
- Defines the 'Projectile' class for creating projectiles in the game.
- Implements logic for projectile movement and behavior when on target.
- Defines the 'MainActor' class representing the main character in the game.
- Implements logic for character movement, animation selection, and projectile creation.
- Defines the 'red_square' class representing red square actors in the game.
- Implements logic for the movement of red square actors within the game environment.

Usage:
- Integrate this script into your game development project to add character and projectile functionalities.
- Customize the behaviors and animations within the 'Projectile', 'MainActor', and 'red_square' classes.

Note: This script is designed to be a part of a larger game development project and may require additional modules and classes.

Author: Sean Mongan
Date: 1/2/2023
"""
possible_character_augments = {}
max_speed = 1000

class Projectile(AnimatedActor):
    
    def logic(self):
        self.center_ = self.center()
        self.current_action = self.move_to
        diff_sum = sum([x-y for x,y in zip(self.center_, self.target)])
        if abs(diff_sum) > 2:
            self.animation = 'fly'
        else:
            self.on_target()
        self.choose_animation()
            
    def on_target(self):
        self.animation = 'bigexplosion'
        self.current_action = self.do_nothing
        
    def on_first_touched(self):
        None
        
class MainActor(AnimatedActor):
    
    def logic(self):
        if self.target[0] - self.center_[0] > 10:
            self.animation = 'walkingright'
        if self.target[1] - self.center_[1] > 10:
            self.animation =  'walkingdown'
        if self.target[0] - self.center_[0] < -10:
            self.animation = 'walkingleft'
        if self.target[1] - self.center_[1] < -10:
            self.animation = 'walkingup'
        if not hasattr(self, 'fireball_counter'):
            self.fireball_counter = 0
            self.launched_fireball = False
        self.choose_animation()
        self.animation = None
        
        if self.launched_fireball:
            self.fireball_counter += 1
        if self.fireball_counter >= 15:
            self.launched_fireball = False
            self.fireball_counter = 0
            
        if not self.launched_fireball and self.game.pressed_status[pg.K_SPACE]:
            try:
                p = Projectile(self.center_, size = [50,50], 
                               death_timer_limit = .075)
                
                p.position = [y-x for x,y in zip(p.size, p.center())]
                
                self.widget.add_actor(p)
                p.AddAnimation(os.path.join(self.game.assets_folder, 'fireball'), 
                               frame_wait = 10, scale = 2,
                               colorkey = (3,5,7))
                p.target = [round(x) for x in self.widget.cursor_loc]
                p.rotate_animations()
                self.launched_fireball = True
                
            except Exception as err:
                raise(err)
            #pg.quit()
            
    def movement(self):
        self.center_ = self.center()
        self.target = copy(self.center_)
        #RIGHT ARROW
        if self.game.pressed_status[pg.K_d]: self.target += np.array([max_speed,0])
        #LEFT ARROW
        if self.game.pressed_status[pg.K_a]: self.target += np.array([-max_speed,0])
        #DOWN ARROW
        if self.game.pressed_status[pg.K_s]: self.target += np.array([0,max_speed])
        #UP ARROW
        if self.game.pressed_status[pg.K_w]: self.target += np.array([0,-max_speed])
        if not is_same_vec(self.center_, self.target):
            self.current_action = self.move_to 
            
class red_square(Actor):
    
    def __init__(self, position):
        super().__init__(position, (25, 25), color = (255, 0, 0))
        self.current_action = self.move_to
        self.target = np.array([position[0] + 25/2, np.random.choice([-200,1000])])
    
    def logic(self):
        if self.position[1] <= 1:
            self.target[1] = self.widget.size[1]+100
            self.position[1] = 1
        elif self.position[1] >= self.widget.size[1]:
            self.target[1] = 0
            self.position[1] = self.widget.size[1]-1