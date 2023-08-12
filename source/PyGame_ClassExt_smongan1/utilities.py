# -*- coding: utf-8 -*-
"""
PyGame_ClassExt_smongan1 Package Documentation

This package provides a collection of utility functions and classes for various tasks involving Pygame, a popular Python library for creating 2D games and graphical applications.

Functions:
- `center_rects(ref_rect, rect_to_center)`: Calculate the position to center a rectangle within another reference rectangle.
- `split_text_into_lines(text, width, font_size)`: Split a text into lines that fit within a given width based on the font size.
- `load_image(name, data_dir, colorkey=None, scale=1, size=None)`: Load an image from a file with optional scaling and colorkey.
- `load_image_strip(name, data_dir, colorkey=None, scale=1, size=None)`: Load an image strip from a file with optional scaling and colorkey.
- `simple_sheer_arr(img, coordinate, direction=1, pixels=None, scale=None, with_smoothing=None)`: Apply a simple shear transformation to an image along a specified coordinate.
- `is_same_vec(vec1, vec2)`: Compare two vectors element-wise and determine if they are identical.
- `centered_buttons_locs_vert(button_size, num_buttons, screen_dim, num_cols=None, spacing=None, hori_offset=0, vert_offset=0, padding=100)`: Calculate the positions of vertically centered buttons.
- `centered_buttons_locs_hori(button_size, num_buttons, screen_dim, spacing=None, vert_offset=0, hori_offset=0, padding=100)`: Calculate the positions of horizontally centered buttons.
- `make_subset_surf(surf, subset_color, subset_alpha, padding)`: Create a subset surface with a colored background.
- `make_fancy_rect_border(size, padding=0)`: Create a list of coordinates for creating a fancy rectangular border.
- `make_widget_dict(size, position, bkg_color, buttons=None, actors=None, textboxs=None, graphics=None, alpha=255)`: Create a dictionary representing a widget with various attributes.
- `deep_finder(x)`: Recursively search for objects within nested iterables.
- `convert_surfs_to_str(x)`: Convert pygame Surfaces in an object to strings.
- `convert_str_to_surfs(x)`: Convert string representations back to pygame Surfaces.
- `convert_fonts_to_str(x)`: Convert pygame fonts in an object to string representations.
- `convert_str_to_fonts(x)`: Convert string representations of pygame fonts back to pygame fonts.
- `point_in_rect(point, rect)`: Check if a point is within a pygame Rect.
- `point_in_obj(point, obj, greater_than_0_check=True)`: Check if a point is within a custom object.
- `run_updates(obj)`: Run update methods of an object based on predefined attributes.
- `blackwhite(img, sheer_amt=None)`: Convert an image to black and white with optional shearing.
- `make_shadow(surf, sheer_amt=None)`: Create a shadow surface from an image with optional shearing.

Classes:
- `timer`: Timer class for measuring time intervals.

For detailed usage instructions and examples, refer to the individual function and class docstrings.

Created on Wed Jul 13 22:18:44 2022

@author: Sean Mongan
"""
import pygame as pg
import os
import numpy as np
from scipy.ndimage.filters import gaussian_filter

