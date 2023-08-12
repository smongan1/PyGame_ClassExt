# -*- coding: utf-8 -*-
"""

PyGame_ClassExt_smongan1 Package

This package provides classes and utilities for implementing game-related functionality using the Pygame library. It includes classes for managing inventories, creating interactive scrollbars, and handling game items.

Classes:
- InventoryItem(Button):
    InventoryItem Class for Representing Items within an Inventory Widget

    This class represents individual items within an inventory widget. Each item has attributes that define its properties, such as its name, type, augments, and more. The class also manages the item's stack size and provides methods to add item stats, manage stacking, and set the item's appearance.

- Inventory(Widget):
    Inventory Class for Managing Inventory Widgets in Games

    This class represents an inventory widget that can be used in games to manage items and organize them by various criteria, such as name or type. The inventory allows adding, sorting, and removing items. It also provides methods to retrieve items by name, type, and manage the layout of the items within the inventory.

- ScrollBar(Actor):
    ScrollBar Class for Creating Interactive Scrollbars

    This class represents a scrollbar widget that can be used in graphical user interfaces to allow users to scroll through content that doesn't fit within the visible area. The scrollbar responds to cursor interactions and adjusts the position of a widget that it's associated with.

Subclasses:
- ScrollBarUpButton(Button): Button class for the up arrow button in the scrollbar.
- ScrollBarDownButton(Button): Button class for the down arrow button in the scrollbar.
- ScrollBarUpButton2(Button): Alternative button class for the up arrow button in the scrollbar.
- ScrollBarDownButton2(Button): Alternative button class for the down arrow button in the scrollbar.

Created on Sat Jan  7 07:19:32 2023

@author: Sean Mongan
"""
from PyGame_ClassExt_smongan1.BaseClasses import *
from copy import copy, deepcopy

class InventoryItem(Button):
    
    """
    InventoryItem Class for Representing Items within an Inventory Widget

    This class represents individual items within an inventory widget. Each item has attributes that define its properties, such as its name, type, augments, and more. The class also manages the item's stack size and provides methods to add item stats, manage stacking, and set the item's appearance.
    
    Attributes:
    - name (str): The name of the item.
    - item_type (str): The type of the item.
    - character_augments (list): Augments that affect characters when using the item.
    - spells_enabled (list): Spells that can be enabled when using the item.
    - useable (bool): Flag indicating whether the item is usable.
    - stack_size_limit (int): The maximum stack size for the item.
    - stack_size (int): The current stack size of the item.
    - surf (pygame.Surface): The surface representing the item's appearance.
    
    Methods:
    - AddItemStats(self, name, item_type, character_augments, spells_enabled, useable,
                   stack_size_limit=1, image_file=None, num_uses=None):
        Set the attributes and appearance of the item.
    - add_to_stack(self, number): Add items to the stack and manage stack overflow.
    
    Usage Example:
    ```python
    # Create an instance of InventoryItem
    item = InventoryItem(position=(0, 0), size=(50, 50), color=(255, 0, 0))
    
    # Add item stats
    item.AddItemStats(name="Health Potion",
                      item_type="Potion",
                      character_augments=["Healing"],
                      spells_enabled=["Heal"],
                      useable=True,
                      stack_size_limit=10,
                      image_file="health_potion.png")
    
    # Add items to the item stack
    overflow = item.add_to_stack(5)

    """
    
    def AddItemStats(self,
                 name,
                 item_type,
                 character_augments,
                 spells_enabled,
                 useable,
                 stack_size_limit = 1,
                 image_file = None,
                 num_uses = None):
        self.name = name
        self.item_type = item_type
        self.character_augments = character_augments
        self.spells_enabled = spells_enabled
        self.useable = useable
        self.stack_size_limit = stack_size_limit
        self.stack_size = 0
        if image_file is None:
            self.surf = pg.Surface([1,1])
            self.surf.fill(self.color)
        else:
            self.surf = load_image(image_file)
    
    def add_to_stack(self, number):
        self.stack_size += number
        over_flow = max(self.stack_size - self.stack_size_limit, 0)
        if over_flow != 0:
            self.stack_size = self.stack_size_limit
        return over_flow
    
