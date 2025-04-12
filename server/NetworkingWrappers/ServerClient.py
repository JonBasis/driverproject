from .SocketWrapper import SocketWrapper
import socket
from socket import socket
from .ProtocolMessages.ProtocolMessage import ProtocolMessage
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

class ServerClient(SocketWrapper):
    users = {
        '123' : b'123456789012345678901234'
    }
    
    def __init__(self, debug : bool, ip : str, port : int, conn : socket, public_key : bytes, private_key : bytes) -> None:
        try:
            super().__init__(debug, ip, port, conn)
            self._public_key : bytes = public_key
            self._private_key : bytes = private_key

        except Exception as e:
            print(f"exception in ServerClient.__init__(), {e}")
            raise
    
    def _decrypt_aes_key(self, key : bytes, private_key : bytes) -> bytes:
        rsa_key = RSA.import_key(private_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        decrypted_key : bytes = cipher.decrypt(key)
        return decrypted_key
    
    def _get_key_hello(self, public_key) -> bool:
        hello_message : ProtocolMessage = self.recv_message()
        if hello_message.get_code() != "HELLO":
            return False
        
        hello_message_response : ProtocolMessage = ProtocolMessage("MYKEY", mykey=public_key)
        self.send_message(hello_message_response)

        return True
    
    def _get_key_key(self) -> bool:
        key_message : ProtocolMessage = self.recv_message()
        if key_message.get_code() != "KEY":
            print("got wrong message code")
            return False
        
        try:
            encrypted_key : bytes = key_message.get_value("key")
            self._key = self._decrypt_aes_key(encrypted_key, self._private_key)
        
        except ValueError as e:
            print(e)
            return False
        
        ack_hello_message : ProtocolMessage = ProtocolMessage("ACKHELLO")
        self.send_message(ack_hello_message)

        return True
    
    def _get_key(self) -> bool:
        success : bool = self._get_key_hello(self._public_key)
        
        if not success:
            return False
        
        success = self._get_key_key()

        if not success:
            return False
        
        return True
    
    def handshake(self) -> bool:
        success : bool = self._get_key()
        
        return success