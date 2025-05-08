from NetworkingWrappers.Client import Client
from DeviceIoControl.DeviceHandler import DeviceHandler
from NetworkingWrappers.ProtocolMessages.ProtocolMessage import ProtocolMessage

SERVER_IP : str = '192.168.1.39'
SERVER_PORT : int = 12345

DEVICE_NAME = r"\\.\driver"

device_handler : DeviceHandler = None

id_password_file_path : str = r"./id_password"

def test_driver() -> None:
    """ function to test that the driver is working """
    
    input_string : str = input("enter a message: ")
    output : str = device_handler.test_driver(input_string)
    print(f"got from driver: {output}")


def block_ip() -> None:
    """ function to block an ip from sending and recieving packets """

    input_string : str = input("ip to block: ")
    success : bool = device_handler.block_ip(input_string)
    print(f"ip {input_string} blocked successfully" if success else "error blocking ip")
    

def unblock_ip() -> None:
    """ function to unblock an ip from sending and recieving packets """

    input_string : str = input("ip to unblock: ")
    success : bool = device_handler.unblock_ip(input_string)
    print(f"ip {input_string} unblocked successfully" if success else "error unblocking ip")
    

def block_port() -> None:
    """ function to block traffic from passing through a port """

    input_string : str = input("port to block: ")
    success : bool = device_handler.block_port(input_string)
    print(f"port {input_string} blocked successfully" if success else "error blocking port")


def unblock_port() -> None:
    """ function to unblock traffic from passing through a port """
    
    input_string : str = input("port to unblock: ")
    success : bool = device_handler.unblock_port(input_string)
    print(f"port {input_string} unblocked successfully" if success else "error unblocking port")


def enum_ip() -> None:
    """ function to enumerate all blocked ip from driver """
    print("enum ip")
    blocked_ip : list[str] = device_handler.enum_ip()
    print(blocked_ip)
    


def enum_port() -> None:
    """ function to enumerate all blocked ports from driver """
    print("enum port")
    blocked_ports : list[int] = device_handler.enum_port()
    if blocked_ports == None:
        print("error enumerating ports")
        return

    print(f"blocked ports: {blocked_ports}")

def print_menu() -> None:
    """ prints menu for DeviceIoControl operations """

    print('''
          -----------------menu-----------------
          1. test driver
          2. block ip
          3. unblock ip
          4. block port
          5. unblock port
          6. enum blocked ip
          7. enum blocked ports
          8. exit
          -----------------menu-----------------
          ''')
    

def menu() -> None:
    """ menu for driver related operations """

    while True:
        print_menu()
        choice : int = int(input("choice: "))
        if choice == 1:
            test_driver()
        elif choice == 2:
            block_ip()
        elif choice == 3:
            unblock_ip()
        elif choice == 4:
            block_port()
        elif choice == 5:
            unblock_port()
        elif choice == 6:
            enum_ip()
        elif choice == 7:
            enum_port()
        elif choice == 8:
            return
        else:
            print("invalid choice")
 

def identify_to_server(client_object : Client, driver_id : int, password : str) -> bool:
    verify_message : ProtocolMessage = ProtocolMessage("IDENTIFY", status="driver")
    client_object.send_message(verify_message)

    verify_ack_message : ProtocolMessage = client_object.recv_message()
    if verify_ack_message.get_code() == "ERROR":
        print(verify_ack_message.get_value("error_code"), verify_ack_message.get_value("error"))
        return False
    
    elif verify_ack_message.get_code() != "ACKIDENTIFY":
        return False
    
    auth_message : ProtocolMessage = ProtocolMessage("AUTH", id=driver_id, password=password)
    client_object.send_message(auth_message)

    auth_ack_message : ProtocolMessage = client_object.recv_message()
    if auth_ack_message.get_code() == "ACKAUTH":
        return True
    
    elif auth_ack_message.get_code() == "ERROR":
        print(auth_ack_message.get_value("error_code"), auth_ack_message.get_value("error"))
        return False
    
    return False


def update_blocked_ips(server_ips_list : list[int], blocked_ips : list[int]) -> None:
    count1 : int = 0
    count2 : int = 0
    while count1 < len(server_ips_list) and count2 < len(blocked_ips):
        if server_ips_list[count1] == blocked_ips[count2]:
            count1 += 1
            count2 += 1
            continue

        if server_ips_list[count1] < blocked_ips[count2]:
            device_handler.block_ip_int(server_ips_list[count1])
            count1 += 1
        else:
            device_handler.unblock_ip_int(blocked_ips[count2])
            count2 += 1
    
    while count1 < len(server_ips_list):
        device_handler.block_ip_int(server_ips_list[count1])
        count1 += 1
    
    while count2 < len(blocked_ips):
        device_handler.unblock_ip_int(blocked_ips[count2])
        count2 += 1


# def update_blocked_ports(server_ports_list : list[int], blocked_ports : list[int]) -> None:
#     for i in range(len(blocked_ports)):
#         if server_ports_list[i] == blocked_ports[i]:
#             continue