class Inventory(Widget):
    """
    Inventory Class for Managing Inventory Widgets in Games
    
    This class represents an inventory widget that can be used in games to manage items and organize them by various criteria, such as name or type. The inventory allows adding, sorting, and removing items. It also provides methods to retrieve items by name, type, and manage the layout of the items within the inventory.
    
    Attributes:
    - item_data (dict): A dictionary storing information about items.
    - item_index (int): An index for tracking items.
    - sort_type (function): A reference to the sorting function currently in use.
    - max_position (float): The maximum position of items within the inventory.
    - default_size (float): The default size of the inventory widget.
    
    Methods:
    - AddItem(self, item_name, number = 1): Add items to the inventory by name and quantity.
    - get_inventory_locs(self): Get the positions of items in the inventory.
    - sort_by_name(self, reverse = False): Sort items in the inventory by name.
    - sort_by_type(self, reverse = False): Sort items in the inventory by type.
    - get_item_by_name(self, name): Get items in the inventory by name.
    - get_item_by_type(self, item_type): Get items in the inventory by type.
    - get_item_type_dictionary(self): Get a dictionary of items categorized by type.
    - resize(self): Resize the inventory based on the items' positions.
    - delete_item(self, item_id): Delete an item from the inventory.
    
    Usage Example:
    ```python
    # Create an instance of Inventory
    inventory = Inventory(position=(100, 100), size=(200, 300))
    
    # Add items to the inventory
    inventory.AddItem("Health Potion", number=5)
    inventory.AddItem("Mana Potion", number=3)
    
    # Sort items by name
    inventory.sort_by_name()
    
    # Get items by name
    health_potions = inventory.get_item_by_name("Health Potion")
    
    # Delete an item from the inventory
    inventory.delete_item("button_item_Health Potion_0")
    """
    
    def AddItem(self, item_name, number = 1):
        self.sort_type = None
        if not hasattr(self, 'item_data'):
            with open('items.dat', 'r') as f:
                 temp_data = f.read()
            self.item_index = 0
            temp_data = temp_data.split('__NEWITEM__')
            for item_info in temp_data:
                item_dict = dict()
                for line in item_info.split('\n'):
                    line = [x.strip() for x in line.split('=')]
                    item_dict[line[0]] = eval(line[1])
                if 'character_augments' not in item_dict:
                    item_dict['character_augments'] = []
                if 'spells_enabled' not in item_dict:
                    item_dict['spells_enabled'] = []
                for keys in item_dict.keys():
                    if key not in { 'name' : None,
                         'item_type': None,
                         'character_augments': None,
                         'spells_enabled': None,
                         'useable': None,
                         'image_file' : None,
                         'num_uses' : None,
                         'stack_size_limit' : None}:
                        if key in possible_character_augments:
                            item_dict['character_augments'].append(item_dict[key])
                        elif key in possible_spells:
                            item_dict['spells_enabled'].append(item_dict[key])
                        del item_dict[key]
                self.item_data[item_dict['name']] = item_dict
                
        if self.item_data[name]['stack_size_limit'] > 1:
            buttons = get_item_by_name(name)
            for button in buttons:
                number = button.add_to_stack(number)
                if number == 0:
                    return None
        if number <= 0: return None
        else:
            inventoryitem = InventoryItem(self.get_new_item_position())
            inventoryitem.id = 'button_item_' + item_name + '_' + str(self.item_index)
            self.max_position = inventoryItem.position[1]
            self.resize()
            self.item_index += 1
            item_dict = self.item_data[item_name]
            self.add_button(inventoryitem)
            AddItem(self, item_name, number - 1)
    
    def get_inventory_locs(self):
        positions = []
        for item_name in self.buttons:
            if item_name.startswith('button_item'):
                positions.append(self.buttons[item_name])
        return positions
    
    def sort_by_name(self, reverse = False):
        item_names = []
        positions = []
        for item_name in self.buttons:
            if item_name.startswith('button_item'):
                item = self.buttons[item_name]
                item_names.append([item.name, item])
                positions.append(item.position[1])
        positions = sorted(positions, reverse = reverse)
        item_names = sorted(item_names, key = lambda x:x[0], reverse = reverse)
        for [item, position] in zip(item_names, positions):
            item[1].position[1] = position
        self.sort_type = self.sort_by_name
        
    def sort_by_type(self, reverse = False):
        types = set()
        positions = []
        for item_name in self.buttons:
            if item_name.startswith('button_item'):
                types = self.buttons[item_name]
        types = sorted(types, reverse = reverse)
        positions = []
        pos_ind = 0
        items_dict = self.get_item_type_dictionary()
        for item_type in types:
            for item in sorted(items_dict[item_type], key = lambda x: x.name):
                item.position = positions[0]
                positions = positions[1:]
        self.sort_type = self.sort_by_type
        
    def get_item_by_name(self, name):
        item_name_buttons = []
        for button_name in self.buttons:
            if button_name.startswith('button_item_' + name):
                item_name_buttons.append(self.buttons[button_name])
        return item_name_buttons
    
    def get_item_by_type(self, item_type):
        item_type_buttons = []
        for button_name in self.buttons:
            if (button_name.startswith('button_item_') 
            and self.buttons[button_name].item_type == item_type):
                item_type_buttons.append(self.buttons[button_name])
        return item_type_buttons
    
    def get_item_type_dictionary(self):
        item_type_buttons_dict = dict()
        for button_name in self.buttons:
            if button_name.startswith('button_item_'):
                item = self.buttons[button_name]
                if not item.item_type in item_type_buttons:
                    item_type_buttons_dict[item.item_type] = []
                item_type_buttons_dict[item.item_type].append(item)
        return item_type_buttons_dict
    
    def resize(self):
        self.size[1] = max(self.default_size, self.max_position)
        
    def delete_item(self, item_id):
        self.max_position = self.max_position - self.buttons[item_id].size[1]
        del self.buttons[item_id]
        if hasattr(self, "self.sort_type") and not self.sort_type is None:
            self.sort_type()

