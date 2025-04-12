from NetworkingWrappers.Server import Server
from NetworkingWrappers.ServerClient import ServerClient
import threading
from threading import Thread
import datetime
from datetime import datetime

SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345

DEBUG : bool = True

server_object : Server = None


def debug_print(message : str):
    """ debug print a message with datetime.now() """
    print(f"[{datetime.now()}] {message}")
    

def handle_client(client : ServerClient):
    """ client handling function """

    debug_print("client handler started")
    # try:
    client.handshake()
    
    while True:
        message : str = client.recv_str()
        client.send_str(message)
    
    # except Exception as e:
    #     print(f"exception in handle_client(), {e}")
    #     debug_print("terminating connection with client")
    #     client.__del__()
    

def main() -> None:
    global server_object
    
    debug_print("server starting")
    
    try:
        server_object = Server(DEBUG, SERVER_IP, SERVER_PORT)
        
    except Exception as e:
        print(f"exception in main(), {e}")
        return
    
    debug_print("server is listening")
    threads : list[Thread] = []
    threads_count : int = 0
    try:
        while True:
            client : ServerClient = server_object.accept_client()
            
            t : Thread = Thread(target=handle_client, args=(client, ))
            t.start()
            threads.append(t)
            threads_count += 1
            
    except Exception as e:
        print(f"exception in main(), {e}")
    

if __name__ == '__main__':
    main()