import win32file
import winioctlcon
import win32api
import ctypes

IP_PART_MIN_VALUE : int = 0
IP_PART_MAX_VALUE : int = 255
IP_BYTES_SIZE : int = 4
IP_STRUCT_SIZE : int = 16
IP_BYTE_ORDER : str = 'little'

MIN_PORTS : int = 0
MAX_PORTS : int = 65535
PORT_BYTES_SIZE : int = 2
PORT_STRUCT_SIZE : int = 16
PORT_BYTE_ORDER : str = 'little'


class DeviceHandler:
    DEFAULT_DEVICE_OBJECT_PERMISSIONS : int = win32file.GENERIC_READ | win32file.GENERIC_WRITE

    """
    #define IOCTL_DRIVER_TEST CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_BLOCK_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_UNBLOCK_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_BLOCK_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_UNBLOCK_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_ENUM_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_ANY_ACCESS)
    #define IOCTL_DRIVER_ENUM_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x806, METHOD_BUFFERED, FILE_ANY_ACCESS)
    """
    
    IOCTL_DRIVER_TEST : int = 0x222000
    IOCTL_DRIVER_BLOCK_IP : int = 0x222004
    IOCTL_DRIVER_UNBLOCK_IP : int = 0x222008
    IOCTL_DRIVER_BLOCK_PORT : int = 0x22200C
    IOCTL_DRIVER_UNBLOCK_PORT : int = 0x222010
    IOCTL_DRIVER_ENUM_IP : int = 0x222014
    IOCTL_DRIVER_ENUM_PORT : int = 0x222018
    
    KNOWN_IOCTL_DRIVER : set[int] = set([
        IOCTL_DRIVER_TEST,
        IOCTL_DRIVER_BLOCK_IP,
        IOCTL_DRIVER_UNBLOCK_IP,
        IOCTL_DRIVER_BLOCK_PORT,
        IOCTL_DRIVER_UNBLOCK_PORT,
        IOCTL_DRIVER_ENUM_IP,
        IOCTL_DRIVER_ENUM_PORT,
    ])

    SIZE_OF_IP_ENUM_RESPONSE_HEADER_STRUCT : int = 8

    def __init__(self, device_name : str) -> None:
        self.device_name : str = device_name

        share_mode : int = 0
        security_attributes : int = None
        flags_and_attributes : int = 0
        template_file : int = None
        self._handle = win32file.CreateFile(
            self.device_name,
            DeviceHandler.DEFAULT_DEVICE_OBJECT_PERMISSIONS,
            share_mode,
            security_attributes,
            win32file.OPEN_EXISTING,
            flags_and_attributes,
            template_file
        )

        print(f"got handle {self._handle}")

        if self._handle == -1:
            error_code : int = win32file.GetLastError() 
            raise ValueError(f"failed to open handle, error code {error_code}")
        
    def __del__(self) -> None:
        if self._handle:
            win32file.CloseHandle(self._handle)
            self._handle = None
    
    def _DeviceIoControl(self, ioctl : int, input_buffer : bytes, output_buffer_size : int = 1024) -> tuple[int, bytes]:
        """ DeviceIoControl for communication with driver """
        
        try:
            if ioctl not in DeviceHandler.KNOWN_IOCTL_DRIVER:
                raise ValueError("ioctl unkown")

            if output_buffer_size < 0:
                raise ValueError("output_buffer_size must be above or equal to 0")

            output = win32file.DeviceIoControl(
                self._handle,
                ioctl,
                input_buffer,
                output_buffer_size
            )
            
            return output
        
        except win32api.error as e:
            print(f"error in DeviceIoControl, {e}")
            print(ioctl)
            print(input_buffer)
            print(output_buffer_size)
            return None
        
    def test_driver(self, input : str, output_buffer_size : int = 1024) -> str:
        """ IOCTL_DRIVER_TEST handler """

        try:
            response = self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_TEST,
                input.encode(),
                output_buffer_size,
            )

            return response.decode()
        
        except win32api.error as e:
            print(f"error in test_driver, {e}")
            return None
    
    def _convert_string_to_ip(self, string : str) -> bytes:
        """ converts ip string to bytes """
        try:
            ip_parts : list[str] = [int(part) for part in string.split(".")]

        except ValueError as e:
            print("invalid ip string")
            return None
        
        if len(ip_parts) != 4:
            return None
        
        sum_of_parts : int = 0
        for i in range(len(ip_parts)):
            if ip_parts[i] < IP_PART_MIN_VALUE or ip_parts[i] > IP_PART_MAX_VALUE:
                return None
            
            sum_of_parts += (ip_parts[i] << (8 * (3 - i)))
            
        return sum_of_parts
        
    def block_ip_int(self, int_ip : int) -> bool:
        """ IOCTL_DRIVER_BLOCK_IP handler """
        
        try:
            self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_BLOCK_IP,
                int_ip.to_bytes(IP_BYTES_SIZE, IP_BYTE_ORDER),
                0,
            )

            return True
        
        except win32api.error as e:
            print(f"error in block_ip, {e}")
            return False
    
    def block_ip(self, input : str) -> bool:
        """ IOCTL_DRIVER_BLOCK_IP handler """

        int_ip : bytes = self._convert_string_to_ip(input)
        if int_ip == None:
            print("error, invalid ip")
            return False
        
        return self.block_ip_int(int_ip)
    
    def unblock_ip_int(self, int_ip : int) -> bool:
        """ IOCTL_DRIVER_BLOCK_IP handler """

        try:
            self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_UNBLOCK_IP,
                int_ip.to_bytes(IP_BYTES_SIZE, IP_BYTE_ORDER),
                0,
            )

            return True
        
        except win32api.error as e:
            print(f"error in unblock_ip, {e}")
            return False
    
    def unblock_ip(self, input) -> bool:
        """ IOCTL_DRIVER_BLOCK_IP handler """
        
        int_ip : bytes = self._convert_string_to_ip(input)
        if int_ip == None:
            print("error, invalid ip")
            return False
        
        return self.unblock_ip_int(int_ip)
    
    def _convert_port_to_integer(self, port : int) -> bytes:
        """ converts port number to bytes """

        return port.to_bytes(PORT_BYTES_SIZE, PORT_BYTE_ORDER)
    
    def block_port(self, port : int) -> True:
        """ IOCTL_DRIVER_BLOCK_PORT handler """
        try:
            port = int(port)
        
        except ValueError as e:
            print("port must be a string describing a number")
        
        if port < MIN_PORTS or port > MAX_PORTS:
            print(f"port must be between {MIN_PORTS} and {MAX_PORTS}")
            return False
        
        port = self._convert_port_to_integer(port)

        try:
            self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_BLOCK_PORT,
                port,
                0
            )

            return True
        
        except win32api.error as e:
            print(f"error in block_port, {e}")
            return False
        
    def unblock_port(self, port : int) -> True:
        """ IOCTL_DRIVER_UNBLOCK_PORT handler """
        try:
            port = int(port)
        
        except ValueError as e:
            print("port must be a string describing a number")
        
        if port < MIN_PORTS or port > MAX_PORTS:
            print(f"port must be between {MIN_PORTS} and {MAX_PORTS}")
            return False
        
        port = self._convert_port_to_integer(port)

        try:
            self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_UNBLOCK_PORT,
                port,
                0
            )

            return True
        
        except win32api.error as e:
            print(f"error in unblock_port, {e}")
            return False
    
    def _convert_ip_int_to_str(self, ip_int : int) -> str:
        """ converts ip int to ip str """

        return f"{str(ip_int >> 24)}.{str((ip_int >> 16) & 0xff)}.{str((ip_int >> 8) & 0xff)}.{str(ip_int & 0xff)}"
    
    def _convert_ip_array_to_list(self, ip_array : bytes) -> list[str, int]:
        """ converts ip array to list containing all blocked ip """

        if len(ip_array) % IP_STRUCT_SIZE != 0:
            print("ip array length must be a multiple of 16")
            return None
        
        blocked_ip : list[str, int] = []
        for i in range(0, len(ip_array), IP_STRUCT_SIZE):
            int_ip : int = int.from_bytes(ip_array[i : i + IP_BYTES_SIZE], IP_BYTE_ORDER)
            print("int_ip: ", int_ip)
            count : int = int.from_bytes(ip_array[i + 8 : i + IP_STRUCT_SIZE], IP_BYTE_ORDER)
            print("count:", count)
            blocked_ip.append((int_ip, count))
        
        return blocked_ip
    
    def enum_ip_int(self) -> list[int, int]:
        """ IOCTL_DRIVER_ENUM_IP handler """
        
        try:
            array_size : bytes = self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_ENUM_IP,
                None,
                DeviceHandler.SIZE_OF_IP_ENUM_RESPONSE_HEADER_STRUCT
            )
            
            response_type : int  = int.from_bytes(array_size[:4], byteorder=IP_BYTE_ORDER)
            if response_type == 1:
                return []
            
            array_size = int.from_bytes(array_size[4:], byteorder=IP_BYTE_ORDER)

            print("ip array size: ", array_size)
            ip_array : bytes = self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_ENUM_IP,
                None,
                DeviceHandler.SIZE_OF_IP_ENUM_RESPONSE_HEADER_STRUCT + array_size
            )
            print("ip array:", ip_array)
            # response_type : int = int.from_bytes(ip_array[-4:], byteorder=IP_BYTE_ORDER)
            # if response_type == 0:
            #     return None
            
            ip_array = ip_array[:-8]

            
            ip_array = self._convert_ip_array_to_list(ip_array)
            print("ip array2:", ip_array)
            
            return ip_array
        
        except win32api.error as e:
            print(f"error in enum_ip, {e}")
            return False
    
    def enum_ip(self) -> list[str, int]:
        """ enump ip with strings """

        blocked_ips : list[int, int] = self.enum_ip_int()
        blocked_ips = [(self._convert_ip_int_to_str(blocked_ip), count) for blocked_ip, count in blocked_ips]
        
        return blocked_ips
    
    def _convert_port_array_to_list(self, port_array : bytes) -> list[int, int]:
        """ converts port array to list containing all blocked ports """

        if len(port_array) % PORT_STRUCT_SIZE != 0:
            print("port array length must be a multiple of 16")
            return None
        
        blocked_ports : list[int, int] = []
        for port in range(0, len(port_array), PORT_STRUCT_SIZE):
            port_state : bytes = port_array[port : port + PORT_BYTES_SIZE]
            int_port_state : int = int.from_bytes(port_state, PORT_BYTE_ORDER)
            count : int = int.from_bytes(port_array[port + 8 : port + PORT_STRUCT_SIZE], PORT_BYTE_ORDER)
            if int_port_state != 0:
                blocked_ports.append((port // PORT_STRUCT_SIZE, count))
        
        return blocked_ports
    
    def enum_port(self) -> list[int, int]:
        """ IOCTL_DRIVER_ENUM_PORT handler """

        try:
            ports_status : bytes = self._DeviceIoControl(
                DeviceHandler.IOCTL_DRIVER_ENUM_PORT,
                None,
                (MAX_PORTS - MIN_PORTS + 1) * PORT_STRUCT_SIZE
                )
            
            blocked_ports : list[int, int] = self._convert_port_array_to_list(ports_status)
            print("blocked ports:", blocked_ports)
            if blocked_ports == None:
                print("got invalid port array")
                return None
            
            return blocked_ports
        
        except win32api.error as e:
            print(f"error in enum_port, {e}")