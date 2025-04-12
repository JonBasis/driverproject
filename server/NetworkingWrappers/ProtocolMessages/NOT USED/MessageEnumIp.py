from ProtocolMessage import ProtocolMessage

class MessageEnumIp(ProtocolMessage):
    MESSAGE_ENUM_IP_CODE = "ENUMIP"

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_ENUM_IP_CODE)
        
        except Exception as e:
            print(f"exception in MessageEnumIp.__init__(), {e}")
            raise