from NetworkingWrappers.Client import Client
from DeviceIoControl.DeviceHandler import DeviceHandler
import struct

SERVER_IP : str = '127.0.0.1'
SERVER_PORT : int = 12345

DEVICE_NAME = r"\\.\driver"

device_handler : DeviceHandler = None

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
    

def main() -> None:
    global device_handler

    # try:
    print("[+] creating device handler object")
    device_handler = DeviceHandler(DEVICE_NAME)

    print("[+] device handler object created")
    
    menu()
    # except Exception as e:
    #     print(e)
    
if __name__ == '__main__':
    main()