from ProtocolMessage import ProtocolMessage

class MessageBlockIp(ProtocolMessage):
    MESSAGE_BLOCK_IP_CODE = 'BLOCKIP'

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_BLOCK_IP_CODE)
        
        except Exception as e:
            print(f"exception in MessageBlockIp.__init__(), {e}")
            raise