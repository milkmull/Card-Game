import pygame as pg
from constants import *
from ui import Textbox, Dragger, rect_outline, intersect, Input

#setup stuff-------------------------------------------------------------------

def init():
    g = globals()
    names = []
    for k in g:
        v = g[k]
        if getattr(v, 'isnode', False) and not (hasattr(v, 'base') or v is Node):
            names.append(k)     
    g['NAMES'] = names
    
class Manager:
    manager = None
    @classmethod
    def set_manager(cls, m):
        cls.manager = m

class Mapping:
    def find_chunk(n, nodes):
        nodes.append(n)
        
        for ip in n.get_input_ports():
            if ip.connection:
                connected_node = ip.connection_port.get_visible_node()
                if connected_node not in nodes:
                    Mapping.find_chunk(connected_node, nodes)
        
        for op in n.get_output_ports():
            if op.connection:
                connected_node = op.connection_port.get_visible_node()
                if connected_node not in nodes:
                    Mapping.find_chunk(connected_node, nodes)
                    
        return nodes

    def map_ports(n, ports, skip_ip=False, skip_op=False, all_ports=False, out_type=None, in_type=None): 
        if not skip_ip:
            for ip in n.get_input_ports():
                if not in_type or (in_type and in_type in ip.types):
                    if ip not in ports:
                        if ip.connection:
                            ports.append(ip)
                            op = ip.connection_port
                            if op not in ports:
                                Mapping.map_ports(op.node, ports, skip_ip=skip_ip, skip_op=skip_op, all_ports=all_ports, out_type=out_type, in_type=in_type)
                        elif all_ports:
                            ports.append(ip)
                
        if not skip_op:
            for op in n.get_output_ports():
                if not out_type or (out_type and out_type in ip.types):
                    if op not in ports:
                        if op.connection:
                            ports.append(op)
                            ip = op.connection_port
                            if ip not in ports:
                                Mapping.map_ports(ip.node, ports, skip_ip=skip_ip, skip_op=skip_op, all_ports=all_ports, out_type=out_type, in_type=in_type) 
                        elif all_ports:
                            ports.append(op)
                    
        return ports

    def trace_flow(n, nodes, dir):
        nodes.append(n)
        
        if dir == -1:
            for ip in n.get_input_ports():
                if ip.connection:
                    if 'flow' in ip.types and ip.connection not in nodes:
                        Mapping.trace_flow(ip.connection, nodes, dir=dir)
                        
        elif dir == 1:
            for op in n.get_output_ports():
                if op.connection:
                    if 'flow' in op.types and op.connection not in nodes:
                        Mapping.trace_flow(op.connection, nodes, dir=dir)
                        
        return nodes

    def find_parent_func(n):
        nodes = Mapping.trace_flow(n, [], -1)
        for n in nodes:
            if n.type == 'func':
                return n

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
                    Mapping.map_flow(connected_node, nodes, columns, column=column - 1)
                    
        opp = n.get_output_ports()
        opp.sort(key=lambda p: p.get_true_port(), reverse=True)
        
        for op in opp[::-1]:
            if 'flow' in op.types and op.connection:
                connected_node = op.connection_port.get_visible_node()
                if connected_node in nodes:
                    Mapping.map_flow(connected_node, nodes, columns, column=column + 1)
                
        for op in opp:
            if 'flow' not in op.types and op.connection:
                connected_node = op.connection_port.get_visible_node()
                if connected_node in nodes:
                    in_flow = connected_node.get_in_flow()
                    if in_flow:
                        if in_flow.connection:
                            if in_flow.connection in nodes:
                                continue
                    Mapping.map_flow(connected_node, nodes, columns, column=column + 1)
                
        return columns
        
    def check_bad_connection(n0, n1):   
        local_funcs = set()
        scope_output = set()
        loop_output = set()
        
        nodes = Mapping.find_chunk(n0, [])
        local_funcs = set(n for n in nodes if n.type == 'func')

        for n in nodes:
            out_port = None
            split_port = None
            check_ports = []
            for op in n.get_output_ports():
                if 'split' in op.types:
                    split_port = op
                    if op.connection:
                        check_ports.append(op)
                elif 'flow' in op.types:
                    out_port = op
                elif op.connection:
                    check_ports.append(op)
                    
            if split_port and check_ports:
                for op in check_ports:
                    ports = Mapping.map_ports(op.connection, check_ports.copy(), all_ports=True, in_type='flow')
                    if out_port in ports:
                        scope_output.add(op)

        opp = n0.get_output_ports()     
        for op in opp:
            if op.connection:
                ports = Mapping.map_ports(op.connection, [], skip_ip=True)
                if any(op in ports for op in opp):
                    loop_output.add(op)
                
        return (local_funcs, scope_output, loop_output)

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
        
    def check_intersect(self, a, b):
        for i in range(len(self.points) - 1):
            c = self.points[i]
            d = self.points[i + 1]
            
            if intersect(a, b, c, d):
                return True
                    
    def check_break(self, a, b):
        if self.op.visible:
            if self.check_intersect(a, b):
                self.op.clear()
                
    def is_bad(self):
        onode = self.op.node
        in_flow = onode.get_in_flow()
        if in_flow:
            if not in_flow.connection:
                return True
            else:
                return in_flow.wire.is_bad()
                
    def clip(self):
        Manager.manager.del_wire(self)
        
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

    def draw(self, win):
        if self.op.visible and self.ip.visible:
            c = self.op.get_color()
            if not self.bad:
                pg.draw.lines(win, c, False, self.points, width=2)
            else:
                for i in range(0, len(self.dashed_points) - 1, 2):
                    p0 = self.dashed_points[i]
                    p1 = self.dashed_points[i + 1]
                    pg.draw.line(win, c, p0, p1, width=2)

