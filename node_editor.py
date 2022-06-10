import json
import difflib

import pygame as pg

from save import CONSTANTS

import node_data
import mapping
import tester
import ui
import screens

WIDTH, HEIGHT = CONSTANTS['screen_size']
CENTER = CONSTANTS['center']
   
def save_group_node(gn):
    nodes = gn.nodes.copy() + [gn]
    data = node_data.pack(nodes)
    with open('data/group_nodes.json', 'r') as f:
        group_data = json.load(f)
    group_data[gn.get_name()] = data
    with open('data/group_nodes.json', 'w') as f:
        json.dump(group_data, f, indent=4)

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

class Node_Menu(ui.Compound_Object):
    def __init__(self, ne):
        super().__init__()
        
        self.ne = ne

        p = ui.Live_Popup((450, 350), vel=60, hide_label=True)
        p.set_inflation(x=175, y =-100)
        p.rect.midtop = (WIDTH // 2, HEIGHT)
        self.rect = p.rect
        self.add_child(p, current_offset=True)
        self.popup = p
        
        up_arrow = ui.Image_Manager.get_arrow('u', (16, 16))
        
        popup_button = ui.Button.image_button(up_arrow, padding=(5, 5), func=self.popup_control, tag='u')
        popup_button.rect.bottomright = self.popup.rect.topright
        popup_button.rect.y -= 20
        self.add_child(popup_button, current_offset=True)
        self.popup_button = popup_button
 
        self.tabs = {}

        self.node_groups = {}
        self.node_buttons = {}
        self.node_labels = {}
        
        for name, n in ne.NODES.items():
            if hasattr(n, 'cat'):
                cat = n.cat
                subcat = getattr(n, 'subcat', 'base')
                if cat not in self.node_groups:
                    self.node_groups[cat] = {}
                if subcat not in self.node_groups[cat]:
                    self.node_groups[cat][subcat] = [name]
                else:
                    self.node_groups[cat][subcat].append(name)
                img = node_data.get_cached_img(name)
                b = ui.Button.image_button(img, border_radius=0, func=self.get_node, args=[name], padding=(0, 5), color2=(50, 50, 50))
                self.node_buttons[name] = b
                if subcat not in self.node_labels:
                    self.new_subcat(subcat)
                    
        cat = 'group'
        self.node_groups[cat] = {}
        for name, data in ne.GROUPS.items():
            subcat = data.get('subcat', 'base')
            if subcat not in self.node_groups[cat]:
                self.node_groups[cat][subcat] = [name]
            else:
                self.node_groups[cat][subcat].append(name)
            img = node_data.get_cached_img(name)
            b = ui.Button.image_button(img, border_radius=0, func=self.get_group_node, args=[name])
            self.node_buttons[name] = b
            if subcat not in self.node_labels:
                self.new_subcat(subcat)
                
        for cat in self.node_groups:
            for subcat in self.node_groups[cat]:
                self.node_groups[cat][subcat].sort(key=lambda name: self.node_buttons[name].rect.height)
                     
        self.tabs['node'] = {'button': None, 'tabs': {}, 'subtab': list(self.node_groups)[0]}
        x = self.rect.x - 5
        y = self.rect.y + 5
        for subtab, _ in self.node_groups.items():
            b = ui.Button.text_button(subtab, func=self.set_node_subtab, args=[subtab], padding=(5, 2))
            b.rect.topright = (x, y)
            self.tabs['node']['tabs'][subtab] = b
            self.add_child(b, current_offset=True)
            y += b.rect.height + 5
            
        b = ui.Button.text_button('nodes', func=self.set_tab, args=['node'], padding=(10, 5))
        b.rect.midbottom = (self.rect.x + (self.rect.width // 3), self.rect.y - 10)
        self.add_child(b, current_offset=True)
        self.tabs['node']['button'] = b
            
        self.tabs['info'] = {'button': None, 'tabs': {}, 'subtab': 'cards'}
        x = self.rect.x - 5
        y = self.rect.y + 5
        subtabs = ('cards', 'tags', 'decks', 'requests', 'logs')
        for subtab in subtabs:
            b = ui.Button.text_button(subtab, func=self.set_info_subtab, args=[subtab], padding=(5, 2))
            b.rect.topright = (x, y)
            self.tabs['info']['tabs'][subtab] = b
            self.add_child(b, current_offset=True)
            y += b.rect.height + 5

        b = ui.Button.text_button('info', func=self.set_tab, args=['info'], padding=(10, 5))
        b.rect.midbottom = (self.rect.x + ((2 * self.rect.width) // 3), self.rect.y - 10)
        self.add_child(b, current_offset=True)
        self.tabs['info']['button'] = b
        
        self.tab = None
        self.set_tab('node')
        self.start_force_down()
            
    def new_subcat(self, subcat):
        tb = ui.Textbox(subcat, tsize=40, underline=True)
        space_width = tb.get_text_rect(' ').width
        spaces = ((self.popup.rect.width - tb.rect.width) // space_width) - 1
        tb.set_message(subcat + (' ' * spaces))
        tb = tb.to_static()
        self.node_labels[subcat] = tb
                
    def set_tab(self, tab):
        self.start_force_up()
        for t in self.tabs:
            ev = t == tab
            for b in self.tabs[t]['tabs'].values():
                b.set_enabled(ev)
                b.set_visible(ev)
            if ev:
                self.tabs[t]['button'].color1 = (255, 0, 0)
            else:
                self.tabs[t]['button'].color1 = (0, 0, 0)
        self.tab = tab
        b = self.tabs[tab]['tabs'][self.tabs[tab]['subtab']]
        b.run_func()
        
    def set_subtab(self, subtab):
        for st, b in self.tabs[self.tab]['tabs'].items():
            if st == subtab:
                b.color1 = (0, 0, 255)
            else:
                b.color1 = (0, 0, 0)
        self.tabs[self.tab]['subtab'] = subtab

    def set_node_subtab(self, subtab):
        items = []
        for subcat in self.node_groups[subtab]:
            items.append(self.node_labels[subcat])
            for name in self.node_groups[subtab][subcat]:
                items.append(self.node_buttons[name])
        self.popup.join_objects(items, xpad=10, ypad=10, dir='x', pack=True)
        
        self.set_subtab(subtab)
        
    def set_info_subtab(self, subtab):
        if subtab == 'cards':
            self.get_cards()
        elif subtab == 'tags':
            self.get_tags()
        elif subtab == 'decks':
            self.get_decks()
        elif subtab == 'requests':
            self.get_requests()
        elif subtab == 'logs':
            self.get_logs()
            
        self.set_subtab(subtab)
        
    def get_cards(self):
        with open('save/cards.json', 'r') as f:
            card_data = json.load(f)
        
        objects = []
        offsets = []
        y = 20
        
        for type in card_data:
            tb = ui.Textbox.static_textbox(type, tsize=15)
            objects.append(tb)
            x = (self.popup.rect.width // 2) - tb.rect.width - 10
            offsets.append((x, y))
            for name in sorted(card_data[type]):
                b = ui.Button.text_button(name, func=self.get_node, args=['String'], kwargs={'val': name}, tsize=15, padding=(5, 2))
                objects.append(b)
                x = (self.popup.rect.width // 2) + 10
                offsets.append((x, y))
                y += b.rect.height
            y += b.rect.height
               
        self.popup.join_objects_custom(offsets, objects)
        
    def get_tags(self):
        with open('data/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for cat in data['tags']:
            tb = ui.Textbox.static_textbox(cat, tsize=15)
            objects.append(tb)
            x = (self.popup.rect.width // 2) - tb.rect.width - 10
            offsets.append((x, y))
            for tag in data['tags'][cat]:
                b = ui.Button.text_button(tag, func=self.get_node, args=['String'], kwargs={'val': tag}, tsize=15, padding=(5, 2))
                objects.append(b)
                x = (self.popup.rect.width // 2) + 10
                offsets.append((x, y))
                y += b.rect.height
            y += b.rect.height

        self.popup.join_objects_custom(offsets, objects)
    
    def get_decks(self):
        with open('data/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for deck in data['player decks']:
            b = ui.Button.text_button(deck, func=self.get_node, args=['String'], kwargs={'val': deck}, tsize=15, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5
        self.popup.join_objects_custom(offsets, objects)
        
    def get_requests(self):
        with open('data/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        for req in data['request strings']:
            b = ui.Button.text_button(req, func=self.get_node, args=['String'], kwargs={'val': req}, tsize=20, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5   
        self.popup.join_objects_custom(offsets, objects)
        
    def get_logs(self):
        with open('data/sheet_info.json', 'r') as f:
            data = json.load(f)
            
        objects = []
        offsets = []
        y = 20
        
        def run_log_menu(*args):
            m = ui.Menu(get_objects=screens.log_menu, args=args)
            m.run()
        
        for log, d in data['logs'].items():
            b = ui.Button.text_button(log, func=run_log_menu, args=[log, d], tsize=12, padding=(5, 2))
            objects.append(b)
            x = (self.popup.rect.width - b.rect.width) // 2
            offsets.append((x, y))
            y += b.rect.height + 5 
        self.popup.join_objects_custom(offsets, objects)
        
    def is_open(self):
        return self.popup_button.tag == 'd'
        
    def flip_arrow(self):
        img = self.popup_button.object
        img.set_image(pg.transform.flip(img.image, False, True))
        
    def popup_control(self):
        self.flip_arrow()
        if self.popup_button.tag == 'd':
            self.popup_button.set_tag('u')
            self.popup.start_force_down()
        elif self.popup_button.tag == 'u':
            self.popup_button.set_tag('d')
            self.popup.start_force_up()
            
    def start_force_down(self):
        if self.popup_button.tag == 'd':
            self.flip_arrow()
            self.popup_button.set_tag('u')
            self.popup.start_force_down()
            
    def start_force_up(self):
        if self.popup_button.tag == 'u':
            self.flip_arrow()
            self.popup_button.set_tag('d')
            self.popup.start_force_up()
            
    def get_node(self, *args, **kwargs):
        self.ne.get_node(*args, **kwargs)
        self.start_force_down()
        
    def get_group_node(self, *args, **kwargs):
        self.ne.get_group_node(*args, **kwargs)
        self.start_force_down()
        
    def draw(self, surf):
        super().draw(surf)
        if self.popup.is_visible():
            points = (
                (self.popup.get_total_rect().right - 2, self.rect.top),
                (self.rect.left, self.rect.top),
                (self.rect.left, self.rect.bottom - 2),
                (self.popup.get_total_rect().right - 2, self.rect.bottom - 2)
            )
            pg.draw.lines(surf, (255, 255, 255), not self.popup.scroll_bar.visible, points, width=3)

class Context_Manager(ui.Compound_Object):
    def __init__(self, ne):
        super().__init__()
        self.rect = pg.Rect(0, 0, 1, 1)
        
        self.ne = ne
        self.node = None
        
        self.objects_dict = {}
        
        kwargs = {'size': (100, 25), 'border_radius': 0, 'color1': (255, 255, 255), 'fgcolor': (0, 0, 0), 'tsize': 12}
        
        b = ui.Button.text_button('copy', func=self.ne.copy_nodes, **kwargs)
        self.objects_dict['copy'] = b
        
        b = ui.Button.text_button('delete', func=self.ne.delete_nodes, **kwargs)
        self.objects_dict['delete'] = b
        
        b = ui.Button.text_button('transform', **kwargs)
        self.objects_dict['transform'] = b
        
        b = ui.Button.text_button('info', func=ui.Menu.build_and_run, **kwargs)
        self.objects_dict['info'] = b
        
        b = ui.Button.text_button('group', func=self.ne.create_new_group_node, **kwargs)
        self.objects_dict['group'] = b
        
        b = ui.Button.text_button('ungroup', func=self.ne.ungroup_node, **kwargs)
        self.objects_dict['ungroup'] = b
        
        b = ui.Button.text_button('paste', func=self.ne.paste_nodes, **kwargs)
        self.objects_dict['paste'] = b
        
        b = ui.Button.text_button('select all', func=self.ne.drag_manager.select_all, **kwargs)
        self.objects_dict['select_all'] = b
        
        b = ui.Button.text_button('clean up', func=self.ne.spread, **kwargs)
        self.objects_dict['clean_up'] = b
        
        self.close()
        
    @property
    def objects(self):
        return list(self.objects_dict.values())
        
    def is_open(self):
        return self.rect.topleft != (-100, -100)
        
    def open(self, pos, node):
        self.clear_children()
        self.rect.topleft = pos
        
        if node:
            selected = self.ne.get_selected()

        x, y = pos
        for name, b in self.objects_dict.items():
            add = False
            
            if node:
                if name == 'copy':
                    if not selected:
                        b.set_args(kwargs={'nodes': [node]})
                        add = True
                    elif node in selected:
                        b.set_args(kwargs={'nodes': selected})
                        add = True
                elif name == 'delete':
                    if not selected:
                        b.set_args(kwargs={'nodes': [node]})
                        add = True
                    elif node in selected:
                        b.set_args(kwargs={'nodes': selected})
                        add = True
                elif name == 'transform':
                    if node.can_transform():
                        b.set_func(node.transform)
                        add = True
                elif name == 'info':
                    b.set_args(args=[screens.info_menu, node])
                    add = True
                elif name == 'group':
                    add = [n for n in selected if not n.is_group() and n is not node]
                elif name == 'ungroup':
                    add = node.is_group()
                    if add:
                        b.set_args(args=[node])

            else:
                if name == 'paste':
                    add = self.ne.copy_data
                elif name == 'select_all':
                    add = True
                elif name == 'clean_up':
                    add = True
                    
            if name == 'select_all':
                add = True
                
            if add:
                b.rect.topleft = (x, y)
                self.add_child(b, current_offset=True)
                y += b.rect.height
            
    def close(self):
        self.rect.topleft = (-100, -100)
        for b in self.objects_dict.values():
            b.rect.topleft = self.rect.topleft

    def draw(self, surf):
        super().draw(surf)
        if self.is_open():
            for b in self.children[1:]:
                pg.draw.line(surf, (0, 0, 0), (b.rect.x + 5, b.rect.y - 1), (b.rect.right - 5, b.rect.y - 1), width=2)

#menu stuff--------------------------------------------------------------------

def run_data_sheet(ne):
    m = ui.Menu(get_objects=screens.data_sheet_menu, args=[ne])
    m.run()

#string sorting stuff-----------------------------------------------------------------------

def sort_strings(a, b):
    d = difflib.SequenceMatcher(None, a, b).ratio()
    d = -int(d * 100)
    return d

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
        self.drag_manager = ui.DraggerManager(self.nodes)

        self.objects_dict = {}
        ui.Menu.__init__(self, get_objects=self.editor_objects)
        
        self.anchor = None

        self.info_box = pg.Rect(0, 0, 100, 100)
        self.info_box.topright = (WIDTH, 0)
        self.info_node = None
        
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
        
        if self.card.node_data:
            self.load_save_data(self.card.node_data)
        
#visual stuff--------------------------------------------------------------------
        
    def editor_objects(self):
        objects = []

        buttons = []
        for name, obj in self.NODES.items():
            b = ui.Button.text_button(name, size=(100, 30), border_radius=0, func=self.get_node, args=[name], tsize=15)
            buttons.append(b)
        for name, data in self.GROUPS.items():
            b = ui.Button.text_button(name, size=(100, 30), border_radius=0, func=self.load_group_node, args=[name, data], tsize=15)
            buttons.append(b)

        sb = Search_Bar(buttons, (WIDTH, HEIGHT))
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
    
        b = ui.Button.text_button('group node', func=self.create_new_group_node, tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-1].rect.right + 5
        objects.append(b)
        
        b = ui.Button.text_button('ungroup node', func=self.ungroup_nodes, tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-1].rect.right + 5
        objects.append(b)
        
        b = ui.Button.text_button('data sheet', func=run_data_sheet, args=[self], tsize=15)
        b.rect.top = 5
        b.rect.left = objects[-1].rect.right + 5
        objects.append(b)
        
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
        self.info_box.topright = (WIDTH - 20, 20)
        
        b = ui.Button.text_button('See node info', func=self.check_info, tsize=15)
        b.rect.midtop = self.info_box.midbottom
        b.rect.y += 10
        objects.append(b)
        
        nm = Node_Menu(self)
        objects.append(nm)
        self.objects_dict['menu'] = nm
        
        cm = Context_Manager(self)
        objects.append(cm)
        self.objects_dict['context'] = cm

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
                    n.recall_port_mem()
                    n.reset_ports()
                    
            elif type == 'conn':
                p0, p1 = log['ports']
                self.disconnect(p0, p1, d=True)
                
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
                self.new_connection(p0, p1, force=True, d=True)
                
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
                self.disconnect(p0, p1, d=True)
                
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
                self.new_connection(p0, p1, d=True)
                
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
        breaks = 0
        a = self.anchor
        b = pg.mouse.get_pos()
        for w in self.wires.copy():
            if w.check_break(a, b):
                breaks += 1
        return breaks

#node management stuff--------------------------------------------------------------------

    def add_nodes(self, nodes):
        for n in nodes:
            self.add_node(n)

    def add_node(self, n, d=False):
        self.nodes.append(n)
        if not d:
            self.add_log({'t': 'add', 'node': n})
             
    def get_node(self, name, val=None, pos=None, held=True):
        if len(self.nodes) == 50:
            return
    
        if pos is None and held:
            pos = pg.mouse.get_pos()
        
        n = super().get_node(name, val=val, pos=pos)
        
        if held:
            n.start_held()
            
        self.add_node(n)
        return n
        
    def get_group_node(self, name, pos=None, held=True):
        data = self.GROUPS[name]
        
        if len(self.nodes) + len(data['nodes']) + 1 > 50:
            return
            
        if pos is None and held:
            pos = pg.mouse.get_pos()
        
        nodes = self.unpack(data)
        n = nodes[-1]
        
        if pos:
            n.rect.center = pos
            n.set_port_pos()
        if held:
            n.start_held()
  
        return n
        
    def make_group_node(self, nodes, name='group', pos=None):
        n = super().make_group_node(nodes, name=name, pos=pos)
        self.add_node(n)
        self.add_log({'t': 'gn', 'gn': n, 'nodes': nodes})
        return n

    def create_new_group_node(self):
        nodes = [n for n in self.get_selected() if not n.is_group()]
        if len(nodes) <= 1:
            return
        n = self.make_group_node(nodes)
        return n

    def ungroup_nodes(self):
        nodes = [n for n in self.get_selected() if n.is_group()]
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
        
    def copy_nodes(self, nodes=None):
        if nodes is None:
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

        save_group_node(gn)

#other stuff--------------------------------------------------------------------

    def spread(self):
        funcs = []
        for n in self.nodes:
            if n.visible:
                func = mapping.find_visible_chunk(n, [])
                if not any({set(o) == set(func) for o in funcs}):
                    funcs.append(func)

        for nodes in funcs:
            lead = mapping.find_lead(nodes)
            columns = mapping.map_flow(lead, nodes.copy(), {})
            columns = [columns[key][::-1] for key in sorted(columns)]
            
            x = WIDTH // 2
            y = HEIGHT // 2
            cy = y
            
            for col in columns:
                r = pg.Rect(0, 0, 0, 0)
                for n in col:
                    print(n, n.visible)
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
                y = HEIGHT // 2

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
                dist = n.get_carry_dist()
                if dist:
                    draggers[n] = dist
                n.drop()
                
            y += r.height + 20
            if y > HEIGHT - 100:
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
            m = ui.Menu(get_objects=screens.info_menu, args=[n], fill_color=(100, 0, 0))
            m.run()

#run stuff--------------------------------------------------------------------
    
    def exit(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(self.fps)
            self.events()
            self.update()
            self.draw()
            self.update_log()
            
    def events(self):
        hit = False
        dub = False
        click_up = False
        click_down = False
        open_context = False
        
        context_node = None
        
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
                breaks = self.check_wire_break()
                open_context = not breaks and ui.Line.distance(p, self.anchor) < 2
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
                if n.big_rect.collidepoint(p):
                    if mbd and not hit:
                        hit = True
                    elif mbu and not context_node:
                        context_node = n
                    
        if open_context:
            self.objects_dict['context'].open(p, context_node)
                    
        if click_up:
            self.close_active_node()
        
        hit = (super().sub_events(events) and mbd) or hit
                        
        if dub and not hit:
            self.objects_dict['search_bar'].open_search()
                
        elif click_down:
            self.objects_dict['context'].close()
            if not self.objects_dict['search_bar'].collide(p):
                self.objects_dict['search_bar'].close_search()
            if not self.objects_dict['menu'].collide(p):
                self.objects_dict['menu'].start_force_down()

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
            if ui.Line.distance(s, e) > 2:
                pg.draw.line(self.window, (0, 0, 255), s, e, width=4)
            
        if self.info_node:
            self.info_node.draw(self.window)
                
        pg.display.flip()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            