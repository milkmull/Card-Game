import pygame as pg
from constants import *
from ui import Textbox, Dragger, rect_outline, intersect, Input

def init():
    g = globals()
    g['NODES'] = []
    g['ID'] = 0

    names = []
    for k in g:
        v = g[k]
        if hasattr(v, 'isnode') and not (hasattr(v, 'base') or v is Node):
            names.append(k)     
    g['NAMES'] = names
    
def get_node(node, args=[], kwargs={}, pos=None, held=True):
    global NODES
    global ID
    
    g = globals()
    if node in g:
        n = g[node](ID, *args, **kwargs)
        if not pos:
            n.rect.center = pg.mouse.get_pos()
        else:
            n.rect.center = pos
        n.set_port_pos()
        if held:
            n.start_held()
        NODES.append(n)
        ID += 1
        return n
        
def del_node(node):
    global NODES
    global ID
    
    if node in NODES:
        NODES.remove(node)
        ID -= 1
        
def eval_scope_data():
    global NODES
    
    data = []
    for n in NODES:
        data.append(n.start_map())
            
    return all(data)
    
def new_break():
    global NODES
    
    for n in NODES:
        n.check_status()
        
def exists(name):
    global NODES
    return any(n.name == name for n in NODES)

def get_color(types):
    if 'player' in types and 'card' in types:
        return (128, 128, 255)
    elif 'player' in types:
        return (255, 0, 0)
    elif 'seq' in types:
        return (0, 255, 0)
    elif 'num' in types:
        return (0, 0, 255)
    elif 'bool' in types:
        return (255, 255, 0)
    elif 'string' in types:
        return (255, 0, 255)
    elif 'card' in types:
        return (0, 255, 255)
    elif 'split' in types:
        return (128, 128, 128)
    elif 'flow' in types:
        return (255, 255, 255)
    else:
        return (100, 100, 100)
        
def get_image(node):
    image = pg.Surface((40, 40)).convert()
    image.fill(node.color)
    w, h = image.get_size()
    label = Textbox(node.name)
    r = pg.Rect(0, 0, w - 5, h - 5)
    r.center = image.get_rect().center
    label.fit_text(r)
    image.blit(label.get_image(), r)
    return image

class Port:
    def __init__(self, port, types):
        self.port = port
        self.types = types
        
        self.node = None
        
        self.connection = None
        self.connection_port = None
        
        self.live_wire = False
        self.visible = True
        
        self.rect = pg.Rect(0, 0, 10, 10)
        
        self.cfunc = None
        self.cargs = []
        self.ckwargs = {}
        
        self.dfunc = None
        self.dargs = []
        self.dkwargs = {}
        
    def __str__(self):
        return f'{self.port}: {self.connection}'
        
    def __repr__(self):
        return str(self)
        
    def set_cfunc(self, cfunc, cargs=[], ckwargs={}):
        self.cfunc = cfunc
        self.cargs = cargs
        self.ckwargs = ckwargs
        
    def set_dfunc(self, dfunc, dargs=[], dkwargs={}):
        self.dfunc = dfunc
        self.dargs = dargs
        self.dkwargs = dkwargs
        
    def make_visible(self):
        self.visible = True
        
    def make_invisible(self):
        self.visible = False
        
    def open_wire(self):
        self.live_wire = True
        
    def close_wire(self):
        self.live_wire = False
        
    def set_node(self, node):
        self.node = node
        
    def set_types(self, types):
        self.types = types
        
    def add_type(self, type):
        self.types.append(type)
        
    def remove_type(self, type):
        if type in self.types:
            self.types.remove(type)

    def has_connection(self):
        return self.connection is not None
            
    def get_connection(self):
        return self.connection
        
    def get_connection_port(self):
        return self.connection_port
        
    def get_connection_info(self):
        return (self.connection, self.connection_port)
        
    def connect(self, connection, connection_port):
        self.connection = connection
        self.connection_port = connection_port
        
        if self.cfunc is not None:
            self.cfunc(*self.cargs, **self.ckwargs)
        
    def clear(self):
        self.connection = None
        self.connection_port = None
        
        if self.dfunc is not None:
            self.dfunc(*self.dargs, **self.dkwargs)
            
    def clear_connection(self):
        if self.connection:
            self.connection_port.clear()
            self.clear()
        
    def get_port(self):
        return self.port
        
    def is_active(self):
        return self.live_wire
        
    def is_input(self):
        return self.port > 0
        
    def is_output(self):
        return self.port < 0
        
    def is_open(self):
        return self.connection is None

