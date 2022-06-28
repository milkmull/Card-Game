import json

import pygame as pg

from . import mapping

from ui.image import rect_outline, get_arrow
from ui.geometry import line
from ui.element.base import Compound_Object
from ui.element.standard import Image, Textbox, Button
from ui.element.extended import Logged_Input as Input, Logged_Check_Box as Check_Box, Logged_Dropdown as Dropdown
from ui.drag import Dragger

NODE_DATA_PATH = 'data/node/'

def pack(nodes):
    s = {'nodes': [], 'groups': []}
    for n in nodes:
        if n.is_group():
            s['groups'].append(n)
        else:
            s['nodes'].append(n)
    nodes = s
    
    save_data = {'nodes': {}, 'groups': {}}
    
    for n in nodes['nodes']:
        node_data = {}
        node_data['name'] = n.__class__.__name__
        node_data['pos'] = n.rect.center
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
            port_data['object_value'] = p.value
            ports[str(p.port)] = port_data
        node_data['ports'] = ports
        save_data['nodes'][str(n.id)] = node_data
        
    for g in nodes['groups']:
        group_data = {}
        group_data['name'] = g.get_string_val()
        group_data['pos'] = g.rect.center
        group_data['nodes'] = [n.id for n in g.nodes]
        group_data['rel_node_pos'] = g.get_rel_node_pos()
        save_data['groups'][str(g.id)] = group_data
        
    return save_data
        
def unpack(data):
    if not data:
        return {}
        
    nodes = {}
    id_map = {}

    for id, d in data['nodes'].items():
        id = int(id)
        name = d['name']
        contains = d['contains']
        pos = d['pos']
        n = Node.from_name(name, pos=pos)
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n

    while True:
    
        missed = False
    
        for id, d in data['nodes'].items():
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
                object_value = ports[port]['object_value']
                if parent_port is not None:
                    n0.new_output_port(n0.get_port(parent_port))
                port = int(port)
                p0 = n0.get_port(port)
                p0.set_types(types)
                if object_value is not None:
                    p0.value = object_value
                p0.suppressed = suppressed
                p0.visible = visible
                p0.parent_port = parent_port
                if connection is not None and port < 0:
                    connection = id_map.get(connection)
                    if connection is not None:
                        n1 = nodes[connection]
                        p1 = n1.get_port(connection_port)
                        if p0 and p1:
                            Port.new_connection(p0, p1, force=True)
                        else:
                            missed = True
      
        if not missed:
            break

    for id, d in data['groups'].items():
        id = int(id)
        name = d['name']
        group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
        pos = d['pos']
        n = Group_Node.get_new(group_nodes, name=name, pos=pos)
        n.rel_node_pos = {nodes[id_map[int(nid)]]: pos for nid, pos in d['rel_node_pos'].items()}
        new_id = n.id
        id_map[id] = new_id
        nodes[new_id] = n
        
    nodes = list(nodes.values())
    for n in nodes:
        n.set_port_pos()
        
    return nodes
     
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
        Node.del_wire(self)
        
    def find_points(self): 
        onode = self.op.parent
        inode = self.ip.parent
        
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
        self.update()
        if self.op.visible and self.ip.visible:
            if not self.bad:
                pg.draw.lines(surf, self.op.color, False, self.points, width=3)
            else:
                for i in range(0, len(self.dashed_points) - 1, 2):
                    p0 = self.dashed_points[i]
                    p1 = self.dashed_points[i + 1]
                    pg.draw.line(surf, self.op.color, p0, p1, width=3)

