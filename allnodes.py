import json

import pygame as pg

from constants import *
import mapping
import ui

def get_nodes():
    NODES = {}
    for k, v in globals().items():
        if getattr(v, 'isnode', False) and not (hasattr(v, 'base') or v is Node or v is GroupNode):
            NODES[k] = v    
    return NODES

def get_groups():
    with open('data/group_nodes.json', 'r') as f:
        GROUPS = json.load(f)
    return GROUPS

class Wire:
    @staticmethod
    def get_dashed_line(points, step=3):
        dashed_points = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            x0, y0 = p0
            x1, y1 = p1
            
            if y0 == y1:
                y = y0
                if x0 > x1:
                    s = -step
                else:
                    s = step
                for x in range(x0, x1, s):
                    dashed_points.append((x, y))
            elif x0 == x1:
                x = x0
                if y0 > y1:
                    s = -step
                else:
                    s = step
                for y in range(y0, y1, s):
                    dashed_points.append((x, y))
        return dashed_points

    def __init__(self, p0, p1):
        if p0.port < 0:
            self.op = p0
            self.ip = p1
        else:
            self.op = p1
            self.ip = p0
        self.op.wire = self
        self.ip.wire = self

        self.points = self.find_points()

        self.bad = False
        self.dashed_points = Wire.get_dashed_line(self.points)
        
        self.last_pos_out = self.op.rect.center
        self.last_pos_in = self.ip.rect.center
        
    @property
    def manager(self):
        return self.op.manager
        
    def check_intersect(self, a, b):
        for i in range(len(self.points) - 1):
            c = self.points[i]
            d = self.points[i + 1]
            
            if ui.Line.intersect(a, b, c, d):
                return True
                    
    def check_break(self, a, b):
        if self.op.visible:
            if self.check_intersect(a, b):
                self.op.clear()
                return True
                
    def is_bad(self):
        onode = self.op.node
        in_flow = onode.get_in_flow()
        if in_flow:
            if not in_flow.connection:
                return True
            else:
                return in_flow.wire.is_bad()
                
    def clip(self):
        self.manager.del_wire(self)
        
    def find_points(self): 
        onode = self.op.get_visible_node()
        inode = self.ip.get_visible_node()
        
        start = self.op.rect.center
        end = self.ip.rect.center
        
        ox, oy = start
        ix, iy = end
        
        do = -self.op.port
        di = self.ip.port
        if self.op.parent_port:
            do = di = 1
            
        do = di = 0

        if onode.rect.right < inode.rect.left:
            cx = (onode.rect.right + inode.rect.left) // 2
        else:
            cx = (inode.rect.right + onode.rect.left) // 2
        if onode.rect.bottom < inode.rect.top:
            cy = (onode.rect.bottom + inode.rect.top) // 2
        else:
            cy = (inode.rect.bottom + onode.rect.top) // 2

        if ix - 10 < ox:
                 
            r = onode.rect.union(inode.rect)

            orect = onode.rect
            irect = inode.rect
            
            oshift = 8
            ishift = 8
           
            xmax = orect.right + oshift

            if r.height - 5 > orect.height + irect.height:
                xmin = irect.left - ishift
                midy = cy + ((do - 1) * 5)
                return (start, (xmax, oy), (xmax, midy), (xmin, midy), (xmin, iy), end)
                
            else:

                if orect.right > irect.left:
                    if orect.left < irect.left:
                        xmin = orect.left - oshift
                    else:
                        xmin = irect.left - ishift
                else:
                    xmin = orect.left - oshift
            
                if irect.top == r.top:
                    ymax = r.bottom + oshift
                    return (start, (xmax, oy), (xmax, ymax), (xmin, ymax), (xmin, iy), end)
                else:
                    ymin = r.top - oshift
                    return (start, (xmax, oy), (xmax, ymin), (xmin, ymin), (xmin, iy), end)

        else:
            if oy < iy:
                midx = cx - ((do - 1) * 5)
            else:
                midx = cx + ((do - 1) * 5)
            return (start, (midx, oy), (midx, iy), end)
        
    def update(self):
        update_points = False
            
        bad = self.is_bad()
        if self.bad != bad:
            self.bad = bad
            self.update_points = True

        current_pos_out = self.op.rect.center
        current_pos_in = self.ip.rect.center
        if update_points or (self.last_pos_out != current_pos_out or self.last_pos_in != current_pos_in):
            self.points = self.find_points()
            self.dashed_points = Wire.get_dashed_line(self.points)
        self.last_pos_out = current_pos_out
        self.last_pos_in = current_pos_in

    def draw(self, surf):
        if self.op.visible and self.ip.visible:
            c = Port.get_color(self.op.types)
            if not self.bad:
                pg.draw.lines(surf, c, False, self.points, width=3)
                
            else:
                for i in range(0, len(self.dashed_points) - 1, 2):
                    p0 = self.dashed_points[i]
                    p1 = self.dashed_points[i + 1]
                    pg.draw.line(surf, c, p0, p1, width=3)