class Node(Dragger):
    isnode = True
    wire = None
    
    def __init__(self, id, name, ports, pos=(width // 2, height // 2), val=None, types=None, color=(100, 100, 100)):
        self.id = id
        self.name = name
      
        self.types = types if types is not None else []
        self.val = val
        
        self.ports = ports
        for p in self.ports:
            p.set_node(self)
      
        self.ctimer = 0

        self.prune = False
        
        self.color = color
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
        
    def get_image(self):
        if isinstance(self, (Num, Bool)):
        
            image = pg.Surface((50, 30)).convert()
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name)
            r = pg.Rect(0, 0, w, 10)
            r.topleft = image.get_rect().topleft
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        elif isinstance(self, String):
            
            image = pg.Surface((50, 50)).convert()
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name)
            r = pg.Rect(0, 0, w, 10)
            r.topleft = image.get_rect().topleft
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        else:
        
            image = pg.Surface((40, 40)).convert()
            image.fill(self.color)
            w, h = image.get_size()
            label = Textbox(self.name)
            r = pg.Rect(0, 0, w - 5, h - 5)
            r.center = image.get_rect().center
            label.fit_text(r)
            image.blit(label.get_image(), r)
            
        return image
        
    def get_elements(self):
        elements = {}
        
        if isinstance(self, Num):
            check = lambda t: t.isnumeric()
            length = 3
        
        elif isinstance(self, Bool):
            check = lambda t: t.lower() in ('t', 'f')
            length = 1
            
        elif isinstance(self, String):
            check = lambda t: True
            length = 50
            
        else:
            return elements
            
        i = Input((self.rect.width - 10, 15 if length != 50 else 30), message=self.val, tcolor=(0, 0, 0), color=(255, 255, 255), check=check, length=length, fitted=True)
        i.rect.center = self.rect.center
        i.rect.y += 5
        elements[i] = (i.rect.x - self.rect.x, i.rect.y - self.rect.y)

        return elements

    def set_port_pos(self):
        ip = self.get_input_ports()
        op = self.get_output_ports()
        
        h = self.rect.height
        
        step = h // (len(ip) + 1)
        for i, y in enumerate(range(self.rect.top + step, self.rect.bottom, step)):
            if i in range(len(ip)):
                ip[i].rect.center = (self.rect.x, y)
            
        step = h // (len(op) + 1)
        for i, y in enumerate(range(self.rect.top + step, self.rect.bottom, step)):
            if i in range(len(op)):
                op[i].rect.center = (self.rect.right, y)

        self.big_rect.center = self.rect.center
        
        sx, sy = self.rect.topleft
        for e in self.elements:
            rx, ry = self.elements[e]
            e.rect.topleft = (sx + rx, sy + ry)
        
    def set_element_pos(self):
        for rel_pos, e in self.elements:
            rx, ry = rel_pos
            sx, sy = self.rect.topleft
            
            r.rect.topleft = (sx + rx, sy + ry)
        
    def set_pos(self, pos):
        self.rect.center = pos
        self.set_port_pos()
        
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
                input.append(ip.connection.get_output(ip.connection_port.port))
            else:
                input.append(self.get_default(ip.port))
                
        return input
        
    def can_compile(self):
        return True
                
    def get_port(self, num):
        return next(p for p in self.ports if p.port == num)
        
    def get_input_ports(self):
        return [p for p in self.ports if p.is_input()]
    
    def get_output_ports(self):
        return [p for p in self.ports if p.is_output()]
        
    def close_all(self):
        for p in self.ports:
            p.close_wire()
            
    def disconnect_all(self):
        for p in self.ports:
            p.clear_connection()
            
    def delete(self):
        self.close_all()
        self.disconnect_all()
        del_node(self)
        
    def new_output_port(self):
        op = self.get_output_ports()
        port = min([p.port for p in op]) - 1
        types = op[0].types.copy() + ['ex']
        p = Port(port, types)
        p.node = self
        p.rect.center = op[0].rect.center
        self.ports.append(p)
        return p
        
    def prune_extra_ports(self):
        for p in self.ports.copy():
            if 'ex' in p.types and not p.connection:
                self.ports.remove(p)
            p.close_wire()
        self.prune = False
        
    def create_out_indicator(self, port):
        n = get_node('Indicator', args=[self.name + ' indicator', [Port(1, port.types), Port(-1, port.types + ['ind'])]])
        n.id = self.id
        n.types = ['ind']
        if hasattr(self, 'contains'):
            setattr(n, 'contains', self.contains)
        n.get_text = self.get_text
        n.get_output = self.get_output
        n.get_default = self.get_default
        port.open_wire()
        self.connect(n, n.get_port(1))
        
    def create_in_indicator(self, port):
        if 'bool' in port.types:
            name = 'Bool'
        elif 'string' in port.types:
            name = 'String'
        elif 'num' in port.types:
            name = 'Num'
        elif 'player' in port.types:
            name = 'Player'
        else:
            return 

        n = get_node(name)
        op = n.get_port(-1)
        op.open_wire()
        n.connect(self, port)
        
    def clear_connections(self):
        for p in self.ports:
            if p.connection:
                p.clear_connection()
                
    def check_break(self, A, B):
        for p in self.get_output_ports():
            if p.visible and p.connection:
                C = p.rect.center
                D = p.connection_port.rect.center
                
                if intersect(A, B, C, D):
                    p.clear_connection()
        self.prune_extra_ports()

    def get_active_port(self):
        return next((p for p in self.ports if p.live_wire), None)
        
    def check_status(self):
        pass
        
    def start_map(self):
        loc_port = None
        flow_port = None
        func_port = None
        
        for op in self.get_output_ports():
            if 'loc' in op.types and op.connection:
                loc_port = op
            elif 'func' in op.types and op.connection:
                func_port = op
            elif 'flow' in op.types and 'split' not in op.types:
                flow_port = op
                
        if loc_port and flow_port:
            ports = loc_port.connection.map_scope([loc_port])
            if flow_port in ports:
                return False
                
        ports = self.map_scope([])
        if len([1 for p in ports if 'func' in p.node.types]) > 1:
            return False
                
        ports = []      
        for op in self.get_output_ports():
            if op.connection:
                ports += op.connection.map_circle([])
        return not any(op in ports for op in self.get_output_ports())
        
    def map_circle(self, ports):                
        for op in self.get_output_ports():
            if op.connection and op not in ports:
                ports.append(op)
                ip = op.connection_port
                if ip not in ports:
                    ip.node.map_circle(ports) 
                    
        return ports

    def map_scope(self, ports, skip_ip=False, skip_op=False): 
        if not skip_ip:
            for ip in self.get_input_ports():
                if ip.connection and ip not in ports:
                    ports.append(ip)
                    op = ip.connection_port
                    if op not in ports:
                        op.node.map_scope(ports, skip_ip=skip_ip, skip_op=skip_op)
                
        if not skip_op:
            for op in self.get_output_ports():
                if 'glob' not in op.types:
                    if op.connection and op not in ports:
                        ports.append(op)
                        ip = op.connection_port
                        if ip not in ports:
                            ip.node.map_scope(ports, skip_ip=skip_ip, skip_op=skip_op)   
                    
        return ports
        
    def trace_flow(self, nodes, dir):
        nodes.append(self)
        
        if dir == -1:
            for ip in self.get_input_ports():
                if ip.connection:
                    if 'flow' in ip.types and ip.connection not in nodes:
                        ip.connection.trace_flow(nodes, dir=dir)
                        
        elif dir == 1:
            for op in self.get_output_ports():
                if op.connection:
                    if 'flow' in op.types and op.connection not in nodes:
                        op.connection.trace_flow(nodes, dir=dir)
                        
        return nodes
        
    def find_parent_func(self):
        nodes = self.trace_flow([], -1)
        return next((n for n in nodes if 'func' in n.types), None)

    def connect(self, n1, p1):
        n0 = self
        p0 = self.get_active_port()

        if any(t in p1.types for t in p0.types):
            p0.connect(n1, p1)
            p1.connect(n0, p0)
            if not eval_scope_data():
                p0.clear()
                p1.clear()
            else:
                if hasattr(self, 'on_connect'):
                    self.on_connect(p0)
                if hasattr(n1, 'on_connect'):
                    n1.on_connect(p1) 

        p0.close_wire()
        p1.close_wire()
        
    def click_down(self, p):
        hit_node = False
        hit_port = False
        dub_click = False
        
        if self.ctimer > 20:
            self.ctimer = 0
        else:
            dub_click = True
        
        for op in self.get_output_ports():
            if op.visible:
                if op.rect.collidepoint(p):
                    
                    hit_port = True
                    
                    if not op.connection:
                    
                        if dub_click:
                            if 'ind' not in op.types:
                                self.create_out_indicator(op)
                        else:
                            op.open_wire()
                            
                            Node.wire = True
                        
                    elif 'val' in op.types:
                        op = self.new_output_port()
                        op.open_wire()
                        
                    break
                    
        if not hit_port:
            for ip in self.get_input_ports():
                if ip.visible:
                    if ip.rect.collidepoint(p):
                        
                        hit_port = True
                        
                        if not ip.connection:
                            
                            if dub_click:
                                self.create_in_indicator(ip)
                                
                        break
                        
        return (hit_node, hit_port, dub_click)
        
    def click_up(self, p):
        n0 = self
        p0 = self.get_active_port()
        if p0:
            for n1 in NODES:
                for p1 in n1.get_input_ports():
                    if p1.rect.collidepoint(p) and not p1.connection:
                        n0.connect(n1, p1)
                        break
                        
        self.close_all()
        self.prune = True
        
        Node.wire = None

    def events(self, input):
        p = pg.mouse.get_pos()
        
        for e in input.copy():
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    hit_node, hit_port, dub_click = self.click_down(p)
                    #if (hit_node or hit_port) and dub_click:
                    #    input.remove(e)
 
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.click_up(p)
                    
        if not self.get_active_port():
            super().events(input)
            
        for e in self.elements:
            e.events(input)
            
    def node_update(self):
        pass
        
    def update(self):
        dx, dy = super().update()
        for p in self.ports.copy():
            p.rect.move_ip(dx, dy)
        self.big_rect.move_ip(dx, dy)
            
        if 'ind' in self.types and self.get_port(1).is_open():
            self.clear_connections()
            del_node(self)
            
        if self.prune:
            self.prune_extra_ports()
            
        self.check_status()

        if self.ctimer < 40:
            self.ctimer += 1
            
        for e in self.elements:
            e.rect.move_ip(dx, dy)
            e.update()
            
        self.node_update()
        
    def draw(self, win):
        if self._selected or self.hover:
            win.blit(rect_outline(self.image, color=(255, 0, 0)), self.rect)
        else:
            win.blit(self.image, self.rect)

        for p in self.ports:
            if p.visible:
                pg.draw.circle(win, get_color(p.types), p.rect.center, p.rect.width // 2)
            if p.live_wire:
                pg.draw.line(win, get_color(p.types), p.rect.center, pg.mouse.get_pos(), width=4)
                
        for e in self.elements:
            e.draw(win)
                
    def draw_ports(self, win):
        for p in self.get_output_ports():
            if p.connection and p.visible:
                s = p.rect.center
                e = p.connection_port.rect.center
                pg.draw.line(win, get_color(p.types), s, e, width=4)
                
class Indicator(Node):
    base = False
    def __init__(self, id, name, ports):
        super().__init__(id, name, ports, types=['ind'])

class Start(Node):
    def __init__(self, id):
        super().__init__(id, 'start', [Port(-1, ['flow'])], types=['func'])
        
    def get_start(self):
        return '\t\tself.mode = 0\n\t\tself.players.clear()\n\t\tself.cards.clear()\n'
        
    def get_text(self):
        return 'def start(self, player):\n'
        
class If(Node):
    def __init__(self, id):
        super().__init__(id, 'if', [Port(1, ['bool']), Port(2, ['flow']), Port(-1, ['split', 'flow']), Port(-2, ['main', 'flow', 'el'])])
        
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'if {0}:\n'.format(*self.get_input())   
        return text
        
class Elif(Node):
    def __init__(self, id):
        super().__init__(id, 'elif', [Port(1, ['bool']), Port(2, ['el']), Port(-1, ['split', 'flow']), Port(-2, ['main', 'flow', 'el'])])
        
    def get_default(self, p):
        if p == 1:
            return 'True'
        
    def get_text(self):
        text = 'elif {0}:\n'.format(*self.get_input())   
        return text
        
class Else(Node):
    def __init__(self, id):
        super().__init__(id, 'else', [Port(1, ['el']), Port(-1, ['split', 'flow']), Port(-2, ['main', 'flow'])])
        
    def get_text(self):
        text = 'else:\n'  
        return text
        
class Bool(Node):
    def __init__(self, id):
        super().__init__(id, 'bool', [Port(-1, ['bool', 'glob', 'val'])], types=['var'], val='T')

    def get_output(self, p):
        v = list(self.elements)[0].get_message()
        if v.lower() == 't':
            return 'True'
        else:
            return 'False'
        
class Num(Node):
    def __init__(self, id):
        super().__init__(id, 'num', [Port(-1, ['num', 'glob', 'val', 'bool'])], types=['var'], val='0')
        
    def get_val(self):
        return self.val

    def get_output(self, p):
        return int(list(self.elements)[0].get_message())
        
class String(Node):
    def __init__(self, id):
        super().__init__(id, 'string', [Port(-1, ['string', 'glob', 'val'])], types=['var'], val="''")
        
    def get_output(self, p):
        return f"'{list(self.elements)[0].get_message()}'"
        
class And(Node):
    def __init__(self, id):
        super().__init__(id, 'and', [Port(1, ['bool']), Port(2, ['bool']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} and {})'.format(*self.get_input())     
        return text
        
class Or(Node):
    def __init__(self, id):
        super().__init__(id, 'or', [Port(1, ['bool']), Port(2, ['bool']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return 'True'
        
    def get_output(self, p):
        text = '({} or {})'.format(*self.get_input())     
        return text
        
class Not(Node):
    def __init__(self, id):
        super().__init__(id, 'not', [Port(1, ['bool']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return 'True'

    def get_output(self, p):
        text = '(not {})'.format(*self.get_input())    
        return text
        
class Equal(Node):
    def __init__(self, id):
        super().__init__(id, 'equal', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({} == {})'.format(*self.get_input())    
        return text
        
class Greater(Node):
    def __init__(self, id):
        super().__init__(id, 'greater', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} > {1})'.format(*self.get_input())    
        return text
        
class Less(Node):
    def __init__(self, id):
        super().__init__(id, 'less', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['bool'])])
        
    def get_default(self, p):
        return '1'

    def get_output(self, p):
        text = '({0} < {1})'.format(*self.get_input())    
        return text
        
class Add(Node):
    def __init__(self, id):
        super().__init__(id, 'add', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['num'])])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class Subtract(Node):
    def __init__(self, id):
        super().__init__(id, 'subtract', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['num'])])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} - {1})'.format(*self.get_input())
        
