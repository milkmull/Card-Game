import socket
import json

class InvalidIP(Exception):
    pass

class Network:
    def __init__(self, server=None):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #type of connection, how server string is delivered
        
        self.server = server if server is not None else socket.gethostbyname(socket.gethostname()) #local ip address, must be the same as server
        self.port = 5555
        
        print(self.server)
        
        self.addr = (self.server, self.port)
        
        print(self.server, 'n2')
        
        self.pid = self.connect() #sets initial return string recieved from server
        
    def get_pid(self):
        return self.pid
        
    def connect(self):
        self.client.settimeout(3)

        try:

            self.client.connect(self.addr) #connects to server, sends address
            
        except socket.gaierror:
        
            raise InvalidIP
        
        return self.client.recv(4096).decode() #loads byte data
            
    def send(self, data):
        try:
            
            self.client.send(str.encode(data)) #dumps object into byte data and sends info
            
            return json.loads(self.client.recv(4096)) #recieves info from client
            
        except socket.error as e:
            
            print(e, 'n')
            
            return
            
    def close(self):
        self.send('disconnect')