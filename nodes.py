import pygame as pg
from constants import *
from spritesheet import Textbox, create_text, Input
from writecard import NodeParser
from builder import outline_buttons, fit_text, Dropdown, apply_outline

colors = {'player': (255, 0, 0), 'seq': (0, 255, 0), 'num': (0, 0, 255), 'bool': (255, 255, 0), 'string': (255, 0, 255), 'card': (0, 255, 255), 'flow': (128, 128, 128), 'spawn': (255, 255, 255)}

class Port:
    def __init__(self, port, types):
        self.port = port
        self.types = types
        
        self.connection = None
        self.connection_port = None
        
        self.rect = None
        self.color = (0, 0, 0)
        
    def add_type(self, type):
        if type not in self.types:
            
            self.types.append(type)
            
    def remove_type(self, type):
        if type in self.types:
            
            self.types.remove(type)

    def update_types(self, types):
        self.types = types

    def is_input(self):
        return self.port > 0
        
    def is_output(self):
        return self.port < 0
        
    def clear(self):
        self.connection = None
        self.connection_port = None

class Node:
    def __init__(self, name, id, ports, type, val=None):
        self.name = name
        self.id = id
        self.scope = 0

        self.val = val
        
        self.type = type
        
        self.children = []
        self.parents = []
        
        self.contains = ''

        self.ports = ports
        self.open_port = None
        
        self.parent_block = None
        
        self.pos = (width // 2, height // 2)
        
        self.init_visual()

    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name

    def get_input_ports(self):
        return [p for p in self.ports if p.port > 0]
        
    def get_output_ports(self):
        return [p for p in self.ports if p.port < 0]

    def get_port_by_num(self, port):
        return next((p for p in self.ports if p.port == port), None)
        
    def clear_port(self, port):
        p = self.get_port_by_num(port) 
        p.clear()
        
    def update_connection_scope(self, scope1, scope2):
        self.scope = scope2
        
        for p in self.ports:
            
            if p.connection is not None:
                
                if p.connection.scope == scope1:

                    p.connection.update_connection_scope(scope1, scope2)

    def get_port_by_types(self, io, types, force=False):
        if io == 'in':
            
            ports = self.get_input_ports()
            
        else:
            
            ports = self.get_output_ports()
            
        for p in ports:
            
            if any(t in p.types for t in types) and p.connection is None:
                
                return p
                
        else:
            
            if force:
                
                p = self.add_port(io, types)
                
                return p

    def add_port(self, io, types, mult=False):
        if io == 'in':
            
            p = len(self.get_input_ports()) + 1

        elif io == 'out':
            
            p = -len(self.get_output_ports()) - 1
            
        port = Port(p, types)
        self.ports.append(port)
        
        if not mult:
        
            self.init_visual()
            
        else:
            
            port.rect = self.get_input_ports()[0].rect.copy()
        
        return port
        
    def add_child(self, child):
        self.children.append(child)
        
        if child.type != 'func':

            child.scope = self.scope
            
    def get_all_scope_nodes(self, nodes=[]):
        nodes.append(self)

        for p in self.ports:
            
            if p.connection is not None:
                
                if p.connection not in nodes and p.connection.scope == self.scope:
                
                    nodes += p.connection.get_all_scope_nodes(nodes)
                    
        return list(set(nodes))

#visual stuff------------------------------------------------------------------------
    
    def init_visual(self):
        if self.type == 'func':
        
            self.color = (128, 0, 128)
        
        else:
        
            self.color = (128, 128, 128)
        
        self.image = pg.Surface((50, 50)).convert()
        self.image.fill(self.color)
        
        tl = self.pos
        self.rect = self.image.get_rect()
        
        tr = pg.Rect(0, 0, 30, 30)
        text = fit_text(tr, self.name)
        tr.center = self.rect.center
        self.image.blit(text, tr)
        
        p_image = pg.Surface((10, 10)).convert()

        input_ports = self.get_input_ports()
        output_ports = self.get_output_ports()
 
        for i, ports in enumerate((input_ports, output_ports)):

            step = self.rect.height // (len(ports) + 1)
            
            if i == 0:
                
                x = 0
                
            elif i == 1:
                
                x = self.rect.width - p_image.get_size()[0]

            for y, p in enumerate(ports):

                types = p.types
                
                if len(types) > 1:
                    
                    color = (255, 255, 255)
                    
                elif types:
                    
                    color = colors[types[0]]
                    
                else:
                    
                    color = (0, 0, 0)
                    
                p_image.fill(color)

                y = (y * step) + step
                
                r = p_image.get_rect()
                r.midleft = (x, y)
                self.image.blit(apply_outline(p_image, (255, 255, 255)), r)
                
                p.rect = r
                p.color = color
                
        self.move(tl)
        
    def get_input(self):
        if self.val is not None:
            
            if self.name == 'num':
                
                type = 2
                val = self.get_val()
                length = 5
                
            elif self.name == 'string':
                
                type = 4
                val = self.get_val().replace("'", '')
                length = 20
                
            elif self.name == 'bool':
                
                type = 'tfTF'
                val = self.get_val()[0]
                length = 1
            
            return Input(val, tsize=20, type=type, length=length)
    
    def update_text(self, input):
        val = input.get_message()

        if self.name == 'num':
    
            val = int(val)
            
        elif self.name == 'string':
            
            val = "'" + val + "'"
            
        elif self.name == 'bool':
            
            if val == 'T':
                
                val = True
                
            else:
                
                val = False
        
        self.val = val
    
    def move(self, pos):
        dx, dy = pos
        
        self.rect = self.rect.move(dx, dy)
        
        for p in self.ports:
            
            p.rect = p.rect.move(dx, dy)

    def can_hold(self, mouse):
        
        var = mouse.colliderect(self.rect) and not any(mouse.colliderect(p.rect) for p in self.ports)
        
        if var:
            
            print(self.get_parent_blocks([]))
            
        return var
            
    def hit_mouse(self, mouse, other_node):
        if self.rect.colliderect(mouse):
        
            for p in self.ports:

                if p.rect.colliderect(mouse):
                    
                    if p.connection is None or self.type in ('loc', 'glob', 'op'):
                    
                        if other_node is None and p.is_output():
                            
                            self.open_port = p

                            return self
                            
    def get_parent_blocks(self, checked, func=None): 
        blocks = self.parents.copy()

        checked.append(self)
      
        if self.type == 'block':
            
            blocks.append(self)
            
        if self.type == 'func':
            
            if func is None:
                
                func = self
            
        if self.type != 'flow':
            
            for p in self.get_output_ports():
            
                if p.connection is not None and p.connection not in checked:

                    b, f = p.connection.get_parent_blocks(checked, func)
                    blocks += b
                    func = f
                    
        if self.type != 'func':
   
            for p in self.get_input_ports():
                
                if p.connection is not None and p.connection not in checked:

                    b, f = p.connection.get_parent_blocks(checked, func)
                    blocks += b
                    func = f

        return (blocks, func)
        
    def get_parent_function(self):
        return self.get_parent_blocks([])[1]
                     
    def check_parents(self, node):
        if node.type == 'glob':
            
            return True
        
        p1, f1 = self.get_parent_blocks([])
        p2, f2 = node.get_parent_blocks([])
        
        if node.type == 'loc':
            
            return (f1 is f2 and (f1 and f2)) or ((f1 and not f2) or (f2 and not f1))
            
        else:

            start = f1 or f2

            return start and (any(p in p1 for p in p2) or (not p1 or not p2))
 
#connection stuff-------------------------------------------------------------------------------------

    def can_connect(self, node, iport, oport):
        if node is not self and self.check_parents(node):

            if iport.connection is None:
                
                if hasattr(self, 'special_connect'):
                    
                    cond = self.special_connect(iport, oport, node)
                    
                else:
                    
                    cond = True
                
                if any(t in oport.types for t in iport.types) and cond:

                    return True
                    
        return False
  
    def accept_connection(self, mouse, node):
        oport = node.open_port
        
        for iport in self.get_input_ports():
        
            if iport.rect.colliderect(mouse):

                if self.can_connect(node, iport, oport):
                    
                    sn = []
                    
                    self.connect(node, iport, oport, sn)

                    return sn
        
    def connect(self, node, iport, oport, sn):
        iport.connection = node
        iport.connection_port = oport
        oport.connection = self
        oport.connection_port = iport
        
        if hasattr(self, 'spawn_node'):

            nn = self.spawn_node(iport, oport, node)
            
            if nn is not None:
                
                sn.append(nn)
            
                iport = nn.get_port_by_types('in', ['spawn'], force=True)
                oport = self.get_port_by_types('out', ['spawn'])  

                nn.connect(self, iport, oport, sn)

        if hasattr(self, 'on_connect'):
            
            self.on_connect(iport, oport, node)
                    
        return sn

    def get_value(self):
        return self.val
          
    def get_inputs(self):
        return [ip.get_val() for ip in self.inputs if 'flow' not in ip.output_types]
                    
    def get_child_id(self):
        return str(self.id) + str(self.id)
        
    def find_parent(self):
        if 'block' in self.types:
                
            return self.id
            
        else:
            
            n = next((n for n in self.inputs if 'flow' in n.input_types), None)
            
            if n:
                
                return n.find_parent()

    def check_open(self, p, io):
        if io == 'in':
            
            ports = self.inputs
            
        elif io == 'out':
            
            ports = self.outputs
            
        return ports.get(p) is None

    def find_port(self, io, type):
        p = None
        
        for p in self.ports:
            
            if type in self.ports[p] or self.ports[p] == type:
                
                if io == 'in':
                
                    ports = self.inputs
                    
                else:
                    
                    ports = self.outputs
                    
                if ports.get(p) is None:

                    return p

        p = self.add_port(io, type)
            
        return p

class Start(Node):
    def __init__(self, id):
        super().__init__('start', id, [Port(-1, ['flow'])], 'func')

    def get_val(self):
        return 'def start(self, player):\n\t\tself.mode = 0\n'
        
    def get_default_body(self):
        return '\t\tpass\n'
          
class Player(Node):
    def __init__(self, id, val='player'):
        super().__init__('player', id, [Port(-1, ['player'])], 'glob', val)
        
    def get_val(self):
        return self.val
        
class Players(Node):
    def __init__(self, id):
        super().__init__('players', id, [Port(-1, ['seq'])], 'glob', 'self.game.players.copy()')

        self.contains = 'player'

    def get_val(self):
        return self.val
        
class Opponents(Node):
    def __init__(self, id):
        super().__init__('opponents', id, [Port(-1, ['seq'])], 'glob', 'self.sort_players(player)')

        self.contains = 'player'
        
    def get_val(self):
        return self.val
        
class StealOpp(Node):
    def __init__(self, id):
        super().__init__('steal opp', id, [Port(-1, ['seq'])], 'glob', "self.sort_players(player, 'steal')")

        self.contains = 'player'
        
    def get_val(self):
        return self.val
        
class Num(Node):
    def __init__(self, id, val=0):
        super().__init__('num', id, [Port(-1, ['num'])], 'glob', val)
        
    def get_val(self):
        return str(self.val)
        
class String(Node):
    def __init__(self, id, val="''"):
        super().__init__('string', id, [Port(-1, ['string'])], 'glob', val)
        
    def get_val(self):
        return str(self.val)
        
class Bool(Node):
    def __init__(self, id, val=True):
        super().__init__('bool', id, [Port(-1, ['bool'])], 'glob', val)
        
    def get_val(self):
        return str(self.val)
        
class List(Node):
    def __init__(self, id, contains):
        super().__init__(f'{contains} list', id, [Port(-1, ['seq'])], 'loc')
        
        self.contains = contains
        
    def get_val(self):
        return 'seq{}'.format(self.id)
        
    def get_dec(self):
        return '{} = {}'.format(self.get_val(), str([n.connection.val for n in self.get_input_ports() if n.connection is not None]))

class PlayerList(List):
    def __init__(self, id):
        super().__init__(id, 'player')
        
class CardList(List):
    def __init__(self, id):
        super().__init__(id, 'card')
        
class Range(Node):
    def __init__(self, id):
        super().__init__('range', id, [Port(1, ['num']), Port(2, ['num']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'num'
        
    def get_val(self):
        return 'range({}, {})'
        
    def get_default(self):
        return 'range(1)'
        
class AddTo(Node):
    def __init__(self, id):
        super().__init__('add to', id, [Port(1, ['seq']), Port(2, ['card', 'player']), Port(3, ['flow']), Port(-1, ['flow'])], 'flow')
        
        self.contains = ''
        
    def get_val(self):
        return '{}.append({})\n'
        
    def get_default(self):
        return '\n'
        
    def special_connect(self, iport, oport, node):
        if iport.port == 1:
            
            p = self.get_port_by_num(2)
            
            if p.connection is not None:
               
                if 'player' in p.connection_port.types:    
                    
                    return node.contains == 'player'
                    
                elif 'card' in p.connection_port.types:
                    
                    return node.contains == 'card'
                    
            else:
                
                return True
                
        elif iport.port == 2:
            
            p = self.get_port_by_num(1)

            if p.connection is not None:
                
                if 'player' in oport.types:    
                    
                    return p.connection.contains == 'player'
                    
                elif 'card' in oport.types:
                    
                    return p.connection.contains == 'card'
                    
            else:
                
                return True
                
        else:
            
            return True
  
class Card(Node):
    def __init__(self, id, val='None'):
        super().__init__('card', id, [Port(-1, ['card'])], 'spawn', val)
        
    def get_val(self):
        return self.val
        
class Length(Node):
    def __init__(self, id):
        super().__init__('length', id, [Port(1, ['seq']), Port(-1, ['num'])], 'op')
        
    def get_val(self):
        return 'len({})'
        
    def get_default(self):
        return 'len([])'
        
class And(Node):
    def __init__(self, id):
        super().__init__('and', id, [Port(1, ['bool']), Port(2, ['bool']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '({} and {})'
        
    def get_default(self):
        return '(True and True)'
        
class Or(Node):
    def __init__(self, id):
        super().__init__('or', id, [Port(1, ['bool']), Port(2, ['bool']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '({} or {})'
        
    def get_default(self):
        return '(True and True)'
        
class Not(Node):
    def __init__(self, id):
        super().__init__('not', id, [Port(1, ['bool']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '(not ({}))'
        
    def get_default(self):
        return '(not (False))'
        
class Equal(Node):
    def __init__(self, id):
        super().__init__('equal', id, [Port(1, ['num', 'string', 'seq', 'player', 'card']), Port(2, ['num', 'string', 'seq', 'player', 'card']), Port(-1, ['bool'])], 'op')

    def special_connect(self, iport, oport, node):
        p1 = self.get_port_by_num(1)
        p2 = self.get_port_by_num(2)
        
        if p1.connection:
            
            types = p1.connection_port.types
            
        elif p2.connection:
            
            types = p2.connection_port.types
            
        else:
            
            return True
            
        return any(t in types for t in oport.types)

    def get_val(self):
        return '({} == {})'
        
    def get_default(self):
        return '(0 == 0)'
        
class GreaterThan(Node):
    def __init__(self, id):
        super().__init__('greater', id, [Port(1, ['num']), Port(2, ['num']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '({} > {})'
        
    def get_default(self):
        return '(1 > 0)'
        
class LessThan(Node):
    def __init__(self, id):
        super().__init__('less', id, [Port(1, ['num']), Port(2, ['num']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '({} < {})'
        
    def get_default(self):
        return '(0 > 1)'
            
class IfBlock(Node):
    def __init__(self, id):
        super().__init__('if block', id, [Port(1, ['bool']), Port(2, ['spawn']), Port(-1, ['flow'])], 'block')
   
    def get_val(self):
        return 'if {}:\n'
        
    def get_default(self):
        return 'if True:\n'
        
class If(Node):
    def __init__(self, id):
        super().__init__('if', id, [Port(1, ['flow']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'flow')
        
    def get_val(self):
        return ''
        
    def get_default(self):
        return ''
        
    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
        
            nn = IfBlock(self.id)
            self.add_child(nn)
            
            return nn
  
class ElifBlock(Node):
    def __init__(self, id):
        super().__init__('elif block', id, [Port(1, ['bool']), Port(2, ['spawn']), Port(-1, ['flow'])], 'block')
   
    def get_val(self):
        return 'elif {}:\n'
        
    def get_default(self):
        return 'elif True:\n'
        
class Elif(Node):
    def __init__(self, id):
        super().__init__('elif', id, [Port(1, ['flow']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'flow')
        
    def get_val(self):
        return ''

    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
        
            nn = ElifBlock(self.id)
            self.add_child(nn)
            node.add_child(nn)
            
            return nn
            
    def special_connect(self, iport, oport, node):
        return node.name in ('if', 'elif')
  
class ElseBlock(Node):
    def __init__(self, id):
        super().__init__('else block', id, [Port(1, ['spawn']), Port(-1, ['flow'])], 'block')
   
    def get_val(self):
        return 'else:\n'
        
class Else(Node):
    def __init__(self, id):
        super().__init__('else', id, [Port(1, ['flow']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'flow')
        
    def get_val(self):
        return ''
        
    def get_default(self):
        return ''
        
    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
        
            nn = ElseBlock(self.id)
            self.add_child(nn)
            node.add_child(nn)
            
            return nn
            
    def special_connect(self, iport, oport, node):
        return node.name in ('if', 'elif')
  
class ForBlock(Node):
    def __init__(self, id):
        super().__init__('for block', id, [Port(1, ['seq']), Port(2, ['spawn']), Port(-1, []), Port(-2, ['flow'])], 'block')
        
        self.loop_var = 'i{}'.format(self.id)
        
    def get_val(self):
        return 'for {} in {{}}:\n'.format(self.loop_var)
        
    def get_default(self):
        return 'for i{} in range(1):\n'.format(self.id)
        
    def on_connect(self, iport, oport, node):
        if 'seq' in iport.types:

            if node.contains == 'player':
                
                self.loop_var = f'p{self.id}'
                
            elif node.contains == 'num':
                
                self.loop_var = f'i{self.id}'

            elif node.contains == 'card':
                
                self.loop_var = f'c{self.id}'

            elif node.contains == 'string':
                
                self.loop_var = f's{self.id}'

            elif node.contains == 'bool':
                
                self.loop_var = f'b{self.id}'
                
            self.get_port_by_num(-1).update_types([node.contains])
            self.init_visual()
  
class For(Node):
    def __init__(self, id):
        super().__init__('for', id, [Port(1, ['flow']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'flow')
        
    def get_val(self):
        return ''
        
    def get_default(self):
        return ''
        
    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:

            nn = ForBlock(self.id)
            self.add_child(nn)
            
            return nn

class Break(Node):
    def __init__(self, id):
        super().__init__('end for', id, [Port(1, ['flow'])], 'flow')
        
    def get_val(self):
        return 'break\n'
        
    def special_connect(self, iport, oport, node):
        return any(n.name == 'for block' for n in node.get_parent_blocks([])[0])
        
class Continue(Node):
    def __init__(self, id):
        super().__init__('continue for', id, [Port(1, ['flow'])], 'flow')
        
    def get_val(self):
        return 'continue\n'
        
    def special_connect(self, iport, oport, node):
        return any(n.name == 'for block' for n in node.get_parent_blocks([])[0])

class Gain(Node):
    def __init__(self, id):
        super().__init__('gain', id, [Port(1, ['player']), Port(2, ['num']), Port(3, ['flow']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return '{}.gain(self, {})\n'
        
    def get_default(self):
        return 'player.gain(self, 1)\n'
        
class Lose(Node):
    def __init__(self, id):
        super().__init__('lose', id, [Port(1, ['player']), Port(2, ['num']), Port(3, ['flow']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return '{}.lose(self, {})\n'
        
    def get_default(self):
        return 'player.lose(self, 1)\n'
        
class Steal(Node):
    def __init__(self, id):
        super().__init__('steal', id, [Port(1, ['player']), Port(2, ['num']), Port(3, ['flow']), Port(3, ['player']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return '{}.steal(self, {}, {})\n'
        
    def get_default(self):
        return "player.steal(self, 1, self.sort_players(player, 'steal')[0])\n"
        
class GetPlayed(Node):
    def __init__(self, id):
        super().__init__('get played', id, [Port(1, ['player']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'card'
        
    def get_val(self):
        return '{}.played.copy()'
        
    def get_default(self):
        return 'player.played.copy()'

class FlipBlock(Node):
    def __init__(self, id):
        super().__init__('flip block', id, [Port(1, ['spawn', 'flow']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'func')
        
    def get_val(self):
        return 'def coin(self, player, coin):\n'
        
    def get_default_body(self):
        return '\t\tpass\n'

    def spawn_node(self, iport, oport, node):
        nn = Bool(self.id, 'coin')
        nn.name = 'coin'
        self.add_child(nn)
        
        return nn

class Flip(Node):
    def __init__(self, id):
        super().__init__('flip coin', id, [Port(1, ['flow']), Port(-1, ['spawn', 'flow'])], 'flow')
        
    def get_val(self):
        pf = self.get_parent_function()
        
        if pf:
            
            if pf.name in ('flip block', 'roll block', 'select block'):
                
                return "self.wait = 'flip'\n"

        return "player.add_request(self, 'flip')\n"

    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
            
            nn = FlipBlock(self.id)
            self.add_child(nn)
            
            return nn
            
class RollBlock(Node):
    def __init__(self, id):
        super().__init__('roll block', id, [Port(1, ['spawn']), Port(-1, ['spawn']), Port(-2, ['flow'])], 'func')
        
    def get_val(self):
        return 'def dice(self, player, dice):\n'
        
    def get_default_body(self):
        return '\t\tpass\n'

    def spawn_node(self, iport, oport, node):
        nn = Num(self.id, 'dice')
        nn.name = 'dice'
        self.add_child(nn)
        
        return nn

class Roll(Node):
    def __init__(self, id):
        super().__init__('roll dice', id, [Port(1, ['flow']), Port(-1, ['spawn'])], 'flow')
        
    def get_val(self):
        pf = self.get_parent_function()
        
        if pf:
            
            if pf.name in ('flip block', 'roll block', 'select block'):
                
                return "self.wait = 'roll'\n"

        return "player.add_request(self, 'roll')\n"

    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
            
            nn = RollBlock(self.id)
            self.add_child(nn)
            
            return nn

class ReturnList(Node):
    def __init__(self, id):
        super().__init__('return list', id, [Port(1, ['flow']), Port(2, ['seq']), Port(-1, ['seq'])], 'flow')
        
        self.contains = ''
        
    def on_connect(self, iport, oport, node):
        if iport.port == 3:
            
            self.contains = node.contains
        
    def get_val(self):
        return 'return {}\n'
        
    def get_default(self):
        return 'return []\n'

class SelectBlock(Node):
    def __init__(self, id):
        super().__init__('select block', id, [Port(1, ['flow', 'spawn']), Port(-2, ['flow'])], 'func')
        
    def get_val(self):
        return 'def get_selection(self, player):\n'
        
    def get_default_body(self):
        return '\t\treturn []\n'

class Select(Node):
    def __init__(self, id):
        super().__init__('new selection', id, [Port(1, ['flow']), Port(-1, ['flow', 'spawn']), Port(-2, ['flow'])], 'flow')
        
    def get_val(self):
        pf = self.get_parent_function()
        
        if pf:
            
            if pf.name in ('flip block', 'roll block', 'select block'):
                
                return "self.wait = 'select'\n"

        return "player.add_request(self, 'select')\n"

    def spawn_node(self, iport, oport, node):
        if 'flow' in iport.types:
            
            nn = SelectBlock(self.id)
            self.add_child(nn)
            
            return nn
            
class PostSelectBlock(Node):
    def __init__(self, id):
        super().__init__('post select block', id, [Port(1, ['flow', 'spawn']), Port(-1, ['flow'])], 'func')
        
    def get_val(self):
        return 'def select(self, player, num):\n\t\ts = player.selected.pop(0)\n\t\tif isinstance(s, Card):\n\t\t\tself.extra_card = s\n\t\telse:\n\t\t\tself.extra_player = s\n'
        
    def get_default_body(self):
        return '\t\tpass\n'
  
class PostSelect(Node):
    def __init__(self, id):
        super().__init__('post select', id, [Port(1, ['flow']), Port(-1, ['flow'])], 'func')
        
    def special_connect(self, iport, oport, node):
        return node.name == 'new selection'
        
    def get_val(self):
        return 'def select(self, player, num):\n\t\ts = player.selected.pop(0)\n\t\tif isinstance(s, Card):\n\t\t\tself.extra_card = s\n\t\telse:\n\t\t\tself.extra_player = s\n'
        
    def get_default_body(self):
        return '\t\tpass\n'
  
class HasName(Node):
    def __init__(self, id):
        super().__init__('has name', id, [Port(1, ['card']), Port(2, ['string']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '{}.name == {}'
        
    def get_default(self):
        return 'True'

class DrawTreasure(Node):
    def __init__(self, id):
        super().__init__('draw treasure', id, [Port(1, ['player']), Port(2, ['flow'])], 'op')
        
    def get_val(self):
        return "{}.draw_cards('treasure')"    

class DrawItem(Node):
    def __init__(self, id):
        super().__init__('draw item', id, [Port(1, ['player']), Port(2, ['flow'])], 'op')
        
    def get_val(self):
        return "{}.draw_cards('items')"

class HasTag(Node):
    def __init__(self, id):
        super().__init__('has tag', id, [Port(1, ['string']), Port(2, ['card']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '{} in {}.tags'
        
    def get_default(self):
        return 'True'
        
class TagFilter(Node):
    def __init__(self, id):
        super().__init__('filter by tag', id, [Port(1, ['seq']), Port(2, ['string']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'card'
        
    def get_val(self):
        return "[x for x in {} if {} in getattr(x, 'tags', [])]"
        
    def get_default(self):
        return '[]'
      
class CombineList(Node):
    def __init__(self, id):
        super().__init__('combine list', id, [Port(1, ['seq']), Port(2, ['seq']), Port(3, ['flow']), Port(-1, ['flow'])], 'flow')
        
        self.contains = ''
        
    def get_val(self):
        return '{} += {}\n'
        
    def get_default(self):
        return '[]'
        
    def on_connect(self, iport, oport, node):
        self.contains = node.contains
        
    def special_connect(self, iport, oport, node):
        p1, p2 = self.get_input_ports()[:-1]
        
        if p1.connection or p2.connection:
        
            return node.contains == self.contains
        
        else:
            
            return True

class Multiply(Node):
    def __init__(self, id):
        super().__init__('mult', id, [Port(1, ['num']), Port(2, ['num']), Port(-1, ['num'])], 'op')
        
    def get_val(self):
        return '{} * {}'
        
    def get_default(self):
        return '1'

class CheckFirst(Node):
    def __init__(self, id):
        super().__init__('check first', id, [Port(1, ['player']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return 'self.game.check_first({})'
        
    def get_default(self):
        return 'True'

class CheckLast(Node):
    def __init__(self, id):
        super().__init__('check last', id, [Port(1, ['player']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return 'self.game.check_last({})'
        
    def get_default(self):
        return 'True'
       
class RandomCards(Node):
    def __init__(self, id):
        super().__init__('random cards', id, [Port(1, ['num']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'card'
        
    def get_val(self):
        return "self.game.draw_cards('play', {})"
        
    def get_default(self):
        return "self.game.draw_cards('play', 1)"
               
class HasLandscape(Node):
    def __init__(self, id):
        super().__init__('has landscape', id, [Port(1, ['player']), Port(2, ['string']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return "{}.has_card('landscapes', {})"
        
    def get_default(self):
        return 'True'
        
class HasSpell(Node):
    def __init__(self, id):
        super().__init__('has spell', id, [Port(1, ['player']), Port(2, ['string']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return "{}.has_card('ongoing', {})"
        
    def get_default(self):
        return 'True'
        
class HasItem(Node):
    def __init__(self, id):
        super().__init__('has item', id, [Port(1, ['player']), Port(2, ['string']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return "{}.has_card('items', {})"
        
    def get_default(self):
        return 'True'

class MaxScore(Node):
    def __init__(self, id):
        super().__init__('max score', id, [Port(1, ['seq']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'player'
        
    def special_connect(self, iport, oport, node):
        return 'player' in oport.types
        
    def get_val(self):
        return '[p for p in {0} if p.score == max(p.score for p in {0}, default=-1)]'
        
    def get_default(self):
        return '[]'

class MinScore(Node):
    def __init__(self, id):
        super().__init__('min score', id, [Port(1, ['seq']), Port(-1, ['seq'])], 'op')
        
        self.contains = 'player'
        
    def special_connect(self, iport, oport, node):
        return 'player' in oport.types
        
    def get_val(self):
        return '[p for p in {0} if p.score == min(p.score for p in {0}, default=-1)]'
        
    def get_default(self):
        return '[]'
        
class IsEvent(Node):
    def __init__(self, id):
        super().__init__('is event', id, [Port(1, ['string']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return "(self.game.get_event() == {})"
        
    def get_default(self):
        return 'True'
 
class IndexSelf(Node):
    def __init__(self, id):
        super().__init__('index self', id, [Port(-1, ['num'])], 'glob')
        
    def get_val(self):
        return '(player.played.index(self) if self in player.played else len(player.played))'
        
    def get_default(self):
        return 'True'
    
class TagExists(Node):
    def __init__(self, id):
        super().__init__('tag exists', id, [Port(1, ['string']), Port(2, ['seq']), Port(-1, ['num'])], 'op')
        
    def special_connect(self, iport, oport, node):
        return node.contains == 'card'
        
    def get_val(self):
        return 'any({} in c.tags for c in {})'
        
    def get_default(self):
        return 'True'
    
class SetCard(Node):
    def __init__(self, id):
        super().__init__('set card', id, [Port(1, ['card']), Port(2, ['flow']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return 'self.extra_card = {}\n'
        
    def get_default(self):
        return 'self.extra_card = self.copy()\n'
        
class GetCard(Node):
    def __init__(self, id):
        super().__init__('get card', id, [Port(-1, ['card'])], 'glob')
        
    def get_val(self):
        return 'self.extra_card'
        
class SetPlayer(Node):
    def __init__(self, id):
        super().__init__('set player', id, [Port(1, ['player']), Port(2, ['flow']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return 'self.extra_player = {}\n'
        
    def get_default(self):
        return 'self.extra_player = player\n'
        
class GetPlayer(Node):
    def __init__(self, id):
        super().__init__('get player', id, [Port(-1, ['player'])], 'glob')
        
    def get_val(self):
        return 'self.extra_player'
        
class GetMode(Node):
    def __init__(self, id):
        super().__init__('get mode', id, [Port(-1, ['num'])], 'num', 'self.mode')
        
    def get_val(self):
        return 'self.mode'
        
class IncMode(Node):
    def __init__(self, id):
        super().__init__('inc mode', id, [Port(1, ['flow']), Port(-1, ['flow'])], 'flow')
        
    def get_val(self):
        return 'self.mode += 1\n'
        
class ModeComp(Node):
    def __init__(self, id):
        super().__init__('mode is eq', id, [Port(1, ['num']), Port(-1, ['bool'])], 'op')
        
    def get_val(self):
        return '(self.mode == {})'
  
all_nodes = [Player, Players, Opponents, StealOpp, Num, String, Bool, PlayerList, CardList, Range, AddTo, Length,
             And, Or, Not, Equal, GreaterThan, LessThan, If, Elif, Else, For, Break, Continue, Gain, Lose, Steal,
             GetPlayed, Flip, Roll, Select, PostSelect, ReturnList, HasName, DrawItem, DrawTreasure, HasTag, TagFilter, 
             CombineList, Multiply, CheckFirst, CheckLast, HasLandscape, HasSpell, HasItem, MaxScore, MinScore, IsEvent, 
             IndexSelf, TagExists, SetCard, GetCard, SetPlayer, GetPlayer, GetMode, IncMode, ModeComp]
             

  
class NodePane:
    def __init__(self):
        self.rect = pg.Rect(0, 0, 300, 300)
        self.target = self.rect.copy()
        self.tab = pg.Rect(0, 0, 300, 30)
        
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill((255, 0, 0))
        
        self.nodes = {}
        self.set_image()
        
    def set_image(self):
        x = 5
        y = 5
        
        for i in all_nodes:
            
            node = i(0)
            self.nodes[node.name] = [i, node.rect.copy()]
            
            self.image.blit(node.image, (x, y))
            
            x += node.rect.width + 5
            
            if x > self.rect.width:
                
                x = 5
                y += node.rect.height + 5

    def set_pos(self):
        self.tab.midbottom = self.rect.midtop
        self.target.midbottom = self.rect.midtop
        
    def adjust_pos(self, dy):
        if dy:
            
            self.tab = self.tab.move(0, dy)
            
            for n in self.nodes:
                
                self.nodes[n][1] = self.nodes[n][1].move(0, dy)
        
    def open(self):
        y1 = self.rect.y
        
        self.rect.y -= 30
        
        if self.rect.y < self.target.y:
            
            self.rect.y = self.target.y
            
        dy = self.rect.y - y1
        self.adjust_pos(dy)
        
    def close(self):
        y1 = self.rect.y
        
        self.rect.y += 30
        
        if self.rect.y > self.target.bottom:
            
            self.rect.y = self.target.bottom
            
        dy = self.rect.y - y1
        self.adjust_pos(dy)
        
    def update(self, mouse):
        if mouse.colliderect(self.rect) or mouse.colliderect(self.tab):
            
            self.open()
            
        else:
            
            self.close()

class NodeManager:
    def __init__(self, win):
        self.screen = win
        self.frame = pg.Surface((width, height)).convert()
        
        self.clock = pg.time.Clock()
        
        self.pane = NodePane()
        self.pane.rect.midtop = (width // 2, height)
        self.pane.set_pos()
        
        self.running = True

        self.mouse = pg.Rect(0, 0, 1, 1)
        self.last_pos = (0, 0)
        
        self.group_rect = pg.Rect(0, 0, 0, 0)
        self.anchor = None
        self.group_nodes = []
        self.mbd = False
        
        self.field = None
        self.backspace = False
        self.slider = None
        
        self.nid = 1

        self.nodes = [Start(0)]

        self.active_node = None
        self.active_port = None
        self.active_line = None
        self.line_color = (0, 0, 0)
        self.line_remover = None
        self.held_node = None
        self.edit_node = None
        self.field = None
        
        self.btns = []
        self.text = []
        self.panes = []
        self.graphics = []
        self.sliders = []
        self.dropdowns = []

        self.set_screen()

    def set_screen(self):
        dd = Dropdown(list(node_dict.keys()))
        dd.rect.topleft = (20, 20)
        dd.adjust_pos()
        self.dropdowns.append(dd)
        
    def run(self):
        while self.running:
            
            self.clock.tick(fps)
            
            self.events()
            self.update()
            self.draw()
            
            self.last_pos = self.mouse.topleft
            
    def events(self):
        self.mouse.center = pg.mouse.get_pos()
        
        outline_buttons(self.mouse, self.btns)

        for e in pg.event.get():
            
            if e.type == pg.QUIT:
                
                self.running = False
            
            elif e.type == pg.KEYDOWN:
                
                if e.key == pg.K_ESCAPE:
                    
                    self.running = False
                    
                if e.key == pg.K_DELETE:
                    
                    self.delete_nodes(self.group_nodes.copy())

                if self.field is not None and e.key == pg.K_BACKSPACE:
                
                    self.backspace = True
                    
                elif self.field is not None and e.key == pg.K_RETURN:

                    self.close_field()
                    
                elif self.field is not None and hasattr(e, 'unicode'):
                    
                    char = e.unicode
                    
                    if (char and char in chars) or char.isspace():
                        
                        self.field.send_keys(char)
                    
            elif e.type == pg.KEYUP:
                
                if e.key == pg.K_BACKSPACE:
                    
                    self.backspace = False
                
            elif e.type == pg.MOUSEBUTTONDOWN:
                
                if self.field is not None:
                    
                    self.close_field()
            
                self.click(1, e.button)
                
                if e.button == 1:

                    self.collide_buttons()
                    self.collide_dropdowns()
                    
                    self.mbd = True
                    
                elif e.button == 3:
                    
                    self.edit_nodes()
                    
                elif e.button in (4, 5):
                    
                    self.collide_dropdowns(e.button)
                    
            elif e.type == pg.MOUSEBUTTONUP:
                
                self.click(0, e.button)
                
                if e.button == 1:
                    
                    for n in self.nodes:
                        
                        if self.group_rect.colliderect(n.rect):
                            
                            self.group_nodes.append(n)
                            
                    if self.edit_node is not None:
                        
                        self.close_field()

                    
                    self.slider = None
                    self.active_line = None
                    self.held_node = None
                    self.active_node = None
                    self.active_port = None
                    self.group_rect.size = (0, 0)
                    
                    self.mbd = False
                    
    def edit_nodes(self):
        for n in self.nodes:
            
            if self.mouse.colliderect(n.rect):
                
                if n.type == 'glob':
                    
                    input = n.get_input()
                    
                    if input is not None:
                        
                        self.field = input
                        self.field.rect.midbottom = n.rect.midtop
                        self.edit_node = n
                    
                    break
                    
    def close_field(self):
        self.edit_node.update_text(self.field)
        
        self.edit_node = None
        self.field = None
                    
    def click(self, mode, button):
        if button == 1:
        
            for n in self.nodes[::-1]:
                
                if mode == 1:

                    if n.can_hold(self.mouse):
                        
                        if n in self.group_nodes:
                            
                            self.held_node = -1
                            
                        else:
                        
                            self.held_node = n
                        
                        break

                    an = n.hit_mouse(self.mouse, self.active_node)
        
                    if an is not None:
                        
                        self.active_node = an
                        self.active_line = an.open_port.rect.center
                        self.line_color = an.open_port.color
                        
                elif mode == 0:

                    if self.active_node is not None:
                        
                        sn = n.accept_connection(self.mouse, self.active_node)
                        
                        if sn:
                        
                            self.spawn_nodes(sn) 
                        
            else:
                
                if mode == 1:
                    
                    if self.active_line is None:
                    
                        self.anchor = self.mouse.topleft
                        
                    self.group_nodes.clear()
                    
            if mode == 0:
                
                self.anchor = None
                
        elif button == 3:
            
            if mode == 1:
            
                if self.held_node is None and self.anchor is None and self.active_line is None:
                    
                    self.line_remover = self.mouse.topleft
                    
            elif mode == 0:
            
                x00, y00 = self.mouse.center
                x01, y01 = self.line_remover
                
                dx0 = x01 - x00
                dy0 = y01 - y00
                
                if dx0 != 0:

                    m0 = dx0 / dy0
                    
                else:
                    
                    m0 = 999
  
                b0 = y00 - (m0 * x00)

                rx0 = set(range(min(x00, x01), max(x00, x01)))
                ry0 = set(range(min(y00, y01), max(y00, y01)))

                if self.line_remover is not None:
                    
                    for n in self.nodes:
                        
                        for p in n.ports:
                            
                            if p.connection_port:
                                
                                x10, y10 = p.rect.center
                                x11, y11 = p.connection_port.rect.center
                                
                                rx1 = set(range(min(x10, x11), max(x10, x11)))
                                ry1 = set(range(min(y10, y11), max(y10, y11)))

                                m1 = (y11 - y10) / (x11 - x10)
                                
                                if m0 != m1:
                                
                                    
                                    b1 = y10 - (m1 * x10)
                                    
                                    xi = (b1 - b0) // (m0 - m1)
                                    yi = (m0 * xi) + b0

                                    rsx = rx0 & rx1
                                    rsy = ry0 & ry1
                                    
                                    print(xi, yi)
                                    
                                    if int(xi) in rsx and int(yi) in rsy:
                                    
                                        print(True)
                                

                self.line_remover = None
            
    def collide_buttons(self):
        for b in self.btns:
                            
            if self.mouse.colliderect(b.rect):
                
                if isinstance(b, Input):
                    
                    if self.field is not None:
                        
                        field.close()
                        
                    self.field = b
                    
                    break
                    
                else:
                    
                    if b.message == 'set card image':
                        
                        self.open_image()
                        
                    break
                    
        else:
            
            if self.field is not None:
                
                self.close_field()
            
    def collide_dropdowns(self, dir=1):
        for dd in self.dropdowns:
            
            if (dd.opened and self.mouse.colliderect(dd.rect)) or self.mouse.colliderect(dd.arrow.rect):
                
                if dir == 1:
                    
                    name = dd.click(self.mouse)
                    
                    if name:
                        
                        self.add_node(name)
                    
                else:

                    dd.scroll(self.mouse, dir)
                
                break
       
    def update(self):
        dx = self.mouse.x - self.last_pos[0]
        dy = self.mouse.y - self.last_pos[1]

        if self.held_node is not None:
            
            if self.held_node == -1:
                
                for n in self.group_nodes:
                
                    n.move((dx, dy))
                    
            else:
            
                self.held_node.move((dx, dy))
            
        if self.anchor is not None:
            
            x, y = self.anchor
            w = self.mouse.x - self.anchor[0]
            h = self.mouse.y - self.anchor[1]
            
            r = pg.Rect(self.anchor[0], self.anchor[1], abs(w), abs(h))
            
            if w < 0:
                
                r.right = x
                
            if h < 0:
                
                r.bottom = y
                
            self.group_rect = r
            
        if self.field is not None:
            
            if self.backspace:
                
                self.field.send_keys()
            
            self.field.update()
            
        self.pane.update(self.mouse)

    def draw(self):
        self.frame.fill((0, 0, 0))

        if self.anchor is not None:
        
            points = (self.group_rect.topleft, self.group_rect.bottomleft, self.group_rect.bottomright, self.group_rect.topright)
            pg.draw.lines(self.frame, (255, 0, 0), True, points, 3)
        
        for dd in self.dropdowns:
            
            dd.draw(self.frame)

        for n in self.nodes:
            
            if n in self.group_nodes:
                
                self.frame.blit(apply_outline(n.image, (255, 0, 0), 3), n.rect)
                
            else:
            
                self.frame.blit(n.image, n.rect)

            for p in n.ports:
                
                if p.connection_port is not None:
                    
                    pg.draw.line(self.frame, p.color, p.rect.center, p.connection_port.rect.center, 3)
            
        if self.active_line is not None:

            pg.draw.line(self.frame, self.line_color, self.active_line, self.mouse.topleft, 10)
            
        if self.line_remover is not None:
            
            pg.draw.line(self.frame, (0, 0, 255), self.line_remover, self.mouse.topleft, 10)
            
        if self.field is not None:

            self.frame.blit(self.field.get_image(), self.field.rect)
            
        self.frame.blit(self.pane.image, self.pane.rect)
            
        self.screen.blit(self.frame, (0, 0))

        pg.display.flip()
        
    def add_node(self, name):
        init = node_dict[name]
        node = init(self.nid)
        self.nid += 1
        self.nodes.append(node)
        
    def spawn_nodes(self, nodes):
        for nn in nodes:
        
            self.nodes.append(nn)
        
        #if nn is not None:
        #
        #    self.spawn_node(node1, nn)

    def get_nodes(self):
        return [node.node for node in self.nodes]
        
    def get_start_node(self):
        return self.nodes[0]
        
    def delete_nodes(self, nodes, force=False):
        for n in nodes:
            
            if n.parents and not force:
                
                continue
                
            elif n.children:

                self.delete_nodes(n.children, force=True)
        
            for o in self.nodes:
                
                for p in o.ports:
                    
                    if p.connection is n:
  
                        o.clear_port(p.port)
                        
            if n in self.nodes:
                            
                self.nodes.remove(n)

nodes = {
            
            'multiply': Multiply,
            'post select': PostSelect,
            'list combine': CombineList,
            'tag filter': TagFilter,
            'new selection': Select,
            'draw treasure': DrawTreasure,
            'steal': Steal,
            'lose': Lose,
            'has name': HasName,
            'has tag': HasTag,
            'roll': Roll,
            'flip': Flip,
            'getplayed': GetPlayed,
            'range': Range,
            'player': Player,
            'num': Num,
            'bool': Bool,
            'string': String,
            'player list': PlayerList,
            'card list': CardList,
            'length': Length,
            'and': And,
            'or': Or,
            'not': Not,
            'equal': Equal,
            'greater': GreaterThan,
            'less': LessThan,
            'if': If,
            'elif': Elif,
            'else': Else,
            'gain': Gain,
            'for': For,
            'end loop': Break,
            'continue loop': Continue,
            'players': Players,
            'opponents': Opponents,
            'add to': AddTo

        }
        
if __name__ == '__main__':
    
    pg.init()

    win = pg.display.set_mode((width, height))
    pg.display.set_caption('card game')
    
    node_dict = {n(0).name: n for n in all_nodes}
            
    n = NodeManager(win)
    n.run()
    
    sn = n.get_start_node()
    NodeParser(sn)

    pg.quit()
    
    
    
    