class Multiply(Node):
    def __init__(self, id):
        super().__init__(id, 'multiply', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['num'])])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} * {1})'.format(*self.get_input())
        
class Divide(Node):
    def __init__(self, id):
        super().__init__(id, 'divide', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['num'])])
        
    def get_default(self, p):
        return '0'
        
    def get_output(self, p):
        return '({0} / {1})'.format(*self.get_input())
        
class For(Node):
    def __init__(self, id):
        super().__init__(id, 'for', [Port(1, ['seq']), Port(2, ['flow']), Port(-1, ['loc', 'val']), Port(-2, ['split', 'flow']), Port(-3, ['flow'])])  
        
        self.get_port(-1).make_invisible()
        ip = self.get_port(1)
        ip.set_cfunc(self.p1_connect)
        ip.set_dfunc(self.p1_disconnect)
        
    def p1_connect(self):
        op = self.get_port(-1)
        op.make_visible()
        n = self.get_port(1).connection
        op.add_type(n.contains)
        
    def p1_disconnect(self):
        op = self.get_port(-1)
        if not op.is_open():
            op.connection_port.clear()
            op.clear()
        op.set_types(['loc', 'val'])
        op.make_invisible()
        
    def get_loop_var(self):
        loop_var = f'x{self.id}'
        
        ip = self.get_port(1)
        
        if not ip.is_open():
            
            node = ip.connection
            
            if node.contains == 'player':
                loop_var = f'p{self.id}'  
            elif node.contains == 'num':  
                loop_var = f'i{self.id}'
            elif node.contains == 'card':
                loop_var = f'c{self.id}'
            elif node.contains == 'string':
                loop_var = f's{self.id}'
            elif node.contains == 'bool':
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
        if p == -1:
            text = self.get_loop_var()
        return text
        
