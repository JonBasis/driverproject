from ProtocolMessage import ProtocolMessage

class MessageClose(ProtocolMessage):
    MESSAGE_CLOSE_CODE = "CLOSE"

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_CLOSE_CODE)
        
        except Exception as e:
            print(f"exception in MessageClose.__init__(), {e}")
            raise