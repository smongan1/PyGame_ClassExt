# -*- coding: utf-8 -*-
"""
This script defines setup functions for creating various game widgets and layers.

Script Overview:
- Defines setup functions to initialize game widgets and layers for different game screens.
- Provides setup functions for the main game, main menu, in-game menu, save menu, and inventory.
- Each setup function returns dictionaries containing widget and layer configurations.
- Integrate these setup functions into your larger game development project.

Usage:
- Integrate this script into your game development project to define and configure different game screens.
- Customize the behaviors, buttons, graphics, and other aspects of each screen using the provided setup functions.
- Combine these setup functions with other scripts to create a complete game experience.

Author: Sean Mongan
Date: 1/2/2023
"""

def setup_main(game): 
    widget_dict_main_play = dict()
    a1 = MainActor(np.array([1, 1]), np.array([100, 100]), speed = 240)
    a1.AddAnimation(os.path.join(game.assets_folder, 'Soldier'), path = game.handler.path, colorkey = -1)
    a1.is_pc = True
    widget_dict_main_play["actors"] = [a1]
    for n in range(20):
        pos = np.random.choice(range(800))
        r = red_square(position = np.array([pos, 350]))
        widget_dict_main_play["actors"].append(r)
    game.PC["Main"] = a1
    widget_dict_main_play["size"] = [game.width, 
                           game.height]
    widget_dict_main_play["color"] = (180, 180, 180)
    widget_dict_main_play["position"] = [0, 0]
    widget_dict_main_play['id'] = "widget_MainGame"
    widget_dict_menu = dict()
    widget_dict_menu['size'] = [game.width, round(game.height*.08)]
    
    button_locs = centered_buttons_locs_hori([200, 50], 2, widget_dict_menu['size'])
    widget_dict_menu["buttons"] = [ChangeLayerButton("In_Game_Menu", button_locs[0], [200, 50], (100, 100, 255), 
                                          255, "MENU"), 
                                   ChangeLayerButton("Inventory", button_locs[1], [200, 50], (100, 100, 255), 
                                          255, "INVENTORY")]
    widget_dict_menu['color'] = (100, 100, 100)
    widget_dict_menu['position'] = [0,0]
    widget_dict_menu['alpha'] = 25
    widget_dict_menu['class'] = HoverWidget
    widget_dict_menu['colorkey'] = (100,100,100)
    return [widget_dict_main_play, widget_dict_menu], {"name" : "Main"}
        
def setup_main_menu(game):
    widget_dict = dict()
    button_pos = centered_buttons_locs_vert([200, 50], 2, 
                           [game.width, game.height], spacing = 20)
    button_color = (100, 100, 255)
    button_size = [200, 50]
    button_alpha = 255
    buttons = []
    buttons.append(
        ChangeLayerButton("Main", button_pos[0], button_size, button_color, 
                    button_alpha, "START")
        )
    buttons.append(
        ChangeLayerButton("Options", button_pos[1], button_size, button_color, 
                    button_alpha, "Options")
        )
    size = [game.height, game.width]
    position = [0, 0]
    color = (255,255,255)
    graphic = Graphic([300, 120], [250, 100])
    font = pg.font.SysFont('Arial', 60).render('Fecktopia', True, (150, 100, 100))
    graphic.add_surf(font, [20,20])
    widget_dict = make_widget_dict(size, position, color, 
                                  buttons = buttons,
                                  graphics = [graphic])
    return [widget_dict], {"name" : "Main_menu"}


#def setup_options():
    
def setup_ingame_menu(game):
    widget_dict = dict()
    widget_dict['size'] = game.size*.5
    widget_dict['position'] = game.size*.25
    button_color = (100, 100, 255)
    button_size = [200, 50]
    button_alpha = 255
    button_locs = centered_buttons_locs_vert([200, 50], 3, widget_dict['size'])
    widget_dict['buttons'] = [ChangeLayerButton("Save_Menu", button_locs[0], button_size, button_color, 
                                          button_alpha, "SAVE"),
                                   Button(button_locs[1], button_size, button_color, 
                                          button_alpha, "LOAD"),
                                   ChangeLayerButton("Main", button_locs[2], button_size, button_color, 
                    button_alpha, "EXIT")]
    widget_dict['color'] = (100,100,100)
    layer_dict = {'uses_prev_screen':True}
    layer_dict = {'name' : "In_Game_Menu"}
    return [widget_dict], layer_dict

def setup_save_menu(game):
    widget_dict = dict()
    widget_dict['size'] = game.size*.5
    widget_dict['position'] = game.size*.25
    widget_dict['class'] = SaveWidget
    widget_dict['color'] = (100,100,100)
    layer_dict = {'uses_prev_screen':True,
                  "name" : "Save_Menu"}
    return [widget_dict], layer_dict


def setup_inventory(game):
    inventory_widget_dict = dict()
    widget_dict_scroll = dict()
    
    inventory_widget_dict['size'] = game.size*.75
    inventory_widget_dict['position'] = [0, game.size[1]*.25]
    inventory_widget_dict['other'] = {'default_position' : inventory_widget_dict['position'][:],
                                      'default_size' : inventory_widget_dict['size'][:]}
    inventory_widget_dict['class'] = Inventory
    inventory_widget_dict['id'] = "widget_inventory_main"
    inventory_widget_dict['color'] = (165, 82, 82)
    widget_dict_scroll['size'] = [game.width*.025, inventory_widget_dict['size'][1]]
    widget_dict_scroll['color'] = (165, 42, 42)
    offset = inventory_widget_dict['size'][0] + inventory_widget_dict['position'][0]
    widget_dict_scroll['position'] = [offset,  inventory_widget_dict['position'][1]]
    widget_dict_scroll['alpha'] = 255
    
    scroll_bar = ScrollBar([0,0], [game.width*.025, game.height*.15], 
                                    color = [x + 20 for x in widget_dict_scroll['color'] ])
    scroll_bar.__setattr__('widget_to_scroll_id', inventory_widget_dict['id'])
    UpButton = ScrollBarUpButton([0,0], [game.width*.025, game.width*.025], (0,0,0), 255)
    DownButton = ScrollBarDownButton([0, widget_dict_scroll['size'][1] - game.width*.025],
                        [game.width*.025, game.width*.025], (0,0,0), 255)
    DownButton.scroll_bar = scroll_bar
    UpButton.scroll_bar = scroll_bar
    widget_dict_scroll['actors'] = [scroll_bar]
    widget_dict_scroll['buttons'] = [UpButton, DownButton]
    
    return [inventory_widget_dict, widget_dict_scroll], {'name' : "Inventory"}