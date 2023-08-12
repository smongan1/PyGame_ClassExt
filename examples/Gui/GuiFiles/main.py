import os
import pygame as pg
pg.init()
pg.font.init()
import numpy as np
np.float = np.float64
from PyGame_ClassExt_smongan1.utilities import *
from PyGame_ClassExt_smongan1.BaseClasses import *
from PyGame_ClassExt_smongan1.AnimationClasses import *
from PyGame_ClassExt_smongan1.RPGElements import *

from threading import Thread
import time
import subprocess
from copy import copy, deepcopy
from glob import glob
import pyautogui
from ctypes import windll

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
max_speed = 1000
ind_to_letter = { 4+i : x for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}
letter_to_ind = { x : 4+i for i,x in enumerate('abcdefghijklmnopqrstuvwxyz')}

def standard_button_colors():
    return (50, 50, 255), (180, 240, 200), (100, 255, 140)

class symbol_getter():
    seen_ext_dict = {}
    
    @staticmethod
    def get_symbol(file, size):
        path = None
        if os.path.isdir(file):
            path = os.path.join('Assets', 'folder.png')
        ext = file.split('.')[-1]
        if ext in symbol_getter.seen_ext_dict:
            return symbol_getter.seen_ext_dict[ext].copy()
        if not ext and not path:
            path = os.path.join('Assets', 'document.png')
        elif not path:
            path = path = os.path.join('Assets', 'document.png')
        sym, sym_rect = load_image(path, data_path, size = size, colorkey = -1)
        sym_surf = pg.Surface(size)
        sym_surf.fill((5,7,11))
        sym_surf.blit(sym, [0,0])
        symbol_getter.seen_ext_dict[ext] = sym_surf.copy()
        return sym_surf

def create_add_to_case_button(button):
    case_button_id = 'button_case_add_button'
    if case_button_id in button.widget.buttons:
        case_button = button.widget.buttons[case_button_id]
        case_button.position[1] = button.position[1]
        case_button.ref_button = button
        return
    sze = button.size
    button_size = [sze[1] + 4, sze[1]]
    button_color = [100, 100, 200]
    button_hover_color = [100, 150, 150]
    button_pressed_color = [150, 200, 200]
    button_alpha = 255
    loc = [x for x in button.position]
    loc[0] += sze[0]
    case_button = AddToCase(loc, button_size, button_color, 
                          button_alpha, text = 'ADD',
                          font = ['Arial', 16, (0, 0, 0)],
                          hover_over_color = button_hover_color,
                          pressed_color = button_pressed_color)
    case_button.text_offset = 4
    case_button.id = case_button_id
    case_button.ref_button = button
    button.widget.add_button(case_button)

def create_file_button(file, loc, wid_file):
    browse_tb = wid_file.layer.get_component('textbox_dir_browse')
    button_size = [wid_file.size[0] - 100, 40]
    button_color = [255, 255, 255]
    button_hover_color = [200, 200, 200]
    button_pressed_color = [150, 150, 150]
    button_alpha = 255
    fname = os.path.split(file)[-1]
    button = FolderButton(loc, button_size, button_color, 
                          button_alpha, text = fname[:100],
                          font = ['Arial', 20, (0, 0, 0)],
                          hover_over_color = button_hover_color,
                          pressed_color = button_pressed_color)
    button.text_offset = 10
    button.browse_tb = browse_tb
    button.file = file
    button.last_pressed = 0
    g = Graphic([30,30], [loc[0] - 35, loc[1] + 4])
    g.surf.set_colorkey((5,7,11))
    symbol = symbol_getter.get_symbol(file, [30,30])
    g.add_surf(symbol, [0,0])
    wid_file.add_graphic(g)
    wid_file.add_button(button)
    