class Port:
    comparison_types = ['bool', 'num', 'string', 'ps', 'cs', 'ns', 'bs', 'player', 'card']
    desc_cache = {}
    
    @classmethod
    def get_comparison_types(cls):
        return cls.comparison_types.copy()
        
    @classmethod
    def get_desc(cls, desc):
        if desc not in cls.desc_cache:
            cls.desc_cache[desc] = Textbox(desc, tsize=15, bgcolor=(0, 0, 0))
        return cls.desc_cache[desc]
        
    @staticmethod
    def new_connection(p0, p1, force=False, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if (any(t in p1.types for t in p0.types) or force) and p0.is_output() != p1.is_output():
        
            p0.connect(n1, p1)
            p1.connect(n0, p0)
            
            local_funcs, scope_output, loop_output = Mapping.check_bad_connection(n0, n1)
            can_connect0 = n0.can_connect(p0, n1, p1)
            can_connect1 = n1.can_connect(p1, n0, p0)
            if not can_connect0 or not can_connect1 or (len(local_funcs) > 1 or scope_output or loop_output):
                p0.clear()
                p1.clear()
                
            else:
                Manager.manager.new_wire(p0, p1)
                if hasattr(n0, 'on_connect'):
                    n0.on_connect(p0)
                if hasattr(n1, 'on_connect'):
                    n1.on_connect(p1) 
                if not d:
                    Manager.manager.add_log({'t': 'conn', 'nodes': (n0, n1), 'ports': (p0, p1)})

        p0.close_wire()
        p1.close_wire()
        n0.prune_extra_ports()
        n1.prune_extra_ports()
    
    @staticmethod
    def disconnect(p0, p1, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if not d:
            Manager.manager.add_log({'t': 'disconn', 'ports': (p0, p1), 'nodes': (n0, n1)})
            
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
   
    def __init__(self, port, types, desc=None):
        self.port = port
        self.types = types
     
        self.parent_port = None
        self.group_node = None
        self.node = None
                
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
        
    def copy(self):
        n = self.node
        port = min([p.port for p in n.get_output_ports()]) - 1
        types = self.types
        p = Port(port, types)
        p.parent_port = self.port
        p.node = self.node
        p.group_node = self.group_node
        p.rect = self.rect.copy()
        p.desc = self.desc
        p.open_wire()
        n.ports.append(p)
        if self.group_node:
            self.group_node.ports.append(p)
        return p
        
#color stuff-------------------------------------------------------------------
        
    def get_color(self):
        if not self.types:
            return (0, 0, 0)
        main_type = self.types[0]
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
     
    def get_contains_color(self):
        types = self.types
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
                Manager.manager.add_log({'t': 'suppress', 's': suppressed, 'p': self})
         
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

class Node(Dragger):
    isnode = True
    def __init__(self, id, name, ports, pos=(width // 2, height // 2), val=None, type=None, color=(100, 100, 100)):
        self.id = id
        self.name = name
        self.type = type
        self.val = val
        
        self.ports = ports
        if not self.is_group():
            for p in self.ports:
                p.node = self

        self.ctimer = 0
        self.visible = True
        
        self.color = color
        self.tcolor = (255, 255, 255)
        self.image = self.get_image()

        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.big_rect = pg.Rect(0, 0, self.rect.width + 10, self.rect.height + 10)
        self.big_rect.center = self.rect.center
        
        self.elements = self.get_elements()

        super().__init__()
        self.set_port_pos()
 
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def copy(self):
        return Manager.manager.get_node(type(self).__name__)
        
    def is_group(self):
        return isinstance(self, GroupNode)
        
    def is_input(self):
        return hasattr(self, 'input')
        
    def is_flow(self):
        return any('flow' in p.types for p in self.ports)
        
    def can_transform(self):
        return hasattr(self, 'transform')
        
    def set_name(self, name):
        self.name = name
        self.image = self.get_image()
        
#image and element stuff-------------------------------------------------------------------

    def set_visibility(self, visible):
        self.visible = visible

    def get_image(self):
        if isinstance(self, (Num, Bool)):
        
            image = pg.Surface((50, 40)).convert()
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name)
            r = pg.Rect(0, 0, w, 10)
            r.topleft = image.get_rect().topleft
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        elif isinstance(self, String):
            
            image = pg.Surface((100, 50)).convert()
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name)
            r = pg.Rect(0, 0, w, 10)
            r.topleft = image.get_rect().topleft
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        else:
            
            w = 40
            h = 40
            side_ports = max(len(self.get_output_ports()), len(self.get_input_ports()))
            if side_ports > 3:
                h += (10 * side_ports)
            image = pg.Surface((w, h)).convert()
            if self.type == 'func':
                self.color = (100, 255, 100)
                self.tcolor = (0, 0, 0)
            elif self.is_group():
                self.color = (255, 100, 100)
                self.tcolor = (0, 0, 0)
            elif self.is_flow():
                self.color = (100, 100, 255)
                self.tcolor = (0, 0, 0)
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name, fgcolor=self.tcolor)
            r = pg.Rect(0, 0, w - 5, h - 5)
            r.center = image.get_rect().center
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        return image
        
    def get_elements(self):
        elements = {}
        
        if isinstance(self, Num):
            check = lambda t: (t + '0').strip('-').isnumeric()
            length = 3
        
        elif isinstance(self, Bool):
            check = lambda t: t.lower() in ('', 't', 'f')
            length = 1
            
        elif isinstance(self, String):
            check = lambda t: t.count("'") < 3
            length = 50
            
        else:
            return elements
            
        i = Input((self.rect.width - 10, 15 if length != 50 else 30), message=self.val, tcolor=(255, 255, 255), color=(0, 0, 0), check=check, length=length, fitted=True)
        i.rect.center = self.rect.center
        i.rect.y += 5
        elements[i] = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)
        self.input = i

        return elements

    def get_string_val(self):
        if self.val:
            return list(self.elements)[0].get_message()
            
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
            
        step = h // (len(op) + 1)
        for i, y in enumerate(range(self.rect.top + step, self.rect.bottom, step)):
            if i in range(len(op)):
                op[i].rect.center = (self.rect.right, y)
                
        for ep in ex:
            ep.rect.center = ep.get_parent_port().rect.center

        self.big_rect.center = self.rect.center
        
        sx, sy = self.rect.topleft
        for e in self.elements:
            rx, ry = self.elements[e]
            e.rect.topleft = (sx + rx, sy + ry)

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
        if hasattr(self, 'input'):
            self.input.close()
  
    def prune_extra_ports(self):
        for p in self.ports.copy():
            if p.parent_port and not p.connection:
                self.ports.remove(p)
            p.close_wire()
     
    def new_output_port(self, parent):
        p = parent.copy()
        self.set_stuck(True)
        Manager.manager.set_active_node(self)
        return p
 
    def create_in_indicator(self, port):
        if 'bool' in port.types:
            name = 'Bool'
        elif 'num' in port.types:
            name = 'Num'
        elif 'string' in port.types:
            name = 'String'
        elif 'player' in port.types:
            name = 'Player'
        else:
            return 

        n = Manager.manager.get_node(name)
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
                    Manager.manager.set_active_node(self)                            
                elif 'flow' not in port.types:
                    self.new_output_port(port)
                        
            elif port.port > 0:
                if not port.connection:
                    if dub_click:
                        self.create_in_indicator(port)
                        
        if button == 1:
            if self.can_transform() and hit and dub_click and not port:
                log = {'t': 'transform', 'n': self}
                Manager.manager.add_log(log)
                t0 = {p.port: p.types.copy() for p in self.ports}
                self.transform()
                t1 = {p.port: p.types.copy() for p in self.ports}
                log['types'] = (t0, t1)
        
    def click_up(self, button, hit, port):
        if port:
            
            an = Manager.manager.get_active_node()
            
            if button == 1:
                if an and an is not self:
                    if not port.connection:
                        p0 = an.get_active_port()
                        p1 = port
                        Port.new_connection(p0, p1)
                        Manager.manager.close_active_node()
                    elif 'flow' not in port.types:
                        p0 = self.new_output_port(port)
                        p1 = an.get_active_port()
                        Port.new_connection(p0, p1)
                        Manager.manager.close_active_node()

            elif button == 3:
                self.suppress_port(port)

    def events(self, input):
        mp = pg.mouse.get_pos()
        
        hit_node = self.rect.collidepoint(mp)
        hit_port = None
        for p in self.ports:
            if p.visible:
                if p.rect.collidepoint(mp):
                    hit_port = p
                    break
        
        for e in input:
            if e.type == pg.MOUSEBUTTONDOWN:
                self.click_down(e.button, hit_node, hit_port)
            elif e.type == pg.MOUSEBUTTONUP:
                self.click_up(e.button, hit_node, hit_port)
            
        for e in self.elements:
            e.events(input)
            
        if self.is_input():
            if self.input.active:
                self.drop()
            
#update stuff-------------------------------------------------------------------
        
    def update(self):
        if self.visible:
            dx, dy = super().update()
            for p in self.ports:
                p.rect.move_ip(dx, dy)
            self.big_rect.move_ip(dx, dy)            
            for e in self.elements:
                e.rect.move_ip(dx, dy)
                e.update()

            if self.ctimer < 30:
                self.ctimer += 1
                
            if not self.get_active_port():
                self.prune_extra_ports()
                if self._stuck:
                    self.set_stuck(False)
                
            if self.is_input():
                logs = self.input.get_logs()
                if logs:
                    for log in logs:
                        Manager.manager.add_log(log)
        
#draw stuff-------------------------------------------------------------------
        
    def draw(self, win):
        if self._selected or self._hover:
            win.blit(rect_outline(self.image, color=(255, 0, 0)), self.rect)
        else:
            win.blit(self.image, self.rect)

        mp = pg.mouse.get_pos()
        for p in self.ports:
            if p.visible and not p.parent_port:
            
                if not p.suppressed:
                    r = p.rect.width // 2
                else:
                    r = 3
                pg.draw.circle(win, p.get_color(), p.rect.center, r)
                
                if not p.suppressed:
                    contains = p.get_contains()
                    if contains:
                        pg.draw.circle(win, p.get_contains_color(), p.rect.center, r - 2)
                        
                if p.rect.collidepoint(mp):
                    p.desc.rect.centerx = p.rect.centerx
                    p.desc.rect.y = self.rect.bottom + 5
                    p.desc.draw(win)
                
        for e in self.elements:
            e.draw(win)
            
    def draw_at(self, surf, c):
        new_rect = self.rect.copy()
        new_rect.center = c
        dx = new_rect.x - self.rect.x
        dy = new_rect.y - self.rect.y
        
        surf.blit(self.image, new_rect)

        for p in self.ports:
            p_rect = p.rect.move(dx, dy)
            r = p_rect.width // 2
            pg.draw.circle(surf, p.get_color(), p_rect.center, r)
            contains = p.get_contains()
            if contains:
                pg.draw.circle(surf, p.get_contains_color(), p_rect.center, r - 2)

    def draw_wire(self, win):
        p = self.get_active_port()
        if p:
            pg.draw.line(win, p.get_color(), p.rect.center, pg.mouse.get_pos(), width=3)
            
