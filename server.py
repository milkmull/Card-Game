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
    
    print(e)
    
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

                if data == 'info':
                    
                    reply = game.info(id) #get info for each player (points, visible cards)
                
                elif data == 'start':
                    
                    reply = game.start(id) #signals the start of game
                    
                elif data == 'reset': 
                    
                    reply = game.reset() #resets the game
                    
                elif data == 'settings':
                    
                    reply = game.get_settings() #gets the games current settings
                    
                elif '-' == data[0]: #signals settings are being updated
                    
                    if game.wait:
                    
                        reply = game.update_settings(data) #only update settings if game is not active
                        
                    else:
                        
                        reply = False
                        
                elif data == 'disconnect': #end thread if player disconnected
                    
                    break
                    
                elif game.wait: #won't go past here if client is waiting to start game
                    
                    reply = 1

                elif check_int(data): #when player clicks on a card, the card id is sent to the game to check if the card can be interacted with

                    reply = game.select(id, int(data))
                    
                elif data == 'click': #if player clicks anywhere, the game checks if player is selecting a card from the selection area
                    
                    reply = game.select(id)
                    
                elif data == 'play': #when player is playing a card
                    
                    reply = game.play(id)
                    
                elif data == 'cancel': #when player cancels an input
                    
                    reply = game.cancel(id)
 
                if reply == 'close':
                    
                    break

                conn.sendall(pickle.dumps(reply))

        except Exception as e:
            
            print(e)
            
            break
            
    print('lost connection')
        
    pid -= 1
    
    if connected:

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
        
        
        
        
        
        
        
        
        
        
        
    
    

