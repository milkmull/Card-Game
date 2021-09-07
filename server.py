import socket, json, os, time
from _thread import start_new_thread
from game import Game
import save

confirmation_code = 'thisisthecardgameserver'

class PortInUse(Exception):
    pass

def get_port():
    try:
        port = save.get_data('port')       
    except:
        port = 5555
        
    return port

class Server:
    def __init__(self):
        self.pid = 0
        
        self.connections = {}
        
        self.server = socket.gethostbyname(socket.gethostname())
        self.port = get_port()
        self.addr = (self.server, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        
        self.game = None
        self.player_info = {}
        
    def set_game(self):
        self.game = Game()
            
    def close(self):
        for pid, conn in self.connections.items():
            conn.close()
        self.sock.close()
        
        for f in os.listdir('img/temp'):
            os.remove(f'img/temp/{f}')
        
        print('server closed')
            
    def send_player_info(self, conn, pid):
        p = self.game.get_player(pid)
        info = p.get_info()
        with open(info['image'], 'rb') as f:
            image = f.read()
        info['len'] = len(image)
        
        conn.sendall(bytes(json.dumps(info), encoding='utf-8'))
        conn.recv(4096)
            
        while image:

            reply = image[:4096]
            conn.sendall(reply)
            
            image = image[4096:]

    def recieve_player_info(self, id, conn):
        info = json.loads(conn.recv(4096))
        self.player_info[id] = info
        
        length = info['len']
        image = b''
        
        conn.sendall(b'next')
        
        while len(image) < length:

            reply = conn.recv(4096)
            image += reply
            
            conn.sendall(b'next')
                
        filename = f'img/temp/{id}.png'
        with open(filename, 'wb') as f:
            f.write(image)
            
        self.player_info[id]['image'] = filename
        self.player_info[id]['id'] = id

    def threaded_client(self, conn, id):
        try:
            
            self.recieve_player_info(id, conn)
        
            connected = self.game.new_player(id, self.player_info[id])
        
            if connected:
            
                reply = ''

                while connected:

                    data = conn.recv(4096).decode()

                    if data is None:
                        break
                        
                    else:
                        
                        if data == 'pid':
                            reply = id
                        
                        if data == 'disconnect':
                            connected = False

                        elif data == 'info':
                            self.game.update_player(id)
                            self.game.main()
                            reply = self.game.get_info(id)
                            
                        elif data.startswith('name'):
                            reply = self.game.get_player(id).set_name(data[5:])
                        
                        elif data == 'start':
                            self.game.start(id)
                            reply = 1
                            
                        elif data == 'reset':
                            self.game.reset()
                            reply = 1
                            
                        elif data == 'continue':
                            status = self.game.status
                            if status == 'next round':
                                self.game.new_round()   
                            elif status == 'new game':
                                self.game.new_game()  
                            reply = 1
                            
                        elif data == 'play':
                            if self.game.status == 'playing':
                                self.game.update_player(id, 'play')  
                            reply = 1
                            
                        elif data == 'cancel':
                            if self.game.status == 'playing':
                                self.game.update_player(id, 'cancel')  
                            reply = 1
                            
                        elif data.isdigit():
                            self.game.update_player(id, f'select {data}') 
                            reply = 1
                            
                        elif data == 'flip':
                            if self.game.status == 'playing':
                                self.game.update_player(id, 'flip') 
                            reply = 1
                            
                        elif data == 'roll':
                            if self.game.status == 'playing':
                                self.game.update_player(id, 'roll')  
                            reply = 1

                        elif data == 'settings':
                            reply = self.game.get_settings()
                            
                        elif data == 'us':
                            self.game.update_settings()
                            reply = 1

                        elif data.startswith('getinfo'):
                            self.send_player_info(conn, int(data[7:]))
                            reply = ''
                            continue
     
                        conn.sendall(bytes(json.dumps(reply), encoding='utf-8'))

        except Exception as e:
            print(e, 's1')
                
        print('lost connection')
            
        self.pid -= 1

        self.game.remove_player(id)
                
        conn.close()
        del self.connections[id]
        
    def verify_connection(self, conn):
        code = conn.recv(4096).decode()
        conn.sendall(str.encode(confirmation_code))
        
        return code == confirmation_code
        
    def start(self):
        bind = False
        try: 
            self.sock.bind(self.addr)
            bind = True

        except socket.error as e:
            print(e, 's3')
            raise PortInUse
            
        finally:
        
            if bind:
                self.set_game()
                self.run()

        self.close()
            
    def run(self):
        self.sock.listen()
        
        while True:
    
            try:
                conn, addr = self.sock.accept()
                
                print('connected to', addr)
                
                if self.verify_connection(conn):
                    start_new_thread(self.threaded_client, (conn, self.pid))
                    self.connections[self.pid] = conn
                    self.pid += 1
                else:
                    conn.close()

            except socket.timeout:
                if self.pid == 0:
                    break
                    
            except Exception as e:
                print(e, 's4')
                break
                
            finally:
                if len(self.connections) == 0: 
                    break

s = Server()
s.start()
        
        
        
        
        
        
        
        
        
    
    

