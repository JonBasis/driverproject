#include "main.h"



#define BUFFER_SIZE 20
void testNetworking(void) {
	networkingSetup();

	while (1) {
		BOOL Success = TRUE;

		char message[BUFFER_SIZE];
		fgets(message, BUFFER_SIZE, stdin);

		Success = networkingSend(message, BUFFER_SIZE);
		if (!Success) return;

		printf("[+] sent: %.20s\n", message);


		Success = networkingRecv(message, BUFFER_SIZE);
		if (!Success) return;

		printf("got from server: %.20s\n", message);
	}

	networkingCleanup();
}


int main(void) 
	/*
	user mode proccess main function
	
	@return exit code
	*/
{

	puts("[+] welcome!\n");

	testNetworking();

	/*HANDLE hDeviceObject = CreateFileW(DRIVERNAME, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
	if (hDeviceObject == INVALID_HANDLE_VALUE) {
		printf("[-] failed to get handle to the device object, error: %ld\n", GetLastError());
		return 1;
	}

	printf("[+] got handle to the device object, %p\n", hDeviceObject);

	menu(hDeviceObject);*/

	return 0;
}