class Port:
    comparison_types = ['bool', 'num', 'string', 'ps', 'cs', 'ns', 'bs', 'player', 'card']
    desc_cache = {}
    
    @classmethod
    def get_comparison_types(cls):
        return cls.comparison_types.copy()
        
    @classmethod
    def get_desc(cls, desc):
        if desc not in cls.desc_cache:
            cls.desc_cache[desc] = ui.Textbox(desc, tsize=15, bgcolor=(0, 0, 0))
        return cls.desc_cache[desc]
        
    @staticmethod
    def new_connection(p0, p1, force=False, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if (any({t in p1.types for t in p0.types}) or force) and p0.is_output() != p1.is_output():
        
            p0.connect(n1, p1)
            p1.connect(n0, p0)
            
            local_funcs, scope_output, loop_output = mapping.check_bad_connection(n0, n1)
            can_connect0 = n0.can_connect(p0, n1, p1)
            can_connect1 = n1.can_connect(p1, n0, p0)
            if not can_connect0 or not can_connect1 or (len(local_funcs) > 1 or scope_output or loop_output):
                p0.clear()
                p1.clear()
                
            else:
                p0.manager.new_wire(p0, p1)
                if hasattr(n0, 'on_connect'):
                    n0.on_connect(p0)
                if hasattr(n1, 'on_connect'):
                    n1.on_connect(p1) 
                if not d:
                    p0.manager.add_log({'t': 'conn', 'nodes': (n0, n1), 'ports': (p0, p1)})

        p0.close_wire()
        p1.close_wire()
        n0.prune_extra_ports()
        n1.prune_extra_ports()
    
    @staticmethod
    def disconnect(p0, p1, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if not d:
            p0.manager.add_log({'t': 'disconn', 'ports': (p0, p1), 'nodes': (n0, n1)})
            
        if p0.wire:
            p0.wire.clip()
        if p1.wire:
            p1.wire.clip()
            
        p0.connection = None
        p0.connection_port = None
        p0.wire = None
        if p0.parent_port:
            n0.prune_extra_ports()
        
        p1.connection = None
        p1.connection_port = None
        p1.wire = None
        if p1.parent_port:
            n1.prune_extra_ports()
            
#color stuff-------------------------------------------------------------------
        
    @staticmethod
    def get_color(types):
        if not types:
            return (0, 0, 0)
        main_type = types[0]
        if main_type == 'bool':
            return (255, 255, 0)
        elif main_type == 'player':
            return (255, 0, 0)
        elif main_type in ('cs', 'ps', 'ns', 'bs'):
            return (0, 255, 0)
        elif main_type == 'log':
            return (255, 128, 0)
        elif main_type == 'num':
            return (0, 0, 255)
        elif main_type == 'string':
            return (255, 0, 255)
        elif main_type == 'card':
            return (145, 30, 180)
        elif main_type == 'split':
            return (128, 128, 128)
        elif main_type == 'flow':
            return (255, 255, 255)
        else:
            return (100, 100, 100)
     
    @staticmethod
    def get_contains_color(types):
        if 'ps' in types and 'cs' in types:
            return (0, 255, 0)
        elif 'ps' in types:
            return (255, 0, 0)
        elif 'cs' in types:
            return (145, 30, 180)
        elif 'ns' in types:
            return (0, 0, 255)
        elif 'bs' in types:
            return (255, 255, 0)
        else:
            return (0, 255, 0)
   
    def __init__(self, port, types, desc=None):
        self.port = port
        self.types = types
     
        self.parent_port = None
        self.node = None
        self.offset = None
                
        self.connection = None
        self.connection_port = None
        
        self.wire = None
        
        self.live_wire = False
        self.visible = True
        self.suppressed = False
        
        self.rect = pg.Rect(0, 0, 10, 10)

        if not desc and not self.types:
            desc = ''
        elif not desc:
            desc = self.types[0]
        self.desc = Port.get_desc(desc)
        
    def __str__(self):
        return f"{self.port}: name: {getattr(self.connection, 'name', None)}, id: {getattr(self.connection, 'id', None)}"
        
    def __repr__(self):
        return str(self)
        
    @property
    def manager(self):
        return self.node.manager
        
    @property
    def group_node(self):
        return self.node.group_node

    def get_parent(self):
        if self.group_node:
            return self.group_node
        return self.node
        
    def copy(self):
        n = self.node
        port = min({p.port for p in n.get_output_ports()}) - 1
        types = self.types
        p = Port(port, types)
        p.parent_port = self.port
        p.node = self.node
        p.rect = self.rect.copy()
        p.desc = self.desc
        p.open_wire()
        n.ports.append(p)
        if self.group_node:
            if self in self.group_node.ports:
                self.group_node.ports.append(p)
        p.offset = (self.offset[0], self.offset[1])
        return p
        
#position stuff---------------------------------------------------------------
        
    def set_offset(self):
        r = self.get_parent().rect
        dx = self.rect.x - r.x
        dy = self.rect.y - r.y
        self.offset = (dx, dy)
        
    def update_position(self):
        r = self.get_parent().rect
        dx, dy = self.offset
        self.rect.x = r.x + dx
        self.rect.y = r.y + dy

#visibility stuff-------------------------------------------------------------------

    def is_visible(self):
        return self.visible
        
    def set_visibility(self, visible):
        self.visible = visible
        
    def set_suppressed(self, suppressed, d=False):
        if self.suppressed != suppressed:
            if not self.suppressed:
                self.clear()
            self.suppressed = suppressed
            if not d:
                self.manager.add_log({'t': 'suppress', 's': suppressed, 'p': self})
         
    def get_visible_node(self):
        if self.group_node:
            return self.group_node
        return self.node

    def get_parent_port(self):
        if self.parent_port is not None:
            n = self.node
            pp = n.get_port(self.parent_port)
            return pp
            
    def get_true_port(self):
        if self.parent_port:
            return self.parent_port
        return self.port
        
#type stuff-------------------------------------------------------------------
        
    def set_types(self, types):
        self.types = types
        
    def add_type(self, type):
        self.types.append(type)
        
    def remove_type(self, type):
        if type in self.types:
            self.types.remove(type)
            
    def clear_types(self):
        self.types.clear()
        self.clear()
        
    def get_contains(self):
        contains = [t for t in self.types if t in ('ps', 'cs', 'ns', 'bs')]
        if contains:
            if self.port < 0 or len(contains) == 1:
                t = contains[0]
            else:
                return
               
            if t == 'ps':
                return 'player'
            elif t == 'cs':
                return 'card'
            elif t == 'ns':
                return 'num'
            elif t == 'bs':
                return 'bool'

#connection stuff-------------------------------------------------------------------

    def connect(self, connection, connection_port):
        self.set_suppressed(False)
        self.connection = connection_port.node
        self.connection_port = connection_port
        
    def clear(self):
        if self.connection:
            p0 = self
            p1 = self.connection_port
            Port.disconnect(p0, p1)

    def is_open(self):
        return self.connection is None

    def open_wire(self):
        self.set_suppressed(False)
        self.live_wire = True
        
    def close_wire(self):
        self.live_wire = False
        
    def is_output(self):
        return self.port < 0
        
    def is_input(self):
        return self.port > 0

    def draw(self, surf):
        if self.visible and not self.parent_port:
        
            if not self.suppressed:
                r = self.rect.width // 2
            else:
                r = 3
            pg.draw.circle(surf, Port.get_color(self.types), self.rect.center, r)
            
            if not self.suppressed:
                contains = self.get_contains()
                if contains:
                    pg.draw.circle(surf, Port.get_contains_color(self.types), self.rect.center, r - 2)
                    
            if self.rect.collidepoint(pg.mouse.get_pos()):
                r = self.get_parent().rect
                self.desc.rect.centerx = self.rect.centerx
                self.desc.rect.y = r.bottom + 5
                self.desc.draw(surf)

class Node(ui.Dragger, ui.Base_Object, ui.Position):
    isnode = True
    IMAGE_CACHE = {}
    LABEL_CACHE = {}
    RAW_CACHE = {}
    
    @classmethod
    def set_raw(cls, nodes):
        for name, node in nodes.items():
            img = node.get_raw_image()
            cls.RAW_CACHE[name] = img

    @classmethod
    def get_image(cls, node):
        size = node.size
        if node.type == 'func':
            color = (100, 255, 100)
        elif node.is_group():
            color = (255, 100, 100)
        elif node.is_flow():
            color = (100, 100, 255)
        else:
            color = (100, 100, 100)

        if size not in cls.IMAGE_CACHE:
            cls.IMAGE_CACHE[size] = {}
        image = cls.IMAGE_CACHE[size].get(color)
        if not image:
            image = pg.Surface(node.size).convert()
            image.fill(color) 
            cls.IMAGE_CACHE[size][color] = image
            
        return image
        
    @classmethod
    def get_label(cls, node):
        label = cls.LABEL_CACHE.get(node.name)
        if not label:
        
            if node.type == 'func':
                tcolor = (0, 0, 0)
            elif node.is_group():
                tcolor = (0, 0, 0)
            elif node.is_flow():
                tcolor = (0, 0, 0)
            else:
                tcolor = (255, 255, 255)

            label = ui.Textbox(node.get_name(), tsize=20, fgcolor=tcolor)
            w, h = node.image.get_size()
            r = pg.Rect(0, 0, w - 5, h - 5)
            r.center = node.image.get_rect().center
            label.fit_text(r)
            
            label = label.get_image()
            cls.LABEL_CACHE[node.name] = label
            
        label = ui.Image(label)  
        return label

    def __init__(self, manager, id, ports, pos=(width // 2, height // 2), val=None, type=None, color=(100, 100, 100)):
        ui.Base_Object.__init__(self)
        ui.Position.__init__(self)
        
        self.manager = manager
        self.id = id
        self.type = type
        self.val = val
        self.group_node = None

        self.ports = ports
        if not self.is_group():
            for p in self.ports:
                p.node = self

        self.ctimer = 0
        self.visible = True

        self.image = Node.get_image(self)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.big_rect = pg.Rect(0, 0, self.rect.width + 10, self.rect.height + 10)
        self.big_rect.center = self.rect.center

        self.objects_dict = {}
        self.objects = self.get_objects()

        ui.Dragger.__init__(self)
        self.set_port_pos()
 
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    @property
    def name(self):
        return type(self).__name__
        
    def get_name(self):
        return self.name.replace('_', ' ')
        
    @property
    def size(self):
        w = 50 if not self.is_group() else 75
        h = 50 if not self.is_group() else 75
        ports = max({len(self.get_output_ports()), len(self.get_input_ports())})
        if ports > 3:
            h += (10 * ports)
        return (w, h)
        
    def copy(self):
        return self.manager.get_node(self.name)
        
    def is_group(self):
        return isinstance(self, GroupNode)
        
    def is_input(self):
        return 'input' in self.objects_dict
        
    def is_flow(self):
        return any({'flow' in p.types for p in self.ports})

    def can_transform(self):
        return hasattr(self, 'tf')
        
#image and element stuff-------------------------------------------------------------------

    def set_visibility(self, visible):
        self.visible = visible
        
    def get_raw_image(self):
        w, h = self.rect.size
        surf = pg.Surface((w + 10, h)).convert_alpha()
        surf.fill((0, 0, 0, 0))
        self.rect.topleft = (5, 0)
        self.update_position(all=True)
        self.draw_on(surf, surf.get_rect())
        return surf

    def get_objects(self):
        label = Node.get_label(self)
        label.rect.center = self.rect.center
        self.add_child(label, set_parent=True, current_offset=True)
        self.objects_dict['label'] = label
        return [label]

    def get_string_val(self):
        input = self.objects_dict.get('input')
        if input:
            return input.get_message()
            
    def set_port_pos(self):
        ip = self.get_input_ports()
        op = self.get_output_ports()
        ex = []
        for p in op.copy():
            if p.parent_port:
                op.remove(p)
                ex.append(p)
        
        h = self.rect.height
        
        step = h // (len(ip) + 1)
        for i, y in enumerate(range(self.rect.top + step, self.rect.bottom, step)):
            if i in range(len(ip)):
                ip[i].rect.center = (self.rect.x, y)
                ip[i].set_offset()
            
        step = h // (len(op) + 1)
        for i, y in enumerate(range(self.rect.top + step, self.rect.bottom, step)):
            if i in range(len(op)):
                op[i].rect.center = (self.rect.right, y)
                op[i].set_offset()
                
        for ep in ex:
            ep.rect.center = ep.get_parent_port().rect.center
            ep.set_offset()

        self.big_rect.center = self.rect.center

#writing stuff----------------------------------------------------------------------

    def get_text(self):
        return ''
        
    def get_output(self, p):
        return ''
        
    def get_dec(self):
        return ''
        
    def get_default(self, p):
        return ''
        
    def get_start(self):
        return ''
        
    def get_end(self):
        return ''
        
    def get_input(self):
        input = []
        
        for ip in self.get_input_ports():
            if ip.connection:
                if ip.connection_port.parent_port:
                    input.append(ip.connection.get_output(ip.connection_port.parent_port))
                else:
                    input.append(ip.connection.get_output(ip.connection_port.port))
            else:
                input.append(self.get_default(ip.port))
                
        return input

    def check_errors(self):
        return ''
        
    def get_input_from(self, p):
        ip = self.get_port(p)
        if ip.connection:
            if ip.connection_port.parent_port:
                return ip.connection.get_output(ip.connection_port.parent_port)
            else:
                return ip.connection.get_output(ip.connection_port.port)
        return self.get_default(ip.port)
     
#port stuff-------------------------------------------------------------------

    def get_port(self, num):
        for p in self.ports:
            if p.port == num:
                return p
        
    def get_input_ports(self):
        return [p for p in self.ports if p.port > 0]
    
    def get_output_ports(self):
        return [p for p in self.ports if p.port < 0]
    
    def get_extra_ports(self):
        return [p for p in self.ports if p.parent_port]
        
    def get_in_flow(self):
        for ip in self.get_input_ports():
            if 'flow' in ip.types:
                return ip
                
    def get_out_flow(self):
        for op in self.get_output_ports():
            if 'flow' in op.types and 'split' not in op.types:
                return op
                
    def get_split_port(self):
        for op in self.get_output_ports():
            if 'split' in op.types:
                return op
                
    def get_port_info(self):
        info = {'in_flow': None, 'out_flow': None, 'split': None, 'in_var': [], 'out_var': []}
        for p in self.ports:
            if 'flow' in p.types:
                if 'split' in p.types:
                    info['split'] = p
                elif p.port > 0:
                    info['in_flow'] = p
                else:
                    info['out_flow'] = p
            elif p.port > 0:
                info['in_var'].append(p)
            else:
                info['out_var'].append(p)
                
        return info
        
    def close_all(self):
        for p in self.ports:
            p.close_wire()
            
    def clear_connections(self):
        for p in self.ports.copy():
            p.clear()
            
    def delete(self):
        self.close_all()
        self.clear_connections()
        if self.is_input():
            self.objects_dict['input'].close()
  
    def prune_extra_ports(self):
        for p in self.ports.copy():
            if p.parent_port and not p.connection:
                self.ports.remove(p)
            p.close_wire()
     
    def new_output_port(self, parent):
        p = parent.copy()
        self.set_stuck(True)
        self.manager.set_active_node(self)
        return p
 
    def create_in_indicator(self, port):
        if 'bool' in port.types:
            name = 'Bool'
        elif 'num' in port.types:
            name = 'Num'
        elif 'string' in port.types:
            name = 'String'
        elif 'player' in port.types:
            name = 'User'
        else:
            return 

        n = self.manager.get_node(name)
        op = n.get_port(-1)
        op.open_wire()
        Port.new_connection(op, port)
        return n

    def get_active_port(self):
        for p in self.ports:
            if p.live_wire:
                return p
        
    def end_connect(self):
        self.close_all()
        self.prune_extra_ports()
        
    def suppress_port(self, port):
        port.set_suppressed(not port.suppressed)
        for p in self.get_extra_ports():
            if port.port == p.parent_port:
                p.set_suppressed(not p.suppressed)

    def can_connect(self, p0, n1, p1):
        return True
        
#input stuff-------------------------------------------------------------------
        
    def transform(self):
        self.clear_connections()
        log = {'t': 'transform', 'n': self}
        self.manager.add_log(log)
        t0 = {p.port: p.types.copy() for p in self.ports}
        self.tf()
        t1 = {p.port: p.types.copy() for p in self.ports}
        log['types'] = (t0, t1)
        
    def click_down(self, button, hit, port):
        dub_click = self.ctimer <= 15
        if not dub_click:
            self.ctimer = 0
            
        if port:
            if button == 1:
                if dub_click:
                    if port.port > 0 and not port.connection:
                        self.create_in_indicator(port)
                elif not port.connection and port.types:
                    port.open_wire() 
                    self.set_stuck(True)
                    self.manager.set_active_node(self)                            
                elif 'flow' not in port.types:
                    self.new_output_port(port)
                        
            elif port.port > 0:
                if not port.connection:
                    if dub_click:
                        self.create_in_indicator(port)
                        
        if button == 1:
            if self.can_transform() and hit and dub_click and not port:
                self.transform()
        
    def click_up(self, button, hit, port):
        if port:
            
            an = self.manager.get_active_node()
            
            if button == 1:
                if an and an is not self:
                    if not port.connection:
                        p0 = an.get_active_port()
                        p1 = port
                        Port.new_connection(p0, p1)
                        self.manager.close_active_node()
                    elif 'flow' not in port.types:
                        p0 = self.new_output_port(port)
                        p1 = an.get_active_port()
                        Port.new_connection(p0, p1)
                        self.manager.close_active_node()

            elif button == 3:
                self.suppress_port(port)

    def events(self, events):
        mp = events['p']
        kd = events.get('kd')
        ku = events.get('ku')
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        
        hit_node = self.rect.collidepoint(mp)
        hit_port = None
        for p in self.ports:
            if p.visible:
                if p.rect.collidepoint(mp):
                    hit_port = p
                    break
                    
        if mbd:
            self.click_down(mbd.button, hit_node, hit_port)
        elif mbu:
            self.click_up(mbu.button, hit_node, hit_port)
            
        for o in self.objects:
            o.events(events)
            
        if self.is_input():
            if self.objects_dict['input'].active:
                self.drop()
            
#update stuff-------------------------------------------------------------------
        
    def update(self):
        if self.visible:
            super().update()
            
            for p in self.ports:
                p.update_position()
            
            self.big_rect.center = self.rect.center
           
            for o in self.objects:
                o.update()

            if self.ctimer < 30:
                self.ctimer += 1
                
            if not self.get_active_port():
                self.prune_extra_ports()
                if self._stuck:
                    self.set_stuck(False)
                
            if self.is_input():
                logs = self.objects_dict['input'].get_logs()
                if logs:
                    for log in logs:
                        self.manager.add_log(log)
        
#draw stuff-------------------------------------------------------------------
        
    def draw(self, surf):
        if self._selected or self._hover:
            surf.blit(ui.Image_Manager.rect_outline(self.image, color=(255, 0, 0)), self.rect)
        else:
            surf.blit(self.image, self.rect)

        for p in self.ports:
            p.draw(surf)
                
        for o in self.objects:
            o.draw(surf)
            
    def draw_on(self, surf, rect):
        dx, dy = rect.topleft
        self.rect.move_ip(-dx, -dy)
        self.update_children()
        for p in self.ports:
            p.update_position()
        self.draw(surf)
        self.rect.move_ip(dx, dy)
        self.update_children()
        for p in self.ports:
            p.update_position()

    def draw_wire(self, win):
        p = self.get_active_port()
        if p:
            pg.draw.line(win, Port.get_color(p.types), p.rect.center, pg.mouse.get_pos(), width=3)
            
class GroupNode(Node):
    def __init__(self, manager, id, nodes, name='Group'):
        self.nodes = nodes
        self.port_mem = {}
        ports = self.get_group_ports(nodes)
        super().__init__(manager, id, ports, val=name)
        self.set_self_pos()
        self.set_rel_node_pos()
        
    @property
    def name(self):
        return self.get_string_val()
        
    def get_objects(self):
        size = (self.rect.width - 25, self.rect.height - 50)
        i = ui.Input(size, message=self.val, fgcolor=(0, 0, 0), color=(255, 100, 100), length=25, fitted=True, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]
        
    def reset_ports(self):
        self.ports = self.get_group_ports(self.nodes)
        self.set_port_pos()
        
    def recall_port_mem(self):
        for p, visible in self.port_mem.items():
            p.set_visibility(visible)
   
    def set_rel_node_pos(self):
        rel_node_pos = {}
        x0, y0 = self.rect.center
        for n in self.nodes:
            x1, y1 = n.rect.center
            rel_node_pos[n] = (x1 - x0, y1 - y0)
        self.rel_node_pos = rel_node_pos
        
    def get_rel_node_pos(self):
        return {n.id: pos for n, pos in self.rel_node_pos.items()}
        
    def get_group_ports(self, nodes):
        ipp = []
        opp = []
        
        for n in nodes:
            n.prune_extra_ports()
            n.group_node = self
            n.set_visibility(False)
            
            for ip in n.get_input_ports():
                if (not ip.suppressed or (ip.suppressed and self.port_mem.get(ip, False))) and ip.connection not in nodes:
                    ipp.append(ip)
                else:
                    ip.set_visibility(False)
                    
            for op in n.get_output_ports():
                if (not op.suppressed or (op.suppressed and self.port_mem.get(op, False))) and op.connection not in nodes:
                    opp.append(op)
                else:
                    op.set_visibility(False)

        ipp.sort(key=lambda p: p.port if 'flow' not in p.types else 10)
        opp.sort(key=lambda p: abs(p.port) if 'flow' not in p.types else 10)
        ports = opp + ipp
        
        return ports
       
    def set_self_pos(self):
        self.rect.centerx = sum([n.rect.centerx for n in self.nodes]) // len(self.nodes)
        self.rect.centery = sum([n.rect.centery for n in self.nodes]) // len(self.nodes)
        self.set_port_pos()
        
    def set_port_mem(self):
        self.port_mem.clear()
        for n in self.nodes:
            for p in n.ports:
                self.port_mem[p] = p.visible

    def ungroup(self):
        self.set_port_mem()
        sx, sy = self.rect.center
        for n in self.nodes:
            n.set_visibility(True)
            n.group_node = None
            for p in n.ports:
                if p.types:
                    p.set_visibility(True)
            rx, ry = self.rel_node_pos[n]
            n.rect.center = (sx + rx, sy + ry)
            n.set_port_pos()
            n.drop()
        self.ports.clear()
        
    def new_output_port(self, parent):
        n = parent.node
        p = parent.copy()
        self.set_stuck(True)
        self.manager.set_active_node(n)
        return p
        
    def update(self):
        for n in self.nodes:
            n.update()
            
        super().update()

class Start(Node):
    cat = 'func'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['flow'], desc='flow')], type='func')
        
    def get_start(self):
        return '\t\tself.reset()\n'
        
    def get_text(self):
        return '\n\tdef start(self, player):\n'
   
class If(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='condition'), Port(2, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
        
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'if {0}:\n'.format(*self.get_input())   
        return text
        
class Elif(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='condition'), Port(2, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
 
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, If)
        return True
 
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'elif {0}:\n'.format(*self.get_input())   
        return text
        
class Else(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return isinstance(n1, (If, Elif))
        return True
        
    def get_text(self):
        text = 'else:\n'  
        return text
 
class If_Else(Node):
    cat = 'flow'
    subcat = 'conditional'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='if true'), Port(2, ['num'], desc='if false'), Port(3, Port.get_comparison_types()), Port(-1, [])])
        
    def tf(self):
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        
        if 'num' in ip1.types:
            ip1.set_types(['string'])
            ip2.set_types(['string'])
        elif 'string' in ip1.types:
            ip1.set_types(['player'])
            ip2.set_types(['player'])
        elif 'player' in ip1.types:
            ip1.set_types(['card'])
            ip2.set_types(['card'])
        elif 'card' in ip1.types:
            ip1.set_types(['num'])
            ip2.set_types(['num'])
            
    def update(self):
        super().update()
        
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        op = self.get_port(-1)
        
        t = None

        if ip1.connection:
            t = ip1.types[0]
        elif ip2.connection:
            t = ip2.types[0]
        if t:
            if not op.types:
                op.add_type(t)
        elif op.types:
            if op.connection:
                op.clear()
            op.set_types([])
        
    def get_default(self, p):
        if p == 1 or p == 2:
            return '1'
        elif p == 3:
            return 'True'
        
    def get_output(self, p):
        text = '{0} if {2} else {1}'.format(*self.get_input())   
        return text
 
