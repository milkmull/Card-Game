import os
import socket
import threading
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
    
class Pass:
    pass

class Server(Network_Base):
    def __init__(self):
        server = get_local_ip()
        port = get_port()
        super().__init__(server, port)
        
        self.pid = 0
        self.threads = []

        self.game = Game('online')
        self.player_info = {}
            
    def close(self):
        super().close()
        for t in self.threads:
            t.join()
        for f in os.listdir('img/temp'):
            os.remove(f'img/temp/{f}')
        
        info = self.pop_exception()
        if info:
            e, tb = info
            if not isinstance(e, socket.error):
                print(f'server closed with error: {e}')
                print(tb)
                return
        print('server closed')
      
    def send_player_info(self, conn, pid):
        p = self.game.get_player(pid)
        info = p.get_info()
        with open(info['image'], 'rb') as f:
            image = f.read()
        info['raw_image'] = self.b64encode(image)
        
        data = bytes(self.dump_json(info), encoding='utf-8')
        self.send_large_raw(data, conn=conn)
   
    def recieve_player_info(self, id, conn):
        info = self.recv_large_raw(conn=conn)

        info = self.load_json(info)
        image = self.b64decode(info['raw_image'])

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
            while connected and self.connected:
                data = conn.recv(4096).decode()
                if data is None:
                    break
                reply = self.update_game(id, data, conn)
                if reply is Pass:
                    continue
                conn.sendall(self.encode(self.dump_json(reply)))

        except Exception as e:
            self.add_exception(e)
                
        print('lost connection to', address)
            
        self.pid -= 1
        self.game.remove_player(id)
        self.close_connection(conn, address)
        
    def update_game(self, id, data, conn):
        if data == 'pid':
            return id

        elif data == 'info':
            self.game.update_player(id)
            self.game.main()
            return self.game.get_info(id)
            
        elif data.startswith('name'):
            reply = self.game.get_player(id).set_name(data[5:])
        
        elif data == 'start':
            self.game.start(id)
            return 1
            
        elif data == 'reset':
            self.game.reset()
            return 1
            
        elif data == 'continue':
            status = self.game.status
            if status == 'next round':
                self.game.new_round()   
            elif status == 'new game':
                self.game.new_game()  
            return 1
            
        elif data == 'play':
            if self.game.status == 'playing':
                self.game.update_player(id, 'play')  
            return 1
            
        elif data == 'cancel':
            if self.game.status == 'playing':
                self.game.update_player(id, 'cancel')  
            return 1
            
        elif data.lstrip('-').isdigit():
            self.game.update_player(id, f'select {data}') 
            return 1
            
        elif data == 'flip':
            if self.game.status == 'playing':
                self.game.update_player(id, 'flip') 
            return 1
            
        elif data == 'roll':
            if self.game.status == 'playing':
                self.game.update_player(id, 'roll')  
            return 1

        elif data == 'settings':
            return self.game.get_settings()
            
        elif data == 'us':
            save.SAVE.load_save()
            self.game.update_settings()
            return 1

        elif data.startswith('getinfo'):
            self.send_player_info(conn, int(data[7:]))
            return Pass
        
    def verify_connection(self, conn):
        connected = False
        try:
            code = self.recv(conn=conn)
            self.send(CONFIRMATION_CODE, conn=conn)
            connected = True
        except:
            return False
        return connected and code == CONFIRMATION_CODE
        
    def add_connection(self, conn, address):
        if self.verify_connection(conn):
            print('connected to', address)
            t = threading.Thread(target=self.threaded_client, args=(address, conn, self.pid))
            t.start()
            self.threads.append(t)
            self.pid += 1
            super().add_connection(conn, address)
        else:
            conn.close()
            
    def check_close(self):
        return not self.pid
            
    def run(self):
        self.start_server()
        if not self.connected:  
            self.raise_last()
        self.listen()
        
    def get_exception(self, e):
        if e is OSError:
            errno = e.args[0]
            if errno == 98:
                return exceptions.PortInUse
        return e

s = Server()
s.run()
        
        
    
    

