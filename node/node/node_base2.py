import pygame as pg

from . import mapping

from ui.image import rect_outline
from ui.geometry import line
from ui.element.base import Compound_Object
from ui.element.standard import Textbox, Image
from ui.element.extended import Logged_Input as Input
from ui.drag import Dragger

class Wire:
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
        self.dashed_points = line.segment(self.points)
        
        self.last_pos_out = self.op.rect.center
        self.last_pos_in = self.ip.rect.center
        
    @property
    def manager(self):
        return self.op.manager
        
    def check_intersect(self, a, b):
        for i in range(len(self.points) - 1):
            c = self.points[i]
            d = self.points[i + 1]
            
            if line.intersect(a, b, c, d):
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
                return (start, (xmax, oy), (xmax, cy), (xmin, cy), (xmin, iy), end)
                
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
            return (start, (cx, oy), (cx, iy), end)
        
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
            self.dashed_points = line.segment(self.points)
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
            cls.desc_cache[desc] = Textbox(desc, tsize=15, bgcolor=(0, 0, 0))
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
        
    def update_types(self, types):
        if not self.check_connection(types):
            self.clear()
        self.set_types(types)
        
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
                
    def check_connection(self, new_types):
        if not self.connection:
            return True
        return any({t in new_types for t in self.connection_port.types})

class Node(Dragger, Compound_Object):
    cat = 'base'
    subcat = 'base'
    
    IMAGE_CACHE = {}
    LABEL_CACHE = {}
    RAW_CACHE = {}
    
    @classmethod
    def get_subclasses(cls):
        sc = cls.__subclasses__()
        sc.remove(GroupNode)
        return sc
    
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

            label = Textbox(node.get_name(), tsize=20, fgcolor=tcolor)
            w, h = node.image.get_size()
            r = pg.Rect(0, 0, w - 5, h - 5)
            r.center = node.image.get_rect().center
            label.fit_text(r)
            
            label = label.get_image()
            cls.LABEL_CACHE[node.name] = label
            
        label = Image(label)  
        return label

    def __init__(self, manager, id, ports, pos=(0, 0), val=None, type=None, color=(100, 100, 100)):
        Compound_Object.__init__(self)
        
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

        Dragger.__init__(self)
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
        
    def get_required(self):
        return []

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
                
        return hit_port
            
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
            surf.blit(rect_outline(self.image, color=(255, 0, 0)), self.rect)
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
        i = Input(size, message=self.val, fgcolor=(0, 0, 0), color=(255, 100, 100), length=25, fitted=True, double_click=True)
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
 