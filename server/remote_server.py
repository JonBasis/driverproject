from NetworkingWrappers.Server import Server
from NetworkingWrappers.ServerClient import ServerClient
import threading
from threading import Thread
import datetime
from datetime import datetime
from db_handling.DBHandler import DBHandler
from NetworkingWrappers.ProtocolMessages.ProtocolMessage import ProtocolMessage
from time import sleep
from DeviceIoControl.DeviceHandler import DeviceHandler

db : DBHandler = DBHandler()

SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345

DEBUG : bool = True

server_object : Server = None

server_running : bool = True

logged_drivers : dict[int, (threading.Lock, ServerClient)] = {}

logged_drivers_lock : threading.Lock = threading.Lock()

logged_admins : set[int] = set([])

logged_admins_lock : threading.Lock = threading.Lock()

def debug_print(message : str):
    """ debug print a message with datetime.now() """
    print(f"[{datetime.now()}] {message}")
    

def setup_admin() -> None:
    """ setup admin user """

    db.add_admin(0, 'root')

def update_driver(client : ServerClient, driver_id : int) -> None:
    """ update driver blocked_ips and blocked_ports """

    while server_running:
        blocked_ips : list[int] = db.get_blocked_ips(driver_id)
        blocked_ports : list[int] = db.get_blocked_ports(driver_id)

        update_message : ProtocolMessage = ProtocolMessage("UPDATE", blocked_ips=blocked_ips, blocked_ports=blocked_ports)
        client.send_message(update_message)
        sleep(30)


def handle_driver(client : ServerClient):
    """ driver handler function """
    try:
        auth_message : ProtocolMessage = client.recv_message()
        if not auth_message or auth_message.get_code() != "AUTH":
            client.send_error("AUTH", "expected AUTH message")
            return
        
        driver_id : int = auth_message.get_value("id")
        password : str = auth_message.get_value("password")

        with logged_drivers_lock:
            if driver_id in logged_drivers.keys():
                client.send_error("AUTH", "driver already logged on")
                return
        
        if not db.verify_driver(driver_id, password):
            client.send_error("AUTH", "driver unverified")
            return
        
        auth_ack_message : ProtocolMessage = ProtocolMessage("ACKAUTH")
        client.send_message(auth_ack_message)

        with logged_drivers_lock:
            logged_drivers[driver_id] = threading.Lock(), client
        
        update_driver(client, driver_id)
    
    except Exception as e:
        print(f"error in handle_driver: {e}")
        with logged_drivers_lock:
            if driver_id in logged_drivers.keys():
                del logged_drivers[driver_id]
                print(f"logged_drivers: {logged_drivers}")
    finally:
        client.__del__()
    
def _convert_string_to_ip(string : str) -> int:
        """ converts ip string to int """
        try:
            ip_parts : list[str] = [int(part) for part in string.split(".")]

        except ValueError as e:
            print("invalid ip string")
            return None
        
        if len(ip_parts) != 4:
            return None
        
        sum_of_parts : int = 0
        for i in range(len(ip_parts)):
            if ip_parts[i] < 0 or ip_parts[i] > 255:
                return None
            
            sum_of_parts += (ip_parts[i] << (8 * (3 - i)))
            
        return sum_of_parts


def block_ip_handler(driver_id : int, ip : str) -> bool:
    """ block ip handler """

    int_ip : int = _convert_string_to_ip(ip)
    
    if int_ip == None:
        return False
    
    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return False
    
    success : bool = db.block_ip(driver_id, int_ip)
    if not success:
        return False
    
    with logged_drivers[driver_id][0]:
        command_message : ProtocolMessage = ProtocolMessage("BLOCKIP", ip=ip)
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
        if response.get_code() != "ACKCOMMAND":
            return False
        
        success = response.get_value("success")
    
    return success


def unblock_ip_handler(driver_id : int, ip : str) -> bool:
    """ unblock ip handler """

    int_ip : int = _convert_string_to_ip(ip)

    if int_ip == None:
        return False
    
    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return False
    
    success : bool = db.unblock_ip(driver_id, int_ip)
    if not success:
        return False
    
    with logged_drivers[driver_id][0]:
        command_message : ProtocolMessage = ProtocolMessage("UNBLOCKIP", ip=ip)
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
        if response.get_code() != "ACKCOMMAND":
            return False
        
        success = response.get_value("success")
    
    return success


def block_port_handler(driver_id : int, port : int) -> bool:
    """ block port handler """

    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return False
    
    success : bool = db.block_port(driver_id, port)
    if not success:
        return False
    
    with logged_drivers[driver_id][0]:
        command_message : ProtocolMessage = ProtocolMessage("BLOCKPORT", port=port)
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
        if response.get_code() != "ACKCOMMAND":
            return False
        
        success = response.get_value("success")
    
    return success


def unblock_port_handler(driver_id : int, port : int) -> bool:
    """ unblock port handler """
    
    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return False
    
    success : bool = db.unblock_port(driver_id, port)
    if not success:
        return False
    
    with logged_drivers[driver_id][0]:
        command_message : ProtocolMessage = ProtocolMessage("UNBLOCKPORT", port=port)
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
        if response.get_code() != "ACKCOMMAND":
            return False
        
        success = response.get_value("success")
    
    return success


def enum_ip_handler(driver_id : int) -> list[str, int]:
    """ enum ip handler """

    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return None
    
    command_message : ProtocolMessage = ProtocolMessage("ENUMIP")
    with logged_drivers[driver_id][0]:
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
    
    if response.get_code() != "ENUMIPR":
        return None
    
    ip_array : list[str, int] = response.get_value("ip_array")
    
    return ip_array


