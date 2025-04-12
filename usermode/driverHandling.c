#include "driverHandling.h"

BOOL ipStringToUINT32(PCHAR ipString, PUINT32 ipOut) {
	UINT32 parts[4];
	if (sscanf(ipString, "%u.%u.%u.%u", &parts[0], &parts[1], &parts[2], &parts[3]) != 4) {
		printf("[-] unrecongised ip addres (%s)\n", ipString);
		return FALSE;
	}

	if (parts[0] > 255 || parts[1] > 255 || parts[2] > 255 || parts[3] > 255) {
		puts("[-] one or more ip fields are larger than the limit\n");
		return FALSE;
	}

	*ipOut = parts[0] * 0x1000000 + parts[1] * 0x10000 + parts[2] * 0x100 + parts[3];

	return TRUE;
}


void testDriver(HANDLE hDeviceObject) {

	PCHAR inputBuffer = "Hello driver!\n";
	CHAR outputBuffer[20];

	DWORD bytesReturned = 0;
	BOOL Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_TEST, inputBuffer, (DWORD)strlen(inputBuffer), outputBuffer, sizeof(outputBuffer), &bytesReturned, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}

	printf("[+] got from driver: %20s\n", outputBuffer);
}


void blockIp(HANDLE hDeviceObject) {
	UINT32 inputBuffer[1];
	CHAR ipString[16];
	BOOL Success = TRUE;

	while (1) {
		puts("enter ip to block: ");
		if (scanf("%16s", ipString) == 1) break;
	}

	Success = ipStringToUINT32(ipString, &inputBuffer[0]);
	if (!Success) return;

	printf("[+] attempting to block %s (%u)\n", ipString, inputBuffer[0]);
	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_BLOCK_IP, inputBuffer, (DWORD)sizeof(inputBuffer), NULL, 0, NULL, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}
	else {
		puts("[+] blocked!\n");
	}
}


void unblockIp(HANDLE hDeviceObject) {
	UINT32 inputBuffer[1];
	CHAR ipString[16];
	BOOL Success = TRUE;

	while (1) {
		puts("enter ip to unblock: ");
		if (scanf("%16s", ipString) == 1) break;
	}

	Success = ipStringToUINT32(ipString, &inputBuffer[0]);
	if (!Success) return;

	printf("[+] attempting to unblock %s (%u)\n", ipString, inputBuffer[0]);
	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_UNBLOCK_IP, inputBuffer, (DWORD)sizeof(inputBuffer), NULL, 0, NULL, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}
	else {
		puts("[+] unblocked!\n");
	}
}


void blockPort(HANDLE hDeviceObject) {
	UINT16 inputBuffer[1];
	BOOL Success = TRUE;

	while (1) {
		puts("enter port to block: ");
		if (scanf("%hu", &inputBuffer[0]) == 1) break;
	}

	printf("[+] attempting to block %hu\n", inputBuffer[0]);
	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_BLOCK_PORT, inputBuffer, (DWORD)sizeof(inputBuffer), NULL, 0, NULL, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}
	else {
		puts("[+] blocked!\n");
	}
}


void unblockPort(HANDLE hDeviceObject) {
	UINT16 inputBuffer[1];
	BOOL Success = TRUE;

	while (1) {
		puts("enter port to unblock: ");
		if (scanf("%hu", &inputBuffer[0]) == 1) break;
	}

	printf("[+] attempting to unblock %hu\n", inputBuffer[0]);
	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_UNBLOCK_PORT, inputBuffer, (DWORD)sizeof(inputBuffer), NULL, 0, NULL, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}
	else {
		puts("[+] unblocked!\n");
	}
}


void printBlockedIp(PUINT32 outputBuffer, DWORD outputBufferSize) {
	UINT32 ip;

	printf("[+] outputBufferSize %lu\n", outputBufferSize);
	puts("[+] blocked ips:");
	for (SIZE_T i = 0; i < outputBufferSize; i++) {
		ip = outputBuffer[i];

		printf("%u.%u.%u.%u, ", ip >> 24, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF);
	}

	puts("");
}


DWORD getIpArraySize(HANDLE hDeviceObject) {
	BOOL Success = TRUE;
	ipEnumResponseHeader responseHeader;
	DWORD outputBufferSize = sizeof(ipEnumResponseHeader);

	puts("[+] attempting DeviceIoControl in enumIp");

	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_ENUM_IP, NULL, 0, &responseHeader, outputBufferSize, NULL, NULL);

	if (!Success) {
		printf("[-] DeviceIoControl failed in enumIp, error %ld\n", GetLastError());
		return 0;
	}

	if (responseHeader.type == IP_ARRAY_DATA) {
		puts("[+] ip array is empty, no ip's are blocked");
		return 0;
	}

	return responseHeader.dataSize;
}


void enumIp(HANDLE hDeviceObject) {
	BOOL Success = TRUE;
	DWORD outputBufferSize;

	DWORD ipArraySize = getIpArraySize(hDeviceObject);

	if (ipArraySize == 0) {
		return;
	}


	outputBufferSize = ipArraySize + sizeof(ipEnumResponseHeader);

	printf("[+] needed buffer size is %u, ipEnumResponseHeader size is %zu, ipArraySize is %u\n", outputBufferSize, sizeof(ipEnumResponseHeader), ipArraySize);

	PUINT32 outputBuffer = (PUINT32)calloc(outputBufferSize / sizeof(UINT32), sizeof(UINT32));

	if (!outputBuffer) {
		puts("[-] malloc failed in ipArray");
		return;
	}


	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_ENUM_IP, NULL, 0, outputBuffer, outputBufferSize, NULL, NULL);

	if (!Success) {
		printf("[-] 2nd DeviceIoControl failed in enumIp, error %ld\n", GetLastError());
		return;
	}

	PUINT32 ipArray = outputBuffer + sizeof(ipEnumResponseHeader) / sizeof(UINT32);
	printBlockedIp(ipArray, ipArraySize / sizeof(UINT32));

	free(outputBuffer);
	puts("[+] enumIp finished successfully");
}


void printBlockedPort(PUINT16 ports) {
	puts("[+] blocked ports:");

	for (INT32 i = 0; i < PORTS_COUNT; i++) {
		if (ports[i]) printf("%hu, ", (i & 0xFFFF));
	}

	puts("");
}


void enumPort(HANDLE hDeviceObject) {
	BOOL Success = TRUE;
	PUINT16 ports;

	ports = (PUINT16)calloc(PORTS_COUNT, sizeof(UINT16));
	if (!ports) {
		puts("[-] malloc failed in enumPort");
		return;
	}

	Success = DeviceIoControl(hDeviceObject, IOCTL_DRIVER_ENUM_PORT, NULL, 0, ports, PORTS_COUNT * sizeof(UINT16), NULL, NULL);

	if (!Success) {
		printf("[-] failed to DeviceIoControl, error: %ld\n", GetLastError());
	}
	else {
		printBlockedPort(ports);
	}

	free(ports);

	return;
}