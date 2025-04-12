import json
from ProtocolMessage import ProtocolMessage
from ProtocolTypes import MessageAuth
from ProtocolTypes import MessageBlockIp

class MessageParser:

    @staticmethod
    def parse_message(message_json : str):
        try:
            representing_list : list = json.loads(message_json)
            message_code : str = representing_list[0]

            if message_code not in MessageParser.MESSAGE_DICT:
                return None
            
            message_dict : dict = representing_list[1]
            
            imported_message = MessageParser[message_code].__init__(message_dict)

            return imported_message
        
        except Exception as e:
            print(f"exception in MessageParser.parse_message(), {e}")
            raise