class Break(Node):
    def __init__(self, id):
        super().__init__(id, 'break', [Port(1, ['flow'])]) 
        
        self.on_connect = self.check_status
        
    def check_status(self, p):
        ip = self.get_port(1)
        if ip.connection:
            ports = self.map_scope([], skip_op=True)
            for p in ports:
                if p.connection:
                    if p.connection.name == 'for' and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear_connection()
        
    def get_text(self):
        return 'break\n'
        
class Continue(Node):
    def __init__(self, id):
        super().__init__(id, 'continue', [Port(1, ['flow'])]) 
        
        self.on_connect = self.check_status
        
    def check_status(self, p):
        ip = self.get_port(1)
        if ip.connection:
            ports = self.map_scope([], skip_op=True)
            for p in ports:
                if p.connection:
                    if p.connection.name == 'for' and 'split' in p.connection_port.types:
                        break
            else:
                ip.clear_connection()
        
    def get_text(self):
        return 'continue\n'
        
class List(Node):
    base = False
    def __init__(self, id, name, contains, types=[]):
        super().__init__(id, name, [Port(-1, ['loc', 'seq', 'val'] + [contains])], types=types.copy())   

        self.contains = contains
        
    def get_output(self, p):
        return f'seq{self.id}'
        
    def get_dec(self):
        return f'seq{self.id} = []\n'
        
