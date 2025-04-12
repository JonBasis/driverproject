from NetworkingWrappers.Client import Client
import datetime
from datetime import datetime

SERVER_IP : str = "127.0.0.1"
SERVER_PORT : int = 12345

DEBUG = True

PASSWORD : bytes = b'123456789012345678901234'

def debug_print(message : str) -> None:
    if DEBUG:
        print(f"[{datetime.now()}], {message}")
    

def main() -> None:
    client_object : Client = Client(DEBUG, SERVER_IP, SERVER_PORT, b'123456789012345678901234')

    print("welcome!")
    
    client_object.handshake()

    while True:
        message : str = input("enter a message to send to the server: ")
        client_object.send_str(message)
        
        response : str = client_object.recv_message()
        debug_print(response)
    
    print("goodbye!")

if __name__ == '__main__':
    main()