class Bool(Node):
    size = (50, 40)
    cat = 'boolean'
    def __init__(self, manager, id, val='T'):
        super().__init__(manager, id, [Port(-1, ['bool'])], val=val, type='var')
        
    def get_objects(self):
        size = (self.rect.width - 25, self.rect.height - 25)
        full_check = lambda t: t.lower() in ('', 't', 'f')
        i = ui.Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=1, fitted=True, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]
        
    def get_actual_value(self):
        return self.get_string_val().lower() == 't'

    def get_output(self, p):
        val = self.get_string_val()
        if val.lower() == 't':
            return 'True'
        else:
            return 'False'
        
class Num(Node):
    size = (50, 40)
    cat = 'numeric'
    def __init__(self, manager, id, val='0'):
        super().__init__(manager, id, [Port(-1, ['num'])], val=val, type='var')
        
    def get_objects(self):
        full_check = lambda t: (t + '0').strip('-').isnumeric()
        size = (self.rect.width - 25, self.rect.height - 25)
        i = ui.Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=3, fitted=True, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]

    def get_val(self):
        return self.val

    def get_output(self, p):
        val = self.get_string_val()
        if not val.strip('-'):
            val = '0'
        return int(val)
        
class String(Node):
    size = (100, 50)
    cat = 'string'
    def __init__(self, manager, id, val="-"):
        super().__init__(manager, id, [Port(-1, ['string'])], val=val, type='var')
        
    def get_objects(self):
        full_check = lambda t: t.count("'") < 3
        size = (self.rect.width - 25, self.rect.height - 25)
        i = ui.Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=50, fitted=True, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]
        
    def get_output(self, p):
        val = self.get_string_val()
        return f"'{val}'"
        