def center_rects(ref_rect, rect_to_center):
    """
    Calculate the position to center a rectangle within another reference rectangle.

    Args:
        ref_rect (pygame.Rect): The reference rectangle.
        rect_to_center (pygame.Rect): The rectangle to be centered.

    Returns:
        list: The x and y coordinates to position the rectangle for centering.

    """
    return [x - y//2 for x,y in zip(ref_rect.center, rect_to_center.size)]

def split_text_into_lines(text, width, font_size):
    """
    Split a text into lines that fit within a given width based on the font size.

    Args:
        text (str): The input text.
        width (int): The maximum width for each line.
        font_size (int): The font size of the text.

    Returns:
        list: A list of lines after splitting the text.

    """
    text = text.replace('\n', ' ').replace('\t', '<><>').split(' ')
    a = 16/10
    linelen = a*width/font_size
    lines = [text[0]]
    line_pos_shift = (16/14)*font_size
    locs = [[0, 0]]
    curr_len = len(lines)
    for word in text[1:]:
        if len(word) + 1 + curr_len > linelen and lines[-1] != '':
            locs.append([0, locs[-1][1] + line_pos_shift])
            lines.append('')
            curr_len = 0
        lines[-1] += ' ' + word
        curr_len += len(word)
    return [x.replace('<><>', '\t') for x in lines], locs

def load_image(name, data_dir, colorkey=None, scale=1, size = None):
    """
    Load an image from a file and optionally apply scaling and colorkey.

    Args:
        name (str): The name of the image file.
        data_dir (str): The directory containing the image file.
        colorkey (tuple, optional): Color to set as transparent. Defaults to None.
        scale (int, optional): Scaling factor for the image. Defaults to 1.
        size (tuple, optional): Target size of the image after scaling. Defaults to None.

    Returns:
        tuple: A tuple containing the loaded image and its bounding rectangle.

    """
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    """
    image_rect = image.get_bounding_rect()
    image_size = image.get_size()
    image = image.subsurface(image_rect)
    """
    if not size is None:
        image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

def load_image_strip(name, data_dir, colorkey=None, scale=1, size = None):
    """
    Load an image strip from a file and optionally apply scaling and colorkey.

    Args:
        name (str): The name of the image file.
        data_dir (str): The directory containing the image file.
        colorkey (tuple, optional): Color to set as transparent. Defaults to None.
        scale (int, optional): Scaling factor for the image. Defaults to 1.
        size (tuple, optional): Target size of the image after scaling. Defaults to None.

    Returns:
        tuple: A tuple containing the loaded image strip and its bounding rectangle.

    """
    fullname = os.path.join(data_dir, name)
    image = pg.image.load(fullname)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)

    image_rect = image.get_bounding_rect()
    image_size = image.get_size()
    image = image.subsurface(image_rect)
    if not size is None:
        image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

def simple_sheer_arr(img, coordinate, direction = 1,
                       pixels = None, scale = None,
                       with_smoothing = None):
    """
    Apply a simple sheer transformation to an image along a specified coordinate.

    Args:
        img (numpy.ndarray): The input image.
        coordinate (int): The coordinate along which to apply the sheer.
        direction (int, optional): The direction of the sheer. Defaults to 1.
        pixels (int, optional): The number of pixels to shear by. Defaults to None.
        scale (float, optional): The scaling factor for sheer. Defaults to None.
        with_smoothing (bool, optional): Apply smoothing after sheer. Defaults to None.

    Returns:
        numpy.ndarray: The sheared image.

    """
    if pixels is None:
        pixels = round(img.shape[coordinate] * scale)
    if scale is None:
        scale = pixels/img.shape[coordinate]
    if scale > 1:
        print("Warning, scale size large enough to cause gaps in simple sheer image")
        print("Please use an interpolation sheer function for better results")
    shape2 = [x for x in img.shape]
    shape2[coordinate] = shape2[coordinate] + pixels
    img2 = np.zeros(shape2)
    sheer_fun = lambda x: (x) * direction*(pixels/(img.shape[1-coordinate]))
    for x in range(img.shape[1-coordinate]):
        sheer = round(sheer_fun(x))
        for y in range(img.shape[coordinate]):
            position = [0,0]
            position[coordinate] = y
            position[1-coordinate] = x
            sheer_position = position[:]
            sheer_position[coordinate] += sheer
            img2[sheer_position[0], sheer_position[1]] = img[position[0],position[1]]
            
    x_pos, y_pos = img2.nonzero()
    if with_smoothing is None and scale > 1:
        with_smoothing = True
    if with_smoothing:
        sig = [0,0]
        sig[coordinate] = .05 * abs(sheer_fun(img.shape[1-coordinate]/4))
        sig[1-coordinate] = .025 * abs(sheer_fun(img.shape[1-coordinate]/4))
        img2 = gaussian_filter(img2, sigma = sig)
        img2 = 1 * (img2 > np.mean(img2))
    return img2[min(x_pos) : max(x_pos), min(y_pos) : max(y_pos)]