class Range(Node):
    def __init__(self, id):
        super().__init__(id, 'range', [Port(1, ['num']), Port(2, ['num']), Port(-1, ['glob', 'seq', 'num', 'val'])])
        self.contains = 'num'
        
    def get_default(self, p):
        return '1'
        
    def get_output(self, p):
        text = 'range({0}, {1})'.format(*self.get_input()) 
        return text
        
class Players(Node):
    def __init__(self, id):
        super().__init__(id, 'all players', [Port(-1, ['glob', 'seq', 'val'])])
        self.contains = 'player'
        
    def get_output(self, p):
        return 'self.game.players.copy()'
        
class Opponents(Node):
    def __init__(self, id):
        super().__init__(id, 'opponents', [Port(-1, ['glob', 'seq', 'val'])])
        self.contains = 'player'
        
    def get_output(self, p):
        return 'self.sort_players(player)'
        
class StealOpp(Node):
    def __init__(self, id):
        super().__init__(id, 'opponents with points', [Port(-1, ['glob', 'seq', 'val'])])
        self.contains = 'player'
        
    def get_output(self, p):
        return '[p for p in self.game.players if p.score > 0]'
        
class Player(Node):
    def __init__(self, id):
        super().__init__(id, 'player', [Port(-1, ['glob', 'player', 'val'])])  

    def get_output(self, p):
        return 'player'
        