class Port(Compound_Object):
    SIZE = 10
    comparison_types = [
        'bool',
        'num',
        'string',
        'ps',
        'cs',
        'ns',
        'ss', 
        'bs',
        'player',
        'card'
    ]
    contains_dict = {
        'ps': 'player',
        'cs': 'card',
        'ns': 'num',
        'ss': 'string',
        'bs': 'bool'
    }
    desc_cache = {}
    num_check = lambda t: (t + '0').strip('-').isnumeric()
    string_check = lambda t: t.count("'") < 3
    get_output = lambda : None
    
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
                Node.new_wire(p0, p1)
                
                if p0.manager and not d:
                    p0.manager.add_log({'t': 'conn', 'nodes': (n0, n1), 'ports': (p0, p1)})

        n0.prune_extra_ports()
        n1.prune_extra_ports()
    
    @staticmethod
    def disconnect(p0, p1, d=False):
        n0 = p0.node
        n1 = p1.node
        
        if p0.manager and not d:
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

    def __init__(self, port, types, desc=None):
        super().__init__()
        
        self.port = port
        self.types = types
     
        self.parent_port = None
        self.node = None
        
        self.object = None
       
        self.connection = None
        self.connection_port = None
        
        self.wire = None
        self.suppressed = False
        
        self.rect = pg.Rect(0, 0, Port.SIZE, Port.SIZE)
        
        self.set_desc(desc)
        
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
        
    @property
    def true_port(self):
        if self.parent_port is not None:
            return self.parent_port
        return self.port
        
    @property
    def object_type(self):
        if self.object:
            return self.object.tag
        
    @property
    def value(self):
        if isinstance(self.object, Input):
            return self.object.message
        elif isinstance(self.object, Check_Box):
            return self.object.get_state()
        elif isinstance(self.object, Dropdown):
            return self.object.current_value
            
    @value.setter
    def value(self, value):
        if isinstance(self.object, Input):
            return self.object.update_message(value, force=True)
        elif isinstance(self.object, Check_Box):
            return self.object.set_state(value)
        elif isinstance(self.object, Dropdown):
            return self.object.set_value(value)
            
    def set_value(self, value, d=True):
        if isinstance(self.object, Input):
            return self.object.update_message(value, force=True)
        elif isinstance(self.object, Check_Box):
            return self.object.set_state(value, d=d)
        elif isinstance(self.object, Dropdown):
            return self.object.set_value(value, d=d)

    def set_desc(self, desc):
        if not desc and not self.types:
            desc = ''
        elif not desc:
            desc = self.types[0]
        desc = Textbox(desc, tsize=15)
        
        if self.port > 0:
            desc.fit_text(pg.Rect(0, 0, Node.WIDTH - 18, 999), allignment='l', width_only=True)
            desc = desc.to_static()
            desc.rect.midleft = (self.rect.right + 5, self.rect.centery)
        else:
            desc.fit_text(pg.Rect(0, 0, Node.WIDTH - 18, 999), allignment='r', width_only=True)
            desc = desc.to_static()
            desc.rect.midright = (self.rect.left - 5, self.rect.centery)
        self.add_child(desc, current_offset=True)
        self.desc = desc
        
    def set_input_object(self, type, value=''):
        if self.object:
            self.remove_child(self.object)
            
        if type == 'num':
            full_check = Port.num_check
            length = 3
            
            def get_output():
                return self.object.message
            
        elif type == 'string':
            full_check = Port.string_check
            length = 50
            
            def get_output():
                return f"'{self.object.message}'"
        
        i = Input(
                size=(self.node.rect.width - 18, 22),
                padding=(2, 2),
                special_pad=2,
                message=value.strip("'"),
                default=self.node.get_default(self.port).strip("'"),
                color=(255, 255, 255),
                fgcolor=(0, 0, 0),
                border_radius=0,
                full_check=full_check,
                length=length,
                fitted=True,
                allignment='l',
                double_click=True,
            )
            
        self.object = i
        self.get_output = get_output
        
        if self.port > 0:
            i.rect.midleft = (self.rect.right + 5, self.rect.centery)
        elif self.port < 0:
            i.rect.midright = (self.rect.left - 5, self.rect.centery)
        i.rect.y += self.desc.rect.height + 8
        self.add_child(i, current_offset=True)
        
    def set_check_object(self, value=True):
        if self.object:
            self.remove_child(self.object)
            
        cb = Check_Box()
        cb.set_state(value)
        
        def get_output():
            return str(self.object.get_state())
        
        self.object = cb
        self.get_output = get_output
        
        if self.port > 0:
            cb.rect.midleft = (self.rect.right + 5, self.rect.centery)
        elif self.port < 0:
            cb.rect.midright = (self.rect.left - 5, self.rect.centery)
        cb.rect.y += self.desc.rect.height + 8
        self.add_child(cb, current_offset=True)
        
    def set_dropdown_object(self, options, value=None):
        if self.object: 
            self.remove_child(self.object)
            
        dd = Dropdown(
            options,
            selected=value,
            size=(self.node.rect.width - 16, 22),
            padding=(4, 2, 2, 2),
            special_pad=2,
            fitted=True,
            allignment='l',
            fgcolor=(255, 255, 255),
            color=(32, 32, 40),
            outline_color=(0, 0, 0),
            outline_width=3,
            border_radius=5,
        )
        
        def get_output():
            return f"'{self.object.current_value}'"
            
        self.object = dd
        self.get_output = get_output
        
        if self.port > 0:
            dd.rect.midleft = (self.rect.right + 5, self.rect.centery)
        elif self.port < 0:
            dd.rect.midright = (self.rect.left - 5, self.rect.centery)
        dd.rect.y += self.desc.rect.height + 8
        self.add_child(dd, current_offset=True)
    
    def clear_object(self):
        self.remove_child(self.object)
        self.object = None
    
    def set_node(self, node):
        if not node.is_group():
            self.node = node

    def copy(self):
        n = self.node
        p = Port(self.node.get_new_output_port(), self.types)
        p.parent_port = self.port
        p.node = n
        p.rect = self.rect.copy()
        n.ports.append(p)
        return p