def create_file_button2(file, loc, wid_case):
    button_size = [wid_case.size[0], 30]
    button_color = [255, 255, 255]
    button_hover_color = [200, 200, 200]
    button_pressed_color = [150, 150, 150]
    button_alpha = 255
    fname = os.path.split(file)[-1]
    button = FolderButton2(loc, button_size, button_color, 
                          button_alpha, text = fname[:100],
                          font = ['Arial', 14, (0, 0, 0)],
                          hover_over_color = button_hover_color,
                          pressed_color = button_pressed_color)
    button.text_offset = 10
    button.file = file
    button.last_pressed = 0
    g = Graphic([30,30], [loc[0] - 35, loc[1]])
    g.surf.set_colorkey((5,7,11))
    symbol = symbol_getter.get_symbol(file, [30,30])
    g.add_surf(symbol, [0,0])
    wid_case.add_graphic(g)
    wid_case.add_button(button)

def create_results_button(result, loc, wid_case, text_in):
    button_size = [wid_case.size[0], 30]
    button_color = [255, 255, 255]
    button_hover_color = [200, 200, 200]
    button_pressed_color = [150, 150, 150]
    button_alpha = 255
    text = result.get_displayable_text()
    doc = result.document
    doc_name = '>      ' + os.path.split(doc.name)[-1][:50]
    score = round(doc.score3(text_in)*100)
    button = ResultsButton('layer_document_viewer', [0, loc], button_size, 
                           button_color, 
                          button_alpha, text = doc_name,
                          font = ['Arial', 18, (0, 0, 0)],
                          hover_over_color = button_hover_color,
                          pressed_color = button_pressed_color,
                          justification = 'Left')
    button.result = result
    button.last_pressed = 0
    wid_case.add_button(button)
    button_color2 = (150,150,255)
    button = Button([0, loc], [30,30], button_color2, 
                          button_alpha, text = str(score),
                          font = ['Arial', 18, (0, 0, 0)],
                          hover_over_color = button_color2,
                          pressed_color = button_color2,
                          justification = 'Left')
    
    button_size = [wid_case.size[0], 30]
    wid_case.add_button(button)
    button = DocumentButton([0, loc+30], button_size, button_color, 
                          button_alpha, text = text,
                          font = ['Arial', 18, (0, 0, 0)],
                          hover_over_color = button_color,
                          pressed_color = button_color,
                          justification = 'Left')
    wid_case.add_button(button)
    button.last_text = ''
    button.resize()
    outloc = loc + button.size[1] + 40
    page_number = 'pg ' + str(result.page_number)
    if not result.is_estimate_page_count:
        page_number = 'pg ' +'(' + str(result.page_number) + ')'
        
    button = SquareButton([wid_case.size[0] - 80, loc], [80, 30], button_color, 
                          button_alpha, text = page_number,
                          font = ['Arial', 14, (0, 0, 0)],
                          hover_over_color = button_color,
                          pressed_color = button_color,
                          justification = 'Left')
    wid_case.add_button(button)
    return outloc
    
def get_mongoose_graphic():
    graphic = Graphic([300, 120], [250, 100])
    graphic.surf.set_colorkey((5, 7, 11))
    font = pg.font.SysFont('Arial', 60).render(
        'Mongoose', True, (0,0,0))
    graphic.add_surf(font, [20,20])
    return graphic

def import_documents():
    with open(os.path.join(data_path, 'BaseClasses_pages.py')) as f:
        base_classes = f.read()
    exec(base_classes, globals())
    
def get_all_deep_files(files):
    if not isinstance(files, str):
        return [file for file_dir in files for file 
                in get_all_deep_files(file_dir) 
                if file.split('.')[-1] in ['txt', 'pdf']]
    if not os.path.isdir(files):
        return [files]
    glob_path = os.path.join(files, '**')
    return get_all_deep_files(glob(glob_path))

class LoadThread(Thread):
    def run(self):
        print("importing documents")
        print(os.getcwd())
        import_documents()
        print("building case")
        if self.files:
            self.files = get_all_deep_files(self.files)
            self.value = Case(self.files)
        
class SquareButton(Button):
    
    def init_draw(self):
        self.surf = pg.Surface(self.size)
        self.surf.fill(self.color)
        self.hover_over_surf = self.surf.copy()
        if all(x>8 for x in self.size):
            highlight_surf = pg.Surface(self.size - 8)
            highlight_surf.fill(self.hover_over_color)
            self.hover_over_surf.blit(highlight_surf, [4,4])
        self.pressed_surf = self.hover_over_surf.copy()
        if all(x>24 for x in self.size):
            sze = np.array([min(x,0) for x in self.size - 24])
            pressed_surf = pg.Surface(sze)
            pressed_surf.fill(self.pressed_color)
            self.pressed_surf.blit(pressed_surf, [12,12])
        self.to_draw_surf = self.surf.copy()
        self.draw()
        