class CardList(Node):
    def __init__(self, id):
        super().__init__(id, 'card list', [Port(-1, ['loc', 'seq', 'val', 'cs'])], types=['dec'])   

        self.contains = 'card'
        
    def get_output(self, p):
        return f'seq{self.id}'
        
    def get_dec(self):
        return f'seq{self.id} = []\n'
        
class PlayerList(Node):
    def __init__(self, id):
        super().__init__(id, 'player list', [Port(-1, ['loc', 'seq', 'val', 'ps'])], types=['dec'])   

        self.contains = 'player'
        
    def get_output(self, p):
        return f'seq{self.id}'
        
    def get_dec(self):
        return f'seq{self.id} = []\n'
        
class Length(Node):
    def __init__(self, id):
        super().__init__(id, 'length', [Port(1, ['seq', 'string']), Port(-1, ['num'])])   
        
    def get_default(self, port):
        return '[]'
        
    def get_output(self, p):
        return 'len({})'.format(*self.get_input())
        
class AddTo(Node):
    def __init__(self, id):
        super().__init__(id, 'add to', [Port(1, ['seq']), Port(2, []), Port(3, ['flow']), Port(-1, ['flow'])]) 
        
        self.get_port(2).make_invisible()
        ip = self.get_port(1)
        ip.set_cfunc(self.p1_connect)
        ip.set_dfunc(self.p1_disconnect)
        
    def p1_connect(self):
        op = self.get_port(2)
        op.make_visible()
        n = self.get_port(1).connection
        op.set_types([n.contains])
        
    def p1_disconnect(self):
        op = self.get_port(2)
        if not op.is_open():
            op.connection_port.clear()
            op.clear()
        op.set_types([])
        op.make_invisible()
        
    def get_default(self, n):
        if n == 1:
            return '[]'
        elif n == 2:
            p = self.get_port(1)
            if not p.connection:
                return 'None'
            cn = p.connection
            if cn.contains == 'player':
                return 'player'
            elif cn.contains == 'card':
                return 'self'

    def get_text(self):
        return '{0}.append({1})\n'.format(*self.get_input())
      