#visibility stuff-------------------------------------------------------------------

    def set_suppressed(self, suppressed, d=False):
        if self.suppressed != suppressed:
            if not self.suppressed:
                self.clear()
            self.suppressed = suppressed
            
            if self.manager and not d:
                self.manager.add_log({'t': 'suppress', 's': suppressed, 'p': self})

    def get_parent_port(self):
        if self.parent_port is not None:
            return self.node.get_port(self.parent_port)
        
#type stuff-------------------------------------------------------------------
        
    def set_types(self, types):
        self.types.clear()
        self.types += types
        
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
        return Port.contains_dict.get(self.types[0])
                
    def check_connection(self, new_types):
        if not self.connection:
            return True
        return any({t in new_types for t in self.connection_port.types})

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
        
    def is_output(self):
        return self.port < 0
        
    def is_input(self):
        return self.port > 0
        
    def has_value(self):
        if self.object is not None:
            if isinstance(self.object, Input):
                return self.object.is_filled()
        
    def update_object(self):
        if self.connection:
            self.object.set_enabled(False)
            out = self.connection.get_output(self.connection_port.true_port)
            try:
                out = eval(out)
            except:
                pass
            if isinstance(self.object, Input):
                self.object.update_message(str(out), force=True)
            elif isinstance(self.object, Check_Box):
                self.object.set_state(out)
            elif isinstance(self.object, Dropdown):
                self.object.set_value(out)
            self.object.clear_logs()
        else:
            self.object.set_enabled(True)
        
    def update(self):
        if self.port > 0 and self.object is not None:
            self.update_object()
        super().update()
        if self.object:
            logs = self.object.get_logs()
            for log in logs:
                self.manager.add_log(log)
        
#draw stuff--------------------------------------------------------------------------
        
    @property
    def color(self):
        if not self.types:
            return (0, 0, 0)
        main_type = self.types[0]
        if main_type == 'bool':
            return (255, 255, 0)
        elif main_type == 'player':
            return (255, 0, 0)
        elif main_type in ('cs', 'ps', 'ns', 'ss', 'bs'):
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

    @property
    def contains_color(self):
        if 'ps' in self.types and 'cs' in self.types:
            return (0, 255, 0)
        elif 'ps' in self.types:
            return (255, 0, 0)
        elif 'cs' in self.types:
            return (145, 30, 180)
        elif 'ns' in self.types:
            return (0, 0, 255)
        elif 'ss' in self.types:
            return (255, 0, 255)
        elif 'bs' in self.types:
            return (255, 255, 0)
        else:
            return (0, 255, 0)

    def draw(self, surf):
        if not self.parent_port:
        
            if not self.suppressed:
                r = self.rect.width // 2
            else:
                r = 3
            pg.draw.circle(surf, self.color, self.rect.center, r)
            
            if not self.suppressed:
                contains = self.get_contains()
                if contains:
                    pg.draw.circle(surf, self.contains_color, self.rect.center, r - 2)

            super().draw(surf)