class Line(Node):
    size = (300, 50)
    cat = 'flow'
    subcat = 'other'
    def __init__(self, manager, id, val="-"):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['flow'])], val=val)
        
    def get_objects(self):
        full_check = lambda t: t.count("'") < 3
        size = (self.rect.width - 25, self.rect.height - 25)
        i = ui.Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=300, fitted=True, allignment='l', lines=1, scroll=False, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]
        
    def get_text(self):
        val = self.get_string_val()
        if 'import' in val:
            val = 'raise ValueError'
        return f"{val}\n"
        
class Block(Node):
    size = (300, 300)
    cat = 'flow'
    subcat = 'other'
    def __init__(self, manager, id, val="-"):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['flow'])], val=val)
        
    def get_objects(self):
        full_check = lambda t: t.count("'") < 3
        size = (self.rect.width - 25, self.rect.height - 25)
        i = ui.Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=300, fitted=True, allignment='l', lines=20, scroll=False, double_click=True)
        i.rect.center = self.rect.center
        offset = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.add_child(i, set_parent=True, offset=offset)
        self.objects_dict['input'] = i
        return [i]
        
    def get_text(self):
        val = self.get_string_val()
        if 'import' in val:
            val = 'raise ValueError'
        return f"{val}\n"
        
class And(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='x'), Port(2, Port.get_comparison_types(), desc='y'), Port(-1, ['bool'], desc='x and y')])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} and {})'.format(*self.get_input())     
        return text
        
