from ProtocolMessage import ProtocolMessage

class MessageBlockPort(ProtocolMessage):
    MESSAGE_BLOCK_PORT_CODE = 'BLOCKPORT'

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_BLOCK_PORT_CODE)
        
        except Exception as e:
            print(f"exception in MessageBlockPort.__init__(), {e}")
            raise