#         if server_ports_list[i] and not blocked_ports[i]:
#             device_handler.block_port(i)
#         elif not server_ports_list[i] and blocked_ports[i]:
#             device_handler.unblock_port[i]


def update_blocked_ports(server_ports_list : list[int], blocked_ports : list[int]) -> None:
    count1 : int = 0
    count2 : int = 0
    while count1 < len(server_ports_list) and count2 < len(blocked_ports):
        if server_ports_list[count1] == blocked_ports[count2]:
            count1 += 1
            count2 += 1
            continue

        if server_ports_list[count1] < blocked_ports[count2]:
            device_handler.block_port(server_ports_list[count1])
            count1 += 1
        else:
            device_handler.unblock_port(blocked_ports[count2])
            count2 += 1
    
    while count1 < len(server_ports_list):
        device_handler.block_port(server_ports_list[count1])
        count1 += 1
    
    while count2 < len(blocked_ports):
        device_handler.unblock_port(blocked_ports[count2])
        count2 += 1


def handle_update(client_object : Client, server_ips_list : list[int], server_ports_list : list[int]) -> None:
    blocked_ips : list[int] = [blocked_ip for blocked_ip, count in device_handler.enum_ip_int()]
    blocked_ports : list[int] = [blocked_port for blocked_port, count in device_handler.enum_port()]

    update_blocked_ips(server_ips_list, blocked_ips)
    update_blocked_ports(server_ports_list, blocked_ports)


def is_id_password_file_empty() -> bool:
    with open(id_password_file_path, "r") as file:
        return True if file.read() else False


def setup_id_password(driver_id, driver_password) -> None:
    print("ask for admin to create a new id and password")
    with open(id_password_file_path, "w") as file:
        file.write(str(driver_id) + "\n" + driver_password)


def clear_id_password() -> None:
    with open(id_password_file_path, "w") as file:
        file.write("")


def get_id_password() -> tuple[int, str]:
    with open(id_password_file_path, "r") as file:
        id_password : str = file.read()
        fields : list[str, str] = id_password.split("\n")
        if len(fields) != 2:
            return None, None
        return int(fields[0]), fields[1]


def handle_requests(client_object : Client) -> None:
    while True:
        response : ProtocolMessage = None
        update_message : ProtocolMessage = client_object.recv_message()
        if update_message.get_code() == "ERROR":
            print(update_message.get_value("error_code"), update_message.get_value("error"))
            continue

        elif update_message.get_code() == "UPDATE":
            to_be_blocked_ips : list[int] = update_message.get_value("blocked_ips")
            to_be_blocked_ports : list[int] = update_message.get_value("blocked_ports")
            handle_update(client_object, to_be_blocked_ips, to_be_blocked_ports)
            continue

        elif update_message.get_code() == "BLOCKIP":
            ip : str = update_message.get_value("ip")
            success = device_handler.block_ip(ip)

        elif update_message.get_code() == "UNBLOCKIP":
            ip : str = update_message.get_value("ip")
            success = device_handler.unblock_ip(ip)
            
        elif update_message.get_code() == "BLOCKPORT":
            port : int = update_message.get_value("port")
            success = device_handler.block_port(port)

        elif update_message.get_code() == "UNBLOCKPORT":
            port : int = update_message.get_value("port")
            success = device_handler.unblock_port(port)
        
        elif update_message.get_code() == "ENUMIP":
            ip_array : list[int, int] = device_handler.enum_ip_int()
            if ip_array == None:
                client_object.send_error("ENUMIP", "error getting ip array")
                continue
            response = ProtocolMessage("ENUMIPR", ip_array=ip_array)
        
        elif update_message.get_code() == "ENUMPORT":
            port_array : list[int, int] = device_handler.enum_port()
            if port_array == None:
                client_object.send_error("ENUMPORT", "error getting port array")
                continue
            response = ProtocolMessage("ENUMPORTR", port_array=port_array)
        
        if response:
            client_object.send_message(response)
        else:
            ack_command_message : ProtocolMessage = ProtocolMessage("ACKCOMMAND", success=success)
            client_object.send_message(ack_command_message)


def main() -> None:
    global device_handler

    # try:
    print("[+] creating device handler object")
    device_handler = DeviceHandler(DEVICE_NAME)

    print("[+] device handler object created")
    
    client_object : Client = Client(False, SERVER_IP, SERVER_PORT)

    success : bool = client_object.handshake()
    if not success:
        print("handshake failed")
        return
    
    # if is_id_password_file_empty():
    driver_id : int = int(input("id:"))
    password : str = input("password:")
    #     setup_id_password(driver_id, password)
    # else:
    #     driver_id, password = get_id_password()
    #     if not driver_id:
    #         clear_id_password()
    #         print("invalid id password file")
    #         return
    
    success : bool = identify_to_server(client_object, driver_id, password)

    if not success:
        clear_id_password()
        print("invalid id or password")
        return
    
    handle_requests(client_object)
    
    menu()
    # except Exception as e:
    #     print(e)
    
if __name__ == '__main__':
    main()