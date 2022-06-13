import pygame as pg

from ui.element.standard import Textbox
from ui.element.extended import Logged_Input as Input

from node_base import Node, Port, mapping

class Start(Node):
    cat = 'func'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['flow'], desc='flow')], type='func')
        
    def get_start(self):
        return '\t\tself.reset()\n'
        
    def get_text(self):
        return '\n\tdef start(self, player):\n'
        
class End(Node):
    cat = 'func'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['flow'], desc='flow')], type='func')
        
    def get_text(self):
        return '\n\tdef end(self, player):\n'
   
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
        super().__init__(manager, id, [Port(1, ['num'], desc='if true'), Port(2, ['num'], desc='if false'), Port(3, Port.get_comparison_types()), Port(-1, ['num'])])
        
    def tf(self):
        ip1 = self.get_port(1)
        ip2 = self.get_port(2)
        op = self.get_port(-1)
        
        if 'num' in ip1.types:
            ip1.set_types(['string'])
            ip2.set_types(['string'])
            op.set_types(['string'])
        elif 'string' in ip1.types:
            ip1.set_types(['player'])
            ip2.set_types(['player'])
            op.set_types(['player'])
        elif 'player' in ip1.types:
            ip1.set_types(['card'])
            ip2.set_types(['card'])
            op.set_types(['card'])
        elif 'card' in ip1.types:
            ip1.set_types(['num'])
            ip2.set_types(['num'])
            op.set_types(['num'])
        
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
        i = Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=1, fitted=True, double_click=True)
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
        i = Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=3, fitted=True, double_click=True)
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
        i = Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=50, fitted=True, double_click=True)
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
        i = Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=300, fitted=True, allignment='l', lines=1, scroll=False, double_click=True)
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
        i = Input(size, message=self.val, color=(0, 0, 0), full_check=full_check, length=300, fitted=True, allignment='l', lines=20, scroll=False, double_click=True)
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
      
class Scope(Node):
    size = (300, 50)
    cat = 'flow'
    subcat = 'other'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['flow'] + Port.get_comparison_types())])
        
    def get_objects(self):
        tb = Textbox('-', bgcolor=(0, 0, 0), fitted=True)
        tb.fit_text(self.rect.inflate(-15, -15))
        tb.rect.center = self.rect.center
        offset = (tb.rect.x - self.rect.x, tb.rect.y - self.rect.y)
        self.add_child(tb, set_parent=True, offset=offset)
        self.objects_dict['textbox'] = tb
        return [tb]
        
    def update(self):
        super().update()
        
        ip = self.get_port(1)
        
        if ip.connection:
            if 'flow' in ip.connection_port.types:
                text = ip.connection.get_text().strip('\n\t ')
            else:
                text = ip.connection.get_output(ip.connection_port.port)
            if self.objects_dict['textbox'].get_message() != text:
                self.objects_dict['textbox'].set_message(text)
        else:
            if self.objects_dict['textbox'].get_message() != '-':
                self.objects_dict['textbox'].set_message('-')

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
        super().__init__(manager, id, [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list'), Port(2, ['flow']), Port(-1, ['num'], desc='list value'), Port(-2, ['split', 'flow']), Port(-3, ['flow'])])  

    def update(self):
        super().update()
        
        ip = self.get_port(1)
        op = self.get_port(-1)

        if ip.connection:
            t = ip.connection_port.get_contains()
            if t not in op.types:
                op.update_types([t])
        elif 'num' not in op.types:
            op.update_types(['num'])

    def get_loop_var(self):
        op = self.get_port(-1)
        contains = op.types[0]
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
        text = 'for {0} in {1}:\n'.format(*input)   
        return text
        
    def get_output(self, p):
        return self.get_loop_var()
        
class Zipped_For(Node):
    cat = 'flow'
    subcat = 'loop'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['cs', 'ps', 'ns', 'bs'], desc='list 1'), Port(2, ['cs', 'ps', 'ns', 'bs'], desc='list 2'), Port(3, ['flow']), Port(-1, ['num'], desc='value 1'), Port(-2, ['num'], desc='value 2'), Port(-3, ['split', 'flow']), Port(-4, ['flow'])])  

    def update(self):
        super().update()
        
        for p in (1, 2):
        
            ip = self.get_port(p)
            op = self.get_port(-p)
            
            if ip.connection:
                t = ip.connection_port.get_contains()
                if t not in op.types:
                    op.update_types([t])
            elif 'num' not in op.types:
                op.update_types(['num'])

    def get_loop_var(self, p):   
        op = self.get_port(p)
        contains = op.types[0]
        if contains == 'player':
            return f'p{self.id}{abs(p)}'  
        elif contains == 'num':  
            return f'i{self.id}{abs(p)}'
        elif contains == 'card':
            return f'c{self.id}{abs(p)}'
        elif contains == 'string':
            return f's{self.id}{abs(p)}'
        elif contains == 'bool':
            return f'b{self.id}{abs(p)}'
        
    def get_default(self, p):
        return 'range(1)'
        
    def get_text(self):
        vars = [self.get_loop_var(-1), self.get_loop_var(-2)]
        input = vars + self.get_input()
        text = 'for {0}, {1} in zip({2}.copy(), {3}.copy()):\n'.format(*input)   
        return text
        
    def get_output(self, p):
        return self.get_loop_var(p)
        
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
        return 'self.get_players()'
        
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
        return 'self.get_opponents(player)'
        