class MergLists(Node):
    def __init__(self, id):
        super().__init__(id, 'merge lists', [Port(1, ['seq']), Port(2, ['seq']), Port(-1, ['seq'])])  
        
        self.contains = ''

    def on_connect(self, p1):
        if p1.port > 0:
        
            cleared = False
            ap = p1
            if p1.port == 1:
                p2 = self.get_port(2)
            else:
                p2 = p1
                p1 = self.get_port(1)
            
            if p1.connection and p2.connection:
                n1 = p1.connection
                n2 = p2.connection
                
                if n1.contains != n2.contains:
                    ap.clear_connection()
                    cleared = True
            
            if not cleared:
                self.contains = ap.connection.contains
                print(self.contains)

    def get_default(self, p):
        return '[]'
        
    def get_output(self, p):
        return '({} + {})'.format(*self.get_input())
        
class MergLists_ip(Node):
    def __init__(self, id):
        super().__init__(id, 'merge lists in place', [Port(1, ['seq']), Port(2, ['seq']), Port(3, ['flow']), Port(-1, ['flow'])])   
        
    def on_connect(self, p1):
        ap = p1
        if p1.port == 1:
            p2 = self.get_port(2)
        else:
            p2 = p1
            p1 = self.get_port(1)
        
        if p1.connection and p2.connection:
            n1 = p1.connection
            n2 = p2.connection
            
            if n1.contains != n2.contains:
                ap.clear_connection()
        
    def get_default(self, p):
        return '[]'
        
    def get_text(self):
        return '{0} += {1}\n'.format(*self.get_input())