class Node(Dragger, Compound_Object):
    cat = 'base'
    subcat = 'base'
    
    IMAGE_CACHE = {}
    LABEL_CACHE = {}
    RAW_CACHE = {}
    
    LABEL_HEIGHT = 20
    OUTLINE_SPACE = 3
    PORT_SPACING = 15
    WIDTH = 150
    
    ACTIVE_NODE = None
    CLOSE_ACIVE = False
    WIRES = []
    
    ID = 0
    NODE_DATA = {}
    GROUP_DATA = {}

    @classmethod
    def get_subclasses(cls):
        sc = cls.__subclasses__()
        sc.remove(Group_Node)
        return sc
        
    @classmethod
    def set_node_data(cls):
        subclasses = cls.get_subclasses()
        for subcls in subclasses:
            name = subcls.__name__
            cls.NODE_DATA[name] = subcls
          
    @classmethod
    def set_group_data(cls):
        with open(f'{NODE_DATA_PATH}group_nodes.json', 'r') as f:
            cls.GROUP_DATA = json.load(f)
        
    @classmethod
    def set_active_node(cls, node):
        node.set_stuck(True)
        cls.ACTIVE_NODE = node
        
    @classmethod
    def close_active_node(cls):
        if cls.ACTIVE_NODE:
            cls.ACTIVE_NODE.prune_extra_ports()
            cls.ACTIVE_NODE.set_stuck(False)
            cls.ACTIVE_NODE = None
        cls.CLOSE_ACIVE = False
        
    @classmethod
    def new_wire(cls, p0, p1):
        cls.WIRES.append(Wire(p0, p1))
        
    @classmethod
    def del_wire(cls, wire):
        if wire in cls.WIRES:
            cls.WIRES.remove(wire)
        
    @classmethod
    def get_new_id(cls):
        id = cls.ID
        cls.ID += 1
        return id
        
    @classmethod
    def set_raw(cls):
        for name, subcls in cls.NODE_DATA.items():
            node = subcls(0)
            img = node.get_raw_image()
            cls.RAW_CACHE[name] = img
        for name, data in cls.GROUP_DATA.items():
            node = Group_Node.from_data(data)
            img = node.get_raw_image()
            cls.RAW_CACHE[name] = img
        return cls.RAW_CACHE
        
    @classmethod
    def get_cached_img(cls, name):
        return cls.RAW_CACHE.get(name)
        
    @classmethod
    def reset(cls):
        cls.close_active_node()
        cls.WIRES.clear()
        cls.ID = 0

    @classmethod
    def get_image(cls, node):
        size = node.size
        if node.is_func():
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

            tcolor = (255, 255, 255)

            label = Textbox(node.get_name(), tsize=20, fgcolor=tcolor)
            label.fit_text(node.label_rect.inflate(-3, -3))
            label = label.get_image()
            cls.LABEL_CACHE[node.name] = label
            
        label = Image(label)  
        return label
        
    @classmethod
    def from_name(cls, name, **kwargs):
        id = cls.get_new_id()
        n = cls.NODE_DATA[name](id, **kwargs)
        return n

    def __init__(self, id, val=None, pos=(0, 0), manager=None, **kwargs):
        Compound_Object.__init__(self, **kwargs)
        
        self.manager = manager
        
        self.id = id
        self.val = val
        self.form = 0
        self.active_port = None
        self.group_node = None

        self.rect = pg.Rect(0, 0, Node.WIDTH, Node.WIDTH)
        self.rect.center = pos

        self.objects_dict = {}
        self.objects = self.get_objects()

        Dragger.__init__(self)

    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def set_manager(self, manager):
        self.manager = manager
        
    @property
    def name(self):
        return type(self).__name__
        
    def get_name(self):
        return self.name.replace('_', ' ')
        
    @property
    def color(self):
        return (89, 90, 123)
    
    @property
    def label_rect(self):
        return pg.Rect(
            self.rect.x,
            self.rect.y - Node.LABEL_HEIGHT - Node.OUTLINE_SPACE,
            self.rect.width,
            Node.LABEL_HEIGHT
        )
        
    @property
    def background_rect(self):
        return pg.Rect(
            self.rect.x - Node.OUTLINE_SPACE,
            self.rect.y - (2 * Node.OUTLINE_SPACE) - Node.LABEL_HEIGHT,
            self.rect.width + (2 * Node.OUTLINE_SPACE),
            self.rect.height + (3 * Node.OUTLINE_SPACE) + Node.LABEL_HEIGHT
        )

    def is_group(self):
        return isinstance(self, Group_Node)
        
    def is_input(self):
        return 'input' in self.objects_dict
        
    def is_flow(self):
        return any({'flow' in p.types for p in self.ports})
        
    def is_func(self):
        return self.tag == 'func'

    def can_transform(self):
        return hasattr(self, 'tf')
        
    def set_ports(self, ports):
        self.ports = ports
        self.set_port_pos()
        