class SquareChangeLayer(ChangeLayerButton, SquareButton):
    def __NNNNNNN__(self):
        None
    
class SizeChanger(Widget):

    
    def update_scroll(self):
        if isinstance(self.scroll_bar, str):
            self.scroll_bar = self.layer.get_component(self.scroll_bar)
            self.prev_pos = self.scroll_bar.get_relative_position()
        if not hasattr(self.scroll_bar, 'scroll_range'):
            return
        pos = self.scroll_bar.get_relative_position()
        if self.prev_pos == pos: return
        self.prev_pos = pos
        self.scroll_pos[1] = pos*(self.orig_size[1] - self.size[1])
    
    def update(self):
        if not self.initialized:
            self.initial()
        """ Render the screen. """
        #self.screen.fill((255, 255, 255))
        if self.to_update:
            self.blit_offset = np.zeros(2)
            self.get_cursor_loc()
            self.logic()
            self.surf.fill((255,255,255))
            run_updates(self)
            
    def draw(self):
        if not hasattr(self, 'orig_surf'):
            self.orig_surf = pg.Surface(self.orig_size)
            self.scroll_pos = np.array([0,0])
        if not self.initialized:
            self.initial()
        for obj_type in ['actors', 'graphics', 'buttons', 'textboxs']:
            for obj in self.__getattribute__(obj_type).values():
                obj.draw()
        if self.to_draw:
            self.orig_surf.fill((255,255,255))
            self.orig_surf.blit(self.surf, self.scroll_pos)
            self.game.screen.blit(self.orig_surf, self.position + self.blit_offset)
    
    def get_cursor_loc(self):
        offset = 0
        if hasattr(self, 'scroll_pos'):
            offset = -self.scroll_pos 
        self.cursor_loc = offset + self.game.cursor_loc - self.position
        self.hover_over = all(x > 0 and x < self.orig_size[i] for i, x 
                   in enumerate(self.cursor_loc - offset))
        
    def resize(self, max_size):
        self.size[1] = max([x for x in [max_size, self.orig_size[1]]])
        self.surf = pg.Surface(self.size)
        self.surf.fill((255,255,255))
        if not isinstance(self.scroll_bar, str):
            self.scroll_bar.move_actor(-8000)

class DocumentButton(SquareButton):
    
    def resize(self):
        self.size = np.array([self.size[0], self.surf_font.get_size()[1]])
        self.init_draw()

class DocumentPath(SquareButton):
    def run_pressed(self):
        path = os.path.realpath(self.text)
        folder = os.path.dirname(path)
        
        subprocess.Popen(f'start "{path}"', shell=True)
        #wbopen(path)
        
class DocumentShower(Actor):
    def logic(self):
        if not self.widget.new_results: return
        self.widget.new_results = False
        self.document_button.render_font()
        self.document_button.resize()
        self.widget.resize(self.document_button.size[1])
        
class LeftSideText(SquareButton):

    def draw(self):
        if self.to_draw:
            if not self.text is None:
                font_surf = self.font.render(self.text, True,
                                             self.font_details[2], None)
                font_surf.set_alpha(self.alpha)
                font_size = np.array(font_surf.get_size())
                font_button_size_diff = (self.size - font_size)//2
                if hasattr(self, 'text_offset'):
                    font_button_size_diff[0] = self.text_offset
                self.to_draw_surf.blit(font_surf, font_button_size_diff)
            if self.widget:
                self.widget.surf.blit(self.to_draw_surf, self.position + self.blit_offset)

