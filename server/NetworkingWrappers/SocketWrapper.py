import socket
from socket import socket
import datetime
from datetime import datetime
from .ProtocolMessages.ProtocolMessage import ProtocolMessage
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class SocketWrapper:
    MESSAGE_SIZE_PADDING : int = 6
    KEY_LENGTH : int = 32
    
    def __init__(self, debug : bool, ip : str, port : int, existing_socket : socket = None) -> None:
        try:
            self.debug : bool = debug
            self.ip : str = ip
            self.port : int = port

            self._socket : socket = existing_socket if existing_socket else socket()
            self._key : bytes = None

        except Exception as e:
            print(f"exception in SocketWrapper.__init__(), {e}")
            raise
    
    def __del__(self) -> None:
        self._socket.close()
    
    def debug_print(self, message : str) -> None:
        """ debug print """

        if self.debug:
            print(f"[{datetime.now()}] {message}")

    def _add_size(self, message : bytes) -> bytes:
        """ add size field to message """

        size_str : bytes = str(len(message)).zfill(self.MESSAGE_SIZE_PADDING).encode()
        message_with_size : bytes = size_str + message
        return message_with_size
    
    def _encrypt_message(self, message : bytes) -> bytes:
        """ encrypt message using session key """

        try:
            if not self._key:
                return message
            
            iv : bytes = get_random_bytes(AES.block_size)
            cipher = AES.new(self._key, AES.MODE_CBC, iv)
            padded_data : bytes = pad(message, AES.block_size)
            ciphertext : bytes = cipher.encrypt(padded_data)
            to_send : bytes = iv + ciphertext
            
            return to_send
        
        except Exception as e:
            print(f"exception in SocketWrapper._encrypt_message(), {e}")
            raise
    
    def send_message(self, message : ProtocolMessage) -> None:
        """ send message to connection """

        try:
            if type(message) != ProtocolMessage:
                raise ValueError(f"expected a ProtocolMessage object, got {type(message)}")
            
            to_send_message : bytes = message.export_message()
            to_send : bytes = self._encrypt_message(to_send_message)
            to_send = self._add_size(to_send)
            
            self._socket.send(to_send)
            self.debug_print(f"sent: {to_send_message}")

        except Exception as e:
            print(f"exception in SocketWrapper.send_message(), {e}")
            raise
    
    def send_str(self, message : str) -> None:
        """ send string to connection """

        try:
            protocol_message : ProtocolMessage = ProtocolMessage("STRMESSAGE", message_str=message)
            self.send_message(protocol_message)

        except Exception as e:
            print(f"exception in SocketWrappers.send_str(), {e}")
            raise
    
    def _get_size(self) -> int:
        """ get size from size field """

        try:
            size_str : bytes = self._socket.recv(self.MESSAGE_SIZE_PADDING)
            if not size_str:
                raise ValueError("recieved message is empty")
            
            size_str : str = size_str.decode()

            size : int = int(size_str)
            return size
        
        except Exception as e:
            print(f"exception in SocketWrapper._get_size(), {e}")
            raise
    
    def _decrypt_message(self, ciphertext : bytes) -> bytes:
        """ decrypt message using session key """

        try:
            if not self._key:
                return ciphertext
            
            iv : bytes = ciphertext[:AES.block_size]
            ciphertext = ciphertext[AES.block_size:]
            c = AES.new(self._key, AES.MODE_CBC, iv)
            decrypted_message : bytes = unpad(c.decrypt(ciphertext), AES.block_size)

            return decrypted_message
        
        except Exception as e:
            print(f"exception in SocketWrapper._decrypt_message(), {e}")
            raise
        
    def recv_message(self, recv_size = 1024) -> ProtocolMessage:
        """ recv message from connection """

        try:
            size : int = self._get_size()
            print(f"size: {size}")
            message : bytes = b""
            message_piece : bytes = None

            while True:
                if len(message) >= size:
                    break
                
                message_piece = self._socket.recv(recv_size)
                if not message_piece:
                    break
                
                message += message_piece
            
            self.debug_print(f"recieved: {message}")
            if len(message) < AES.block_size and self._key:
                raise ValueError("recieved message not valid")
            
            message = self._decrypt_message(message)
            message_json : str = message.decode()
            print(f'recv json: {message_json}')
            parsed_message : ProtocolMessage = ProtocolMessage.import_message(message_json)

            return parsed_message
        
        except Exception as e:
            print(f"exception in SocketWrapper.recv_message(), {e}")
            raise
    
    def recv_str(self, recv_size = 1024) -> str:
        """ recv string from connection """

        try:
            protocol_message : ProtocolMessage = self.recv_message(recv_size)
            if protocol_message.code != "STRMESSAGE":
                raise ValueError("recieved message is not a string message")
            
            return protocol_message.message_str
        
        except Exception as e:
            print(f"exception in SocketWrapper.recv_str(), {e}")
    
    def connect_to(self, ip : str, port : int) -> None:
        """ connect to server """

        try:
            self.debug_print(f"socket is connecting to ({ip}, {port})")
            self._socket.connect((ip, port))

        except Exception as e:
            print(f"exception in SocketWrapper.connect_to(), {e}")
            raise
    
    def send_error(self, error_code : str, error : str) -> None:
        """ send error message to connection """
        
        error_message : ProtocolMessage = ProtocolMessage("ERROR", error_code = error_code, error = error)
        self.send_message(error_message)