class GroupNode(Node):
    def __init__(self, id, nodes, name='group'):
        self.nodes = nodes
        ports = self.get_group_ports(nodes)
        super().__init__(id, name, ports)
        self.set_self_pos()
        self.set_rel_node_pos()
        
    def reset_ports(self):
        self.ports = self.get_group_ports(self.nodes)
        self.set_port_pos()
   
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
            n.set_visibility(False)
            
            for ip in n.get_input_ports():
                if not ip.suppressed and ip.connection not in nodes:
                    ip.group_node = self
                    ipp.append(ip)
                else:
                    ip.set_visibility(False)
                    
            for op in n.get_output_ports():
                if not op.suppressed and op.connection not in nodes:
                    op.group_node = self
                    opp.append(op)
                else:
                    op.set_visibility(False)

        ipp.sort(key=lambda p: p.port)
        ports = opp + ipp
        
        return ports
       
    def set_self_pos(self):
        self.rect.centerx = sum(n.rect.centerx for n in self.nodes) // len(self.nodes)
        self.rect.centery = sum(n.rect.centery for n in self.nodes) // len(self.nodes)
        self.set_port_pos()

    def ungroup(self):
        sx, sy = self.rect.center
        for n in self.nodes:
            n.set_visibility(True)
            for p in n.ports:
                if p.types:
                    p.set_visibility(True)
                p.group_node = None
            rx, ry = self.rel_node_pos[n]
            n.rect.center = (sx + rx, sy + ry)
            n.set_port_pos()
            n.drop()
        
    def new_output_port(self, parent):
        n = parent.node
        p = parent.copy()
        self.set_stuck(True)
        Manager.manager.set_active_node(n)
        return p
        
    def update(self):
        for n in self.nodes:
            n.update()
            
        super().update()

class Start(Node):
    info = "This node is a function. Function nodes are green. They have no in-flow ports and a single out-flow port. When a card is played, this is the first process that will be run. Every play card has a 'Start' function."
    def __init__(self, id):
        super().__init__(id, 'start', [Port(-1, ['flow'], desc='flow')], type='func')
        
    def get_start(self):
        return '\t\tself.reset()\n'
        
    def get_text(self):
        return '\n\tdef start(self, player):\n'
   
class If(Node):
    info = 'If the boolean input is True, the split path is run before continuing the main path. If it is False, the split path is skipped.'
    tips = 'If nodes can evaluate all kinds of data, not just boolean values.\n\nIf you plug in a number, if the number is not 0 it will evaluate to True, otherwise False.\n\nIf you plug in a list, if the list is not empty it will evaluate to True, otherwise False.\n\n'
    ip1 = 'This boolean argument decides if the split path is run or skipped'
    op2 = "This out-flow port can be wired to an 'elif' node or an 'else' node."
    def __init__(self, id):
        super().__init__(id, 'if', [Port(1, Port.get_comparison_types(), desc='condition'), Port(2, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
        
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'if {0}:\n'.format(*self.get_input())   
        return text
        
class Elif(Node):
    info = "This node can only be placed after 'if' or 'elif' nodes. If the previous node is evaluated to be False, this node will be evaluated as an 'if' node. If the previous node is evaluated to be True, this whole node will be skipped."
    tips = 'Elif nodes can evaluate all kinds of data, not just boolean values.\n\nIf you plug in a number, if the number is not 0 it will evaluate to True, otherwise False.\n\nIf you plug in a list, if the list is not empty it will evaluate to True, otherwise False.\n\n'
    ip1 = 'This boolean argument decides if the split path is run or skipped' 
    ip2 = "This in-flow port can only be wired to the out-flow of an 'if' node or another 'elif' node."
    op2 = "This out-flow port can be wired to an additional 'elif' node or an 'else' node."
    def __init__(self, id):
        super().__init__(id, 'elif', [Port(1, Port.get_comparison_types(), desc='condition'), Port(2, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
 
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return n1.name == 'if'
        return True
 
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'elif {0}:\n'.format(*self.get_input())   
        return text
        
class Else(Node):
    info = "This node can only be placed after 'if' or 'elif' nodes. If all previous nodes are evaluated to be False, this node will run its split path. Otherwise, the split path will be skipped."
    ip1 = "This in-flow port can only be wired to the out-flow of an 'if' or 'elif' node."
    def __init__(self, id):
        super().__init__(id, 'else', [Port(1, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['flow'])])
        
    def can_connect(self, p0, n1, p1):
        if p0.port == 2:
            return n1.name == 'if' or name == 'elif'
        return True
        
    def get_text(self):
        text = 'else:\n'  
        return text
        
class Bool(Node):
    info = "Produces a boolean value of either True or False. Type 'T' or 't' for True, and 'F' for 'f' for False."
    tips = "If a node requires a boolean input, double click on the boolean input port to spawn a 'Bool' node that will automatically be wired into the port."
    op1 = "Boolean value. Defaults to True"
    def __init__(self, id, val='T'):
        super().__init__(id, 'bool', [Port(-1, ['bool'])], val=val, type='var')
        
    def get_actual_value(self):
        return self.get_string_val().lower() == 't'

    def get_output(self, p):
        val = self.get_string_val()
        if val.lower() == 't':
            return 'True'
        else:
            return 'False'
        
class Num(Node):
    info = "Produces a numeric value. The value can be either positive or negative. Floating point numbers are not allowed."
    tips = "If a node requires a numeric input, double click on the numeric input port to spawn a 'Num' node that will automatically be wired into the port."
    op1 = 'Numeric value'
    def __init__(self, id, val='0'):
        super().__init__(id, 'num', [Port(-1, ['num'])], val=val, type='var')
        
    def get_val(self):
        return self.val

    def get_output(self, p):
        val = self.get_string_val()
        if not val.strip('-'):
            val = '0'
        return int(val)
        
class String(Node):
    info = "Produces a string of characters. These are often used to access card names and tags which are stored as string values. Player decks also must be accessed using string values that represent the name of the deck."
    tips = "If a node requires a string input, double click on the string input port to spawn a 'string' node that will automatically be wired into the port."
    op1 = 'String value'
    def __init__(self, id, val="''"):
        super().__init__(id, 'string', [Port(-1, ['string'])], val=val, type='var')
        
    def get_output(self, p):
        val = self.get_string_val()
        return f"'{val.lower()}'"
        
class And(Node):
    info = "Used to compare two boolean values. This node will output True if and only if both input values are True, otherwise False."
    tips = 'And nodes can evaluate all kinds of data, not just boolean values.\n\nIf you plug in a number, if the number is not 0 it will evaluate to True, otherwise False.\n\nIf you plug in a list, if the list is not empty it will evaluate to True, otherwise False.\n\n'
    ip1 = 'Boolean input (x)'
    ip2 = 'Boolean input (y)'
    op1 = "If x is True and y is True, this port will output True, otherwise it will output False."
    def __init__(self, id):
        super().__init__(id, 'and', [Port(1, Port.get_comparison_types(), desc='x'), Port(2, Port.get_comparison_types(), desc='y'), Port(-1, ['bool'], desc='x and y')])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} and {})'.format(*self.get_input())     
        return text
        
class Or(Node):
    info = "Used to compare two boolean values. This node will output True if one or both input values are True, otherwise False."
    tips = 'Or nodes can evaluate all kinds of data, not just boolean values.\n\nIf you plug in a number, if the number is not 0 it will evaluate to True, otherwise False.\n\nIf you plug in a list, if the list is not empty it will evaluate to True, otherwise False.\n\n'
    ip1 = 'Boolean input (x)'
    ip2 = 'Boolean input (y)'
    op1 = "If x is True or y is True or both x and y are True, this port will output True, otherwise it will output False."
    def __init__(self, id):
        super().__init__(id, 'or', [Port(1, Port.get_comparison_types(), desc='x'), Port(2, Port.get_comparison_types(), desc='y'), Port(-1, ['bool'], desc='x or y')])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} or {})'.format(*self.get_input())     
        return text
        
class Not(Node):
    info = "Used to flip a boolean value. If the input is True, it will output False, and vice-versa."
    ip1 = 'Boolean input'
    op1 = "If the input is True, this port will output False. If it is False it will output True."
    def __init__(self, id):
        super().__init__(id, 'not', [Port(1, Port.get_comparison_types(), desc='x'), Port(-1, ['bool'], desc='not x')])
        
    def get_default(self, p):
        return 'True'

    def get_output(self, p):
        text = '(not {})'.format(*self.get_input())    
        return text
        
class Equal(Node):
    info = "Used to compare two input values. If they are the same, this node will output True, otherwise False."
    tips = "This node can evaluate the equality if almost any type of data including players, cards, lists, numbers and strings. Inputting two different data types will always yeild 'False'"
    ip1 = 'value x'
    ip2 = 'value y'
    op1 = "True if x and y are equal, otherwise False."
    def __init__(self, id):
        types = Port.get_comparison_types()
        types = types[1:] + [types[0], 'string']
        super().__init__(id, 'equal', [Port(1, types, desc='x'), Port(2, types.copy(), desc='y'), Port(-1, ['bool'], desc='x == y')])
        
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
    info = "Used to compare two numeric values. This node will output True if the first is greater than the second input, otherwise False."
    tips = "This node is not like the 'Equal' node, and can only be used to compare numeric values."
    ip1 = 'Numeric input (x), defaults to 0'
    ip2 = 'Numeric input (y), defaults to 0'
    op1 = "If x > y this port will output True, otherwise it will output False."
    def __init__(self, id):
        super().__init__(id, 'greater', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['bool'], desc='x > y')])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} > {1})'.format(*self.get_input())    
        return text
        