class Or(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='x'), Port(2, Port.get_comparison_types(), desc='y'), Port(-1, ['bool'], desc='x or y')])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} or {})'.format(*self.get_input())     
        return text
        
class Not(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='x'), Port(-1, ['bool'], desc='not x')])
        
    def get_default(self, p):
        return 'True'

    def get_output(self, p):
        text = '(not {})'.format(*self.get_input())    
        return text
        
class Equal(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, manager, id):
        types = Port.get_comparison_types()
        types = types[1:] + [types[0], 'string']
        super().__init__(manager, id, [Port(1, types, desc='x'), Port(2, types.copy(), desc='y'), Port(-1, ['bool'], desc='x == y')])
        
    def get_default(self, p):
        ip = self.get_port(1)
        if 'num' in ip.types:
            return '1'
        elif 'string' in ip.types:
            return "''"
        elif 'bool' in ip.types:
            return 'True'
        elif 'player' in ip.types:
            return 'player'
        elif 'card' in ip.types:
            return 'self'
        else:
            return '[]'

    def get_output(self, p):
        text = '({} == {})'.format(*self.get_input())    
        return text
      
class Greater(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['bool'], desc='x > y')])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} > {1})'.format(*self.get_input())    
        return text
        
class Less(Node):
    cat = 'boolean'
    subcat = 'numeric'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['bool'], desc='x < y')])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} < {1})'.format(*self.get_input())    
        return text
     
class Max(Node):
    cat = 'numeric'
    subcat = 'statistic'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['ns'], desc='[0, 1, 2...]'), Port(-1, ['num'], desc='max value')])
        
    def get_default(self, p):
        return '[]'

    def get_output(self, p):
        text = 'max({0}, 0)'.format(*self.get_input())    
        return text
        
class Min(Node):
    cat = 'numeric'
    subcat = 'statistic'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['ns'], desc='[0, 1, 2...]'), Port(-1, ['num'], desc='min value')])
        
    def get_default(self, p):
        return '[]'

    def get_output(self, p):
        text = 'min({0}, 0)'.format(*self.get_input())    
        return text
     
class Add(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x + y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Incriment(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(-1, ['num'], desc='x + 1')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({} + 1)'.format(*self.get_input())
        
class Subtract(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x - y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} - {1})'.format(*self.get_input())
        
class Multiply(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x * y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} * {1})'.format(*self.get_input())
        
class Negate(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(-1, ['num'], desc='-x')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '(-1 * {0})'.format(*self.get_input())
        
class Divide(Node):
    cat = 'numeric'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x / y')])
        
    def get_default(self, p):
        return str(p)
        
    def get_output(self, p):
        return '({0} // {1})'.format(*self.get_input())
  
class Exists(Node):
    cat = 'boolean'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player', 'card'], desc='x'), Port(-1, ['bool'], desc='x is not None')])
        
    def get_default(self, p):
        return '1'
        
    def get_output(self, p):
        return '({0} is not None)'.format(*self.get_input())
  
class For(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list'), Port(2, ['flow']), Port(-1, [], desc='list value'), Port(-2, ['split', 'flow']), Port(-3, ['flow'])])  

    def update(self):
        super().update()
        
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            if not op.types:
                op.add_type(ip.connection_port.get_contains())
        elif op.types:
            if op.connection:
                op.clear()
            op.set_types([])

    def get_loop_var(self):
        loop_var = f'x{self.id}'
        
        ip = self.get_port(1)
        
        if not ip.is_open():
            
            contains = ip.connection_port.get_contains()

            if contains == 'player':
                loop_var = f'p{self.id}'  
            elif contains == 'num':  
                loop_var = f'i{self.id}'
            elif contains == 'card':
                loop_var = f'c{self.id}'
            elif contains == 'string':
                loop_var = f's{self.id}'
            elif contains == 'bool':
                loop_var = f'b{self.id}'
                
        return loop_var
        
    def get_default(self, p):
        if p == 1:
            return 'range(1)'
        
    def get_text(self):
        input = [self.get_loop_var()] + self.get_input()
        text = 'for {} in {}:\n'.format(*input)   
        return text
        
    def get_output(self, p):
        text = ''
        if p not in (-2, -3):
            text = self.get_loop_var()
        return text
        
class Zipped_For(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list 1'), Port(2, ['cs', 'ps', 'ns', 'bs'], desc='list 2'), Port(3, ['flow']), Port(-1, [], desc='value 1'), Port(-2, [], desc='value 2'), Port(-3, ['split', 'flow']), Port(-4, ['flow'])])  

    def update(self):
        super().update()
        
        for p in (1, 2):
        
            ip = self.get_port(p)
            op = self.get_port(-p)
            
            if ip.connection:
                if not op.types:
                    op.add_type(ip.connection_port.get_contains())
            elif op.types:
                if op.connection:
                    op.clear()
                op.set_types([])

    def get_loop_var(self, p):   
        ip = self.get_port(p)
        loop_var = f'x{self.id}'
        
        if not ip.is_open():
            contains = ip.connection_port.get_contains()
            if contains == 'player':
                return f'p{self.id}'  
            elif contains == 'num':  
                return f'i{self.id}'
            elif contains == 'card':
                return f'c{self.id}'
            elif contains == 'string':
                return f's{self.id}'
            elif contains == 'bool':
                return f'b{self.id}'
        
    def get_default(self, p):
        return 'range(1)'
        
    def get_text(self):
        vars = [self.get_loop_var(1), self.get_loop_var(2)]
        input = vars + self.get_input()
        text = 'for {0}, {1} in zip({2}.copy(), {3}.copy()):\n'.format(*input)   
        return text
        
    def get_output(self, p):
        if p == -1:
            return self.get_loop_var(1)
        elif p == -2:
            return self.get_loop_var(2)
        
class Break(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, (For, Zipped_For)) and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def get_text(self):
        return 'break\n'
        
class Continue(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if isinstance(p.connection, (For, Zipped_For)) and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def get_text(self):
        return 'continue\n'
        
class Range(Node):
    cat = 'numeric'
    subcat = 'iterator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='min'), Port(2, ['num'], desc='max'), Port(-1, ['ns'], desc='[min, ..., max]')])
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '0'
        
    def get_output(self, p):
        text = 'range({0}, {1})'.format(*self.get_input()) 
        return text
       
class User(Node):
    cat = 'player'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['player'], desc='player')])  

    def get_output(self, p):
        return 'player'
       
class All_Players(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='player list')])

    def get_output(self, p):
        return 'self.game.players.copy()'
        
class Stored_Players(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return 'self.players'
        
class Stored_Cards(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['cs'], desc='card list')])
        
    def get_output(self, p):
        return 'self.cards'
        
class Opponents(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return 'self.sort_players(player)'
        
class Opponents_With_Points(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return '[p for p in self.game.players if p.score > 0]'
      
class Card(Node):
    cat = 'card'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['card'], desc='this card')])  

    def get_output(self, p):
        return 'self'
      