def is_same_vec(vec1, vec2):
    """
    Compare two vectors element-wise and determine if they are identical.

    Args:
        vec1 (list): The first vector.
        vec2 (list): The second vector.

    Returns:
        bool: True if the vectors are identical, False otherwise.
    """
    ii = 0
    while (ii < len(vec1)) and (vec1[ii] == vec2[ii]):
        ii += 1
        
    return ii >= len(vec1)

class timer():
    """
    Timer class for measuring time intervals.

    This class provides functionality for measuring time intervals, such as start, stop, and reset operations.

    Attributes:
        time (function): A reference to the time function for time measurement.
        clk (float): Accumulated time interval.
        start_time (float): The time when the timer was started.

    Methods:
        restart(self): Reset and start the timer.
        start(self): Start or resume the timer.
        stop(self): Stop the timer and accumulate the time interval.
        getTime(self): Get the elapsed time since starting the timer.
        reset(self): Reset the accumulated time interval to zero.
    """
    def __init__(self):
        from time import time
        self.time = time
    def restart(self):
        self.clk = 0
        self.start()
    def start(self):
        try: self.clk
        except: self.clk = 0
        self.start_time = self.time()
    def stop(self):
        self.clk += self.time() - self.start_time
    def getTime(self):
        return self.time() - self.start_time
    def reset(self):
        self.clk = 0

