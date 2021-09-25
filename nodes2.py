import pygame as pg

import save

import allnodes

from ui import *

from constants import *

import difflib

def get_nodes(nodes_in):
    nodes_out = []
    
    for n in nodes_in:
        n = allnodes.get_node(n)
        if n:
            nodes_out.append(n)
            
    return nodes_out
    
def sort_strings(a, b):
    d = difflib.SequenceMatcher(None, a, b).ratio()
    d = -int(d * 100)
    return d

def run_parser(nodes):
    np = Node_Parser(nodes)
    out = np.run()
    
    #print(out)
    
    with open('new_card.py', 'w') as f:
        f.write(out)
    
class Node_Parser:
    def __init__(self, nodes):
        self.nodes = nodes
        self.start_node = next((n for n in self.nodes if n.name == 'start'), None)
        
        self.header = "class Test(Card):\n\tdef __init__(self, game, uid):\n\t\tsuper().__init__(game, uid, 'test', tags=[])\n\n"
        self.dec_line = ''

        self.funcs = {}
        
    def new_func(self, node):
        self.funcs[node.name] = {'header': '\t' + node.get_text(), 'start': '', 'dec': '', 'body': '', 'end': ''}
        
    def find_funcs(self):
        return [n for n in self.nodes if 'func' in n.types]
        
    def run(self):
        if not self.start_node:
            return ''
            
        for n in self.find_funcs():
            self.parse_nodes(n, func=None)
        
        out = self.header

        for func in self.funcs:
            info = self.funcs[func]
            header = info['header']
            start = info['start']
            dec = info['dec']
            body = info['body']
            end = info['end']
            if not start + body + end:
                body = '\t\tpass\n'
            out += header + start + dec + body + end

        return out
        
    def find_locals(self, node):
        dec_line = ''
        ports = set(node.map_scope([]))
        for p in ports:
            print(p, p.node)
            n = p.node
            if 'dec' in n.types:
                dec_line += (2 * '\t') + n.get_dec()
                
        return dec_line

    def parse_nodes(self, node, func=None, tabs=2):
        text = ''
        
        if 'func' in node.types:
            self.new_func(node)
            func = node.name
            self.funcs[func]['start'] = node.get_start()
            self.funcs[func]['dec'] += self.find_locals(node)
            self.funcs[func]['end'] = node.get_end()
            tabs = 2
        else:
            text = (tabs * '\t') + node.get_text()
            self.funcs[func]['body'] += text
        
        split_found = False
        for op in node.get_output_ports():
            if 'split' in op.types:
                if op.connection:
                    self.parse_nodes(op.connection, func=func, tabs=tabs + 1)
                split_found = True
                break
     
        if split_found:
            if self.funcs[func]['body'].endswith(text):
                self.funcs[func]['body'] += ((tabs + 1) * '\t') + 'pass\n'

        for op in node.get_output_ports():
            if 'flow' in op.types and 'split' not in op.types:
                if not op.is_open():
                    self.parse_nodes(op.connection, func=func, tabs=tabs)

class Node_Editor:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        
        self.camera = self.screen.get_rect()

        self.nodes = allnodes.NODES
        self.dwire = None
        self.elements = self.set_screen()
        
        self.input = []
        self.ctimer = 40
        
        self.running = True
        
    def set_screen(self):
        screen = []
        
        i = Input((100, 30))
        i.rect.bottomleft = (width, 0)
        screen.append(i)
        self.search_bar = i
        
        buttons = []
        for name in allnodes.NAMES:
            b = Button((100, 20), name, border_radius=0)
            b.set_func(allnodes.get_node, args=[name])
            buttons.append(b)
        screen += buttons
        
        p = Pane((100, 200), color=(0, 0, 0), live=True)
        p.rect.topleft = i.rect.bottomright
        p.join_objects(buttons, xpad=0, ypad=0)
        p.update()
        screen.append(p)
        self.search_window = p
        
        r = Rect_Selector(func=self.select_nodes)
        self.selecion_rect = r
        
        nc = Input((50, 20))
        nc.rect.bottomleft = (width, 0)
        screen.append(nc)
        self.numeric_control = nc

        return screen
        
    def check_wire_break(self):
        A = self.dwire
        B = pg.mouse.get_pos()
        
        for n in self.nodes:
            n.check_break(A, B)
            
    def dub_click(self, p):
        self.search_bar.rect.center = p
        self.search_window.rect.topleft = self.search_bar.rect.bottomleft
        self.search_window.rect.y += 5
        
    def search(self):
        m = self.search_bar.get_message()
        key = lambda b: sort_strings(m, b.get_message())
        self.search_window.sort_objects(key)
        
    def close_search(self):
        self.search_bar.close()
        self.search_bar.rect.bottomleft = (width, 0)
        self.search_window.rect.topleft = self.search_bar.rect.bottomright
        
    def select_nodes(self):
        selected = self.selecion_rect.get_selected(self.nodes)
        for n in selected:
            n._selected = True
            n.add_to_held_list()
        
    def delete_nodes(self):
        for n in self.nodes.copy():
            if n._selected:
                n.delete()

    def run(self):
        while self.running:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        hit = False
        dub = False
        p = pg.mouse.get_pos()
        self.input = pg.event.get()
        
        for e in self.input:
            
            if e.type == pg.QUIT:
                quit()       
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    quit()
                
                elif e.key == pg.K_DELETE:
                    self.delete_nodes()
                    
                elif e.key == pg.K_p:
                    run_parser(self.nodes)

            elif e.type == pg.MOUSEBUTTONDOWN:
            
                if e.button == 1:
                    if self.ctimer > 10:
                        self.ctimer = 0
                    elif not self.search_bar.active:
                        dub = True
                        
                elif e.button == 3:
                    self.dwire = pg.mouse.get_pos()
  
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 3:
                    self.check_wire_break()
                    self.dwire = None

        for n in self.nodes[::-1]:
            n.events(self.input)
            if not hit:
                if n.big_rect.collidepoint(p):
                    hit = True
                    
        if dub and not hit:
            self.dub_click(p)
                    
        for e in self.elements:
            if hasattr(e, 'events'):
                e.events(self.input)
                if not hit:
                    if e.rect.collidepoint(p):
                        hit = True
                        
        if dub:
            self.search_bar.highlight_full()
                        
        if not hit and not allnodes.Node.wire:
            self.selecion_rect.events(self.input)
                
        if not self.search_bar.active:
            self.close_search()
            
    def update(self):            
        if self.search_bar.active:
            self.search()
            
        for e in self.elements:
            if hasattr(e, 'update'):
                e.update()
        self.selecion_rect.update()
                
        for n in self.nodes:
            n.update()
            
        if self.ctimer < 20:
            self.ctimer += 1
                
    def draw(self):
        self.screen.fill((0, 0, 0))
                
        for n in self.nodes:
            n.draw(self.screen)
            
        for n in self.nodes:
            n.draw_ports(self.screen)
 
        for e in self.elements:
            if hasattr(e, 'draw'):
                e.draw(self.screen)
        self.selecion_rect.draw(self.screen)
            
        if self.dwire:
            s = self.dwire
            e = pg.mouse.get_pos()
            pg.draw.line(self.screen, (0, 0, 255), s, e, width=4)
                
        pg.display.flip()
        
if __name__ == '__main__':

    pg.init()
    pg.display.set_mode((width, height))
    
    allnodes.init()

    ne = Node_Editor()
    ne.run()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            