class Length(Node):
    cat = 'iterator'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['ps', 'cs', 'ns', 'bs'], desc='list'), Port(-1, ['num'], desc='length of list')])   
        
    def get_default(self, port):
        return '[]'
        
    def get_output(self, p):
        return 'len({})'.format(*self.get_input())
      
class New_List(Node):
    cat = 'iterator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='list')]) 

    def tf(self):
        op = self.get_port(-1)
        if 'ps' in op.types:
            op.set_types(['cs'])
        elif 'cs' in op.types:
            op.set_types(['ps'])
            
    def get_dec(self):
        return f'ls{self.id} = []\n'
        
    def get_output(self, p):
        return f'ls{self.id}'

class Merge_Lists(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['ps'], desc='list 1'), Port(2, ['ps'], desc='list 2'), Port(-1, ['ps'], desc='list 1 + list 2')])  
        
    def tf(self):
        op = self.get_port(-1)
        if 'ps' in op.types:
            for p in self.ports:
                p.set_types(['cs'])
        elif 'cs' in op.types:
            for p in self.ports:
                p.set_types(['ps'])

    def get_default(self, p):
        return '[]'
        
    def get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Merge_Lists_In_Place(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['ps'], desc='merging list'), Port(2, ['ps'], desc='original list'), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def tf(self):
        ports = (self.get_port(1), self.get_port(2))
        if 'ps' in ports[0].types:
            for p in ports:
                p.set_types(['cs'])
        elif 'cs' in ports[0].types:
            for p in ports:
                p.set_types(['ps'])
 
    def get_default(self, p):
        return '[]'
        
    def get_text(self):
        return '{1} += {0}\n'.format(*self.get_input())
       
class Add_To(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs'], desc='value'), Port(2, ['card'], desc='list'), Port(3, ['flow']), Port(-1, ['flow'])])

    def tf(self):
        p1 = self.get_port(1)
        p2 = self.get_port(2)
        if 'cs' in p1.types:
            p1.set_types(['ps'])
            p2.set_types(['player'])
        elif 'ps' in p1.types:
            p1.set_types(['cs'])
            p2.set_types(['card'])
        
    def get_default(self, p):
        if p == 1:
            return '[]'
        elif p == 2:
            return 'self'

    def get_text(self):
        return "{0}.append({1})\n".format(*self.get_input())
        
class Remove_From(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs'], desc='list'), Port(2, ['card'], desc='value'), Port(3, ['flow']), Port(-1, ['flow'])])

    def tf(self):
        p1 = self.get_port(1)
        p2 = self.get_port(2)
        if 'cs' in p1.types:
            p1.set_types(['ps'])
            p2.set_types(['player'])
        elif 'ps' in p1.types:
            p1.set_types(['cs'])
            p2.set_types(['card'])
        
    def get_default(self, p):
        if p == 1:
            return '[]'
        elif p == 2:
            return 'self'

    def get_text(self):
        return "{0}.remove({1})\n".format(*self.get_input())
        
class Clear_List(Node):
    cat = 'iterator'
    subcat = 'operators'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs', 'ps'], desc='list'), Port(2, ['flow']), Port(-1, ['flow'])])
        
    def get_default(self, p):
        return '[]'

    def get_text(self):
        return "{0}.clear()\n".format(*self.get_input())

class Contains(Node):
    cat = 'iterator'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player', 'card'], desc='value'), Port(2, ['ps', 'cs'], desc='list'), Port(-1, ['bool'], desc='value in list')])  

    def tf(self):
        p = self.get_port(2)
        p.types.reverse()
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '[]'
        
    def get_output(self, p):
        text = '({0} in {1})'.format(*self.get_input())
        return text
  
class Has_Tag(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='tag'), Port(2, ['card'], desc='card'), Port(-1, ['bool'], desc='card has tag')])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({0} in {1}.tags)'.format(*self.get_input())
        return text
      
class Get_Name(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card'], desc='card'), Port(-1, ['string'], desc='card name')])   
        
    def get_default(self, p):
        return 'self'
        
    def get_output(self, p):
        text = '{0}.name'.format(*self.get_input())
        return text 
      
class Has_Name(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='name'), Port(2, ['card'], desc='card'), Port(-1, ['bool'], desc='card has name')])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({1}.name == {0})'.format(*self.get_input())
        return text
    
class Find_Owner(Node):
    cat = 'card'
    subcat = 'player'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card'], desc='card'), Port(-1, ['player'], desc='card owner')])   
        
    def get_default(self, p):
        return 'self'
        
    def get_output(self, p):
        text = 'self.game.find_owner({0})'.format(*self.get_input())
        return text

class Tag_Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='tag'), Port(2, ['bool'], desc='filter self'), Port(3, ['cs'], desc='card list'), Port(-1, ['cs'], desc='cards with tag from list')])
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 3:
            return '[]'
        
    def get_output(self, p):
        ip = self.get_port(2)
        if ip.connection:
            if ip.connection.get_actual_value():
                text = "[x for x in {2} if {0} in getattr(x, 'tags', []) and x != self]"
            else:
                text = "[x for x in {2} if {0} in getattr(x, 'tags', [])]"
        else:
            text = "[x for x in {2} if {0} in getattr(x, 'tags', [])]"
        text = text.format(*self.get_input())
        return text
        
class Name_Filter(Node):
    cat = 'iterator'
    subcat = 'filter'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='name'), Port(2, ['bool'], desc='include self'), Port(3, ['cs'], desc='list'), Port(-1, ['cs'], desc='cards with name from list')])
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 3:
            return '[]'
        
    def get_output(self, p):
        ip = self.get_port(2)
        if ip.connection:
            if ip.connection.get_actual_value():
                text = "[x for x in {2} if x.name == {0} and x != self]"
            else:
                text = "[x for x in {2} if x.name == {0}]"
        else:
            text = "[x for x in {2} if x.name == {0}]"
        text = text.format(*self.get_input())
        return text
   
