import socket
import json

class InvalidIP(Exception):
    pass
    
class PortInUse(Exception):
    pass

class Network:
    def __init__(self, server, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server = server if server else socket.gethostbyname(socket.gethostname())
        self.port = port

        self.addr = (self.server, self.port)
        
        self.pid = int(self.connect())
        
    def get_pid(self):
        return self.pid
        
    def connect(self):
        self.client.settimeout(3)

        try:

            self.client.connect(self.addr) #connects to server, sends address
            
        except socket.gaierror:
        
            raise InvalidIP
        
        pid = self.client.recv(4096).decode() #loads byte data
        
        try:
            
            pid = int(pid)
            
        except ValueError:
            
            self.client.close()
            
            raise PortInUse
            
        return pid
            
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