class search_button(ChangeLayerButton, SquareButton):
    def run_pressed(self):
        if not hasattr(self, 'results_wid'):
            wid = self.game.get_component('widget_case_results')
            self.results_wid = wid
            self.search_bars = [self.layer.get_component(x)
                               for x in ['textbox_search_bar',
                                         'textbox_search_bar2']]
            self.search_bars2 = [self.game.get_component(x)
                               for x in ['textbox_search_bar',
                                         'textbox_search_bar2']]
        self.results_wid.new_results = True
        for x in self.search_bars:
            if x: text = x.text
        for x in self.search_bars2:
            if x:  x.text = text
        self.results_wid.results2 = self.game.case.search(text)
        self.results_wid.results = self.results_wid.results2['sentences']
        self.game.change_layer(self.results_wid.layer.id)
        
class LoadingScreen(Widget):
    def logic(self):
        if self.load_bar_orig is None:
            for graphic in self.graphics:
                if 'load_bar' in graphic:
                    self.load_bar_orig = self.graphics[graphic].surf.copy()
                    self.load_bar = self.graphics[graphic]
                    self.rot_cnt = 0
        temp = pg.transform.rotate(self.load_bar_orig, -10*self.rot_cnt)
        size1 = np.array(temp.get_size())
        size2 = np.array(self.load_bar.surf.get_size())
        self.load_bar.surf.fill((255,255,255))
        self.load_bar.surf.blit(temp, (size2 - size1)/2)
        self.rot_cnt += 1
        if self.thread.is_alive(): return
        print('joining')
        self.thread.join()
        self.game.case = self.thread.value
        self.game.change_layer(self.next_layer)
        self.load_bar.surf = self.load_bar_orig.copy()
        
    def update_init(self):
        if self.first_screen:
           
            self.thread = thread
            self.next_layer = 'Main_menu2'
            self.first_screen = False
        
class BuildCase(ChangeLayerButton):
    
    def run_pressed(self):
        loading_screen = self.game.get_component('Main_menu')
        loading_wid = [x for x in loading_screen.widgets.values()][0]
        thread = LoadThread()
        thread.value = None
        thread.files = self.layer.get_component('widget_case_files').case_files
        print("thread starting")
        thread.start()
        loading_wid.thread = thread
        loading_wid.next_layer = 'search_menu'
        self.game.change_layer('Main_menu')
        
class FileShower(Actor):
    
    def logic(self):
        wid_file = self.widget
        if self.prev_file == wid_file.file_loc: return
        self.prev_file = wid_file.file_loc
        tags = [x for x in wid_file.buttons.values()]
        tags += [x for x in wid_file.graphics.values()]
        for x in tags: x.__del__()
        files = glob(os.path.join(wid_file.file_loc,'**'))
        if not files: return
        button_size = [wid_file.size[0], 40]
        locs = centered_buttons_locs_vert(button_size, len(files), 
                           [wid_file.size[0], 0],
                           spacing = 5,
                           num_cols = 1)
        min_x = min([x[1] for x in locs])
        locs = [[x[0] + 40, x[1] - min_x] for x in locs]
        wid_file.resize(max([x[1] for x in locs]))
        for file, loc in zip(files, locs):
            button = create_file_button(file, loc, wid_file)
            
class FileShower2(Actor):
    
    def logic(self):
        if not self.widget.files_changed: return
        self.widget.files_changed = False
        button_keys = [key for key in self.widget.buttons]
        temp = set(self.widget.case_files)
        if temp == self.prev_files: return
        self.prev_files = temp
        tags = [x for x in self.widget.buttons.values()]
        tags += [x for x in self.widget.graphics.values()]
        for x in tags: x.__del__()
        if not self.widget.case_files: return
        button_size = [100, 25]
        locs = centered_buttons_locs_vert(button_size, len(self.widget.case_files), 
                           [self.widget.size[0], 0],
                           spacing = 5,
                           num_cols = 1)
        min_x = min([x[1] for x in locs])
        locs = [[x[0] + 20, x[1] - min_x +4] for x in locs]
        self.widget.resize(max([x[1] for x in locs])+25)
        for file, loc in zip(self.widget.case_files, locs):
            button = create_file_button2(file, loc, self.widget)
            
class ResultsShower(Actor):
    
    def logic(self):
        if not self.widget.new_results: return
        self.widget.new_results = False
        tags = [x for x in self.widget.buttons.values()]
        for x in tags: x.__del__()
        if not self.widget.results: return
        search_bar = self.game.get_component('textbox_search_bar')
        txt = search_bar.text
        loc = 10
        for result in self.widget.results:
            loc = create_results_button(result, loc, self.widget, txt)
        self.widget.resize(loc)    
        