class Less(Node):
    info = "Used to compare two numeric values. This node will output True if the first is less than the second input, otherwise False."
    tips = "This node is not like the 'Equal' node, and can only be used to compare numeric values."
    ip1 = 'Numeric input (x), defaults to 0'
    ip2 = 'Numeric input (y), defaults to 0'
    op1 = "If x < y this port will output True, otherwise it will output False."
    def __init__(self, id):
        super().__init__(id, 'less', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['bool'], desc='x < y')])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} < {1})'.format(*self.get_input())    
        return text
     
class Max(Node):
    info = "Use this node to find the max value in a numeric sequence. This node is only used when evaluating roll results from a deployed card."
    ip1 = 'Numeric sequence'
    op1 = "Max value from input sequence."
    def __init__(self, id):
        super().__init__(id, 'max', [Port(1, ['ns'], desc='[0, 1, 2...]'), Port(-1, ['num'], desc='max value')])
        
    def get_default(self, p):
        return '[]'

    def get_output(self, p):
        text = 'max({0}, 0)'.format(*self.get_input())    
        return text
        
class Min(Node):
    info = "Use this node to find the min value in a numeric sequence. This node is only used when evaluating roll results from a deployed card."
    ip1 = 'Numeric sequence'
    op1 = "Min value from input sequence."
    def __init__(self, id):
        super().__init__(id, 'min', [Port(1, ['ns'], desc='[0, 1, 2...]'), Port(-1, ['num'], desc='min value')])
        
    def get_default(self, p):
        return '[]'

    def get_output(self, p):
        text = 'min({0}, 0)'.format(*self.get_input())    
        return text
     
