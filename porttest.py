import socket

server = socket.gethostbyname(socket.gethostname())
port = 80

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	
    try:
        
        s.bind((server, port))
        
    except Exception as e:
        
        print(e)