class ResultsButton(ChangeLayerButton, SquareButton):
    
    def run_pressed(self):
        path = self.result.document.file
        try:
            windll.user32.BlockInput(True)
            a = subprocess.run(f'explorer "{path}"', 
                           shell=True, 
                           stderr = subprocess.PIPE)
            print(a)
            time.sleep(.5)
            with pyautogui.hold('ctrl'):
                with pyautogui.hold('alt'):
                    pyautogui.press('g')
            time.sleep(0.5)
            pyautogui.typewrite(str(self.result.page_number))
            time.sleep(0.5)
            pyautogui.press('enter')
        except:
            None
        finally:
            windll.user32.BlockInput(False)
            
class AddToCase(LeftSideText):
    
    def run_pressed(self):
        
        ref_button = self.ref_button
        wid = self.layer.get_component('widget_case_files')
        wid.case_files.append(ref_button.file)
        wid.case_files = sorted(set(wid.case_files))
        wid.files_changed = True
        
class FolderButton(LeftSideText):
    
    def run_pressed(self):
        if self.double_click():
            if os.path.isdir(self.file):
                self.widget.file_loc = self.file
                self.browse_tb.text = self.file
        
        create_add_to_case_button(self)
            
    def double_click(self):
        out = False
        now = time.time()
        pressed_timer = now - self.last_pressed
        if pressed_timer < 0.5:
            out = True
        self.last_pressed = now
        return out
    
    
class RemoveCase(SquareButton):
    def run_pressed(self):
        wid = self.layer.get_component('widget_case_files')
        b_keys = [x for x in wid.buttons]
        for button_key in b_keys:
            button = wid.buttons[button_key]
            if button.is_selected:
                wid.case_files.remove(button.file)
                button.__del__()
                if not wid.files_changed:
                    wid.files_changed = True

class SearchBar(Textbox):
    
    def on_enter(self):
        self.search_button.run_pressed()

class FolderButton2(LeftSideText):
    
    def run_pressed(self):
        self.is_selected = not self.is_selected
    
    def update_selected(self):
        if self.is_selected:
            self.to_draw_surf = self.hover_over_surf.copy()
            
class UpOneDir(SquareButton):
    
    def run_pressed(self):
        if isinstance(self.wid_f, str):
            self.wid_f = self.layer.get_component(self.wid_f)
            self.browse_tb = self.layer.get_component(self.browse_tb)
        path = self.wid_f.file_loc
        path = os.path.split(path)
        path = os.path.join(*path[:-1])
        self.wid_f.file_loc = path
        self.browse_tb.text = path
        
class ChangeDir(Textbox):

    def on_enter(self):
        if os.path.isdir(self.text):
            self.wid_f.file_loc = self.text
            self.invalid_path = False
        else:
            self.invalid_path = True
            
    def update_invalid_path(self):
        if isinstance(self.wid_f, str):
            self.wid_f = self.layer.get_component(self.wid_f)
        if self.text == self.wid_f.file_loc:
            self.invalid_path = False
        g_id =  'graphic_invalid_path'
        if self.invalid_path:
            if g_id in self.widget.graphics: return
            g = Graphic(self.size, 
                        self.position + np.array([0, -self.size[1]]))
            font = pg.font.SysFont('Arial', 20).render(
        'Invalid Path', True, (150,0,0))
            g.surf.fill((255,255,255))
            g.add_surf(font, [0,0])
            g.id = g_id
            self.widget.add_graphic(g)
        elif g_id in self.widget.graphics:
            g = self.widget.graphics[g_id]
            g.__del__()
 


