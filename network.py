import socket
import json
import subprocess
import re
import threading

import save
import exceptions

def init():
    globals()['SAVE'] = save.get_save()

confirmation_code = 'thisisthecardgameserver'
 
def find_connections():
    out = subprocess.check_output(['arp', '-a']).decode()
    ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
    return ips

class Network:
    def __init__(self, server, port):
        self.port = port
        self.client = self.init_client(server)
        self.client.settimeout(3)
        self.addr = (self.server, self.port)
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
                t = threading.Thread(target=self.verify_connection, args=(server, connections))
                t.start()
                threads.append(t)
                
            while any(t.is_alive() for t in threads):
                continue
       
        for server, (sock, res) in connections.items():

            if res and not found_game: 
                self.set_server(server)
                client = sock
                found_game = True  
            else:
                sock.close()
                
        if client is None:
            raise exceptions.NoGamesFound
                
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

    def send_player_info(self):
        player_info = SAVE.get_data('cards')[0]
        player_info['name'] = SAVE.get_data('username')
        with open(player_info['image'], 'rb') as f:
            image = f.read()
        player_info['len'] = len(image)
        chunk_size = 4096
        
        self.client.sendall(bytes(json.dumps(player_info), encoding='utf-8'))
        self.client.recv(chunk_size)
        
        while image:
            data = image[:chunk_size]
            self.client.sendall(data)
            reply = self.client.recv(chunk_size)
            
            image = image[chunk_size:]
            
        while b'done' not in reply:
            reply = self.client.recv(chunk_size)

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
                if errno != 13:
                    raise e

        return info

    def send(self, data):
        try: 
            self.client.sendall(str.encode(data))
            reply = json.loads(self.client.recv(4096)) 
            return reply
            
        except socket.error as e:
            return

    def close(self):
        self.send('disconnect')
        self.client.close()
