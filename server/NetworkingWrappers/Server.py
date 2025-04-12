import socket
from socket import socket
from .ServerClient import ServerClient
import threading
from threading import Lock
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

class Server():
    RSA_KEY_SIZE : int = 2048

    def _generate_rsa_keys(self) -> None:
        key = RSA.generate(2048)
        self._private_key : bytes = key.export_key()
        self._public_key : bytes = key.publickey().export_key()

    def __init__(self, debug : bool, ip : str, port : int, backlog : int = None) -> None:
        try:
            self._debug : bool = debug
            self._ip : str = ip
            self._port : int = port
            self._socket : socket = socket()
            self._socket.bind((ip, port))
            self._clients : list[ServerClient] = []
            self._client_count : int = 0
            self._clients_lock : Lock = Lock()
            
            self._generate_rsa_keys()

            if backlog:
                self._socket.listen(backlog)
            else:
                self._socket.listen()

        except Exception as e:
            print(f"exception in Server.__init__(), {e}")
            raise

        except Exception as e:
            print(f"exception in Server.setup(), {e}")
            raise
        
    def _add_client(self, client : ServerClient) -> None:
        with self._clients_lock:
            self._clients.append(client)
            self._client_count += 1

    def accept_client(self) -> ServerClient:
        try:
            conn, address = self._socket.accept()
            ip : str = address[0]
            port : int = address[1]

            client : ServerClient = ServerClient(self._debug, ip, port, conn, self._public_key, self._private_key)
            self._add_client(client)

            return client
        
        except Exception as e:
            print(f"exception in Server.accept_client(), {e}")
            raise