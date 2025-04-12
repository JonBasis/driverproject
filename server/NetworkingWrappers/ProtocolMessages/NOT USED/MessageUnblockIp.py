from ProtocolMessage import ProtocolMessage

class MessageUnblockIp(ProtocolMessage):
    MESSAGE_UNBLOCK_IP_CODE = 'UNBLOCKIP'

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(self.MESSAGE_BLOCK_IP_CODE)
        
        except Exception as e:
            print(f"exception in MessageUnblockIp.__init__(), {e}")
            raise