class Gain(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.gain(self, {0})\n'.format(*self.get_input())
        return text      

class Lose(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.lose(self, {0})\n'.format(*self.get_input())
        return text      
        
class Steal(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['player'], desc='target'), Port(4, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p in (2, 3):
            return 'player'
        
    def get_text(self):
        text = '{1}.steal(self, {0}, {2})\n'.format(*self.get_input())
        return text      

class Start_Flip(Node):
    cat = 'func'
    subcat = 'flip'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 

    def get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'flip'\n"
        return "player.add_request(self, 'flip')\n"
        
    def on_connect(self, p):
        if p.port == 1 and not self.manager.exists('flip'):
            self.manager.get_node('Flip')
            
    def check_errors(self):
        text = ''
        if not self.manager.exists('flip'):
            text = 'a flip node must be added to process flip results'
        return text

class Flip(Node):
    cat = 'func'
    subcat = 'flip'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['bool'], desc='flip result'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tself.t_coin = coin\n'
            
    def get_text(self):
        return '\n\tdef coin(self, player, coin):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'coin'

class Start_Roll(Node):
    cat = 'func'
    subcat = 'roll'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 
        
    def get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'roll'\n"
        return "player.add_request(self, 'roll')\n"
        
    def on_connect(self, p):
        if p.port == 1 and not self.manager.exists('roll'):
            self.manager.get_node('Roll')
            
    def check_errors(self):
        text = ''
        if not self.manager.exists('roll'):
            text = 'a roll node must be added to process roll results'
        return text
        
class Roll(Node):
    cat = 'func'
    subcat = 'roll'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'], desc='roll result'), Port(-2, ['flow'])], type='func') 

    def get_start(self):
        return '\t\tself.t_roll = dice\n'
            
    def get_text(self):
        return '\n\tdef roll(self, player, dice):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'dice'
            
class Start_Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 
        
    def on_connect(self, p):
        if p.port == 1:
            if not self.manager.exists('Get_Selection'):
                self.manager.get_node('Get_Selection', pos=(self.rect.centerx + self.rect.width + 5, self.rect.centery), held=False)
            if not self.manager.exists('Select'):
                self.manager.get_node('Select', pos=(self.rect.centerx, self.rect.centery + self.rect.height + 25), held=False)

    def get_text(self):
        pf = mapping.find_parent_func(self)
        if pf:
            if isinstance(pf, (Flip, Roll, Select)):
                return "self.wait = 'select'\n"
        return "player.add_request(self, 'select')\n"
        
    def check_errors(self):
        text = ''
        if not self.manager.exists('Get_Selection'):
            text = 'a get selection node must be added to initiate selection process'
        elif not self.manager.exists('Select'):
            text = 'a select node must be added to process player selection'
        return text
            
class Get_Selection(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='selection'), Port(-2, ['cs'], desc='selection'), Port(-3, ['flow'])], type='func') 
            
    def get_start(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_List):
                    return ''
        else:
            return '\t\tselection = []\n'
            
    def get_text(self):
        return '\n\tdef get_selection(self, player):\n'
        
    def get_end(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_List):
                    return ''
        else:
            return '\t\treturn selection\n'
        
    def get_output(self, p):
        return 'selection'
            
    def check_errors(self):
        text = ''
        if self.manager.exists('start selection') and not self.manager.exists('select'):
            text = 'a select node must be added to process player selection'
        return text
        
class Return_List(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs', 'ps'], desc='list'), Port(2, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, Get_Selection):
                    break
            else:
                ip.clear()
        
    def get_default(self, p):
        return '[]'
        
    def get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class Select(Node):
    cat = 'func'
    subcat = 'select'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'], desc='number of selected items'), Port(-2, ['player'], desc='selected player'), Port(-3, ['card'], desc='selected card'), Port(-4, ['flow'])], type='func') 
                
    def get_start(self):
        return '\t\tif not num:\n\t\t\treturn\n\t\tsel = player.selected[-1]\n\t\tself.t_select = sel\n\t\tsel_c = None\n\t\tsel_p = None\n\t\tif isinstance(sel, Card):\n\t\t\tsel_c = sel\n\t\telse:\n\t\t\tsel_p = sel\n'
            
    def get_text(self):
        return '\n\tdef select(self, player, num):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'num'
        elif p == -2:
            return 'sel_p'
        elif p == -3:
            return 'sel_c'
            
    def check_errors(self):
        text = ''
        if self.manager.exists('start selection') and not self.manager.exists('get select'):
            text = 'a get selection node must be added to initiate selection process'
        return text
  
class Return_Bool(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='return bool'), Port(2, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, (Can_Use, Can_Cast)):
                    break
            else:
                ip.clear()
        
    def get_default(self, p):
        return 'True'
        
    def get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class Can_Cast(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['bool'], desc='can cast'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tcancast = True\n'
            
    def get_text(self):
        return '\n\tdef can_cast(self, player):\n'
        
    def get_end(self):
        ports = map_scope(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_Bool):
                    return ''
        else:
            return '\t\treturn cancast\n'

    def get_output(self, p):
        if p == -1:
            return 'cancast'   

class Can_Use(Node):
    cat = 'func'
    subcat = 'item and spell'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['bool'], desc='can use'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tcanuse = True\n'
            
    def get_text(self):
        return '\n\tdef can_use(self, player):\n'
        
    def get_end(self):
        ports = mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if isinstance(p.connection, Return_Bool):
                    return ''
        else:
            return '\t\treturn canuse\n'

    def get_output(self, p):
        if p == -1:
            return 'canuse'             
  
class Start_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'])]) 

    def on_connect(self, p):
        if p.port == 1:
            if not self.manager.exists('Init_Ongoing'):
                self.manager.get_node('Init_Ongoing', pos=(self.rect.centerx + self.rect.width + 5, self.rect.centery), held=False)
            if not self.manager.exists('Add_To_Ongoing'):
                self.manager.get_node('Add_To_Ongoing', pos=(self.rect.centerx + (self.rect.width * 2) + 15, self.rect.centery), held=False)
            if not self.manager.exists('Ongoing'):
                self.manager.get_node('Ongoing', pos=(self.rect.centerx, self.rect.centery + self.rect.height + 5), held=False)
                
    def get_text(self):
        return "self.start_ongoing(player)\n"
        
class Init_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['flow'])], type='func') 
            
    def get_text(self):
        return '\n\tdef start_ongoing(self, player):\n'
        
class Add_To_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='log type'), Port(2, ['flow']), Port(-1, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(2)
        if ip.connection:
            ports = mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if isinstance(p.connection, Init_Ongoing):
                    break
            else:
                ip.clear()
            
    def get_default(self, p):
        return "''"
            
    def get_text(self):
        return 'player.add_og(self, {0})\n'.format(*self.get_input())
        
class Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['log'], desc='log info'), Port(-2, ['flow'])], type='func') 
        
    def get_text(self):
        return '\n\tdef ongoing(self, player, log):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'log'

class Extract_Value(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='key'), Port(2, ['log'], desc='log'), Port(-1, [], desc='value')]) 
        
    def get_output(self, p):
        text = "{1}.get({0})".format(*self.get_input())
        return text
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'dict()'
        
    def eval_text(self, text):
        if text == 'c':
            return 'card'
        elif text in ('gp', 'lp', 'sp', 'give', 'dice'):
            return 'num'
        elif text in ('t', 'deck'):
            return 'string'
        elif text in ('u', 'target'):
            return 'player'
        elif text == 'coin':
            return 'bool'
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        op = self.get_port(-1)
        
        if ip.connection:
            text = ip.connection.get_string_val()
            type = self.eval_text(text)
            if type:
                if type not in op.types:
                    op.add_type(type)
            else:
                op.clear_types()
        elif op.types:
            op.clear_types()

class Deploy(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='type'), Port(2, ['ps'], desc='players to send to'), Port(3, ['card'], desc='set stored card'), Port(4, ['player'], desc='set stored player'), Port(5, ['flow']), Port(-1, ['flow'])]) 
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return '[]'
        elif p == 3 or p == 4:
            return 'None'
            
    def get_text(self):
        input = self.get_input()
        request = input[0]
        if request.strip("'") not in ('', 'flip', 'roll', 'select', 'og'):
            input[0] = "''"
        return "self.deploy(player, {1}, {0}, extra_card={2}, extra_player={3})\n".format(*input)

class Get_Flip_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['bs'], desc='flip results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_flip_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class Get_Roll_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['ns'], desc='roll results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_roll_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class Get_Select_Results(Node):
    cat = 'func'
    subcat = 'deploy'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['cs'], desc='select results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_select_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'

class Self_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'])])  

    def get_output(self, p):
        return 'player.played.index(self)'
        
class Index_Above(Node):
    cat = 'iterator'
    subcat = 'index'
    tipe = "Like the 'Self Index' node, an 'IndexError' will be raised if this card does not exist in the user's played cards."
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'], desc='self index - 1')])  

    def get_output(self, p):
        return 'max({player.played.index(self) - 1, 0})'
        
class Index_Below(Node):
    cat = 'iterator'
    subcat = 'index'
    tipe = "Like the 'Self Index' node, an 'IndexError' will be raised if this card does not exist in the user's played cards."
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'], desc='self index + 1')])  

    def get_output(self, p):
        return 'min({player.played.index(self) + 1, len(player.played)})'
        
class Check_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(2, ['num'], desc='index'), Port(3, ['string'], desc='tag'), Port(4, ['flow']), Port(-1, ['card'], desc='card at index'), Port(-2, ['bool'], desc='new card'), Port(-3, ['flow'])])   
 
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return '-1'
        elif p == 3:
            return ''
        
    def get_text(self):
        ip = self.get_port(3)
        input = self.get_input()
        if ip.connection:
            if ip.connection.get_string_val().strip("'"):
                text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'}, tags=[{'{2}'}])\n"
            else:
                text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'})\n"
                input.pop(-1)
        else:
            text = f"added{self.id}, c{self.id} = self.check_index({'{0}'}, {'{1}'})\n"
            input.pop(-1)
        return text.format(*input)
        
    def get_output(self, p):
        if p == -1:
            return f'c{self.id}'
        elif p == -2:
            return f'added{self.id}'