class Contains(Node):
    def __init__(self, id):
        super().__init__(id, 'contains', [Port(1, ['player', 'card']), Port(2, ['seq']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return '[]'
        
    def get_output(self, p):
        text = '({0} in {1})'.format(*self.get_input())
        return text
        
class GetPlayed(Node):
    def __init__(self, id):
        super().__init__(id, 'get played', [Port(1, ['player']), Port(-1, ['loc', 'seq', 'val', 'cs'])])   

        self.contains = 'card'
        
    def get_default(self, p):
        return 'player'
        
    def get_output(self, p):
        text = '{}.played.copy()'.format(*self.get_input())
        return text
        
class HasTag(Node):
    def __init__(self, id):
        super().__init__(id, 'has tag', [Port(1, ['string']), Port(2, ['card']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({0} in {1}.tags)'.format(*self.get_input())
        return text
        
class HasName(Node):
    def __init__(self, id):
        super().__init__(id, 'has name', [Port(1, ['string']), Port(2, ['card']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        if p == 1:
            return "''"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({1}.name == {0})'.format(*self.get_input())
        return text
        
class TagFilter(Node):
    def __init__(self, id):
        super().__init__(id, 'tag filter', [Port(1, ['string']), Port(2, ['cs']), Port(-1, ['seq'])])
        
        self.contains = 'card'
        
    def get_default(self, p):
        return '[]'
        
    def get_output(self, p):
        text = "[x for x in {1} if {0} in getattr(x, 'tags', [])]"
        text = text.format(*self.get_input())
        return text
        
class Gain(Node):
    def __init__(self, id):
        super().__init__(id, 'gain', [Port(1, ['num']), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.gain(self, {0})\n'.format(*self.get_input())
        return text      

class Lose(Node):
    def __init__(self, id):
        super().__init__(id, 'lose', [Port(1, ['num']), Port(2, ['player']), Port(3, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'player'
        
    def get_text(self):
        text = '{1}.lose(self, {0})\n'.format(*self.get_input())
        return text      
        
class Steal(Node):
    def __init__(self, id):
        super().__init__(id, 'steal', [Port(1, ['num']), Port(2, ['player']), Port(3, ['player']), Port(4, ['flow']), Port(-1, ['flow'])])  
     
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p in (2, 3):
            return 'player'
        
    def get_text(self):
        text = '{1}.steal(self, {0}, {2})\n'.format(*self.get_input())
        return text      

class StartFlip(Node):
    def __init__(self, id):
        super().__init__(id, 'start flip', [Port(1, ['flow'])]) 

    def get_text(self):
        pf = self.find_parent_func()
        if pf:
            if pf.name != 'start':
                return "self.wait = 'flip'\n"
        return "player.add_request(self, 'flip')\n"
        
    def on_connect(self, p):
        if p.port == 1 and not exists('flip'):
            get_node('Flip')
        
class Flip(Node):
    def __init__(self, id):
        super().__init__(id, 'flip', [Port(-1, ['bool', 'loc']), Port(-2, ['flow', 'func'])], types=['func']) 
            
    def get_text(self):
        return '\n\tdef flip(self, player, coin):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'coin'

class StartRoll(Node):
    def __init__(self, id):
        super().__init__(id, 'start roll', [Port(1, ['flow'])]) 

    def get_text(self):
        return "player.add_request(self, 'roll')\n"
        
    def on_connect(self, p):
        if p.port == 1 and not exists('roll'):
            get_node('Roll')
        
class Roll(Node):
    def __init__(self, id):
        super().__init__(id, 'roll', [Port(-1, ['num', 'loc']), Port(-2, ['flow', 'func'])], types=['func']) 
            
    def get_text(self):
        return '\n\tdef roll(self, player, dice):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'dice'
            
class StartSelect(Node):
    def __init__(self, id):
        super().__init__(id, 'start select', [Port(1, ['flow'])]) 

    def get_text(self):
        return "player.add_request(self, 'select')\n"
        
    def on_connect(self, p):
        if p.port == 1:
            if not exists('get selection'):
                get_node('GetSelection', pos=(self.rect.centerx + self.rect.width + 5, self.rect.centery), held=False)
            if not exists('select'):
                get_node('Select', pos=(self.rect.centerx, self.rect.centery + self.rect.height + 5), held=False)
            
class GetSelection(Node):
    def __init__(self, id):
        super().__init__(id, 'get selection', [Port(-1, ['seq', 'loc']), Port(-2, ['flow', 'func'])], types=['func']) 
        self.contains = ''
            
    def get_start(self):
        return '\t\tselection = []\n'
            
    def get_text(self):
        return '\n\tdef get_selection(self, player):\n'
        
    def get_end(self):
        return '\t\treturn selection\n'
        
    def get_output(self, p):
        if p == -1:
            return 'selection'
      
class Select(Node):
    def __init__(self, id):
        super().__init__(id, 'select', [Port(-1, ['num', 'loc']), Port(-2, ['card', 'player', 'loc']), Port(-3, ['flow', 'func'])], types=['func']) 
            
    def get_start(self):
        return '\t\tif not num:\n\t\t\treturn\n\t\tc = player.selected.pop(0)\n'
            
    def get_text(self):
        return '\n\tdef select(self, player, num):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'num'
        elif p == -2:
            return 'c'
  
