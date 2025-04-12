from ProtocolMessage import ProtocolMessage

class MessageEnumPort(ProtocolMessage):
    MESSAGE_ENUM_PORT_CODE = "ENUMPORT"

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_ENUM_PORT_CODE)
        
        except Exception as e:
            print(f"exception in MessageEnumPort.__init__(), {e}")
            raise