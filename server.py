import os
import threading
from _thread import start_new_thread
import traceback

from save import SAVE, CONFIRMATION_CODE
from net_base import Network_Base, get_local_ip
from game import Game
import exceptions

def get_port():
    try:
        port = SAVE.get_data('port')       
    except:
        port = 5555
    return port

class Server(Network_Base):
    def __init__(self):
        server = get_local_ip()
        port = get_port()
        super().__init__(server, port)
        
        self.pid = 0

        self.game = Game('online')
        self.player_info = {}
            
    def close(self):
        super().close()
        
        for f in os.listdir('img/temp'):
            os.remove(f'img/temp/{f}')
        
        print('server closed')
      
    def send_player_info(self, conn, pid):
        p = self.game.get_player(pid)
        info = p.get_info()
        with open(info['image'], 'rb') as f:
            image = f.read()
        info['raw_image'] = self.encode_bytes(image)
        
        data = bytes(self.dump_json(info), encoding='utf-8')
        self.send_large_raw(data, conn=conn)
   
    def recieve_player_info(self, id, conn):
        info = self.recv_large_raw(conn=conn)

        info = self.load_json(info)
        image = self.decode_bytes(info['raw_image'])

        filename = f'img/temp/{id}.png'
        with open(filename, 'wb') as f:
            f.write(image)
            
        info['image'] = filename
        info['id'] = id 
        self.player_info[id] = info

    def threaded_client(self, address, conn, id):
        try:
            
            self.recieve_player_info(id, conn)
            connected = self.game.add_player(id, self.player_info[id])
        
            if connected:
            
                reply = ''

                while connected:

                    data = self.recv(conn=conn)

                    if data is None:
                        break
                        
                    else:
                        
                        if data == 'pid':
                            reply = id
                        
                        if data == 'disconnect':
                            reply = '1'
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
                            
                        elif data.lstrip('-').isdigit():
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
                            save.SAVE.load_save()
                            self.game.update_settings()
                            reply = 1

                        elif data.startswith('getinfo'):
                            self.send_player_info(conn, int(data[7:]))
                            reply = ''
                            continue

                        self.send(self.dump_json(reply), conn=conn)

        except Exception as e:
            print(e, 's1', traceback.format_exc())
                
        print('lost connection')
            
        self.pid -= 1
        self.game.remove_player(id)
        self.close_connection(conn, address)
        
    def verify_connection(self, conn):
        code = self.recv(conn=conn)
        self.send(CONFIRMATION_CODE, conn=conn)
        return code == CONFIRMATION_CODE
        
    def add_connection(self, conn, address):
        if self.verify_connection(conn):
            print('connected to', address)
            start_new_thread(self.threaded_client, (address, conn, self.pid))
            self.pid += 1
            super().add_connection(conn, address)
        else:
            conn.close()
            
    def check_close(self):
        return not self.pid or self.errors
            
    def run(self):
        self.start_server()
        e = self.get_error()
        if e is OSError:
            print(e, 's3')
            errno = e.args[0]
            if errno == 98:
                raise exceptions.PortInUse
            self.close()
        else:
            self.listen()
        
s = Server()
s.run()
        
        
    
    