class Opponents_With_Points(Node):
    cat = 'player'
    subcat = 'lists'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['ps'], desc='player list')])
        
    def get_output(self, p):
        return 'self.get_opponents_with_points(player)'
      
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
        
class Is_Type(Node):
    cat = 'string'
    subcat = 'card attributes'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='type'), Port(2, ['card'], desc='card'), Port(-1, ['bool'], desc='card is type')])   
        
    def get_default(self, p):
        if p == 1:
            return "'play'"
        elif p == 2:
            return 'self'
        
    def get_output(self, p):
        text = '({1}.type == {0})'.format(*self.get_input())
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
                text = "[x for x in {2} if {0} in x.tags and x != self]"
            else:
                text = "[x for x in {2} if {0} in x.tags]"
        else:
            text = "[x for x in {2} if {0} in x.tags]"
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
            
    def get_required(self):
        return ['Flip']

class Flip(Node):
    cat = 'func'
    subcat = 'flip'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['bool'], desc='flip result'), Port(-2, ['flow'])], type='func') 
            
    def get_start(self):
        return '\t\tself.t_coin = coin\n'
            
    def get_text(self):
        return '\n\tdef flip(self, player, coin):\n'
        
    def get_output(self, p):
        if p == -1:
            return 'coin'
            
    def get_required(self):
        return ['Start_Flip']

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
            
    def get_required(self):
        return ['Roll']

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
            
    def get_required(self):
        return ['Start_Roll']
            
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
        
    def get_required(self):
        return ['Get_Selection', 'Select']
            
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
        
    def get_required(self):
        return ['Start_Select', 'Select']
        
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
            
    def get_required(self):
        return ['Start_Select', 'Get_Selection']
  
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
        
    def get_required(self):
        return ['Init_Ongoing', 'Add_To_Ongoing', 'Ongoing']
        
class Init_Ongoing(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(-1, ['flow'])], type='func') 
            
    def get_text(self):
        return '\n\tdef start_ongoing(self, player):\n'
        
    def get_required(self):
        return ['Start_Ongoing', 'Add_To_Ongoing', 'Ongoing']
        
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
        
    def get_required(self):
        return ['Start_Ongoing', 'Init_Ongoing', 'Ongoing']
        
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
            
    def get_required(self):
        return ['Start_Ongoing', 'Init_Ongoing', 'Add_To_Ongoing']

class Extract_Value(Node):
    cat = 'func'
    subcat = 'ongoing'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='key'), Port(2, ['log'], desc='log'), Port(-1, ['num'], desc='value')]) 
        
    def get_output(self, p):
        text = "{1}.get({0})".format(*self.get_input())
        return text
        
    def get_default(self, p):
        if p == 1:
            return '0'
        elif p == 2:
            return 'dict()'
        
    def eval_text(self, text):
        if text == 'c': #not true for draw
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
            t = self.eval_text(text)
            if t not in op.types:
                op.update_types([t])
        elif 'num' not in op.types:
            op.update_types(['num'])

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
        super().__init__(manager, id, [Port(1, ['string'], desc='type'), Port(2, ['num'], desc='number of cards'), Port(3, ['player']), Port(4, ['flow']), Port(-1, ['cs'], desc='cards'), Port(-2, ['flow'])])   
        
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
            return "player.string_to_deck('played')"
        
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
        return '{1}[{0}] if {0} < len({1}) else None'.format(*self.get_input())
        
    def get_default(self, p):
        if p == 1:
            return '-1'
        elif p == 2:
            return "player.string_to_deck('played')"
        
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
        super().__init__(manager, id, [Port(1, ['string'], desc='type'), Port(2, ['player'], desc='target'), Port(3, ['flow']), Port(-1, ['card']), Port(-2, ['flow'])])   
        
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
        elif p == 4:
            return '-1'
        else:
            return 'None'

    def get_text(self):
        return "{0}.add_card({1}, deck_string={2}, i={3})\n".format(*self.get_input())
                
class Get_Deck(Node):
    cat = 'player'
    subcat = 'card operator'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['string'], desc='deck name'), Port(2, ['player']), Port(-1, ['cs'], desc='deck')])   
        
    def get_default(self, p):
        if p == 1:
            return "'played'"
        elif p == 2:
            return 'player'
            
    def get_output(self, p):
        return '{1}.string_to_deck({0})'.format(*self.get_input())
        
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
        return "{0}.type == 'player'".format(*self.get_input())        
        
class Is_Card(Node):
    cat = 'card'
    subcat = 'boolean'
    def __init__(self, manager, id):
        super().__init__(manager, id, [Port(1, ['card', 'player']), Port(-1, ['bool'])])   
        
    def get_default(self, p):
        return 'self'

    def get_output(self):
        return "isinstance({0}, card_base.Card)".format(*self.get_input())  
        