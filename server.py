import socket
from _thread import start_new_thread
import json
from game import Game

confirmation_code = 'thisisthecardgameserver'

class PortInUse(Exception):
    pass

def get_port():
    try:
    
        with open('save.json', 'r') as f:
            
            data = json.load(f)
            port = data['port']
            
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
        
        self.game = None
        
    def set_game(self):
        self.game = Game()
        
    def close_all(self):
        for pid, conn in self.connections.items():
            
            conn.close()
            
    def threaded_client(self, conn, id):
        connected = self.game.new_player(id)
    
        if connected:
        
            conn.send(str.encode(confirmation_code))
            reply = ''
            
            while connected:
                
                try:
                
                    data = conn.recv(4096).decode()

                    if data is None:
                        
                        break
                        
                    else:
                        
                        if data == 'pid':
                            
                            reply = id
                        
                        if data == 'disconnect': #disconnect
                            
                            connected = False

                        elif data == 'info': #get update info
                            
                            self.game.update_player(id)
                            self.game.main()
                            reply = self.game.get_info(id)
                            
                        elif data.startswith('name'): #set player name
                            
                            reply = self.game.get_player(id).set_name(data.split(',')[-1])
                        
                        elif data == 'start': #start game
                            
                            self.game.start(id)
                            reply = 1
                            
                        elif data == 'reset': #reset game
                            
                            self.game.reset()
                            reply = 1
                            
                        elif data == 'continue': #continue to next game/round
                            
                            status = self.game.status
                            
                            if status == 'next round':
                                
                                self.game.new_round()
                                
                            elif status == 'new game':
                                
                                self.game.new_game()
                                
                            reply = 1
                            
                        elif data == 'play': #play card
                            
                            if self.game.status == 'playing':
                            
                                self.game.update_player(id, 'play')
                                
                            reply = 1
                            
                        elif data == 'cancel': #cancel selection
                            
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

                        elif data == 'settings': #get settings
                            
                            reply = self.game.get_settings()
                            
                        elif data == 'us':
                
                            if self.game.status == 'waiting':
                                
                                self.game.update_settings()
                                reply = 1
                            
                            else:
                                
                                reply = 0

                        conn.sendall(bytes(json.dumps(reply), encoding='utf-8'))

                except Exception as e:
                    
                    print(e, 's1')
                    
                    break
                
        print('lost connection')
            
        self.pid -= 1

        self.game.remove_player(id)
                
        conn.close()
        del self.connections[id]
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.settimeout(3)
            
            try: 

                s.bind(self.addr)

            except socket.error as e:
                
                print(e, 's3')
                
                raise PortInUse

            print('server started')

            self.set_game()

            self.run(s)
            
    def run(self, s):
        s.listen()
        
        while True:
    
            try:

                conn, addr = s.accept()
                
                print('connected to', addr)
                
                start_new_thread(self.threaded_client, (conn, self.pid))
                self.connections[self.pid] = conn
                self.pid += 1

            except socket.timeout:
                
                if self.pid == 0:

                    break
                    
            except Exception as e:
                
                print(e, 's4')
                
                break
                
            finally:
                
                if len(self.connections) == 0:
                    
                    break
                
        self.close_all()     
        s.close()

        print('server closed')

s = Server()
s.start()
        
        
        
        
        
        
        
        
        
    
    

