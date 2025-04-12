#pragma once

#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 12345

VOID networkingSetup();

VOID networkingCleanup();

BOOL networkingSend(char* message, int messageLength);

BOOL networkingRecv(char* outputBuffer, int outputBufferSize);