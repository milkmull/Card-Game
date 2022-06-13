import mapping

class Node_Parser:  
    def __init__(self, card, nodes):
        self.card = card
        self.nodes = nodes
        self.start_node = self.find_start()
        self.missing = self.check_missing_nodes()

        self.header = (
            f"\nclass {self.card.classname}(card_base.Card):\n"
                f"\tname = '{self.card.name}'\n"
                f"\ttype = '{self.card.type}'\n"
                f"\tweight = {self.card.weight}\n"
                f"\ttags = {self.card.tags}\n"
        )
        self.dec_line = ''
        self.funcs = {}
        self.text = self.run()
        
    def find_start(self):
        for n in self.nodes:
            if n.name == 'Start':
                return n
        
    def get_text(self):
        return self.text
        
    def get_lines(self):
        return self.text.splitlines()
        
    def new_func(self, node):
        self.funcs[node.name] = {'header': '\t' + node.get_text(), 'start': '', 'dec': '', 'body': '', 'end': ''}
        
    def find_funcs(self):
        return [n for n in self.nodes if n.type == 'func']

    def check_missing_nodes(self):
        missing = set()
        for n in self.nodes:
            for name in n.get_required():
                if not any({o.name == name for o in self.nodes}):
                    missing.add(name)
        return list(missing)
        
    def run(self):
        if not self.start_node or self.missing:
            return ''
                
        for n in self.find_funcs():
            self.parse_nodes(n, func=None)
        
        out = self.header

        for func, info in self.funcs.items():
            header = info['header']
            start = info['start']
            dec = info['dec']
            body = info['body']
            end = info['end']
            if not start + body + end:
                body = '\t\tpass\n'
            out += header + start + dec + body + end
        
        out = out.replace('\t', '    ')
        return out
        
    def find_locals(self, node):
        dec_line = ''
        ports = set(mapping.map_ports(node, []))
        for p in ports:
            n = p.node
            line = n.get_dec()
            if line:
                v = line.split()[0]
                if line and v not in dec_line:
                    dec_line += '\t\t' + n.get_dec()
                
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
                for line in out_text.splitlines():
                    text += (tabs * '\t') + line + '\n'
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