def centered_buttons_locs_vert(button_size, 
                              num_buttons, 
                               screen_dim, 
                               num_cols = None, 
                               spacing = None,
                               hori_offset = 0,
                               vert_offset = 0,
                               padding = 100):
    """
    Calculate the positions of vertically centered buttons.

    Args:
        button_size (tuple): The size of each button (width, height).
        num_buttons (int): The number of buttons.
        screen_dim (tuple): The dimensions of the screen (width, height).
        num_cols (int, optional): The number of columns. Defaults to None.
        spacing (int, optional): Spacing between buttons. Defaults to None.
        hori_offset (int, optional): Horizontal offset. Defaults to 0.
        vert_offset (int, optional): Vertical offset. Defaults to 0.
        padding (int, optional): Padding around the buttons. Defaults to 100.

    Returns:
        list: A list of button positions (x, y).
    """
    
    if num_cols is None:
        if spacing is None: temp_space = 20
        else: temp_space = spacing
        num_cols = int(np.ceil((button_size[1] + temp_space)*num_buttons/screen_dim[1]))
    if num_cols == 1:
        if spacing is None:
            spacing = (screen_dim[1] - button_size[1]*num_buttons -
                       2*padding - vert_offset)//num_buttons
        button_vert = lambda x: (x*(button_size[1] + spacing) + button_size[1]//2 +
                                 vert_offset - button_size[1]*num_buttons)
        return [[(screen_dim[0] - button_size[0])//2, button_vert(x) + screen_dim[0]//2] for x in range(num_buttons)]
    button_locs = []
    num_rows = np.ceil(num_buttons/num_cols)
    rem_buttons = num_buttons
    i = 0
    while rem_buttons > 0:
        v_offset = i*(screen_dim[1]//num_rows) - button_size[1]//2 + screen_dim[1]//2
        button_locs.extend(centered_buttons_locs_hori(button_size, 
                                                     num_cols, 
                                                     screen_dim,
                                                     hori_offset = hori_offset,
                                                     vert_offset = v_offset))
        rem_buttons -= num_cols
        i+=1
    return button_locs

def centered_buttons_locs_hori(button_size, 
                               num_buttons,
                               screen_dim, 
                               spacing = None,
                               vert_offset = 0,
                               hori_offset = 0,
                               padding = 100):
    """
    Calculate the positions of horizontally centered buttons.

    Args:
        button_size (tuple): The size of each button (width, height).
        num_buttons (int): The number of buttons.
        screen_dim (tuple): The dimensions of the screen (width, height).
        spacing (int, optional): Spacing between buttons. Defaults to None.
        vert_offset (int, optional): Vertical offset. Defaults to 0.
        hori_offset (int, optional): Horizontal offset. Defaults to 0.
        padding (int, optional): Padding around the buttons. Defaults to 100.

    Returns:
        list: A list of button positions (x, y).
    """

    if spacing is None:
        spacing = np.ceil((screen_dim[0] - button_size[0]*num_buttons -
                       2*padding - hori_offset)/num_buttons)
    button_locs = []
    start_loc = (screen_dim[0] - button_size[0]*num_buttons - spacing*(num_buttons - 1))//2
    for i in range(num_buttons):
        button_locs.append([hori_offset + start_loc + i*(button_size[0] + spacing), 
                            vert_offset + (screen_dim[1] - button_size[1])//2])
    return button_locs

def make_subset_surf(surf, subset_color, subset_alpha, padding):
    
    """
    Create a subset surface with a colored background.

    Args:
        surf (pygame.Surface): The input surface.
        subset_color (tuple): The color of the subset background (R, G, B).
        subset_alpha (int): The alpha value of the subset background.
        padding (int): Padding around the subset surface.

    Returns:
        pygame.Surface: The subset surface with the specified background.
    """
    
    sub_surf = pg.Surface([x-padding for x in surf.get_rect().size])
    sub_surf.fill(subset_color)
    sub_surf.set_alpha(subset_alpha)
    temp = surf.copy()
    temp.blit(sub_surf, [padding//2, padding//2])
    return temp

def make_fancy_rect_border(size, padding = 0):
    
    """
    Create a list of coordinates for creating a fancy rectangular border.

    Args:
        size (tuple): The size of the rectangle (width, height).
        padding (int, optional): Padding around the rectangle. Defaults to 0.

    Returns:
        list: A list of coordinates representing the border points.
    """
    
    size = [x - 2*padding for x in size]
    offset = min(size)//2
    return [[x + padding for x in y] for y in [[offset, 0], 
            [size[0] - offset, 0],
            [size[0], offset],
            [size[0], size[1] - offset],
            [size[0] - offset, size[1]],
            [offset, size[1]],
            [0, size[1] - offset],
            [0, offset]]]

def make_widget_dict(size, position, bkg_color, buttons = None, 
                     actors = None, textboxs = None, 
                     graphics = None, alpha = 255):
    
    """
    Create a dictionary representing a widget with various attributes.

    Args:
        size (tuple): The size of the widget (width, height).
        position (tuple): The position of the widget (x, y).
        bkg_color (tuple): The background color of the widget (R, G, B).
        buttons (list, optional): List of buttons. Defaults to None.
        actors (list, optional): List of actors. Defaults to None.
        textboxs (list, optional): List of textboxes. Defaults to None.
        graphics (list, optional): List of graphics. Defaults to None.
        alpha (int, optional): The alpha value of the widget. Defaults to 255.

    Returns:
        dict: A dictionary representing the widget's attributes.
    """
    
    wid_dict = dict()
    wid_dict["size"] = size
    wid_dict["position"] = position
    wid_dict["color"] = bkg_color
    wid_dict["alpha"] = alpha
    if not buttons is None: wid_dict["buttons"] = buttons
    if not actors is None: wid_dict["actors"] = actors
    if not textboxs is None: wid_dict["textboxs"] = textboxs
    if not graphics is None: wid_dict["graphics"] = graphics
    return wid_dict

def deep_finder(x):
    """
    Recursively search for objects within nested iterables.

    Args:
        x: The input object or iterable.

    Returns:
        list: A list containing all objects found within the input object.
    """
    
    objs = []
    if '__iter__' in dir(x):
        for key in x:
            try: objs.extend(deep_finder(x[key]))
            except: objs.extend(deep_finder(key))
    else:
        objs = [x]
    return objs

def convert_surfs_to_str(x):
    
    """
    Convert pygame Surfaces in an object to strings.

    Args:
        x: The input object.

    Modifies:
        x: Modifies the input object by converting pygame Surfaces to string representation.
    """
    
    for attr_name in dir(x):
        if isinstance(x.__getattribute__(attr_name), pg.Surface):
            surf = x.__getattribute__(attr_name)
            x.__setattr__(attr_name, ['is_surf', 
                              pg.image.tostring(surf, "RGBA"),
                              surf.get_size()])
             
def convert_str_to_surfs(x):
    """
   Convert string representations back to pygame Surfaces.

   Args:
       x: The input object with string representations of pygame Surfaces.

   Modifies:
       x: Modifies the input object by converting string representations to pygame Surfaces.
   """
    for attr_name in dir(x):
        if isinstance(x.__getattribute__(attr_name), list):
            attr = x.__getattribute__(attr_name)
            if 'is_surf' in attr[:1]:
                surf = pg.image.fromstring(attr[1], attr[2], 'RGBA')
                x.__setattr__(attr_name, surf)

def convert_fonts_to_str(x):
    
    """
    Convert pygame fonts in an object to string representations.

    Args:
        x: The input object.

    Modifies:
        x: Modifies the input object by converting pygame fonts to string representation.
    """
    
    if hasattr(x, 'font'):
        x.__setattr__('font', 'is_font')
            
def convert_str_to_fonts(x):
    
    """
    Convert string representations of pygame fonts back to pygame fonts.

    Args:
        x: The input object with string representations of pygame fonts.

    Modifies:
        x: Modifies the input object by converting string representations to pygame fonts.
    """
    
    if hasattr(x, 'font'):
        x.font = pg.font.SysFont(x.font_details[0], x.font_details[1])

def point_in_rect(point, rect):
    """
    Check if a point is within a pygame Rect.

    Args:
        point (tuple): The coordinates of the point (x, y).
        rect (pygame.Rect): The pygame Rect.

    Returns:
        bool: True if the point is inside the rect, False otherwise.
    """
    return ((point[0] - rect.left) >= 0 and
                    (point[0] - rect.right) <= 0 and
                    (point[1] - rect.bottom) <= 0 and
                    (point[1] - rect.top) >= 0)

def point_in_obj(point, obj, greater_than_0_check = True):
    """
    Check if a point is within a custom object.

    Args:
        point (tuple): The coordinates of the point (x, y).
        obj: The custom object to check.
        greater_than_0_check (bool, optional): Perform additional check for point coordinates greater than 0. Defaults to True.

    Returns:
        bool: True if the point is inside the object, False otherwise.
    """
    if greater_than_0_check and any(x < 0 for x in point):
        return False
    left = obj.position[0]
    right = obj.position[0] + obj.size[0]
    top = obj.position[1]
    bottom = obj.position[1] + obj.size[1]
    return ((point[0] - left) >= 0 and
                    (point[0] - right) <= 0 and
                    (point[1] - bottom) <= 0 and
                    (point[1] - top) >= 0)

def run_updates(obj):
    """
    Run update methods of an object based on predefined attributes.

    Args:
        obj: The object to update.

    Modifies:
        obj: Modifies the object by running update methods.
    """
    obj.__setattr__('to_update_attrs', {x : None for x in dir(obj) 
                           if x in obj.to_update_attrs or 
                           x.startswith('update_')})
    for update_attr in obj.to_update_attrs:
        obj.__getattribute__(update_attr)()

def blackwhite(img, sheer_amt = None):
    
    """
    Convert an image to black and white with optional shearing.

    Args:
        img (pygame.Surface): The input image.
        sheer_amt (list, optional): Shearing amounts for each coordinate. Defaults to None.

    Returns:
        pygame.Surface: The black and white image.
    """
    
    if not sheer_amt is None:
        arr = pg.surfarray.pixels2d(img)
        for coordinate, sheer in enumerate(sheer_amt):
            if sheer == 0: continue
            arr = simple_sheer_arr(arr, coordinate, 
                                   direction = sheer/abs(sheer),
                                   scale = abs(sheer))
    mask = pg.mask.from_surface(img)
    mask.invert()
    return mask.to_surface()

def make_shadow(surf, sheer_amt = None):
    
    """
    Create a shadow surface from an image with optional shearing.

    Args:
        surf (pygame.Surface): The input image.
        sheer_amt (list, optional): Shearing amounts for each coordinate. Defaults to None.

    Returns:
        pygame.Surface: The shadow surface.
    """
    
    bw = blackwhite(surf, sheer_amt)
    bw.set_colorkey((255,255,255))
    bw.set_alpha(150)
    return bw