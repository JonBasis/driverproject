import json
import base64

class ProtocolMessage:
    MESSAGE_SET : set[str] = set({
        'HELLO',
        'MYKEY',
        'KEY',
        'ACKHELLO',

        'IDENTIFY',
        'ACKIDENTIFY',
        
        'AUTH',
        'ACKAUTH',
        
        'UPDATE',
        
        'BLOCKIP',
        'UNBLOCKIP',
        'BLOCKPORT',
        'UNBLOCKPORT',
        'ENUMIP',
        'ENUMPORT',
        'ACKCOMMAND',
        'ENUMIPR',
        'ENUMPORTR',
        'ADDADMIN',
        'ADDDRIVER',
        
        'CLOSE',
        'ACKCLOSE',
        
        'STRMESSAGE',

        'ERROR'
    })
    
    def __init__(self, code : str, **kwargs) -> None:
        try:
            self._code : str = code
            self._dict : dict = kwargs
            
        except Exception as e:
            print(f"exception in ProtocolMessage.__init__(), {e}")
            raise
    
    def get_value(self, key):
        """ get value from message dict """

        if self._dict[key] != None:
            return self._dict[key]
        
        raise ValueError(f"value for {key} does not exist in ProtocolMessage dict")
    
    def get_code(self) -> str:
        """ get message code """

        return self._code
    
    def export_message(self) -> bytes:
        """ export message to (json) bytes """

        try:
            representing_list_dict : dict = {key : ["b64", base64.b64encode(value).decode('utf-8')] if type(value) == bytes else value for key, value in self._dict.items()}
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
        """ import message from json """
        
        try:
            representing_list : list = json.loads(message_json)
            message_code : str = representing_list[0]

            if message_code not in ProtocolMessage.MESSAGE_SET:
                raise ValueError("missing message code in message")
            
            message_dict : dict = {key : base64.b64decode(value[1]) if (type(value) == list and len(value) > 0 and value[0] == "b64") else value for key, value in representing_list[1].items()}
            
            if type(message_dict) != dict:
                raise ValueError("message dict is not dict")
            
            imported_message : ProtocolMessage = ProtocolMessage(message_code, **message_dict)

            return imported_message
        
        except Exception as e:
            print(f"exception in MessageParser.import_message(), {e}")
            raise