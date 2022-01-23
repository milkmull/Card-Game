import socket
import json
import subprocess
from threading import Thread
import save

def init():
    globals()['SAVE'] = save.get_save()

confirmation_code = 'thisisthecardgameserver'

class InvalidIP(Exception):
    pass
    
class NoGamesFound(Exception):
    pass
 
def find_connections():
    out = subprocess.check_output(['arp', '-a']).decode().split()
    ips = [s for s in out if s.startswith(('10.166', '192.168')) and not s.endswith(('.1', '.255'))]
    return ips

class Network:
    def __init__(self, server, port):
        self.port = port
        self.client = self.init_client(server)
        self.client.settimeout(3)
        self.addr = (self.server, self.port)

        self.reply_queue = []
        
        self.send_player_info()

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
            
            sock.sendall(str.encode(confirmation_code))
            code = sock.recv(4096).decode()
            
            if code == confirmation_code:
                res = True
                
        except socket.error:
            pass
            
        finally: 
            connections[server] = (sock, res)
  
    def reset(self):
        self.reply_queue.clear()

    def send_player_info(self):
        player_info = SAVE.get_data('cards')[0]
        player_info['name'] = SAVE.get_data('username')
        with open(player_info['image'], 'rb') as f:
            image = f.read()
        player_info['len'] = len(image)
        
        self.client.sendall(bytes(json.dumps(player_info), encoding='utf-8'))
        self.client.recv(4096)
        
        while image:
            data = image[:4096]
            self.client.sendall(data)
            reply = self.client.recv(4096)
            
            image = image[4096:]
            
        while reply != b'done':
            reply = self.client.recv(4096)

    def recieve_player_info(self, pid):
        info = self.send(f'getinfo{pid}')
        length = info['len']

        image = b''

        self.client.sendall(b'next')
        
        while len(image) < length:
            reply = self.client.recv(4096)
            image += reply

        while True:
            try:
                with open(info['image'], 'wb') as f:
                    f.write(image)
                break
            except OSError as e:
                errno = e.args[0]
                if errno == 13:
                    continue
                else:
                    raise e

        return info

    def send(self, data, return_val=False):
        try: 
            self.client.sendall(str.encode(data))
            reply = self.client.recv(4096)
            print('reply', reply)
            reply = json.loads(reply)

            if return_val:
                self.reply_queue.append((data, reply))
                
            return reply
            
        except socket.error as e:
            return ''

    def threaded_send(self, data, return_val):
        reply = 0
        
        if len(self.reply_queue) < 10:

            t = Thread(target=self.send, args=(data,), kwargs={'return_val': return_val})
            t.start()

        for info in self.reply_queue.copy():
            d, r = info
            if d == data:
                reply = r
                self.reply_queue.remove(info)
                break

        return reply
        
            
    def close(self):
        self.send('disconnect')
        self.client.close()
