import socket
from _thread import *
import sys

server = "192.168.88.150"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    a.bind((Server, port))
except socket.error as e:
    str(e)
    
a.listen() #In the bracket: The number of people you want to connect to the game
print("Waiting for a connection, Sever Started")

def threaded_client (conn):
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            
            if not data:
                print("Disconnected")
                break
            else:
                print("Received: ", reply)
                print("Sending: ", reply)
                
            conn.sendall(str.endcode(reply))
        except:
            break
        
    

while True: #continuously look for connection
    conn, addr = s.accept ()
    print("Connected to: ", addr)
    
    start_new_thread(threaded_client, (conn,))