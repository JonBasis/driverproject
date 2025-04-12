#include "menu.h"

void printMenu() {
	puts("");
	puts("-------------------------");
	puts("menu:");
	puts("1: test driver");
	puts("2: block ip");
	puts("3: unblock ip");
	puts("4: block port");
	puts("5: unblock port");
	puts("6: get all blocked ip's");
	puts("7: get all blocked ports");
	puts("-------------------------");
	puts("");
}


void menu(HANDLE hDeviceObject) {
	CHAR buffer[20];
	int choice;

	while (1) {
		printMenu();
		puts("choice: ");
		fgets(buffer, sizeof(buffer), stdin);
		choice = atoi(buffer);

		switch (choice) {
		case 1:
			testDriver(hDeviceObject);
			break;

		case 2:
			blockIp(hDeviceObject);
			break;

		case 3:
			unblockIp(hDeviceObject);
			break;

		case 4:
			blockPort(hDeviceObject);
			break;

		case 5:
			unblockPort(hDeviceObject);
			break;

		case 6:
			enumIp(hDeviceObject);
			break;

		case 7:
			enumPort(hDeviceObject);
			break;

		default:
			puts("uknown choice\n");
			break;
		}
	}
}