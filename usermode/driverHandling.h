#pragma once

#include <windows.h>
#include <stdio.h>

//common to kernel mode
#define IOCTL_DRIVER_TEST CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DRIVER_BLOCK_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DRIVER_UNBLOCK_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DRIVER_BLOCK_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DRIVER_UNBLOCK_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_DRIVER_ENUM_IP CTL_CODE(FILE_DEVICE_UNKNOWN, 0x805, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DRIVER_ENUM_PORT CTL_CODE(FILE_DEVICE_UNKNOWN, 0x806, METHOD_BUFFERED, FILE_ANY_ACCESS)


typedef enum _ipEnumResponseType {
	IP_ARRAY_SIZE = 0,
	IP_ARRAY_DATA = 1,

} ipEnumResponseType;


typedef struct _ipEnumResponseHeader {
	//type of the response
	ipEnumResponseType type;

	//the size of the data not including the response header itself
	DWORD dataSize;

} ipEnumResponseHeader, * PipEnumResponseHeader;

//end of common


#define DRIVERNAME L"\\\\.\\driver"

#define PORTS_COUNT 65536

BOOL ipStringToUINT32(PCHAR ipString, PUINT32 ipOut);

void testDriver(HANDLE hDeviceObject);

void blockIp(HANDLE hDeviceObject);

void unblockIp(HANDLE hDeviceObject);

void blockPort(HANDLE hDeviceObject);

void unblockPort(HANDLE hDeviceObject);

void enumIp(HANDLE hDeviceObject);

void enumPort(HANDLE hDeviceObject);