def setup_search_results(gui): 
    position = [100, 180]
    size = [570, 600]
    color = (255,255,255)
    actors = [ResultsShower([0,0], [0,0])]
    results_widget = make_widget_dict(size, position, color, 
                                  actors = actors)
    results_widget['id'] = 'widget_case_results'
    results_widget['other'] = {'new_results' : True,
                               'results' : [],
                               'scroll_bar' : 'actor_results_scroll_bar',
                               'orig_size' : size}
    
    results_widget['class'] = SizeChanger
    
    position = [size[0] + position[0] + 10, position[1]]
    size = [20, size[1]]
    scroll_bar = ScrollBar([0,20], [20,40])
    scroll_bar.id = 'actor_results_scroll_bar'
    results_scroll = make_widget_dict(size, 
                                      position, 
                                      (100,100,100), 
                                      actors = [scroll_bar])
    position = [0, 0]
    size = [800, 800]
    color = (255,255,255)
    graphic = get_mongoose_graphic()
    graphic.position[1] = graphic.position[1] - 75
    button_colors = standard_button_colors()
    button_alpha = 255
    button_size = [120, 35]
    buttons = []
    buttons.append(
        search_button("search_results", [580, 140], button_size, button_colors[0], 
                    button_alpha, "Search", font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = button_colors[1],
                    pressed_color = button_colors[2])
        )
    buttons[-1].id = 'button_search_results'
    return_to_build_case = SquareChangeLayer(
        "Main_menu2", [25, 25], button_size, button_colors[0], 
                    button_alpha, "Rebuild Case", font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = button_colors[1],
                    pressed_color = button_colors[2])
    buttons.append(return_to_build_case)
    textboxes = [
        SearchBar([100, 140], length = 470,
                 box_color = (200,200,200),
                 font = ["Arial", 20, (0,0,0)],
                 default_text = "Enter Search Terms")]
    textboxes[-1].id = 'textbox_search_bar'
    textboxes[-1].search_button = buttons[-2]
    search_widget = make_widget_dict(size, position, color, 
                                  buttons = buttons,
                                  graphics = [graphic],
                                  textboxs = textboxes)
    
    return [search_widget, results_widget, results_scroll], {"name" : "search_results"}

def setup_document_menu(gui):
    
    graphic = get_mongoose_graphic()
    graphic.position[1] = graphic.position[1] - 75
    position = [0, 0]
    size = [800, 800]
    color = (255,255,255)
    button_colors = standard_button_colors()
    return_to_search = SquareChangeLayer(
        "search_results", [25, 25], [120,35], button_colors[0], 
                    255, "Return to Search", font = ['Arial', 12, (0, 0, 0)],
                    hover_over_color = button_colors[1],
                    pressed_color = button_colors[2])
    
    document_path = DocumentPath([100, 140], [600, 35], (255,255,255), 
                    255, " ", font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = (200,200,200),
                    pressed_color = (150,150,150))
    document_path.id = 'button_document_path'
    title_widget = make_widget_dict(size, position, color,
                                  graphics = [graphic],
                                  buttons = [return_to_search,document_path])
    
    position = [25, 180]
    size = [720, 600]
    button_colors = standard_button_colors()
    button_alpha = 255
    button_size = [720, 100]
    buttons = []
    buttons.append(
        DocumentButton([0, 0], button_size, (255,255,255), 
                    button_alpha, "Search "*1000, 
                    font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = (255,255,255),
                    pressed_color = (255,255,255),
                    justification = 'Left')
        )
    actors = [DocumentShower([0,0],[0,0])]
    actors[-1].document_button = buttons[-1]
    actors[-1].id = 'actor_document_shower'
    actors[-1].document_path = document_path
    document_widget = make_widget_dict(size, position, color,
                                       buttons = buttons,
                                       actors = actors)
    document_widget['class'] = SizeChanger
    document_widget['other'] = {'new_results' : True,
                               'results' : [],
                               'scroll_bar' : 'actor_results_scroll_bar',
                               'orig_size' : size}
    position = [size[0] + position[0] + 10, position[1]]
    size = [20, size[1]]
    scroll_bar = ScrollBar([0,20], [20,40])
    scroll_bar.id = 'actor_results_scroll_bar'
    document_scroll = make_widget_dict(size, 
                                      position,
                                      (100,100,100), 
                                      actors = [scroll_bar])
    
    return [title_widget, document_widget, document_scroll], {'name' : 'document'}

