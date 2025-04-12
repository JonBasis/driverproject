from ProtocolMessage import ProtocolMessage

class MessageAuth(ProtocolMessage):
    MESSAGE_AUTH_CODE = 'AUTH'
    
    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_AUTH_CODE)
        
        except Exception as e:
            print(f"exception in MessageAuth.__init__(), {e}")
            raise