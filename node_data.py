import allnodes

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
        group_data['pos'] = g.rect.center
        group_data['nodes'] = [n.id for n in g.nodes]
        group_data['rel_node_pos'] = g.get_rel_node_pos()
        save_data['groups'][str(g.id)] = group_data
        
    return save_data
    
def unpack(data):
    nd = Node_Data()
    return nd.unpack(data)

class Node_Data:
    def __init__(self):
        self.id = 0
        
    def get_new_id(self):
        id = self.id
        self.id += 1
        return id

    def get_node(self, name, val=None, pos=None, nodes=None):
        id = self.get_new_id()
        
        if nodes is None:
            nodes = []
            
        if name == 'GroupNode':
            n = getattr(allnodes, name)(id, nodes)
        elif val is not None:
            n = getattr(allnodes, name)(id, val=str(val))
        else:
            n = getattr(allnodes, name)(id)

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
                    print(n0.name)
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
                                allnodes.Port.new_connection(p0, p1, force=True)
                            else:
                                missed = True
                        
            if not missed:
                break

        for id, d in data['groups'].items():
            id = int(id)
            group_nodes = [nodes[id_map[nid]] for nid in d['nodes']]
            pos = d['pos']
            n = self.get_node('GroupNode', nodes=group_nodes, pos=pos)
            n.rel_node_pos = {nodes[id_map[int(nid)]]: pos for nid, pos in d['rel_node_pos'].items()}
            new_id = n.id
            id_map[id] = new_id
            nodes[new_id] = n
            
        nodes = list(nodes.values())
        for n in nodes:
            n.prune_extra_ports()
            n.set_stuck(False)

        return nodes