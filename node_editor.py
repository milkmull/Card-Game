import json
import difflib

import pygame as pg

import save
from custom_card_base import Card
import allnodes
import node_parser
import node_data
import tester
import ui
import screens
from constants import *

def init():
    allnodes.init()
    tester.init()
    globals()['SAVE'] = save.get_save()

#visual stuff-----------------------------------------------------------------------

class Search_Bar(ui.Compound_Object):
    def __init__(self, buttons, start_pos):
        super().__init__()
        
        self.search_bar = ui.Input((100, 30), highlight=True)
        self.search_window = ui.Live_Window((100, 200), color=(0, 0, 0), hide_label=True)
        self.buttons = buttons
        self.search_window.join_objects(buttons, xpad=0, ypad=0)

        self.rect = self.search_bar.rect.copy()
        self.start_pos = start_pos
        self.rect.topleft = start_pos
        self.search_bar.rect.topleft = self.rect.topleft
        self.add_child(self.search_bar, current_offset=True)
        self.search_window.rect.midtop = self.rect.midbottom
        self.add_child(self.search_window, current_offset=True)
        
    @property
    def active(self):
        return self.rect.topleft != self.start_pos
        
    def search(self):
        m = self.search_bar.get_message()
        key = lambda b: sort_strings(m, b.object.get_message())
        self.search_window.sort_objects(key)
       
    def open_search(self):
        self.rect.center = pg.mouse.get_pos()
        self.search_bar.open()
        self.search_bar.highlight_full()
       
    def close_search(self):
        self.search_bar.close()
        self.rect.topleft = self.start_pos

