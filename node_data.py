import node_base

def init_nodes():
    import nodes
init_nodes()

def get_node_data():
    ndb = Node_Data_Base()
    subclasses = node_base.Node.get_subclasses()
    node_data = {}
    raw_nodes = {}
    for cls in subclasses:
        name = cls.__name__
        node_data[name] = cls
        raw_nodes[name] = cls(ndb, 0)
    node_base.Node.set_raw(raw_nodes)
    return node_data
    
def get_group_data():
    ndb = Node_Data_Base()
    import save
    group_data = save.load_json('data/group_nodes.json')
    raw_groups = {name: ndb.unpack(data)[-1] for name, data in group_data.items()}
    node_base.Node.set_raw(raw_groups)
    return group_data
    
def get_cached_img(name):
    return node_base.Node.RAW_CACHE.get(name)
    
def write_node_data(nodes):
    import json
    with open('data/node_info.json', 'r') as f:
        data = json.load(f)
        
    for i, old_name in enumerate(data.copy()):
        new_name = list(nodes)[i]
        data[new_name] = data.pop(old_name)

    with open('data/node_info1.json', 'w') as f:
        json.dump(data, f, indent=4)

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
        group_data['name'] = g.get_string_val()
        group_data['pos'] = g.rect.center
        group_data['nodes'] = [n.id for n in g.nodes]
        group_data['rel_node_pos'] = g.get_rel_node_pos()
        save_data['groups'][str(g.id)] = group_data
        
    return save_data
    
def unpack(data):
    nd = Node_Data_Base()
    return nd.unpack(data)
    
class Node_Data_Base:
    NODES = None
    GROUPS = None
    @classmethod
    def init_node_data(cls):
        cls.NODES = get_node_data()
        cls.GROUPS = get_group_data()

    def __init__(self):
        self.id = 0
        
    def get_new_id(self):
        id = self.id
        self.id += 1
        return id
        
    def get_node(self, name, val=None, pos=None):
        id = self.get_new_id()
        if val is not None:
            n = Node_Data_Base.NODES[name](self, id, val=val)
        else:
            n = Node_Data_Base.NODES[name](self, id)
        
        if pos:
            n.rect.center = pos
            n.set_port_pos()
        return n
        
    def get_group_node(self, name, pos=None):
        data = Node_Data_Base.GROUPS[name]
        nodes = self.unpack(data)
        n = nodes[-1]
        if pos:
            n.rect.center = pos
            n.set_port_pos()
        return n
        
    def make_group_node(self, nodes, name='group', pos=None):
        id = self.get_new_id()
        n = node_base.GroupNode(self, id, nodes, name=name)
        if pos:
            n.rect.center = pos
            n.set_port_pos()
        return n
        
    def unpack(self, data):
        if not data:
            return {}
            
        nodes = {}
        id_map = {}

        for id, d in data['nodes'].items():
            id = int(id)
            name = d['name']
            val = d['val']
            contains = d['contains']
            pos = d['pos']
            n = self.get_node(name, val=val, pos=pos)
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
                                node_base.Port.new_connection(p0, p1, force=True)
                            else:
                                missed = True
                        
            if not missed:
                break

        for id, d in data['groups'].items():
            id = int(id)
            name = d['name']
            group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
            pos = d['pos']
            n = self.make_group_node(group_nodes, name=name, pos=pos)
            n.rel_node_pos = {nodes[id_map[int(nid)]]: pos for nid, pos in d['rel_node_pos'].items()}
            new_id = n.id
            id_map[id] = new_id
            nodes[new_id] = n
            
        nodes = list(nodes.values())
        for n in nodes:
            n.prune_extra_ports()
            n.set_stuck(False)

        return nodes
        
    def new_wire(self, p0, p1):
        node_base.Wire(p0, p1)
        
    def add_log(self, log):
        pass
        
    def set_active_node(self, n):
        pass

Node_Data_Base.init_node_data()

class Node_Data(Node_Data_Base):
    def __init__(self):
        super().__init__()
        self.active_node = None
        self.nodes = []
        self.wires = []

    def exists(self, name):
        return any({n.name == name for n in self.nodes})
        
    def add_log(self, log):
        pass
        
#wire stuff--------------------------------------------------------------------

    def new_wire(self, p0, p1):
        w = node_base.Wire(p0, p1)
        self.wires.append(w)
        
    def del_wire(self, w):
        if w in self.wires:
            self.wires.remove(w)
            
    def disconnect(self, p0, p1, d=True):
        node_base.Port.disconnect(p0, p1, d=d)
        
    def new_connection(self, p0, p1, force=True, d=True):
        node_base.Port.new_connection(p0, p1, force=force, d=d)
            
#active node stuff--------------------------------------------------------------------
        
    def get_active_node(self):
        return self.active_node
        
    def set_active_node(self, n):
        self.active_node = n
        
    def close_active_node(self):
        if self.active_node:
            self.active_node.end_connect()
            self.active_node = None
            