class Add(Node):
    info = "Outputs the sum of two numeric inputs."
    ip1 = 'Numeric input (x)'
    ip2 = 'Numeric input (y)'
    op1 = "x + y"
    def __init__(self, id):
        super().__init__(id, 'add', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x + y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Incriment(Node):
    info = "Outputs a numeric input + 1."
    tips = "This node if often used to obtain the index below this card. use the 'self index' node and incriment to obtain the index below."
    ip1 = 'Numeric input x'
    op1 = "x + 1"
    def __init__(self, id):
        super().__init__(id, 'incriment', [Port(1, ['num'], desc='x'), Port(-1, ['num'], desc='x + 1')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({} + 1)'.format(*self.get_input())
        
class Subtract(Node):
    info = "Outputs the difference of two numeric inputs."
    ip1 = 'Numeric input (x)'
    ip2 = 'Numeric input (y)'
    op1 = "x - y"
    def __init__(self, id):
        super().__init__(id, 'subtract', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x - y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} - {1})'.format(*self.get_input())
        
class Multiply(Node):
    info = "Outputs the product of two numeric inputs."
    ip1 = 'Numeric input (a)'
    ip2 = 'Numeric input (b)'
    op1 = "a * b"
    def __init__(self, id):
        super().__init__(id, 'multiply', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x * y')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} * {1})'.format(*self.get_input())
        
class Negate(Node):
    info = "Outputs the additive inverse of a numeric input."
    tips = "This node will convert positive numbers to negative, and negative numbers to positive. It is the equivalent of multiplying by -1."
    ip1 = 'Numeric input a'
    op1 = "-a"
    def __init__(self, id):
        super().__init__(id, 'negate', [Port(1, ['num'], desc='x'), Port(-1, ['num'], desc='-x')])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '(-1 * {0})'.format(*self.get_input())
        
class Divide(Node):
    info = "Outputs the quotient of two numeric inputs."
    tips = "This operation uses floor division meaning the output will always be rounded to the nearest integer."
    ip1 = 'Numeric input (a)'
    ip2 = 'Numeric input (b)'
    op1 = "a / b"
    def __init__(self, id):
        super().__init__(id, 'divide', [Port(1, ['num'], desc='x'), Port(2, ['num'], desc='y'), Port(-1, ['num'], desc='x / y')])
        
    def get_default(self, p):
        return str(p)
        
    def get_output(self, p):
        return '({0} // {1})'.format(*self.get_input())
  
class Exists(Node):
    info = "Outputs True if the input is not a None value, otherwise False."
    tips = "This node is often used to validate a card or player output. For example, the 'Safe Index' node allows you to index a deck. If there is no value at the index, it will return a None value."
    ip1 = 'Takes either a player or card argument.'
    op1 = "Input is not None"
    def __init__(self, id):
        super().__init__(id, 'exists', [Port(1, ['player', 'card'], desc='x'), Port(-1, ['bool'], desc='x is not None')])
        
    def get_default(self, p):
        return '1'
        
    def get_output(self, p):
        return '{0} is not None'.format(*self.get_input())
  
class For(Node):
    info = "This node can be used to pull out each individual value from a list and run a process on them. Plug in a list of values to port 1. The port -1 will then open up with the type of values that the list contains. If an empty list is plugged in, the split path will be skipped."
    tips = "Say you want all players to gain 5 points. Just plug in a list containing all players, then add in a 'Gain' node wired to port -2. Finally wire in the output player to the 'Gain' node."
    ip1 = 'This input takes any type of list.'
    op1 = "This port will output a value corresponding to the type of list at the input. This value represents each individual value in the input list. The output value can only be wired to nodes within the split path."
    op2 = "This split path will run for each value in the input list. If the list is empty, this split path will be skipped."
    def __init__(self, id):
        super().__init__(id, 'for', [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list'), Port(2, ['flow']), Port(-1, [], desc='list value'), Port(-2, ['split', 'flow']), Port(-3, ['flow'])])  

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
        
class ZippedFor(Node):
    info = "This node can be used to pull out each individual value from two lists at the same time and run a process on them. Plug in two lists of values to ports 1 and 2. Ports -1 and -2 will then open up with the type of values that their corresponding list contains."
    tips = "This node is most commonly used to check flip, roll and selection results. The 'Get _ Results' nodes will output a list of players and a list of results. You can plug in those lists to this node to get player and result pairs."
    ip1 = 'This input takes any type of list.'
    ip2 = ip1
    op1 = "This port will output a value corresponding to the type of list at port 1. This value represents each individual value in the input list. The output value can only be wired to nodes within the split path."
    op2 = "This port will output a value corresponding to the type of list at port 2. This value represents each individual value in the input list. The output value can only be wired to nodes within the split path."
    op3 = "This split path will run for each value pair in the input lists. If both lists are empty, this split path will be skipped."
    def __init__(self, id):
        super().__init__(id, 'zipped for', [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list 1'), Port(2, ['cs', 'ps', 'ns', 'bs'], desc='list 2'), Port(3, ['flow']), Port(-1, [], desc='value 1'), Port(-2, [], desc='value 2'), Port(-3, ['split', 'flow']), Port(-4, ['flow'])])  

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
    info = "This node can be used to exit a 'For' node split path prematurly. If you are only looking for a specific result, you can place this node after it is found to return to the main path."
    tips = "This node can only be used within the split path of a 'For' or 'Zipped For' node."
    def __init__(self, id):
        super().__init__(id, 'break', [Port(1, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        if ip.connection:
            ports = Mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if p.connection.name in ('for', 'zipped for') and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def get_text(self):
        return 'break\n'
        
class Continue(Node):
    info = "This node can be used to skip to the next value in a 'For' node split path. If you don't want to evaluate a value, use this node to skip to the next."
    tips = "This node can only be used within the split path of a 'For' or 'Zipped For' node."
    def __init__(self, id):
        super().__init__(id, 'continue', [Port(1, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        if ip.connection:
            ports = Mapping.map_ports(self, [], skip_op=True, in_type='flow')
            for p in ports:
                if p.connection:
                    if p.connection.name in ('for', 'zipped for') and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear()
        
    def get_text(self):
        return 'continue\n'
        
class Range(Node):
    info = "This node outputs a list of numbers between the two input values. If the input values are the same, the list will be empty."
    tips = "This node is usually used when checking each index of a deck. Use the 'Length' node to generate a range of indicies based on the length of the deck. Then loop over those indecies with a 'For' node, using the 'Check Index' node."
    ip1 = "This numeric input is where the range will start. The default value is 0 so if you need numbers between 0 and an upper value you can leave this port blank."
    ip2 = "This numeric input is where the range ends. If you need to check each index of a deck, you will want to input the length of the deck at this port."
    op1 = "A list of numbers."
    def __init__(self, id):
        super().__init__(id, 'range', [Port(1, ['num'], desc='min'), Port(2, ['num'], desc='max'), Port(-1, ['ns'], desc='[min, ..., max]')])
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '1'
        
    def get_output(self, p):
        text = 'range({0}, {1})'.format(*self.get_input()) 
        return text
       
class Player(Node):
    info = "This node returns the player in any given scope. The player is the player who plays your card."
    tips = "The actual player this node represents could change depending on where it is used. If you use a 'Deploy' node to deploy cards to opponents to request that they flip a coin, In the 'Flip' function, this node will represent your opponents."
    op1 = "A player value. Any time a node requires a player input, this will almost always be the default value."
    def __init__(self, id):
        super().__init__(id, 'player', [Port(-1, ['player'], desc='player')])  

    def get_output(self, p):
        return 'player'
       
class Players(Node):
    info = "This node returns a list of all players."
    op1 = "A list of all players"
    def __init__(self, id):
        super().__init__(id, 'all players', [Port(-1, ['ps'], desc='player list')])

    def get_output(self, p):
        return 'self.game.players.copy()'
        
class SelfPlayers(Node):
    info = "This node returns a list of stored players. Players can be added to or removed from this list."
    tips = "Any time you call a 'Deploy' node, this list will be emptied and populated with new player values from the players passed to the 'Deploy' node."
    op1 = "A list of stored players"
    def __init__(self, id):
        super().__init__(id, 'stored players', [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return 'self.players'
        
class SelfCards(Node):
    info = "This node returns a list of stored cards. Cards can be added to or removed from this list."
    tips = "Any time you call a 'Deploy' node, this list will be emptied and populated with new card values."
    op1 = "A list of stored cards"
    def __init__(self, id):
        super().__init__(id, 'stored cards', [Port(-1, ['cs'], desc='card list')])
        
    def get_output(self, p):
        return 'self.cards'
        
class Opponents(Node):
    info = "This node returns a list of all opponents. The player who played the card is filtered out."
    op1 = "A list of opponents"
    def __init__(self, id):
        super().__init__(id, 'opponents', [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return 'self.sort_players(player)'
        
class StealOpp(Node):
    info = "This node returns a list of all opponents who have points."
    tips = "You cannot steal points from a player with a score of 0 so use this node when you want to ensure you get a list of players who have points."
    op1 = "A list of all players with a score greater than 0"
    def __init__(self, id):
        super().__init__(id, 'opponents with points', [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return '[p for p in self.game.players if p.score > 0]'
      
class Self(Node):
    info = "This node returns a reference to your card."
    op1 = "Your card"
    def __init__(self, id):
        super().__init__(id, 'card', [Port(-1, ['card'], desc='this card')])  

    def get_output(self, p):
        return 'self'
      
class Length(Node):
    info = "This node returns the number of values in a list."
    ip1 = "Any type of list"
    op1 = "Length of the given list"
    def __init__(self, id):
        super().__init__(id, 'length', [Port(1, ['ps', 'cs', 'ns', 'bs'], desc='list'), Port(-1, ['num'], desc='length of list')])   
        
    def get_default(self, port):
        return '[]'
        
    def get_output(self, p):
        return 'len({})'.format(*self.get_input())
      
class NewList(Node):
    info = "This node declares a new empty list. Double click the node to swap between a player list and a card list."
    tips = "Often times you will want to use this node to create a new list of filtered values from a larger list based on some criteria. Use a 'For' node to check each value in the larger list. If the value meets some criteria, add it to your new list."
    op1 = "A brand new empty list."
    def __init__(self, id):
        super().__init__(id, 'new list', [Port(-1, ['ps'], desc='list')], type='dec') 

    def transform(self):
        self.clear_connections()
        op = self.get_port(-1)
        if 'ps' in op.types:
            op.set_types(['cs'])
        elif 'cs' in op.types:
            op.set_types(['ps'])
            
    def get_dec(self):
        return f'ls{self.id} = []\n'
        
    def get_output(self, p):
        return f'ls{self.id}'

class MergLists(Node):
    info = "This node returns a new list with values from both input lists."
    tips = "Double click to swap between merging player lists and card lists."
    ip1 = 'List 1'
    ip2 = 'List 2'
    op1 = "New list containing values from list 1 and list 2."
    def __init__(self, id):
        super().__init__(id, 'merge lists', [Port(1, ['ps'], desc='list 1'), Port(2, ['ps'], desc='list 2'), Port(-1, ['ps'], desc='list 1 + list 2')])  
        
    def transform(self):
        self.clear_connections()
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
        
class MergLists_ip(Node):
    info = "This node adds all values from list 2 to list 1."
    tips = "Double click to swap between player lists and card lists."
    ip1 = "All values from this list will be added to the list at port 2"
    ip2 = 'All values from the list at port 1 will be added to this list.'
    def __init__(self, id):
        super().__init__(id, 'merge lists in place', [Port(1, ['ps'], desc='merging list'), Port(2, ['ps'], desc='original list'), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def transform(self):
        self.clear_connections()
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
       
class AddTo(Node):
    info = "This node adds a value to a list."
    tips = "Double click to swap between player lists, and card lists."
    ip1 = 'List to add value to'
    ip2 = 'Value to add to list'
    def __init__(self, id):
        super().__init__(id, 'add to', [Port(1, ['cs'], desc='value'), Port(2, ['card'], desc='list'), Port(3, ['flow']), Port(-1, ['flow'])])

    def transform(self):
        self.clear_connections()
        
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
        
class RemoveFrom(Node):
    info = "This node removes a value from a list. If the given value is not in the list, an error will be raised. Make sure to check if the value is in the list before attempting to remove it."
    tips = "Double click to swap between player lists, and card lists."
    ip1 = 'List to remove value from'
    ip2 = 'Value to remove from list'
    def __init__(self, id):
        super().__init__(id, 'remove from', [Port(1, ['cs'], desc='list'), Port(2, ['card'], desc='value'), Port(3, ['flow']), Port(-1, ['flow'])])

    def transform(self):
        self.clear_connections()
        
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
        
class ClearList(Node):
    info = "This node removes all values from a=the given list."
    ip1 = 'List to clean'
    def __init__(self, id):
        super().__init__(id, 'clear list', [Port(1, ['cs', 'ps'], desc='list'), Port(2, ['flow']), Port(-1, ['flow'])])
        
    def get_default(self, p):
        return '[]'

    def get_text(self):
        return "{0}.clear()\n".format(*self.get_input())

class Contains(Node):
    info = "This node checks if a value is in a list. If the value is found, it returns True, otherwise False."
    tips = "Use this node to check if a value is in a list before attempting to remove it."
    ip1 = 'List to check for value in'
    ip2 = 'Value to check for'
    op1 = "Returns True if value is in list, and False if not."
    def __init__(self, id):
        super().__init__(id, 'contains', [Port(1, ['ps', 'cs'], desc='list'), Port(2, ['player', 'card'], desc='value'), Port(-1, ['bool'], desc='value in list')])  

    def transform(self):
        self.clear_connections()
        p = self.get_port(2)
        p.types.reverse()
        
    def get_default(self, p):
        if p == 1:
            return '[]'
        elif p == 2:
            return '0'
        
    def get_output(self, p):
        text = '({1} in {0})'.format(*self.get_input())
        return text
  
class HasTag(Node):
    info = "This node can be used to check if a card has a specific tag. It will return True if the card has the tag, and False if not."
    ip1 = 'Tag to check for'
    ip2 = 'Card to evaluate'
    op1 = "Returns True if the card has the tag, and False if not."
    def __init__(self, id):
        super().__init__(id, 'has tag', [Port(1, ['string'], desc='tag'), Port(2, ['card'], desc='card'), Port(-1, ['bool'], desc='card has tag')])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({0} in {1}.tags)'.format(*self.get_input())
        return text
      
class GetName(Node):
    info = "This node returns the name of a card."
    ip1 = 'Card'
    op1 = 'Name of card'
    def __init__(self, id):
        super().__init__(id, 'get name', [Port(1, ['card'], desc='card'), Port(-1, ['string'], desc='card name')])   
        
    def get_default(self, p):
        return 'self'
        
    def get_output(self, p):
        text = '{0}.name'.format(*self.get_input())
        return text 
      
class HasName(Node):
    info = "This node returns True if the given card has the given name, and False if it does not."
    ip1 = 'Name'
    ip2 = 'Card'
    op1 = 'Returns True if the given card has the given name, and False if it does not.'
    def __init__(self, id):
        super().__init__(id, 'has name', [Port(1, ['string'], desc='name'), Port(2, ['card'], desc='card'), Port(-1, ['bool'], desc='card has name')])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({1}.name == {0})'.format(*self.get_input())
        return text
    
class FindOwner(Node):
    info = "This node returns the owner of a given card."
    ip1 = 'Card'
    op1 = 'Player who has card. If no owner is found, this will return a None value.'
    def __init__(self, id):
        super().__init__(id, 'find owner', [Port(1, ['card'], desc='card'), Port(-1, ['player'], desc='card owner')])   
        
    def get_default(self, p):
        return 'self'
        
    def get_output(self, p):
        text = 'self.game.find_owner({0})'.format(*self.get_input())
        return text

class TagFilter(Node):
    info = "This node returns a new list of cards that all have a given tag."
    tips = "If you don't want your card to be included in the new filtered list. set the boolean input to True."
    ip1 = 'This is the tag which will be used as filtering criteria.'
    ip2 = 'This is an optional boolean argument. If True, your card will be filtered out regardless of wheather or not it has the given tag. This will default to False.'
    ip3 = "This is the card list which will be filtered."
    op1 = 'Returns a new list of cards, all of which have the given tag.'
    def __init__(self, id):
        super().__init__(id, 'tag filter', [Port(1, ['string'], desc='tag'), Port(2, ['bool'], desc='filter self'), Port(3, ['cs'], desc='card list'), Port(-1, ['cs'], desc='cards with tag from list')])
        
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
        
class NameFilter(Node):
    info = "This node returns a new list of cards that all have a given name."
    tips = "If you don't want your card to be included in the new filtered list. set the boolean input to True."
    ip1 = 'This is the name which will be used as filtering criteria.'
    ip2 = 'This is an optional boolean argument. If True, your card will be filtered out regardless of wheather or not it has the given name. This will default to False.'
    ip3 = "This is the card list which will be filtered."
    op1 = 'Returns a new list of cards, all of which have the given name.'
    def __init__(self, id):
        super().__init__(id, 'name filter', [Port(1, ['string'], desc='name'), Port(2, ['bool'], desc='include self'), Port(3, ['cs'], desc='list'), Port(-1, ['cs'], desc='cards with name from list')])
        
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
    info = "This node adds points to a players score."
    tips = "This node only accepts positive numbers as input. Use the 'Lose' node to subtract from a players score."
    ip1 = 'The number of points that the player will gain.'
    ip2 = 'The player who will gain points. This will default to the player who played your card.'
    def __init__(self, id):
        super().__init__(id, 'gain', [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.gain(self, {0})\n'.format(*self.get_input())
        return text      

class Lose(Node):
    info = "This node subtracts points from a players score."
    tips = "This node only accepts positive numbers as input. Players cannot go into negative point values. If a player has a score of 0, they will not go any lower."
    ip1 = 'The number of points that the player will lose.'
    ip2 = 'The player who will lose points. This will default to the player who played your card.'
    def __init__(self, id):
        super().__init__(id, 'lose', [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.lose(self, {0})\n'.format(*self.get_input())
        return text      
        
class Steal(Node):
    info = "This node transfers points from one player to another."
    tips = "This node only accepts positive numbers as input."
    ip1 = 'The number of points that will be transferred.'
    ip2 = 'The player who will gain points. This will default to the player who played your card.'
    ip2 = 'The player who will lose points.'
    def __init__(self, id):
        super().__init__(id, 'steal', [Port(1, ['num'], desc='points'), Port(2, ['player']), Port(3, ['player'], desc='target'), Port(4, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p in (2, 3):
            return 'player'
        
    def get_text(self):
        text = '{1}.steal(self, {0}, {2})\n'.format(*self.get_input())
        return text      

class StartFlip(Node):
    info = "This node initiates a coin flip request. Coin flip requests must be processed in a separate process with a 'Flip' node."
    def __init__(self, id):
        super().__init__(id, 'start flip', [Port(1, ['flow'])]) 

    def get_text(self):
        pf = find_parent_func(self)
        if pf:
            if pf.name in ('flip', 'roll', 'select'):
                return "self.wait = 'flip'\n"
        return "player.add_request(self, 'flip')\n"
        
    def on_connect(self, p):
        if p.port == 1 and not Manager.manager.exists('flip'):
            Manager.manager.get_node('Flip')
            
    def check_errors(self):
        text = ''
        if not Manager.manager.exists('flip'):
            text = 'a flip node must be added to process flip results'
        return text

class Flip(Node):
    info = "This node is a function. It is used to process the results of a flip request. This process will only activate if a 'Start Flip' node is called somewhere in a separate process."
    tips = "Be careful when initiating a coin flip within a 'Flip' process. It's possible to create an endless loop of flips which will result in an 'InfiniteLoop' error being raised."
    op1 = "This port will output the result of the coin flip as a boolean value. This value will be True if the result was heads, and False if it was tails."
    def __init__(self, id):
        super().__init__(id, 'flip', [Port(-1, ['bool'], desc='flip result'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tself.t_coin = coin\n'
            
    def get_text(self):
        return '\n\tdef coin(self, player, coin):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'coin'

class StartRoll(Node):
    info = "This node initiates a dice roll request. Dice roll requests must be processed in a separate process with a 'Roll' node."
    def __init__(self, id):
        super().__init__(id, 'start roll', [Port(1, ['flow'])]) 
        
    def get_text(self):
        pf = find_parent_func(self)
        if pf:
            if pf.name in ('flip', 'roll', 'select'):
                return "self.wait = 'roll'\n"
        return "player.add_request(self, 'roll')\n"
        
    def on_connect(self, p):
        if p.port == 2 and not Manager.manager.exists('roll'):
            Manager.manager.get_node('Roll')
            
    def check_errors(self):
        text = ''
        if not Manager.manager.exists('roll'):
            text = 'a roll node must be added to process roll results'
        return text
        
class Roll(Node):
    info = "This node is a function. It is used to process the results of a roll request. This process will only activate if a 'Start Roll' node is called somewhere in a separate process."
    tips = "Be careful when initiating a dice roll within a 'Roll' process. It's possible to create an endless loop of rolls which will result in an 'InfiniteLoop' error being raised."
    op1 = "This port will output the result of the dice roll as a numeric value. The value will be in the range 1 to 6."
    def __init__(self, id):
        super().__init__(id, 'roll', [Port(-1, ['num'], desc='roll result'), Port(-2, ['flow'])], type='func') 

    def get_start(self):
        return '\t\tself.t_coin = coin\n'
            
    def get_text(self):
        return '\n\tdef roll(self, player, dice):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'dice'
            
class StartSelect(Node):
    info = "This node initiates a select request. Select requests must be dealt with in a separate process using a 'Select' node. There must also be a 'Get Selection' process which will return a list of players or cards that the player will select from."
    def __init__(self, id):
        super().__init__(id, 'start select', [Port(1, ['flow'])]) 
        
    def on_connect(self, p):
        if p.port == 2:
            if not Manager.manager.exists('get selection'):
                Manager.manager.get_node('GetSelection', pos=(self.rect.centerx + self.rect.width + 5, self.rect.centery), held=False)
            if not Manager.manager.exists('select'):
                Manager.manager.get_node('Select', pos=(self.rect.centerx, self.rect.centery + self.rect.height + 25), held=False)

    def get_text(self):
        pf = find_parent_func(self)
        if pf:
            if pf.name in ('flip', 'roll', 'select'):
                return "self.wait = 'select'\n"
        return "player.add_request(self, 'select')\n"
        
    def check_errors(self):
        text = ''
        if not Manager.manager.exists('get selection'):
            text = 'a get selection node must be added to initiate selection process'
        elif not Manager.manager.exists('select'):
            text = 'a select node must be added to process player selection'
        return text
            
class GetSelection(Node):
    info = "This node is used to put together a list of players or cards for the player to select from. This process will only activate if a 'Start Select' node is present somewhere in a separate process. After this process returns a list, the selection that the player makes can be assessed in a separate process using a 'Select' node."
    tips = "Two lists are provided at ports -1 and -2. These lists can be used to add values to and will be automatically returned after the process. If you wish to return a different list, it must be done using the 'Return List' node. This will override the default lists."
    op1 = "This port will output the result of the dice roll as a numeric value. The value will be in the range 1 to 6."
    def __init__(self, id):
        super().__init__(id, 'get selection', [Port(-1, ['ps'], desc='selection'), Port(-2, ['cs'], desc='selection'), Port(-3, ['flow'])], type='func') 
            
    def get_start(self):
        ports = Mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if p.connection.name == 'return list':
                    return ''
        else:
            return '\t\tselection = []\n'
            
    def get_text(self):
        return '\n\tdef get_selection(self, player):\n'
        
    def get_end(self):
        ports = Mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if p.connection.name == 'return list':
                    return ''
        else:
            return '\t\treturn selection\n'
        
    def get_output(self, p):
        return 'selection'
            
    def check_errors(self):
        text = ''
        if Manager.manager.exists('start selection') and not Manager.manager.exists('select'):
            text = 'a select node must be added to process player selection'
        return text
        
class ReturnList(Node):
    def __init__(self, id):
        super().__init__(id, 'return list', [Port(1, ['cs', 'ps'], desc='list'), Port(2, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(2)
        if ip.connection:
            ports = Mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if p.connection.name == 'get selection':
                    break
            else:
                ip.clear()
        
    def get_default(self, p):
        return '[]'
        
    def get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class Select(Node):
    def __init__(self, id):
        super().__init__(id, 'select', [Port(-1, ['num'], desc='number of selected items'), Port(-2, ['player'], desc='selected player'), Port(-3, ['card'], desc='selected card'), Port(-4, ['flow'])], type='func') 
                
    def get_start(self):
        return '\t\tif not num:\n\t\t\treturn\n\t\tsel = player.selected[-1]\n\t\tself.t_select = sel\n'
            
    def get_text(self):
        return '\n\tdef select(self, player, num):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'num'
        else:
            return 'sel'
            
    def check_errors(self):
        text = ''
        if Manager.manager.exists('start selection') and not Manager.manager.exists('get select'):
            text = 'a get selection node must be added to initiate selection process'
        return text
  
class ReturnBool(Node):
    def __init__(self, id):
        super().__init__(id, 'return bool', [Port(1, ['bool'], desc='return bool'), Port(2, ['flow'])]) 
        
    def update(self):
        super().update()
        
        ip = self.get_port(2)
        if ip.connection:
            ports = Mapping.map_ports(self, [], skip_op=True)
            for p in ports:
                if p.connection.name in ('can use', 'can cast'):
                    break
            else:
                ip.clear()
        
    def get_default(self, p):
        return 'True'
        
    def get_text(self):
        return 'return {0}\n'.format(*self.get_input())

class CanCast(Node):
    def __init__(self, id):
        super().__init__(id, 'can cast', [Port(-1, ['bool'], desc='can cast'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tcancast = True\n'
            
    def get_text(self):
        return '\n\tdef can_cast(self, player):\n'
        
    def get_end(self):
        ports = map_scope(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if p.connection.name == 'return bool':
                    return ''
        else:
            return '\t\treturn cancast\n'

    def get_output(self, p):
        if p == -1:
            return 'cancast'   

class CanUse(Node):
    def __init__(self, id):
        super().__init__(id, 'can use', [Port(-1, ['bool'], desc='can use'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tcanuse = True\n'
            
    def get_text(self):
        return '\n\tdef can_use(self, player):\n'
        
    def get_end(self):
        ports = Mapping.map_ports(self, [], skip_ip=True)
        for p in ports:
            if 'flow' in p.types:
                if p.connection.name == 'return bool':
                    return ''
        else:
            return '\t\treturn canuse\n'

    def get_output(self, p):
        if p == -1:
            return 'canuse'             
  
class StartOngoing(Node):
    def __init__(self, id):
        super().__init__(id, 'start ongoing', [Port(1, ['flow'])]) 

    def on_connect(self, p):
        if p.port == 1:
            if not Manager.manager.exists('init ongoing'):
                Manager.manager.get_node('InitOngoing', pos=(self.rect.centerx + self.rect.width + 5, self.rect.centery), held=False)
            if not Manager.manager.exists('add to ongoing'):
                Manager.manager.get_node('AddToOg', pos=(self.rect.centerx + (self.rect.width * 2) + 15, self.rect.centery), held=False)
            if not Manager.manager.exists('ongoing'):
                Manager.manager.get_node('Ongoing', pos=(self.rect.centerx, self.rect.centery + self.rect.height + 5), held=False)
                
    def get_text(self):
        return "self.start_ongoing(player)\n"
        
class InitOngoing(Node):
    def __init__(self, id):
        super().__init__(id, 'init ongoing', [Port(-1, ['flow'])], type='func') 
            
    def get_text(self):
        return '\n\tdef start_ongoing(self, player):\n'
        
class AddToOg(Node):
    def __init__(self, id):
        super().__init__(id, 'add to ongoing', [Port(1, ['string'], desc='log type'), Port(2, ['flow']), Port(-1, ['flow'])]) 
            
    def get_default(self, p):
        return "''"
            
    def get_text(self):
        return 'player.add_og(self, {0})\n'.format(*self.get_input())
        
class Ongoing(Node):
    def __init__(self, id):
        super().__init__(id, 'ongoing', [Port(-1, ['log'], desc='log info'), Port(-2, ['flow'])], type='func') 
        
    def get_text(self):
        return '\n\tdef ongoing(self, player, log):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'log'

class ExtractVal(Node):
    def __init__(self, id):
        super().__init__(id, 'extract value', [Port(1, ['string'], desc='key'), Port(2, ['log'], desc='value'), Port(-1, [])]) 
        
    def get_output(self, p):
        text = "{1}.get({0}, '')".format(*self.get_input())
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
            text = ip.connection.get_text_value()
            type = self.eval_text(text)
            if type:
                if type not in ip.types:
                    op.add_type(type)
                else:
                    op.clear_types()
            else:
                op.clear_types()
        elif op.types:
            op.clear_types()

class Deploy(Node):
    info = 'This node deploys copies of this card to a passed list of players. You can use deployed cards to request that an opponent flips a coin or rolls the dice or makes a selection. You can then access these results from the original card.'
    tips = 'Using ports 3 and 4, you can pass player and card values for the deployed cards to set as their extra player and extra card values. This is an easy way to allow trojan cards to access the original player and parent card.'
    ip1 = "A string representing what the trojan card is to do once passed to an opponent. 'flip' will activate a flip request, 'roll' a roll request, 'select' a select request and 'og' will start an ongoing process."
    ip2 = 'List of players who will recieve deployed cards. The main player is automatically filtered out if they are included in the given list.'
    ip3 = "A card which will be set as the extra card for all deployed cards. Often you will want to set this value to the original card (accessed by a 'self' node). This will allow you to access the parent card from any trojan card."
    ip4 = "A player which will be set as the extra player for all deployed cards. Often you will want to set this value to the original player. This will allow you to access the original player from any trojan card."
    def __init__(self, id):
        super().__init__(id, 'deploy', [Port(1, ['string'], desc='type'), Port(2, ['ps'], desc='players to send to'), Port(3, ['card'], desc='set stored card'), Port(4, ['player'], desc='set stored player'), Port(5, ['flow']), Port(-1, ['flow'])]) 
        
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

class GetFlipResults(Node):
    def __init__(self, id):
        super().__init__(id, 'get flip results', [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['bs'], desc='flip results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_flip_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class GetRollResults(Node):
    def __init__(self, id):
        super().__init__(id, 'get roll results', [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['ns'], desc='roll results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_flip_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'
            
class GetSelectResults(Node):
    def __init__(self, id):
        super().__init__(id, 'get select results', [Port(1, ['flow']), Port(-1, ['ps'], desc='players'), Port(-2, ['cs'], desc='select results'), Port(-3, ['flow'])])   
        
    def get_text(self):
        return f'players{self.id}, results{self.id} = self.get_flip_results()\n'
        
    def get_output(self, p):
        if p == -1:
            return f'players{self.id}'
        elif p == -2:
            return f'results{self.id}'

class SelfIndex(Node):
    def __init__(self, id):
        super().__init__(id, 'self index', [Port(-1, ['num'])])  

    def get_output(self, p):
        return 'player.played.index(self)'
        
class IndexAbove(Node):
    def __init__(self, id):
        super().__init__(id, 'index above', [Port(-1, ['num'], desc='self index - 1')])  

    def get_output(self, p):
        return 'max(player.played.index(self) - 1, 0)'
        
class IndexBelow(Node):
    def __init__(self, id):
        super().__init__(id, 'index below', [Port(-1, ['num'], desc='self index + 1')])  

    def get_output(self, p):
        return 'min(player.played.index(self) + 1, len(player.played))'
        
class CheckIndex(Node):
    info = "This function will check a card at a given index in a players 'played' deck. The card at the index and a boolean value are returned. This card will keep a memory of cards it has checked. If an unrecognized card is found at the given index, the boolean value will be True, otherwise it will be False."
    tips = "This function is best used in an ongoing process with the 'cont' condition. It will continuously check an index to see if there is a new card."
    ip1 = "The player whos 'played' deck will be checked. This will default to the original player."
    ip2 = "The index which is being checked. It is safe to index out of range if the length of the 'played' deck is unknown. The boolean value will return False. This will default to the index at the end of the deck."
    ip3 = "An optional tag used as additional criteria to verrify a new card. The returned boolean value will only trigger if the card at the given index is new AND has the given tag."
    op1 = "The card that is found at the given index. If the index is out of range, this will be a None value."
    op2 = "Boolean value representing if a new card was found at the given index. If the index is out of range or no new card is found that meets the criteria, this value will be False, otherwise it will be True."
    def __init__(self, id):
        super().__init__(id, 'check index', [Port(1, ['player']), Port(2, ['num'], desc='index'), Port(3, ['string'], desc='tag'), Port(4, ['flow']), Port(-1, ['card'], desc='card at index'), Port(-2, ['bool'], desc='new card'), Port(-3, ['flow'])])   
 
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
    def __init__(self, id):
        super().__init__(id, 'splitter', [Port(1, Port.get_comparison_types(), desc='value'), Port(-1, [], desc='value'), Port(-2, [], desc='value')])
        
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
        
class CheckFirst(Node):
    def __init__(self, id):
        super().__init__(id, 'check first', [Port(1, ['player']), Port(-1, ['bool'], desc='player is first')])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        
    def get_output(self, p):
        return 'self.game.check_first({0})'.format(*self.get_input())  
        
class CheckLast(Node):
    def __init__(self, id):
        super().__init__(id, 'check last', [Port(1, ['player']), Port(-1, ['bool'], desc='player is last')])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        
    def get_output(self, p):
        return 'self.game.check_last({0})'.format(*self.get_input())  

class DrawCards(Node):
    def __init__(self, id):
        super().__init__(id, 'draw cards', [Port(1, ['string'], desc='card type'), Port(2, ['num'], desc='number of cards'), Port(3, ['player']), Port(4, ['flow']), Port(-1, ['cs'], desc='cards'), Port(-2, ['flow'])])   
        
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
        
class IsEvent(Node):
    def __init__(self, id):
        super().__init__(id, 'is event', [Port(1, ['string'], desc='event name'), Port(-1, ['bool'], desc='event has name')])   
        
    def get_default(self, p):
        return "''"
        
    def get_output(self, p):
        return 'self.game.is_event({0})'.format(*self.get_input())
                
class PlayCard(Node):
    def __init__(self, id):
        super().__init__(id, 'play card', [Port(1, ['card']), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return 'self'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        return "{1}.play_card({0})\n".format(*self.get_input())
           
class Copy(Node):
    def __init__(self, id):
        super().__init__(id, 'copy', [Port(1, ['card']), Port(-1, ['card'], desc='card copy')])
        
    def get_default(self, p):
        return 'self'

    def get_output(self, p):
        return "{0}.copy()".format(*self.get_input())

class SetExtraCard(Node):
    def __init__(self, id):
        super().__init__(id, 'set extra card', [Port(1, ['card'], desc='new extra card'), Port(2, ['flow']), Port(-1, ['flow'])])
            
    def get_text(self):
        return 'self.extra_card = {0}\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'None'

class GetExtraCard(Node):
    def __init__(self, id):
        super().__init__(id, 'get extra card', [Port(-1, ['card'], desc='extra card')])
            
    def get_output(self, p):
        return 'self.extra_card'   
        
class SetExtraPlayer(Node):
    def __init__(self, id):
        super().__init__(id, 'set extra player', [Port(1, ['player'], desc='new extra player'), Port(2, ['flow']), Port(-1, ['flow'])])
            
    def get_text(self):
        return 'self.extra_player = {0}\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'None'

class GetExtraPlayer(Node):
    def __init__(self, id):
        super().__init__(id, 'get extra player', [Port(-1, ['player'], desc='extra player')])
            
    def get_output(self, p):
        return 'self.extra_player' 
        
class Index(Node):
    def __init__(self, id):
        super().__init__(id, 'index', [Port(1, ['num'], desc='index'), Port(2, ['ps'], desc='list'), Port(-1, ['player'], desc='list value at index')])
        
    def transform(self):
        self.clear_connections()
        
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
            return 'player.get_played.copy()'
        
class SafeIndex(Node):
    def __init__(self, id):
        super().__init__(id, 'safe index', [Port(1, ['num'], desc='index'), Port(2, ['ps'], desc='list'), Port(-1, ['player'], desc='list value at index')])
        
    def transform(self):
        self.clear_connections()
        
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
    def __init__(self, id):
        super().__init__(id, 'discard', [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return '{0}.discard_card({1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
            
class SafeDiscard(Node):
    def __init__(self, id):
        super().__init__(id, 'safe discard', [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return '{0}.safe_discard({1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'
            
class UseItem(Node):
    def __init__(self, id):
        super().__init__(id, 'use item', [Port(1, ['card'], desc='item'), Port(2, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'player.use_item({0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self'
            
class GiveCard(Node):
    def __init__(self, id):
        super().__init__(id, 'give card', [Port(1, ['player']), Port(2, ['card']), Port(3, ['player'], desc='target'), Port(4, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return '{0}.give_card({1}, {2})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'self'
        elif p == 3:
            return 'player'
     
class GetNewCard(Node):
    def __init__(self, id):
        super().__init__(id, 'get new card', [Port(1, ['string'], desc='card name')])

    def get_text(self):
        return 'self.game.get_card({0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self.name'
     
class Transfom(Node):
    def __init__(self, id):
        super().__init__(id, 'transform', [Port(1, ['string'], desc='new card name'), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'self.game.transform({1}, {0})\n'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'self'
            
class Swap(Node):
    def __init__(self, id):
        super().__init__(id, 'swap', [Port(1, ['card']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])

    def get_text(self):
        return 'self.game.swap({0}, {1})\n'.format(*self.get_input())
        
    def get_default(self, p):
        return 'self'
        
class GetDiscard(Node):
    def __init__(self, id):
        super().__init__(id, 'get discard', [Port(-1, ['cs'], desc='discarded cards')])
        
    def get_output(self, p):
        return 'self.game.discard.copy()'
     
class SetMode(Node):
    def __init__(self, id):
        super().__init__(id, 'set mode', [Port(1, ['num'], desc='new mode'), Port(2, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return '0'
        
    def get_text(self):
        return 'self.mode = {0}\n'.format(*self.get_input())
        
class GetMode(Node):
    def __init__(self, id):
        super().__init__(id, 'get mode', [Port(-1, ['num'], desc='mode')])   
        
    def get_output(self, p):
        return 'self.mode'

class StealRandom(Node):
    def __init__(self, id):
        super().__init__(id, 'steal random', [Port(1, ['string'], desc='deck'), Port(2, ['player']), Port(3, ['player'], desc='target'), Port(4, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return "'treasure'"
        elif p == 2 or p == 3:
            return 'player'

    def get_text(self):
        return "{2}.steal_random_card({0}, {1})\n".format(*self.get_input())
        
class AddCard(Node):
    def __init__(self, id):
        super().__init__(id, 'add card', [Port(1, ['player']), Port(2, ['card']), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def get_default(self, p):
        if p == 1:
            return 'player'
        elif p == 2:
            return 'None'

    def get_text(self):
        return "{0}.safe_add({1})\n".format(*self.get_input())
        
class GetDeck(Node):
    def __init__(self, id):
        super().__init__(id, 'get deck', [Port(1, ['string'], desc='deck name'), Port(2, ['player']), Port(-1, ['cs'], desc='deck')])   
        
    def update(self):
        super().update()
        
        op = self.get_port(-1)
        deck = self.get_input()[0].strip("'").lower()
        
        if deck in ('played', 'unplayed', 'items', 'spells', 'active_spells', 'equipment', 'treasure', 'landscapes'):
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
        return 'getattr({1}, {0}, []).copy()'.format(*self.get_input())
        
class GetScore(Node):
    def __init__(self, id):
        super().__init__(id, 'get score', [Port(1, ['player']), Port(-1, ['num'], desc='points')])   
        
    def get_default(self, p):
        return 'player'

    def get_output(self, p):
        return "{0}.score".format(*self.get_input())
        
class HasCard(Node):
    def __init__(self, id):
        super().__init__(id, 'has card', [Port(1, ['string'], desc='card name'), Port(2, ['player']), Port(-1, ['bool'], desc='player has card')])   
        
    def get_default(self, p):
        if p == 1:
            return 'self.name'
        elif p == 2:
            return 'player'

    def get_output(self):
        return "{1}.has_card_by_name({0})".format(*self.get_input())
        
        
        
        
        