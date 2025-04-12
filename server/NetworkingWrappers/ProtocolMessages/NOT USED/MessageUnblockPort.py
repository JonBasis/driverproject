from ProtocolMessage import ProtocolMessage

class MessageUnblockPort(ProtocolMessage):
    MESSAGE_UNBLOCK_PORT_CODE = 'UNBLOCKPORT'

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_UNBLOCK_PORT_CODE)
        
        except Exception as e:
            print(f"exception in MessageUnblockIp.__init__(), {e}")
            raise