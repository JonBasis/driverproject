# driverproject
final 12th grade project for bagrut

the project consists of a windows wdm driver that utilizes the wfp engine and a python client.\
the driver communicates with the client via the DeviceIoControl function provided by the windows api, using custom IOCTLs.

### Usage
the driver allows the user to remotely block or unblock ip addresses and ports from recieving or sending network traffic to the client, and enumerate all blocked ip addresses and ports.

## IOCTLs
- IOCTL_DRIVER_ENUM_IP - used for general testing
- IOCTL_DRIVER_BLOCK_IP - allows client to block specified ip address from sending or recieving network traffic from the client
- IOCTL_DRIVER_UNBLOCK_IP - unblocks a previously blocked ip
- IOCTL_DRIVER_BLOCK_PORT - blocks specified port from sending or recieving networking traffic
- IOCTL_DRIVER_UNBLOCK_PORT - unblocks a previously blocked port
- IOCTL_DRIVER_ENUM_IP - allows the client to recieve an array of all blocked ip addresses
- IOCTL_DRIVER_ENUM_PORT allows the client to recieve an array of all blocked ports

## 
#### the server stores each driver's ip and port block rules using a mysql server and updates the drivers every 30 seconds
#### the drivers are remotely configured using the admin client gui
## 


### P.S. - folders in use are driver and server, usermode is for general testing
