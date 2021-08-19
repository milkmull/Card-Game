
    
def get_tabs(tabs):
    text = ''
    
    for t in range(tabs):
        
        text += '\t'
        
    return text

def start_node_parse(node, tabs=2):
    print(parse_nodes(node))
    #with open('newcard.txt', 'w') as f:
    #    
    #    text = parse_nodes(node)
    #    
    #    print(text)
    #    
    #    f.write(text)
    
class NodeParser:
    def __init__(self, start_node):
        self.node = start_node
        
        self.tabs = 2
        
        self.header = "class Test(Card):\n\tdef __init__(self, game, uid):\n\t\tsuper().__init__(game, uid, 'test', [])\n\n"
        self.dec_line = ''

        self.funcs = {}
        
        self.parse_nodes(self.node, -1)
        
        print(self.funcs)
        
        self.write_card()
        
    def new_func(self, func):
        self.funcs[func] = {'title': '', 'dec': '', 'body': ''}
        
    def parse_nodes(self, node, func, tabs=1, back=True):
        print(node, func)
        text = ''

        if node is None:
            
            return '{}'
            
        if node.type == 'flow':
            
            text += get_tabs(tabs)
            
        if node.type == 'loc':
            
            dec = node.get_dec()
            dec_line = self.funcs[func]['dec']
            
            if dec not in dec_line:
                
                self.funcs[func]['dec'] += '\t\t' + dec + '\n'
                
        if node.type == 'func':

            if node.name not in self.funcs:
            
                self.new_func(node.name)

            self.funcs[node.name]['title'] = '\t' + node.get_val()
            body = ''
            
            for p in node.get_output_ports():
                
                if p.connection is not None and 'flow' in p.types:
                
                    body += self.parse_nodes(p.connection, node.name, 2)
                    
            if not body.strip():
                
                body = node.get_default_body()
                
            self.funcs[node.name]['body'] += body
                    
            return ''
                    
        else:

            t = node.get_val()
            spots = t.count('{}')
            format_vals = []

            for p in node.get_input_ports():
                
                if 'flow' not in p.types and 'spawn' not in p.types:
                    
                    format_vals.append(self.parse_nodes(p.connection, func, tabs, back=False))
        
            if len(format_vals) == spots:
                
                t = t.format(*format_vals)
                
            if '{}' in t:
                
                t = node.get_default()
                
            text += t
                
            if back:

                for p in node.get_output_ports():
                    
                    if p.connection is not None:
                        
                        if p.connection.type == 'block' or p.connection.type == 'func' or 'block' in p.types:

                            text += self.parse_nodes(p.connection, func, tabs + 1)
                            
                for p in node.get_output_ports():
                    
                    if p.connection is not None:
                        
                        if p.connection.type == 'flow':
                            
                            text += self.parse_nodes(p.connection, func, tabs)
                            
                            break
                            
                else:
                    
                    if node.type == 'block':
                        
                        text += get_tabs(tabs) + 'pass\n'
        
        return text
        
    def write_card(self):
        with open('newcard.py', 'w') as f:
            
            f.write(self.header)
            
            for func in self.funcs.values():
                
                t = func['title']
                d = func['dec']
                b = func['body']
                
                if not b.strip():
                    
                    b = '\t\tpass\n'

                f.write(t + d + b + '\n')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