def setup_search(gui):
    widget_dict = dict()
    button_size = [120, 35]
    button_pos = centered_buttons_locs_hori(button_size, 3, 
                           [gui.width, gui.height], spacing = 150)
    button_colors = standard_button_colors()
    button_alpha = 255
    buttons = []
    buttons.append(
        search_button("search_results", button_pos[2], button_size, button_colors[0], 
                    button_alpha, "Search", font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = button_colors[1],
                    pressed_color = button_colors[2])
        )
    buttons[-1].id = 'button_search_'
    return_to_build_case = SquareChangeLayer(
        "Main_menu2", [25, 25], button_size, button_colors[0], 
                    button_alpha, "Rebuild Case", font = ['Arial', 20, (0, 0, 0)],
                    hover_over_color = button_colors[1],
                    pressed_color = button_colors[2])
    buttons.append(return_to_build_case)
    size = [gui.height, gui.width]
    position = [0, 0]
    color = (255,255,255)
    graphic = get_mongoose_graphic()
    textboxes = [
        SearchBar(button_pos[0], length = button_pos[2][0] - button_pos[0][0] - 10,
                 box_color = (200,200,200),
                 font = ["Arial", 20, (0,0,0)],
                 default_text = "Enter Search Terms")]
    textboxes[-1].id = 'textbox_search_bar2'
    textboxes[-1].search_button = buttons[-2]
    widget_dict = make_widget_dict(size, position, color, 
                                  buttons = buttons,
                                  graphics = [graphic],
                                  textboxs = textboxes)
    
    return [widget_dict], {"name" : "search_menu"}

