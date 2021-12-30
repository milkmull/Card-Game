import json
import difflib

import pygame as pg

import save
import allnodes
import tester
from ui import *
from ui import init as uinit
from constants import *

def init():
    g = globals()
    g['logs'] = []
    
#log stuff--------------------------------------------------------------------
    
def add_log(log):
    global logs
    logs.append(log)
    
def get_logs():
    global logs
    return_logs = logs.copy()
    logs.clear()
    return return_logs

#visual stuff-----------------------------------------------------------------------

def error_screen(errors):
    screen = []
    
    body = pg.Rect(0, 0, 500, 300)
    upper = pg.Rect(0, 0, 500, 250)
    lower = pg.Rect(0, 100, 500, 50)
    outline = pg.Rect(0, 0, body.width + 10, body.height + 10)
    
    s = pg.Surface(outline.size).convert()
    pg.draw.rect(s, (255, 255, 255), outline, border_radius=10)
    body.center = outline.center
    pg.draw.rect(s, (100, 100, 100), body, border_radius=10)
    lower.bottomleft = body.bottomleft
    pg.draw.rect(s, (50, 50, 50), lower, border_bottom_right_radius=10, border_bottom_left_radius=10)
    i = Image(s)
    i.rect.center = (width // 2, height // 2)
    screen.append(i)
    
    body.center = (width // 2, height // 2)
    upper.topleft = body.topleft
    lower.bottomleft = body.bottomleft
    
    num = len(errors)
    if num:
        text_rect = pg.Rect(0, 0, 200, 25)
        text_rect.center = upper.center
        
        if len(errors) < 6:
            message = f"{num} error{'s' if num > 1 else ''} found:"
        else:
            message = '5+ errors found:'
        
        t = Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25, centered=False)
        t.rect.topleft = upper.topleft
        t.rect.x += 10
        t.rect.y += 10
        screen.append(t)
        
        x = t.rect.left
        y = t.rect.bottom + 10
        text_rect = pg.Rect(0, 0, body.width, 30)
        
        for err in errors[:5]:
            t = Textbox(err, olcolor=(0, 0, 0))
            t.fit_text(text_rect, tsize=25, centered=False)
            t.rect.topleft = (x, y)
            screen.append(t)
            
            y += text_rect.height + 10
            rx = t.rect.left - i.rect.left
            ry = t.rect.top - i.rect.top
            pg.draw.line(i.image, (0, 0, 0), (rx, ry + t.rect.height + 5), (i.rect.width - rx, ry + t.rect.height + 5), width=2)

    else:
        text_rect = pg.Rect(0, 0, upper.width - 15, upper.height - 15)
        text_rect.center = upper.center
        message = 'all tests passed, no errors found!'
        t = Textbox(message, olcolor=(0, 0, 0))
        t.fit_text(text_rect, tsize=25)
        t.rect.center = text_rect.center
        screen.append(t)
    
    b = Button((200, 30), 'ok', color2=(0, 200, 0), tag='break')
    b.rect.center = lower.center
    screen.append(b)

    return screen

#string sorting stuff-----------------------------------------------------------------------

def sort_strings(a, b):
    d = difflib.SequenceMatcher(None, a, b).ratio()
    d = -int(d * 100)
    return d
    
#packing stuff----------------------------------------------------------------------

def sort_nodes(nodes):
    s = {'nodes': [], 'groups': []}
    for n in nodes:
        if n.is_group():
            s['groups'].append(n)
        else:
            s['nodes'].append(n)
    return s

def pack_data(nodes):
    nodes = sort_nodes(nodes) 
    save_data = {'nodes': {}, 'groups': {}}
    
    for n in nodes['nodes']:
        node_data = {}
        node_data['name'] = n.__class__.__name__
        node_data['pos'] = n.rect.center
        node_data['val'] = n.get_string_val()
        node_data['contains'] = getattr(n, 'contains', None)
        ports = {}
        for p in n.ports:
            port_data = {}
            port_data['connection'] = p.connection.id if p.connection else None
            port_data['connection_port'] = p.connection_port.port if p.connection_port else None
            port_data['parent_port'] = p.parent_port
            port_data['suppressed'] = p.suppressed
            port_data['visible'] = p.visible
            port_data['types'] = p.types
            ports[str(p.port)] = port_data
        node_data['ports'] = ports
        save_data['nodes'][str(n.id)] = node_data
        
    for g in nodes['groups']:
        group_data = {}
        group_data['pos'] = g.rect.center
        group_data['nodes'] = [n.id for n in g.nodes]
        group_data['rel_node_pos'] = g.rel_node_pos
        save_data['groups'][str(g.id)] = group_data
        
    return save_data
    
def unpack_data(save_data, copy=False):
    nodes = {}
    id_map = {}
 
    for id, d in save_data['nodes'].items():
        id = int(id)
        name = d['name']
        val = d['val']
        contains = d['contains']
        pos = d['pos']
        n = allnodes.get_node(name, id=id if not copy else None, val=val, pos=pos)
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n

    while True:
    
        missed = False
    
        for id, d in save_data['nodes'].items():
            id = id_map[int(id)]
            n0 = nodes[id]
            ports = d['ports']
            for port in ports:
                connection = ports[port]['connection']
                connection_port = ports[port]['connection_port']
                parent_port = ports[port]['parent_port']
                suppressed = ports[port]['suppressed']
                visible = ports[port]['visible']
                types = ports[port]['types']
                if parent_port is not None:
                    n0.new_output_port(n0.get_port(parent_port))
                port = int(port)
                p0 = n0.get_port(port)
                p0.set_types(types)
                p0.suppressed = suppressed
                p0.visible = visible
                p0.parent_port = parent_port
                if connection is not None and port < 0:
                    connection = id_map.get(connection)
                    if connection is not None:
                        n1 = nodes[connection]
                        p1 = n1.get_port(connection_port)
                        if p0 and p1:
                            p0.open_wire()
                            allnodes.connect(p0, p1, force=True)
                        else:
                            missed = True
                    
        if not missed:
            break

    for id, d in save_data['groups'].items():
        id = int(id)
        group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
        pos = d['pos']
        n = allnodes.get_node('GroupNode', nodes=group_nodes, id=id if not copy else None, pos=pos, held=copy)
        n.rel_node_pos = {id_map[int(rid)]: rp for rid, rp in d['rel_node_pos'].items()}
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        
    nodes = list(nodes.values())
    for n in nodes:
        n.prune_extra_ports()
        n.set_stuck(False)

    return nodes
  
#saving and loading stuff-----------------------------------------------------------------------

def save_progress(nodes):
    if not nodes:
        return   
    save_data = pack_data(nodes)
    with open('save/card.json', 'w') as f:
        json.dump(save_data, f, indent=4)
        
def load_progress():
    allnodes.reset()
    with open('save/card.json', 'r') as f:
        save_data = json.load(f) 
    nodes = unpack_data(save_data)
    allnodes.set_loaded_id()

def save_group_node(name, gn):
    nodes = gn.nodes.copy() + [gn]
    
    group_data = load_group_data()
    group_data[name] = pack_data(nodes)
    
    with open('save/group_nodes.json', 'w') as f:
        json.dump(group_data, f, indent=4)
    
def load_group_node(name, data):
    nodes = unpack_data(data, copy=True)
    nodes[-1].set_name(name)
    return nodes
    
def load_group_data():
    with open('save/group_nodes.json', 'r') as f:
        data = json.load(f)
    return data

#parsing stuff--------------------------------------------------------------------

def run_parser(nodes):
    np = Node_Parser(nodes)
    out = np.get_text()

    with open('new_card.py', 'w') as f:
        f.write(out)  
    with open('save/custom_cards.json', 'r') as f:
        cards = json.load(f)
    cards['test'] = {'weight': 5, 'init': 'Test', 'custom': True}
    with open('save/custom_cards.json', 'w') as f:
        json.dump(cards, f, indent=4)
          
class Node_Parser:
    def __init__(self, nodes):
        self.nodes = nodes
        self.start_node = next((n for n in self.nodes if n.name == 'start'), None)
        
        self.header = "from card_base import *\n\nclass Test(Card):\n\tdef __init__(self, game, uid):\n\t\tsuper().__init__(game, uid, 'test', tags=[])\n"
        self.dec_line = ''

        self.funcs = {}
        
        self.text = self.run().replace('\t', '    ')
        
    def get_text(self):
        return self.text
        
    def get_lines(self):
        return self.text.splitlines()
        
    def new_func(self, node):
        self.funcs[node.name] = {'header': '\t' + node.get_text(), 'start': '', 'dec': '', 'body': '', 'end': ''}
        
    def find_funcs(self):
        return [n for n in self.nodes if n.type == 'func']
        
    def check_errors(self):
        return [n.check_errors() for n in self.nodes]
        
    def run(self):
        if not self.start_node:
            return ''
            
        errors = self.check_errors()
        for e in errors[::-1]:
            if e:
                menu(notice, args=[e])
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
        ports = set(allnodes.map_ports(node, []))
        for p in ports:
            n = p.node
            if n.type == 'dec':
                line = n.get_dec()
                if line not in dec_line:
                    dec_line += (2 * '\t') + n.get_dec()
                
        return dec_line

    def parse_nodes(self, node, func=None, tabs=2):
        text = ''
        
        if node.type == 'func':
            self.new_func(node)
            func = node.name
            self.funcs[func]['start'] = node.get_start()
            self.funcs[func]['dec'] += self.find_locals(node)
            self.funcs[func]['end'] = node.get_end()
            tabs = 2
        else:
            out_text = node.get_text()
            if out_text:
                text = (tabs * '\t') + out_text
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
  
#testing stuff--------------------------------------------------------------------

def run_tester():
    t = tester.Tester()
    menu(loading_screen, kwargs={'message': 'testing card...'}, func=step_test, fargs=[t])
    t.process()
    messages = t.get_error_messages()
    #print(t.get_error_lines())
    menu(error_screen, args=[messages])
    #for err in messages:
    #    print(err)
        
def step_test(t):
    t.step_sim()
    return t.get_sims() == 100
    
def test_run():
    text = tester.test_run()
    if text:
        menu(notice, args=[text])
  
#copy and paste----------------------------------------------------------------------

def copy_nodes(nodes):
    data = pack_data(nodes)
    return data
    
def paste_nodes(data):
    if not data or len(allnodes.NODES) + len(data['nodes']) > 50:
        return
    nodes = unpack_data(data, copy=True)
    if nodes:
        move_nodes(nodes, pg.mouse.get_pos())
        for n in nodes:
            n.start_held() 
    return nodes
    
def move_nodes(nodes, c):
    left = min(n.rect.left for n in nodes)
    right = max(n.rect.right for n in nodes)
    top = min(n.rect.top for n in nodes)
    bottom = max(n.rect.bottom for n in nodes)
    r = pg.Rect(left, top, right - left, bottom - top)
    cx, cy = r.center
    r.center = c
    dx = r.centerx - cx
    dy = r.centery - cy
    
    for n in nodes:
        n.rect.move_ip(dx, dy)
        n.set_port_pos()

#sorting stuff-------------------------------------------------------------------------

def find_lead(nodes):
    lead = nodes[0]
    for n in nodes:
        for op in n.get_output_ports():
            if 'flow' in op.types:
                ips = n.get_input_ports()
                if not ips:
                    return n
                else:
                    for ip in ips:
                        if 'flow' in ip.types and not ip.connection:
                            return n
            elif not n.get_input_ports():
                lead = n
                
    return lead

def map_flow(n, nodes, columns, column=0):
    if column not in columns:
        columns[column] = [n]
    else:
        columns[column].append(n)
    nodes.remove(n)

    for ip in n.get_input_ports()[::-1]:
        if 'flow' not in ip.types and ip.connection:
            connected_node = ip.connection_port.get_visible_node()
            if connected_node in nodes:
                map_flow(connected_node, nodes, columns, column=column - 1)
                
    opp = n.get_output_ports()
    opp.sort(key=lambda p: p.get_true_port(), reverse=True)
    
    for op in opp[::-1]:
        if 'flow' in op.types and op.connection:
            connected_node = op.connection_port.get_visible_node()
            if connected_node in nodes:
                map_flow(connected_node, nodes, columns, column=column + 1)
            
    for op in opp:
        if 'flow' not in op.types and op.connection:
            connected_node = op.connection_port.get_visible_node()
            if connected_node in nodes:
                in_flow = connected_node.get_in_flow()
                if in_flow:
                    if in_flow.connection:
                        if in_flow.connection in nodes:
                            continue
                map_flow(connected_node, nodes, columns, column=column + 1)
            
    return columns

def spread(nodes):
    funcs = []
    for n in nodes:
        if n.visible:
            func = allnodes.find_chunck(n, [])
            if not any(set(o) == set(func) for o in funcs):
                funcs.append(func)

    for nodes in funcs:
        lead = find_lead(nodes)
        columns = map_flow(lead, nodes.copy(), {})
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
  
            x += max(n.rect.width for n in col) + 20
            y = height // 2

    draggers = {}

    x = 50
    y = 50
        
    for nodes in funcs:
        left = min(n.rect.left for n in nodes)
        right = max(n.rect.right for n in nodes)
        top = min(n.rect.top for n in nodes)
        bottom = max(n.rect.bottom for n in nodes)
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
        add_log({'t': 'carry', 'draggers': draggers})

#info screen-----------------------------------------------------------------------------

def info_menu(n):
    screen = []
    n = type(n)(-1)
    
    title = Textbox(n.name, tsize=35)
    title.rect.topleft = (30, 20)
    screen.append(title)
    
    info_rect = pg.Rect(0, 0, 400, 200)
    info_surf = pg.Surface(info_rect.size).convert()
    pg.draw.rect(info_surf, (255, 255, 255), info_rect, width=3, border_radius=10)
    info_rect.topleft = (30, 150)
    i = Image(info_surf)
    i.rect = info_rect.copy()
    screen.append(i)
    
    label = Textbox('info:', tsize=20)
    label.rect.bottomleft = info_rect.topleft
    label.rect.x += 10
    label.rect.y -= 5
    screen.append(label)
    
    node_info = Textbox(n.info)
    node_info.fit_text(info_rect.inflate(-10, -10), tsize=20, centered=False)
    node_info.rect.center = info_rect.center
    
    if hasattr(n, 'tips'):
    
        node_tips = Textbox(n.tips)
        node_tips.fit_text(info_rect.inflate(-10, -10), tsize=20, centered=False)
        node_tips.rect.center = info_rect.center
        
        node_text = Image(node_info.image)
        node_text.rect.center = info_rect.center
        screen.append(node_text)
        
        def update_info():
            if label.get_message() == 'info:':
                label.update_message('tips:')
                node_text.image = node_tips.image
            else:
                label.update_message('info:')
                node_text.image = node_info.image
                
        b = Button((40, 40), '>', func=update_info, border_radius=20)
        b.rect.midleft = info_rect.midright
        screen.append(b)
    
    else:
        screen.append(node_info)

    port_rect = pg.Rect(0, 0, 300, 200)
    w, h = port_rect.size
    port_surf = pg.Surface(port_rect.size).convert()
    port_surf.fill((1, 1, 1))
    port_info_rect = pg.Rect(5, 20, w - 10, h - 25)
    pg.draw.rect(port_surf, (0, 0, 0), port_info_rect)
    port_surf.set_colorkey((1, 1, 1))
    port_box = Image(port_surf, bgcolor=(100, 100, 100))
    port_box.rect = port_rect.copy()
    port_box.rect.topleft = (650, 100)
    screen.append(port_box)
    
    port_label_rect = pg.Rect(0, 0, w, 20)
    port_label_rect.midtop = port_box.rect.midtop
    port_info_rect.midtop = port_label_rect.midbottom
    port_info_rect.inflate_ip(-10, -5)

    port_data = []
    port_index = [0]
    for p in n.ports:
        info_text = getattr(n, f"{'ip' if p.port > 0 else 'op'}{abs(p.port)}", '')
        if not info_text:
            continue
        data = {'port': p, 'color': allnodes.get_color(p.types)}
        p_label = Textbox(f'Port {p.port}', fgcolor=(0, 0, 0))
        p_label.fit_text(port_label_rect, tsize=20, centered=False)
        data['label'] = p_label.image
        p_info = Textbox(info_text)
        p_info.fit_text(port_info_rect, tsize=15, centered=False)
        data['info'] = p_info.image
        port_data.append(data)

    n.rect.midtop = port_box.rect.midbottom
    n.rect.y += 100
    n.set_port_pos()
    screen.append(n)
        
    if port_data:
        
        port_label = Image(port_data[0]['label'])
        port_label.rect.center = port_label_rect.center
        port_label.rect.x += 5
        screen.append(port_label)
        port_info = Image(port_data[0]['info'])
        port_info.rect.center = port_info_rect.center
        screen.append(port_info)
        port_box.set_background(port_data[0]['color'])

        def update_points(port):
            start = port.rect.center
            end = port_box.rect.midbottom
            
            xs, ys = start
            xe, ye = end
            
            if port.port > 0:
                return (start, (xs - 20, ys), (xs - 20, n.rect.top - 50), (port_box.rect.centerx, n.rect.top - 50), end)
            else:
                return (start, (xs + 20, ys), (xs + 20, n.rect.top - 50), (port_box.rect.centerx, n.rect.top - 50), end)
                
        points = update_points(port_data[0]['port'])
        o = Draw_Lines(points, color=port_data[0]['color'])
        screen.append(o)
        
        if len(port_data) > 1:
        
            def update_port_info(port_index, dir=None, i=None):
                if i is None:
                    port_index[0] = (port_index[0] + dir) % len(port_data)
                else:
                    port_index[0] = i
                data = port_data[port_index[0]]
                port_label.image = data['label']
                port_info.image = data['info']
                port_box.set_background(data['color'])
                o.set_color(data['color'])
                o.set_points(update_points(data['port']))
                
            b = Button((40, 40), '>', func=update_port_info, args=[port_index], kwargs={'dir': 1}, border_radius=20)
            b.rect.midleft = port_box.rect.midright
            screen.append(b)
            b = Button((40, 40), '<', func=update_port_info, args=[port_index], kwargs={'dir': -1}, border_radius=20)
            b.rect.midright = port_box.rect.midleft
            screen.append(b)
            
            for i, pd in enumerate(port_data):
                r = pd['port'].rect
                b = Button(r.size, '', func=update_port_info, args=[port_index], kwargs={'i': i})
                b.rect.center = r.center
                screen.insert(0, b)
                
    else:
        screen.pop(-2)

    b = Button((200, 30), 'back', color2=(0, 200, 0), tag='break')
    b.rect.centerx = width // 2
    b.rect.bottom = height - 10
    screen.append(b)
    
    return screen

#node editor--------------------------------------------------------------------------

class Node_Editor:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()
        
        self.camera = self.screen.get_rect()
        self.offset = [0, 0]

        self.nodes = allnodes.NODES
        self.wires = allnodes.WIRES
        
        self.anchor = None
        
        self.elements = self.set_screen()
        self.info_box = pg.Rect(0, 0, 100, 100)
        self.info_box.topright = (width, 0)
        self.info_node = None
        self.drag_manager = DraggerManager(self.nodes)
        
        self.logs = []
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
        
#visual stuff--------------------------------------------------------------------
        
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

        for name, data in load_group_data().items():
            b = Button((100, 20), name, border_radius=0)
            b.set_func(load_group_node, args=[name, data])
            buttons.append(b)
        screen += buttons
        
        p = Pane((100, 200), color=(0, 0, 0), live=True)
        p.rect.topleft = i.rect.bottomright
        p.join_objects(buttons, xpad=0, ypad=0)
        p.update()
        screen.append(p)
        self.search_window = p

        b = Button((100, 20), 'save', func=save_progress, args=[self.nodes])
        b.rect.topleft = (5, 5)
        screen.append(b)
   
        b = Button((100, 20), 'test', func=run_tester)
        b.rect.topleft = screen[-1].rect.bottomleft
        b.rect.top += 5
        screen.append(b)
        
        b = Button((100, 20), 'test game', func=test_run)
        b.rect.topleft = screen[-1].rect.bottomleft
        b.rect.top += 5
        screen.append(b)
        
        b = Button((100, 20), 'load', func=load_progress)
        b.rect.top = 5
        b.rect.left = screen[-2].rect.right + 5
        screen.append(b)
    
        b = Button((100, 20), 'group node', func=self.make_group_node)
        b.rect.top = 5
        b.rect.left = screen[-1].rect.right + 5
        screen.append(b)
        
        b = Button((100, 20), 'ungroup node', func=self.ungroup_node)
        b.rect.top = 5
        b.rect.left = screen[-1].rect.right + 5
        screen.append(b)
        
        nc = Input((50, 20))
        nc.rect.bottomleft = (width, 0)
        screen.append(nc)
        self.numeric_control = nc
        
        group_name = Input((100, 20), tsize=20)
        group_name.rect.topleft = screen[-4].rect.bottomleft
        group_name.rect.y += 5
        screen.append(group_name)
        self.group_name = group_name
        
        b = Button((100, 20), 'save group node', func=self.save_group_node)
        b.rect.midleft = screen[-1].rect.midright
        b.rect.x -= 5
        b.rect.y += 5
        screen.append(b)
        
        self.info_box = pg.Rect(0, 0, 50, 50)
        self.info_box.topright = (width - 20, 20)
        
        b = Button((100, 20), 'See node info', func=self.check_info)
        b.rect.midtop = self.info_box.midbottom
        b.rect.y += 10
        screen.append(b)

        return screen
        
#log stuff--------------------------------------------------------------------

    def update_log(self):
        new_logs = []
        carry_log = self.drag_manager.get_next_log()
        if carry_log:
            new_logs.append(carry_log)
        new_logs += get_logs()
        new_logs += allnodes.get_logs()
        if new_logs:

            if self.log_index == -1:
                self.logs.clear()

            if self.log_index == 14:
                self.logs = self.logs[1:]
            else:
                if self.log_index > -1:
                    self.logs = self.logs[:self.log_index + 1]
                else:
                    self.logs.clear()
                self.log_index += 1
                
            self.logs.append(new_logs)
            
            print('d', new_logs)

#undo/redo--------------------------------------------------------------------

    def undo_log(self):
        if not self.logs or self.log_index == -1:
            return
            
        logs = self.logs[self.log_index]
        
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
                    n.delete(d=True)
                else:
                    n.ungroup(d=True)
                    
            elif type == 'del':
                n = log['node']
                m = log['m']
                allnodes.add_node(n) 
                if m == 'ug':
                    n.reset_ports()
                    
            elif type == 'conn':
                p0, p1 = log['ports']
                allnodes.disconnect(p0, p1, d=True)
                
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
                allnodes.connect(p0, p1, force=True, d=True)
                
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
                
        self.log_index -= 1
        
    def redo_log(self):
        if not self.logs or self.log_index == len(self.logs) - 1:
            return
            
        logs = self.logs[self.log_index + 1]
        
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
                    n.ungroup(d=True)
                else:
                    n.delete(d=True)   
                    
            elif type == 'add':
                n = log['node']
                allnodes.add_node(n)
                if n.is_group():
                    n.reset_ports()
                    
            elif type == 'disconn':
                p0, p1 = log['ports']
                allnodes.disconnect(p0, p1, d=True)
                
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
                allnodes.connect(p0, p1, d=True)
                
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
                
        self.log_index += 1

#search stuff--------------------------------------------------------------------
     
    def search(self):
        m = self.search_bar.get_message()
        key = lambda b: sort_strings(m, b.get_message())
        self.search_window.sort_objects(key)
       
    def open_search(self, p):
        self.search_bar.rect.center = p
        self.search_window.rect.topleft = self.search_bar.rect.bottomleft
        self.search_window.rect.y += 5
        self.search_bar.events(self.input)
        self.search_bar.highlight_full()
       
    def close_search(self):
        self.search_bar.close()
        self.search_bar.rect.bottomleft = (width, 0)
        self.search_window.rect.topleft = self.search_bar.rect.bottomright

#controls stuff--------------------------------------------------------------------
        
    def check_wire_break(self):
        a = self.anchor
        b = pg.mouse.get_pos()
        
        for w in self.wires.copy():
            w.check_break(a, b)

#node stuff--------------------------------------------------------------------
            
    def get_selected(self):
        return [n for n in self.drag_manager.get_selected() if n.visible]
        
    def copy_nodes(self):
        nodes = self.get_selected()
        for n in nodes.copy():
            if n.is_group():
                nodes += n.nodes
        self.copy_data = copy_nodes(nodes)
            
    def make_group_node(self):
        nodes = [n for n in self.get_selected() if not n.is_group()]
        if len(nodes) > 1:
            gn = allnodes.get_node('GroupNode', nodes=nodes, held=False)
            if gn:
                add_log({'t': 'gn', 'gn': gn, 'nodes': nodes})
                return gn
        
    def ungroup_node(self):
        nodes = [n for n in self.get_selected() if n.is_group()]
        if nodes:
            for n in nodes:
                n.ungroup()
                add_log({'t': 'ug', 'gn': n, 'nodes': n.nodes})
                
    def save_group_node(self):
        gn = None
        for n in self.nodes:
            if n.is_group():
                gn = n
                break
        else:
            return
            
        name = self.group_name.get_message()
        save_group_node(name, gn)

    def delete_nodes(self):
        nodes = self.get_selected()
        for n in nodes:
            n.delete()

    def check_info(self):
        info_node = None
        for n in self.nodes:
            if n.rect.colliderect(self.info_box):
                info_node = n
                break
        if info_node:
            menu(info_menu, args=[n])

#run stuff--------------------------------------------------------------------

    def run(self):
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
        p = pg.mouse.get_pos()
        self.input = pg.event.get()

        for e in self.input:
            
            if e.type == pg.QUIT:
                quit()       
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    quit()
                    
                elif (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    self.ctrl = True                  
                elif e.key == pg.K_c:
                    self.copy = True
                elif e.key == pg.K_v:
                    self.paste = True
                elif e.key == pg.K_s:
                    self.sort = True
                elif e.key == pg.K_z:
                    self.undo = True
                elif e.key == pg.K_y:
                    self.redo = True
                    
                elif e.key == pg.K_DELETE:
                    self.delete_nodes()
                    
                elif e.key == pg.K_p:
                    run_parser(self.nodes)

            elif e.type == pg.KEYUP:
                if (e.key == pg.K_RCTRL) or (e.key == pg.K_LCTRL):
                    self.ctrl = False
                elif e.key == pg.K_c:
                    self.copy = False
                elif e.key == pg.K_v:
                    self.paste = False
                elif e.key == pg.K_s:
                    self.sort = False
                elif e.key == pg.K_z:
                    self.undo = False
                elif e.key == pg.K_y:
                    self.redo = False

            elif e.type == pg.MOUSEBUTTONDOWN:
            
                if e.button == 1:
                    click_down = True
                    if self.ctimer > 10:
                        self.ctimer = 0
                    elif not self.search_bar.active:
                        dub = True
                        
                elif e.button == 3:
                    self.anchor = pg.mouse.get_pos()
  
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    click_up = True
                elif e.button == 3:
                    self.check_wire_break()
                    self.anchor = None
                    
        if self.ctrl:     
            if self.copy:
                self.copy_nodes()
                self.copy = False
            elif self.paste:
                paste_nodes(self.copy_data)
                self.paste = False
            elif self.sort:
                spread(self.nodes)
                self.sort = False
            elif self.undo:
                self.undo_log()
                self.undo = False
            elif self.redo:
                self.redo_log()
                self.redo = False

        for n in self.nodes[::-1]:
            if n.visible:
                n.events(self.input)
                if not hit and n.big_rect.collidepoint(p):
                    hit = True
                    
        if click_up:
            allnodes.close_active_node()
        
        for e in self.elements:
            if hasattr(e, 'events'):
                e.events(self.input)
                if not hit:
                    if e.rect.collidepoint(p):
                        hit = True

        self.drag_manager.events(self.input)

        if allnodes.get_active_node():
            self.drag_manager.cancel()
                        
        if dub and not hit:
            self.open_search(p)
                
        if not self.search_bar.active:
            self.close_search()
            
    def update(self):            
        if self.search_bar.active:
            self.search()
            
        for e in self.elements:
            if hasattr(e, 'update'):
                e.update()
        self.drag_manager.update()

        for n in self.nodes:
            if n.visible:
                n.update()

        for w in self.wires:
            w.update()
            
        if self.ctimer < 20:
            self.ctimer += 1
                
    def draw(self):
        self.screen.fill((0, 0, 0))
 
        for e in self.elements:
            if hasattr(e, 'draw'):
                e.draw(self.screen)
        self.drag_manager.draw(self.screen)
        
        for n in self.nodes:
            if n.visible:
                n.draw(self.screen)
            
        for w in self.wires:
            w.draw(self.screen)
            
        n = allnodes.get_active_node()
        if n:
            n.draw_wire(self.screen)
            
        if self.anchor:
            s = self.anchor
            e = pg.mouse.get_pos()
            pg.draw.line(self.screen, (0, 0, 255), s, e, width=4)
            
        if self.info_node:
            self.info_node.draw(self.screen)
                
        pg.display.flip()
        
if __name__ == '__main__':

    pg.init()
    pg.display.set_mode((width, height))
    
    init()
    
    allnodes.init()
    tester.init()
    uinit()
    
    #menu(info_menu, args=[allnodes.Deploy(0)])
    
    ne = Node_Editor()
    ne.run()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            