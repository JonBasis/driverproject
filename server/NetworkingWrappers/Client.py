from .SocketWrapper import SocketWrapper
from .ProtocolMessages.ProtocolMessage import ProtocolMessage
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA

class Client(SocketWrapper):
    def __init__(self, debug : bool, ip : str, port : int, password : bytes) -> None:
        try:
            super().__init__(debug, ip, port)
            self.connect_to(ip, port)
            self._password : bytes = password
            
        except Exception as e:
            print(f"exception in Client.__init__(), {e}")
            raise
    
    def _generate_aes_key(self) -> bytes:
        key : bytes = get_random_bytes(self.KEY_LENGTH)
        
        return key
    
    def _encrypt_aes_key(self, key : bytes, server_public_key : bytes) -> bytes:
        rsa_key = RSA.import_key(server_public_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        encrypted_key : bytes = cipher.encrypt(key)
        return encrypted_key
    
    def _get_key_hello(self) -> bytes:
        hello_message : ProtocolMessage = ProtocolMessage("HELLO")
        self.send_message(hello_message)
        
        response : ProtocolMessage = self.recv_message()
        if type(response) != ProtocolMessage or response.get_code() != "MYKEY":
            raise ValueError(f"got invalid response, {response}")
        
        try:
            server_public_key : bytes = response.get_value("mykey")
            return server_public_key
        
        except ValueError as e:
            print(e)
            return None
        
    def _get_key_key(self, encrypted_aes_key : bytes, aes_key : bytes) -> bool:
        key_message : ProtocolMessage = ProtocolMessage("KEY", key=encrypted_aes_key)
        self.send_message(key_message)
        
        self._key = aes_key
        try:
            response : ProtocolMessage = self.recv_message()
            if response.get_code() != "ACKHELLO":
                print("got wrong message code")
                return False
            
            return True
        
        except ValueError as e:
            print(f"handshake failed, {e}")
            return False
    
    def _get_key(self) -> bool:
        server_public_key : bytes = self._get_key_hello()
        
        aes_key : bytes = self._generate_aes_key()
        encrypted_aes_key : bytes = self._encrypt_aes_key(aes_key, server_public_key)
        proof_for_server : bytes = b'ACKHELLO'
        
        success : bool = self._get_key_key(encrypted_aes_key, aes_key)

        return success
    
    def handshake(self) -> bool:
        success : bool = self._get_key()

        return success