class ScrollBar(Actor):
    """
    ScrollBar Class for Creating Interactive Scrollbars

    This class represents a scrollbar widget that can be used in graphical user interfaces to allow users to scroll through content that doesn't fit within the visible area. The scrollbar responds to cursor interactions and adjusts the position of a widget that it's associated with.
    
    Attributes:
    - prev_cursor_loc (list): The previous cursor location to track cursor movement.
    - scroll_range (numpy.array): The range of valid scroll positions based on widget and scrollbar sizes.
    
    Methods:
    - logic(self): Handle the logic for scrollbar interactions, such as hover, press, and movement.
    - move_actor_and_widget(self, pos_diff): Move both the scrollbar actor and associated widget.
    - move_widget(self): Move the associated widget based on the scrollbar position.
    - move_actor(self, pos_diff): Move the scrollbar actor based on cursor interactions.
    - get_relative_position(self): Get the relative position of the scrollbar within the valid scroll range.
    
    Usage Example:
    ```python
    # Create an instance of ScrollBar
    scroll_bar = ScrollBar(position=(0, 0), size=(20, 200))
    
    # Associate the scrollbar with a widget to be scrolled
    scroll_bar.widget_to_scroll_id = "widget_id"
    
    # Add the scrollbar to a widget
    widget.add_actor(scroll_bar)
    """
    
    def logic(self):
        if not hasattr(self, 'prev_cursor_loc'):
            self.prev_cursor_loc = copy(self.widget.cursor_loc)
            #uses self.widget.size[0] to leave room for up and down buttons
            self.scroll_range = np.array([self.widget.size[0], 
                                          (self.widget.size[1] - 
                                           self.widget.size[0] -
                                           self.size[1])])
        if (self.hover_over or self.is_pressed) and self.game.mouse_pressed[0]:
            if not self.is_pressed:
                if not hasattr(self, 'orig_color'):
                    self.orig_color = self.surf.get_at([0,0])[:3]
                self.surf.fill([x+20 for x in self.orig_color])
            self.is_pressed = True
        else: 
            if self.is_pressed:
                self.surf.fill(self.orig_color)
            self.is_pressed = False
            
        if self.is_pressed:
            pos_diff = self.widget.cursor_loc[1] - self.prev_cursor_loc[1]
            self.move_actor_and_widget(pos_diff)
        self.prev_cursor_loc = copy(self.widget.cursor_loc)
        
    def move_actor_and_widget(self, pos_diff):
        self.move_actor(pos_diff)
        if hasattr(self, 'widget_to_scroll_id'):
            self.move_widget()
        
    def move_widget(self):
        if not hasattr(self, "widget_to_scroll"):
            widget_id = copy(self.widget_to_scroll_id)
            if not widget_id.startswith('widget_'):
                widget_id = 'widget_' + widget_id
            self.widget_to_scroll = self.layer.get_component(widget_id)
            
        total_scroll_dis = self.scroll_range[1] - self.scroll_range[0]
        relative_position =  self.position[1] - self.scroll_range[0]
        proportion_pos = relative_position/total_scroll_dis
        
        def_pos = 0
        if hasattr(self.widget_to_scroll, "default_position"):
            def_pos = self.widget_to_scroll.default_position[1]
        
        widget_padding = 0
        if hasattr(self.widget_to_scroll, "default_size") and not self.widget_to_scroll is None:
            widget_padding = self.widget_to_scroll.default_size[1]
            
        relative_widget_pos = proportion_pos*(self.widget_to_scroll.size[1] - widget_padding)
        self.widget_to_scroll.position[1] = def_pos +  relative_widget_pos
        
    def move_actor(self, pos_diff):
        self.position[1] = max(min((self.position[1] + pos_diff), 
                                   self.scroll_range[1]), 
                               self.scroll_range[0])
    
    def get_relative_position(self):
        if not hasattr(self, 'scroll_range'):
            return 0
        return (self.position[1] - self.scroll_range[0])/(
            self.scroll_range[1] - self.scroll_range[0])
    
class ScrollBarUpButton(Button):
    
    def logic(self):
        if self.is_pressed:
            self.scroll_bar.move_actor_and_widget(-5 * self.game.dt * 60)
        
class ScrollBarDownButton(Button):
    
    def logic(self):
        if self.is_pressed:
            self.scroll_bar.move_actor_and_widget(5 * self.game.dt * 60)
class ScrollBarUpButton2(Button):
    
    def logic(self):
        if self.is_pressed:
            self.scroll_bar.move_actor(-5 * self.game.dt * 60)
        
class ScrollBarDownButton2(Button):
    
    def logic(self):
        if self.is_pressed:
            self.scroll_bar.move_actor(5 * self.game.dt * 60)
            
class GameItem(Actor):
    
    def add_item_to_inventory(self, actor):
        actor.inventory.add_item(self.name, self.amount)
        self.kill()