def enum_port_handler(driver_id : int) -> list[int, int]:
    """ enum port handler """

    with logged_drivers_lock:
        if driver_id not in logged_drivers.keys():
            return None
    
    command_message : ProtocolMessage = ProtocolMessage("ENUMPORT")
    with logged_drivers[driver_id][0]:
        client : ServerClient = logged_drivers[driver_id][1]
        client.send_message(command_message)
        response : ProtocolMessage = client.recv_message()
    
    if response.get_code() != "ENUMPORTR":
        return None
    
    port_array : list[str, int] = response.get_value("port_array")
    
    return port_array


def handle_admin_commands(client : ServerClient, admin_id : int) -> None:
    """ admin commands handler """

    admin_commands_message : ProtocolMessage = None
    while server_running:
        admin_commands_message = client.recv_message()
        message_code : str = admin_commands_message.get_code()
        success : bool = False
        if message_code == "CLOSE":
            close_ack_message : ProtocolMessage = ProtocolMessage("ACKCLOSE")
            client.send_message(close_ack_message)
            return
        
        elif message_code == "BLOCKIP":
            ip : str = admin_commands_message.get_value("ip")
            driver_id : int = admin_commands_message.get_value("driver_id")
            success = block_ip_handler(driver_id, ip)
        
        elif message_code == "UNBLOCKIP":
            ip : str = admin_commands_message.get_value("ip")
            driver_id : int = admin_commands_message.get_value("driver_id")
            success = unblock_ip_handler(driver_id, ip)
        
        elif message_code == "BLOCKPORT":
            port : int = admin_commands_message.get_value("port")
            driver_id : int = admin_commands_message.get_value("driver_id")
            success = block_port_handler(driver_id, port)
        
        elif message_code == "UNBLOCKPORT":
            port : int = admin_commands_message.get_value("port")
            driver_id : int = admin_commands_message.get_value("driver_id")
            success = unblock_port_handler(driver_id, port)
        
        elif message_code == "ENUMIP":
            driver_id : int = admin_commands_message.get_value("driver_id")
            ip_array : list[str, int] = enum_ip_handler(driver_id)
            command_response : ProtocolMessage = ProtocolMessage("ENUMIPR", ip_array=ip_array)
            client.send_message(command_response)
            continue

        elif message_code == "ENUMPORT":
            driver_id : int = admin_commands_message.get_value("driver_id")
            port_array : list[int, int] = enum_port_handler(driver_id)
            command_response : ProtocolMessage = ProtocolMessage("ENUMPORTR", port_array=port_array)
            client.send_message(command_response)
            continue
            
        elif message_code == "ADDADMIN":
            admin_id : int = admin_commands_message.get_value("id")
            admin_password : str = admin_commands_message.get_value("password")
            success = db.add_admin(admin_id, admin_password)
        
        elif message_code == "ADDDRIVER":
            driver_id : int = admin_commands_message.get_value("id")
            driver_password : str = admin_commands_message.get_value("password")
            success = db.add_driver(driver_id, driver_password)
        
        else:
            client.send_error("ERROR", "unknown admin command")
            continue

        command_ack_message : ProtocolMessage = ProtocolMessage("ACKCOMMAND", command=message_code, success=success)
        client.send_message(command_ack_message)

def handle_admin(client : ServerClient):
    """ admin handler function """
    
    try:
        auth_message : ProtocolMessage = client.recv_message()
        if not auth_message or auth_message.get_code() != "AUTH":
            client.send_error("AUTH", "expected AUTH message")
            return
        
        admin_id : int = auth_message.get_value("id")
        password : str = auth_message.get_value("password")

        with logged_admins_lock:
            if admin_id in logged_admins:
                client.send_error("AUTH", "admin already logged on")
                return
        
        if not db.verify_admin(admin_id, password):
            client.send_error("AUTH", "admin unverified")
            return
        
        auth_ack_message : ProtocolMessage = ProtocolMessage("ACKAUTH")
        client.send_message(auth_ack_message)
        
        with logged_admins_lock:
            logged_admins.add(admin_id)
        
        handle_admin_commands(client, admin_id)
        
        with logged_admins_lock:
            logged_admins.remove(admin_id)
    
    except Exception as e:
        print(f"exception in handle_admin: {e}")
        with logged_admins_lock:
            if admin_id in logged_admins:
                logged_admins.remove(admin_id)
                print(f"logged_admins: {logged_admins}")
    finally:
        client.__del__()


def handle_client(client : ServerClient):
    """ client handling function """

    debug_print("client handler started")
    try:
        
        status : str = client.get_status()
        if status == 'driver':
            identify_ack_message : ProtocolMessage = ProtocolMessage("ACKIDENTIFY")
            client.send_message(identify_ack_message)
            handle_driver(client)
        elif status == 'admin':
            identify_ack_message : ProtocolMessage = ProtocolMessage("ACKIDENTIFY")
            client.send_message(identify_ack_message)
            handle_admin(client)
        else:
            return None
    
    except Exception as e:
        print(f"exception in handle_client(), {e}")
        debug_print("terminating connection with client")
        client.__del__()
    

def main() -> None:
    global server_object, server_running
    
    debug_print("server starting")
    setup_admin()
    try:
        server_object = Server(DEBUG, SERVER_IP, SERVER_PORT)
        
    except Exception as e:
        print(f"exception in main(), {e}")
        return
    
    debug_print("server is listening")
    threads : list[Thread] = []
    threads_count : int = 0
    try:
        while True:
            client : ServerClient = server_object.accept_client()
            
            t : Thread = Thread(target=handle_client, args=(client, ))
            t.start()
            threads.append(t)
            threads_count += 1
            
    except Exception as e:
        print(f"exception in main(), {e}")
    
    server_running = False
    for t in threads:
        t.join()
    
if __name__ == '__main__':
    main()