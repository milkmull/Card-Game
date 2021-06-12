import socket
from _thread import start_new_thread
import json
import sys
from game import Game

def get_port():
    try:
    
        with open('save.json', 'r') as f:
            
            data = json.load(f)
            port = data['port']
            
    except:
        
        port = 5555
        
    return port

server = socket.gethostbyname(socket.gethostname())# '192.168.1.15' local ip address --> 'ipconfig' in cmd, IPv4
port = get_port()

pid = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #type of connection, how server string is delivered

try: 

    s.bind((server, port)) #binding server to port

except socket.error as e:
    
    print(e, 's3')
    
s.settimeout(3) #sets server to close if nobody connects within 10 seconds

s.listen() #listen for connections. argument is how many people can connect

print('waiting for connection, server started')

game = Game()

def check_int(string):
    try:
        
        int(string)
        
        return True
        
    except ValueError:
        
        return False
        
def close_all(connections):
    for pid, conn in connections.items():
        
        conn.close()

def threaded_client(conn, id):
    global game
    global pid
    global connections
    
    connected = game.new_player(id)
    
    if connected:
    
        conn.send(str.encode(str(id)))
        
        reply = ''
        
        while connected:
            
            try:
            
                data = conn.recv(4096).decode() #might need to increase
                    
                if not data:
                    
                    break
                    
                else:
                    
                    if data == 'disconnect': #disconnect
                        
                        connected = False

                    elif data == 'u': #check if there are any updates

                        game.update_player(id)
                        game.main()
                        
                        reply = game.check_logs(id)
                        
                    elif data == 'info': #get update info
                    
                        reply = game.get_info(id)
                        
                    elif data.startswith('name'): #set player name
                        
                        reply = game.get_player(id).set_name(data.split(',')[-1])
                    
                    elif data == 'start': #start game
                        
                        game.start(id)
                        
                        reply = 1
                        
                    elif data == 'reset': #reset game
                        
                        game.reset()
                        
                        reply = 1
                        
                    elif data == 'continue': #continue to next game/round
                        
                        status = game.status
                        
                        if status == 'next round':
                            
                            game.new_round()
                            
                        elif status == 'new game':
                            
                            game.new_game()
                            
                        reply = 1
                        
                    elif data == 'play': #play card
                        
                        if game.status == 'playing':
                        
                            game.play(id)
                            
                        reply = 1
                        
                    elif data == 'cancel': #cancel selection
                        
                        if game.status == 'playing':
                        
                            game.cancel(id)
                            
                        reply = 1
                        
                    elif check_int(data):
                    
                        game.select(id, int(data))
                            
                        reply = 1
                        
                    elif data == 'update':

                        game.update_player(id)
                        game.main()
                            
                        reply = 1
                        
                    elif data == 'flip':
                        
                        if game.status == 'playing':
                        
                            game.flip(id)
                            
                        reply = 1
                        
                    elif data == 'roll':
                        
                        if game.status == 'playing':
                        
                            game.roll(id)
                            
                        reply = 1

                    elif data == 'settings': #get settings
                        
                        reply = game.get_settings()
                        
                    elif data.startswith('-s:'):
                    
                        reply = game.get_setting(data[3:])
                        
                    elif '~' == data[0]: #update settings
                        
                        if game.status == 'waiting':
                        
                            game.update_settings(data)
                            
                            reply = 1
                            
                        else:
                            
                            reply = 0

                    conn.sendall(bytes(json.dumps(reply), encoding='utf-8'))

            except Exception as e:
                
                print(e, 's1')
                
                break
            
    print('lost connection')
        
    pid -= 1

    game.remove_player(id)
            
    conn.close()
    del connections[id]
    
connections = {}
                
while True: #looking for connections
    
    try:

        conn, addr = s.accept() #accepts incomming connection. conn is object representing what has connected, addr is local ip address of connected device
        
        print('connected to', addr)
        
        start_new_thread(threaded_client, (conn, pid)) #function imported from _thread. precesses client's requests while searching for other connections
        connections[pid] = conn
        pid += 1

    except socket.timeout:
        
        if pid == 0:

            break
            
    except Exception as e:
        
        print(e, 's4')
        
        break
        
    if len(connections) == 0:
        
        break
            
close_all(connections)     
s.close()

print('server closed')
        
        
        
        
        
        
        
        
        
    
    