#image and element stuff-------------------------------------------------------------------

    def get_raw_image(self):
        w = self.rect.width + (2 * Node.OUTLINE_SPACE) + Port.SIZE
        h = self.rect.height + (3 * Node.OUTLINE_SPACE) + Node.LABEL_HEIGHT
        surf = pg.Surface((w, h)).convert_alpha()
        surf.fill((0, 0, 0, 0))
        self.rect.bottomleft = (Port.SIZE // 2, h - Node.OUTLINE_SPACE)
        self.update_position(all=True)
        self.draw_on(surf, surf.get_rect())
        return pg.transform.smoothscale(surf, (w // 1.5, h // 1.5))

    def get_objects(self):
        label = Node.get_label(self)
        label.rect.center = self.label_rect.center
        self.add_child(label, current_offset=True)
        self.objects_dict['label'] = label
        return [label]
        
    def get_transform_button(self):
        h = self.label_rect.height - 5
        i = get_arrow('r', (h, h), padding=(5, 5))
        b = Button.image_button(i, func=self.transform, border_radius=2, color=None)
        b.rect.midright = self.label_rect.midright
        b.rect.x -= 5
        self.add_child(b, current_offset=True)
        
    def get_ar_buttons(self, io):
        h = self.label_rect.height - 5
        a = Button.text_button('+', size=(h, h), func=self.add_port, color=None, special_pad=2)
        r = Button.text_button('-', size=(h, h), func=self.remove_port, color=None, special_pad=2)
        if io == 1:
            a.rect.midleft = self.label_rect.midleft
            a.rect.x += 5
            r.rect.topleft = a.rect.topright
        elif io == -1:
            r.rect.mifright = self.label_rect.midright
            r.rect.x -= 5
            a.rect.topright = r.rect.topright
        self.add_child(a, current_offset=True)
        self.add_child(r, current_offset=True)

    def get_string_val(self):
        input = self.objects_dict.get('input')
        if input:
            return input.message
            
    def set_port_pos(self):
        ip = self.get_input_ports()
        op = self.get_output_ports()
        ex = []
        for p in op.copy():
            if p.parent_port:
                op.remove(p)
                ex.append(p)

        y = self.rect.y + Node.PORT_SPACING
        
        for p in ip + op:
            p.set_node(self)
            p.rect.center = (self.rect.x if p.port > 0 else self.rect.right, y)
            self.add_child(p, current_offset=True)
            
            if p.object:
                y += p.object.rect.height
            y += p.rect.height + Node.PORT_SPACING
                
        for p in ex:
            p.set_node(self)
            p.rect.center = p.get_parent_port().rect.center
            self.add_child(p, current_offset=True)
            
        tl = self.rect.topleft
        self.rect.height = y - self.rect.y
        self.rect.topleft = tl
        
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
                input.append(ip.connection.get_output(ip.connection_port.true_port))
            elif ip.object:
                input.append(ip.get_output())
            else:
                input.append(self.get_default(ip.port))
                
        return input
        
    def get_input_from(self, p):
        ip = self.get_port(p)
        if ip.connection:
            return ip.connection.get_output(ip.connection_port.true_port)
        elif ip.object:
            return ip.get_output()
        else:
            return self.get_default(ip.port)
     
#port stuff-------------------------------------------------------------------

    def set_active_port(self, port):
        port.set_suppressed(False)
        self.active_port = port
        self.set_stuck(True)
        Node.set_active_node(self)

    def get_port(self, num):
        for p in self.ports:
            if p.port == num:
                return p
        
    def get_input_ports(self):
        return [p for p in self.ports if p.port > 0]
    
    def get_output_ports(self):
        return [p for p in self.ports if p.port < 0]
    
    def get_extra_ports(self):
        return [p for p in self.ports if p.parent_port is not None]
        
    def get_new_input_port(self):
        return max({p.port for p in self.get_input_ports()}, default=0) + 1
        
    def get_new_output_port(self):
        return min({p.port for p in self.get_output_ports()}, default=0) - 1
        
    def get_in_flow(self):
        for ip in self.get_input_ports():
            if 'flow' in ip.types:
                return ip
            
    def clear_connections(self):
        for p in self.ports.copy(): 
            print('dc', self, p)
            p.clear()
            
    def delete(self):
        self.clear_connections()
        if self.is_input():
            self.objects_dict['input'].close()
  
    def prune_extra_ports(self):
        for p in self.ports.copy():
            if p.parent_port and not p.connection:
                self.ports.remove(p)

    def new_output_port(self, parent):
        p = parent.copy()
        self.add_child(p, current_offset=True)
        return p
        
    def suppress_port(self, port):
        port.set_suppressed(not port.suppressed)
        for p in self.get_extra_ports():
            if port.port == p.parent_port:
                p.set_suppressed(not p.suppressed)

    def can_connect(self, p0, n1, p1):
        return True

    def add_port(self):
        p = self.ap()
        
        if p and self.manager:
            log = {'t': 'ap', 'node': self, 'port': p}
            self.manager.add_log(log)
    
    def remove_port(self):
        p = self.rp()
        
        if p and self.manager:
            log = {'t': 'rp', 'node': self, 'port': p}
            self.manager.add_log(log)
        
#input stuff-------------------------------------------------------------------
        
    def transform(self, form=None, d=False):
        self.clear_connections()
        
        if d or not self.manager:
            self.tf(form=form)
            
        elif not d:
            log = {'t': 'transform', 'node': self, 'form0': self.form}
            self.manager.add_log(log)
            self.tf(form=form)
            log['form1'] = self.form
        
    def click_down(self, dub_click, button, hit, port):
        if port:
            if button == 1:
                if not port.connection:
                    self.set_active_port(port)
                elif 'flow' not in port.types:
                    self.set_active_port(self.new_output_port(port))
        
    def click_up(self, button, hit, port):
        if port:
            
            an = Node.ACTIVE_NODE
            
            if button == 1:
                if an and an is not self:
                    if not port.connection:
                        p0 = an.active_port
                        p1 = port
                        Port.new_connection(p0, p1)
                        Node.close_active_node()
                    elif 'flow' not in port.types:
                        p0 = self.new_output_port(port)
                        p1 = an.active_port
                        Port.new_connection(p0, p1)
                        Node.close_active_node()

            elif button == 3:
                self.suppress_port(port)

    def events(self, events):
        mp = events['p']
        kd = events.get('kd')
        ku = events.get('ku')
        mbd = events.get('mbd')
        mbu = events.get('mbu')
        dub = events.get('dub')
        
        hit_node = self.rect.collidepoint(mp)
        hit_port = None
        for p in self.ports:
            if p.visible:
                if not hit_port:
                    if p.rect.collidepoint(mp):
                        hit_port = p
                        break
                    
        if mbd:
            self.click_down(dub, mbd.button, hit_node, hit_port)
        elif mbu:
            Node.CLOSE_ACIVE = True
            self.click_up(mbu.button, hit_node, hit_port)
        elif Node.CLOSE_ACIVE:
            Node.close_active_node()
            
        super().events(events)
            
        if self.is_input():
            if self.objects_dict['input'].active:
                self.drop()
                
        return hit_port
            
#update stuff-------------------------------------------------------------------
        
    def update(self):
        if self.visible:
            self.update_drag()
            super().update()
            
            if self.manager:
                if self.is_input():
                    logs = self.objects_dict['input'].get_logs()
                    for log in logs:
                        self.manager.add_log(log)
                        
        if not self.active_port:
            self.prune_extra_ports()
        
#draw stuff-------------------------------------------------------------------
        
    def draw(self, surf):
        pg.draw.rect(surf, (0, 0, 0), self.background_rect, border_radius=10)
        pg.draw.rect(surf, (173, 19, 64), self.label_rect, border_top_left_radius=5, border_top_right_radius=5)
        pg.draw.rect(surf, self.color, self.rect, border_bottom_left_radius=5, border_bottom_right_radius=5)
        if self._selected or self._hover:
            pg.draw.rect(surf, (255, 0, 0), self.rect.inflate(3, 3), width=3)

        super().draw(surf, reverse=True)

    def draw_wire(self, surf):
        p = self.active_port
        pg.draw.line(surf, p.color, p.rect.center, pg.mouse.get_pos(), width=3)
                    
class Group_Node(Node):
    @classmethod
    def get_new(cls, nodes, **kwargs):
        id = cls.get_new_id()
        n = cls(id, nodes, **kwargs)
        return n
        
    @classmethod
    def from_data(cls, data):
        return unpack(data)[-1]
        
    @classmethod
    def from_name(cls, name):
        return unpack(Node.GROUP_DATA[name])[-1]
    
    def __init__(self, id, nodes, name='Group', **kwargs):
        self.nodes = nodes
        self.port_mem = {}
        super().__init__(id, **kwargs)

        self.set_ports(self.get_group_ports(nodes))
        self.set_self_pos()
        self.set_rel_node_pos()
        
    @property
    def name(self):
        return self.get_string_val()
        
    def get_objects(self):
        i = Input(size=self.label_rect.size, message=self.val, fgcolor=(0, 0, 0), length=25, fitted=True, double_click=True)
        i.rect.center = self.label_rect.center
        self.add_child(i, current_offset=True)
        self.objects_dict['input'] = i
        return [i]
        
    def reset_ports(self):
        self.ports = self.get_group_ports(self.nodes)
        self.set_port_pos()
        
    def recall_port_mem(self):
        for p, visible in self.port_mem.items():
            p.set_visible(visible)
   
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
            n.turn_off()
            
            for ip in n.get_input_ports():
                if (not ip.suppressed or (ip.suppressed and self.port_mem.get(ip, False))) and ip.connection not in nodes:
                    ipp.append(ip)
                else:
                    ip.turn_off()
                    
            for op in n.get_output_ports():
                if (not op.suppressed or (op.suppressed and self.port_mem.get(op, False))) and op.connection not in nodes:
                    opp.append(op)
                else:
                    op.turn_off()

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
            n.turn_on()
            n.group_node = None
            for p in n.ports:
                p.turn_on()
            rx, ry = self.rel_node_pos[n]
            n.rect.center = (sx + rx, sy + ry)
            n.set_port_pos()
            n.drop()
        self.ports.clear()
        
    def new_output_port(self, parent):
        p = parent.copy()
        self.add_child(p, current_offset=True)
        self.ports.append(p)
        return p
        
    def update(self):
        for n in self.nodes:
            n.update()
        super().update() 

 