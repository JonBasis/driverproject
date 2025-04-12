import json
import base64

class ProtocolMessage:
    MESSAGE_SET : set[str] = set({
        'HELLO',
        'MYKEY',
        'KEY',
        'ACKHELLO',
        'AUTH',
        'BLOCKIP',
        'UNBLOCKIP',
        'BLOCKPORT',
        'UNBLOCKPORT',
        'ENUMIP',
        'ENUMPORT',
        'CLOSE',
        'STRMESSAGE'
    })
    
    def __init__(self, code : str, **kwargs) -> None:
        try:
            self._code : str = code
            self._dict : dict = kwargs
            
        except Exception as e:
            print(f"exception in ProtocolMessage.__init__(), {e}")
            raise
    
    def get_value(self, key):
        if self._dict[key]:
            return self._dict[key]
        
        raise ValueError(f"value for {key} does not exist in ProtocolMessage dict")
    
    def get_code(self) -> str:
        return self._code
    
    def export_message(self) -> bytes:
        try:
            representing_list_dict : dict = {key : base64.b64encode(value.encode() if type(value) != bytes and value != None else value).decode('utf-8') for key, value in self._dict.items()}
            representing_list : list = [
                self._code,
                representing_list_dict
            ]

            json_list : str = json.dumps(representing_list)

            return json_list.encode()
        
        except Exception as e:
            print(f"exception in ProtocolMessage.export_message(), {e}")
            raise
    
    @staticmethod
    def import_message(message_json : str) -> 'ProtocolMessage':
        try:
            representing_list : list = json.loads(message_json)
            message_code : str = representing_list[0]

            if message_code not in ProtocolMessage.MESSAGE_SET:
                raise ValueError("missing message code in message")
            
            message_dict : dict = {key : base64.b64decode(value) for key, value in representing_list[1].items()}
            
            if type(message_dict) != dict:
                raise ValueError("message dict is not dict")
            
            imported_message : ProtocolMessage = ProtocolMessage(message_code, **message_dict)

            return imported_message
        
        except Exception as e:
            print(f"exception in MessageParser.parse_message(), {e}")
            raise