class Splitter(Node):
    cat = 'flow'
    subcat = 'other'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, Port.get_comparison_types(), desc='value'), Port(-1, [], desc='value'), Port(-2, [], desc='value')])
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        opp = self.ports[1:]
        
        if ip.connection:
            p = ip.connection_port
            for op in opp:
                if not op.types:
                    op.set_visibility(True)
                    op.set_types(p.types.copy())
                    
        else:
            for op in opp:
                if op.types:
                    op.clear()
                    op.set_visibility(False)
                    op.set_types([])

    def get_output(self, p):
        ip = self.get_input()
        text = '{}' * len(ip)
        return text.format(*ip)
        
class Check_First(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(-1, ['bool'], desc='player is first')])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        
    def get_output(self, p):
        return 'self.game.check_first({0})'.format(*self.get_input())  
        
class Check_Last(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(-1, ['bool'], desc='player is last')])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        
    def get_output(self, p):
        return 'self.game.check_last({0})'.format(*self.get_input())  

class Draw_Cards(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='card type'), Port(2, ['num'], desc='number of cards'), Port(3, ['player']), Port(4, ['flow']), Port(-1, ['cs'], desc='cards'), Port(-2, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return "'treasure'"
        elif p == 2:
            return '1'
        elif p == 3:
            return 'player'
        
    def get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output(0))
        return "{0} = {3}.draw_cards({1}, num={2})\n".format(*input)
        
    def get_output(self, p):
        return f'seq{self.id}'
        
class Is_Event(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='event name'), Port(-1, ['bool'], desc='event has name')])   
        
    def get_default(self, p):
        return "''"
        
    def get_output(self, p):
        return 'self.game.is_event({0})'.format(*self.get_input())
                
class Play_Card(Node):
    cat = 'player'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card']), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        return "{1}.play_card({0})\n".format(*self.get_input())
           
class Copy_Card(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card']), Port(-1, ['card'], desc='card copy')])
        
    def get_default(self, p):
        return 'self'

    def get_output(self, p):
        return "{0}.copy()".format(*self.get_input())

class Set_Extra_Card(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card'], desc='new extra card'), Port(2, ['flow']), Port(-1, ['flow'])])
            
    def get_text(self):
        return 'self.extra_card = {0}\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'None'

class Get_Extra_Card(Node):
    cat = 'card attributes'
    subcat = 'card'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['card'], desc='extra card')])
            
    def get_output(self, p):
        return 'self.extra_card'   
        
class Set_Extra_Player(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player'], desc='new extra player'), Port(2, ['flow']), Port(-1, ['flow'])])
            
    def get_text(self):
        return 'self.extra_player = {0}\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'None'

class Get_Extra_Player(Node):
    cat = 'card attributes'
    subcat = 'player'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['player'], desc='extra player')])
            
    def get_output(self, p):
        return 'self.extra_player' 
        
class Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='index'), Port(2, ['ps'], desc='list'), Port(-1, ['player'], desc='list value at index')])
        
    def tf(self):
        ip = self.get_port(2)
        op = self.get_port(-1)
        
        if 'ps' in ip.types:
            ip.set_types(['cs'])
            op.set_types(['card'])
        elif 'cs' in ip.types:
            ip.set_types(['ps'])
            op.set_types(['player'])
            
    def get_output(self, p):
        return '{1}[{0}]'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return 'player.get_played().copy()'
        
class Safe_Index(Node):
    cat = 'iterator'
    subcat = 'index'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='index'), Port(2, ['ps'], desc='list'), Port(-1, ['player'], desc='list value at index')])
        
    def tf(self):
        ip = self.get_port(2)
        op = self.get_port(-1)
        
        if 'ps' in ip.types:
            ip.set_types(['cs'])
            op.set_types(['card'])
        elif 'cs' in ip.types:
            ip.set_types(['ps'])
            op.set_types(['player'])
            
    def get_output(self, p):
        return 'safe_index({1}, {0})'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return 'player.get_played.copy()'
        
class Discard(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return '{0}.discard_card({1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
            
class Safe_Discard(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return '{0}.safe_discard({1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
            
class Use_Item(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card'], desc='item'), Port(2, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'player.use_item({0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self'
        
class Cast_Spell(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card'], desc='spell card'), Port(2, ['player'], desc='target'), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'player.cast({1}, {0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
            
class Give_Card(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card']), Port(2, ['player'], desc='target'), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'player.give_card({0}, {1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
     
class Get_New_Card(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='card name')])

    def get_text(self):
        return 'self.game.get_card({0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self.name'
     
class Transfom(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='new card name'), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'self.game.transform({1}, {0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'self'
            
class Swap(Node):
    cat = 'card'
    subcat = 'operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'self.game.swap({0}, {1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self'
        
class Get_Discard(Node):
    cat = 'card'
    subcat = 'iterator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['cs'], desc='discarded cards')])
        
    def get_output(self, p):
        return 'self.game.get_discard()'
     
class Set_Mode(Node):
    cat = 'card attributes'
    subcat = 'mode'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['num'], desc='new mode'), Port(2, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return '0'
        
    def get_text(self):
        return 'self.mode = {0}\n'.format(*self.get_input())
        
class Get_Mode(Node):
    cat = 'card attributes'
    subcat = 'mode'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['num'], desc='mode')])   
        
    def get_output(self, p):
        return 'self.mode'

class Steal_Random(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='deck'), Port(2, ['player'], desc='target'), Port(3, ['flow']), Port(-1, ['card']), Port(-2, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return "'treasure'"
        elif p == 2:
            return 'player'

    def get_text(self):
        input = self.get_input()
        input.insert(0, self.get_output())
        return "{0} = player.steal_random_card({1}, {2})\n".format(*input)
        
    def get_output(self):
        return f'c{self.id}'
        
class Add_Card(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(2, ['card']), Port(3, ['string'], desc='deck'), Port(4, ['num'], desc='index'), Port(5, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
        elif p == 3:
            return 'unplayed'
        elif p == 4:
            return 'None'

    def get_text(self):
        return "{0}.add_card({1}, {2}, i={3})\n".format(*self.get_input())
        
class Safe_Add_Card(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'

    def get_text(self):
        return "{0}.safe_add({1})\n".format(*self.get_input())
        
class Get_Deck(Node):
    cat = 'player'
    subcat = 'card operator'
    accepted_strings = ('played', 'unplayed', 'items', 'spells', 'active_spells', 'equipment', 'treasure', 'landscapes')
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='deck name'), Port(2, ['player']), Port(-1, ['cs'], desc='deck')])   
        
    def update(self):
        super().update()
        
        op = self.get_port(-1)
        deck = self.get_input()[0].strip("'").lower()
        
        if deck in Get_Deck.accepted_strings:
            if 'cs' not in op.types:
                op.set_types(['cs'])
        else:
            op.clear()
            op.clear_types()
        
    def get_default(self, p):
        if p == 1:
            return "'played'"
        elif p == 2:
            return 'player'
            
    def get_output(self, p):
        return 'getattr({1}, {0}).copy()'.format(*self.get_input())
        
class Get_Score(Node):
    cat = 'player'
    subcat = 'score'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['player']), Port(-1, ['num'], desc='points')])   
        
    def get_default(self, p):
        return 'player'

    def get_output(self, p):
        return "{0}.score".format(*self.get_input())
        
class Has_Card(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='card name'), Port(2, ['player']), Port(-1, ['bool'], desc='player has card')])   
        
    def get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'player'

    def get_output(self):
        return "{1}.has_card({0})".format(*self.get_input())
        
class Is_Player(Node):
    cat = 'player'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card', 'player']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        return 'player'

    def get_output(self):
        return "({0}.__name__ == 'Player')".format(*self.get_input())        
        
class Is_Card(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card', 'player']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        return 'self'

    def get_output(self):
        return "({0}.__name__ == 'Card')".format(*self.get_input())  
        