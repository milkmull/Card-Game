import socket
import json
import urllib.request
import traceback
import base64

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
    
def get_public_ip():
    ip = None
    try:
        ip = urllib.request.urlopen('https://api.ipify.org').read().decode()
    except urllib.error.URLError:
        pass
    return ip
        
class Network_Base:
    @staticmethod
    def load_json(data):
        return json.loads(data) 
        
    @staticmethod
    def dump_json(data):
        return json.dumps(data)
        
    @staticmethod
    def b64encode(data):
        return base64.b64encode(data).decode('utf-8')
        
    @staticmethod
    def b64decode(data):
        return base64.b64decode(data)
        
    @staticmethod
    def encode(data):
        return bytes(data, encoding='utf-8')
        
    @staticmethod
    def decode(data):
        return data.decode()
        
    @staticmethod
    def get_sock(timeout=3):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        return sock
        
    def __init__(self, server, port, timeout=3):
        self.server = server
        self.port = port

        self.connections = {}
        self.connected = False
        self.listening = False
        
        self.sock = self.get_sock(timeout=timeout)
        
        self.exceptions = []
        
    @property
    def address(self):
        return (self.server, self.port)
        
    def add_exception(self, err):
        info = (err, traceback.format_exc())
        self.exceptions.append(info)
        
    def pop_exception(self):
        if self.exceptions:
            return self.exceptions.pop(-1)
            
    def get_exception(self, e):
        return e
            
    def raise_exception(self, e):
        self.close()
        e = self.get_exception(e)
        if e is not None:
            raise e
        
    def raise_last(self):
        info = self.pop_exception()
        if info:
            self.raise_exception(info[0])
        
    def close(self):
        for address, conn in self.connections.copy().items():
            self.close_connection(conn, address)
        self.sock.close()
        self.connected = False
        self.listening = False
        
    def check_close(self):
        return self.exceptions

    def start_server(self):
        self.connected = False
        try: 
            self.sock.bind(self.address)
            self.connected = True
        except Exception as e:
            self.add_exception(e)
        return self.connected
        
    def connect(self):
        self.connected = False
        try:
            self.sock.connect(self.address)
            self.connected = True
        except Exception as e:
            self.add_exception(e)
        return self.connected
            
    def add_connection(self, conn, address):
        self.connections[address] = conn
        
    def close_connection(self, conn, address):
        conn.close()
        self.connections.pop(address)
        
    def listen(self):
        self.listening = True
        self.sock.listen()
        while self.listening:
            try:
                conn, address = self.sock.accept()
                self.add_connection(conn, address)
            except socket.timeout:
                pass
            except Exception as e:
                self.raise_exception(e)
            if self.check_close():
                self.close()
                break
        self.listening = False
        
    def _send(self, conn, data):
        conn.sendall(data)
        
    def _recv(self, conn, chunk_size):
        return conn.recv(chunk_size).decode()
    
    def send(self, data, conn=None, raw=False):
        if conn is None:
            conn = self.sock
        if not raw:
            data = bytes(data, encoding='utf-8')
        conn.sendall(data)
        
    def recv(self, conn=None, raw=False, chunk_size=4096):
        if conn is None:
            conn = self.sock
        data = conn.recv(chunk_size)
        if not raw and data is not None:
            data = data.decode()
        return data
        
    def send_and_recv(self, data, conn=None, raw=False):
        if conn is None:
            conn = self.sock
        self.send(data, conn=conn, raw=raw)
        return self.recv(conn=conn, raw=raw)
        
    def send_large_raw(self, data, conn=None, chunk_size=4096):
        if conn is None:
            conn = self.sock
            
        info = {
            'length': len(data),
            'chunk_size': chunk_size
        }
        self.send(self.dump_json(info), conn=conn)
        self.recv(conn=conn, raw=True)
            
        while data:
            d = data[:chunk_size]
            self.send(d, conn=conn, raw=True)
            data = data[chunk_size:]
        
        reply = b''
        while b'done' not in reply:
            reply = self.recv(conn=conn, raw=True)
        
    def recv_large_raw(self, conn=None):
        if conn is None:
            conn = self.sock
            
        info = json.loads(self.recv(conn=conn))
        length = info['length']
        chunk_size = info['chunk_size']
        data = b''
        
        self.send(b'next', conn=conn, raw=True)
        
        while len(data) < length:
            d = self.recv(conn=conn, raw=True)
            data += d
            self.send(b'next', conn=conn, raw=True)

        self.send(b'done', conn=conn, raw=True)
        
        return data
