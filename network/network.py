import socket
import subprocess
import re
import threading

from data.save import SAVE, CONFIRMATION_CODE
from .net_base import Network_Base
import exceptions

def find_connections():
    out = subprocess.check_output(['arp', '-a']).decode()
    ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
    return ips

class Network(Network_Base):
    def __init__(self, server, port):
        super().__init__(server, port)
        self.sock.settimeout(5)
        self.send_player_info()
        self.connected = True
        
    def get_sock(self, timeout=3):
        connections = {}
        sock = None
        found_game = False
        
        if self.server:
            self.verify_connection(self.server, connections) 
        else:
            threads = []
            for server in find_connections()[::-1]:
                t = threading.Thread(target=self.verify_connection, args=(server, connections))
                t.start()
                threads.append(t)
            while any({t.is_alive() for t in threads}):
                continue
       
        for server, (s, res) in connections.items():
            if res and not found_game: 
                self.server = server
                sock = s
                found_game = True  
            else:
                s.close()
                
        if sock is None:
            raise exceptions.NoGamesFound
                
        return sock
        
    def verify_connection(self, server, connections):
        sock = super().get_sock(timeout=1)
        res = False
        try:
            sock.connect((server, self.port))
            sock.sendall(bytes(CONFIRMATION_CODE, encoding='utf-8'))
            code = sock.recv(4096).decode()
            res = code == CONFIRMATION_CODE
        except socket.error:
            pass
        finally: 
            connections[server] = (sock, res)
          
    def send_player_info(self):
        info = SAVE.get_data('cards')[0]
        info['name'] = SAVE.get_data('username')
        with open(info['image'], 'rb') as f:
            image = f.read()
        info['raw_image'] = self.b64encode(image)

        data = bytes(self.dump_json(info), encoding='utf-8')
        try:
            self.send_large_raw(data)
        except socket.error:
            self.close()
        except Exception as e:
            self.raise_exception(e)

    def recieve_player_info(self, pid):
        try:
            self.send(f'getinfo{pid}')
            info = self.load_json(self.recv_large_raw())
        except socket.error:
            self.close()
            return
        except Exception as e:
            self.raise_exception(e)

        image = self.b64decode(info['raw_image'])

        try:
            with open(info['image'], 'wb') as f:
                f.write(image)
        except Exception as e:
            self.raise_exception(e)

        return info
        
    def send_and_recv(self, data):
        reply = None
        if self.connected:
            try:
                self.send(data)
                reply = self.load_json(self.recv())
            except socket.error:
                self.close()
        return reply

    def close(self):
        super().close()
        
        info = self.pop_exception()
        if info:
            e, tb = info
            print(f'client closed with error: {e}')
            print(tb)
        else:
            print('client closed')
            
    def get_exception(self, e):
        if e is OSError:
            errno = e.args[0]
            if errno == 13:
                return
        return e