class Sorter(ui.Compound_Object):
    def __init__(self, ne):
        super().__init__()

        p = ui.Live_Popup((450, 300), label='nodes')
        p.set_inflation(x=175)
        p.rect.midtop = (width // 2, height)
        self.rect = p.rect
        self.add_child(p, current_offset=True)
        self.popup = p

        self.groups = {}
        self.buttons = {}
        self.labels = {}
        for name in allnodes.NAMES:
            n = getattr(allnodes, name)
            if hasattr(n, 'cat'):
                cat = n.cat
                subcat = getattr(n, 'subcat', 'base')
                if cat not in self.groups:
                    self.groups[cat] = {}
                if subcat not in self.groups[cat]:
                    self.groups[cat][subcat] = [name]
                else:
                    self.groups[cat][subcat].append(name)
                img = allnodes.Node.RAW_CACHE[name]
                b = ui.Button.image_button(img, border_radius=0, func=ne.get_node, args=[name])
                self.buttons[name] = b
                if subcat not in self.labels:
                    tb = ui.Textbox(subcat, tsize=40, underline=True)
                    space_width = tb.get_text_rect(' ').width
                    spaces = ((self.popup.rect.width - tb.rect.width) // space_width) - 1
                    tb.set_message(subcat + (' ' * spaces))
                    tb = tb.to_static()
                    self.labels[subcat] = tb
                
        for cat in self.groups:
            for subcat in self.groups[cat]:
                self.groups[cat][subcat].sort(key=lambda name: self.buttons[name].rect.height)
                       
        x = self.rect.x - 5
        y = self.rect.y + 5
        for cat, _ in self.groups.items():
            b = ui.Button.text_button(cat, func=self.set_selection, args=[cat])
            b.rect.topright = (x, y)
            self.add_child(b, current_offset=True)
            y += b.rect.height + 5

    def set_selection(self, cat):
        items = []
        for subcat in self.groups[cat]:
            items.append(self.labels[subcat])
            for name in self.groups[cat][subcat]:
                items.append(self.buttons[name])
        self.popup.join_objects(items, xpad=10, ypad=10, dir='x', pack=True)

#string sorting stuff-----------------------------------------------------------------------

def sort_strings(a, b):
    d = difflib.SequenceMatcher(None, a, b).ratio()
    d = -int(d * 100)
    return d

#saving and loading stuff-----------------------------------------------------------------------

def save_group_node(name, gn):
    nodes = gn.nodes.copy() + [gn]
    
    group_data = load_group_data()
    group_data[name] = node_data.pack(nodes)
    
    with open('save/group_nodes.json', 'w') as f:
        json.dump(group_data, f, indent=4)

def load_group_data():
    with open('save/group_nodes.json', 'r') as f:
        data = json.load(f)
    return data

#sorting stuff-------------------------------------------------------------------------

def move_nodes(nodes, c):
    left = min({n.rect.left for n in nodes})
    right = max({n.rect.right for n in nodes})
    top = min({n.rect.top for n in nodes})
    bottom = max({n.rect.bottom for n in nodes})
    r = pg.Rect(left, top, right - left, bottom - top)
    cx, cy = r.center
    r.center = c
    dx = r.centerx - cx
    dy = r.centery - cy
    
    for n in nodes:
        n.rect.move_ip(dx, dy)
        n.set_port_pos()

#node editor--------------------------------------------------------------------------

class Node_Editor(ui.Menu, node_data.Node_Data):        
    def __init__(self, card):
        self.card = card

        node_data.Node_Data.__init__(self)
        self.active_node = None
        self.nodes = []
        self.wires = []
        self.objects_dict = {}
        ui.Menu.__init__(self, get_objects=self.editor_objects)
        
        self.anchor = None

        self.info_box = pg.Rect(0, 0, 100, 100)
        self.info_box.topright = (width, 0)
        self.info_node = None
        self.drag_manager = ui.DraggerManager(self.nodes)
        
        self.log = []
        self.logs = []
        self.log_history = []
        self.log_index = -1
        
        self.ctrl = False
        self.copy = False
        self.copy_data = None
        self.paste = False
        self.sort = False
        self.undo = False
        self.redo = False
        self.input = []

        self.ctimer = 40
        
        self.running = True
        
        allnodes.Manager.set_manager(self)
        
        if self.card.node_data:
            self.load_save_data(self.card.node_data)
        
#visual stuff--------------------------------------------------------------------
        
    def editor_objects(self):
        objects = []
        
        #search_bar = ui.Input((100, 30))
        #search_bar.rect.bottomleft = (width, 0)
        #self.objects_dict['search_bar'] = search_bar
        #objects.append(search_bar)
        
        buttons = []
        for name in allnodes.NAMES:
            b = ui.Button.text_button(name, size=(100, 30), border_radius=0, func=self.get_node, args=[name], tsize=15)
            buttons.append(b)
        for name, data in load_group_data().items():
            b = ui.Button.text_button(name, border_radius=0, func=self.load_group_node, args=[name, data])
            buttons.append(b)
        #objects += buttons
        
        #p = ui.Live_Window((100, 200), color=(0, 0, 0), hide_label=True)
        #p.rect.topleft = (width, height)
        #p.join_objects(buttons, xpad=0, ypad=0)
        #objects.append(p)
        #self.objects_dict['search_window'] = p
        
        sb = Search_Bar(buttons, (width, height))
        self.objects_dict['search_bar'] = sb
        objects.append(sb)

        b = ui.Button.text_button('save', func=self.save, tsize=15)
        b.rect.topleft = (5, 5)
        objects.append(b)
   
        b = ui.Button.text_button('test', tsize=15, func=tester.run_tester, args=[self.card])
        b.rect.topleft = objects[-1].rect.bottomleft
        b.rect.top += 5
        objects.append(b)

        def test_run():
            text = tester.test_run(self.card)
            if text:
                ui.menu.notice(text)
        
        b = ui.Button.text_button('test game', func=test_run, tsize=15)
        b.rect.topleft = objects[-1].rect.bottomleft
        b.rect.top += 5
        objects.append(b)
                
        b = ui.Button.text_button('publish card', func=self.publish, tsize=15)
        b.rect.top = 5
        b.rect.midleft = objects[-1].rect.midright
        b.rect.y += 5
        objects.append(b)
        
        b = ui.Button.text_button('load', func=self.load_progress, tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-2].rect.right + 5
        objects.append(b)
    
        b = ui.Button.text_button('group node', func=self.make_group_node, tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-1].rect.right + 5
        objects.append(b)
        
        b = ui.Button.text_button('ungroup node', func=self.ungroup_nodes, tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-1].rect.right + 5
        objects.append(b)
        
        nc = ui.Input((50, 20))
        nc.rect.bottomleft = (width, 0)
        objects.append(nc)
        self.objects_dict['numeric_control'] = nc
        
        group_name = ui.Input((100, 20), tsize=20)
        group_name.rect.topleft = objects[-4].rect.bottomleft
        group_name.rect.y += 5
        objects.append(group_name)
        self.objects_dict['group_name'] = group_name
        
        b = ui.Button.text_button('save group node', func=self.save_group_node, tsize=15)
        b.rect.midleft = objects[-1].rect.midright
        b.rect.x -= 5
        b.rect.y += 5
        objects.append(b)
        
        b = ui.Button.text_button('exit', func=self.exit, tsize=15)
        b.rect.midtop = objects[-1].rect.midbottom
        b.rect.y += 5
        objects.append(b)
        
        self.info_box = pg.Rect(0, 0, 50, 50)
        self.info_box.topright = (width - 20, 20)
        
        b = ui.Button.text_button('See node info', func=self.check_info, tsize=15)
        b.rect.midtop = self.info_box.midbottom
        b.rect.y += 10
        objects.append(b)
        
        s = Sorter(self)
        objects.append(s)
        
        #groups = {}
        #for n in allnodes.NAMES:
        #    n = getattr(allnodes, n)
        #    if hasattr(n, 'categories'):
        #        for g in n.categories:
        #            if g not in groups:
        #                groups[g] = [n]
        #            else:
        #                groups[g].append(n)
        #x = 10
        #for g, nodes in groups.items():
        #    p = ui.Live_Popup((100, 300), label=g)
        #    p.rect.topleft = (x, height)
        #    objects.append(p)
        #    x += p.rect.width + 20
        #    
        #    buttons = []
        #    for n in nodes:
        #        img = allnodes.Node.RAW_CACHE[n.__name__]
        #        b = ui.Button.image_button(img, border_radius=0, func=self.get_node, args=[n.__name__])#, tsize=15)
        #        buttons.append(b)
        #        
        #    p.join_objects(buttons)

        return objects
        
#log stuff--------------------------------------------------------------------

    def reset_logs(self):
        self.logs.clear()
        self.log.clear()
        self.log_index = -1

    def add_log(self, log):
        self.logs.append(log)
        
    def get_logs(self):
        logs = self.logs.copy()
        self.logs.clear()
        return logs

    def update_log(self):
        new_logs = self.get_logs()
        if new_logs:

            if self.log_index == -1:
                self.log_history.clear()

            if self.log_index == 14:
                self.log_history = self.log_history[1:]
            else:
                if self.log_index > -1:
                    self.log_history = self.log_history[:self.log_index + 1]
                else:
                    self.log_history.clear()
                self.log_index += 1
                
            self.log_history.append(new_logs)
            
            print('d', new_logs)

    def undo_log(self):
        if not self.log_history or self.log_index == -1:
            return
            
        logs = self.log_history[self.log_index]
        
        print('u', logs)
        
        for log in logs[::-1]:
            type = log['t']
            
            if type == 'carry':
                nodes = log['draggers']
                for n in nodes:
                    dx, dy = nodes[n]
                    n.rect.move_ip(-dx, -dy)
                    n.set_port_pos()
                    
            elif type == 'add':
                n = log['node']
                if not n.is_group():
                    self.del_node(n, d=True)
                else:
                    self.ungroup_node(n, d=True)
                    
            elif type == 'del':
                n = log['node']
                m = log['m']
                self.add_node(n, d=True) 
                if m == 'ug':
                    n.reset_ports()
                    
            elif type == 'conn':
                p0, p1 = log['ports']
                allnodes.Port.disconnect(p0, p1, d=True)
                
            elif type == 'disconn':
                n0, n1 = log['nodes']
                p0, p1 = log['ports']
                if p0.parent_port:
                    if p0 not in n0.ports:
                        n0.ports.append(p0)
                    if p0.group_node:
                        if p0 not in p0.group_node.ports:
                            p0.group_node.ports.append(p0)
                if p1.parent_port:
                    if p1 not in n1.ports:
                        n1.ports.append(p1)
                    if p1.group_node:
                        if p1 not in p1.group_node.ports:
                            p1.group_node.ports.append(p1)
                allnodes.Port.new_connection(p0, p1, force=True, d=True)
                
            elif type == 'val':
                i = log['i']
                m = log['m'][0]
                i.update_message(m)
                
            elif type == 'transform':
                n = log['n']
                types = log['types'][0]
                for p, t in types.items():
                    p = n.get_port(p)
                    p.set_types(t)
                    
            elif type == 'suppress':
                p = log['p']
                s = log['s']
                p.set_suppressed(not s, d=True)
                
        self.log_index -= 1
        
    def redo_log(self):
        if not self.log_history or self.log_index == len(self.log_history) - 1:
            return
            
        logs = self.log_history[self.log_index + 1]
        
        print('r', logs)
        
        for log in logs:
            type = log['t']
            
            if type == 'carry':
                nodes = log['draggers']
                for n in nodes:
                    dx, dy = nodes[n]
                    n.rect.move_ip(dx, dy)
                    n.set_port_pos()
                    
            elif type == 'del':
                n = log['node']
                m = log['m']
                if m == 'ug':
                    self.ungroup_node(n, d=True)
                else:
                    self.del_node(n, d=True)   
                    
            elif type == 'add':
                n = log['node']
                self.add_node(n, d=True)
                if n.is_group():
                    n.reset_ports()
                    
            elif type == 'disconn':
                p0, p1 = log['ports']
                allnodes.Port.disconnect(p0, p1, d=True)
                
            elif type == 'conn':
                n0, n1 = log['nodes']
                p0, p1 = log['ports']
                if p0.parent_port:
                    if p0 not in n0.ports:
                        n0.ports.append(p0)
                    if p0.group_node:
                        if p0 not in p0.group_node.ports:
                            p0.group_node.ports.append(p0)
                if p1.parent_port:
                    if p1 not in n1.ports:
                        n1.ports.append(p1)
                    if p1.group_node:
                        if p1 not in p1.group_node.ports:
                            p1.group_node.ports.append(p1)
                allnodes.Port.new_connection(p0, p1, d=True)
                
            elif type == 'val':
                i = log['i']
                m = log['m'][1]
                i.update_message(m)
                
            elif type == 'transform':
                n = log['n']
                types = log['types'][1]
                for p, t in types.items():
                    p = n.get_port(p)
                    p.set_types(t)
                    
            elif type == 'suppress':
                p = log['p']
                s = log['s']
                p.set_suppressed(s, d=True)
                
        self.log_index += 1

#base node stuff--------------------------------------------------------------------

    def reset(self):
        self.delete_nodes(nodes=self.nodes.copy())
        self.wires.clear()
        self.id = 0
        
    def set_loaded_id(self):
        self.id = max({n.id for n in self.nodes}, default=-1) + 1
        
#wire stuff--------------------------------------------------------------------
        
    def check_wire_break(self):
        a = self.anchor
        b = pg.mouse.get_pos()
        
        for w in self.wires.copy():
            w.check_break(a, b)
        
    def new_wire(self, p0, p1):
        w = allnodes.Wire(p0, p1)
        self.wires.append(w)
        
    def del_wire(self, w):
        if w in self.wires:
            self.wires.remove(w)
        
#node management stuff--------------------------------------------------------------------

    def add_nodes(self, nodes):
        for n in nodes:
            self.add_node(n)

    def add_node(self, n, d=False):
        self.nodes.append(n)
        if not d:
            self.add_log({'t': 'add', 'node': n})
             
    def get_node(self, name, val=None, pos=None, nodes=None, held=True):
        if len(self.nodes) == 50:
            return

        if pos is None and held:
            pos = pg.mouse.get_pos()
        
        n = super().get_node(name, val=val, pos=pos, nodes=nodes)
        
        if held:
            n.start_held()
            
        self.add_node(n)
        return n

    def make_group_node(self):
        nodes = [n for n in self.get_selected() if not n.is_group()]
        if len(nodes) > 1:
            gn = self.get_node('GroupNode', nodes=nodes, held=False)
            if gn:
                self.add_log({'t': 'gn', 'gn': gn, 'nodes': nodes})
                return gn

    def ungroup_nodes(self):
        nodes = [n for n in self.get_selected() if n.is_group()]
        if nodes:
            for n in nodes:
                self.ungroup_node(n)
                
    def ungroup_node(self, n, d=False):
        n.ungroup()
        self.del_node(n, method='ug', d=d)

    def delete_nodes(self, nodes=None):
        if nodes is None:
            nodes = self.get_all_selected()
        for n in nodes:
            self.del_node(n)
            
    def del_node(self, n, method='del', d=False):
        n.delete()
        self.nodes.remove(n)
        if not d:
            self.add_log({'t': 'del', 'node': n, 'm': method})

    def exists(self, name):
        return any({n.name == name for n in self.nodes})
        
#active node stuff--------------------------------------------------------------------
        
    def get_active_node(self):
        return self.active_node
        
    def set_active_node(self, n):
        self.active_node = n
        
    def close_active_node(self):
        if self.active_node:
            self.active_node.end_connect()
            self.active_node = None

#selection stuff--------------------------------------------------------------------
            
    def get_selected(self):
        return [n for n in self.drag_manager.get_selected() if n.visible]
        
    def get_all_selected(self):
        nodes = self.get_selected()
        for n in nodes:
            if n.is_group():
                nodes += n.nodes
        return nodes
        
#copy and paste stuff--------------------------------------------------------------------
        
    def copy_nodes(self):
        nodes = self.get_all_selected()
        self.copy_data = node_data.pack(nodes)

    def paste_nodes(self):
        data = self.copy_data
        if not data or len(self.nodes) + len(data['nodes']) > 50:
            return
        nodes = self.unpack(data)
        if nodes:
            move_nodes(nodes, pg.mouse.get_pos())
            for n in nodes:
                n.start_held() 
        return nodes
        
    def remap_nodes(self, nodes):
        for n in nodes:
            n.id = self.id
            self.id += 1

#loading stuff--------------------------------------------------------------------

    def load_progress(self):
        self.reset()
        with open('save/card.json', 'r') as f:
            save_data = json.load(f) 
        self.unpack(save_data)
        self.set_loaded_id()

    def load_group_node(self, name, data):
        nodes = self.unpack(data)
        nodes[-1].set_name(name)
        return nodes

    def load_save_data(self, data):
        self.reset()
        nodes = self.unpack(data)
        for n in nodes:
            n.drop()
        self.reset_logs()

#saving stuff--------------------------------------------------------------------

    def get_save_data(self):
        return node_data.pack(self.nodes)

    def save(self):
        self.card.save(nodes=self.nodes)
    
    def publish(self):
        self.card.publish(nodes=self.nodes)

    def save_group_node(self):
        gn = None
        nodes = self.get_selected()
        for n in nodes:
            if n.is_group():
                gn = n
                break
        else:
            return
            
        name = self.group_name.get_message()
        save_group_node(name, gn)

#other stuff--------------------------------------------------------------------

    def spread(self):
        funcs = []
        for n in self.nodes:
            if n.visible:
                func = allnodes.Mapping.find_chunk(n, [])
                if not any({set(o) == set(func) for o in funcs}):
                    funcs.append(func)

        for nodes in funcs:
            lead = allnodes.Mapping.find_lead(nodes)
            columns = allnodes.Mapping.map_flow(lead, nodes.copy(), {})
            columns = [columns[key][::-1] for key in sorted(columns)]
            
            x = width // 2
            y = height // 2
            cy = y
            
            for col in columns:
                r = pg.Rect(0, 0, 0, 0)
                for n in col:
                    n.start_held()
                    n.rect.topleft = (x, y)
                    y += n.rect.height + 10
                    r.height += n.rect.height + 10
                    
                r.top = col[0].rect.top
                dy = cy - r.centery
                for n in col:
                    n.rect.move_ip(0, dy)
                    n.set_port_pos()
      
                x += max({n.rect.width for n in col}) + 20
                y = height // 2

        draggers = {}

        x = 50
        y = 50
            
        for nodes in funcs:
            left = min({n.rect.left for n in nodes})
            right = max({n.rect.right for n in nodes})
            top = min({n.rect.top for n in nodes})
            bottom = max({n.rect.bottom for n in nodes})
            r = pg.Rect(left, top, right - left, bottom - top)
            cx, cy = r.center
            r.topleft = (x, y)
            dx = r.centerx - cx
            dy = r.centery - cy
            
            for n in nodes:
                n.rect.move_ip(dx, dy)
                n.set_port_pos()
                dist = n.get_carry_dist()
                if dist:
                    draggers[n] = dist
                n.drop()
                
            y += r.height + 20
            if y > height - 100:
                y = 50
                x += r.width + 20
                
        if draggers:
            self.add_log({'t': 'carry', 'draggers': draggers})

    def check_info(self):
        info_node = None
        for n in self.nodes:
            if n.rect.colliderect(self.info_box):
                info_node = n
                break
        if info_node:
            m = ui.Menu(get_objects=screens.info_menu, args=[n])
            m.run()

#run stuff--------------------------------------------------------------------
    
    def exit(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()
            self.update_log()
            
    def events(self):
        hit = False
        dub = False
        click_up = False
        click_down = False
        
        events = self.get_events()
        
        p = events['p']
        q = events.get('q')
        kd = events.get('kd')
        ku = events.get('ku')
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        
        if q:
            self.quit()
            
        if kd:
            if kd.key == pg.K_ESCAPE:
                self.quit()
                
            elif (kd.key == pg.K_RCTRL) or (kd.key == pg.K_LCTRL): 
                self.ctrl = True
            elif kd.key == pg.K_c:
                self.copy = True
            elif kd.key == pg.K_v:
                self.paste = True
            elif kd.key == pg.K_q:
                self.sort = True
            elif kd.key == pg.K_z:
                self.undo = True
            elif kd.key == pg.K_y:
                self.redo = True
                
            elif kd.key == pg.K_DELETE:
                self.delete_nodes()
                
        elif ku:
            if (ku.key == pg.K_RCTRL) or (ku.key == pg.K_LCTRL):
                self.ctrl = False
            elif ku.key == pg.K_c:
                self.copy = False
            elif ku.key == pg.K_v:
                self.paste = False
            elif ku.key == pg.K_q:
                self.sort = False
            elif ku.key == pg.K_z:
                self.undo = False
            elif ku.key == pg.K_y:
                self.redo = False
        
        if mbd:
            if mbd.button == 1:
                click_down = True
                if self.ctimer > 10:
                    self.ctimer = 0
                elif not self.objects_dict['search_bar'].active:
                    dub = True     
            elif mbd.button == 3:
                self.anchor = p

        elif mbu:
            if mbu.button == 1:
                click_up = True
            elif mbu.button == 3:
                self.check_wire_break()
                self.anchor = None
                
        if self.ctrl:     
            if self.copy:
                self.copy_nodes()
                self.copy = False
            elif self.paste:
                self.paste_nodes()
                self.paste = False
            elif self.sort:
                self.spread()
                self.sort = False
            elif self.undo:
                self.undo_log()
                self.undo = False
            elif self.redo:
                self.redo_log()
                self.redo = False
                
        for n in self.nodes[::-1]:
            if n.visible:
                n.events(events)
                if not hit and n.big_rect.collidepoint(p) and mbd:
                    hit = True
                    
        if click_up:
            self.close_active_node()
        
        hit = (super().sub_events(events) and mbd) or hit
                        
        if dub and not hit:
            self.objects_dict['search_bar'].open_search()
                
        elif click_down and not self.objects_dict['search_bar'].collide(p):
            self.objects_dict['search_bar'].close_search()

        rect = not (self.get_active_node() or hit)
        self.drag_manager.events(events, rect=rect)

    def update(self):   
        if self.objects_dict['search_bar'].active:
            self.objects_dict['search_bar'].search()
            
        super().update()
                
        self.drag_manager.update()
        carry_log = self.drag_manager.get_next_log()
        if carry_log:
            self.add_log(carry_log)

        for n in self.nodes:
            if n.visible:
                n.update()
        for w in self.wires:
            w.update()
            
        if self.ctimer < 20:
            self.ctimer += 1
                
    def draw(self):
        self.window.fill((0, 0, 0))
        
        self.drag_manager.draw(self.window)
        
        for n in self.nodes:
            if n.visible:
                n.draw(self.window)
    
        for w in self.wires:
            w.draw(self.window)
            
        super().lite_draw()
            
        n = self.get_active_node()
        if n:
            n.draw_wire(self.window)
            
        if self.anchor:
            s = self.anchor
            e = pg.mouse.get_pos()
            pg.draw.line(self.window, (0, 0, 255), s, e, width=4)
            
        if self.info_node:
            self.info_node.draw(self.window)
                
        pg.display.flip()
        
if __name__ == '__main__':

    pg.init()
    pg.display.set_mode((width, height))
    
    save.init()
    init()
    uinit()

    ne = Node_Editor(Card(name='__test__'))
    ne.run()
            
    pg.quit()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            