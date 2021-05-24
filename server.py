import socket
from _thread import start_new_thread
import pickle
import sys
from game import Game

server = socket.gethostbyname(socket.gethostname())# '192.168.1.15' local ip address --> 'ipconfig' in cmd, IPv4
port = 5555 #port we are using

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

def threaded_client(conn, id):
    global game
    global pid
    
    connected = game.new_player(id)
    
    conn.send(str.encode(str(id)))
    
    reply = ''
    
    while connected:
        
        try:
        
            data = conn.recv(4096).decode() #might need to increase
                
            if not data:
                
                break
                
            else:

                if data.startswith('info'):
                    
                    data = data.split('-')
                    
                    reply = game.get_info(id, int(data[1]), data[2].split(',')) #get info for each player (points, visible cards)
                    
                elif data.startswith('name'):
                    
                    reply = game.get_player(id).set_name(data.split(',')[-1])
                    
                elif data == 'players':
                            
                    reply = game.check_order()
                
                elif data == 'start':
                    
                    reply = game.start(id)
                    
                elif data == 'reset':
                    
                    reply = game.reset()
                    
                elif data == 'settings':
                    
                    reply = game.get_settings()
                    
                elif '~' == data[0]:
                    
                    if game.wait:
                    
                        reply = game.update_settings(data)
                        
                    else:
                        
                        reply = False
                        
                elif data == 'disconnect':
                    
                    connected = False
                    
                elif data == 'status':
                            
                    reply = game.check_status()
                    
                elif game.wait: #won't go past here if client is waiting to start game
                    
                    reply = 'w'
                
                elif data == 'status':
                            
                    reply = game.check_status()
                    
                elif data == 'continue':
                    
                    text = game.check_status()
                    
                    if text == 'next round':
                        
                        game.new_round()
                        
                    elif text == 'new game':
                        
                        game.new_game()
                        
                    reply = True
                    
                elif data == 'winner':
                    
                    reply = game.get_winner()
                    
                elif data == 'update':
                    
                    game.update_player(id)
                    
                    game.main()

                elif check_int(data):

                    reply = game.select(id, int(data))
                    
                elif data == 'event':
                    
                    reply = game.event_info()
                    
                elif data == 'shop':
                    
                    reply = game.get_shop()
                    
                elif data == 'click':
                    
                    reply = game.select(id)
                    
                elif data == 'play':
                    
                    reply = game.play(id)
                    
                elif data == 'flip':
                    
                    reply = game.flip(id)
                    
                elif data == 'roll':
                    
                    reply = game.roll(id)
                    
                elif data == 'cancel':
                    
                    reply = game.cancel(id)

                conn.sendall(pickle.dumps(reply))

        except Exception as e:
            
            print(e, 's1')
            
            break
            
    print('lost connection')
        
    pid -= 1

    game.remove_player(id)
            
    conn.close()
                
while True: #looking for connections
    
    try:

        conn, addr = s.accept() #accepts incomming connection. conn is object representing what has connected, addr is local ip address of connected device
        
        print('connected to', addr)
        
        start_new_thread(threaded_client, (conn, pid)) #function imported from _thread. precesses client's requests while searching for other connections
        
        pid += 1
        
    except socket.timeout:
        
        if pid == 0:
        
            break
            
    except Exception as e:
        
        print(e, 's4')
        
        if pid == 0:
            
            break
        

        
        
        
        
        
        
        
        
        
    
    