def setup_main_menu(gui):
    
    button_size = [150, 35]
    button_pos = centered_buttons_locs_hori(button_size, 1, 
                           [gui.width, gui.height], spacing = 0, 
                           vert_offset = -gui.height//6)
    button_color = (200, 200, 255)
    button_alpha = 255
    buttons = []
    buttons.append(
        BuildCase("search_menu", button_pos[0], button_size, button_color, 
                    button_alpha, "Build Case", font = ['Arial', 20, (0, 0, 0)])
        )
    graphic = get_mongoose_graphic()
    size = [gui.height, gui.width]
    position = [0, 0]
    color = (255,255,255)
    button_colors = standard_button_colors()
    updir = UpOneDir([2, gui.height/2 - 100], [24, 37], button_colors[0], 
                    button_alpha, "^", font = ['Arial', 20, (0, 0, 0)])
    updir.wid_f = 'widget_files'
    updir.browse_tb = 'textbox_dir_browse'
    buttons.append(updir)
    r_button = RemoveCase([size[0]-210, size[1]-50], [200, 40], 
                          button_colors[0], 
                    button_alpha, "Remove", font = ['Arial', 20, (0, 0, 0)])
    r_button.id = 'button_remove'
    buttons.append(r_button)
    case_button_widget = make_widget_dict(size, position, color, 
                                  buttons = buttons,
                                  graphics = [graphic])
    case_button_widget['id'] = 'widget_case'
    size = [gui.width-260, gui.height/2]
    position = [30, gui.height/2 - 50]
    def_path = os.path.expanduser('~')
    lg = size[0]-30
    file_browse = ChangeDir([25, gui.height/2 - 100], length = lg,
                 box_color = (200,200,200),
                 font = ["Arial", 20, (0,0,0)],
                 default_text = "Enter Directory")
    file_browse.wid_f = 'widget_files'
    file_browse.text = def_path
    file_browse.id = 'textbox_dir_browse'
    case_button_widget['textboxs'] = [file_browse]
    fshower = FileShower([0,0],[0,0])
    fshower.prev_file = ''
    file_explorer_widget = make_widget_dict(size, position, color, 
                                  actors = [fshower])
    file_explorer_widget['id'] = 'widget_files'
    file_explorer_widget['other'] = {'file_loc' : def_path,
                                     'scroll_bar' : 'actor_scroll_bar',
                                     'orig_size' : [x for x in size]}
    file_explorer_widget['class'] = SizeChanger
    position = [size[0] + position[0]-5, position[1]]
    size = [20, size[1]]
    scroll_bar = ScrollBar([0,20], [20,40])
    scroll_bar.id = 'actor_scroll_bar'
    file_explorer_scroll = make_widget_dict(size, position, (100,100,100), 
                                  actors = [scroll_bar])
    fshower2 = FileShower2([0,0],[0,0])
    fshower2.prev_files = set()
    size = [210, gui.height/2+50]
    position = [gui.width-230, gui.height/2 - 110]
    color = (255,255,255)
    c_files_graphic = Graphic([size[0],40], [position[0], position[1] - 40])
    c_files_graphic.surf.set_colorkey((5, 7, 11))
    font = pg.font.SysFont('Arial', 20, bold = True).render(
        'Case Files', True, (0,0,0))
    sze = np.array(font.get_size())
    sze2 = np.array(c_files_graphic.surf.get_size())
    c_files_graphic.add_surf(font, (sze2 - sze)/2)
    case_button_widget['graphics'].append(c_files_graphic)

    case_explorer_widget = make_widget_dict(size, position, color, 
                                  actors = [fshower2])
    case_explorer_widget['id'] = 'widget_case_files'
    case_explorer_widget['other'] = {'case_files' : [],
                                     'files_changed' : False,
                                     'scroll_bar' : 'actor_case_scroll_bar',
                                     'orig_size' : size}
    case_explorer_widget['class'] = SizeChanger
    position = [size[0] + position[0], position[1]]
    size = [15, size[1]]
    case_scroll_bar = ScrollBar([0,20], [15,40])
    case_scroll_bar.id = 'actor_case_scroll_bar'
    case_explorer_scroll = make_widget_dict(size, position, (100,100,100), 
                                  actors = [case_scroll_bar])
    return [case_button_widget, 
            file_explorer_widget,
            case_explorer_widget,
            case_explorer_scroll,
            file_explorer_scroll], {"name" : "Main_menu2"}

def setup_loading_screen(gui):
    
    locs = centered_buttons_locs_vert([200,100], 2, 
                           [gui.width, gui.height], 
                           spacing = gui.height//6,
                           vert_offset = gui.height//12)
    
    loadbar = Graphic([200,200], position = locs[0])
    loading_circle_path = os.path.join('Assets', 'loadingcircle.png')
    bar, bar_rect = load_image(loading_circle_path, data_path, colorkey = -1, size = [100,100])
    loadbar.surf.set_colorkey(bar.get_colorkey())
    color = bar.get_colorkey()
    loadbar.surf.fill(bar.get_colorkey())
    loadbar.add_surf(bar,[0,0])
    loadbar.id = 'load_bar'
    
    a = Actor([0,0], size = [0,0])
    graphic = Graphic([200, 100], locs[1])
    graphic.surf.set_colorkey((5, 7, 11))
    font = pg.font.SysFont('Arial', 20).render('Building Case...', True, (250, 100, 100))
    sze = font.get_size()
    graphic.add_surf(font, [(200 - sze[0])/2,0])
    mongoose = get_mongoose_graphic()
    size = [gui.height, gui.width]
    position = [0, 0]
    color = (255,255,255)
    graphics = [graphic, loadbar, mongoose]
    widget_dict = make_widget_dict(size, position, color,
                                 graphics = graphics,
                                  actors = [a])
    thread = LoadThread()
    thread.value = None
    thread.files = []
    print("thread starting")
    thread.start()
            
    widget_dict['other'] = {'thread' : thread,
                            'next_layer': 'Main_menu2',
                            'load_bar_orig' : None,
                            'files' : [],
                            'first_screen' : False}
    widget_dict['class'] = LoadingScreen
    return [widget_dict], {"name" : "Main_menu"}


def main():
    gui = Game(width = SCREEN_WIDTH, 
                  height = SCREEN_HEIGHT,
                  save_layers = [],
                  layer_funcs = [eval(fun) for fun in setup],
                  always_draw = True,
                  enable_shadows = True)
    res = [800, 800]
    handle = GameHandler(gui, framerate = 25, resolution = res)
    handle.run()
    return handle

try:
    if __name__ == "__main__":
        handle = main()
except:
    e = Exception("quiting")
    raise(e)
finally:
    pg.quit()
print(sum(handle.times)/len(handle.times))
# Run until the user asks to quit

# Done! Time to quit.
pg.quit()
