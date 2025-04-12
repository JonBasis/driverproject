#include "networking.h"


WSADATA wsaData;
SOCKET client_socket;

VOID networkingSetup() {
	int result = 0;

	result = WSAStartup(MAKEWORD(2, 2), &wsaData);

	if (result) {
		printf("[-] error in WSAStartup, %ld\n", WSAGetLastError());
		return;
	}

	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2) {
		WSACleanup();
		puts("[-] error, WinSock DLL does not support version");

		return;
	}


	client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (client_socket == INVALID_SOCKET) {
		printf("[-] failed creating client socket, error: %ld\n", WSAGetLastError());
		WSACleanup();

		return;
	}


	SOCKADDR_IN serverAddress = { 0 };
	serverAddress.sin_family = AF_INET;
	serverAddress.sin_port = htons(SERVER_PORT);
	CHAR ipv4[INET_ADDRSTRLEN] = SERVER_IP;
	inet_pton(AF_INET, ipv4, &(serverAddress.sin_addr));

	result = connect(client_socket, (SOCKADDR*)&serverAddress, sizeof(serverAddress));
	if (result == SOCKET_ERROR) {
		printf("[-] failed connecting to server, %ld\n", WSAGetLastError());
		closesocket(client_socket);
		WSACleanup();

		return;
	}
}


VOID networkingCleanup() {
	closesocket(client_socket);
	WSACleanup();
}


BOOL networkingSend(char* message, int messageLength) {
	BOOL Success = TRUE;
	int result;

	result = send(client_socket, message, messageLength, 0);

	if (result == SOCKET_ERROR) {
		printf("[-] failed to send message to server, error %ld\n", WSAGetLastError());
		closesocket(client_socket);
		WSACleanup();

		return FALSE;
	}

	return Success;
}


BOOL networkingRecv(char* outputBuffer, int outputBufferSize) {
	BOOL Success = TRUE;
	int result;

	result = recv(client_socket, outputBuffer, outputBufferSize, 0);

	if (result == SOCKET_ERROR) {
		printf("[-] failed to recieve a message from server, error %ld\n", WSAGetLastError());
		closesocket(client_socket);
		WSACleanup();

		return FALSE;
	}

	return Success;
}

