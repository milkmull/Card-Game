import socket
import json
import subprocess
from threading import Thread

confirmation_code = 'thisisthecardgameserver'

class InvalidIP(Exception):
    pass
    
class NoGamesFound(Exception):
    pass
 
def find_connections():
    out = subprocess.check_output(['arp', '-a']).decode().split()
    ips = [s for s in out if s.startswith('192.168') and not s.endswith(('.1', '.255'))]
    
    return ips

class Network:
    def __init__(self, server, port):
        self.port = port
        self.client = self.init_client(server)
        self.addr = (self.server, self.port)
        
        self.pid = self.send('pid')
        
    def set_server(self, server):
        self.server = server
        
    def init_client(self, server):
        connections = {}
        client = None
        found_game = False
        
        if server:
            
            self.verify_connection(server, connections)
            
        else:
            
            threads = []
            
            for server in find_connections()[::-1]:

                t = Thread(target=self.verify_connection, args=(server, connections))
                t.start()
                threads.append(t)
                
            while any(t.is_alive() for t in threads):
                
                continue
       
        for server in connections:
            
            sock, res = connections[server]

            if res and not found_game:
                
                self.set_server(server)
                client = sock
                found_game = True
                
            else:
                
                sock.close()
                
        if client is None:
            
            raise NoGamesFound
                
        return client
        
    def verify_connection(self, server, connections):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        res = False
        
        try:
        
            sock.connect((server, self.port))
            code = sock.recv(4096).decode()
            
            if code == confirmation_code:

                res = True
                
        except socket.error:
            
            pass
            
        connections[server] = (sock, res)

    def get_pid(self):
        return self.pid
            
    def send(self, data):
        try:
            
            self.client.send(str.encode(data)) #dumps object into byte data and sends info
            
            return json.loads(self.client.recv(4096)) #recieves info from client
            
        except socket.error as e:
            
            print(e, 'n')
            
            return
            
    def close(self):
        self.send('disconnect')
        self.client.close()
        
    def close_error(self, error):
        self.close()
        
        raise error