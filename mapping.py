
def find_visible_chunk(n, nodes):
    nodes.append(n)
    
    for ip in n.get_input_ports():
        if ip.connection:
            connected_node = ip.connection_port.get_visible_node()
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
    
    for op in n.get_output_ports():
        if op.connection:
            connected_node = op.connection_port.get_visible_node()
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
                
    return nodes
    
def find_chunk(n, nodes):
    nodes.append(n)
    
    for ip in n.get_input_ports():
        if ip.connection:
            connected_node = ip.connection_port.node
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
    
    for op in n.get_output_ports():
        if op.connection:
            connected_node = op.connection_port.node
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
                
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
                            map_ports(op.node, ports, skip_ip=skip_ip, skip_op=skip_op, all_ports=all_ports, out_type=out_type, in_type=in_type)
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
                            map_ports(ip.node, ports, skip_ip=skip_ip, skip_op=skip_op, all_ports=all_ports, out_type=out_type, in_type=in_type) 
                    elif all_ports:
                        ports.append(op)
                
    return ports

def trace_flow(n, nodes, dir):
    nodes.append(n)
    
    if dir == -1:
        for ip in n.get_input_ports():
            if ip.connection:
                if 'flow' in ip.types and ip.connection not in nodes:
                    trace_flow(ip.connection, nodes, dir=dir)
                    
    elif dir == 1:
        for op in n.get_output_ports():
            if op.connection:
                if 'flow' in op.types and op.connection not in nodes:
                    trace_flow(op.connection, nodes, dir=dir)
                    
    return nodes

def find_parent_func(n):
    nodes = trace_flow(n, [], -1)
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
                map_flow(connected_node, nodes, columns, column=column - 1)
                
    opp = n.get_output_ports()
    opp.sort(key=lambda p: p.get_true_port(), reverse=True)
    
    for op in opp[::-1]:
        if 'flow' in op.types and op.connection:
            connected_node = op.connection_port.get_visible_node()
            if connected_node in nodes:
                map_flow(connected_node, nodes, columns, column=column + 1)
            
    for op in opp:
        if 'flow' not in op.types and op.connection:
            connected_node = op.connection_port.get_visible_node()
            if connected_node in nodes:
                in_flow = connected_node.get_in_flow()
                if in_flow:
                    if in_flow.connection:
                        if in_flow.connection in nodes:
                            continue
                map_flow(connected_node, nodes, columns, column=column + 1)
            
    return columns

def check_bad_connection(n0, n1):   
    local_funcs = set()
    scope_output = set()
    loop_output = set()
    
    nodes = find_chunk(n0, [])
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
                ports = map_ports(op.connection, check_ports.copy(), all_ports=True, in_type='flow')
                if out_port in ports:
                    scope_output.add(op)

    opp = n0.get_output_ports()     
    for op in opp:
        if op.connection:
            ports = map_ports(op.connection, [], skip_ip=True)
            if any({op in ports for op in opp}):
                loop_output.add(op)
            
    return (local_funcs, scope_output, loop_output)
